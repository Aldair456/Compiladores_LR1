#!/usr/bin/env python3
"""
Debug detallado del closure LR(1)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.lr1_class import LR1, LR1Item

def debug_closure_step_by_step():
    """Debug paso a paso del closure"""
    
    productions = [
        "S' -> S",
        "S -> a A", 
        "A -> b"
    ]
    start_symbol = "S'"
    
    lr1 = LR1(productions, start_symbol)
    lr1.calcular_first()
    lr1.calcular_follow()
    
    print("=== DEBUGGING CLOSURE STEP BY STEP ===")
    print(f"Expanded productions: {lr1.expanded_productions}")
    print(f"Nonterminals: {lr1.nonterminals}")
    print(f"Terminals: {lr1.terminals}")
    print()
    
    # Crear elemento inicial
    initial_item = LR1Item("S' -> S", 0, '$')
    print(f"Initial item: {initial_item}")
    print(f"Symbol after dot: {initial_item.get_symbol_after_dot()}")
    print()
    
    closure_set = {initial_item}
    iteration = 0
    
    while True:
        iteration += 1
        print(f"=== ITERATION {iteration} ===")
        print(f"Current closure_set size: {len(closure_set)}")
        
        changed = False
        items_to_process = list(closure_set)
        
        for item in items_to_process:
            symbol_after_dot = item.get_symbol_after_dot()
            print(f"Processing item: {item}")
            print(f"  Symbol after dot: {symbol_after_dot}")
            
            if symbol_after_dot and symbol_after_dot in lr1.nonterminals:
                print(f"  {symbol_after_dot} is nonterminal, looking for productions...")
                
                # Buscar producciones que empiecen con este símbolo
                for production in lr1.expanded_productions:
                    left, right = production.split(' -> ')
                    left = left.strip()
                    
                    if left == symbol_after_dot:
                        print(f"    Found production: {production}")
                        
                        # Calcular FIRST(βa) donde β son los símbolos después del punto
                        item_left, item_right = item.production.split(' -> ')
                        item_right_symbols = item_right.split()
                        
                        # Símbolos después del punto (β)
                        beta = []
                        if item.dot_position + 1 < len(item_right_symbols):
                            beta = item_right_symbols[item.dot_position + 1:]
                        
                        print(f"    Beta (symbols after dot): {beta}")
                        print(f"    Lookahead: {item.lookahead}")
                        
                        # Calcular FIRST(βa)
                        lookaheads = lr1.first_of_beta_a(beta, item.lookahead)
                        print(f"    FIRST(βa) = {lookaheads}")
                        
                        for lookahead in lookaheads:
                            if lookahead != 'ε':  # No agregar ε como lookahead
                                new_item = LR1Item(production, 0, lookahead)
                                print(f"    Creating new item: {new_item}")
                                if new_item not in closure_set:
                                    closure_set.add(new_item)
                                    changed = True
                                    print(f"    ADDED to closure_set")
                                else:
                                    print(f"    Already exists in closure_set")
            else:
                print(f"  {symbol_after_dot} is terminal or None, skipping")
        
        print(f"Changed: {changed}")
        print(f"Closure_set after iteration {iteration}:")
        for item in sorted(closure_set, key=str):
            print(f"  {item}")
        print()
        
        if not changed:
            break
    
    print("=== FINAL RESULT ===")
    for item in sorted(closure_set, key=str):
        print(f"  {item}")

if __name__ == "__main__":
    debug_closure_step_by_step()
