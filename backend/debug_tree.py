#!/usr/bin/env python3
"""
Debug del árbol de derivación
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from utils.tree_builder import construir_arbol_derivacion

def debug_tree_construction():
    """Debug paso a paso de la construcción del árbol"""
    
    trace_steps = [
        {
            "step": 1,
            "state": 0,
            "stack": [0],
            "input_position": 0,
            "current_token": "a",
            "action": "s3",
            "description": "SHIFT: mover 'a' al stack, ir al estado 3"
        },
        {
            "step": 2,
            "state": 3,
            "stack": [0, 3],
            "input_position": 1,
            "current_token": "b",
            "action": "s2",
            "description": "SHIFT: mover 'b' al stack, ir al estado 2"
        },
        {
            "step": 3,
            "state": 2,
            "stack": [0, 3, 2],
            "input_position": 2,
            "current_token": "$",
            "action": "r2",
            "description": "REDUCE: A -> b (pop 1), GOTO(3, A) = 4"
        },
        {
            "step": 4,
            "state": 4,
            "stack": [0, 3, 4],
            "input_position": 2,
            "current_token": "$",
            "action": "r1",
            "description": "REDUCE: S -> a A (pop 2), GOTO(0, S) = 1"
        },
        {
            "step": 5,
            "state": 1,
            "stack": [0, 1],
            "input_position": 2,
            "current_token": "$",
            "action": "acc",
            "description": "ACCEPT: Cadena aceptada"
        }
    ]
    
    grammar = {
        "productions": [
            "S -> a A",
            "A -> b"
        ]
    }
    
    print("=== DEBUGGING TREE CONSTRUCTION ===")
    print("Trace steps (in order):")
    for i, step in enumerate(trace_steps):
        print(f"  {i+1}. {step['action']} - {step['description']}")
    
    print("\nTrace steps (reversed order for processing):")
    for i, step in enumerate(reversed(trace_steps)):
        print(f"  {i+1}. {step['action']} - {step['description']}")
    
    print("\nBuilding tree...")
    tree = construir_arbol_derivacion(trace_steps, grammar)
    
    print("\nResulting tree:")
    import json
    print(json.dumps(tree, indent=2))
    
    print("\nExpected tree:")
    expected = {
        "node": "S'",
        "children": [
            {
                "node": "S",
                "children": [
                    { "node": "a" },
                    {
                        "node": "A",
                        "children": [
                            { "node": "b" }
                        ]
                    }
                ]
            }
        ]
    }
    print(json.dumps(expected, indent=2))

if __name__ == "__main__":
    debug_tree_construction()
