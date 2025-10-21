import logging
from typing import Dict, Any, List, Set, Tuple, Optional
from src.utils.lr1_class import LR1, LR1Item
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
    AWS Lambda handler para construir la LR(1) Closure Table.
    
    Args:
        event: Evento con gramática y opciones
        context: Contexto de Lambda
    
    Returns:
        dict: Respuesta JSON con la Closure Table
    """
    try:
        # Parsear el body
        body = parse_request_body(event)
        
        # Log de información del request
        log_request_info("lr1_closure", body)
        
        # Validar entrada
        if 'start_symbol' not in body:
            return validation_error_response("start_symbol es obligatorio", "start_symbol")
        
        if 'productions' not in body:
            return validation_error_response("productions es obligatorio", "productions")
        
        # Obtener parámetros
        start_symbol = body['start_symbol']
        productions = body['productions']
        options = body.get('options', {})
        
        # Configurar opciones por defecto
        augment = options.get('augment', True)
        expand_alternatives = options.get('expand_alternatives', True)
        epsilon_symbol = options.get('epsilon_symbol', 'ε')
        end_marker = options.get('end_marker', '$')
        
        logger.info(f"Procesando gramática: start_symbol={start_symbol}, productions={len(productions)}")
        logger.info(f"Opciones: augment={augment}, expand_alternatives={expand_alternatives}")
        
        # Crear instancia LR1
        lr1 = LR1(productions, start_symbol)
        
        # Aplicar aumentación si es necesario
        if augment:
            augmented_productions = lr1.aumentar_gramatica(start_symbol, end_marker)
            logger.info(f"Gramática aumentada: {augmented_productions}")
        else:
            augmented_productions = lr1.obtener_producciones_expandidas()
        
        # Actualizar la instancia con las producciones aumentadas
        lr1.expanded_productions = augmented_productions
        lr1.terminals, lr1.nonterminals = lr1._extract_symbols_from_grammar(augmented_productions)
        
        # Calcular FIRST y FOLLOW
        lr1.calcular_first()
        lr1.calcular_follow()
        
        logger.info("Calculando colección canónica LR(1)")
        
        # Construir colección canónica LR(1)
        estados, transiciones = lr1.construir_coleccion_lr1()
        
        logger.info(f"Colección construida: {len(estados)} estados, {len(transiciones)} transiciones")
        
        # Generar respuesta
        response = _generar_respuesta_exitosa(
            lr1, start_symbol, productions, augmented_productions,
            estados, transiciones, augment, epsilon_symbol, end_marker
        )
        
        logger.info("LR(1) Closure Table construida exitosamente")
        return response
        
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return internal_error_response(e, "Error construyendo Closure Table", include_traceback=True)


def _generar_respuesta_exitosa(
    lr1: LR1,
    original_start_symbol: str,
    original_productions: List[str],
    augmented_productions: List[str],
    estados: List[Set[LR1Item]],
    transiciones: Dict[Tuple[int, str], int],
    augment: bool,
    epsilon_symbol: str,
    end_marker: str
) -> Dict[str, Any]:
    """
    Genera la respuesta exitosa con la Closure Table.
    
    Args:
        lr1: Instancia de LR1
        original_start_symbol: Símbolo inicial original
        original_productions: Producciones originales
        augmented_productions: Producciones aumentadas
        estados: Lista de estados LR(1)
        transiciones: Diccionario de transiciones
        augment: Si se aplicó aumentación
        epsilon_symbol: Símbolo epsilon
        end_marker: Marcador de fin
    
    Returns:
        dict: Respuesta exitosa
    """
    # Determinar símbolo inicial final
    final_start_symbol = "S'" if augment else original_start_symbol
    
    # Construir estados para la respuesta
    states_data = []
    for i, estado in enumerate(estados):
        # Convertir ítems a strings legibles
        items_strings = [str(item) for item in sorted(estado, key=str)]
        
        # Construir transiciones desde este estado
        state_transitions = {}
        for (estado_origen, simbolo), estado_destino in transiciones.items():
            if estado_origen == i:
                state_transitions[simbolo] = estado_destino
        
        states_data.append({
            "id": i,
            "items": items_strings,
            "transitions": state_transitions
        })
    
    response_data = {
        "success": True,
        "grammar": {
            "augmented": augment,
            "start_symbol": final_start_symbol,
            "original_start_symbol": original_start_symbol,
            "epsilon": epsilon_symbol,
            "end_marker": end_marker,
            "original_productions": original_productions,
            "expanded_productions": augmented_productions
        },
        "closure_table": {
            "states": states_data
        }
    }
    
    return success_response(response_data)


# Ejemplo de uso para pruebas
if __name__ == "__main__":
    # Evento de prueba
    # 1) Aritmética clásica (E→E+T|T, T→T*F|F, F→(E)|id)
    test_event = {
    "start_symbol": "E",
    "productions": [
        "E -> E + T | T",
        "T -> T * F | F",
        "F -> ( E ) | id"
    ],
    "options": {
        "augment": True,
        "expand_alternatives": True
    }
}

    
    result = lambda_handler(test_event, None)
    print(f"Status Code: {result['statusCode']}")
    print(f"Response: {result['body']}")
