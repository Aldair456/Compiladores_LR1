"""
Procesador de trace LR(1).
Contiene la lógica para ejecutar el trace de parsing usando una tabla LR(1).
"""

import logging
from typing import Dict, Any, Optional, List

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def ejecutar_trace_lr1(
    lr1_table: Dict[str, Any],
    input_string: str,
    end_marker: str = '$',
    accept_token: str = 'acc'
) -> Dict[str, Any]:
    """
    Ejecuta el trace LR(1) para validar una cadena de entrada.
    
    Args:
        lr1_table: Tabla LR(1) completa (action_table, goto_table, reductions)
        input_string: Cadena de entrada
        end_marker: Marcador de fin (default: '$')
        accept_token: Token de aceptación (default: 'acc')
    
    Returns:
        dict: Resultado del trace con success, accepted, trace_steps y summary
    """
    action_table = lr1_table['action_table']
    goto_table = lr1_table['goto_table']
    reductions = lr1_table['reductions']
    
    # Preparar entrada: agregar marcador de fin
    input_tokens = input_string.split() + [end_marker]
    
    # Estado inicial
    current_state = 0
    stack = [0]  # Stack con estados
    input_position = 0
    trace_steps = []
    step_number = 0
    
    logger.info(f"Iniciando parsing de: {input_tokens}")
    
    while True:
        step_number += 1
        
        # Validar posición de entrada
        if input_position >= len(input_tokens):
            return _build_error_result(
                f"Error: posición de entrada {input_position} fuera de rango",
                trace_steps
            )
        
        current_token = input_tokens[input_position]
        
        # Obtener acción para el estado y token actual
        if str(current_state) not in action_table:
            return _build_error_result(
                f"Error: estado {current_state} no encontrado en action_table",
                trace_steps
            )
        
        state_actions = action_table[str(current_state)]
        
        if current_token not in state_actions:
            return _build_error_result(
                f"Error: token '{current_token}' no válido en estado {current_state}",
                trace_steps
            )
        
        action = state_actions[current_token]
        
        # Crear paso del trace
        step = {
            "step": step_number,
            "state": current_state,
            "stack": stack.copy(),
            "input_position": input_position,
            "current_token": current_token,
            "action": action,
            "description": ""
        }
        
        # Procesar acción según tipo
        if action == accept_token:
            # ACCEPT: Cadena aceptada
            step["description"] = "ACCEPT: Cadena aceptada"
            trace_steps.append(step)
            
            return {
                "success": True,
                "accepted": True,
                "operation": "lr1_trace",
                "input_string": input_string,
                "trace_steps": trace_steps,
                "summary": {
                    "total_steps": step_number,
                    "final_state": current_state,
                    "stack_depth": len(stack),
                    "tokens_processed": input_position + 1
                }
            }
        
        elif action.startswith('s'):
            # SHIFT
            result = _process_shift(action, current_token, stack)
            if isinstance(result, dict) and not result.get('success', True):
                return _build_error_result(result['error'], trace_steps)
            
            current_state, input_increment, step["description"] = result
            input_position += input_increment
            trace_steps.append(step)
        
        elif action.startswith('r'):
            # REDUCE
            result = _process_reduce(action, current_state, stack, reductions, goto_table)
            if isinstance(result, dict) and not result.get('success', True):
                return _build_error_result(result['error'], trace_steps)
            
            current_state, step["description"] = result
            trace_steps.append(step)
        
        else:
            return _build_error_result(
                f"Error: acción desconocida '{action}'",
                trace_steps
            )
        
        # Límite de pasos para evitar bucles infinitos
        if step_number > 1000:
            return _build_error_result(
                "Error: límite de pasos excedido (posible bucle infinito)",
                trace_steps
            )


def _process_shift(
    action: str,
    current_token: str,
    stack: List[int]
) -> tuple[int, int, str]:
    """
    Procesa una acción SHIFT.
    
    Args:
        action: Acción SHIFT (ej: 's5')
        current_token: Token actual
        stack: Stack de estados (se modifica in-place)
    
    Returns:
        tuple: (nuevo_estado, incremento_input, descripcion)
    """
    try:
        target_state = int(action[1:])
        stack.append(target_state)
        description = f"SHIFT: mover '{current_token}' al stack, ir al estado {target_state}"
        return target_state, 1, description
    except (ValueError, IndexError) as e:
        return {"success": False, "error": f"Error procesando SHIFT '{action}': {str(e)}"}


def _process_reduce(
    action: str,
    current_state: int,
    stack: List[int],
    reductions: Dict[str, Any],
    goto_table: Dict[str, Any]
) -> tuple[int, str] | Dict[str, Any]:
    """
    Procesa una acción REDUCE.
    
    Args:
        action: Acción REDUCE (ej: 'r2')
        current_state: Estado actual
        stack: Stack de estados (se modifica in-place)
        reductions: Tabla de reducciones
        goto_table: Tabla GOTO
    
    Returns:
        tuple: (nuevo_estado, descripcion) o dict con error
    """
    try:
        production_number = int(action[1:])
    except (ValueError, IndexError) as e:
        return {"success": False, "error": f"Error procesando REDUCE '{action}': {str(e)}"}
    
    # Buscar información de la reducción
    reduction_info = _find_reduction_info(reductions, current_state, production_number)
    if not reduction_info:
        return {
            "success": False,
            "error": f"Error: información de reducción no encontrada para producción {production_number}"
        }
    
    production = reduction_info['production']
    left_side = production.split(' -> ')[0].strip()
    right_side = production.split(' -> ')[1].strip()
    
    # Calcular cuántos símbolos popear del stack
    symbols_to_pop = 0 if right_side == 'ε' else len(right_side.split())
    
    # Validar y popear del stack
    if len(stack) < symbols_to_pop:
        return {
            "success": False,
            "error": f"Error: stack insuficiente para reducción {production}"
        }
    
    for _ in range(symbols_to_pop):
        stack.pop()
    
    if len(stack) == 0:
        return {"success": False, "error": "Error: stack vacío después de reducción"}
    
    previous_state = stack[-1]
    
    # Realizar GOTO
    goto_result = _perform_goto(goto_table, previous_state, left_side)
    if isinstance(goto_result, dict) and not goto_result.get('success', True):
        return goto_result
    
    goto_state = goto_result
    stack.append(goto_state)
    
    description = f"REDUCE: {production} (pop {symbols_to_pop}), GOTO({previous_state}, {left_side}) = {goto_state}"
    return goto_state, description


def _find_reduction_info(
    reductions: Dict[str, Any],
    current_state: int,
    production_number: int
) -> Optional[Dict[str, Any]]:
    """
    Busca información de una reducción específica.
    
    Args:
        reductions: Tabla de reducciones
        current_state: Estado actual
        production_number: Número de producción a buscar
    
    Returns:
        dict: Información de la reducción o None si no se encuentra
    """
    for state_id, state_reductions in reductions.items():
        if int(state_id) == current_state:
            for lookahead, info in state_reductions.items():
                if info.get('production_number') == production_number:
                    return info
    return None


def _perform_goto(
    goto_table: Dict[str, Any],
    state: int,
    symbol: str
) -> int | Dict[str, Any]:
    """
    Realiza una operación GOTO.
    
    Args:
        goto_table: Tabla GOTO
        state: Estado actual
        symbol: Símbolo no terminal
    
    Returns:
        int: Nuevo estado o dict con error
    """
    if str(state) not in goto_table:
        return {
            "success": False,
            "error": f"Error: estado {state} no encontrado en goto_table"
        }
    
    state_gotos = goto_table[str(state)]
    
    if symbol not in state_gotos:
        return {
            "success": False,
            "error": f"Error: GOTO no encontrado para {symbol} en estado {state}"
        }
    
    return state_gotos[symbol]


def _build_error_result(
    error_message: str,
    trace_steps: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Construye un resultado de error para el trace.
    
    Args:
        error_message: Mensaje de error
        trace_steps: Pasos del trace hasta el error
    
    Returns:
        dict: Resultado de error estructurado
    """
    return {
        "success": False,
        "accepted": False,
        "operation": "lr1_trace",
        "error": error_message,
        "trace_steps": trace_steps,
        "summary": {
            "total_steps": len(trace_steps),
            "error_step": len(trace_steps)
        }
    }

