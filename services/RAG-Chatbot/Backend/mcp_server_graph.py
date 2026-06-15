import os
import json
from typing import List, Dict, Any, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    CallToolRequest, CallToolResult, ListResourcesRequest, ListResourcesResult,
    ReadResourceRequest, ReadResourceResult
)

from graph import get_neo4j_driver
from llm import get_gemini

# Initialize MCP server
server = Server("chatbot-graph-mcp")

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available graph database resources"""
    return [
        Resource(
            uri="graph://entities",
            name="Graph Entities",
            description="All entities in the knowledge graph",
            mimeType="application/json"
        ),
        Resource(
            uri="graph://relationships", 
            name="Graph Relationships",
            description="All relationships in the knowledge graph",
            mimeType="application/json"
        ),
        Resource(
            uri="graph://schema",
            name="Graph Schema",
            description="Graph database schema and structure",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read graph database resources"""
    driver = get_neo4j_driver()
    
    with driver.session() as session:
        if uri == "graph://entities":
            result = session.run("MATCH (e:Entity) RETURN e.name as name, e.org_id as org_id LIMIT 100")
            entities = [{"name": record["name"], "org_id": record["org_id"]} for record in result]
            return json.dumps(entities, indent=2)
            
        elif uri == "graph://relationships":
            result = session.run("""
                MATCH (s:Entity)-[r]->(o:Entity) 
                RETURN s.name as subject, type(r) as predicate, o.name as object, r.org_id as org_id 
                LIMIT 100
            """)
            relationships = [
                {
                    "subject": record["subject"], 
                    "predicate": record["predicate"], 
                    "object": record["object"],
                    "org_id": record["org_id"]
                } 
                for record in result
            ]
            return json.dumps(relationships, indent=2)
            
        elif uri == "graph://schema":
            result = session.run("CALL db.schema.visualization()")
            schema = [dict(record) for record in result]
            return json.dumps(schema, indent=2)
    
    return "Resource not found"

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available graph database tools"""
    return [
        Tool(
            name="graph_search",
            description="Search the knowledge graph for entities and relationships",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query about entities and relationships"
                    },
                    "org_id": {
                        "type": "string", 
                        "description": "Organization ID to filter results"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results to return",
                        "default": 50
                    }
                },
                "required": ["query", "org_id"]
            }
        ),
        Tool(
            name="graph_traverse",
            description="Traverse relationships from a specific entity",
            inputSchema={
                "type": "object",
                "properties": {
                    "entity": {
                        "type": "string",
                        "description": "Name of the entity to start traversal from"
                    },
                    "org_id": {
                        "type": "string",
                        "description": "Organization ID to filter results"
                    },
                    "max_depth": {
                        "type": "integer", 
                        "description": "Maximum traversal depth",
                        "default": 2
                    },
                    "relationship_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific relationship types to follow (optional)"
                    }
                },
                "required": ["entity", "org_id"]
            }
        ),
        Tool(
            name="graph_analyze",
            description="Analyze graph structure and patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "org_id": {
                        "type": "string",
                        "description": "Organization ID to analyze"
                    },
                    "analysis_type": {
                        "type": "string",
                        "enum": ["centrality", "clusters", "paths", "summary"],
                        "description": "Type of analysis to perform"
                    }
                },
                "required": ["org_id", "analysis_type"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute graph database tools"""
    driver = get_neo4j_driver()
    
    try:
        if name == "graph_search":
            return await _graph_search(driver, arguments)
        elif name == "graph_traverse":
            return await _graph_traverse(driver, arguments)
        elif name == "graph_analyze":
            return await _graph_analyze(driver, arguments)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error executing {name}: {str(e)}")]

async def _graph_search(driver, args: Dict[str, Any]) -> List[TextContent]:
    """Search the knowledge graph using natural language"""
    query = args.get("query", "")
    org_id = args.get("org_id", "")
    limit = args.get("limit", 50)
    
    # Use LLM to convert natural language to Cypher query
    model = get_gemini()
    cypher_prompt = f"""
Convert this natural language query to a Neo4j Cypher query:

Query: "{query}"

IMPORTANT: Use these exact labels and structure:
- All nodes have label: Entity
- All nodes have property: org_id
- Relationships are between Entity nodes
- Use org_id property to filter: {{org_id: "{org_id}"}}

Rules:
- Search for entities that contain keywords from the query
- Find relationships between entities
- Use flexible text matching (CONTAINS, STARTS WITH, etc.)
- Return entity names, relationship types, and related entities
- Limit results to {limit}
- Use Entity labels, not Organization or Keyword

Example queries:
1. For "blood pressure": MATCH (e:Entity {{org_id: "{org_id}"}}) WHERE toLower(e.name) CONTAINS "blood" OR toLower(e.name) CONTAINS "pressure" RETURN e.name as entity, labels(e) as labels LIMIT {limit}

2. For relationships: MATCH (e1:Entity {{org_id: "{org_id}"}})-[r]->(e2:Entity {{org_id: "{org_id}"}}) WHERE toLower(e1.name) CONTAINS "blood" OR toLower(e2.name) CONTAINS "pressure" RETURN e1.name as from, type(r) as relationship, e2.name as to LIMIT {limit}

3. For general search: MATCH (e:Entity {{org_id: "{org_id}"}}) WHERE toLower(e.name) CONTAINS "search_term" RETURN e.name as entity, labels(e) as labels LIMIT {limit}

Return ONLY the Cypher query, no explanations.
"""
    
    cypher_response = model.generate_content(cypher_prompt)
    cypher_query = cypher_response.text.strip()
    
    # Clean up the query
    if cypher_query.startswith("```cypher"):
        cypher_query = cypher_query.replace("```cypher", "").replace("```", "").strip()
    elif cypher_query.startswith("```"):
        cypher_query = cypher_query.replace("```", "").strip()
    
    print(f" Generated Cypher query: {cypher_query}")
    
    # Execute the query
    with driver.session() as session:
        try:
            result = session.run(cypher_query, {"org_id": org_id})
            records = list(result)
            
            print(f" Query returned {len(records)} records")
            
            if not records:
                # Try a simpler fallback query
                print(" Trying fallback query...")
                fallback_query = f"""
                MATCH (e:Entity {{org_id: "{org_id}"}}) 
                WHERE toLower(e.name) CONTAINS "blood" OR toLower(e.name) CONTAINS "pressure" OR toLower(e.name) CONTAINS "hypertension"
                RETURN e.name as entity, labels(e) as labels
                LIMIT {limit}
                """
                result = session.run(fallback_query)
                records = list(result)
                print(f" Fallback query returned {len(records)} records")
            
            if not records:
                return [TextContent(type="text", text="No results found for the query. The graph database may not contain relevant data for this topic.")]
            
            # Format results
            formatted_results = []
            for record in records:
                formatted_results.append(dict(record))
            
            print(f" Formatted results: {formatted_results[:3]}...")  # Show first 3 results
            
            return [TextContent(
                type="text", 
                text=f"Graph Search Results:\n\n{json.dumps(formatted_results, indent=2)}"
            )]
            
        except Exception as e:
            print(f" Query execution error: {str(e)}")
            return [TextContent(type="text", text=f"Query execution error: {str(e)}")]

async def _graph_traverse(driver, args: Dict[str, Any]) -> List[TextContent]:
    """Traverse relationships from a specific entity"""
    entity = args.get("entity", "")
    org_id = args.get("org_id", "")
    max_depth = args.get("max_depth", 2)
    relationship_types = args.get("relationship_types", [])
    
    # Build relationship filter
    rel_filter = ""
    if relationship_types:
        rel_types_str = "|".join(relationship_types)
        rel_filter = f"WHERE type(r) IN ['{rel_types_str}']"
    
    cypher_query = f"""
    MATCH path = (start:Entity {{name: $entity, org_id: $org_id}})-[r*1..{max_depth}]->(end:Entity {{org_id: $org_id}})
    {rel_filter}
    RETURN path, length(path) as depth
    ORDER BY depth
    LIMIT 100
    """
    
    with driver.session() as session:
        result = session.run(cypher_query, {"entity": entity, "org_id": org_id})
        records = list(result)
        
        if not records:
            return [TextContent(type="text", text=f"No paths found from entity '{entity}'.")]
        
        # Format traversal results
        paths = []
        for record in records:
            path = record["path"]
            depth = record["depth"]
            
            # Extract nodes and relationships from path
            nodes = [node["name"] for node in path.nodes]
            relationships = [rel.type for rel in path.relationships]
            
            paths.append({
                "path": " -> ".join(nodes),
                "relationships": relationships,
                "depth": depth
            })
        
        return [TextContent(
            type="text",
            text=f"Graph Traversal from '{entity}':\n\n{json.dumps(paths, indent=2)}"
        )]

async def _graph_analyze(driver, args: Dict[str, Any]) -> List[TextContent]:
    """Analyze graph structure and patterns"""
    org_id = args.get("org_id", "")
    analysis_type = args.get("analysis_type", "summary")
    
    with driver.session() as session:
        if analysis_type == "summary":
            # Basic graph statistics
            stats_query = """
            MATCH (e:Entity {org_id: $org_id})
            OPTIONAL MATCH (e)-[r]->(o:Entity {org_id: $org_id})
            RETURN 
                count(DISTINCT e) as entity_count,
                count(DISTINCT r) as relationship_count,
                count(DISTINCT type(r)) as relationship_type_count
            """
            result = session.run(stats_query, {"org_id": org_id})
            stats = dict(result.single())
            
            return [TextContent(
                type="text",
                text=f"Graph Summary for org {org_id}:\n{json.dumps(stats, indent=2)}"
            )]
            
        elif analysis_type == "centrality":
            # Find most connected entities
            centrality_query = """
            MATCH (e:Entity {org_id: $org_id})-[r]->(o:Entity {org_id: $org_id})
            RETURN e.name as entity, count(r) as connections
            ORDER BY connections DESC
            LIMIT 10
            """
            result = session.run(centrality_query, {"org_id": org_id})
            centrality = [dict(record) for record in result]
            
            return [TextContent(
                type="text",
                text=f"Most Connected Entities:\n{json.dumps(centrality, indent=2)}"
            )]
            
        elif analysis_type == "clusters":
            # Find relationship clusters
            cluster_query = """
            MATCH (e:Entity {org_id: $org_id})-[r]->(o:Entity {org_id: $org_id})
            RETURN type(r) as relationship_type, count(*) as frequency
            ORDER BY frequency DESC
            LIMIT 20
            """
            result = session.run(cluster_query, {"org_id": org_id})
            clusters = [dict(record) for record in result]
            
            return [TextContent(
                type="text",
                text=f"Relationship Clusters:\n{json.dumps(clusters, indent=2)}"
            )]
            
        else:
            return [TextContent(type="text", text="Unknown analysis type")]

async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="chatbot-graph-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
