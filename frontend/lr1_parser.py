"""
LR(1) Parser Implementation in Python (Corrected)
Based on references from:
- https://jsmachines.sourceforge.net/machines/lr1.html
- https://compiler-slr-parser.netlify.app/
- https://light0x00.github.io/parser-generator/
"""

from collections import defaultdict, deque
from typing import List, Dict, Set, Tuple, Optional, Any


class Grammar:
    """Represents a context-free grammar for LR(1) parsing"""
    
    def __init__(self):
        self.productions: List[Tuple[str, List[str]]] = []
        self.nonterminals: Set[str] = set()
        self.terminals: Set[str] = set()
        self.start_symbol: str = ""
        self._first_cache: Dict[str, Set[str]] = {}
        
    def add_production(self, left: str, right: List[str]):
        """Add a production rule A -> α"""
        self.productions.append((left, right))
        self.nonterminals.add(left)
        for symbol in right:
            if symbol != 'ε':  # epsilon
                if symbol.isupper() or symbol.startswith('<'):
                    self.nonterminals.add(symbol)
                else:
                    self.terminals.add(symbol)
    
    def set_start_symbol(self, start: str):
        """Set the start symbol"""
        self.start_symbol = start
        self.nonterminals.add(start)
    
    def get_productions_for(self, nonterminal: str) -> List[Tuple[int, List[str]]]:
        """Get all productions for a given nonterminal"""
        return [(i, right) for i, (left, right) in enumerate(self.productions) 
                if left == nonterminal]
    
    def print_info(self):
        """Print grammar information for debugging"""
        print(f"Start symbol: {self.start_symbol}")
        print(f"Terminals: {self.terminals}")
        print(f"Nonterminals: {self.nonterminals}")
        print(f"Productions: {len(self.productions)}")
    
    def is_terminal(self, symbol: str) -> bool:
        """Check if a symbol is terminal"""
        return symbol in self.terminals or symbol == '$'
    
    def is_nonterminal(self, symbol: str) -> bool:
        """Check if a symbol is nonterminal"""
        return symbol in self.nonterminals


class LR1Item:
    """Represents an LR(1) item [A -> α·β, a]"""
    
    def __init__(self, production_index: int, dot_position: int, lookahead: str):
        self.production_index = production_index
        self.dot_position = dot_position
        self.lookahead = lookahead
    
    def __eq__(self, other):
        return (self.production_index == other.production_index and
                self.dot_position == other.dot_position and
                self.lookahead == other.lookahead)
    
    def __hash__(self):
        return hash((self.production_index, self.dot_position, self.lookahead))
    
    def __str__(self):
        return f"[{self.production_index}, {self.dot_position}, {self.lookahead}]"
    
    def is_complete(self, grammar: Grammar) -> bool:
        """Check if this item is complete (dot at the end)"""
        _, right = grammar.productions[self.production_index]
        return self.dot_position >= len(right)
    
    def get_symbol_after_dot(self, grammar: Grammar) -> Optional[str]:
        """Get the symbol immediately after the dot"""
        _, right = grammar.productions[self.production_index]
        if self.dot_position < len(right):
            return right[self.dot_position]
        return None
    
    def advance_dot(self) -> 'LR1Item':
        """Create a new item with the dot advanced by one position"""
        return LR1Item(self.production_index, self.dot_position + 1, self.lookahead)


class LR1Parser:
    """LR(1) Parser implementation"""
    
    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        self.states: List[Set[LR1Item]] = []
        self.transitions: Dict[Tuple[int, str], int] = {}
        self.action_table: Dict[Tuple[int, str], str] = {}
        self.goto_table: Dict[Tuple[int, str], int] = {}
        self._first_cache: Dict[Tuple, Set[str]] = {}
        
        # Add augmented grammar
        self._augment_grammar()
        self._build_automaton()
        self._build_parsing_tables()
    
    def _augment_grammar(self):
        """Augment the grammar with a new start symbol"""
        original_start = self.grammar.start_symbol
        new_start = f"{original_start}'"
        
        # Add new production S' -> S at index 0
        self.grammar.productions.insert(0, (new_start, [original_start]))
        self.grammar.nonterminals.add(new_start)
        self.grammar.start_symbol = new_start
        self.grammar.terminals.add('$')
    
    def _closure(self, items: Set[LR1Item]) -> Set[LR1Item]:
        """Compute the closure of a set of LR(1) items"""
        closure = set(items)
        changed = True
        
        while changed:
            changed = False
            new_items = set()
            
            for item in closure:
                symbol_after_dot = item.get_symbol_after_dot(self.grammar)
                
                if symbol_after_dot and self.grammar.is_nonterminal(symbol_after_dot):
                    # Get the rest of the production after the symbol
                    _, right = self.grammar.productions[item.production_index]
                    beta = right[item.dot_position + 1:]
                    
                    # Compute FIRST(βa) - only terminals, no epsilon
                    first_beta_a = self._first(beta + [item.lookahead])
                    # Remove epsilon if present
                    first_beta_a.discard('ε')
                    
                    if not first_beta_a:
                        first_beta_a = {item.lookahead}
                    
                    # Add items for all productions of the nonterminal
                    for prod_idx, prod_right in self.grammar.get_productions_for(symbol_after_dot):
                        for terminal in first_beta_a:
                            new_item = LR1Item(prod_idx, 0, terminal)
                            if new_item not in closure:
                                new_items.add(new_item)
                                changed = True
            
            closure.update(new_items)
        
        return closure
    
    def _first(self, symbols: List[str]) -> Set[str]:
        """Compute FIRST set for a sequence of symbols"""
        if not symbols:
            return {'ε'}
        
        # Create a hashable key for caching
        key = tuple(symbols)
        if key in self._first_cache:
            return self._first_cache[key].copy()
        
        first_set = set()
        all_have_epsilon = True
        
        for symbol in symbols:
            if symbol == 'ε':
                first_set.add('ε')
                break
            elif self.grammar.is_terminal(symbol):
                first_set.add(symbol)
                all_have_epsilon = False
                break
            else:
                # FIRST of nonterminal
                symbol_first = self._first_nonterminal(symbol)
                first_set.update(symbol_first - {'ε'})
                
                if 'ε' not in symbol_first:
                    all_have_epsilon = False
                    break
        
        if all_have_epsilon:
            first_set.add('ε')
        
        self._first_cache[key] = first_set.copy()
        return first_set
    
    def _first_nonterminal(self, nonterminal: str) -> Set[str]:
        """Compute FIRST set for a nonterminal"""
        first_set = set()
        
        for _, right in self.grammar.get_productions_for(nonterminal):
            if not right or right == ['ε']:
                first_set.add('ε')
            else:
                first_set.update(self._first(right))
        
        return first_set if first_set else {'ε'}
    
    def _goto(self, items: Set[LR1Item], symbol: str) -> Set[LR1Item]:
        """Compute GOTO function"""
        goto_items = set()
        
        for item in items:
            symbol_after_dot = item.get_symbol_after_dot(self.grammar)
            if symbol_after_dot == symbol:
                goto_items.add(item.advance_dot())
        
        return self._closure(goto_items)
    
    def _build_automaton(self):
        """Build the LR(1) automaton"""
        # Initial state - S' -> ·S with lookahead $
        initial_item = LR1Item(0, 0, '$')
        initial_state = self._closure({initial_item})
        
        print(f"[DEBUG] Initial state has {len(initial_state)} items:")
        for item in sorted(initial_state, key=lambda x: (x.production_index, x.dot_position)):
            prod_idx = item.production_index
            left, right = self.grammar.productions[prod_idx]
            dot_pos = item.dot_position
            right_with_dot = right[:dot_pos] + ['·'] + right[dot_pos:]
            print(f"  {left} -> {' '.join(right_with_dot)}, {item.lookahead}")
        
        self.states = [initial_state]
        state_queue = deque([0])
        
        while state_queue:
            state_idx = state_queue.popleft()
            current_state = self.states[state_idx]
            
            # Get all symbols that can be transitioned on
            symbols = set()
            for item in current_state:
                symbol_after_dot = item.get_symbol_after_dot(self.grammar)
                if symbol_after_dot:
                    symbols.add(symbol_after_dot)
            
            # Compute transitions
            for symbol in symbols:
                next_state = self._goto(current_state, symbol)
                
                if next_state:
                    # Check if this state already exists
                    existing_state_idx = None
                    for i, existing_state in enumerate(self.states):
                        if existing_state == next_state:
                            existing_state_idx = i
                            break
                    
                    if existing_state_idx is None:
                        # Add new state
                        existing_state_idx = len(self.states)
                        self.states.append(next_state)
                        state_queue.append(existing_state_idx)
                    
                    # Record transition
                    self.transitions[(state_idx, symbol)] = existing_state_idx
    
    def _build_parsing_tables(self):
        """Build ACTION and GOTO tables"""
        for state_idx, state in enumerate(self.states):
            for item in state:
                if item.is_complete(self.grammar):
                    # Reduce action
                    if item.production_index == 0:  # S' -> S
                        self.action_table[(state_idx, item.lookahead)] = 'accept'
                    else:
                        self.action_table[(state_idx, item.lookahead)] = f'reduce_{item.production_index}'
                else:
                    # Shift or goto action
                    symbol_after_dot = item.get_symbol_after_dot(self.grammar)
                    if symbol_after_dot and (state_idx, symbol_after_dot) in self.transitions:
                        next_state = self.transitions[(state_idx, symbol_after_dot)]
                        if self.grammar.is_terminal(symbol_after_dot):
                            self.action_table[(state_idx, symbol_after_dot)] = f'shift_{next_state}'
                        else:
                            self.goto_table[(state_idx, symbol_after_dot)] = next_state
    
    def parse(self, input_tokens: List[str]) -> Tuple[bool, List[str]]:
        """Parse a sequence of tokens"""
        input_tokens = input_tokens + ['$']  # Add end marker
        stack = [0]  # State stack
        symbol_stack = []  # Symbol stack for tracking
        parse_tree = []
        
        i = 0
        while i < len(input_tokens):
            current_state = stack[-1]
            current_token = input_tokens[i]
            
            if (current_state, current_token) in self.action_table:
                action = self.action_table[(current_state, current_token)]
                
                if action == 'accept':
                    return True, parse_tree
                elif action.startswith('shift_'):
                    next_state = int(action.split('_')[1])
                    stack.append(next_state)
                    symbol_stack.append(current_token)
                    i += 1
                elif action.startswith('reduce_'):
                    prod_idx = int(action.split('_')[1])
                    left, right = self.grammar.productions[prod_idx]
                    
                    # Pop states and symbols for the right-hand side
                    for _ in range(len(right)):
                        if stack:
                            stack.pop()
                        if symbol_stack:
                            symbol_stack.pop()
                    
                    parse_tree.append(f"{left} -> {' '.join(right)}")
                    
                    # Get goto state
                    if stack:
                        current_state = stack[-1]
                        if (current_state, left) in self.goto_table:
                            next_state = self.goto_table[(current_state, left)]
                            stack.append(next_state)
                            symbol_stack.append(left)
                        else:
                            return False, [f"Error: No goto state for {left} from state {current_state}"]
                    else:
                        return False, ["Error: Empty stack during reduce"]
                else:
                    return False, [f"Error: Unknown action {action}"]
            else:
                available = [t for (s, t) in self.action_table.keys() if s == current_state]
                return False, [f"Error: No action for state {current_state} and token '{current_token}'",
                              f"Available tokens: {available}"]
        
        return False, ["Error: End of input reached without accept"]
    
    def print_states(self):
        """Print all states for debugging"""
        for i, state in enumerate(self.states):
            print(f"\nState {i}:")
            for item in sorted(state, key=lambda x: (x.production_index, x.dot_position)):
                prod_idx = item.production_index
                left, right = self.grammar.productions[prod_idx]
                dot_pos = item.dot_position
                
                # Build the item string with dot
                right_with_dot = right[:dot_pos] + ['·'] + right[dot_pos:]
                print(f"  {left} -> {' '.join(right_with_dot)}, {item.lookahead}")


def create_example_grammar() -> Grammar:
    """Create an example grammar for testing"""
    grammar = Grammar()
    
    # Example grammar: E -> E + T | T, T -> T * F | F, F -> (E) | id
    grammar.add_production('E', ['E', '+', 'T'])
    grammar.add_production('E', ['T'])
    grammar.add_production('T', ['T', '*', 'F'])
    grammar.add_production('T', ['F'])
    grammar.add_production('F', ['(', 'E', ')'])
    grammar.add_production('F', ['id'])
    
    grammar.set_start_symbol('E')
    
    return grammar


if __name__ == "__main__":
    # Test the parser
    grammar = create_example_grammar()
    
    print("=== GRAMMAR INFO (BEFORE AUGMENTATION) ===")
    grammar.print_info()
    print(f"\nIs 'E' a nonterminal? {grammar.is_nonterminal('E')}")
    print(f"Is 'T' a nonterminal? {grammar.is_nonterminal('T')}")
    print(f"Is 'F' a nonterminal? {grammar.is_nonterminal('F')}")
    print(f"Is 'id' a terminal? {grammar.is_terminal('id')}")
    
    parser = LR1Parser(grammar)
    
    print("\n=== GRAMMAR INFO (AFTER AUGMENTATION) ===")
    print(f"Is 'E'' a nonterminal? {grammar.is_nonterminal('E\'')}")
    
    # Test input: id + id * id
    test_input = ['id', '+', 'id', '*', 'id']
    
    print("\nGrammar Productions:")
    for i, (left, right) in enumerate(grammar.productions):
        print(f"{i}: {left} -> {' '.join(right)}")
    
    print(f"\nParsing: {' '.join(test_input)}")
    success, parse_tree = parser.parse(test_input)
    
    if success:
        print("✓ Parse successful!")
        print("Parse tree (reductions):")
        for step in parse_tree:
            print(f"  {step}")
    else:
        print("✗ Parse failed!")
        for error in parse_tree:
            print(f"  {error}")
    
    print(f"\nNumber of states: {len(parser.states)}")
    print(f"Number of transitions: {len(parser.transitions)}")
    print(f"Action table entries: {len(parser.action_table)}")
    print(f"GOTO table entries: {len(parser.goto_table)}")
    
    # Uncomment to see detailed state information
    # parser.print_states()