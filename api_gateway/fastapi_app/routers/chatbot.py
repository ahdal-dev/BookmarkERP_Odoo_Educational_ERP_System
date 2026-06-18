"""
Chatbot router — proxies authenticated chat requests to the Academic Agent
microservice.

The gateway is the auth authority: it validates the client JWT, derives the
student's identity from the verified token (never from client input), and
forwards it to the agent service guarded by a shared secret. This is the data
isolation boundary — the agent's tools only ever act on this student's records.
"""

import logging
import os
from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from .deps import TokenData, call_kw, get_current_token, odoo_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["chatbot"])

RAG_CHATBOT_URL = os.getenv("RAG_CHATBOT_URL", "http://academic-agent:8001").rstrip("/")
CHATBOT_SHARED_SECRET = os.getenv("CHATBOT_SHARED_SECRET", "")
CHATBOT_TIMEOUT = float(os.getenv("CHATBOT_TIMEOUT", "60"))


class ChatHistoryItem(BaseModel):
    role: str = Field(..., description='"user" or "assistant"')
    content: str


class ChatQueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    history: Optional[List[ChatHistoryItem]] = None


class ChatQueryResponse(BaseModel):
    answer: str
    tool_used: Optional[str] = None
    tool_ok: Optional[bool] = None
    queued: Optional[bool] = None


async def _resolve_student_email(token: TokenData) -> str:
    """Trusted student email from the verified JWT, falling back to an Odoo lookup."""
    if token.email:
        return token.email
    async with odoo_session() as client:
        rows = await call_kw(client, "res.users", "read", [[token.user_id], ["login", "email"]])
    if rows:
        return rows[0].get("email") or rows[0].get("login") or ""
    return ""


@router.post("/chatbot/query", response_model=ChatQueryResponse,
             summary="Ask the Academic Agent a question")
async def chatbot_query(
    body: ChatQueryRequest,
    token: TokenData = Depends(get_current_token),
):
    if not CHATBOT_SHARED_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Chatbot integration is not configured (missing shared secret).",
        )

    student_email = await _resolve_student_email(token)

    payload = {
        "question": body.question,
        "student_email": student_email,
        "history": [h.model_dump() for h in (body.history or [])],
    }

    try:
        async with httpx.AsyncClient(timeout=CHATBOT_TIMEOUT) as client:
            resp = await client.post(
                f"{RAG_CHATBOT_URL}/agent/query",
                json=payload,
                headers={"X-Chatbot-Secret": CHATBOT_SHARED_SECRET},
            )
    except httpx.RequestError as e:
        logger.error("Academic Agent unreachable: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The assistant service is currently unavailable. Please try again shortly.",
        )

    if resp.status_code >= 400:
        logger.error("Academic Agent error %s: %s", resp.status_code, resp.text[:500])
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The assistant service returned an error.",
        )

    return resp.json()
