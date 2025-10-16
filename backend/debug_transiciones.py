#!/usr/bin/env python3
"""
Test para debuggear el problema de transiciones incorrectas.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.handlers.handler_lr1_closure import lambda_handler
import json


def test_debug_transiciones():
    """Test para debuggear transiciones incorrectas."""
    print("=" * 60)
    print("DEBUG: Transiciones incorrectas")
    print("=" * 60)
    
    # Gramática simple que puede generar el problema
    test_event = {
        "start_symbol": "S",
        "productions": [
            "S -> a A",
            "A -> c"
        ],
        "options": {
            "augment": True,
            "expand_alternatives": True,
            "epsilon_symbol": "ε",
            "end_marker": "$"
        }
    }
    
    print("📋 GRAMÁTICA:")
    print("  S -> a A")
    print("  A -> c")
    print("  (Aumentada: S' -> S)")
    
    print("\n🚀 EJECUTANDO CLOSURE...")
    result = lambda_handler(test_event, None)
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        response = json.loads(result['body'])
        
        print(f"\n📊 TODOS LOS ESTADOS:")
        for state in response['closure_table']['states']:
            print(f"\n  Estado {state['id']}:")
            for item in state['items']:
                print(f"    {item}")
            if state['transitions']:
                print(f"    Transiciones: {state['transitions']}")
            else:
                print(f"    Transiciones: NINGUNA")
        
        print(f"\n🔍 ANÁLISIS DE TRANSICIONES:")
        for state in response['closure_table']['states']:
            state_id = state['id']
            items = state['items']
            transitions = state['transitions']
            
            print(f"\n  Estado {state_id}:")
            
            # Verificar cada item
            for item in items:
                if "•" in item:
                    # Extraer símbolo después del punto
                    parts = item.split("•")
                    if len(parts) > 1:
                        after_dot_part = parts[1].split(",")[0].strip()
                        if after_dot_part:
                            symbol_after_dot = after_dot_part.split()[0] if after_dot_part.split() else ""
                            print(f"    ✅ {item} → símbolo después del punto: '{symbol_after_dot}'")
                        else:
                            print(f"    ❌ {item} → NO debería tener transiciones (item completo)")
                    else:
                        print(f"    ❌ {item} → NO debería tener transiciones (item completo)")
                else:
                    print(f"    ❌ {item} → NO debería tener transiciones (item completo)")
            
            # Verificar transiciones
            if transitions:
                print(f"    Transiciones encontradas: {transitions}")
                for symbol, target_state in transitions.items():
                    print(f"      {symbol} → Estado {target_state}")
            else:
                print(f"    ✅ Sin transiciones (correcto para estado de reducción)")
        
        return True
    else:
        print(f"❌ ERROR: {result['body']}")
        return False


if __name__ == "__main__":
    test_debug_transiciones()
