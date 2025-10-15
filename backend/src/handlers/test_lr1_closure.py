#!/usr/bin/env python3
"""
Prueba del handler_lr1_closure.py
"""

import json
from src.handlers.handler_lr1_closure import lambda_handler


def probar_ejemplo_basico():
    """Prueba el ejemplo básico del prompt"""
    
    print("PROBANDO EJEMPLO BÁSICO")
    print("="*50)
    
    # Evento de prueba del prompt
    test_event = {
        "start_symbol": "S",
        "productions": ["S -> A A", "A -> a A | b"],
        "options": {
            "augment": True,
            "expand_alternatives": True
        }
    }
    
    print("Input:")
    print(f"  start_symbol: {test_event['start_symbol']}")
    print(f"  productions: {test_event['productions']}")
    print(f"  options: {test_event['options']}")
    
    # Llamar al lambda_handler
    result = lambda_handler(test_event, None)
    
    print(f"\nStatus Code: {result['statusCode']}")
    
    if result['statusCode'] == 200:
        body_data = json.loads(result['body'])
        
        print("✓ Éxito")
        print(f"\nGramática:")
        print(f"  Augmented: {body_data['grammar']['augmented']}")
        print(f"  Start Symbol: {body_data['grammar']['start_symbol']}")
        print(f"  Original Start Symbol: {body_data['grammar']['original_start_symbol']}")
        print(f"  Original Productions: {body_data['grammar']['original_productions']}")
        print(f"  Expanded Productions: {body_data['grammar']['expanded_productions']}")
        
        print(f"\nClosure Table:")
        print(f"  Total States: {len(body_data['closure_table']['states'])}")
        
        # Mostrar estado 0 (debería tener [S' -> • S, $])
        state_0 = body_data['closure_table']['states'][0]
        print(f"\nState 0:")
        print(f"  Items: {state_0['items']}")
        print(f"  Transitions: {state_0['transitions']}")
        
        # Verificar que tiene el elemento inicial
        has_initial = any("[S' -> • S, $]" in item for item in state_0['items'])
        print(f"  ✓ Tiene elemento inicial [S' -> • S, $]: {has_initial}")
        
        return body_data
    else:
        print("✗ Error")
        print(result['body'])
        return None


def probar_sin_aumentacion():
    """Prueba sin aumentación"""
    
    print("\n\nPROBANDO SIN AUMENTACIÓN")
    print("="*50)
    
    test_event = {
        "start_symbol": "S",
        "productions": ["S -> A A", "A -> a A | b"],
        "options": {
            "augment": False,
            "expand_alternatives": True
        }
    }
    
    result = lambda_handler(test_event, None)
    
    if result['statusCode'] == 200:
        body_data = json.loads(result['body'])
        
        print("✓ Éxito sin aumentación")
        print(f"  Augmented: {body_data['grammar']['augmented']}")
        print(f"  Start Symbol: {body_data['grammar']['start_symbol']}")
        print(f"  Total States: {len(body_data['closure_table']['states'])}")
        
        return body_data
    else:
        print("✗ Error")
        print(result['body'])
        return None


def probar_con_error():
    """Prueba manejo de errores"""
    
    print("\n\nPROBANDO MANEJO DE ERRORES")
    print("="*50)
    
    # Evento con error (falta start_symbol)
    test_event = {
        "productions": ["S -> A A", "A -> a A | b"]
        # Falta start_symbol
    }
    
    result = lambda_handler(test_event, None)
    
    print(f"Status Code: {result['statusCode']}")
    print(f"Response: {result['body']}")
    
    return result


if __name__ == "__main__":
    # Ejecutar todas las pruebas
    probar_ejemplo_basico()
    probar_sin_aumentacion()
    probar_con_error()
