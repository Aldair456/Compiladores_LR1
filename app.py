"""
LR(1) Parser Web Application using Streamlit
Professional frontend for the LR(1) parser implementation
"""

import streamlit as st
import pandas as pd
from lr1_parser import Grammar, LR1Parser
import json
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict


def create_default_grammar():
    """Create a default grammar for demonstration"""
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


def create_simple_grammar():
    """Create a simple grammar for testing"""
    grammar = Grammar()
    
    # Simple grammar: S -> aSb | ab
    grammar.add_production('S', ['a', 'S', 'b'])
    grammar.add_production('S', ['a', 'b'])
    
    grammar.set_start_symbol('S')
    return grammar


def display_grammar_info(grammar):
    """Display grammar information in a professional format"""
    st.subheader("🔧 LR(1) Grammar")
    
    # Grammar display with syntax highlighting
    grammar_text = ""
    for i, (left, right) in enumerate(grammar.productions):
        grammar_text += f"({i}) {left} → {' '.join(right)}\n"
    
    st.code(grammar_text, language="text")
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Start Symbol", grammar.start_symbol)
    with col2:
        st.metric("Nonterminals", len(grammar.nonterminals))
    with col3:
        st.metric("Terminals", len(grammar.terminals))
    with col4:
        st.metric("Productions", len(grammar.productions))


def display_first_table(parser):
    """Display FIRST table"""
    st.subheader("🔍 FIRST Table")
    
    first_data = []
    for nonterminal in sorted(parser.grammar.nonterminals):
        first_set = parser._first_nonterminal(nonterminal)
        first_data.append({
            'Nonterminal': nonterminal,
            'FIRST': '{' + ', '.join(sorted(first_set)) + '}'
        })
    
    first_df = pd.DataFrame(first_data)
    st.dataframe(first_df, use_container_width=True, hide_index=True)


def display_closure_table(parser):
    """Display LR(1) closure table with Kernel and Closure"""
    st.subheader("🔄 LR(1) Closure Table")
    
    closure_data = []
    
    for state_idx, state in enumerate(parser.states):
        # Separate kernel items (original items) from closure items
        kernel_items = []
        closure_items = []
        
        # For simplicity, we'll show all items as closure items
        # In a real implementation, you'd distinguish kernel vs closure
        for item in sorted(state, key=lambda x: (x.production_index, x.dot_position)):
            prod_idx = item.production_index
            left, right = parser.grammar.productions[prod_idx]
            dot_pos = item.dot_position
            right_with_dot = right[:dot_pos] + ['·'] + right[dot_pos:]
            item_str = f"[{left} → {' '.join(right_with_dot)}, {item.lookahead}]"
            
            if item.production_index == 0 and item.dot_position == 0:
                kernel_items.append(item_str)
            else:
                closure_items.append(item_str)
        
        # If no kernel items, use first item as kernel
        if not kernel_items and state:
            first_item = sorted(state, key=lambda x: (x.production_index, x.dot_position))[0]
            prod_idx = first_item.production_index
            left, right = parser.grammar.productions[prod_idx]
            dot_pos = first_item.dot_position
            right_with_dot = right[:dot_pos] + ['·'] + right[dot_pos:]
            kernel_items.append(f"[{left} → {' '.join(right_with_dot)}, {first_item.lookahead}]")
        
        closure_data.append({
            'State': state_idx,
            'Kernel': '; '.join(kernel_items),
            'Closure': '; '.join(closure_items) if closure_items else '; '.join(kernel_items)
        })
    
    closure_df = pd.DataFrame(closure_data)
    st.dataframe(closure_df, use_container_width=True, hide_index=True)


def display_action_goto_table(parser):
    """Display ACTION and GOTO tables in professional format"""
    st.subheader("📊 LR Table (ACTION GOTO)")
    
    # Get all terminals and nonterminals
    terminals = sorted(parser.grammar.terminals)
    nonterminals = sorted(parser.grammar.nonterminals)
    
    # Create combined table
    max_state = max([state for state, _ in parser.action_table.keys()] + 
                   [state for state, _ in parser.goto_table.keys()], default=0)
    
    # Create table data
    table_data = []
    for state in range(max_state + 1):
        row = {'State': state}
        
        # ACTION columns
        for terminal in terminals:
            action = parser.action_table.get((state, terminal), '')
            row[terminal] = action
        
        # GOTO columns  
        for nonterminal in nonterminals:
            goto = parser.goto_table.get((state, nonterminal), '')
            row[nonterminal] = goto
        
        table_data.append(row)
    
    # Create DataFrame
    columns = ['State'] + terminals + nonterminals
    df = pd.DataFrame(table_data, columns=columns)
    
    # Style the table
    st.dataframe(df, use_container_width=True, hide_index=True)


def display_automaton_info(parser):
    """Display automaton information"""
    st.subheader("🤖 LR(1) Automaton")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("States", len(parser.states))
    
    with col2:
        st.metric("Transitions", len(parser.transitions))
    
    with col3:
        st.metric("Action Entries", len(parser.action_table))
    
    # Display states (optional, can be toggled)
    if st.checkbox("Show detailed states"):
        for i, state in enumerate(parser.states):
            with st.expander(f"State {i}"):
                for item in sorted(state, key=lambda x: (x.production_index, x.dot_position)):
                    prod_idx = item.production_index
                    left, right = parser.grammar.productions[prod_idx]
                    dot_pos = item.dot_position
                    right_with_dot = right[:dot_pos] + ['·'] + right[dot_pos:]
                    st.write(f"{left} → {' '.join(right_with_dot)}, {item.lookahead}")


def parse_with_trace(parser, input_tokens):
    """Parse input with step-by-step trace"""
    input_tokens = input_tokens + ['$']  # Add end marker
    stack = [0]  # State stack
    symbol_stack = []  # Symbol stack for tracking
    parse_tree = []
    trace_data = []
    
    i = 0
    step = 0
    
    while i < len(input_tokens):
        current_state = stack[-1]
        current_token = input_tokens[i]
        
        # Create trace entry
        stack_str = ' '.join(map(str, stack))
        input_str = ' '.join(input_tokens[i:])
        
        if (current_state, current_token) in parser.action_table:
            action = parser.action_table[(current_state, current_token)]
            
            trace_data.append({
                'Step': step,
                'Stack': stack_str,
                'Input': input_str,
                'Action': action
            })
            
            if action == 'accept':
                return True, parse_tree, trace_data
            elif action.startswith('shift_'):
                next_state = int(action.split('_')[1])
                stack.append(next_state)
                symbol_stack.append(current_token)
                i += 1
            elif action.startswith('reduce_'):
                prod_idx = int(action.split('_')[1])
                left, right = parser.grammar.productions[prod_idx]
                
                # Pop states and symbols for the right-hand side
                for _ in range(len(right)):
                    if stack:
                        stack.pop()
                    if symbol_stack:
                        symbol_stack.pop()
                
                parse_tree.append(f"{left} → {' '.join(right)}")
                
                # Get goto state
                if stack:
                    current_state = stack[-1]
                    if (current_state, left) in parser.goto_table:
                        next_state = parser.goto_table[(current_state, left)]
                        stack.append(next_state)
                        symbol_stack.append(left)
                    else:
                        return False, [f"Error: No goto state for {left}"], trace_data
                else:
                    return False, ["Error: Empty stack during reduce"], trace_data
            else:
                return False, [f"Error: Unknown action {action}"], trace_data
        else:
            available = [t for (s, t) in parser.action_table.keys() if s == current_state]
            return False, [f"Error: No action for state {current_state} and token '{current_token}'",
                          f"Available tokens: {available}"], trace_data
        
        step += 1
    
    return False, ["Error: End of input reached without accept"], trace_data


def display_parse_trace(trace_data, parse_tree):
    """Display parsing trace and tree"""
    st.subheader("🔍 Parsing Trace")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("**Trace:**")
        trace_df = pd.DataFrame(trace_data)
        st.dataframe(trace_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.write("**Parse Tree:**")
        for i, step in enumerate(parse_tree, 1):
            st.write(f"{i}. {step}")


def main():
    st.set_page_config(
        page_title="LR(1) Parser",
        page_icon="🔧",
        layout="wide"
    )
    
    st.title("🔧 LR(1) Parser Web Application")
    st.markdown("---")
    
    # Sidebar for grammar selection
    st.sidebar.header("⚙️ Configuration")
    
    grammar_type = st.sidebar.selectbox(
        "Select Grammar:",
        ["Expression Grammar", "Simple Grammar", "Custom Grammar"]
    )
    
    # Initialize grammar based on selection
    if grammar_type == "Expression Grammar":
        grammar = create_default_grammar()
    elif grammar_type == "Simple Grammar":
        grammar = create_simple_grammar()
    else:
        # Custom grammar interface
        st.sidebar.subheader("Custom Grammar")
        
        # Start symbol
        start_symbol = st.sidebar.text_input("Start Symbol:", value="S")
        
        # Productions
        st.sidebar.write("**Productions (one per line):**")
        productions_text = st.sidebar.text_area(
            "Format: A -> B C | D",
            value="S -> a S b | a b",
            height=100
        )
        
        # Parse productions
        grammar = Grammar()
        grammar.set_start_symbol(start_symbol)
        
        try:
            for line in productions_text.strip().split('\n'):
                if '->' in line:
                    left, right_part = line.split('->', 1)
                    left = left.strip()
                    
                    # Handle multiple productions separated by |
                    for production in right_part.split('|'):
                        production = production.strip()
                        if production:
                            right = [token.strip() for token in production.split()]
                            grammar.add_production(left, right)
        except Exception as e:
            st.sidebar.error(f"Error parsing grammar: {e}")
            grammar = create_default_grammar()
    
    # Create parser
    try:
        parser = LR1Parser(grammar)
        
        # Display grammar information
        display_grammar_info(grammar)
        
        # Create layout similar to the reference image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # FIRST Table
            display_first_table(parser)
        
        with col2:
            # Closure Table
            display_closure_table(parser)
        
        # ACTION/GOTO Table
        display_action_goto_table(parser)
        
        # Input section
        st.subheader("🎯 Parse Input")
        
        # Example inputs
        if grammar_type == "Expression Grammar":
            example_inputs = [
                "id + id * id",
                "id * id + id",
                "( id + id ) * id",
                "id"
            ]
        elif grammar_type == "Simple Grammar":
            example_inputs = [
                "a b",
                "a a b b",
                "a a a b b b"
            ]
        else:
            example_inputs = ["Enter your input here"]
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Manual Input", "Example Input"]
        )
        
        if input_method == "Manual Input":
            input_string = st.text_input(
                "Enter tokens separated by spaces:",
                placeholder="e.g., id + id * id"
            )
        else:
            input_string = st.selectbox(
                "Select example input:",
                example_inputs
            )
        
        # Parse button with trace
        col1, col2 = st.columns([3, 1])
        with col1:
            max_steps = st.number_input("Maximum number of steps:", min_value=10, max_value=1000, value=100)
        with col2:
            parse_button = st.button("🚀 PARSE", type="primary")
        
        if parse_button:
            if input_string.strip():
                tokens = input_string.strip().split()
                success, parse_tree, trace_data = parse_with_trace(parser, tokens)
                
                if success:
                    st.success("✅ Parse successful!")
                    display_parse_trace(trace_data, parse_tree)
                else:
                    st.error("❌ Parse failed!")
                    for error in parse_tree:
                        st.write(f"• {error}")
            else:
                st.warning("Please enter some input to parse.")
        
        # Statistics section
        st.subheader("📈 Automaton Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("States", len(parser.states))
        
        with col2:
            st.metric("Transitions", len(parser.transitions))
        
        with col3:
            st.metric("Action Entries", len(parser.action_table))
        
        with col4:
            st.metric("GOTO Entries", len(parser.goto_table))
        
    except Exception as e:
        st.error(f"Error creating parser: {e}")
        st.write("Please check your grammar definition.")


if __name__ == "__main__":
    main()
