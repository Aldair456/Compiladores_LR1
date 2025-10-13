import json
import os
import logging
from datetime import datetime
from typing import Dict, Any
from src.utils.funciones_auxiales import (
    extraer_symbols_from_grammar,
    calcular_first_table,
    generar_json_first_table
)
# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def expandir_producciones_con_pipe(productions):
    """
    Expande las producciones que contienen el símbolo | (pipe) en múltiples producciones separadas.
    
    Args:
        productions: Lista de strings con las producciones
    
    Returns:
        list: Lista de producciones expandidas sin pipes
    """
    expanded = []
    
    for production in productions:
        if ' | ' in production:
            # Dividir por el pipe
            left, right_part = production.split(' -> ')
            alternatives = right_part.split(' | ')
            
            for alt in alternatives:
                expanded.append(f"{left.strip()} -> {alt.strip()}")
        else:
            # Si no tiene pipe, mantener como está
            expanded.append(production)
    
    return expanded


def lambda_handler(event, context):
    try:
        # Parsear el body si viene como string
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event
        
        # Verificar que sea operación de FIRST table
        if body.get('operation') != 'first_table':
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Operation must be first_table'})
            }
        
        # Verificar que solo tenga gramática (no debe tener first_table)
        if 'first_table' in body:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'FIRST handler only needs grammar, not first_table'})
            }
        
        # Expandir producciones con | (pipe) en múltiples producciones
        expanded_productions = expandir_producciones_con_pipe(body['grammar']['productions'])
        print(f"Producciones expandidas: {expanded_productions}")
        
        # Extraer terminales y no terminales
        terminals, nonterminals = extraer_symbols_from_grammar(expanded_productions)
        print(f"Terminales: {terminals}")
        print(f"No terminales: {nonterminals}")
        
        # Calcular tabla FIRST
        first_table = calcular_first_table(
            expanded_productions, 
            terminals, 
            nonterminals
        )
        print(f"Tabla FIRST: {first_table}")
        
        # Generar JSON estructurado para la tabla
        result = generar_json_first_table(first_table, body['grammar'])
        
        # Mostrar información específica sobre no terminales
        nonterminals_first = {k: v for k, v in first_table.items() 
                             if k.isupper() or (k.startswith(k[0].upper()) and "'" in k)}
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
        logger.error(f"Error en lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e), 'success': False})
        }



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


result = lambda_handler(event, None)
resultado_body=result['body']
print(resultado_body)