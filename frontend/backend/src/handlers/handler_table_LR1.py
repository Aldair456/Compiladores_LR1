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
        
        # Extraer conjuntos desde closure_data
        for state_data in closure_data:
            # Reconstruir conjunto de elementos LR(1)
            conjunto = set()
            for item_str in state_data['all_items']:
                # Parsear item string para reconstruir LR1Item
                # Formato: "S' -> •S, $"
                try:
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
                            left_tmp, right_tmp = prod_part.split('->', 1)
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
                        
                        # Crear objeto LR1Item
                        item = LR1Item(production, dot_pos, lookahead)
                        conjunto.add(item)
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
                        item = LR1Item(production, 0, lookahead)
                        conjunto.add(item)
                        
                except Exception as e:
                    print(f"Error parseando item '{item_str}': {e}")
                    continue
            
            conjuntos.append(conjunto)
        
        # Generar tabla ACTION/GOTO usando los conjuntos reconstruidos
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


# Evento de prueba para LR(1)
test_event = {
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
        "operation": "lr1_table"
    })
}

# Eventos de prueba para LR(1)
test_events_lr1 = [
    # Caso 1: Gramática simple
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
            "operation": "lr1_table"
        })
    },
    
    # Caso 2: Gramática con epsilon
    {
        'body': json.dumps({
            "grammar": {
                "productions": [
                    "S' -> S",
                    "S -> A B",
                    "A -> a",
                    "A -> ε",
                    "B -> b",
                    "B -> ε"
                ],
                "start_symbol": "S'"
            },
            "operation": "lr1_table"
        })
    },
    
    # Caso 3: Gramática de expresiones
    {
        'body': json.dumps({
            "grammar": {
                "productions": [
                    "S' -> E",
                    "E -> E + T",
                    "E -> T",
                    "T -> T * F",
                    "T -> F",
                    "F -> ( E )",
                    "F -> id"
                ],
                "start_symbol": "S'"
            },
            "operation": "lr1_table"
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
            "operation": "lr1_table"
        })
    }
]

if __name__ == '__main__':
    all_results_lr1 = []
    
    for i, event in enumerate(test_events_lr1, 1):
        print(f"\n{'='*60}")
        print(f"PRUEBA LR(1) {i}")
        print(f"{'='*60}")
        
        result = lambda_handler(event, None)
        print(f"Status Code: {result['statusCode']}")
        
        # Parsear el evento original
        event_data = json.loads(event['body'])
        
        # Crear resultado completo
        test_result = {
            "test_number": i,
            "test_name": f"Prueba LR(1) {i}",
            "grammar": event_data["grammar"],
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
        
        all_results_lr1.append(test_result)
    
    # Guardar todos los resultados LR(1) en un archivo JSON
    output_file_lr1 = "test_results_lr1.json"
    with open(output_file_lr1, 'w', encoding='utf-8') as f:
        json.dump(all_results_lr1, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL LR(1)")
    print(f"{'='*60}")
    
    successful_tests = sum(1 for r in all_results_lr1 if r['success'])
    total_tests = len(all_results_lr1)
    
    print(f"Tests LR(1) exitosos: {successful_tests}/{total_tests}")
    print(f"Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")
    print(f"Resultados LR(1) guardados en: {output_file_lr1}")