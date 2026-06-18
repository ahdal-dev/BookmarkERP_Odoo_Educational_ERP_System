"""Academic Agent microservice — the slim, gateway-fronted API surface.

This is the entrypoint used by the integrated deployment. It exposes only:
  - POST /agent/query : run the academic agent for an authenticated student
  - GET  /health      : liveness + best-effort dependency readiness

Authentication is delegated to the FastAPI gateway: the gateway validates the
client JWT and forwards the *trusted* student identity here, guarded by a shared
secret (``X-Chatbot-Secret`` == ``CHATBOT_ADMIN_TOKEN``). The student_email in the
request body is therefore server-supplied and is the data-isolation boundary —
the agent's tools only ever read/write that student's records.

Run: ``uvicorn agent_service:app --app-dir Backend --host 0.0.0.0 --port 8001``
It deliberately does NOT import the legacy RAG/admin app (Whisper, SQLAlchemy,
embeddings), so it stays lightweight and independent.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from typing import List, Optional

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent_openai import run_agent_openai

app = FastAPI(title="Academic Agent Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

CHATBOT_ADMIN_TOKEN = os.getenv("CHATBOT_ADMIN_TOKEN", "")


class HistoryItem(BaseModel):
    role: str           # "user" | "assistant"
    content: str


class AgentQuery(BaseModel):
    question: str
    student_email: Optional[str] = None  # trusted, supplied by the gateway
    history: Optional[List[HistoryItem]] = None


def _require_secret(provided: Optional[str]) -> None:
    if not CHATBOT_ADMIN_TOKEN:
        raise HTTPException(status_code=503, detail="Service not configured (missing shared secret)")
    if provided != CHATBOT_ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid or missing X-Chatbot-Secret")


@app.get("/health")
def health():
    """Liveness + best-effort dependency checks (never fails on dependency outage)."""
    deps = {}
    try:
        from odoo_client import _get_uid
        deps["odoo"] = bool(_get_uid())
    except Exception:  # noqa: BLE001
        deps["odoo"] = False
    try:
        from mq import connect, mq_enabled
        if mq_enabled():
            conn = connect()
            conn.close()
            deps["rabbitmq"] = True
        else:
            deps["rabbitmq"] = "disabled"
    except Exception:  # noqa: BLE001
        deps["rabbitmq"] = False
    return {"status": "ok", "service": "academic-agent", "dependencies": deps}


@app.post("/agent/query")
def agent_query(body: AgentQuery, x_chatbot_secret: Optional[str] = Header(default=None)):
    _require_secret(x_chatbot_secret)

    if not (body.question or "").strip():
        raise HTTPException(status_code=400, detail="question is required")

    history = [(h.role, h.content) for h in (body.history or [])]
    result = run_agent_openai(
        question=body.question,
        student_email=body.student_email,
        chat_history=history,
    )
    return result
