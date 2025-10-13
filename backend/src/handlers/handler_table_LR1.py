import json
import os
import logging
from datetime import datetime
from typing import Dict, Any
from src.utils.funciones_auxiales import (
    extraer_symbols_from_grammar,
    calcular_first_table
)
from src.utils.funciones_auxiliares_table import (
    construir_conjuntos_lr1,
    generar_tabla_lr1,
    generar_json_tabla_lr1,
    LR1Item
)

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def expandir_producciones_con_pipe(productions):
    """
    Expande las producciones que contienen el símbolo | (pipe) en múltiples producciones separadas.
    
    Args:
        productions: Lista de strings con las producciones
    
    Returns:
        list: Lista de producciones expandidas sin pipes
    """
    expanded = []
    
    for production in productions:
        # Normalizar espacios alrededor de '->'
        if '->' in production:
            left, right_part = production.split('->', 1)
        else:
            left, right_part = production.split(' -> ', 1)
        left = left.strip()
        right_part = right_part.strip()

        # Separar alternativas por '|', sin depender de espacios
        alternatives = [alt.strip() for alt in right_part.split('|')]

        # Si no hay '|', alternatives tendrá un solo elemento
        for alt in alternatives:
            expanded.append(f"{left} -> {alt}")
    
    return expanded


def lambda_handler(event, context):
    try:
        # Parsear el body si viene como string
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Verificar que sea operación de LR1 table
        if body.get('operation') != 'lr1_table':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Operation must be lr1_table'})
            }
        
        # Verificar que tenga gramática y closure_data
        if 'grammar' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'grammar is required'})
            }
        
        if 'closure_data' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'closure_data is required for LR(1) table'})
            }
        
        # Expandir producciones con | (pipe) en múltiples producciones
        expanded_productions = expandir_producciones_con_pipe(body['grammar']['productions'])
        print(f"Producciones expandidas: {expanded_productions}")
        
        # Extraer terminales y no terminales
        terminals, nonterminals = extraer_symbols_from_grammar(expanded_productions)
        print(f"Terminales: {terminals}")
        print(f"No terminales: {nonterminals}")
        
        # Usar los conjuntos LR(1) proporcionados
        closure_data = body['closure_data']
        print(f"Datos de cierre recibidos: {len(closure_data)} estados")
        
        # Reconstruir conjuntos y transiciones desde closure_data
        conjuntos = []
        transiciones = {}
        
        # Mapa normalizado de item (como string) -> estado
        item_a_estado = {}
        
        def parsear_item(item_str: str):
            """Parsea un item del formato texto a LR1Item normalizado."""
            # Dividir por la coma para separar producción y lookahead
            if ', ' in item_str:
                prod_part, lookahead = item_str.split(', ')
                lookahead = lookahead.strip()
            else:
                prod_part = item_str
                lookahead = '$'
            
            # Encontrar el punto (•) para determinar la posición (por token)
            if '•' in prod_part:
                # Calcular posición del punto como índice de token
                try:
                    _left_tmp, right_tmp = prod_part.split('->', 1)
                    right_tokens_with_dot = right_tmp.strip().split()
                    dot_pos = right_tokens_with_dot.index('•')
                except Exception:
                    dot_pos = 0
                # Remover el punto para obtener la producción limpia
                production_raw = prod_part.replace('•', '').strip()
                # Normalizar espacios en la producción (evitar "S ->  e")
                if '->' in production_raw:
                    left_part, right_part = production_raw.split('->', 1)
                    left_part = left_part.strip()
                    right_symbols = right_part.strip().split()
                    production = f"{left_part} -> {' '.join(right_symbols)}"
                else:
                    production = ' '.join(production_raw.split())
                return LR1Item(production, dot_pos, lookahead)
            else:
                # Si no hay punto, asumir posición 0
                production_raw = prod_part.strip()
                # Normalizar espacios en la producción
                if '->' in production_raw:
                    left_part, right_part = production_raw.split('->', 1)
                    left_part = left_part.strip()
                    right_symbols = right_part.strip().split()
                    production = f"{left_part} -> {' '.join(right_symbols)}"
                else:
                    production = ' '.join(production_raw.split())
                return LR1Item(production, 0, lookahead)
        
        # Extraer conjuntos desde closure_data y poblar mapa item->estado
        for state_data in closure_data:
            estado_num = state_data['state']
            conjunto = set()
            for item_str in state_data['all_items']:
                try:
                    item = parsear_item(item_str)
                    conjunto.add(item)
                    # Usar la representación normalizada para mapear
                    item_a_estado[str(item)] = estado_num
                except Exception as e:
                    print(f"Error parseando item '{item_str}': {e}")
                    continue
            conjuntos.append(conjunto)
        
        # Deducir transiciones avanzando el punto y buscando el estado destino
        for i, conjunto in enumerate(conjuntos):
            for item in conjunto:
                symbol = item.get_symbol_after_dot()
                if not symbol:
                    continue
                avanzado = LR1Item(item.production, item.dot_position + 1, item.lookahead)
                clave = str(avanzado)
                estado_destino = item_a_estado.get(clave)
                if estado_destino is not None:
                    transiciones[(i, symbol)] = estado_destino
        
        # Generar tabla ACTION/GOTO usando los conjuntos reconstruidos y transiciones deducidas
        tabla_lr1 = generar_tabla_lr1(
            conjuntos,
            transiciones,
            expanded_productions,
            terminals,
            nonterminals
        )
        
        # Generar JSON estructurado para la tabla
        result = generar_json_tabla_lr1(tabla_lr1, body['grammar'], terminals, nonterminals)
        
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


event = {
  "grammar": {
    "productions": [
      "S' -> S",
      "S -> a b| c d| e"
    ],
    "start_symbol": "S'"
  },
  "closure_data": [
    {
      "state": 0,
      "kernel_items": [
        {
          "item": "S' -> • S, $",
          "production": "S' -> S",
          "dot_position": 0,
          "lookahead": "$",
          "type": "kernel"
        }
      ],
      "closure_items": [
        {
          "item": "S -> • e, $",
          "production": "S -> e",
          "dot_position": 0,
          "lookahead": "$",
          "type": "closure"
        },
        {
          "item": "S -> • a b, $",
          "production": "S -> a b",
          "dot_position": 0,
          "lookahead": "$",
          "type": "closure"
        },
        {
          "item": "S -> • c d, $",
          "production": "S -> c d",
          "dot_position": 0,
          "lookahead": "$",
          "type": "closure"
        }
      ],
      "all_items": [
        "S -> • e, $",
        "S -> • a b, $",
        "S -> • c d, $",
        "S' -> • S, $"
      ]
    },
    {
      "state": 1,
      "kernel_items": [
        {
          "item": "S -> e •, $",
          "production": "S -> e",
          "dot_position": 1,
          "lookahead": "$",
          "type": "kernel"
        }
      ],
      "closure_items": [],
      "all_items": [
        "S -> e •, $"
      ]
    },
    {
      "state": 2,
      "kernel_items": [
        {
          "item": "S -> c • d, $",
          "production": "S -> c d",
          "dot_position": 1,
          "lookahead": "$",
          "type": "kernel"
        }
      ],
      "closure_items": [],
      "all_items": [
        "S -> c • d, $"
      ]
    },
    {
      "state": 3,
      "kernel_items": [
        {
          "item": "S' -> S •, $",
          "production": "S' -> S",
          "dot_position": 1,
          "lookahead": "$",
          "type": "kernel"
        }
      ],
      "closure_items": [],
      "all_items": [
        "S' -> S •, $"
      ]
    },
    {
      "state": 4,
      "kernel_items": [
        {
          "item": "S -> a • b, $",
          "production": "S -> a b",
          "dot_position": 1,
          "lookahead": "$",
          "type": "kernel"
        }
      ],
      "closure_items": [],
      "all_items": [
        "S -> a • b, $"
      ]
    },
    {
      "state": 5,
      "kernel_items": [
        {
          "item": "S -> c d •, $",
          "production": "S -> c d",
          "dot_position": 2,
          "lookahead": "$",
          "type": "kernel"
        }
      ],
      "closure_items": [],
      "all_items": [
        "S -> c d •, $"
      ]
    },
    {
      "state": 6,
      "kernel_items": [
        {
          "item": "S -> a b •, $",
          "production": "S -> a b",
          "dot_position": 2,
          "lookahead": "$",
          "type": "kernel"
        }
      ],
      "closure_items": [],
      "all_items": [
        "S -> a b •, $"
      ]
    }
  ],
  "operation": "lr1_table"
}
if __name__ == '__main__':
    print(json.dumps(event, indent=2, ensure_ascii=False))
    result = lambda_handler(event, None)
    resultado_json=result['body']
    print(json.dumps(resultado_json, indent=2, ensure_ascii=False))
