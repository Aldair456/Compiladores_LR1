import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple
from collections import defaultdict
from src.utils.funciones_auxiales import (
    extraer_symbols_from_grammar,
    calcular_first_table
)

class LR1Item:
    """Representa un elemento LR(1) con lookahead"""
    def __init__(self, production: str, dot_position: int, lookahead: str):
        self.production = production
        self.dot_position = dot_position
        self.lookahead = lookahead
    
    def __str__(self):
        left, right = self.production.split(' -> ')
        right_parts = right.split()
        right_parts.insert(self.dot_position, '•')
        return f"{left} -> {' '.join(right_parts)}, {self.lookahead}"
    
    def __eq__(self, other):
        return (self.production == other.production and 
                self.dot_position == other.dot_position and 
                self.lookahead == other.lookahead)
    
    def __hash__(self):
        return hash((self.production, self.dot_position, self.lookahead))
    
    def get_symbol_after_dot(self):
        """Obtiene el símbolo después del punto"""
        left, right = self.production.split(' -> ')
        right_parts = right.split()
        if self.dot_position < len(right_parts):
            return right_parts[self.dot_position]
        return None
    
    def is_reduce_item(self):
        """Verifica si es un elemento de reducción"""
        left, right = self.production.split(' -> ')
        right_parts = right.split()
        return self.dot_position >= len(right_parts)


def calcular_follow_table(productions, terminals, nonterminals, first_table):
    """
    Calcula la tabla FOLLOW para cada no terminal.
    
    Args:
        productions: Lista de producciones
        terminals: Lista de terminales
        nonterminals: Lista de no terminales
        first_table: Tabla FIRST calculada
    
    Returns:
        dict: Diccionario con FOLLOW de cada no terminal
    """
    follow_table = {nt: set() for nt in nonterminals}
    
    # FOLLOW del símbolo inicial contiene $
    start_symbol = productions[0].split(' -> ')[0].strip()
    follow_table[start_symbol].add('$')
    
    changed = True
    while changed:
        changed = False
        
        for production in productions:
            left, right = production.split(' -> ')
            left = left.strip()
            right_symbols = [s.strip() for s in right.split()]
            
            for i, symbol in enumerate(right_symbols):
                if symbol in nonterminals:
                    # FOLLOW(symbol) += FIRST(resto) - {ε}
                    rest_symbols = right_symbols[i+1:]
                    if rest_symbols:
                        first_of_rest = set()
                        can_derive_epsilon = True
                        
                        for rest_symbol in rest_symbols:
                            if rest_symbol in first_table:
                                first_set = set(first_table[rest_symbol])
                                first_of_rest.update(first_set - {'ε'})
                                if 'ε' not in first_set:
                                    can_derive_epsilon = False
                                    break
                        
                        old_size = len(follow_table[symbol])
                        follow_table[symbol].update(first_of_rest)
                        
                        if can_derive_epsilon:
                            follow_table[symbol].update(follow_table[left])
                        
                        if len(follow_table[symbol]) > old_size:
                            changed = True
                    else:
                        # Si está al final, FOLLOW(symbol) += FOLLOW(left)
                        old_size = len(follow_table[symbol])
                        follow_table[symbol].update(follow_table[left])
                        if len(follow_table[symbol]) > old_size:
                            changed = True
    
    return {symbol: list(follow_set) for symbol, follow_set in follow_table.items()}


def construir_conjuntos_lr1(productions, terminals, nonterminals, first_table):
    """
    Construye los conjuntos de elementos LR(1).
    
    Args:
        productions: Lista de producciones
        terminals: Lista de terminales
        nonterminals: Lista de no terminales
        first_table: Tabla FIRST calculada
    
    Returns:
        tuple: (conjuntos_lr1, transiciones)
    """
    # Encontrar el símbolo inicial real (no S')
    start_symbol = None
    for production in productions:
        left = production.split(' -> ')[0].strip()
        if left != "S'":
            start_symbol = left
            break
    
    if not start_symbol:
        start_symbol = productions[0].split(' -> ')[0].strip()
    
    # Filtrar producciones para evitar S' -> S' (que no existe)
    filtered_productions = []
    for production in productions:
        left, right = production.split(' -> ')
        if not (left.strip() == "S'" and right.strip() == "S'"):
            filtered_productions.append(production)
    
    # Agregar producción inicial aumentada solo si no existe
    augmented_productions = filtered_productions.copy()
    if not any(p.startswith("S' ->") for p in filtered_productions):
        augmented_productions = [f"S' -> {start_symbol}"] + filtered_productions
    
    # Estado inicial
    initial_item = LR1Item(f"S' -> {start_symbol}", 0, '$')
    initial_set = {initial_item}
    
    # Calcular cierre del estado inicial
    initial_closure = calcular_cierre_lr1(initial_set, augmented_productions, first_table)
    
    # Construir todos los conjuntos
    conjuntos = [initial_closure]
    transiciones = {}
    estados_por_conjunto = {frozenset(initial_closure): 0}
    
    i = 0
    while i < len(conjuntos):
        current_set = conjuntos[i]
        
        # Calcular transiciones desde este estado
        symbols_after_dot = set()
        for item in current_set:
            symbol = item.get_symbol_after_dot()
            if symbol:
                symbols_after_dot.add(symbol)
        
        for symbol in symbols_after_dot:
            # Calcular goto(I, symbol)
            goto_set = set()
            for item in current_set:
                if item.get_symbol_after_dot() == symbol:
                    new_item = LR1Item(item.production, item.dot_position + 1, item.lookahead)
                    goto_set.add(new_item)
            
            if goto_set:
                goto_closure = calcular_cierre_lr1(goto_set, augmented_productions, first_table)
                
                # Verificar si ya existe este conjunto
                goto_frozen = frozenset(goto_closure)
                if goto_frozen in estados_por_conjunto:
                    estado_destino = estados_por_conjunto[goto_frozen]
                else:
                    estado_destino = len(conjuntos)
                    conjuntos.append(goto_closure)
                    estados_por_conjunto[goto_frozen] = estado_destino
                
                transiciones[(i, symbol)] = estado_destino
        
        i += 1
    
    return conjuntos, transiciones


def calcular_cierre_lr1(items, productions, first_table):
    """
    Calcula el cierre LR(1) de un conjunto de elementos.
    
    Args:
        items: Conjunto de elementos LR(1)
        productions: Lista de producciones
        first_table: Tabla FIRST calculada
    
    Returns:
        set: Cierre LR(1) del conjunto
    """
    closure = set(items)
    changed = True
    
    while changed:
        changed = False
        
        for item in list(closure):
            symbol_after_dot = item.get_symbol_after_dot()
            if symbol_after_dot and symbol_after_dot not in ['$', 'ε']:
                # Buscar producciones que empiecen con este símbolo
                for production in productions:
                    left, right = production.split(' -> ')
                    left = left.strip()
                    
                    if left == symbol_after_dot:
                        # Calcular lookahead
                        right_symbols = right.split()
                        beta_alpha = []
                        
                        # Obtener símbolos después del punto en el item original
                        item_left, item_right = item.production.split(' -> ')
                        item_right_symbols = item_right.split()
                        
                        # Símbolos después del punto (beta)
                        if item.dot_position + 1 < len(item_right_symbols):
                            beta = item_right_symbols[item.dot_position + 1:]
                            beta_alpha.extend(beta)
                        
                        # Agregar lookahead del item original (alpha)
                        beta_alpha.append(item.lookahead)
                        
                        # Calcular FIRST(beta alpha)
                        lookaheads = calcular_first_beta_alpha(beta_alpha, first_table)
                        
                        for lookahead in lookaheads:
                            new_item = LR1Item(production, 0, lookahead)
                            if new_item not in closure:
                                closure.add(new_item)
                                changed = True
    
    return closure


def calcular_first_beta_alpha(beta_alpha, first_table):
    """
    Calcula FIRST(beta alpha) donde alpha es un terminal.
    
    Args:
        beta_alpha: Lista de símbolos [beta..., alpha]
        first_table: Tabla FIRST calculada
    
    Returns:
        set: Conjunto FIRST(beta alpha)
    """
    if not beta_alpha:
        return set()
    
    result = set()
    for i, symbol in enumerate(beta_alpha):
        if symbol in first_table:
            # Convertir lista a set para operaciones de conjunto
            first_set = set(first_table[symbol])
            result.update(first_set - {'ε'})
            if 'ε' not in first_set:
                break
        else:
            # Es un terminal
            result.add(symbol)
            break
    else:
        # Si todos pueden ser ε, agregar ε
        result.add('ε')
    
    return result


def generar_tabla_lr1(conjuntos, transiciones, productions, terminals, nonterminals):
    """
    Genera la tabla ACTION/GOTO para LR(1).
    
    Args:
        conjuntos: Lista de conjuntos de elementos LR(1)
        transiciones: Diccionario de transiciones
        productions: Lista de producciones
        terminals: Lista de terminales
        nonterminals: Lista de no terminales
    
    Returns:
        dict: Tabla ACTION/GOTO
    """
    action_table = {}
    goto_table = {}
    
    # Determinar símbolo inicial real y agregar producción aumentada correctamente
    start_symbol = None
    for production in productions:
        left = production.split(' -> ')[0].strip()
        if left != "S'":
            start_symbol = left
            break
    if not start_symbol:
        start_symbol = productions[0].split(' -> ')[0].strip()

    augmented_productions = productions[:]
    if not any(p.startswith("S' -> ") for p in productions):
        augmented_productions = [f"S' -> {start_symbol}"] + productions
    
    for i, conjunto in enumerate(conjuntos):
        action_table[i] = {}
        goto_table[i] = {}
        
        for item in conjunto:
            if item.is_reduce_item():
                # Acción de reducción
                try:
                    production_index = augmented_productions.index(item.production)
                except ValueError:
                    # Producción no encontrada: reportar claramente en la tabla de errores
                    raise ValueError(f"Producción no encontrada en la gramática: '{item.production}'. Asegúrate de que closure_data y productions coincidan.")
                if production_index == 0:
                    # Aceptar
                    action_table[i][item.lookahead] = 'acc'
                else:
                    # Reducir
                    action_table[i][item.lookahead] = f'r{production_index}'
            else:
                # Acción de shift
                symbol_after_dot = item.get_symbol_after_dot()
                if symbol_after_dot in terminals:
                    if (i, symbol_after_dot) in transiciones:
                        action_table[i][symbol_after_dot] = f's{transiciones[(i, symbol_after_dot)]}'
        
        # Tabla GOTO para no terminales
        for nonterminal in nonterminals:
            if (i, nonterminal) in transiciones:
                goto_table[i][nonterminal] = transiciones[(i, nonterminal)]
    
    return {
        'action': action_table,
        'goto': goto_table,
        'productions': augmented_productions
    }


def generar_json_tabla_lr1(tabla_lr1, grammar_info, terminals, nonterminals):
    """
    Genera un JSON estructurado para mostrar la tabla LR(1) en una tabla HTML.
    
    Args:
        tabla_lr1: Diccionario con tabla ACTION/GOTO
        grammar_info: Información de la gramática
        terminals: Lista de terminales
        nonterminals: Lista de no terminales
    
    Returns:
        dict: JSON estructurado para la tabla
    """
    action_table = tabla_lr1['action']
    goto_table = tabla_lr1['goto']
    productions = tabla_lr1['productions']
    
    # Crear estructura de tabla
    table_data = []
    for state in sorted(action_table.keys()):
        row = {
            'state': state,
            'action': {},
            'goto': {}
        }
        
        # Acciones para terminales
        for terminal in terminals + ['$']:
            if terminal in action_table[state]:
                row['action'][terminal] = action_table[state][terminal]
            else:
                row['action'][terminal] = ''
        
        # GOTO para no terminales
        for nonterminal in nonterminals:
            if nonterminal in goto_table[state]:
                row['goto'][nonterminal] = goto_table[state][nonterminal]
            else:
                row['goto'][nonterminal] = ''
        
        table_data.append(row)
    
    return {
        "success": True,
        "operation": "lr1_table",
        "grammar": {
            "productions": grammar_info["productions"],
            "start_symbol": grammar_info["start_symbol"]
        },
        "augmented_productions": productions,
        "table_data": table_data,
        "terminals": terminals + ['$'],
        "nonterminals": nonterminals,
        "summary": {
            "total_states": len(action_table),
            "total_terminals": len(terminals) + 1,  # +1 for $
            "total_nonterminals": len(nonterminals)
        }
    }
