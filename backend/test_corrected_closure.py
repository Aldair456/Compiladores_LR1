#!/usr/bin/env python3
"""
Test específico para verificar que la corrección del closure funciona
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.lr1_class import LR1, LR1Item

def test_corrected_closure():
    """Test de la corrección del closure"""
    
    # Gramática del usuario
    productions = [
        "S' -> S",
        "S -> a A", 
        "A -> b"
    ]
    start_symbol = "S'"
    
    print("=== TESTING CORRECTED CLOSURE ===")
    print(f"Grammar: {productions}")
    print(f"Start symbol: {start_symbol}")
    print()
    
    # Crear instancia LR1
    lr1 = LR1(productions, start_symbol)
    
    # Calcular FIRST y FOLLOW
    lr1.calcular_first()
    lr1.calcular_follow()
    
    # Crear elemento inicial
    initial_item = LR1Item("S' -> S", 0, '$')
    print(f"Initial item: {initial_item}")
    print()
    
    # Calcular closure
    closure_set = lr1.closure({initial_item})
    
    print("Closure set:")
    for item in sorted(closure_set, key=str):
        print(f"  {item}")
    print()
    
    # Verificar elementos específicos
    closure_strings = [str(item) for item in closure_set]
    
    expected_items = [
        "[S' -> • S, $]",
        "[S -> • a A, $]", 
        "[A -> • b, $]"
    ]
    
    print("Verification:")
    all_found = True
    for expected in expected_items:
        # Buscar con flexibilidad en espacios
        found = False
        for closure_str in closure_strings:
            # Normalizar espacios para comparación
            normalized_expected = expected.replace("•", "•").replace(" ", " ")
            normalized_closure = closure_str.replace("•", "•").replace(" ", " ")
            
            if normalized_expected.replace(" ", "") == normalized_closure.replace(" ", ""):
                found = True
                break
        
        if found:
            print(f"  ✓ FOUND: {expected}")
        else:
            print(f"  ✗ MISSING: {expected}")
            all_found = False
    
    print(f"\nAll expected items found: {all_found}")
    
    # Verificar específicamente A -> • b, $
    has_a_production = any("A ->  • b" in item for item in closure_strings)
    print(f"Contains A ->  • b, $: {has_a_production}")
    
    return all_found and has_a_production

if __name__ == "__main__":
    success = test_corrected_closure()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
