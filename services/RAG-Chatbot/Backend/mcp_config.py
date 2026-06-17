# MCP Configuration - Switch between different database combinations
# Comment/uncomment the desired mode

# ==========================================
# MODE 1: SQL + Vector Database (Original)
# ==========================================
# Use this for traditional RAG with vector search + SQL queries
# MCP_MODE = "sql_vector"

# ==========================================
# MODE 2: SQL + Graph Database  
# ==========================================
# Use this for knowledge graph reasoning + SQL queries
# MCP_MODE = "sql_graph"

# ==========================================
# MODE 3: SQL + Vector + Graph Database (Combined)
# ==========================================
# Use this for hybrid approach with all three databases
MCP_MODE = "sql_vector_graph"

# ==========================================
# ENDPOINT MAPPING
# ==========================================
ENDPOINT_MAPPING = {
    "sql_vector": {
        "ask_endpoint": "/mcp/pure-ask",
        "description": "SQL + Vector Database (Original RAG)"
    },
    "sql_graph": {
        "ask_endpoint": "/mcp/graph/ask", 
        "description": "SQL + Graph Database (Knowledge Graph)"
    },
    "sql_vector_graph": {
        "ask_endpoint": "/mcp/hybrid-ask",
        "description": "SQL + Vector + Graph Database (Hybrid)"
    }
}

def get_current_mode():
    """Get the currently active MCP mode"""
    return MCP_MODE

def get_ask_endpoint():
    """Get the ask endpoint for the current mode"""
    return ENDPOINT_MAPPING[MCP_MODE]["ask_endpoint"]

def get_mode_description():
    """Get description of the current mode"""
    return ENDPOINT_MAPPING[MCP_MODE]["description"]
