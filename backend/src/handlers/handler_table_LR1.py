import json
import logging
from typing import Dict, Any, Optional, List
from src.utils.lr1_class import construir_tabla_lr1_completa

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler para construir la tabla LR(1) ACTION/GOTO.
    
    Recibe como entrada:
    - grammar: Gramática con productions y start_symbol
    - closure_table: Closure table opcional (si se proporciona, se usa tal cual)
    - options: Opciones de configuración
    
    Args:
        event: Evento con gramática y opciones
        context: Contexto de Lambda
    
    Returns:
        dict: Respuesta JSON con la tabla LR(1)
    """
    try:
        logger.info("Iniciando construcción de tabla LR(1)")
        
        # Parsear el body si viene como string
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Validar entrada obligatoria
        if 'grammar' not in body:
            return _error_response("grammar es obligatorio")
        
        grammar = body['grammar']
        if 'productions' not in grammar:
            return _error_response("grammar.productions es obligatorio")
        
        if 'start_symbol' not in grammar:
            return _error_response("grammar.start_symbol es obligatorio")
        
        # Obtener parámetros
        closure_table = body.get('closure_table')  # Opcional
        options = body.get('options', {})
        
        logger.info(f"Procesando gramática: start_symbol={grammar['start_symbol']}, productions={len(grammar['productions'])}")
        logger.info(f"Closure table proporcionada: {closure_table is not None}")
        
        # Construir tabla LR(1) completa
        logger.info("Construyendo tabla LR(1) completa")
        response_data = construir_tabla_lr1_completa(grammar, options, closure_table)
        
        logger.info(f"Tabla LR(1) construida: {response_data['summary']['total_states']} estados, {response_data['summary']['total_conflicts']} conflictos")
        
        # Generar respuesta HTTP
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(response_data, indent=2)
        }
        
        logger.info("Tabla LR(1) construida exitosamente")
        return response
        
    except Exception as e:
        logger.error(f"Error en lambda_handler: {str(e)}")
        import traceback
        traceback.print_exc()
        return _error_response(f"Error interno: {str(e)}")


def _error_response(message: str, details: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Genera respuesta de error.
    
    Args:
        message: Mensaje de error
        details: Detalles adicionales opcionales
    
    Returns:
        dict: Respuesta de error
    """
    response = {
        "success": False,
        "error": message
    }
    
    if details:
        response["details"] = details
    
    return {
        'statusCode': 400,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(response, indent=2)
    }


# Ejemplo de uso para pruebas
if __name__ == "__main__":
    # Test 1: Solo gramática (construye desde cero)
    test_event_1 = {
        "grammar": {
            "productions": [
                "S -> A B C",
                "A -> a | ε",
                "B -> b | ε",
                "C -> c"
            ],
            "start_symbol": "S"
        },
        "options": {
            "augment": True,
            "epsilon_symbol": "ε",
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    print("=== TEST 1: Solo gramática ===")
    result1 = lambda_handler(test_event_1, None)
    print(f"Status Code: {result1['statusCode']}")
    if result1['statusCode'] == 200:
        print("\n📋 JSON COMPLETO:")
        print(result1['body'])
    
    # Test 2: Con closure_table
    test_event_2 = {
        "grammar": {
            "productions": [
                "S -> A B C",
                "A -> a | ε",
                "B -> b | ε",
                "C -> c"
            ],
            "start_symbol": "S'"
        },
        "closure_table": {
            "states": [
                {
                    "id": 0,
                    "items": ["[S' -> • S, $]", "[S -> • A B C, $]", "[A -> • a, b]", "[A -> • ε, b]", "[A -> • a, c]", "[A -> • ε, c]"],
                    "transitions": {"S": 1, "A": 2, "a": 4}
                },
                {
                    "id": 1,
                    "items": ["[S' -> S •, $]"],
                    "transitions": {}
                },
                {
                    "id": 2,
                    "items": ["[S -> A • B C, $]", "[B -> • b, c]", "[B -> • ε, c]"],
                    "transitions": {"B": 3, "b": 5}
                },
                {
                    "id": 3,
                    "items": ["[S -> A B • C, $]", "[C -> • c, $]"],
                    "transitions": {"C": 6, "c": 7}
                },
                {
                    "id": 4,
                    "items": ["[A -> a •, b]", "[A -> a •, c]"],
                    "transitions": {}
                },
                {
                    "id": 5,
                    "items": ["[B -> b •, c]"],
                    "transitions": {}
                },
                {
                    "id": 6,
                    "items": ["[S -> A B C •, $]"],
                    "transitions": {}
                },
                {
                    "id": 7,
                    "items": ["[C -> c •, $]"],
                    "transitions": {}
                }
            ]
        },
        "options": {
            "augment": True,
            "epsilon_symbol": "ε",
            "end_marker": "$",
            "accept_token": "acc"
        }
    }
    
    print("\n=== TEST 2: Con closure_table ===")
    result2 = lambda_handler(test_event_2, None)
    print(f"Status Code: {result2['statusCode']}")
    if result2['statusCode'] == 200:
        print("\n📋 JSON COMPLETO:")
        print(result2['body'])