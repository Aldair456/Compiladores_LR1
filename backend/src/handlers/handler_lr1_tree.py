import json
import logging
from typing import Dict, Any, List, Optional

from src.utils.tree_builder import construir_arbol_derivacion

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler para construir el árbol de derivación desde trace_steps LR(1).
    
    Recibe como entrada:
    - trace_steps: Lista de pasos del trace LR(1)
    - grammar: Gramática opcional para validación
    
    Args:
        event: Evento con trace_steps
        context: Contexto de Lambda
    
    Returns:
        dict: Respuesta JSON con el árbol de derivación
    """
    try:
        logger.info("Iniciando construcción de árbol de derivación")
        
        # Parsear el body si viene como string
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Validar entrada obligatoria
        if 'trace_steps' not in body:
            return _error_response("trace_steps es obligatorio")
        
        trace_steps = body['trace_steps']
        grammar = body.get('grammar')  # Opcional
        
        logger.info(f"Procesando {len(trace_steps)} pasos del trace")
        
        # Construir árbol de derivación usando la función de utils
        logger.info("Construyendo árbol de derivación")
        derivation_tree = construir_arbol_derivacion(trace_steps, grammar)
        
        logger.info("Árbol de derivación construido exitosamente")
        
        # Generar respuesta HTTP
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(derivation_tree, indent=2)
        }
        
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
    # Test con el ejemplo del usuario
    test_event = {
        "success": True,
        "accepted": True,
        "operation": "lr1_trace",
        "input_string": "a b",
        "trace_steps": [
            {
                "step": 1,
                "state": 0,
                "stack": [
                    0
                ],
                "input_position": 0,
                "current_token": "a",
                "action": "s3",
                "description": "SHIFT: mover 'a' al stack, ir al estado 3"
            },
            {
                "step": 2,
                "state": 3,
                "stack": [
                    0,
                    3
                ],
                "input_position": 1,
                "current_token": "b",
                "action": "s2",
                "description": "SHIFT: mover 'b' al stack, ir al estado 2"
            },
            {
                "step": 3,
                "state": 2,
                "stack": [
                    0,
                    3,
                    2
                ],
                "input_position": 2,
                "current_token": "$",
                "action": "r2",
                "description": "REDUCE: A -> b (pop 1), GOTO(3, A) = 4"
            },
            {
                "step": 4,
                "state": 4,
                "stack": [
                    0,
                    3,
                    4
                ],
                "input_position": 2,
                "current_token": "$",
                "action": "r1",
                "description": "REDUCE: S -> a A (pop 2), GOTO(0, S) = 1"
            },
            {
                "step": 5,
                "state": 1,
                "stack": [
                    0,
                    1
                ],
                "input_position": 2,
                "current_token": "$",
                "action": "acc",
                "description": "ACCEPT: Cadena aceptada"
            }
        ],
        "summary": {
            "total_steps": 5,
            "final_state": 1,
            "stack_depth": 2,
            "tokens_processed": 3
        },
        "grammar": {
            "productions": [
                "S -> a A",
                "A -> b"
            ]
        }
    }
    
    print("=== TESTING LR1 TREE HANDLER ===")
    result = lambda_handler(test_event, None)
    print(f"Status Code: {result['statusCode']}")
    if result['statusCode'] == 200:
        print("\n📋 ÁRBOL DE DERIVACIÓN:")
        print(result['body'])