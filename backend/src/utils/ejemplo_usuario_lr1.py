#!/usr/bin/env python3
"""
Ejemplo específico para el caso del usuario.
Simula exactamente el comportamiento del lambda_handler que proporcionaste.
"""

from src.utils.lr1_class import LR1


def simular_lambda_handler(event):
    """
    Simula el comportamiento del lambda_handler proporcionado por el usuario.
    
    Args:
        event: Evento con gramática y operación
    
    Returns:
        dict: Resultado similar al lambda_handler
    """
    try:
        # Verificar que sea operación de FIRST table
        if event.get('operation') != 'first_table':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Operation must be first_table'})
            }
        
        # Verificar que solo tenga gramática (no debe tener first_table)
        if 'first_table' in event:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'FIRST handler only needs grammar, not first_table'})
            }
        
        # Crear instancia LR1
        productions = event['grammar']['productions']
        start_symbol = event['grammar']['start_symbol']
        lr1 = LR1(productions, start_symbol)
        
        # Obtener información
        terminals = lr1.obtener_terminals()
        nonterminals = lr1.obtener_nonterminals()
        first_table = lr1.calcular_first()
        follow_table = lr1.calcular_follow()
        
        # Generar resultado similar al lambda_handler original
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
        
        # Mostrar información específica sobre no terminales (como en el original)
        nonterminals_first = lr1.obtener_first_no_terminales()
        print(f"\nFIRST para No Terminales:")
        for nt, first_set in nonterminals_first.items():
            print(f"  FIRST({nt}) = {{{', '.join(sorted(first_set))}}}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result, indent=2)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e), 'success': False})
        }


def ejemplo_usuario():
    """Ejemplo usando exactamente el evento proporcionado por el usuario"""
    
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
    
    print("EJEMPLO DEL USUARIO")
    print("="*60)
    
    # Simular lambda_handler
    result = simular_lambda_handler(event)
    
    print(f"Status Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        print("✓ Éxito")
        print(f"\nBody del resultado:")
        print(result['body'])
    else:
        print("✗ Error")
        print(result['body'])
    
    return result


def ejemplo_directo_con_clase():
    """Ejemplo usando directamente la clase LR1"""
    
    print("\n\nEJEMPLO DIRECTO CON CLASE LR1")
    print("="*60)
    
    # Gramática del usuario
    productions = [
        "S -> A B C",
        "A -> a | ε",
        "B -> b | ε",
        "C -> c"
    ]
    
    # Crear instancia
    lr1 = LR1(productions, "S'")
    
    # Obtener información directamente
    print(f"Terminales: {lr1.obtener_terminals()}")
    print(f"No Terminales: {lr1.obtener_nonterminals()}")
    print(f"Símbolo Inicial: {lr1.obtener_simbolo_inicial()}")
    
    # Calcular FIRST y FOLLOW
    first_table = lr1.calcular_first()
    follow_table = lr1.calcular_follow()
    
    print(f"\nFIRST Table completa:")
    for symbol, first_set in first_table.items():
        print(f"  FIRST({symbol}) = {first_set}")
    
    print(f"\nFOLLOW Table:")
    for symbol, follow_set in follow_table.items():
        print(f"  FOLLOW({symbol}) = {follow_set}")
    
    # Generar resumen completo
    print(f"\nResumen completo:")
    resumen = lr1.generar_resumen()
    print(f"Producciones expandidas: {resumen['grammar']['expanded_productions']}")
    
    return lr1


if __name__ == "__main__":
    import json
    
    # Ejecutar ejemplos
    ejemplo_usuario()
    ejemplo_directo_con_clase()
