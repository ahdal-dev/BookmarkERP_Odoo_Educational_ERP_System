"""
In-app notifications feed — backed by the edu.notification Odoo model.

Routes
------
GET    /api/v1/notifications            Any authenticated user (own feed)
PATCH  /api/v1/notifications/{id}/read  Mark one as read
POST   /api/v1/notifications/read-all   Mark all as read
"""

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse

from .deps import TokenData, call_kw, get_current_token, get_current_token_from_string, odoo_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["notifications"])

_FIELDS = ["id", "category", "title", "message", "is_read", "action_url", "create_date"]


def _shape(rec: dict) -> dict:
    """Map Odoo record → the frontend notification shape."""
    return {
        "id": rec["id"],
        "category": rec.get("category") or "other",
        "title": rec.get("title") or "",
        "message": rec.get("message") or "",
        "read": bool(rec.get("is_read")),
        "link": rec.get("action_url") or None,
        "timestamp": rec.get("create_date"),
    }


@router.get("/notifications", summary="List the authenticated user's notifications")
async def list_notifications(token: TokenData = Depends(get_current_token)):
    async with odoo_session() as client:
        records = await call_kw(
            client, "edu.notification", "search_read",
            [[["user_id", "=", token.user_id]]],
            {"fields": _FIELDS, "order": "create_date desc", "limit": 100},
        )
    return [_shape(r) for r in records]


@router.patch("/notifications/{notif_id}/read", summary="Mark a notification as read")
async def mark_read(notif_id: int, token: TokenData = Depends(get_current_token)):
    async with odoo_session() as client:
        owned = await call_kw(
            client, "edu.notification", "search_count",
            [[["id", "=", notif_id], ["user_id", "=", token.user_id]]],
        )
        if not owned:
            raise HTTPException(status_code=404, detail="Notification not found")
        await call_kw(
            client, "edu.notification", "write",
            [[notif_id], {"is_read": True}],
        )
    return {"ok": True}


@router.post("/notifications/read-all", summary="Mark all notifications as read")
async def mark_all_read(token: TokenData = Depends(get_current_token)):
    async with odoo_session() as client:
        ids = await call_kw(
            client, "edu.notification", "search",
            [[["user_id", "=", token.user_id], ["is_read", "=", False]]],
        )
        if ids:
            await call_kw(client, "edu.notification", "write", [ids, {"is_read": True}])
    return {"ok": True, "updated": len(ids) if ids else 0}


@router.get("/notifications/stream", summary="Server-Sent Events stream for real-time notification delivery")
async def notifications_stream(request: Request, token: str = Query(...)):
    """EventSource endpoint. JWT passed as ?token= query param because the browser
    EventSource API does not support custom request headers."""
    td = get_current_token_from_string(token)
    user_id = td.user_id

    queue: asyncio.Queue = asyncio.Queue(maxsize=50)
    sse_qs: dict = getattr(request.app.state, "sse_queues", {})
    sse_qs.setdefault(user_id, []).append(queue)

    async def event_generator():
        try:
            yield "event: connected\ndata: {}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield f"event: notification\ndata: {json.dumps(payload)}\n\n"
                except asyncio.TimeoutError:
                    # Keepalive comment — prevents proxies from closing idle connections
                    yield ": keepalive\n\n"
        finally:
            try:
                sse_qs[user_id].remove(queue)
                if not sse_qs[user_id]:
                    del sse_qs[user_id]
            except (ValueError, KeyError):
                pass

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # prevents nginx from buffering the SSE stream
            "Connection": "keep-alive",
        },
    )
