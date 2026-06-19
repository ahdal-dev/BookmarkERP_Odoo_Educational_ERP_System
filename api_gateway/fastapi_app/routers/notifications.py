"""
In-app notifications feed — backed by the edu.notification Odoo model.

Routes
------
GET    /api/v1/notifications            Any authenticated user (own feed)
PATCH  /api/v1/notifications/{id}/read  Mark one as read
POST   /api/v1/notifications/read-all   Mark all as read
"""

import logging

from fastapi import APIRouter, Depends, HTTPException

from .deps import TokenData, call_kw, get_current_token, odoo_session

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
