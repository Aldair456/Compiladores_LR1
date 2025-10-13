import json
import logging
from typing import Any, Dict, List

from src.handlers.handler_lr1_trace import simular_parsing_lr1

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def build_tree_from_trace(productions: List[str], trace_rows: List[Dict[str, Any]]):
    # Stack de nodos (cada nodo es {label: str, children: List})
    node_stack: List[Dict[str, Any]] = []

    # Mapa rápido de producciones por índice rK
    # productions[0] se asume "S' -> S"; rK usa ese mismo índice
    for row in trace_rows:
        action = row.get('action', '')
        if not action:
            continue
        if action.startswith('s'):
            # En shift, inferir el token consumido como el primer token del input actual (antes de $)
            input_str = row.get('input', '') or ''
            parts = [p for p in input_str.strip().split() if p]
            consumed = None
            for p in parts:
                if p != '$':
                    consumed = p
                    break
            if consumed is not None:
                node_stack.append({'label': consumed, 'children': []})
        elif action.startswith('r'):
            k = int(action[1:])
            production = productions[k]
            left, right = production.split(' -> ')
            right_symbols = right.split()
            children = []
            # Extraer n hijos (si ε, no hay hijos)
            if len(right_symbols) == 1 and right_symbols[0] == 'ε':
                # Nodo epsilon como hijo opcional, o nodo vacío
                children_nodes: List[Dict[str, Any]] = []
            else:
                for _ in range(len(right_symbols)):
                    if node_stack:
                        children.append(node_stack.pop())
                children.reverse()

            node = { 'label': left, 'children': children }
            node_stack.append(node)
        elif action == 'acc':
            break

    # El tope debe ser la raíz
    root = node_stack[-1] if node_stack else { 'label': '∅', 'children': [] }
    return root


def build_tree_from_table(lr1_table: Dict[str, Any], input_string: str):
    # Adaptar formato a simulador existente
    tabla_lr1 = { 'action': {}, 'goto': {}, 'productions': lr1_table['grammar']['productions'] }
    for state_data in lr1_table['table_data']:
        state_num = state_data['state']
        tabla_lr1['action'][state_num] = state_data['action']
        tabla_lr1['goto'][state_num] = state_data['goto']

    steps = simular_parsing_lr1(input_string, tabla_lr1, lr1_table['grammar']['productions'])
    # Convertir steps a trace_rows mínimos con acción
    trace_rows = [ { 'step': s.step_number, 'action': s.action, 'stack': s.stack, 'input': s.input_string } for s in steps ]
    return build_tree_from_trace(lr1_table['grammar']['productions'], trace_rows)


def lambda_handler(event, context):
    try:
        body = json.loads(event['body']) if isinstance(event.get('body'), str) else event
        if body.get('operation') != 'lr1_tree':
            return { 'statusCode': 400, 'body': json.dumps({ 'error': 'Operation must be lr1_tree' }) }

        # Inputs posibles:
        productions = body.get('productions')
        trace_rows = body.get('trace_rows')
        lr1_table = body.get('lr1_table')
        input_string = body.get('input_string')

        if trace_rows and productions:
            root = build_tree_from_trace(productions, trace_rows)
        elif lr1_table and input_string:
            root = build_tree_from_table(lr1_table, input_string)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({ 'error': 'Provide (productions + trace_rows) or (lr1_table + input_string)' })
            }

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({ 'success': True, 'operation': 'lr1_tree', 'root': root }, indent=2)
        }
    except Exception as e:
        logger.error(f"Error en lr1_tree: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({ 'error': str(e), 'success': False })
        }

event={
  "operation": "lr1_tree",
  "productions": [
    "S' -> S",
    "S -> a b",
    "S -> c d",
    "S -> e"
  ],
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
    result = lambda_handler(event, None)
    body = json.loads(result['body'])
    print(json.dumps(body, indent=2, ensure_ascii=False))
    print(f"{'='*60}")

