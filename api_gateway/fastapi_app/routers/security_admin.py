"""Admin endpoints for data-retention policies and service-account rotation.

Routes
------
GET    /api/v1/admin/data-retention          Super Admin
POST   /api/v1/admin/data-retention          Super Admin
PUT    /api/v1/admin/data-retention/{id}     Super Admin
DELETE /api/v1/admin/data-retention/{id}     Super Admin
POST   /api/v1/admin/data-retention/run      Super Admin  (manual cron trigger)

GET    /api/v1/admin/service-accounts        Super Admin
POST   /api/v1/admin/service-accounts        Super Admin  (returns key once)
POST   /api/v1/admin/service-accounts/{id}/rotate  Super Admin  (returns key once)
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

import crypto_utils
from .deps import TokenData, call_kw, odoo_session, require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/admin", tags=["security-admin"])

_POLICY_FIELDS = ["name", "record_type", "retention_days", "action", "active",
                  "last_run", "last_purged_count"]
_SA_FIELDS = ["name", "description", "api_key_hint", "last_rotated",
              "rotation_interval_days", "active"]


# ---------------------------------------------------------------------------
# Data retention
# ---------------------------------------------------------------------------
class PolicyBody(BaseModel):
    name: str
    record_type: str = Field(..., pattern="^(student_record|admission|petition|support_ticket|audit_log)$")
    retention_days: int = Field(..., ge=1)
    action: str = Field(..., pattern="^(archive|anonymize|delete)$")
    active: bool = True


class PolicyPatch(BaseModel):
    name: Optional[str] = None
    record_type: Optional[str] = None
    retention_days: Optional[int] = Field(None, ge=1)
    action: Optional[str] = None
    active: Optional[bool] = None


@router.get("/data-retention", summary="List data-retention policies")
async def list_policies(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        rows = await call_kw(client, "data.retention.policy", "search_read",
                             [[]], {"fields": _POLICY_FIELDS, "order": "record_type"})
    return {"policies": rows or []}


@router.post("/data-retention", summary="Create a retention policy")
async def create_policy(body: PolicyBody,
                        token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        pid = await call_kw(client, "data.retention.policy", "create", [body.model_dump()])
    return {"ok": True, "id": pid}


@router.put("/data-retention/{policy_id}", summary="Update a retention policy")
async def update_policy(policy_id: int, body: PolicyPatch,
                        token: TokenData = Depends(require_roles("super_admin"))):
    vals = {k: v for k, v in body.model_dump().items() if v is not None}
    if not vals:
        raise HTTPException(status_code=400, detail="No fields to update")
    async with odoo_session() as client:
        await call_kw(client, "data.retention.policy", "write", [[policy_id], vals])
    return {"ok": True}


@router.delete("/data-retention/{policy_id}", summary="Delete a retention policy")
async def delete_policy(policy_id: int,
                        token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        await call_kw(client, "data.retention.policy", "unlink", [[policy_id]])
    return {"ok": True}


@router.post("/data-retention/run", summary="Run all retention policies now")
async def run_retention(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        total = await call_kw(client, "data.retention.policy", "run_retention", [])
    logger.info("Manual retention run by %s purged %s records", token.username, total)
    return {"ok": True, "purged": total}


# ---------------------------------------------------------------------------
# Service accounts
# ---------------------------------------------------------------------------
class ServiceAccountBody(BaseModel):
    name: str
    description: Optional[str] = ""
    rotation_interval_days: int = Field(30, ge=1)


def _sa_status(row: dict) -> str:
    last = row.get("last_rotated")
    interval = row.get("rotation_interval_days") or 30
    if not last:
        return "due"
    try:
        last_dt = datetime.strptime(last, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return "ok"
    return "due" if datetime.utcnow() >= last_dt + timedelta(days=interval) else "ok"


@router.get("/service-accounts", summary="List service accounts")
async def list_service_accounts(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        rows = await call_kw(client, "service.account", "search_read",
                             [[]], {"fields": _SA_FIELDS, "order": "name"})
    for r in rows or []:
        r["status"] = _sa_status(r)
    return {"service_accounts": rows or []}


@router.post("/service-accounts", summary="Create a service account (reveals key once)")
async def create_service_account(body: ServiceAccountBody,
                                 token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        sa_id = await call_kw(client, "service.account", "create", [{
            "name": body.name,
            "description": body.description or "",
            "rotation_interval_days": body.rotation_interval_days,
        }])
        rows = await call_kw(client, "service.account", "read",
                             [[sa_id], ["api_key", "api_key_hint"]])
    enc = (rows[0] if rows else {}).get("api_key") or ""
    plaintext = crypto_utils.field_decrypt(enc) if crypto_utils.field_key_available() else ""
    return {"ok": True, "id": sa_id, "api_key": plaintext,
            "api_key_hint": (rows[0] if rows else {}).get("api_key_hint")}


@router.post("/service-accounts/{sa_id}/rotate", summary="Rotate a service account key")
async def rotate_service_account(sa_id: int,
                                 token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        plaintext = await call_kw(client, "service.account", "rotate_key", [[sa_id]])
    try:
        from routers import audit as audit_router
        await audit_router.record_audit_event(
            "service_account_rotation", "warning", user_id=token.user_id,
            actor_login=token.username, detail=f"manual rotate id={sa_id}")
    except Exception:
        pass
    return {"ok": True, "api_key": plaintext}
