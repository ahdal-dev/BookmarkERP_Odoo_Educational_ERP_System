#!/usr/bin/env python3
"""
MCP Server for ChatBot RAG
Pure MCP: the LLM decides the tool (sql_query or rag_search).
"""

import asyncio, json, logging, numpy as np
from typing import Any, Dict, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from sqlalchemy import text

# Imports from your project
from database import get_sql_db, get_db
from llm import generate_sql, get_gemini, make_prompt, rewrite_query_with_history, judge_answer_llm, make_unknown_reply_llm
from ingestion import embed_query
from models import Chat, ChatMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatBotMCPServer:
    def __init__(self):
        self.server = Server("chatbot-rag")
        self.setup_handlers()

    def setup_handlers(self):
        """Expose MCP tools only — no classification inside server."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="sql_query",
                    description="Run a structured SQL query on the medical schema",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {"type": "string"},
                            "schema": {"type": "string"}
                        },
                        "required": ["question", "schema"]
                    }
                ),
                Tool(
                    name="rag_search",
                    description="Run a semantic vector search on documents",
                    inputSchema={
                        "type": "object",
                        "properties": {"question": {"type": "string"}, "org_id": {"type": "string"}},
                        "required": ["question", "org_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            if name == "sql_query":
                return [TextContent(type="text", text=await self.handle_sql_query(arguments))]
            elif name == "rag_search":
                return [TextContent(type="text", text=await self.handle_rag_search(arguments))]
            else:
                return [TextContent(type="text", text=f"Unknown tool {name}")]

    async def handle_sql_query(self, args: Dict[str, Any]) -> str:
        """Executes SQL query via LLM-generated query."""
        question = args["question"]
        schema = args.get("schema", "medical")
        try:
            with next(get_sql_db()) as sql_db:
                sql_query = generate_sql(question, schema)
                rows = sql_db.execute(text(sql_query)).fetchall()
                data = [dict(r._mapping) for r in rows]
                return json.dumps(data, indent=2) if data else "No results found."
        except Exception as e:
            return f"SQL error: {e}"

    async def handle_rag_search(self, args: Dict[str, Any]) -> str:
        """Executes RAG pipeline with embeddings + LLM."""
        question = args["question"]
        org_id = args["org_id"]

        qvec = embed_query(question)
        qvec_np = np.array(qvec, dtype=np.float32)

        with next(get_db()) as db:
            rows = db.execute(
                text("""
                    SELECT dc.content, d.filename, (dc.embedding <=> (:q)::vector) AS distance
                    FROM document_chunks dc
                    JOIN documents d ON d.id = dc.document_id
                    WHERE d.organization_id = :org
                    ORDER BY dc.embedding <=> (:q)::vector
                    LIMIT 8
                """),
                {"q": qvec_np.tolist(), "org": str(org_id)}
            ).fetchall()

            if not rows:
                return make_unknown_reply_llm(question)

            snippets = [r.content for r in rows]
            model = get_gemini()
            rsp = model.generate_content(make_prompt(question, snippets))
            answer = (getattr(rsp, "text", "") or "").strip()
            return answer

    async def run(self):
        """Run the MCP server over stdio."""
        async with stdio_server() as (read, write):
            await self.server.run(
                read, write,
                InitializationOptions(
                    server_name="chatbot-rag",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities()
                )
            )

async def main():
    server = ChatBotMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())