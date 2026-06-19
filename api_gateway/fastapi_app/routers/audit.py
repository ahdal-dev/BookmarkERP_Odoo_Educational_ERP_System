"""
Audit log — persisted security events.

Routes
------
GET  /api/v1/admin/audit-log    Super Admin
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Query

from .deps import TokenData, call_kw, odoo_session, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["audit"])

_FIELDS = ["event_type", "severity", "user_id", "actor_login", "ip", "detail", "create_date"]


@router.get("/admin/audit-log", summary="Paginated audit events")
async def audit_log(
    severity: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    token: TokenData = Depends(require_roles("super_admin")),
):
    domain = [["severity", "=", severity]] if severity else []
    async with odoo_session() as client:
        rows = await call_kw(
            client, "audit.log", "search_read",
            [domain],
            {"fields": _FIELDS, "order": "create_date desc", "limit": limit, "offset": offset},
        )
        total = await call_kw(client, "audit.log", "search_count", [domain])
    events = [{
        "event_type": r.get("event_type"),
        "severity": r.get("severity"),
        "actor": r["user_id"][1] if r.get("user_id") else (r.get("actor_login") or "—"),
        "ip": r.get("ip") or "",
        "detail": r.get("detail") or "",
        "date": r.get("create_date"),
    } for r in (rows or [])]
    return {"count": len(events), "total": total, "events": events}


async def record_audit_event(event_type, severity="info", user_id=None,
                             actor_login=None, ip=None, detail=None):
    """Best-effort write of an audit event to Odoo. Never raises."""
    try:
        async with odoo_session() as client:
            await call_kw(client, "audit.log", "log_event", [], {
                "event_type": event_type,
                "severity": severity,
                "user_id": user_id or False,
                "actor_login": actor_login or "",
                "ip": ip or "",
                "detail": detail or "",
            })
    except Exception:
        logger.debug("audit write skipped", exc_info=True)
