import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict

# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class LR1Item:
    """
    Clase para representar un elemento LR(1).
    """
    
    def __init__(self, production: str, dot_position: int, lookahead: str):
        """
        Inicializa un elemento LR(1).
        
        Args:
            production: Producción en formato "A -> α β"
            dot_position: Posición del punto (0 = al inicio)
            lookahead: Terminal de lookahead
        """
        self.production = production
        self.dot_position = dot_position
        self.lookahead = lookahead
    
    def get_symbol_after_dot(self) -> str:
        """
        Obtiene el símbolo que está después del punto.
        
        Returns:
            str: Símbolo después del punto, o None si está al final
        """
        if ' -> ' not in self.production:
            return None
        
        left, right = self.production.split(' -> ')
        right_symbols = right.split()
        
        if self.dot_position >= len(right_symbols):
            return None
        
        return right_symbols[self.dot_position]
    
    def is_reduce_item(self) -> bool:
        """
        Verifica si es un elemento de reducción (punto al final).
        
        Returns:
            bool: True si es elemento de reducción
        """
        if ' -> ' not in self.production:
            return False
        
        left, right = self.production.split(' -> ')
        right_symbols = right.split()
        
        return self.dot_position >= len(right_symbols)
    
    def __str__(self) -> str:
        """
        Representación string del elemento LR(1).
        
        Returns:
            str: Elemento en formato "[A -> α • β, a]"
        """
        if ' -> ' not in self.production:
            return f"[{self.production}, {self.lookahead}]"
        
        left, right = self.production.split(' -> ')
        right_symbols = right.split()
        
        # Construir la parte derecha con el punto
        if self.dot_position >= len(right_symbols):
            # Punto al final
            right_with_dot = ' '.join(right_symbols) + ' •'
        else:
            # Insertar punto en la posición correcta
            right_with_dot = ' '.join(right_symbols[:self.dot_position]) + ' • ' + ' '.join(right_symbols[self.dot_position:])
        
        return f"[{left} -> {right_with_dot}, {self.lookahead}]"
    
    def __eq__(self, other):
        """Comparación de igualdad."""
        if not isinstance(other, LR1Item):
            return False
        return (self.production == other.production and 
                self.dot_position == other.dot_position and 
                self.lookahead == other.lookahead)
    
    def __hash__(self):
        """Hash para usar en sets."""
        return hash((self.production, self.dot_position, self.lookahead))


def extraer_symbols_from_grammar(productions: List[str]) -> Tuple[List[str], List[str]]:
    """
    Extrae terminales y no terminales de una lista de producciones.
    
    Args:
        productions: Lista de producciones en formato "A -> α"
    
    Returns:
        tuple: (terminales, no_terminales)
    """
    terminals = set()
    nonterminals = set()
    
    for production in productions:
        if ' -> ' not in production:
            continue
        
        left, right = production.split(' -> ')
        left = left.strip()
        right = right.strip()
        
        # LHS es no terminal
        nonterminals.add(left)
        
        # Procesar RHS
        symbols = right.split()
        for symbol in symbols:
            if symbol == 'ε':
                continue
            elif symbol.isupper() or (symbol.startswith(symbol[0].upper()) and "'" in symbol):
                # Es no terminal
                nonterminals.add(symbol)
            else:
                # Es terminal
                terminals.add(symbol)
    
    return sorted(list(terminals)), sorted(list(nonterminals))


def calcular_first_table(productions: List[str], terminals: List[str], nonterminals: List[str]) -> Dict[str, List[str]]:
    """
    Calcula la tabla FIRST para todos los símbolos de la gramática.
    
    Args:
        productions: Lista de producciones
        terminals: Lista de terminales
        nonterminals: Lista de no terminales
    
    Returns:
        dict: Tabla FIRST con símbolos como claves y listas de terminales como valores
    """
    first_table = {}
    
    # Inicializar FIRST para todos los símbolos
    for symbol in terminals + nonterminals:
        first_table[symbol] = set()
    
    # Paso 1: FIRST(a) = {a} para terminales
    for terminal in terminals:
        first_table[terminal].add(terminal)
    
    # Paso 2: Si A -> ε, entonces ε ∈ FIRST(A)
    for production in productions:
        if ' -> ' not in production:
            continue
        
        left, right = production.split(' -> ')
        left = left.strip()
        right = right.strip()
        
        if right == 'ε':
            first_table[left].add('ε')
    
    # Paso 3: Iterar hasta que no haya cambios
    changed = True
    while changed:
        changed = False
        
        for production in productions:
            if ' -> ' not in production:
                continue
            
            left, right = production.split(' -> ')
            left = left.strip()
            right = right.strip()
            
            if right == 'ε':
                continue
            
            symbols = right.split()
            if not symbols:
                continue
            
            # Calcular FIRST de la cadena del lado derecho
            first_beta = set()
            all_epsilon = True
            
            for symbol in symbols:
                if symbol in first_table:
                    first_beta.update(first_table[symbol] - {'ε'})
                    if 'ε' not in first_table[symbol]:
                        all_epsilon = False
                        break
                else:
                    # Es terminal
                    first_beta.add(symbol)
                    all_epsilon = False
                    break
            
            if all_epsilon:
                first_beta.add('ε')
            
            # Agregar a FIRST(A)
            old_size = len(first_table[left])
            first_table[left].update(first_beta)
            if len(first_table[left]) > old_size:
                changed = True
    
    # Convertir sets a listas y ordenar
    for symbol in first_table:
        first_table[symbol] = sorted(list(first_table[symbol]))
    
    return first_table


def calcular_follow_table(productions: List[str], terminals: List[str], nonterminals: List[str], first_table: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Calcula la tabla FOLLOW para todos los no terminales de la gramática.
    
    Args:
        productions: Lista de producciones
        terminals: Lista de terminales
        nonterminals: Lista de no terminales
        first_table: Tabla FIRST calculada
    
    Returns:
        dict: Tabla FOLLOW con no terminales como claves y listas de terminales como valores
    """
    follow_table = {}
    
    # Inicializar FOLLOW para todos los no terminales
    for nonterminal in nonterminals:
        follow_table[nonterminal] = set()
    
    # Encontrar símbolo inicial y símbolo aumentado
    start_symbol = None
    augmented_start = None
    
    for production in productions:
        if ' -> ' not in production:
            continue
        left = production.split(' -> ')[0].strip()
        if left == "S'":
            augmented_start = left
        elif left != "S'":
            start_symbol = left
            break
    
    if not start_symbol:
        start_symbol = productions[0].split(' -> ')[0].strip()
    
    # Paso 1: $ ∈ FOLLOW(S') si existe, o FOLLOW(S) donde S es el símbolo inicial
    if augmented_start:
        follow_table[augmented_start].add('$')
    else:
        follow_table[start_symbol].add('$')
    
    # Paso 2: Iterar hasta que no haya cambios
    changed = True
    while changed:
        changed = False
        
        for production in productions:
            if ' -> ' not in production:
                continue
            
            left, right = production.split(' -> ')
            left = left.strip()
            right = right.strip()
            
            if right == 'ε':
                continue
            
            symbols = right.split()
            if not symbols:
                continue
            
            # Para cada A -> αBβ
            for i, symbol in enumerate(symbols):
                if symbol in nonterminals:  # B es no terminal
                    # Calcular FIRST(β)
                    beta = symbols[i+1:]
                    first_beta = set()
                    
                    if not beta:
                        # β = ε, agregar FOLLOW(A) a FOLLOW(B)
                        old_size = len(follow_table[symbol])
                        follow_table[symbol].update(follow_table[left])
                        if len(follow_table[symbol]) > old_size:
                            changed = True
                    else:
                        # Calcular FIRST(β)
                        all_epsilon = True
                        for beta_symbol in beta:
                            if beta_symbol in first_table:
                                first_beta.update(set(first_table[beta_symbol]) - {'ε'})
                                if 'ε' not in first_table[beta_symbol]:
                                    all_epsilon = False
                                    break
                            else:
                                # Es terminal
                                first_beta.add(beta_symbol)
                                all_epsilon = False
                                break
                        
                        # Agregar FIRST(β) - {ε} a FOLLOW(B)
                        old_size = len(follow_table[symbol])
                        follow_table[symbol].update(first_beta)
                        if len(follow_table[symbol]) > old_size:
                            changed = True
                        
                        # Si ε ∈ FIRST(β), agregar FOLLOW(A) a FOLLOW(B)
                        if all_epsilon:
                            old_size = len(follow_table[symbol])
                            follow_table[symbol].update(follow_table[left])
                            if len(follow_table[symbol]) > old_size:
                                changed = True
    
    # Convertir sets a listas y ordenar
    for symbol in follow_table:
        follow_table[symbol] = sorted(list(follow_table[symbol]))
    
    return follow_table


class LR1:
    """
    Clase para manejar análisis LR(1) completo de gramáticas.
    Proporciona métodos para calcular FIRST, FOLLOW, y construir conjuntos LR(1).
    """
    
    def __init__(self, productions: List[str], start_symbol: str = None):
        """
        Inicializa la clase LR1 con una gramática.
        
        Args:
            productions: Lista de producciones de la gramática
            start_symbol: Símbolo inicial (opcional, se detecta automáticamente)
        """
        self.original_productions = productions
        self.expanded_productions = self._expandir_producciones_con_pipe(productions)
        self.terminals, self.nonterminals = extraer_symbols_from_grammar(self.expanded_productions)
        self.start_symbol = start_symbol or self._detectar_simbolo_inicial()
        
        # Tablas calculadas
        self.first_table = None
        self.follow_table = None
        self.lr1_conjuntos = None
        self.transiciones = None
        
        # Estado de cálculo
        self._first_calculado = False
        self._follow_calculado = False
        self._lr1_calculado = False
    
    def _expandir_producciones_con_pipe(self, productions: List[str]) -> List[str]:
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
    
    def _detectar_simbolo_inicial(self) -> str:
        """
        Detecta el símbolo inicial de la gramática.
        
        Returns:
            str: Símbolo inicial detectado
        """
        # Buscar producción que no sea S' -> algo
        for production in self.expanded_productions:
            left = production.split(' -> ')[0].strip()
            if left != "S'":
                return left
        
        # Si no encuentra, usar el primero
        return self.expanded_productions[0].split(' -> ')[0].strip()
    
    def _extract_symbols_from_grammar(self, productions: List[str]) -> Tuple[List[str], List[str]]:
        """
        Extrae terminales y no terminales de una lista de producciones.
        Método interno para uso en la clase.
        
        Args:
            productions: Lista de producciones
        
        Returns:
            tuple: (terminales, no_terminales)
        """
        return extraer_symbols_from_grammar(productions)
    
    def calcular_first(self) -> Dict[str, List[str]]:
        """
        Calcula la tabla FIRST para todos los símbolos de la gramática.
        
        Returns:
            dict: Tabla FIRST con símbolos como claves y listas de terminales como valores
        """
        if not self._first_calculado:
            self.first_table = calcular_first_table(
                self.expanded_productions,
                self.terminals,
                self.nonterminals
            )
            self._first_calculado = True
        
        return self.first_table
    
    def calcular_follow(self) -> Dict[str, List[str]]:
        """
        Calcula la tabla FOLLOW para todos los no terminales de la gramática.
        
        Returns:
            dict: Tabla FOLLOW con no terminales como claves y listas de terminales como valores
        """
        if not self._follow_calculado:
            if not self._first_calculado:
                self.calcular_first()
            
            self.follow_table = calcular_follow_table(
                self.expanded_productions,
                self.terminals,
                self.nonterminals,
                self.first_table
            )
            self._follow_calculado = True
        
        return self.follow_table
    
    def obtener_terminals(self) -> List[str]:
        """
        Obtiene la lista de terminales de la gramática.
        
        Returns:
            list: Lista de terminales
        """
        return self.terminals
    
    def obtener_nonterminals(self) -> List[str]:
        """
        Obtiene la lista de no terminales de la gramática.
        
        Returns:
            list: Lista de no terminales
        """
        return self.nonterminals
    
    def obtener_producciones_expandidas(self) -> List[str]:
        """
        Obtiene las producciones expandidas (sin pipes).
        
        Returns:
            list: Lista de producciones expandidas
        """
        return self.expanded_productions
    
    def obtener_simbolo_inicial(self) -> str:
        """
        Obtiene el símbolo inicial de la gramática.
        
        Returns:
            str: Símbolo inicial
        """
        return self.start_symbol
    
    def obtener_first_no_terminales(self) -> Dict[str, List[str]]:
        """
        Obtiene solo los FIRST de los no terminales.
        
        Returns:
            dict: FIRST de no terminales únicamente
        """
        if not self._first_calculado:
            self.calcular_first()
        
        return {
            symbol: self.first_table[symbol] 
            for symbol in self.first_table.keys()
            if symbol.isupper() or (symbol.startswith(symbol[0].upper()) and "'" in symbol)
        }
    
    def obtener_follow_no_terminales(self) -> Dict[str, List[str]]:
        """
        Obtiene la tabla FOLLOW completa (solo no terminales).
        
        Returns:
            dict: Tabla FOLLOW
        """
        if not self._follow_calculado:
            self.calcular_follow()
        
        return self.follow_table
    
    def generar_resumen(self) -> Dict[str, Any]:
        """
        Genera un resumen completo de la gramática y sus análisis.
        
        Returns:
            dict: Resumen con toda la información
        """
        # Calcular FIRST y FOLLOW si no están calculados
        if not self._first_calculado:
            self.calcular_first()
        if not self._follow_calculado:
            self.calcular_follow()
        
        return {
            "grammar": {
                "productions": self.original_productions,
                "expanded_productions": self.expanded_productions,
                "start_symbol": self.start_symbol
            },
            "symbols": {
                "terminals": self.terminals,
                "nonterminals": self.nonterminals
            },
            "first_sets": self.obtener_first_no_terminales(),
            "follow_sets": self.follow_table,
            "summary": {
                "total_productions": len(self.expanded_productions),
                "total_terminals": len(self.terminals),
                "total_nonterminals": len(self.nonterminals)
            }
        }
    
    def imprimir_resumen(self):
        """
        Imprime un resumen formateado de la gramática y sus análisis.
        """
        resumen = self.generar_resumen()
        
        print("="*60)
        print("RESUMEN DE GRAMÁTICA LR(1)")
        print("="*60)
        
        print(f"\nSímbolo Inicial: {resumen['grammar']['start_symbol']}")
        print(f"Total Producciones: {resumen['summary']['total_productions']}")
        print(f"Total Terminales: {resumen['summary']['total_terminals']}")
        print(f"Total No Terminales: {resumen['summary']['total_nonterminals']}")
        
        print(f"\nTerminales: {', '.join(sorted(resumen['symbols']['terminals']))}")
        print(f"No Terminales: {', '.join(sorted(resumen['symbols']['nonterminals']))}")
        
        print(f"\nFIRST Sets:")
        for symbol, first_set in resumen['first_sets'].items():
            print(f"  FIRST({symbol}) = {{{', '.join(sorted(first_set))}}}")
        
        print(f"\nFOLLOW Sets:")
        for symbol, follow_set in resumen['follow_sets'].items():
            print(f"  FOLLOW({symbol}) = {{{', '.join(sorted(follow_set))}}}")
        
        print("="*60)
    
    def first_seq(self, seq: List[str]) -> Set[str]:
        """
        Calcula FIRST(seq) para una secuencia de símbolos.
        
        Args:
            seq: Lista de símbolos [X1, X2, ..., Xn]
        
        Returns:
            set: FIRST(seq)
        """
        if not seq:
            return {'ε'}
        
        result = set()
        for i, symbol in enumerate(seq):
            if symbol in self.first_table:
                first_set = set(self.first_table[symbol])
                result.update(first_set - {'ε'})
                if 'ε' not in first_set:
                    break
            else:
                # Es terminal
                result.add(symbol)
                break
        else:
            # Si todos pueden ser ε, agregar ε
            result.add('ε')
        
        return result
    
    def first_of_beta_a(self, beta: List[str], a: str) -> Set[str]:
        """
        Calcula FIRST(β a) para lookaheads en construcción LR(1).
        
        Args:
            beta: Lista de símbolos β
            a: Terminal de lookahead
        
        Returns:
            set: FIRST(β a)
        """
        # Crear secuencia β + a
        seq = beta + [a]
        return self.first_seq(seq)
    
    def closure(self, items: Set[LR1Item]) -> Set[LR1Item]:
        """
        Calcula el closure LR(1) de un conjunto de elementos.
        
        Args:
            items: Conjunto inicial de elementos LR(1)
        
        Returns:
            set: Closure LR(1) del conjunto
        """
        closure_set = set(items)
        changed = True
        
        while changed:
            changed = False
            
            for item in list(closure_set):
                symbol_after_dot = item.get_symbol_after_dot()
                
                if symbol_after_dot and symbol_after_dot in self.nonterminals:
                    # Buscar producciones que empiecen con este símbolo
                    for production in self.expanded_productions:
                        left, right = production.split(' -> ')
                        left = left.strip()
                        
                        if left == symbol_after_dot:
                            # Calcular FIRST(βa) donde β son los símbolos después del punto
                            item_left, item_right = item.production.split(' -> ')
                            item_right_symbols = item_right.split()
                            
                            # Símbolos después del punto (β)
                            beta = []
                            if item.dot_position + 1 < len(item_right_symbols):
                                beta = item_right_symbols[item.dot_position + 1:]
                            
                            # Calcular FIRST(βa)
                            lookaheads = self.first_of_beta_a(beta, item.lookahead)
                            
                            for lookahead in lookaheads:
                                if lookahead != 'ε':  # No agregar ε como lookahead
                                    new_item = LR1Item(production, 0, lookahead)
                                    if new_item not in closure_set:
                                        closure_set.add(new_item)
                                        changed = True
        
        return closure_set
    
    def goto(self, items: Set[LR1Item], X: str) -> Set[LR1Item]:
        """
        Calcula goto(I, X) para un conjunto de elementos y un símbolo.
        
        Args:
            items: Conjunto de elementos LR(1)
            X: Símbolo para mover el punto
        
        Returns:
            set: goto(I, X)
        """
        goto_items = set()
        
        # Mover el punto sobre X en todos los ítems donde toca X
        for item in items:
            if item.get_symbol_after_dot() == X:
                new_item = LR1Item(item.production, item.dot_position + 1, item.lookahead)
                goto_items.add(new_item)
        
        # Calcular closure del conjunto resultante
        if goto_items:
            return self.closure(goto_items)
        else:
            return set()
    
    def aumentar_gramatica(self, start_symbol: str, end_marker: str = "$") -> List[str]:
        """
        Aumenta la gramática agregando S' -> S si es necesario.
        
        Args:
            start_symbol: Símbolo inicial de la gramática
            end_marker: Marcador de fin (por defecto "$")
        
        Returns:
            list: Lista de producciones aumentadas
        """
        augmented_productions = self.expanded_productions.copy()
        
        # Si el símbolo inicial no es S', agregar producción aumentada
        if not start_symbol.startswith("S'"):
            augmented_productions = [f"S' -> {start_symbol}"] + augmented_productions
        
        return augmented_productions
    
    def construir_coleccion_lr1(self) -> Tuple[List[Set[LR1Item]], Dict[Tuple[int, str], int]]:
        """
        Construye la colección canónica de conjuntos LR(1).
        
        Returns:
            tuple: (lista_de_estados, transiciones)
                - lista_de_estados: Lista de conjuntos de elementos LR(1)
                - transiciones: Diccionario {(estado, símbolo): estado_destino}
        """
        # Asegurar que tenemos FIRST y FOLLOW calculados
        if not self._first_calculado:
            self.calcular_first()
        if not self._follow_calculado:
            self.calcular_follow()
        
        # Crear elemento inicial
        initial_item = LR1Item(f"S' -> {self.start_symbol}", 0, '$')
        initial_set = self.closure({initial_item})
        
        # Construir todos los estados
        estados = [initial_set]
        transiciones = {}
        estados_por_conjunto = {frozenset(initial_set): 0}
        
        i = 0
        while i < len(estados):
            current_set = estados[i]
            
            # Calcular transiciones desde este estado
            symbols_after_dot = set()
            for item in current_set:
                symbol = item.get_symbol_after_dot()
                if symbol:
                    symbols_after_dot.add(symbol)
            
            for symbol in symbols_after_dot:
                # Calcular goto(I, symbol)
                goto_set = self.goto(current_set, symbol)
                
                if goto_set:
                    # Verificar si ya existe este conjunto
                    goto_frozen = frozenset(goto_set)
                    if goto_frozen in estados_por_conjunto:
                        estado_destino = estados_por_conjunto[goto_frozen]
                    else:
                        estado_destino = len(estados)
                        estados.append(goto_set)
                        estados_por_conjunto[goto_frozen] = estado_destino
                    
                    transiciones[(i, symbol)] = estado_destino
            
            i += 1
        
        return estados, transiciones


def convertir_estados_a_closure_table(estados: List[Set[LR1Item]], transiciones: Dict[Tuple[int, str], int]) -> Dict[str, Any]:
    """
    Convierte estados LR(1) a formato de closure table.
    
    Args:
        estados: Lista de conjuntos de elementos LR(1)
        transiciones: Diccionario de transiciones
    
    Returns:
        dict: Closure table en formato estándar
    """
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
    
    return {
        "states": states_data
    }


def reconstruir_estados_desde_closure_table(closure_table: Dict[str, Any], lr1: LR1) -> Tuple[List[Set[LR1Item]], Dict[Tuple[int, str], int]]:
    """
    Reconstruye estados LR(1) desde closure table.
    
    Args:
        closure_table: Closure table en formato estándar
        lr1: Instancia de LR1
    
    Returns:
        tuple: (estados, transiciones)
    """
    estados = []
    transiciones = {}
    
    for state_data in closure_table['states']:
        estado_id = state_data['id']
        items = set()
        
        # Reconstruir elementos LR(1) desde strings
        for item_str in state_data['items']:
            item = parsear_item_string(item_str)
            if item:
                items.add(item)
        
        estados.append(items)
        
        # Reconstruir transiciones
        for simbolo, estado_destino in state_data['transitions'].items():
            transiciones[(estado_id, simbolo)] = estado_destino
    
    return estados, transiciones


def parsear_item_string(item_str: str) -> Optional[LR1Item]:
    """
    Parsea un string de elemento LR(1) a objeto LR1Item.
    
    Args:
        item_str: String en formato "[A -> α • β, a]"
    
    Returns:
        LR1Item: Elemento parseado o None si hay error
    """
    try:
        # Remover corchetes externos
        if not item_str.startswith('[') or not item_str.endswith(']'):
            return None
        
        content = item_str[1:-1]
        
        # Dividir por la última coma para separar lookahead
        parts = content.rsplit(', ', 1)
        if len(parts) != 2:
            return None
        
        production_part, lookahead = parts
        
        # Buscar el punto - manejar espacios extra
        if ' • ' in production_part:
            # Caso normal: punto en el medio
            left, right_with_dot = production_part.split(' -> ')
            left = left.strip()
            right_symbols = right_with_dot.split()
            dot_position = 0
            
            for i, symbol in enumerate(right_symbols):
                if symbol == '•':
                    dot_position = i
                    break
            
            # Remover el punto de los símbolos
            right_symbols = [s for s in right_symbols if s != '•']
            production = f"{left} -> {' '.join(right_symbols)}"
            
        elif production_part.endswith(' •'):
            # Caso: punto al final
            production_part = production_part[:-2].strip()
            if ' -> ' in production_part:
                left, right = production_part.split(' -> ')
                left = left.strip()
                right_symbols = right.split() if right.strip() else []
                dot_position = len(right_symbols)
                production = f"{left} -> {right}"
            else:
                return None
        else:
            return None
        
        return LR1Item(production, dot_position, lookahead.strip())
        
    except Exception as e:
        logger.warning(f"Error parseando item: {item_str}, error: {e}")
        return None


def construir_tabla_lr1_completa(
    grammar: Dict[str, Any],
    options: Dict[str, Any] = None,
    closure_table: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Construye la tabla LR(1) completa desde cero o desde closure_table existente.
    
    Args:
        grammar: Gramática con productions y start_symbol
        options: Opciones de configuración
        closure_table: Closure table opcional (si se proporciona, se usa tal cual)
    
    Returns:
        dict: Tabla LR(1) completa en formato JSON
    """
    if options is None:
        options = {}
    
    # Configurar opciones
    augment = options.get('augment', True)
    epsilon_symbol = options.get('epsilon_symbol', 'ε')
    end_marker = options.get('end_marker', '$')
    accept_token = options.get('accept_token', 'acc')
    
    # Obtener información de la gramática
    productions = grammar['productions']
    start_symbol = grammar['start_symbol']
    
    # 1) Pre-procesamiento de la gramática
    # Determinar símbolo inicial original
    original_start_symbol = start_symbol
    if augment and start_symbol == "S'":
        # Si ya es S', encontrar el símbolo original
        for prod in productions:
            if prod.startswith("S' -> "):
                original_start_symbol = prod.split(" -> ")[1].strip()
                break
        else:
            # Si no hay S' -> X, usar el primer símbolo no-S'
            for prod in productions:
                left = prod.split(" -> ")[0].strip()
                if left != "S'":
                    original_start_symbol = left
                    break
    
    # Crear instancia LR1
    lr1 = LR1(productions, start_symbol)
    
    # Expandir alternativas con | a producciones simples
    expanded_productions = lr1.obtener_producciones_expandidas()
    
    # Aplicar aumentación si es necesario
    if augment:
        augmented_productions = lr1.aumentar_gramatica(original_start_symbol, end_marker)
    else:
        augmented_productions = expanded_productions
    
    # Actualizar instancia
    lr1.expanded_productions = augmented_productions
    lr1.terminals, lr1.nonterminals = lr1._extract_symbols_from_grammar(augmented_productions)
    
    # 2) Cálculo FIRST/FOLLOW
    lr1.calcular_first()
    lr1.calcular_follow()
    
    # Extraer símbolos (sin $ en terminales)
    terminals = [t for t in lr1.obtener_terminals() if t != end_marker]
    nonterminals = lr1.obtener_nonterminals()
    
    # 3) Conjunto canónico LR(1)
    if closure_table is None:
        # Construir estados LR(1) desde cero
        estados, transiciones = lr1.construir_coleccion_lr1()
        # Convertir a formato closure_table
        closure_table = convertir_estados_a_closure_table(estados, transiciones)
    else:
        # Usar closure_table proporcionado tal cual
        estados, transiciones = reconstruir_estados_desde_closure_table(closure_table, lr1)
    
    # Crear tabla de producciones numeradas (sin S' -> S si es aumentada)
    productions_table = []
    production_map = {}
    
    for production in augmented_productions:
        # Si es producción aumentada S' -> S, no la numeramos en la tabla
        if augment and production.startswith("S' -> ") and production.split(" -> ")[1].strip() == original_start_symbol:
            continue
        
        prod_num = len(productions_table) + 1
        productions_table.append({
            "number": prod_num,
            "production": production,
            "left_side": production.split(' -> ')[0].strip(),
            "right_side": production.split(' -> ')[1].strip()
        })
        production_map[production] = prod_num
    
    # 4) Construcción de ACTION / GOTO
    action_table = {}
    goto_table = {}
    reductions = {}
    conflicts = []
    
    # Procesar cada estado del closure_table
    for state_data in closure_table['states']:
        estado_id = state_data['id']
        items_strings = state_data['items']
        state_transitions = state_data.get('transitions', {})
        
        # Inicializar tablas para este estado
        action_table[str(estado_id)] = {}
        goto_table[str(estado_id)] = {}
        
        # Procesar transiciones para ACTION (shift) y GOTO
        for symbol, target_state in state_transitions.items():
            if symbol in terminals:
                # Acción de shift
                action_table[str(estado_id)][symbol] = f"s{target_state}"
            elif symbol in nonterminals:
                # Acción de goto
                goto_table[str(estado_id)][symbol] = target_state
        
        # Procesar items para reducciones y accept
        for item_str in items_strings:
            item = parsear_item_string(item_str)
            if not item:
                continue
            
            if item.is_reduce_item():
                production = item.production
                lookahead = item.lookahead
                
                # Verificar si es producción aumentada S' -> S
                if augment and production.startswith("S' -> ") and production.split(" -> ")[1].strip() == original_start_symbol:
                    # Es acción de aceptación
                    if lookahead == end_marker:
                        action_table[str(estado_id)][end_marker] = accept_token
                else:
                    # Es reducción normal
                    prod_num = production_map.get(production, 0)
                    
                    if prod_num == 0:
                        # Buscar en producciones expandidas
                        for i, exp_prod in enumerate(augmented_productions):
                            if exp_prod == production:
                                prod_num = i + 1
                                break
                    
                    if prod_num > 0:
                        # Agregar acción de reducción
                        if lookahead in action_table[str(estado_id)]:
                            # Verificar conflicto
                            existing_action = action_table[str(estado_id)][lookahead]
                            if existing_action != f"r{prod_num}":
                                conflicts.append({
                                    "state": estado_id,
                                    "symbol": lookahead,
                                    "conflict_type": "reduce_reduce" if existing_action.startswith('r') else "shift_reduce",
                                    "existing_action": existing_action,
                                    "new_action": f"r{prod_num}",
                                    "item": str(item)
                                })
                        else:
                            action_table[str(estado_id)][lookahead] = f"r{prod_num}"
                        
                        # Guardar información de reducción
                        if estado_id not in reductions:
                            reductions[estado_id] = {}
                        reductions[estado_id][lookahead] = {
                            "production": production,
                            "production_number": prod_num,
                            "item": str(item)
                        }
    
    # Determinar símbolo inicial final
    final_start_symbol = "S'" if augment else original_start_symbol
    
    # Construir respuesta JSON
    response = {
        "success": True,
        "operation": "lr1_table",
        "grammar": {
            "augmented": augment,
            "start_symbol": final_start_symbol,
            "original_start_symbol": original_start_symbol,
            "epsilon": epsilon_symbol,
            "end_marker": end_marker,
            "accept_token": accept_token,
            "original_productions": productions,
            "expanded_productions": [p['production'] for p in productions_table]
        },
        "lr1_table": {
            "action_table": action_table,
            "goto_table": goto_table,
            "reductions": reductions,
            "conflicts": conflicts
        },
        "closure_table": closure_table,
        "productions_table": productions_table,
        "symbols": {
            "terminals": terminals,
            "nonterminals": nonterminals
        },
        "summary": {
            "total_states": len(action_table),
            "total_terminals": len(terminals),
            "total_nonterminals": len(nonterminals),
            "total_productions": len(productions_table),
            "total_conflicts": len(conflicts),
            "conflict_types": list(set(conflict["conflict_type"] for conflict in conflicts))
        }
    }
    
    return response


def reconstruir_tabla_lr1_desde_closure_table(
    closure_table: Dict[str, Any],
    grammar: Dict[str, Any],
    options: Dict[str, Any] = None
) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, int]], Dict[int, Dict[str, Any]], List[Dict[str, Any]], List[str], List[str], List[Dict[str, Any]]]:
    """
    Reconstruye la tabla LR(1) ACTION/GOTO desde un closure_table existente.
    
    Args:
        closure_table: Closure table con estados y transiciones
        grammar: Gramática con productions y start_symbol
        options: Opciones de configuración
    
    Returns:
        tuple: (action_table, goto_table, reductions, conflicts, terminals, nonterminals, productions_table)
    """
    if options is None:
        options = {}
    
    # Configurar opciones
    augment = options.get('augment', True)
    epsilon_symbol = options.get('epsilon_symbol', 'ε')
    end_marker = options.get('end_marker', '$')
    
    # Obtener información de la gramática
    productions = grammar['productions']
    start_symbol = grammar['start_symbol']
    
    # Determinar símbolo inicial original
    original_start_symbol = start_symbol
    if augment and start_symbol == "S'":
        # Si ya es S', encontrar el símbolo original
        for prod in productions:
            if prod.startswith("S' -> "):
                original_start_symbol = prod.split(" -> ")[1].strip()
                break
        else:
            # Si no hay S' -> X, usar el primer símbolo no-S'
            for prod in productions:
                left = prod.split(" -> ")[0].strip()
                if left != "S'":
                    original_start_symbol = left
                    break
    
    # Crear instancia LR1 para cálculos auxiliares
    lr1 = LR1(productions, start_symbol)
    
    # Aplicar aumentación si es necesario
    if augment:
        augmented_productions = lr1.aumentar_gramatica(original_start_symbol, end_marker)
    else:
        augmented_productions = lr1.obtener_producciones_expandidas()
    
    # Actualizar instancia
    lr1.expanded_productions = augmented_productions
    lr1.terminals, lr1.nonterminals = lr1._extract_symbols_from_grammar(augmented_productions)
    
    # Calcular FIRST y FOLLOW
    lr1.calcular_first()
    lr1.calcular_follow()
    
    # Extraer terminales y no terminales (sin $ en terminales)
    terminals = [t for t in lr1.obtener_terminals() if t != end_marker]
    nonterminals = lr1.obtener_nonterminals()
    
    # Crear tabla de producciones numeradas (sin S' -> S si es aumentada)
    productions_table = []
    production_map = {}
    
    for i, production in enumerate(augmented_productions):
        # Si es producción aumentada S' -> S, no la numeramos en la tabla
        if augment and production.startswith("S' -> ") and production.split(" -> ")[1].strip() == original_start_symbol:
            continue
        
        prod_num = len(productions_table) + 1
        productions_table.append({
            "number": prod_num,
            "production": production,
            "left_side": production.split(' -> ')[0].strip(),
            "right_side": production.split(' -> ')[1].strip()
        })
        production_map[production] = prod_num
    
    # Inicializar tablas
    action_table = {}
    goto_table = {}
    reductions = {}
    conflicts = []
    
    # Procesar cada estado del closure_table
    for state_data in closure_table['states']:
        estado_id = state_data['id']
        items_strings = state_data['items']
        state_transitions = state_data.get('transitions', {})
        
        # Inicializar tablas para este estado
        action_table[str(estado_id)] = {}
        goto_table[str(estado_id)] = {}
        
        # 1. Procesar transiciones para ACTION (shift) y GOTO
        for symbol, target_state in state_transitions.items():
            if symbol in terminals:
                # Acción de shift
                action_table[str(estado_id)][symbol] = f"s{target_state}"
            elif symbol in nonterminals:
                # Acción de goto
                goto_table[str(estado_id)][symbol] = target_state
        
        # 2. Procesar items para reducciones y accept
        for item_str in items_strings:
            item = parsear_item_string(item_str)
            if not item:
                continue
            
            if item.is_reduce_item():
                production = item.production
                lookahead = item.lookahead
                
                # Verificar si es producción aumentada S' -> S
                if augment and production.startswith("S' -> ") and production.split(" -> ")[1].strip() == original_start_symbol:
                    # Es acción de aceptación
                    if lookahead == end_marker:
                        action_table[str(estado_id)][end_marker] = "acc"
                else:
                    # Es reducción normal
                    prod_num = production_map.get(production, 0)
                    
                    if prod_num > 0:
                        # Agregar acción de reducción
                        if lookahead in action_table[str(estado_id)]:
                            # Verificar conflicto
                            existing_action = action_table[str(estado_id)][lookahead]
                            if existing_action != f"r{prod_num}":
                                conflicts.append({
                                    "state": estado_id,
                                    "symbol": lookahead,
                                    "conflict_type": "reduce_reduce" if existing_action.startswith('r') else "shift_reduce",
                                    "existing_action": existing_action,
                                    "new_action": f"r{prod_num}",
                                    "item": str(item)
                                })
                        else:
                            action_table[str(estado_id)][lookahead] = f"r{prod_num}"
                        
                        # Guardar información de reducción
                        if estado_id not in reductions:
                            reductions[estado_id] = {}
                        reductions[estado_id][lookahead] = {
                            "production": production,
                            "production_number": prod_num,
                            "item": str(item)
                        }
    
    return action_table, goto_table, reductions, conflicts, terminals, nonterminals, productions_table


def construir_tabla_lr1(
    estados: List[Set[LR1Item]], 
    transiciones: Dict[Tuple[int, str], int],
    lr1: LR1,
    productions: List[str],
    start_symbol: str
) -> Tuple[Dict[str, Dict[str, str]], Dict[str, Dict[str, int]], Dict[int, Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Construye la tabla LR(1) ACTION/GOTO (función legacy).
    
    Args:
        estados: Lista de estados LR(1)
        transiciones: Diccionario de transiciones
        lr1: Instancia de LR1
        productions: Lista de producciones
        start_symbol: Símbolo inicial
    
    Returns:
        tuple: (action_table, goto_table, reductions, conflicts)
    """
    action_table = {}
    goto_table = {}
    reductions = {}
    conflicts = []
    
    # Obtener terminales y no terminales
    terminals = lr1.obtener_terminals()
    nonterminals = lr1.obtener_nonterminals()
    
    # Crear mapeo de producciones a números
    production_map = {}
    for i, production in enumerate(productions):
        production_map[production] = i + 1
    
    # Procesar cada estado
    for estado_id, estado in enumerate(estados):
        action_table[str(estado_id)] = {}
        goto_table[str(estado_id)] = {}
        
        # Procesar cada elemento en el estado
        for item in estado:
            if item.is_reduce_item():
                # Es un elemento de reducción
                production = item.production
                lookahead = item.lookahead
                
                # Determinar número de producción
                prod_num = production_map.get(production, 0)
                if prod_num == 0:
                    # Buscar en producciones expandidas
                    expanded_prods = lr1.obtener_producciones_expandidas()
                    for i, exp_prod in enumerate(expanded_prods):
                        if exp_prod == production:
                            prod_num = i + 1
                            break
                
                if prod_num > 0:
                    # Agregar acción de reducción
                    if lookahead in action_table[str(estado_id)]:
                        # Conflicto
                        existing_action = action_table[str(estado_id)][lookahead]
                        conflicts.append({
                            "state": estado_id,
                            "symbol": lookahead,
                            "conflict_type": "reduce_reduce" if existing_action.startswith('r') else "shift_reduce",
                            "existing_action": existing_action,
                            "new_action": f"r{prod_num}",
                            "item": str(item)
                        })
                    else:
                        action_table[str(estado_id)][lookahead] = f"r{prod_num}"
                    
                    # Guardar información de reducción
                    if estado_id not in reductions:
                        reductions[estado_id] = {}
                    reductions[estado_id][lookahead] = {
                        "production": production,
                        "production_number": prod_num,
                        "item": str(item)
                    }
            else:
                # Es un elemento de shift
                symbol_after_dot = item.get_symbol_after_dot()
                if symbol_after_dot:
                    if symbol_after_dot in terminals:
                        # Acción de shift
                        if (estado_id, symbol_after_dot) in transiciones:
                            target_state = transiciones[(estado_id, symbol_after_dot)]
                            
                            if symbol_after_dot in action_table[str(estado_id)]:
                                # Conflicto
                                existing_action = action_table[str(estado_id)][symbol_after_dot]
                                conflicts.append({
                                    "state": estado_id,
                                    "symbol": symbol_after_dot,
                                    "conflict_type": "shift_reduce",
                                    "existing_action": existing_action,
                                    "new_action": f"s{target_state}",
                                    "item": str(item)
                                })
                            else:
                                action_table[str(estado_id)][symbol_after_dot] = f"s{target_state}"
                    
                    elif symbol_after_dot in nonterminals:
                        # Acción de goto
                        if (estado_id, symbol_after_dot) in transiciones:
                            target_state = transiciones[(estado_id, symbol_after_dot)]
                            goto_table[str(estado_id)][symbol_after_dot] = target_state
        
        # Agregar acción de aceptación si es el estado inicial con S' -> S •
        if estado_id == 0:
            for item in estado:
                if item.production.startswith("S' ->") and item.is_reduce_item() and item.lookahead == '$':
                    action_table[str(estado_id)]['$'] = "accept"
                    break
    
    return action_table, goto_table, reductions, conflicts


# Función de conveniencia para uso rápido
def analizar_gramatica_lr1(productions: List[str], start_symbol: str = None) -> LR1:
    """
    Función de conveniencia para crear y analizar una gramática LR(1).
    
    Args:
        productions: Lista de producciones de la gramática
        start_symbol: Símbolo inicial (opcional)
    
    Returns:
        LR1: Instancia de la clase LR1 con análisis completo
    """
    lr1 = LR1(productions, start_symbol)
    lr1.calcular_first()
    lr1.calcular_follow()
    return lr1
