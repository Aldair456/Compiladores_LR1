import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Set, Tuple
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
