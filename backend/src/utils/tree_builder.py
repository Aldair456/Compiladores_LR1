"""
Utilidades para construcción de árboles de derivación desde trace LR(1).
"""

from typing import Dict, Any, List, Optional


def construir_arbol_derivacion(trace_steps: List[Dict], grammar: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Construye el árbol de derivación desde los pasos del trace LR(1).
    
    Args:
        trace_steps: Lista de pasos del trace
        grammar: Gramática opcional para validación
    
    Returns:
        dict: Árbol de derivación
    """
    # Crear mapeo de producciones si se proporciona la gramática
    production_map = {}
    if grammar and 'productions' in grammar:
        for i, production in enumerate(grammar['productions'], 1):
            production_map[i] = production
    
    # Stack para construir el árbol durante el parsing
    tree_stack = []
    
    # Procesar pasos en orden normal (como ocurre el parsing)
    for step in trace_steps:
        action = step.get('action', '')
        
        if action.startswith('s'):  # SHIFT
            # En SHIFT, agregamos el token como hoja al stack
            token = step.get('current_token', '')
            if token and token != '$':  # No agregar el marcador de fin
                tree_stack.append({
                    "node": token,
                    "type": "terminal"
                })
        
        elif action.startswith('r'):  # REDUCE
            # En REDUCE, construimos un nodo no terminal
            reduce_num = int(action[1:])  # Número de reducción
            
            # Obtener la producción
            production_str = None
            left_side = None
            right_symbols = []
            
            if reduce_num in production_map:
                production_str = production_map[reduce_num]
                left_side, right_side = production_str.split(' -> ')
                left_side = left_side.strip()
                right_side = right_side.strip()
                
                # Manejar epsilon (producción vacía)
                if right_side == 'ε' or right_side == 'epsilon':
                    right_symbols = []
                else:
                    right_symbols = right_side.split()
            else:
                # Intentar extraer de la descripción
                description = step.get('description', '')
                if 'REDUCE:' in description:
                    parts = description.split('REDUCE:')
                    if len(parts) > 1:
                        production_part = parts[1].strip().split('(')[0].strip()
                        if ' -> ' in production_part:
                            left_side, right_side = production_part.split(' -> ')
                            left_side = left_side.strip()
                            right_side = right_side.strip()
                            if right_side == 'ε' or right_side == 'epsilon':
                                right_symbols = []
                            else:
                                right_symbols = right_side.split()
            
            if left_side:
                # Crear nodo no terminal
                node = {
                    "node": left_side,
                    "type": "nonterminal",
                    "children": []
                }
                
                # Pop children del stack (tantos como símbolos en el lado derecho)
                num_children = len(right_symbols)
                children = []
                for _ in range(num_children):
                    if tree_stack:
                        children.insert(0, tree_stack.pop())  # Insertar al inicio para orden correcto
                
                node["children"] = children
                
                # Push el nuevo nodo al stack
                tree_stack.append(node)
        
        elif action == 'acc':  # ACCEPT
            # En ACCEPT, el árbol completo está en el stack
            pass
    
    # El árbol final debería estar en el stack
    if tree_stack:
        # Buscar el nodo raíz (normalmente S' o S)
        root = tree_stack[-1]  # El último elemento debería ser la raíz
        
        # Si la raíz es S', extraer su hijo S
        if root.get("node") == "S'" and "children" in root and len(root["children"]) == 1:
            root = root["children"][0]
        
        # Limpiar el árbol
        final_tree = _limpiar_arbol(root)
        return final_tree
    else:
        return {"node": "ERROR", "children": []}


def _limpiar_arbol(node: Dict) -> Dict[str, Any]:
    """
    Limpia el árbol removiendo campos internos y ajustando el formato.
    
    Args:
        node: Nodo del árbol
    
    Returns:
        dict: Nodo limpio
    """
    if node.get("type") == "terminal":
        return {"node": node["node"]}
    else:
        result = {"node": node["node"]}
        if "children" in node and node["children"]:
            result["children"] = [_limpiar_arbol(child) for child in node["children"]]
        return result


def extraer_producciones_desde_trace(trace_steps: List[Dict]) -> List[str]:
    """
    Extrae las producciones utilizadas en el trace para construir el árbol.
    
    Args:
        trace_steps: Lista de pasos del trace
    
    Returns:
        list: Lista de producciones utilizadas (en orden de aplicación)
    """
    productions = []
    
    for step in trace_steps:
        action = step.get('action', '')
        if action.startswith('r'):
            # Extraer información de la descripción
            description = step.get('description', '')
            if 'REDUCE:' in description:
                # Buscar el patrón "REDUCE: X -> Y"
                parts = description.split('REDUCE:')
                if len(parts) > 1:
                    production_part = parts[1].strip()
                    # Extraer hasta el primer paréntesis
                    production = production_part.split('(')[0].strip()
                    if ' -> ' in production:
                        productions.append(production)
    
    return productions


def validar_arbol(tree: Dict[str, Any], grammar: Dict) -> bool:
    """
    Valida que el árbol de derivación sea correcto según la gramática.
    
    Args:
        tree: Árbol de derivación
        grammar: Gramática con producciones
    
    Returns:
        bool: True si el árbol es válido
    """
    if not tree or 'node' not in tree:
        return False
    
    # Si es terminal, no hay más que validar
    if 'children' not in tree:
        return True
    
    # Si es no terminal, verificar que la producción exista
    node_name = tree['node']
    children_names = [child['node'] for child in tree.get('children', [])]
    children_str = ' '.join(children_names) if children_names else 'ε'
    
    production = f"{node_name} -> {children_str}"
    
    # Verificar si existe en la gramática
    if 'productions' in grammar:
        if production not in grammar['productions']:
            return False
    
    # Validar recursivamente los hijos
    for child in tree.get('children', []):
        if not validar_arbol(child, grammar):
            return False
    
    return True


def arbol_a_texto(tree: Dict[str, Any], nivel: int = 0) -> str:
    """
    Convierte el árbol a representación textual con indentación.
    
    Args:
        tree: Árbol de derivación
        nivel: Nivel de indentación
    
    Returns:
        str: Representación textual del árbol
    """
    indent = "  " * nivel
    result = f"{indent}{tree['node']}\n"
    
    if 'children' in tree:
        for child in tree['children']:
            result += arbol_a_texto(child, nivel + 1)
    
    return result