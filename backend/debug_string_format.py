#!/usr/bin/env python3
"""
Debug del formato de strings en el closure
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.lr1_class import LR1, LR1Item

def debug_string_format():
    """Debug del formato de strings"""
    
    productions = [
        "S' -> S",
        "S -> a A", 
        "A -> b"
    ]
    start_symbol = "S'"
    
    lr1 = LR1(productions, start_symbol)
    lr1.calcular_first()
    lr1.calcular_follow()
    
    initial_item = LR1Item("S' -> S", 0, '$')
    closure_set = lr1.closure({initial_item})
    
    print("=== DEBUGGING STRING FORMAT ===")
    print("Closure set items:")
    for i, item in enumerate(sorted(closure_set, key=str)):
        print(f"  {i}: '{str(item)}'")
        print(f"      repr: {repr(str(item))}")
    
    print("\nLooking for A -> • b patterns:")
    closure_strings = [str(item) for item in closure_set]
    for i, item_str in enumerate(closure_strings):
        if "A ->" in item_str and "b" in item_str:
            print(f"  Found A -> b pattern in item {i}: '{item_str}'")
            print(f"  Contains 'A -> • b': {'A -> • b' in item_str}")
            print(f"  Contains 'A ->  • b': {'A ->  • b' in item_str}")

if __name__ == "__main__":
    debug_string_format()

