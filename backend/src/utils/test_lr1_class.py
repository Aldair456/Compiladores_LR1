#!/usr/bin/env python3
"""
Ejemplo simple de uso de la clase LR1 completamente independiente.
"""

from src.utils.lr1_class import LR1


def ejemplo_simple():
    """Ejemplo básico usando la clase LR1"""
    
    print("EJEMPLO SIMPLE - CLASE LR1")
    print("="*50)
    
    # Gramática del usuario
    productions = [
        "S -> A B C",
        "A -> a | ε",
        "B -> b | ε",
        "C -> c"
    ]
    
    # Crear instancia LR1
    lr1 = LR1(productions, "S'")
    
    # Obtener información básica
    print(f"Terminales: {lr1.obtener_terminals()}")
    print(f"No Terminales: {lr1.obtener_nonterminals()}")
    print(f"Símbolo Inicial: {lr1.obtener_simbolo_inicial()}")
    
    # Calcular FIRST
    print(f"\nCalculando FIRST...")
    first_table = lr1.calcular_first()
    print(f"FIRST Table:")
    for symbol, first_set in first_table.items():
        print(f"  FIRST({symbol}) = {first_set}")
    
    # Calcular FOLLOW
    print(f"\nCalculando FOLLOW...")
    follow_table = lr1.calcular_follow()
    print(f"FOLLOW Table:")
    for symbol, follow_set in follow_table.items():
        print(f"  FOLLOW({symbol}) = {follow_set}")
    
    # Obtener solo FIRST de no terminales
    print(f"\nFIRST de No Terminales:")
    first_no_terminales = lr1.obtener_first_no_terminales()
    for symbol, first_set in first_no_terminales.items():
        print(f"  FIRST({symbol}) = {first_set}")
    
    # Generar resumen completo
    print(f"\nResumen completo:")
    resumen = lr1.generar_resumen()
    print(f"Producciones expandidas: {resumen['grammar']['expanded_productions']}")
    print(f"Total terminales: {resumen['summary']['total_terminals']}")
    print(f"Total no terminales: {resumen['summary']['total_nonterminals']}")
    
    return lr1


def ejemplo_simulando_lambda_handler():
    """Simula exactamente el comportamiento del lambda_handler del usuario"""
    
    print("\n\nSIMULANDO LAMBDA_HANDLER")
    print("="*50)
    
    # Evento exacto del usuario
    event = {
        "grammar": {
            "productions": [
                "S -> A B C",
                "A -> a | ε",
                "B -> b | ε",
                "C -> c"
            ],
            "start_symbol": "S'"
        },
        "operation": "first_table"
    }
    
    # Extraer datos
    productions = event['grammar']['productions']
    start_symbol = event['grammar']['start_symbol']
    
    # Crear LR1
    lr1 = LR1(productions, start_symbol)
    
    # Obtener información (como en el lambda_handler)
    terminals = lr1.obtener_terminals()
    nonterminals = lr1.obtener_nonterminals()
    first_table = lr1.calcular_first()
    follow_table = lr1.calcular_follow()
    
    # Simular resultado del lambda_handler
    result = {
        "success": True,
        "operation": "first_table",
        "grammar": {
            "productions": productions,
            "start_symbol": start_symbol
        },
        "terminals": terminals,
        "nonterminals": nonterminals,
        "first_sets": lr1.obtener_first_no_terminales(),
        "follow_sets": follow_table,
        "summary": {
            "total_terminals": len(terminals),
            "total_nonterminals": len(nonterminals)
        }
    }
    
    print("Resultado simulado:")
    print(f"Terminales: {result['terminals']}")
    print(f"No Terminales: {result['nonterminals']}")
    print(f"FIRST Sets: {result['first_sets']}")
    print(f"FOLLOW Sets: {result['follow_sets']}")
    
    # Mostrar información específica sobre no terminales (como en el original)
    nonterminals_first = lr1.obtener_first_no_terminales()
    print(f"\nFIRST para No Terminales:")
    for nt, first_set in nonterminals_first.items():
        print(f"  FIRST({nt}) = {{{', '.join(sorted(first_set))}}}")
    
    return result


if __name__ == "__main__":
    # Ejecutar ejemplos
    ejemplo_simple()
    ejemplo_simulando_lambda_handler()

