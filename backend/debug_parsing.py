#!/usr/bin/env python3
"""
Test de debug para verificar el parsing de items LR(1).
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.lr1_class import parsear_item_string, LR1Item


def test_parsing_items():
    """Test del parsing de items LR(1)."""
    print("=" * 60)
    print("TEST DE PARSING DE ITEMS LR(1)")
    print("=" * 60)
    
    # Items de prueba
    test_items = [
        "[S' -> • S, $]",
        "[S -> A • B C, $]",
        "[A -> a •, b]",
        "[A -> ε •, c]",
        "[A ->  • a, b]",  # Con espacios extra
        "[A ->  • ε, b]",  # Con espacios extra
    ]
    
    for item_str in test_items:
        print(f"\n📋 Parsing: '{item_str}'")
        item = parsear_item_string(item_str)
        
        if item:
            print(f"  ✅ Éxito:")
            print(f"    - Producción: '{item.production}'")
            print(f"    - Posición punto: {item.dot_position}")
            print(f"    - Lookahead: '{item.lookahead}'")
            print(f"    - Es reducción: {item.is_reduce_item()}")
            print(f"    - Símbolo después del punto: {item.get_symbol_after_dot()}")
            print(f"    - String reconstruido: '{str(item)}'")
        else:
            print(f"  ❌ Error: No se pudo parsear")


def test_closure_construction():
    """Test de construcción de closure."""
    print("\n" + "=" * 60)
    print("TEST DE CONSTRUCCIÓN DE CLOSURE")
    print("=" * 60)
    
    # Gramática simple
    productions = [
        "S -> A B C",
        "A -> a | ε",
        "B -> b | ε",
        "C -> c"
    ]
    
    lr1 = LR1(productions, "S")
    lr1.calcular_first()
    lr1.calcular_follow()
    
    print(f"📋 Gramática:")
    for prod in productions:
        print(f"  {prod}")
    
    print(f"\n📋 FIRST Sets:")
    first_table = lr1.calcular_first()
    for symbol, first_set in first_table.items():
        if symbol in lr1.nonterminals:
            print(f"  FIRST({symbol}) = {{{', '.join(first_set)}}}")
    
    print(f"\n📋 FOLLOW Sets:")
    follow_table = lr1.calcular_follow()
    for symbol, follow_set in follow_table.items():
        print(f"  FOLLOW({symbol}) = {{{', '.join(follow_set)}}}")
    
    # Construir colección LR(1)
    print(f"\n📋 Construyendo colección LR(1)...")
    estados, transiciones = lr1.construir_coleccion_lr1(debug=True)
    
    print(f"\n📊 Resultado:")
    print(f"  - Estados generados: {len(estados)}")
    print(f"  - Transiciones: {len(transiciones)}")
    
    # Mostrar algunos estados
    for i, estado in enumerate(estados[:3]):  # Solo primeros 3
        print(f"\n  Estado {i}:")
        for item in sorted(estado, key=str):
            print(f"    {item}")


if __name__ == "__main__":
    test_parsing_items()
    test_closure_construction()






