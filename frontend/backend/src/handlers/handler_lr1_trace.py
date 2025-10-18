import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Tuple
from src.utils.funciones_auxiales import (
    extraer_symbols_from_grammar,
    calcular_first_table
)
from src.utils.funciones_auxiliares_table import (
    construir_conjuntos_lr1,
    generar_tabla_lr1
)

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ParseStep:
    """Representa un paso en el trace de parsing"""
    def __init__(self, step_number: int, stack: List[int], input_string: str, action: str):
        self.step_number = step_number
        self.stack = stack.copy()
        self.input_string = input_string
        self.action = action
    
    def __str__(self):
        stack_str = " ".join(map(str, self.stack))
        return f"Step {self.step_number}: Stack=[{stack_str}] Input='{self.input_string}' Action={self.action}"


def simular_parsing_lr1(input_string: str, tabla_lr1: Dict, productions: List[str]) -> List[ParseStep]:
    """
    Simula el parsing LR(1) de una cadena de entrada.
    
    Args:
        input_string: Cadena a parsear (ej: "c d d $")
        tabla_lr1: Tabla ACTION/GOTO generada
        productions: Lista de producciones
    
    Returns:
        List[ParseStep]: Lista de pasos del parsing
    """
    steps = []
    action_table = tabla_lr1['action']
    goto_table = tabla_lr1['goto']
    augmented_productions = tabla_lr1['productions']
    
    # Preparar entrada
    input_tokens = input_string.strip().split()
    if input_tokens[-1] != '$':
        input_tokens.append('$')
    
    # Estado inicial
    stack = [0]  # Stack con estado inicial
    step_number = 1
    
    while True:
        current_state = stack[-1]
        current_token = input_tokens[0] if input_tokens else '$'
        
        # Obtener acción
        if current_token in action_table[current_state]:
            action = action_table[current_state][current_token]
            # Si la acción está vacía, es un error
            if action == "":
                action = "ERROR"
        else:
            action = "ERROR"
        
        # Crear paso actual
        current_input = " ".join(input_tokens)
        step = ParseStep(step_number, stack, current_input, action)
        steps.append(step)
        
        print(f"Paso {step_number}: Estado={current_state}, Token='{current_token}', Acción='{action}'")
        
        # Procesar acción
        if action.startswith('s'):
            # Shift: agregar token y estado
            next_state = int(action[1:])
            stack.append(current_token)
            stack.append(next_state)
            input_tokens.pop(0)
            
        elif action.startswith('r'):
            # Reduce: aplicar producción
            production_index = int(action[1:])
            production = augmented_productions[production_index]
            left, right = production.split(' -> ')
            right_symbols = right.split()
            
            # Remover símbolos del stack
            symbols_to_remove = len(right_symbols) * 2  # token + estado por cada símbolo
            for _ in range(symbols_to_remove):
                if stack:
                    stack.pop()
            
            # Agregar no terminal
            stack.append(left)
            
            # GOTO
            if stack:
                current_state = stack[-2] if len(stack) >= 2 else 0
                if left in goto_table[current_state] and goto_table[current_state][left] != "":
                    next_state = goto_table[current_state][left]
                    stack.append(next_state)
                else:
                    print(f"ERROR: No hay GOTO para {left} en estado {current_state}")
                    break
            
        elif action == 'acc':
            # Accept: parsing exitoso
            break
            
        else:
            # Error
            break
        
        step_number += 1
        
        # Prevenir loops infinitos
        if step_number > 100:
            break
    
    return steps


def generar_json_trace_table(steps: List[ParseStep], grammar_info: Dict, input_string: str):
    """
    Genera un JSON estructurado para mostrar la tabla de trace.
    
    Args:
        steps: Lista de pasos del parsing
        grammar_info: Información de la gramática
        input_string: Cadena de entrada original
    
    Returns:
        dict: JSON estructurado para la tabla de trace
    """
    trace_data = []
    
    for step in steps:
        trace_data.append({
            "step": step.step_number,
            "stack": step.stack,
            "stack_string": " ".join(map(str, step.stack)),
            "input": step.input_string,
            "action": step.action,
            "action_type": get_action_type(step.action)
        })
    
    return {
        "success": True,
        "operation": "lr1_trace",
        "grammar": {
            "productions": grammar_info["productions"],
            "start_symbol": grammar_info["start_symbol"]
        },
        "input_string": input_string,
        "trace_table": trace_data,
        "summary": {
            "total_steps": len(steps),
            "parsing_successful": steps[-1].action == "acc" if steps else False,
            "final_action": steps[-1].action if steps else "ERROR"
        }
    }


def get_action_type(action: str) -> str:
    """Determina el tipo de acción"""
    if action.startswith('s'):
        return "shift"
    elif action.startswith('r'):
        return "reduce"
    elif action == 'acc':
        return "accept"
    else:
        return "error"


def lambda_handler(event, context):
    try:
        # Parsear el body si viene como string
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Verificar que sea operación de LR1 trace
        if body.get('operation') != 'lr1_trace':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Operation must be lr1_trace'})
            }
        
        # Verificar que tenga lr1_table e input_string
        if 'lr1_table' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'lr1_table is required for LR(1) trace'})
            }
        
        if 'input_string' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'input_string is required'})
            }
        
        # Extraer datos del evento
        lr1_table = body['lr1_table']
        input_string = body['input_string']
        
        print(f"Tabla LR(1) recibida: {len(lr1_table.get('table_data', []))} estados")
        print(f"Cadena de entrada: '{input_string}'")
        
        # Convertir el formato de tabla para la función de parsing
        tabla_lr1 = {
            'action': {},
            'goto': {},
            'productions': lr1_table['grammar']['productions']
        }
        
        # Convertir table_data al formato esperado
        for state_data in lr1_table['table_data']:
            state_num = state_data['state']
            tabla_lr1['action'][state_num] = state_data['action']
            tabla_lr1['goto'][state_num] = state_data['goto']
        
        # Simular parsing
        steps = simular_parsing_lr1(input_string, tabla_lr1, lr1_table['grammar']['productions'])
        print(f"Número de pasos: {len(steps)}")
        
        # Generar JSON estructurado para el trace
        result = generar_json_trace_table(steps, lr1_table['grammar'], input_string)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, indent=2)
        }
        
    except Exception as e:
        logger.error(f"Error en lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e), 'success': False})
        }


# Eventos de prueba para LR(1) Trace
test_events_trace = [
    # Caso 1: Gramática simple con cadena válida
    {
        'body': json.dumps({
            "grammar": {
                "productions": [
                    "S' -> S",
                    "S -> C C", 
                    "C -> c C",
                    "C -> d"
                ],
                "start_symbol": "S'"
            },
            "input_string": "c d d",
            "operation": "lr1_trace"
        })
    },
    
    # Caso 2: Gramática simple con cadena más larga
    {
        'body': json.dumps({
            "grammar": {
                "productions": [
                    "S' -> S",
                    "S -> C C", 
                    "C -> c C",
                    "C -> d"
                ],
                "start_symbol": "S'"
            },
            "input_string": "c c d d",
            "operation": "lr1_trace"
        })
    },
    
    # Caso 3: Gramática simple con cadena inválida
    {
        'body': json.dumps({
            "grammar": {
                "productions": [
                    "S' -> S",
                    "S -> C C", 
                    "C -> c C",
                    "C -> d"
                ],
                "start_symbol": "S'"
            },
            "input_string": "c c c",
            "operation": "lr1_trace"
        })
    },
    
    # Caso 4: Gramática simple con un terminal
    {
        'body': json.dumps({
            "grammar": {
                "productions": [
                    "S' -> S",
                    "S -> a"
                ],
                "start_symbol": "S'"
            },
            "input_string": "a",
            "operation": "lr1_trace"
        })
    }
]

if __name__ == '__main__':
    all_results_trace = []
    
    for i, event in enumerate(test_events_trace, 1):
        print(f"\n{'='*60}")
        print(f"PRUEBA LR(1) TRACE {i}")
        print(f"{'='*60}")
        
        result = lambda_handler(event, None)
        print(f"Status Code: {result['statusCode']}")
        
        # Parsear el evento original
        event_data = json.loads(event['body'])
        
        # Crear resultado completo
        test_result = {
            "test_number": i,
            "test_name": f"Prueba LR(1) Trace {i}",
            "grammar": event_data["grammar"],
            "input_string": event_data["input_string"],
            "operation": event_data["operation"],
            "status_code": result['statusCode'],
            "success": result['statusCode'] == 200,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
        if result['statusCode'] == 200:
            body = json.loads(result['body'])
            test_result["result"] = body
            print("✓ Éxito")
            print(json.dumps(body, indent=2, ensure_ascii=False))
        else:
            error_body = json.loads(result['body'])
            test_result["error"] = error_body
            print(f"✗ Error: {result['body']}")
        
        all_results_trace.append(test_result)
    
    # Guardar todos los resultados LR(1) Trace en un archivo JSON
    output_file_trace = "test_results_lr1_trace.json"
    with open(output_file_trace, 'w', encoding='utf-8') as f:
        json.dump(all_results_trace, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL LR(1) TRACE")
    print(f"{'='*60}")
    
    successful_tests = sum(1 for r in all_results_trace if r['success'])
    total_tests = len(all_results_trace)
    
    print(f"Tests LR(1) Trace exitosos: {successful_tests}/{total_tests}")
    print(f"Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")
    print(f"Resultados LR(1) Trace guardados en: {output_file_trace}")
