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
        
        # Extraer terminales y no terminales
        terminals, nonterminals = extraer_symbols_from_grammar(body['grammar']['productions'])
        print(f"Terminales: {terminals}")
        print(f"No terminales: {nonterminals}")
        
        # Usar la tabla FIRST proporcionada
        first_table = body['first_table']
        print(f"Tabla FIRST recibida: {first_table}")
        
        # Construir conjuntos LR(1) usando la tabla FIRST proporcionada
        conjuntos, transiciones = construir_conjuntos_lr1(
            body['grammar']['productions'],
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

if __name__ == '__main__':
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
