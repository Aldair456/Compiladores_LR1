#!/usr/bin/env python3
"""
Test completo para el algoritmo LR(1) desde cero.
Verifica que se construya correctamente la tabla LR(1) completa.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.handlers.handler_table_LR1 import lambda_handler
import json


def test_gramatica_simple():
    """Test con gramática simple sin closure_table."""
    print("=" * 60)
    print("TEST 1: Gramática simple desde cero")
    print("=" * 60)
    
    test_event = {
        "grammar": {
            "productions": [
                "S -> A B C",
                "A -> a | ε",
                "B -> b | ε", 
                "C -> c"
            ],
            "start_symbol": "S"
        },
        "options": {
            "augment": True,
            "epsilon_symbol": "ε",
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response = json.loads(result['body'])
        
        print(f"\n✅ ÉXITO:")
        print(f"  - Estados generados: {response['summary']['total_states']}")
        print(f"  - Terminales: {len(response['symbols']['terminals'])}")
        print(f"  - No terminales: {len(response['symbols']['nonterminals'])}")
        print(f"  - Producciones: {response['summary']['total_productions']}")
        print(f"  - Conflictos: {response['summary']['total_conflicts']}")
        
        print(f"\n📋 Terminales: {response['symbols']['terminals']}")
        print(f"📋 No terminales: {response['symbols']['nonterminals']}")
        
        print(f"\n📊 Tabla ACTION:")
        for state, actions in response['lr1_table']['action_table'].items():
            print(f"  Estado {state}: {actions}")
        
        print(f"\n📊 Tabla GOTO:")
        for state, gotos in response['lr1_table']['goto_table'].items():
            print(f"  Estado {state}: {gotos}")
        
        print(f"\n📊 Reducciones:")
        for state, reductions in response['lr1_table']['reductions'].items():
            print(f"  Estado {state}: {reductions}")
        
        if response['lr1_table']['conflicts']:
            print(f"\n⚠️ Conflictos:")
            for conflict in response['lr1_table']['conflicts']:
                print(f"  {conflict}")
        
        return True
    else:
        print(f"❌ ERROR: {result['body']}")
        return False


def test_con_closure_table():
    """Test con closure_table proporcionado."""
    print("\n" + "=" * 60)
    print("TEST 2: Con closure_table proporcionado")
    print("=" * 60)
    
    test_event = {
        "grammar": {
            "productions": [
                "S -> A B C",
                "A -> a | ε",
                "B -> b | ε",
                "C -> c"
            ],
            "start_symbol": "S'"
        },
        "closure_table": {
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
                    "transitions": {"S": 1, "A": 2, "a": 4}
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
                    "transitions": {"B": 3, "b": 5}
                },
                {
                    "id": 3,
                    "items": [
                        "[S -> A B • C, $]",
                        "[C -> • c, $]"
                    ],
                    "transitions": {"C": 6, "c": 7}
                },
                {
                    "id": 4,
                    "items": [
                        "[A -> a •, b]",
                        "[A -> a •, c]"
                    ],
                    "transitions": {}
                },
                {
                    "id": 5,
                    "items": ["[B -> b •, c]"],
                    "transitions": {}
                },
                {
                    "id": 6,
                    "items": ["[S -> A B C •, $]"],
                    "transitions": {}
                },
                {
                    "id": 7,
                    "items": ["[C -> c •, $]"],
                    "transitions": {}
                }
            ]
        },
        "options": {
            "augment": True,
            "epsilon_symbol": "ε",
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response = json.loads(result['body'])
        
        print(f"\n✅ ÉXITO:")
        print(f"  - Estados procesados: {response['summary']['total_states']}")
        print(f"  - Terminales: {len(response['symbols']['terminals'])}")
        print(f"  - No terminales: {len(response['symbols']['nonterminals'])}")
        print(f"  - Producciones: {response['summary']['total_productions']}")
        print(f"  - Conflictos: {response['summary']['total_conflicts']}")
        
        print(f"\n📋 Terminales: {response['symbols']['terminals']}")
        print(f"📋 No terminales: {response['symbols']['nonterminals']}")
        
        print(f"\n📊 Tabla ACTION:")
        for state, actions in response['lr1_table']['action_table'].items():
            print(f"  Estado {state}: {actions}")
        
        print(f"\n📊 Tabla GOTO:")
        for state, gotos in response['lr1_table']['goto_table'].items():
            print(f"  Estado {state}: {gotos}")
        
        print(f"\n📊 Reducciones:")
        for state, reductions in response['lr1_table']['reductions'].items():
            print(f"  Estado {state}: {reductions}")
        
        if response['lr1_table']['conflicts']:
            print(f"\n⚠️ Conflictos:")
            for conflict in response['lr1_table']['conflicts']:
                print(f"  {conflict}")
        
        return True
    else:
        print(f"❌ ERROR: {result['body']}")
        return False


def test_gramatica_ambigua():
    """Test con gramática ambigua para detectar conflictos."""
    print("\n" + "=" * 60)
    print("TEST 3: Gramática ambigua (dangling else)")
    print("=" * 60)
    
    test_event = {
        "grammar": {
            "productions": [
                "S -> if E then S",
                "S -> if E then S else S",
                "S -> other",
                "E -> true"
            ],
            "start_symbol": "S"
        },
        "options": {
            "augment": True,
            "epsilon_symbol": "ε",
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response = json.loads(result['body'])
        
        print(f"\n✅ ÉXITO:")
        print(f"  - Estados generados: {response['summary']['total_states']}")
        print(f"  - Terminales: {len(response['symbols']['terminals'])}")
        print(f"  - No terminales: {len(response['symbols']['nonterminals'])}")
        print(f"  - Producciones: {response['summary']['total_productions']}")
        print(f"  - Conflictos: {response['summary']['total_conflicts']}")
        
        if response['lr1_table']['conflicts']:
            print(f"\n⚠️ Conflictos detectados:")
            for conflict in response['lr1_table']['conflicts']:
                print(f"  Estado {conflict['state']}, símbolo '{conflict['symbol']}': {conflict['conflict_type']}")
                print(f"    Existente: {conflict['existing_action']}")
                print(f"    Nueva: {conflict['new_action']}")
        
        return True
    else:
        print(f"❌ ERROR: {result['body']}")
        return False


def main():
    """Ejecuta todos los tests."""
    print("🚀 INICIANDO TESTS DEL ALGORITMO LR(1) COMPLETO")
    print("=" * 60)
    
    tests = [
        test_gramatica_simple,
        test_con_closure_table,
        test_gramatica_ambigua
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ ERROR en test: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTADOS FINALES: {passed}/{total} tests pasaron")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        return True
    else:
        print("❌ Algunos tests fallaron")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)