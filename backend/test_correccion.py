#!/usr/bin/env python3
"""
Test simple para verificar la corrección del handler de tabla LR(1)
"""

import json
from src.handlers.handler_table_LR1 import lambda_handler


def test_correccion():
    """Test de corrección con gramática simple"""
    
    print("="*60)
    print("TEST DE CORRECCIÓN - TABLA LR(1)")
    print("="*60)
    
    # Gramática de prueba
    grammar = {
        "productions": [
            "S -> A B C",
            "A -> a | ε",
            "B -> b | ε",
            "C -> c"
        ],
        "start_symbol": "S'"
    }
    
    # Closure table de prueba
    closure_table = {
        "states": [
            {
                "id": 0,
                "items": [
                    "[S' -> • S, $]",
                    "[S -> • A B C, $]",
                    "[A -> • a, b]",
                    "[A -> • ε, b]",
                    "[A -> • a, c]",
                    "[A -> • ε, c]"
                ],
                "transitions": {"S": 1, "A": 2}
            },
            {
                "id": 1,
                "items": ["[S' -> S •, $]"],
                "transitions": {}
            },
            {
                "id": 2,
                "items": [
                    "[S -> A • B C, $]",
                    "[B -> • b, c]",
                    "[B -> • ε, c]"
                ],
                "transitions": {"B": 3}
            },
            {
                "id": 3,
                "items": [
                    "[S -> A B • C, $]",
                    "[C -> • c, $]"
                ],
                "transitions": {"C": 4}
            },
            {
                "id": 4,
                "items": ["[S -> A B C •, $]"],
                "transitions": {}
            }
        ]
    }
    
    # Evento de prueba
    test_event = {
        "grammar": grammar,
        "closure_table": closure_table,
        "operation": "lr1_table",
        "options": {
            "augment": True,
            "epsilon_symbol": "ε",
            "end_marker": "$"
        }
    }
    
    print("Entrada:")
    print(f"  Gramática: {grammar['productions']}")
    print(f"  Símbolo inicial: {grammar['start_symbol']}")
    print(f"  Estados: {len(closure_table['states'])}")
    
    # Ejecutar handler
    result = lambda_handler(test_event, None)
    
    print(f"\nStatus Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        print("✅ Éxito!")
        
        response_data = json.loads(result['body'])
        
        # Verificar estructura básica
        print(f"\nVerificaciones:")
        print(f"  Success: {response_data['success']}")
        print(f"  Operation: {response_data['operation']}")
        
        # Verificar gramática
        grammar_info = response_data['grammar']
        print(f"\nGramática:")
        print(f"  Augmented: {grammar_info['augmented']}")
        print(f"  Start symbol: {grammar_info['start_symbol']}")
        print(f"  Original start symbol: {grammar_info['original_start_symbol']}")
        print(f"  Original productions: {grammar_info['original_productions']}")
        print(f"  Expanded productions: {grammar_info['expanded_productions']}")
        
        # Verificar tabla LR(1)
        lr1_table = response_data['lr1_table']
        print(f"\nTabla LR(1):")
        print(f"  ACTION table:")
        for state_id, actions in lr1_table['action_table'].items():
            if actions:
                print(f"    Estado {state_id}: {actions}")
        
        print(f"  GOTO table:")
        for state_id, gotos in lr1_table['goto_table'].items():
            if gotos:
                print(f"    Estado {state_id}: {gotos}")
        
        print(f"  Reductions: {len(lr1_table['reductions'])}")
        for state_id, reductions in lr1_table['reductions'].items():
            print(f"    Estado {state_id}: {reductions}")
        
        print(f"  Conflicts: {len(lr1_table['conflicts'])}")
        for conflict in lr1_table['conflicts']:
            print(f"    {conflict}")
        
        # Verificar símbolos
        symbols = response_data['symbols']
        print(f"\nSímbolos:")
        print(f"  Terminales: {symbols['terminals']}")
        print(f"  No terminales: {symbols['nonterminals']}")
        
        # Verificar producciones
        productions_table = response_data['productions_table']
        print(f"\nProducciones numeradas:")
        for prod in productions_table:
            print(f"  {prod['number']}: {prod['production']}")
        
        # Verificar resumen
        summary = response_data['summary']
        print(f"\nResumen:")
        print(f"  Total estados: {summary['total_states']}")
        print(f"  Total terminales: {summary['total_terminals']}")
        print(f"  Total no terminales: {summary['total_nonterminals']}")
        print(f"  Total producciones: {summary['total_productions']}")
        print(f"  Total conflictos: {summary['total_conflicts']}")
        
        return response_data
    else:
        print("❌ Error!")
        print(f"Response: {result['body']}")
        return None


if __name__ == "__main__":
    test_correccion()


