import logging
from typing import Dict, Any, Optional, List
from src.utils.lr1_class import construir_tabla_lr1_completa
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
        # Parsear el body
        body = parse_request_body(event)
        
        # Log de información del request
        log_request_info("table_lr1", body)
        
        # Validar entrada obligatoria
        if 'grammar' not in body:
            return validation_error_response("grammar es obligatorio", "grammar")
        
        grammar = body['grammar']
        if 'productions' not in grammar:
            return validation_error_response("grammar.productions es obligatorio", "productions")
        
        if 'start_symbol' not in grammar:
            return validation_error_response("grammar.start_symbol es obligatorio", "start_symbol")
        
        # Obtener parámetros
        closure_table = body.get('closure_table')  # Opcional
        options = body.get('options', {})
        
        logger.info(f"Procesando gramática: start_symbol={grammar['start_symbol']}, productions={len(grammar['productions'])}")
        logger.info(f"Closure table proporcionada: {closure_table is not None}")
        
        # Construir tabla LR(1) completa
        logger.info("Construyendo tabla LR(1) completa")
        response_data = construir_tabla_lr1_completa(grammar, options, closure_table)
        
        logger.info(f"Tabla LR(1) construida: {response_data['summary']['total_states']} estados, {response_data['summary']['total_conflicts']} conflictos")
        
        logger.info("Tabla LR(1) construida exitosamente")
        return success_response(response_data)
        
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return internal_error_response(e, "Error construyendo tabla LR(1)", include_traceback=True)

