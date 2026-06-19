"""
Support tickets + live-chat threads.

Routes
------
GET    /api/v1/support/tickets              All authenticated (own; staff see all)
POST   /api/v1/support/tickets              All authenticated (create)
GET    /api/v1/support/tickets/{id}         All authenticated (own or staff)
POST   /api/v1/support/tickets/{id}/messages
PATCH  /api/v1/support/tickets/{id}         Support | Admin (status/assign/priority)
"""

import logging
import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from .deps import TokenData, call_kw, get_current_token, odoo_session, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["support"])

STAFF_ROLES = ("support_technician", "super_admin")
_FIELDS = ["name", "subject", "description", "category", "priority", "state",
           "channel", "user_id", "assigned_to", "create_date"]


class NewTicket(BaseModel):
    subject: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = ""
    category: str = "other"
    priority: str = "medium"
    channel: str = "ticket"


class TicketMessage(BaseModel):
    body: str = Field(..., min_length=1, max_length=4000)


class TicketUpdate(BaseModel):
    state: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[int] = None


def _shape(rec: dict) -> dict:
    def m2o(v):
        return {"id": v[0], "name": v[1]} if isinstance(v, (list, tuple)) and len(v) == 2 else None
    return {
        "id": rec["id"],
        "ref": rec.get("name"),
        "subject": rec.get("subject"),
        "description": rec.get("description") or "",
        "category": rec.get("category"),
        "priority": rec.get("priority"),
        "state": rec.get("state"),
        "channel": rec.get("channel"),
        "requester": m2o(rec.get("user_id")),
        "assigned_to": m2o(rec.get("assigned_to")),
        "created": rec.get("create_date"),
    }


@router.get("/support/tickets", summary="List support tickets")
async def list_tickets(token: TokenData = Depends(get_current_token)):
    staff = token.role in STAFF_ROLES
    domain = [] if staff else [["user_id", "=", token.user_id]]
    async with odoo_session() as client:
        rows = await call_kw(
            client, "support.ticket", "search_read",
            [domain], {"fields": _FIELDS, "order": "create_date desc", "limit": 200},
        )
    return {"count": len(rows), "tickets": [_shape(r) for r in rows]}


@router.post("/support/tickets", summary="Create a support ticket")
async def create_ticket(body: NewTicket, token: TokenData = Depends(get_current_token)):
    async with odoo_session() as client:
        tid = await call_kw(client, "support.ticket", "create", [{
            "subject": body.subject,
            "description": body.description,
            "category": body.category,
            "priority": body.priority,
            "channel": body.channel,
            "user_id": token.user_id,
        }])
    return {"ok": True, "id": tid}


@router.get("/support/tickets/{ticket_id}", summary="Ticket detail + conversation")
async def ticket_detail(ticket_id: int, token: TokenData = Depends(get_current_token)):
    async with odoo_session() as client:
        rows = await call_kw(client, "support.ticket", "read", [[ticket_id], _FIELDS])
        if not rows:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if token.role not in STAFF_ROLES and rows[0].get("user_id", [None])[0] != token.user_id:
            raise HTTPException(status_code=403, detail="Not your ticket")
        msgs = await call_kw(
            client, "mail.message", "search_read",
            [[["model", "=", "support.ticket"], ["res_id", "=", ticket_id],
              ["message_type", "!=", "notification"]]],
            {"fields": ["body", "author_id", "date"], "order": "date asc"},
        )
    messages = [{
        "body": re.sub(r"<[^>]+>", "", m.get("body") or "").strip(),
        "author": m["author_id"][1] if m.get("author_id") else "System",
        "date": m.get("date"),
    } for m in (msgs or [])]
    return {"ticket": _shape(rows[0]), "messages": messages}


@router.post("/support/tickets/{ticket_id}/messages", summary="Post a message to a ticket")
async def post_message(ticket_id: int, body: TicketMessage, token: TokenData = Depends(get_current_token)):
    async with odoo_session() as client:
        await call_kw(client, "support.ticket", "post_message", [[ticket_id], body.body])
    return {"ok": True}


@router.patch("/support/tickets/{ticket_id}", summary="Update a ticket (staff)")
async def update_ticket(ticket_id: int, body: TicketUpdate, token: TokenData = Depends(require_roles(*STAFF_ROLES))):
    vals = {}
    if body.state is not None:
        vals["state"] = body.state
    if body.priority is not None:
        vals["priority"] = body.priority
    if body.assigned_to is not None:
        vals["assigned_to"] = body.assigned_to
    if not vals:
        return {"ok": True, "updated": []}
    async with odoo_session() as client:
        await call_kw(client, "support.ticket", "write", [[ticket_id], vals])
    return {"ok": True, "updated": list(vals.keys())}
