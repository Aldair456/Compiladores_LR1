import os
import logging
from datetime import datetime
from typing import Dict, Any
from src.utils.lr1_class import LR1
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


def lambda_handler(event, context):
    try:
        # Parsear el body
        body = parse_request_body(event)
        
        # Log de información del request
        log_request_info("first_table", body)
        
        # Verificar que sea operación de FIRST table
        if body.get('operation') != 'first_table':
            return error_response('Operation must be first_table', status_code=400)
        
        # Verificar que solo tenga gramática (no debe tener first_table)
        if 'first_table' in body:
            return error_response('FIRST handler only needs grammar, not first_table', status_code=400)
        
        # Crear instancia LR1 con la gramática
        productions = body['grammar']['productions']
        start_symbol = body['grammar']['start_symbol']
        
        # Si el símbolo inicial es S', asegurar que existe la producción aumentada
        if start_symbol == "S'":
            # Verificar si ya existe la producción aumentada
            augmented_exists = any(p.startswith("S' ->") for p in productions)
            if not augmented_exists:
                # Encontrar el símbolo inicial real (no S')
                real_start = None
                for production in productions:
                    left = production.split(' -> ')[0].strip()
                    if left != "S'":
                        real_start = left
                        break
                
                if real_start:
                    # Agregar producción aumentada al inicio
                    productions = [f"S' -> {real_start}"] + productions
                    print(f"Agregada producción aumentada: S' -> {real_start}")
        
        lr1 = LR1(productions, start_symbol)
        
        print(f"Producciones expandidas: {lr1.obtener_producciones_expandidas()}")
        print(f"Terminales: {lr1.obtener_terminals()}")
        print(f"No terminales: {lr1.obtener_nonterminals()}")
        
        # Calcular tabla FIRST usando la clase LR1
        first_table = lr1.calcular_first()
        print(f"Tabla FIRST: {first_table}")
        
        # Generar resultado estructurado para tablas en frontend
        terminals = lr1.obtener_terminals()
        nonterminals = lr1.obtener_nonterminals()
        first_sets = lr1.obtener_first_no_terminales()
        follow_sets = lr1.calcular_follow()
        
        # Crear tabla FIRST para frontend
        first_table_data = []
        for symbol, first_set in first_sets.items():
            first_table_data.append({
                "symbol": symbol,
                "first_set": first_set,
                "first_string": ", ".join(sorted(first_set))
            })
        
        # Crear tabla FOLLOW para frontend
        follow_table_data = []
        for symbol, follow_set in follow_sets.items():
            follow_table_data.append({
                "symbol": symbol,
                "follow_set": follow_set,
                "follow_string": ", ".join(sorted(follow_set))
            })
        
        # Crear tabla de producciones para frontend
        productions_table_data = []
        for i, production in enumerate(lr1.obtener_producciones_expandidas()):
            productions_table_data.append({
                "id": i + 1,
                "production": production,
                "left_side": production.split(' -> ')[0].strip(),
                "right_side": production.split(' -> ')[1].strip()
            })
        
        result = {
            "success": True,
            "operation": "first_table",
            "grammar": {
                "original_productions": body['grammar']['productions'],
                "augmented_productions": productions,
                "start_symbol": start_symbol,
                "expanded_productions": lr1.obtener_producciones_expandidas(),
                "is_augmented": start_symbol == "S'",
                "real_start_symbol": lr1.obtener_simbolo_inicial()
            },
            "symbols": {
                "terminals": terminals,
                "nonterminals": nonterminals
            },
            "tables": {
                "first_table": first_table_data,
                "follow_table": follow_table_data,
                "productions_table": productions_table_data
            },
            "raw_data": {
                "first_sets": first_sets,
                "follow_sets": follow_sets
            },
            "summary": {
                "total_terminals": len(terminals),
                "total_nonterminals": len(nonterminals),
                "total_productions": len(lr1.obtener_producciones_expandidas())
            }
        }
        
        # Mostrar información específica sobre no terminales
        nonterminals_first = lr1.obtener_first_no_terminales()
        print(f"\nFIRST para No Terminales:")
        for nt, first_set in nonterminals_first.items():
            print(f"  FIRST({nt}) = {{{', '.join(sorted(first_set))}}}")
        
        return success_response(result)
        
    except ValueError as e:
        return error_response(str(e), status_code=400)
    except Exception as e:
        return internal_error_response(e, "Error calculando tabla FIRST", include_traceback=True)



event = {
    "grammar": {
        "productions": [
            "S -> A B C",
            "A -> a",
            "B -> b D",
            "C -> c",
            "D -> d | e | a"
        ],
        "start_symbol": "S"
    },
    "operation": "first_table"
}

result = lambda_handler(event, None)
resultado_body=result['body']
print(resultado_body)