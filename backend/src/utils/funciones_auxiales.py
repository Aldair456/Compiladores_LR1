
import json          
import os            
import logging       
from datetime import datetime  
from typing import Dict, Any  
from collections import defaultdict  





def extraer_symbols_from_grammar(productions):
    """
    Extrae terminales y no terminales de las producciones de una gramática.
    
    Args:
        productions: Lista de strings con las producciones (ej: ["S -> A B", "A -> a"])
    
    Returns:
        tuple: (terminales, no_terminales) - listas de símbolos
    """
    terminales = set()
    no_terminales = set()
    
    for produccion in productions:
        izquierda, derecha = produccion.split(' -> ')
        no_terminales.add(izquierda.strip())
        
        for simbolo in derecha.split():
            simbolo = simbolo.strip()
            if simbolo.islower() or simbolo in ['+', '-', '*', '/', '(', ')', '$', 'ε']:
                terminales.add(simbolo)
            elif simbolo.isupper() or (simbolo.startswith(simbolo[0].upper()) and "'" in simbolo):
                no_terminales.add(simbolo)
    
    return list(terminales), list(no_terminales)


def calcular_first_table(productions, terminals, nonterminals):
    """
    Calcula la tabla FIRST para cada símbolo de la gramática.
    
    Args:
        productions: Lista de producciones
        terminals: Lista de terminales
        nonterminals: Lista de no terminales
    
    Returns:
        dict: Diccionario con FIRST de cada símbolo
    """
    first_table = {}
    
    # Inicializar FIRST de terminales (FIRST(a) = {a})
    for terminal in terminals:
        first_table[terminal] = {terminal}
    
    # Inicializar FIRST de no terminales como conjuntos vacíos
    for nonterminal in nonterminals:
        first_table[nonterminal] = set()
    
    # Algoritmo para calcular FIRST
    changed = True
    while changed:
        changed = False
        
        for production in productions:
            left, right = production.split(' -> ')
            left = left.strip()
            right_symbols = [s.strip() for s in right.split()]
            
            # FIRST(left) += FIRST(right[0]) - {ε}
            if right_symbols:
                first_symbol = right_symbols[0]
                old_size = len(first_table[left])
                
                if first_symbol in first_table:
                    first_table[left].update(first_table[first_symbol] - {'ε'})
                
                # Si el primer símbolo puede ser ε, agregar FIRST del siguiente
                if 'ε' in first_table.get(first_symbol, set()):
                    for i in range(1, len(right_symbols)):
                        next_symbol = right_symbols[i]
                        if next_symbol in first_table:
                            first_table[left].update(first_table[next_symbol] - {'ε'})
                            if 'ε' not in first_table.get(next_symbol, set()):
                                break
                    else:
                        # Si todos pueden ser ε, agregar ε
                        first_table[left].add('ε')
                
                if len(first_table[left]) > old_size:
                    changed = True
    
    # Convertir sets a listas para JSON
    return {symbol: list(first_set) for symbol, first_set in first_table.items()}


def generar_json_first_table(first_table, grammar_info):
    """
    Genera un JSON estructurado para mostrar la tabla FIRST en una tabla HTML.
    
    Args:
        first_table: Diccionario con FIRST de cada símbolo
        grammar_info: Información de la gramática
    
    Returns:
        dict: JSON estructurado para la tabla
    """
    return {
        "success": True,
        "operation": "first_table",
        "grammar": {
            "productions": grammar_info["productions"],
            "start_symbol": grammar_info["start_symbol"]
        },
        "first_table": {
            symbol: first_table[symbol] 
            for symbol in first_table.keys()
            if symbol.isupper() or (symbol.startswith(symbol[0].upper()) and "'" in symbol)
        },
        "table_data": [
            {
                "symbol": symbol,
                "first_set": first_table[symbol],
                "first_string": ", ".join(sorted(first_table[symbol]))
            }
            for symbol in sorted(first_table.keys())
            if symbol.isupper() or (symbol.startswith(symbol[0].upper()) and "'" in symbol)
        ],
        "summary": {
            "total_nonterminals": len([s for s in first_table.keys() if s.isupper() or (s.startswith(s[0].upper()) and "'" in s)]),
            "nonterminals_with_first": len([s for s in first_table.keys() if (s.isupper() or (s.startswith(s[0].upper()) and "'" in s)) and first_table[s]])
        }
    }




