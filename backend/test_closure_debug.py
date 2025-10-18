#!/usr/bin/env python3
"""
Test para debuggear el problema del closure LR(1)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.lr1_class import LR1, LR1Item

def test_closure_problem():
    """Test del problema reportado por el usuario"""
    
    # Gramática del usuario
    productions = [
        "S' -> S",
        "S -> a A", 
        "A -> b"
    ]
    start_symbol = "S'"
    
    print("=== TESTING CLOSURE PROBLEM ===")
    print(f"Grammar: {productions}")
    print(f"Start symbol: {start_symbol}")
    print()
    
    # Crear instancia LR1
    lr1 = LR1(productions, start_symbol)
    
    # Calcular FIRST y FOLLOW
    lr1.calcular_first()
    lr1.calcular_follow()
    
    print("FIRST sets:")
    for symbol, first_set in lr1.first_table.items():
        print(f"  FIRST({symbol}) = {{{', '.join(sorted(first_set))}}}")
    print()
    
    print("FOLLOW sets:")
    for symbol, follow_set in lr1.follow_table.items():
        print(f"  FOLLOW({symbol}) = {{{', '.join(sorted(follow_set))}}}")
    print()
    
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
    
    # Verificar si falta A -> • b, $
    expected_items = [
        "[S' -> • S, $]",
        "[S -> • a A, $]", 
        "[A -> • b, $]"  # Este debería estar pero no está
    ]
    
    print("Expected items:")
    for expected in expected_items:
        print(f"  {expected}")
    print()
    
    # Verificar cada item esperado
    closure_strings = [str(item) for item in closure_set]
    print("Missing items:")
    for expected in expected_items:
        if expected not in closure_strings:
            print(f"  MISSING: {expected}")
        else:
            print(f"  FOUND: {expected}")
    
    return closure_set

if __name__ == "__main__":
    test_closure_problem()

