#!/usr/bin/env python3
"""
MCP Mode Switcher
Easy script to switch between different MCP modes
"""

import os
import sys

def show_current_mode():
    """Show the current MCP mode"""
    try:
        with open('mcp_config.py', 'r') as f:
            content = f.read()
            
        for line in content.split('\n'):
            if line.strip().startswith('MCP_MODE = '):
                mode = line.split('=')[1].strip().strip('"\'')
                print(f"Current MCP Mode: {mode}")
                return mode
    except Exception as e:
        print(f"Error reading config: {e}")
        return None

def switch_mode(new_mode):
    """Switch to a new MCP mode"""
    valid_modes = ['sql_vector', 'sql_graph', 'sql_vector_graph']
    
    if new_mode not in valid_modes:
        print(f"Invalid mode: {new_mode}")
        print(f"Valid modes: {', '.join(valid_modes)}")
        return False
    
    try:
        with open('mcp_config.py', 'r') as f:
            content = f.read()
        
        # Replace the MCP_MODE line
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if line.strip().startswith('MCP_MODE = '):
                new_lines.append(f'MCP_MODE = "{new_mode}"')
            else:
                new_lines.append(line)
        
        with open('mcp_config.py', 'w') as f:
            f.write('\n'.join(new_lines))
        
        print(f"Successfully switched to: {new_mode}")
        return True
        
    except Exception as e:
        print(f" Error switching mode: {e}")
        return False

def show_help():
    
    print("""
MCP Mode Switcher

Usage:
    python switch_mcp_mode.py [mode]

Available modes:
    sql_vector        - SQL + Vector Database (Original RAG)
    sql_graph         - SQL + Graph Database (Knowledge Graph)  
    sql_vector_graph  - SQL + Vector + Graph Database (Hybrid)

Examples:
    python switch_mcp_mode.py sql_graph
    python switch_mcp_mode.py hybrid
    python switch_mcp_mode.py status

Commands:
    status            - Show current mode
    help              - Show this help
""")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        show_current_mode()
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'help':
        show_help()
    elif command == 'status':
        show_current_mode()
    elif command in ['sql_vector', 'sql_graph', 'sql_vector_graph']:
        current = show_current_mode()
        if current != command:
            if switch_mode(command):
                print(f" Restart your FastAPI server to apply changes!")
                print(f"   Old mode: {current}")
                print(f"   New mode: {command}")
        else:
            print(f" Already in {command} mode")
    else:
        print(f" Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
