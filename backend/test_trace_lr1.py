#!/usr/bin/env python3
"""
Test completo para el handler_lr1_trace.py
Verifica que el trace LR(1) funcione correctamente.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.handlers.handler_lr1_trace import lambda_handler
import json


def test_cadena_valida():
    """Test con cadena válida."""
    print("=" * 60)
    print("TEST 1: Cadena válida 'a b c'")
    print("=" * 60)
    
    # Tabla LR(1) del ejemplo anterior
    lr1_table = {
        "action_table": {
            "0": {"a": "s4"},
            "1": {"$": "acc"},
            "2": {"b": "s5"},
            "3": {"c": "s7"},
            "4": {"b": "r2", "c": "r2"},
            "5": {"c": "r4"},
            "6": {"$": "r1"},
            "7": {"$": "r6"}
        },
        "goto_table": {
            "0": {"S": 1, "A": 2},
            "1": {},
            "2": {"B": 3},
            "3": {"C": 6},
            "4": {},
            "5": {},
            "6": {},
            "7": {}
        },
        "reductions": {
            "4": {
                "b": {"production": "A -> a", "production_number": 2},
                "c": {"production": "A -> a", "production_number": 2}
            },
            "5": {
                "c": {"production": "B -> b", "production_number": 4}
            },
            "6": {
                "$": {"production": "S -> A B C", "production_number": 1}
            },
            "7": {
                "$": {"production": "C -> c", "production_number": 6}
            }
        }
    }
    
    test_event = {
        "lr1_table": lr1_table,
        "input_string": "a b c",
        "options": {
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response = json.loads(result['body'])
        
        print(f"\n✅ RESULTADO:")
        print(f"  Aceptada: {response['accepted']}")
        print(f"  Pasos totales: {response['summary']['total_steps']}")
        print(f"  Estado final: {response['summary']['final_state']}")
        print(f"  Tokens procesados: {response['summary']['tokens_processed']}")
        
        print(f"\n📋 TRACE DETALLADO:")
        for step in response['trace_steps']:
            print(f"  Paso {step['step']}: Estado {step['state']}, Token '{step['current_token']}', Acción: {step['action']}")
            print(f"    {step['description']}")
            print(f"    Stack: {step['stack']}")
        
        return True
    else:
        print(f"❌ ERROR: {result['body']}")
        return False


def test_cadena_invalida():
    """Test con cadena inválida."""
    print("\n" + "=" * 60)
    print("TEST 2: Cadena inválida 'a b d'")
    print("=" * 60)
    
    # Misma tabla LR(1)
    lr1_table = {
        "action_table": {
            "0": {"a": "s4"},
            "1": {"$": "acc"},
            "2": {"b": "s5"},
            "3": {"c": "s7"},
            "4": {"b": "r2", "c": "r2"},
            "5": {"c": "r4"},
            "6": {"$": "r1"},
            "7": {"$": "r6"}
        },
        "goto_table": {
            "0": {"S": 1, "A": 2},
            "1": {},
            "2": {"B": 3},
            "3": {"C": 6},
            "4": {},
            "5": {},
            "6": {},
            "7": {}
        },
        "reductions": {
            "4": {
                "b": {"production": "A -> a", "production_number": 2},
                "c": {"production": "A -> a", "production_number": 2}
            },
            "5": {
                "c": {"production": "B -> b", "production_number": 4}
            },
            "6": {
                "$": {"production": "S -> A B C", "production_number": 1}
            },
            "7": {
                "$": {"production": "C -> c", "production_number": 6}
            }
        }
    }
    
    test_event = {
        "lr1_table": lr1_table,
        "input_string": "a b d",  # 'd' no es válido
        "options": {
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response = json.loads(result['body'])
        
        print(f"\n✅ RESULTADO:")
        print(f"  Aceptada: {response['accepted']}")
        print(f"  Error: {response.get('error', 'N/A')}")
        print(f"  Pasos hasta error: {response['summary']['total_steps']}")
        
        print(f"\n📋 TRACE HASTA ERROR:")
        for step in response['trace_steps']:
            print(f"  Paso {step['step']}: Estado {step['state']}, Token '{step['current_token']}', Acción: {step['action']}")
            print(f"    {step['description']}")
        
        return True
    else:
        print(f"❌ ERROR: {result['body']}")
        return False


def test_cadena_con_epsilon():
    """Test con cadena que usa producciones epsilon."""
    print("\n" + "=" * 60)
    print("TEST 3: Cadena con epsilon 'a c'")
    print("=" * 60)
    
    # Tabla LR(1) que incluye producciones epsilon
    lr1_table = {
        "action_table": {
            "0": {"a": "s1"},
            "1": {"b": "r2", "c": "r2"},
            "2": {"b": "r3", "c": "r3"},
            "3": {"$": "acc"},
            "4": {"b": "s5"},
            "5": {"c": "r4"},
            "6": {"c": "s7"},
            "7": {"$": "r6"},
            "8": {"$": "r1"}
        },
        "goto_table": {
            "0": {"S": 3, "A": 4},
            "1": {},
            "2": {},
            "3": {},
            "4": {"B": 6},
            "5": {},
            "6": {"C": 8},
            "7": {},
            "8": {}
        },
        "reductions": {
            "1": {
                "b": {"production": "A -> a", "production_number": 2},
                "c": {"production": "A -> a", "production_number": 2}
            },
            "2": {
                "b": {"production": "A -> ε", "production_number": 3},
                "c": {"production": "A -> ε", "production_number": 3}
            },
            "5": {
                "c": {"production": "B -> b", "production_number": 4}
            },
            "6": {
                "c": {"production": "B -> ε", "production_number": 5}
            },
            "7": {
                "$": {"production": "C -> c", "production_number": 6}
            },
            "8": {
                "$": {"production": "S -> A B C", "production_number": 1}
            }
        }
    }
    
    test_event = {
        "lr1_table": lr1_table,
        "input_string": "a c",  # A -> a, B -> ε, C -> c
        "options": {
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    result = lambda_handler(test_event, None)
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response = json.loads(result['body'])
        
        print(f"\n✅ RESULTADO:")
        print(f"  Aceptada: {response['accepted']}")
        print(f"  Pasos totales: {response['summary']['total_steps']}")
        
        print(f"\n📋 TRACE DETALLADO:")
        for step in response['trace_steps']:
            print(f"  Paso {step['step']}: Estado {step['state']}, Token '{step['current_token']}', Acción: {step['action']}")
            print(f"    {step['description']}")
        
        return True
    else:
        print(f"❌ ERROR: {result['body']}")
        return False


def main():
    """Ejecuta todos los tests."""
    print("🚀 INICIANDO TESTS DEL TRACE LR(1)")
    print("=" * 60)
    
    tests = [
        test_cadena_valida,
        test_cadena_invalida,
        test_cadena_con_epsilon
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
