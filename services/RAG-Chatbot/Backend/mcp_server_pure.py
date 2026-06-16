#!/usr/bin/env python3
"""
Pure MCP Server for ChatBot RAG
The LLM decides which tool to call - no classification in the server.
"""

import asyncio
import json
import logging
import numpy as np
from typing import Any, Dict, List
from mcp.server import Server

from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from sqlalchemy import text

# Imports from your project
from database import get_sql_db, get_db
from llm import generate_sql, get_gemini, make_prompt, rewrite_query_with_history, judge_answer_llm, make_unknown_reply_llm, cross_validate_answer_llm
from ingestion import embed_query
from models import Chat, ChatMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PureChatBotMCPServer:
    def __init__(self):
        self.server = Server("chatbot-rag-pure")
        self.setup_handlers()

    def setup_handlers(self):
        """Expose MCP tools - LLM decides which tool to call."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="sql_query",
                    description="Execute a SQL query on the medical database. Use for structured queries like 'show me all doctors', 'how many patients', 'list appointments', etc.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question that requires database querying"
                            },
                            "schema": {
                                "type": "string",
                                "description": "Database schema to query",
                                "default": "medical"
                            }
                        },
                        "required": ["question"]
                    }
                ),
                Tool(
                    name="rag_search",
                    description="Search through uploaded documents using semantic similarity. Use for general knowledge questions, medical information, document content, etc.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "The question to search for in documents"
                            },
                            "org_id": {
                                "type": "string",
                                "description": "Organization ID for document search"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User ID for chat history context"
                            }
                        },
                        "required": ["question", "org_id", "user_id"]
                    }
                ),
                Tool(
                    name="greeting",
                    description="Respond to greetings and casual conversation. Use for simple greetings like 'hello', 'hi', 'how are you'.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "The greeting message"
                            }
                        },
                        "required": ["message"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool_handler(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                if name == "sql_query":
                    result = await self.handle_sql_query(arguments)
                elif name == "rag_search":
                    result = await self.handle_rag_search(arguments)
                elif name == "greeting":
                    result = await self.handle_greeting(arguments)
                else:
                    result = f"Unknown tool: {name}"
                
                return [TextContent(type="text", text=result)]
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> tuple[List[TextContent], list]:
        
        try:
            sources = []
            if name == "sql_query":
                result = await self.handle_sql_query(arguments)
            elif name == "rag_search":
                result, sources = await self.handle_rag_search(arguments)
            elif name == "greeting":
                result = await self.handle_greeting(arguments)
            else:
                result = f"Unknown tool: {name}"
            
            return [TextContent(type="text", text=result)], sources
        except Exception as e:
            logger.error(f"Error in tool {name}: {e}")
            return [TextContent(type="text", text=f"Error: {str(e)}")], []

    async def handle_sql_query(self, args: Dict[str, Any]) -> str:
        
        question = args["question"]
        schema = args.get("schema", "medical")
        
        print(f" MCP SQL Query: {question}")
        
        try:
            with next(get_sql_db()) as sql_db:
                sql_query = generate_sql(question, schema)
                print(f" Generated SQL: {sql_query}")
                
                rows = sql_db.execute(text(sql_query)).fetchall()
                data = [dict(r._mapping) for r in rows]
                
                if not data:
                    return "No results found."
                
                # Format results nicely
                if len(data) == 1:
                    result = "Here's the result:<br>"
                    for key, value in data[0].items():
                        formatted_key = key.replace('_', ' ').title()
                        result += f"• {formatted_key}: {value}<br>"
                    return result.strip()
                
                result = f"Found {len(data)} results:<br><br>"
                for i, row in enumerate(data, 1):
                    result += f"<strong>Record {i}:</strong><br>"
                    for key, value in row.items():
                        formatted_key = key.replace('_', ' ').title()
                        result += f"&nbsp;&nbsp;• {formatted_key}: {value}<br>"
                    result += "<br>"
                
                return result.strip()
                
        except Exception as e:
            print(f" SQL error: {e}")
            return f"SQL error: {str(e)}"

    async def handle_rag_search(self, args: Dict[str, Any]) -> tuple[str, list]:
        """Execute RAG pipeline with embeddings + LLM."""
        question = args["question"]
        org_id = args["org_id"]
        user_id = args["user_id"]
        
        print(f" MCP RAG Search: {question}")
        
        try:
            # Get vector embeddings
            qvec = embed_query(question)
            qvec_np = np.array(qvec, dtype=np.float32)

            with next(get_db()) as db:
                # Get chat history for context
                chat = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).first()
                history = []
                
                if chat:
                    history_rows = (
                        db.query(ChatMessage)
                        .filter(ChatMessage.chat_id == chat.id)
                        .order_by(ChatMessage.created_at.desc())
                        .limit(8)
                        .all()
                    )
                    history = [(m.role, m.content) for m in reversed(history_rows)]

                # Search vector database
                rows = db.execute(
                    text("""
                        SELECT 
                            dc.content, 
                            d.filename, 
                            (dc.embedding <=> (:q)::vector) AS distance
                        FROM document_chunks dc
                        JOIN documents d ON d.id = dc.document_id
                        WHERE d.organization_id = :org
                        ORDER BY dc.embedding <=> (:q)::vector
                        LIMIT 8
                    """),
                    {"q": qvec_np.tolist(), "org": str(org_id)}
                ).fetchall()

                if not rows:
                    return make_unknown_reply_llm(question), []

                # Process results
                snippets = [r.content for r in rows]
                
                # Add sources
                unique_filenames = []
                seen = set()
                for r in rows:
                    if r.filename and r.filename not in seen:
                        unique_filenames.append(r.filename)
                        seen.add(r.filename)
                
                print(f"Found {len(rows)} document chunks with {len(unique_filenames)} unique sources")

                # Generate answer using LLM
                model = get_gemini()
                prompt = make_prompt(question, snippets, history)
                rsp = model.generate_content(prompt)
                answer = (getattr(rsp, "text", "") or "").strip()
                
                # Judge if answer is good
                judge_result = judge_answer_llm(question, snippets, answer)
                
                if judge_result.get("status") == "unknown":
                    final_answer = judge_result.get("reply_if_unknown", "I don't have enough information to answer that question.")
                    sources_to_return = []
                else:
                    final_answer = answer
                    sources_to_return = unique_filenames
                    
                    # Add sources to the answer text (like your regular system)
                    if unique_filenames:
                        final_answer += "\n\nSources:\n" + "\n".join(unique_filenames)
                        print(f" Added sources to answer text: {unique_filenames}")
                    
                    print(f" Returning {len(sources_to_return)} sources: {sources_to_return}")

                # Run cross-validator (result used by API layer if needed)
                try:
                    _ = cross_validate_answer_llm(question, snippets, final_answer)
                except Exception:
                    pass
                
                print(f" RAG search completed. Answer length: {len(final_answer)}")
                return final_answer, sources_to_return
                
        except Exception as e:
            print(f"RAG error: {e}")
            return f"RAG error: {str(e)}", []

    async def handle_greeting(self, args: Dict[str, Any]) -> str:
       
        message = args["message"]
        print(f" MCP Greeting: {message}")
        
        # Use your existing LLM classification for greetings
        try:
            from llm import classify_message_llm
            classification = classify_message_llm(message)
            if classification.get("intent") == "greeting_only":
                reply = classification.get("reply", "Hello! How can I help you today?")
                return reply
            else:
                # Fallback to simple greeting
                return "Hello! I'm here to help. You can ask me questions about medical data or search through documents. What would you like to know?"
        except Exception as e:
            print(f" Greeting LLM error: {e}")
            return "Hello! I'm here to help. You can ask me questions about medical data or search through documents. What would you like to know?"

    async def run(self):
        
        async with stdio_server() as (read, write):
            await self.server.run(
                read, write,
                InitializationOptions(
                    server_name="chatbot-rag-pure",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities()
                )
            )

async def main():
    server = PureChatBotMCPServer()
    await server.run()

# Standalone functions for main.py compatibility
def create_pure_mcp_server():
    
    return PureChatBotMCPServer()

async def ask_pure_mcp(mcp_server, question: str, org_id: str, user_id: str) -> Dict[str, Any]:
    
    try:
        # Use the LLM to choose the right tool
        model = get_gemini()
        
        tool_choice_prompt = f"""
You are a helpful assistant that chooses the right tool to answer user questions.

Available tools:
1. sql_query - For structured database queries (counts, lists, specific records)
2. rag_search - For general knowledge questions that need document search
3. greeting - For simple greetings and small talk

Question: "{question}"

Choose the most appropriate tool and provide the arguments in JSON format.

Rules:
- If the question asks for counts, lists, specific records, or structured data → use sql_query
- If the question asks for general knowledge, explanations, or document content → use rag_search  
- If it's just a greeting or small talk → use greeting

Return JSON with: {{"tool": "tool_name", "arguments": {{"question": "{question}", "org_id": "{org_id}", "user_id": "{user_id}"}}}}
"""
        
        response = model.generate_content(tool_choice_prompt)
        tool_choice_text = (getattr(response, "text", "") or "").strip()
        
        # Clean up the response
        if tool_choice_text.startswith("```json"):
            tool_choice_text = tool_choice_text.replace("```json", "").replace("```", "").strip()
        elif tool_choice_text.startswith("```"):
            tool_choice_text = tool_choice_text.replace("```", "").strip()
        
        try:
            tool_choice = json.loads(tool_choice_text)
        except json.JSONDecodeError:
            # Fallback to RAG search if parsing fails
            tool_choice = {
                "tool": "rag_search",
                "arguments": {"question": question, "org_id": org_id, "user_id": user_id}
            }
        
        print(f" Gemini tool choice: {tool_choice}")
        
        # Clean the tool choice
        tool_name = tool_choice.get("tool", "rag_search")
        tool_args = tool_choice.get("arguments", {})
        
        # Ensure required arguments
        tool_args["question"] = question
        tool_args["org_id"] = org_id
        tool_args["user_id"] = user_id
        
        print(f"Cleaned tool choice: {{\"tool\": \"{tool_name}\", \"arguments\": {tool_args}}}")
        print(f" Gemini chose tool: {tool_name}")
        print(f" Tool arguments: {tool_args}")
        
        # Execute the chosen tool
        print(f" Executing tool: {tool_name}")
        result, sources = await mcp_server.call_tool(tool_name, tool_args)
        
        # Extract answer from result
        answer_text = ""
        for content in result:
            if hasattr(content, 'text'):
                answer_text += content.text
        
        return {
            "answer": answer_text,
            "sources": sources
        }
        
    except Exception as e:
        logger.error(f"Error in ask_pure_mcp: {e}")
        return {
            "answer": f"I encountered an error: {str(e)}",
            "sources": []
        }

if __name__ == "__main__":
    asyncio.run(main())
