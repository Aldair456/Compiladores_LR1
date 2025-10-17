#!/usr/bin/env python3
"""
Test para verificar que el handler de tabla LR(1) funciona correctamente
con el código existente.
"""

import json
from src.handlers.handler_table_LR1 import lambda_handler


def test_handler_completo():
    """Test completo del handler con gramática y closure_table"""
    
    print("="*80)
    print("TEST DEL HANDLER DE TABLA LR(1)")
    print("="*80)
    
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
    
    # Closure table de prueba (simplificada)
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
            "expand_alternatives": True,
            "epsilon_symbol": "ε",
            "end_marker": "$"
        }
    }
    
    print("Entrada:")
    print(f"  Gramática: {grammar['productions']}")
    print(f"  Símbolo inicial: {grammar['start_symbol']}")
    print(f"  Estados en closure_table: {len(closure_table['states'])}")
    
    # Llamar al handler
    print(f"\nEjecutando handler...")
    result = lambda_handler(test_event, None)
    
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        print("✅ Éxito!")
        
        # Parsear respuesta
        response_data = json.loads(result['body'])
        
        print(f"\nResultado:")
        print(f"  Success: {response_data['success']}")
        print(f"  Operation: {response_data['operation']}")
        
        # Mostrar gramática procesada
        grammar_info = response_data['grammar']
        print(f"\nGramática procesada:")
        print(f"  Augmented: {grammar_info['augmented']}")
        print(f"  Start symbol: {grammar_info['start_symbol']}")
        print(f"  Original start symbol: {grammar_info['original_start_symbol']}")
        print(f"  Expanded productions: {len(grammar_info['expanded_productions'])}")
        
        # Mostrar tabla LR(1)
        lr1_table = response_data['lr1_table']
        print(f"\nTabla LR(1):")
        print(f"  Estados en ACTION: {len(lr1_table['action_table'])}")
        print(f"  Estados en GOTO: {len(lr1_table['goto_table'])}")
        print(f"  Reductions: {len(lr1_table['reductions'])}")
        print(f"  Conflicts: {len(lr1_table['conflicts'])}")
        
        # Mostrar ACTION table
        print(f"\nACTION Table:")
        for state_id, actions in lr1_table['action_table'].items():
            if actions:  # Solo mostrar estados con acciones
                print(f"  Estado {state_id}: {actions}")
        
        # Mostrar GOTO table
        print(f"\nGOTO Table:")
        for state_id, gotos in lr1_table['goto_table'].items():
            if gotos:  # Solo mostrar estados con transiciones GOTO
                print(f"  Estado {state_id}: {gotos}")
        
        # Mostrar reducciones
        if lr1_table['reductions']:
            print(f"\nReductions:")
            for state_id, reductions in lr1_table['reductions'].items():
                print(f"  Estado {state_id}: {reductions}")
        
        # Mostrar conflictos
        if lr1_table['conflicts']:
            print(f"\nConflicts:")
            for conflict in lr1_table['conflicts']:
                print(f"  {conflict}")
        
        # Mostrar símbolos
        symbols = response_data['symbols']
        print(f"\nSímbolos:")
        print(f"  Terminales: {symbols['terminals']}")
        print(f"  No terminales: {symbols['nonterminals']}")
        
        # Mostrar resumen
        summary = response_data['summary']
        print(f"\nResumen:")
        print(f"  Total estados: {summary['total_states']}")
        print(f"  Total terminales: {summary['total_terminals']}")
        print(f"  Total no terminales: {summary['total_nonterminals']}")
        print(f"  Total producciones: {summary['total_productions']}")
        print(f"  Total conflictos: {summary['total_conflicts']}")
        print(f"  Tipos de conflicto: {summary['conflict_types']}")
        
        return response_data
    else:
        print("❌ Error!")
        print(f"Response: {result['body']}")
        return None


if __name__ == "__main__":
    test_handler_completo()


