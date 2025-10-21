"""
AWS Lambda handler para trace/validación de cadenas usando tabla LR(1).
"""

import logging
from typing import Dict, Any

from src.utils.trace_processor import ejecutar_trace_lr1
from src.utils.response_helpers import (
    parse_request_body,
    success_response,
    error_response,
    internal_error_response,
    log_request_info,
    validate_required_fields
)

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler para hacer trace/validación de cadenas usando tabla LR(1).
    
    Recibe como entrada:
    - lr1_table: Tabla LR(1) completa (action_table, goto_table, reductions)
    - input_string: Cadena de entrada a validar
    - options: Opciones de configuración
    
    Args:
        event: Evento con tabla LR(1) y cadena de entrada
        context: Contexto de Lambda
    
    Returns:
        dict: Respuesta JSON con el trace del parsing
    """
    try:
        # Parsear el body
        body = parse_request_body(event)
        
        # Log de información del request
        log_request_info("lr1_trace", body)
        
        # Validar campos requeridos en el body
        validation_error = validate_required_fields(body, ['lr1_table', 'input_string'])
        if validation_error:
            return validation_error
        
        lr1_table = body['lr1_table']
        input_string = body['input_string']
        options = body.get('options', {})
        
        # Validar estructura de tabla LR(1)
        validation_error = validate_required_fields(
            lr1_table, 
            ['action_table', 'goto_table', 'reductions']
        )
        if validation_error:
            return validation_error
        
        # Configurar opciones
        end_marker = options.get('end_marker', '$')
        accept_token = options.get('accept_token', 'acc')
        
        logger.info(f"Procesando cadena: '{input_string}' con tabla LR(1)")
        
        # Ejecutar trace LR(1)
        trace_result = ejecutar_trace_lr1(
            lr1_table, input_string, end_marker, accept_token
        )
        
        logger.info(f"Trace completado: {trace_result['accepted']}")
        
        # Generar respuesta HTTP
        return success_response(trace_result)
        
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return internal_error_response(e, "Error ejecutando trace LR(1)", include_traceback=True)
