#!/usr/bin/env python3
"""
Test del endpoint lr1-closure con la gramática del usuario
"""

import json
import requests

def test_lr1_closure_endpoint():
    """Test del endpoint lr1-closure"""
    
    url = "https://9i7d8f10ih.execute-api.us-east-1.amazonaws.com/dev/lr1-closure"
    
    # Gramática del usuario
    payload = {
        "start_symbol": "S'",
        "productions": [
            "S' -> S",
            "S -> a A", 
            "A -> b"
        ],
        "options": {
            "augment": True,
            "expand_alternatives": True
        }
    }
    
    print("=== TESTING LR1-CLOSURE ENDPOINT ===")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Response:")
            print(json.dumps(result, indent=2))
            
            # Verificar el estado 0
            if 'closure_table' in result and 'states' in result['closure_table']:
                state_0 = result['closure_table']['states'][0]
                print(f"\nState 0 items:")
                for item in state_0['items']:
                    print(f"  {item}")
                
                # Verificar si contiene A -> • b, $
                items = state_0['items']
                has_a_production = any("A -> • b" in item for item in items)
                print(f"\nContains A -> • b, $: {has_a_production}")
                
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_lr1_closure_endpoint()

