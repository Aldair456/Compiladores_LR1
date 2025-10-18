import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Set
from src.utils.funciones_auxiales import (
    extraer_symbols_from_grammar,
    calcular_first_table
)
from src.utils.funciones_auxiliares_table import (
    construir_conjuntos_lr1,
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


def generar_closure_table_detallada(conjuntos, productions):
    """
    Genera una tabla de cierre LR(1) detallada con información adicional.
    
    Args:
        conjuntos: Lista de conjuntos de elementos LR(1)
        productions: Lista de producciones originales
    
    Returns:
        dict: Tabla de cierre detallada
    """
    closure_data = []
    
    for i, conjunto in enumerate(conjuntos):
        # Separar elementos por tipo
        kernel_items = []
        closure_items = []
        
        for item in conjunto:
            item_str = str(item)
            
            # Determinar si es elemento kernel o de cierre
            if item.dot_position == 0 and not item.production.startswith("S' ->"):
                # Es elemento de cierre (no kernel)
                closure_items.append({
                    "item": item_str,
                    "production": item.production,
                    "dot_position": item.dot_position,
                    "lookahead": item.lookahead,
                    "type": "closure"
                })
            else:
                # Es elemento kernel
                kernel_items.append({
                    "item": item_str,
                    "production": item.production,
                    "dot_position": item.dot_position,
                    "lookahead": item.lookahead,
                    "type": "kernel"
                })
        
        # Calcular transiciones desde este estado
        transitions = {}
        symbols_after_dot = set()
        
        for item in conjunto:
            symbol = item.get_symbol_after_dot()
            if symbol:
                symbols_after_dot.add(symbol)
        
        for symbol in symbols_after_dot:
            # Contar cuántos elementos tienen este símbolo después del punto
            count = sum(1 for item in conjunto if item.get_symbol_after_dot() == symbol)
            transitions[symbol] = {
                "symbol": symbol,
                "item_count": count,
                "items": [str(item) for item in conjunto if item.get_symbol_after_dot() == symbol]
            }
        
        closure_data.append({
            "state": i,
            "kernel_items": kernel_items,
            "closure_items": closure_items,
            "total_items": len(conjunto),
            "transitions": transitions,
            "all_items": [str(item) for item in conjunto]
        })
    
    return closure_data


def generar_json_closure_table(closure_data, grammar_info, terminals, nonterminals):
    """
    Genera un JSON estructurado para mostrar la tabla de cierre LR(1).
    
    Args:
        closure_data: Datos de la tabla de cierre
        grammar_info: Información de la gramática
        terminals: Lista de terminales
        nonterminals: Lista de no terminales
    
    Returns:
        dict: JSON estructurado para la tabla de cierre
    """
    # Filtrar epsilon de terminales
    terminals_filtered = [t for t in terminals if t != 'ε']
    
    return {
        "success": True,
        "operation": "lr1_closure_table",
        "grammar": {
            "productions": grammar_info["productions"],
            "start_symbol": grammar_info["start_symbol"]
        },
        "closure_table": closure_data,
        "terminals": terminals_filtered,
        "nonterminals": nonterminals,
        "summary": {
            "total_states": len(closure_data),
            "total_terminals": len(terminals_filtered),
            "total_nonterminals": len(nonterminals),
            "total_items": sum(state["total_items"] for state in closure_data)
        }
    }


def lambda_handler(event, context):
    try:
        # Parsear el body si viene como string
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Verificar que sea operación de LR1 closure table
        if body.get('operation') != 'lr1_closure_table':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Operation must be lr1_closure_table'})
            }
        
        # Verificar que tenga gramática y first_table
        if 'grammar' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'grammar is required'})
            }
        
        if 'first_table' not in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'first_table is required for LR(1) closure'})
            }
        
        # Expandir producciones con | (pipe) en múltiples producciones
        expanded_productions = expandir_producciones_con_pipe(body['grammar']['productions'])
        print(f"Producciones expandidas: {expanded_productions}")
        
        # Extraer terminales y no terminales
        terminals, nonterminals = extraer_symbols_from_grammar(expanded_productions)
        print(f"Terminales: {terminals}")
        print(f"No terminales: {nonterminals}")
        
        # Usar la tabla FIRST proporcionada
        first_table = body['first_table']
        print(f"Tabla FIRST recibida: {first_table}")
        
        # Construir conjuntos LR(1) usando la tabla FIRST proporcionada
        conjuntos, transiciones = construir_conjuntos_lr1(
            expanded_productions,
            terminals,
            nonterminals,
            first_table
        )
        print(f"Número de estados: {len(conjuntos)}")
        
        # Generar tabla de cierre detallada
        closure_data = generar_closure_table_detallada(conjuntos, body['grammar']['productions'])
        
        # Generar JSON estructurado para la tabla de cierre
        result = generar_json_closure_table(closure_data, body['grammar'], terminals, nonterminals)
        
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


# Eventos de prueba para LR(1) Closure Table
test_events_closure = [
    # Caso 1: Gramática específica del usuario
    {
        'body': json.dumps({
            "grammar": {
                "productions": [
                    "S' -> S",
                    "S -> C C | e | a | b | c | d",
                    "C -> c C | d"
                ],
                "start_symbol": "S'"
            },
            "first_table": {
                "S'": ["c", "d", "e", "a", "b"],
                "S": ["c", "d", "e", "a", "b"],
                "C": ["c", "d"]
            },
            "operation": "lr1_closure_table"
        })
    },
    
    # Caso 2: Gramática simple
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
            "first_table": {
                "S'": ["c", "d"],
                "S": ["c", "d"],
                "C": ["c", "d"]
            },
            "operation": "lr1_closure_table"
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
            "operation": "lr1_closure_table"
        })
    },
    
    # Caso 3: Gramática simple con un terminal
    {
        'body': json.dumps({
            "grammar": {
                "productions": [
                    "S' -> S",
                    "S -> a"
                ],
                "start_symbol": "S'"
            },
            "operation": "lr1_closure_table"
        })
    }
]

def test_specific_grammar():
    """Prueba específica para la gramática del usuario"""
    print("\n" + "="*80)
    print("PRUEBA ESPECÍFICA: GRAMÁTICA DEL USUARIO")
    print("="*80)
    
    event = {
        'body': json.dumps({
            "grammar": {
                "productions": [
                    "S' -> S",
                    "S -> C C | e | a | b | c | d",
                    "C -> c C | d"
                ],
                "start_symbol": "S'"
            },
            "first_table": {
                "S'": ["c", "d", "e", "a", "b"],
                "S": ["c", "d", "e", "a", "b"],
                "C": ["c", "d"]
            },
            "operation": "lr1_closure_table"
        })
    }
    
    result = lambda_handler(event, None)
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        body = json.loads(result['body'])
        print("✓ Éxito")
        
        # Mostrar información específica del Estado 0
        if 'closure_table' in body and len(body['closure_table']) > 0:
            estado_0 = body['closure_table'][0]
            print(f"\nESTADO 0:")
            print(f"Kernel Items: {estado_0['kernel_items']}")
            print(f"Closure Items: {estado_0['closure_items']}")
            print(f"Transitions: {estado_0['transitions']}")
            
            # Verificar que no hay S' -> S' items
            all_items = estado_0['kernel_items'] + estado_0['closure_items']
            s_prime_items = [item for item in all_items if "S' -> S'" in item.get('item', '')]
            if s_prime_items:
                print(f"\n❌ ERROR: Se encontraron items S' -> S': {s_prime_items}")
            else:
                print(f"\n✅ CORRECTO: No hay items S' -> S'")
        
        print(f"\nResultado completo:")
        print(json.dumps(body, indent=2, ensure_ascii=False))
    else:
        error_body = json.loads(result['body'])
        print(f"✗ Error: {result['body']}")


if __name__ == '__main__':
    # Ejecutar prueba específica
    test_specific_grammar()
    
    # Ejecutar todas las pruebas
    all_results_closure = []
    
    for i, event in enumerate(test_events_closure, 1):
        print(f"\n{'='*60}")
        print(f"PRUEBA LR(1) CLOSURE {i}")
        print(f"{'='*60}")
        
        result = lambda_handler(event, None)
        print(f"Status Code: {result['statusCode']}")
        
        # Parsear el evento original
        event_data = json.loads(event['body'])
        
        # Crear resultado completo
        test_result = {
            "test_number": i,
            "test_name": f"Prueba LR(1) Closure {i}",
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
        
        all_results_closure.append(test_result)
    
    # Guardar todos los resultados LR(1) Closure en un archivo JSON
    output_file_closure = "test_results_lr1_closure.json"
    with open(output_file_closure, 'w', encoding='utf-8') as f:
        json.dump(all_results_closure, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print(f"RESUMEN FINAL LR(1) CLOSURE")
    print(f"{'='*60}")
    
    successful_tests = sum(1 for r in all_results_closure if r['success'])
    total_tests = len(all_results_closure)
    
    print(f"Tests LR(1) Closure exitosos: {successful_tests}/{total_tests}")
    print(f"Tasa de éxito: {(successful_tests/total_tests)*100:.1f}%")
    print(f"Resultados LR(1) Closure guardados en: {output_file_closure}")
