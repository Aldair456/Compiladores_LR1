import logging
from typing import Dict, Any, List, Optional

from src.utils.tree_builder import construir_arbol_derivacion
from src.utils.response_helpers import (
    parse_request_body,
    success_response,
    error_response,
    validation_error_response,
    internal_error_response,
    log_request_info
)

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
        # Parsear el body
        body = parse_request_body(event)
        
        # Log de información del request
        log_request_info("lr1_tree", body)
        
        # Validar entrada obligatoria
        if 'trace_steps' not in body:
            return validation_error_response("trace_steps es obligatorio", "trace_steps")
        
        trace_steps = body['trace_steps']
        grammar = body.get('grammar')  # Opcional
        
        logger.info(f"Procesando {len(trace_steps)} pasos del trace")
        
        # Construir árbol de derivación usando la función de utils
        logger.info("Construyendo árbol de derivación")
        derivation_tree = construir_arbol_derivacion(trace_steps, grammar)
        
        logger.info("Árbol de derivación construido exitosamente")
        
        # Generar respuesta HTTP
        return success_response(derivation_tree)
        
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return internal_error_response(e, "Error construyendo árbol de derivación", include_traceback=True)
