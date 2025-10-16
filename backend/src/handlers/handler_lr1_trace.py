import json
import logging
from typing import Dict, Any, Optional, List

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler para hacer trace/validación de cadenas usando tabla LR(1).
    
    Recibe como entrada:
    - lr1_table: Tabla LR(1) completa (action_table, goto_table, reductions)
    - input_string: Cadena de entrada a validar
    - options: Opciones de configuración
    
    Args:
        event: Evento con tabla LR(1) y cadena de entrada
        context: Contexto de Lambda
    
    Returns:
        dict: Respuesta JSON con el trace del parsing
    """
    try:
        logger.info("Iniciando trace LR(1)")
        
        # Parsear el body si viene como string
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Validar entrada obligatoria
        if 'lr1_table' not in body:
            return _error_response("lr1_table es obligatorio")
        
        if 'input_string' not in body:
            return _error_response("input_string es obligatorio")
        
        lr1_table = body['lr1_table']
        input_string = body['input_string']
        options = body.get('options', {})
        
        # Validar estructura de tabla LR(1)
        if 'action_table' not in lr1_table:
            return _error_response("lr1_table.action_table es obligatorio")
        
        if 'goto_table' not in lr1_table:
            return _error_response("lr1_table.goto_table es obligatorio")
        
        if 'reductions' not in lr1_table:
            return _error_response("lr1_table.reductions es obligatorio")
        
        # Configurar opciones
        end_marker = options.get('end_marker', '$')
        accept_token = options.get('accept_token', 'acc')
        
        logger.info(f"Procesando cadena: '{input_string}' con tabla LR(1)")
        
        # Ejecutar trace LR(1)
        trace_result = _ejecutar_trace_lr1(
            lr1_table, input_string, end_marker, accept_token
        )
        
        logger.info(f"Trace completado: {trace_result['accepted']}")
        
        # Generar respuesta HTTP
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(trace_result, indent=2)
        }
        
        return response
        
    except Exception as e:
        logger.error(f"Error en lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return _error_response(f"Error interno: {str(e)}")


def _ejecutar_trace_lr1(
    lr1_table: Dict[str, Any],
    input_string: str,
    end_marker: str,
    accept_token: str
) -> Dict[str, Any]:
    """
    Ejecuta el trace LR(1) para validar una cadena de entrada.
    
    Args:
        lr1_table: Tabla LR(1) completa
        input_string: Cadena de entrada
        end_marker: Marcador de fin
        accept_token: Token de aceptación
    
    Returns:
        dict: Resultado del trace
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
        
        if input_position >= len(input_tokens):
            return _error_trace_result(
                f"Error: posición de entrada {input_position} fuera de rango",
                trace_steps, False
            )
        
        current_token = input_tokens[input_position]
        
        # Obtener acción para el estado y token actual
        if str(current_state) not in action_table:
            return _error_trace_result(
                f"Error: estado {current_state} no encontrado en action_table",
                trace_steps, False
            )
        
        state_actions = action_table[str(current_state)]
        
        if current_token not in state_actions:
            return _error_trace_result(
                f"Error: token '{current_token}' no válido en estado {current_state}",
                trace_steps, False
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
        
        # Procesar acción
        if action == accept_token:
            # ACCEPT
            step["description"] = f"ACCEPT: Cadena aceptada"
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
            target_state = int(action[1:])
            stack.append(target_state)
            current_state = target_state
            input_position += 1
            
            step["description"] = f"SHIFT: mover '{current_token}' al stack, ir al estado {target_state}"
            trace_steps.append(step)
        
        elif action.startswith('r'):
            # REDUCE
            production_number = int(action[1:])
            
            # Buscar información de la reducción
            reduction_info = None
            for state_id, state_reductions in reductions.items():
                if int(state_id) == current_state:
                    for lookahead, info in state_reductions.items():
                        if info.get('production_number') == production_number:
                            reduction_info = info
                            break
                    if reduction_info:
                        break
            
            if not reduction_info:
                return _error_trace_result(
                    f"Error: información de reducción no encontrada para producción {production_number}",
                    trace_steps, False
                )
            
            production = reduction_info['production']
            left_side = production.split(' -> ')[0].strip()
            right_side = production.split(' -> ')[1].strip()
            
            # Calcular cuántos símbolos popear del stack
            if right_side == 'ε':
                # Producción epsilon: no popear nada
                symbols_to_pop = 0
            else:
                symbols_to_pop = len(right_side.split())
            
            # Popear estados del stack
            if len(stack) < symbols_to_pop:
                return _error_trace_result(
                    f"Error: stack insuficiente para reducción {production}",
                    trace_steps, False
                )
            
            # Popear estados
            for _ in range(symbols_to_pop):
                stack.pop()
            
            # Obtener nuevo estado
            if len(stack) == 0:
                return _error_trace_result(
                    f"Error: stack vacío después de reducción",
                    trace_steps, False
                )
            
            previous_state = stack[-1]
            
            # GOTO
            if str(previous_state) not in goto_table:
                return _error_trace_result(
                    f"Error: estado {previous_state} no encontrado en goto_table",
                    trace_steps, False
                )
            
            state_gotos = goto_table[str(previous_state)]
            
            if left_side not in state_gotos:
                return _error_trace_result(
                    f"Error: GOTO no encontrado para {left_side} en estado {previous_state}",
                    trace_steps, False
                )
            
            goto_state = state_gotos[left_side]
            stack.append(goto_state)
            current_state = goto_state
            
            step["description"] = f"REDUCE: {production} (pop {symbols_to_pop}), GOTO({previous_state}, {left_side}) = {goto_state}"
            trace_steps.append(step)
        
        else:
            return _error_trace_result(
                f"Error: acción desconocida '{action}'",
                trace_steps, False
            )
        
        # Límite de pasos para evitar bucles infinitos
        if step_number > 1000:
            return _error_trace_result(
                "Error: límite de pasos excedido (posible bucle infinito)",
                trace_steps, False
            )


def _error_trace_result(
    error_message: str,
    trace_steps: List[Dict[str, Any]],
    accepted: bool
) -> Dict[str, Any]:
    """
    Genera resultado de error para el trace.
    
    Args:
        error_message: Mensaje de error
        trace_steps: Pasos del trace hasta el error
        accepted: Si la cadena fue aceptada
    
    Returns:
        dict: Resultado de error
    """
    return {
        "success": False,
        "accepted": accepted,
        "operation": "lr1_trace",
        "error": error_message,
        "trace_steps": trace_steps,
        "summary": {
            "total_steps": len(trace_steps),
            "error_step": len(trace_steps)
        }
    }


def _error_response(message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Genera respuesta de error HTTP.
    
    Args:
        message: Mensaje de error
        details: Detalles adicionales opcionales
    
    Returns:
        dict: Respuesta de error HTTP
    """
    response = {
        "success": False,
        "error": message
    }
    
    if details:
        response["details"] = details
    
    return {
        'statusCode': 400,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response, indent=2)
    }


# Ejemplo de uso para pruebas
if __name__ == "__main__":
    # Test 1: Cadena válida
    test_event_1 = {
        "lr1_table": {
            "action_table": {
                "0": {"a": "s4"},
                "1": {"$": "acc"},
                "2": {"b": "s5"},
                "3": {"c": "s7"},
                "4": {"b": "r2", "c": "r2"},
                "5": {"c": "r4"},
                "6": {"$": "r1"},
                "7": {"$": "r6"}
            },
            "goto_table": {
                "0": {"S": 1, "A": 2},
                "1": {},
                "2": {"B": 3},
                "3": {"C": 6},
                "4": {},
                "5": {},
                "6": {},
                "7": {}
            },
            "reductions": {
                "4": {
                    "b": {"production": "A -> a", "production_number": 2},
                    "c": {"production": "A -> a", "production_number": 2}
                },
                "5": {
                    "c": {"production": "B -> b", "production_number": 4}
                },
                "6": {
                    "$": {"production": "S -> A B C", "production_number": 1}
                },
                "7": {
                    "$": {"production": "C -> c", "production_number": 6}
                }
            }
        },
        "input_string": "a b c",
        "options": {
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    print("=== TEST 1: Cadena válida 'a b c' ===")
    result1 = lambda_handler(test_event_1, None)
    print(f"Status Code: {result1['statusCode']}")
    if result1['statusCode'] == 200:
        print("\n📋 JSON COMPLETO:")
        print(result1['body'])
    
    # Test 2: Cadena inválida
    test_event_2 = {
        "lr1_table": test_event_1["lr1_table"],
        "input_string": "a b ",  # 'd' no es válido
        "options": {
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    print("\n=== TEST 2: Cadena inválida 'a b d' ===")
    result2 = lambda_handler(test_event_2, None)
    print(f"Status Code: {result2['statusCode']}")
    if result2['statusCode'] == 200:
        print("\n📋 JSON COMPLETO:")
        print(result2['body'])
