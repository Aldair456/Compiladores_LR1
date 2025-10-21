"""
Utilidades comunes para handlers de AWS Lambda.
Incluye helpers para respuestas HTTP, parseo de requests, y manejo de errores.
"""

import json
import logging
from typing import Dict, Any, Optional

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Headers CORS comunes para todas las respuestas
CORS_HEADERS = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS'
}


def parse_request_body(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parsea el body del request de Lambda.
    
    Si el body viene como string JSON, lo parsea.
    Si ya es un dict, lo devuelve tal cual.
    
    Args:
        event: Evento de Lambda
    
    Returns:
        dict: Body parseado
    
    Raises:
        ValueError: Si el body no se puede parsear
    """
    try:
        if isinstance(event.get('body'), str):
            return json.loads(event['body'])
        else:
            return event
    except json.JSONDecodeError as e:
        logger.error(f"Error parseando body: {str(e)}")
        raise ValueError(f"JSON inválido en el body: {str(e)}")


def success_response(
    data: Dict[str, Any],
    status_code: int = 200,
    additional_headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Genera una respuesta HTTP exitosa para Lambda.
    
    Args:
        data: Datos a devolver en el body
        status_code: Código de estado HTTP (default: 200)
        additional_headers: Headers adicionales opcionales
    
    Returns:
        dict: Respuesta HTTP de Lambda
    """
    headers = CORS_HEADERS.copy()
    
    if additional_headers:
        headers.update(additional_headers)
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(data, indent=2, ensure_ascii=False)
    }


def error_response(
    message: str,
    status_code: int = 400,
    details: Optional[Dict[str, Any]] = None,
    additional_headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Genera una respuesta HTTP de error para Lambda.
    
    Args:
        message: Mensaje de error principal
        status_code: Código de estado HTTP (default: 400)
        details: Detalles adicionales del error (opcional)
        additional_headers: Headers adicionales opcionales
    
    Returns:
        dict: Respuesta HTTP de error de Lambda
    """
    headers = CORS_HEADERS.copy()
    
    if additional_headers:
        headers.update(additional_headers)
    
    error_data = {
        "success": False,
        "error": message
    }
    
    if details:
        error_data["details"] = details
    
    return {
        'statusCode': status_code,
        'headers': headers,
        'body': json.dumps(error_data, indent=2, ensure_ascii=False)
    }


def validation_error_response(
    message: str,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Genera una respuesta de error de validación (400).
    
    Args:
        message: Mensaje de error de validación
        field: Campo que falló la validación (opcional)
        details: Detalles adicionales (opcional)
    
    Returns:
        dict: Respuesta HTTP de error de validación
    """
    error_details = details or {}
    
    if field:
        error_details['field'] = field
    
    return error_response(
        message=message,
        status_code=400,
        details=error_details if error_details else None
    )


def internal_error_response(
    exception: Exception,
    message: str = "Error interno del servidor",
    include_traceback: bool = False
) -> Dict[str, Any]:
    """
    Genera una respuesta de error interno del servidor (500).
    
    Args:
        exception: Excepción capturada
        message: Mensaje de error personalizado
        include_traceback: Si incluir traceback en la respuesta (default: False)
    
    Returns:
        dict: Respuesta HTTP de error interno
    """
    logger.error(f"Error interno: {str(exception)}")
    
    details = {
        "exception_type": type(exception).__name__,
        "exception_message": str(exception)
    }
    
    if include_traceback:
        import traceback
        details["traceback"] = traceback.format_exc()
        traceback.print_exc()
    
    return error_response(
        message=message,
        status_code=500,
        details=details
    )


def validate_required_fields(
    body: Dict[str, Any],
    required_fields: list[str]
) -> Optional[Dict[str, Any]]:
    """
    Valida que los campos requeridos estén presentes en el body.
    
    Args:
        body: Body del request
        required_fields: Lista de campos requeridos
    
    Returns:
        dict: Respuesta de error si falta algún campo, None si todo está bien
    """
    for field in required_fields:
        if field not in body:
            return validation_error_response(
                message=f"{field} es obligatorio",
                field=field
            )
    
    return None


def log_request_info(operation: str, body: Dict[str, Any]) -> None:
    """
    Log de información del request para debugging.
    
    Args:
        operation: Nombre de la operación
        body: Body del request
    """
    logger.info(f"=== Iniciando operación: {operation} ===")
    logger.info(f"Body keys: {list(body.keys())}")
    
    # Log selectivo de campos relevantes (evitar loggear datos sensibles masivos)
    if 'start_symbol' in body:
        logger.info(f"start_symbol: {body['start_symbol']}")
    
    if 'productions' in body:
        logger.info(f"productions count: {len(body['productions'])}")
    
    if 'input_string' in body:
        logger.info(f"input_string: {body['input_string']}")

