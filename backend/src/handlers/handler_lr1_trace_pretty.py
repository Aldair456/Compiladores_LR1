import json
import logging
from typing import Dict, Any, List

# Reutilizamos la simulación existente
from src.handlers.handler_lr1_trace import simular_parsing_lr1, get_action_type

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    try:
        # Parsear el body si viene como string
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Verificar operación
        if body.get('operation') != 'lr1_trace_pretty':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Operation must be lr1_trace_pretty'})
            }
        
        # Validar entradas
        if 'lr1_table' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'lr1_table is required'})
            }
        if 'input_string' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'input_string is required'})
            }
        
        lr1_table = body['lr1_table']
        input_string = body['input_string']
        max_steps = int(body.get('max_steps', 100))
        
        # Convertir el formato de tabla para la función de parsing existente
        tabla_lr1 = {
            'action': {},
            'goto': {},
            'productions': lr1_table['grammar']['productions']
        }
        for state_data in lr1_table['table_data']:
            state_num = state_data['state']
            tabla_lr1['action'][state_num] = state_data['action']
            tabla_lr1['goto'][state_num] = state_data['goto']
        
        # Simular parsing (la función interna ya corta en 100 pasos)
        steps = simular_parsing_lr1(input_string, tabla_lr1, lr1_table['grammar']['productions'])
        if len(steps) > max_steps:
            steps = steps[:max_steps]
        
        # Preparar salida "bonita"
        input_tokens = input_string.strip().split()
        if not input_tokens or input_tokens[-1] != '$':
            input_tokens = input_tokens + ['$']
        
        trace_rows: List[Dict[str, Any]] = []
        for s in steps:
            trace_rows.append({
                'step': s.step_number,
                'stack': s.stack,
                'stack_string': " ".join(map(str, s.stack)),
                'input': s.input_string,
                'action': s.action,
                'action_type': get_action_type(s.action)
            })
        
        # También devolver una versión de texto simple
        pretty_lines: List[str] = []
        pretty_lines.append(f"Input (tokens): \n{' '.join(input_tokens)}\n")
        pretty_lines.append(f"Maximum number of steps: \n{max_steps}\n\n")
        pretty_lines.append("Trace\tTree")
        pretty_lines.append("Step\tStack\tInput\tAction")
        for row in trace_rows:
            pretty_lines.append(f"{row['step']}\t{row['stack_string']}\t{row['input']}\t{row['action']}")
        
        result = {
            'success': True,
            'operation': 'lr1_trace_pretty',
            'input_tokens': input_tokens,
            'max_steps': max_steps,
            'trace_rows': trace_rows,
            'pretty': "\n".join(pretty_lines)
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, indent=2)
        }
    except Exception as e:
        logger.error(f"Error en lambda_handler (trace_pretty): {str(e)}")
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



event = {
  "operation": "lr1_trace_pretty",
  "lr1_table": {
    "grammar": {
      "productions": [
        "S' -> S",
        "S -> a b",
        "S -> c d",
        "S -> e"
      ]
    },
    "table_data": [
      {
        "state": 0,
        "action": {
          "a": "s2",
          "c": "s1",
          "e": "s3"
        },
        "goto": {
          "S": 4
        }
      },
      {
        "state": 1,
        "action": {
          "$": "r3"
        },
        "goto": {}
      },
      {
        "state": 2,
        "action": {
          "b": "s6"
        },
        "goto": {}
      },
      {
        "state": 3,
        "action": {
          "$": "r4"
        },
        "goto": {}
      },
      {
        "state": 4,
        "action": {
          "$": "acc"
        },
        "goto": {}
      },
      {
        "state": 5,
        "action": {
          "$": "r2"
        },
        "goto": {}
      },
      {
        "state": 6,
        "action": {
          "$": "r1"
        },
        "goto": {}
      }
    ]
  },
  "input_string": "a b",
  "max_steps": 100
}



if __name__ == '__main__':
    print(f"{'='*60}")
    print("PRUEBA LR(1) TRACE PRETTY")
    result = lambda_handler(event, None)
    body = json.loads(result['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    print(f"{'='*60}")
