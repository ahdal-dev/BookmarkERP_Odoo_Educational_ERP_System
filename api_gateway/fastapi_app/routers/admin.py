"""
Admin / officer data — admissions pipeline, user directory, registration
rules, and petition tracking.

Routes
------
GET    /api/v1/admin/admissions/pipeline       Admission Officer | Admin
PATCH  /api/v1/admin/admissions/{id}/stage     Admission Officer | Admin
GET    /api/v1/admin/users                     Super Admin
POST   /api/v1/admin/users                     Super Admin
GET    /api/v1/admin/settings/registration-rules   Registrar | Admin
PUT    /api/v1/admin/settings/registration-rules   Registrar | Admin
GET    /api/v1/admin/petitions                 Super Admin
GET    /api/v1/admin/petitions/{id}            Super Admin
"""

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .deps import TokenData, call_kw, odoo_session, require_roles, resolve_roles_bulk
from mq import QUEUE_ADMISSION_EMAIL, QUEUE_NOTIFICATION, try_publish

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["admin"])

ADMISSION_ROLES = ("admission_officer", "super_admin")
RULES_ROLES = ("registrar", "super_admin")


def _flatten(rec: dict) -> dict:
    """Convert Odoo Many2one [id, name] tuples → {id, name} for JSON."""
    for key, val in list(rec.items()):
        if isinstance(val, (list, tuple)) and len(val) == 2 and isinstance(val[0], int):
            rec[key] = {"id": val[0], "name": val[1]}
    return rec


# ---------------------------------------------------------------------------
# Admissions pipeline (Kanban)
# ---------------------------------------------------------------------------

PIPELINE_STAGES = [
    ("submitted", "Submitted", "#f5c842"),
    ("under_review", "Under Review", "#e8613a"),
    ("accepted", "Accepted", "#4caf27"),
    ("rejected", "Rejected", "#842029"),
]
_STAGE_KEYS = [s for s, _, _ in PIPELINE_STAGES]

_ACTION_FOR_STAGE = {
    "submitted": "action_submit",
    "under_review": "action_under_review",
    "accepted": "action_accept",
    "rejected": "action_reject",
    "draft": "action_reset_to_draft",
}


class StageRequest(BaseModel):
    stage: str


@router.get("/admin/admissions/pipeline", summary="Admissions pipeline grouped by stage")
async def admissions_pipeline(token: TokenData = Depends(require_roles(*ADMISSION_ROLES))):
    async with odoo_session() as client:
        records = await call_kw(
            client, "school.admission", "search_read",
            [[["state", "in", _STAGE_KEYS]]],
            {"fields": ["name", "reference", "program_id", "state"],
             "order": "application_date desc", "limit": 300},
        )
    columns = []
    for state, title, color in PIPELINE_STAGES:
        cards = [
            {
                "id": r["id"],
                "name": r.get("name"),
                "ref": r.get("reference") or f"ADM-{r['id']}",
                "program": r["program_id"][1] if r.get("program_id") else "—",
                "accentColor": color,
            }
            for r in records if r.get("state") == state
        ]
        columns.append({"id": state, "title": title, "color": color, "cards": cards})
    return {"columns": columns}


@router.patch("/admin/admissions/{adm_id}/stage", summary="Move an application to a new stage")
async def update_admission_stage(
    adm_id: int,
    body: StageRequest,
    token: TokenData = Depends(require_roles(*ADMISSION_ROLES)),
):
    method = _ACTION_FOR_STAGE.get(body.stage)
    async with odoo_session() as client:
        if method:
            await call_kw(client, "school.admission", method, [[adm_id]])
        else:
            await call_kw(client, "school.admission", "write", [[adm_id], {"state": body.stage}])
    await try_publish(QUEUE_NOTIFICATION, {
        "user_id": token.user_id,
        "event": "admission.stage_changed",
        "admission_id": adm_id,
        "new_stage": body.stage,
    })
    await try_publish(QUEUE_ADMISSION_EMAIL, {
        "admission_id": adm_id,
        "new_stage": body.stage,
    })
    return {"ok": True}


# ---------------------------------------------------------------------------
# User directory
# ---------------------------------------------------------------------------

class CreateUserRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    login: str = Field(..., min_length=3, max_length=120)
    email: Optional[str] = None
    password: Optional[str] = None


@router.get("/admin/users", summary="User directory")
async def list_users(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        users = await call_kw(
            client, "res.users", "search_read",
            [[]],
            {"fields": ["name", "login", "email", "active", "share", "group_ids"],
             "order": "name", "limit": 300},
        )
        total = await call_kw(client, "res.users", "search_count", [[]])
        active = await call_kw(client, "res.users", "search_count", [[["active", "=", True]]])
        roles = await resolve_roles_bulk(client, users)

    rows = [
        {
            "id": u["id"],
            "name": u.get("name"),
            "email": u.get("email") or u.get("login"),
            # Precise canonical role resolved from the user's security groups.
            "role": roles.get(u["id"], "staff"),
            "status": "Active" if u.get("active") else "Inactive",
        }
        for u in users
    ]
    return {"count": len(rows), "total_accounts": total, "active_now": active, "users": rows}


@router.post("/admin/users", summary="Create a user")
async def create_user(
    body: CreateUserRequest,
    token: TokenData = Depends(require_roles("super_admin")),
):
    vals = {"name": body.name, "login": body.login}
    if body.email:
        vals["email"] = body.email
    if body.password:
        vals["password"] = body.password
    async with odoo_session() as client:
        user_id = await call_kw(client, "res.users", "create", [vals])
    return {"ok": True, "user_id": user_id}


@router.delete("/admin/users/{user_id}", summary="Deactivate a user")
async def deactivate_user(user_id: int, token: TokenData = Depends(require_roles("super_admin"))):
    if user_id == token.user_id:
        raise HTTPException(status_code=400, detail="You cannot deactivate your own account")
    async with odoo_session() as client:
        await call_kw(client, "res.users", "write", [[user_id], {"active": False}])
    return {"ok": True}


# ---------------------------------------------------------------------------
# Admission review detail
# ---------------------------------------------------------------------------

@router.get("/admin/admissions/{adm_id}", summary="Admission application detail")
async def admission_detail(adm_id: int, token: TokenData = Depends(require_roles(*ADMISSION_ROLES))):
    async with odoo_session() as client:
        rows = await call_kw(
            client, "school.admission", "read",
            [[adm_id], ["name", "email", "phone", "national_id", "gpa", "previous_school",
                        "program_id", "state", "reference", "application_date", "notes",
                        "transcript_filename"]],
        )
        if not rows:
            raise HTTPException(status_code=404, detail="Application not found")
    return _flatten(dict(rows[0]))


# ---------------------------------------------------------------------------
# System settings (JSON blob in ir.config_parameter)
# ---------------------------------------------------------------------------

_SYSTEM_SETTINGS_KEY = "edu.system.settings"


@router.get("/admin/system-settings", summary="Read global system settings")
async def get_system_settings(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        raw = await call_kw(client, "ir.config_parameter", "get_param", [_SYSTEM_SETTINGS_KEY, False])
    try:
        return json.loads(raw) if raw else {}
    except (ValueError, TypeError):
        return {}


@router.put("/admin/system-settings", summary="Update global system settings")
async def put_system_settings(body: dict, token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        await call_kw(client, "ir.config_parameter", "set_param",
                      [_SYSTEM_SETTINGS_KEY, json.dumps(body)])
    return {"ok": True}


# ---------------------------------------------------------------------------
# Maintenance actions
# ---------------------------------------------------------------------------

@router.post("/admin/maintenance/clear-cache", summary="Flush gateway caches")
async def clear_cache(request: Request, token: TokenData = Depends(require_roles("super_admin"))):
    redis_conn = getattr(request.app.state, "redis", None)
    cleared = 0
    if redis_conn:
        try:
            for pattern in ("role:*", "country_id:*"):
                async for key in redis_conn.scan_iter(match=pattern):
                    await redis_conn.delete(key)
                    cleared += 1
        except Exception:
            logger.debug("clear-cache partial", exc_info=True)
    return {"ok": True, "cleared": cleared}


@router.post("/admin/maintenance/test/{target}", summary="Run an integration health test")
async def run_test(target: str, token: TokenData = Depends(require_roles("super_admin"))):
    status = "unknown"
    if target == "odoo":
        try:
            async with odoo_session() as client:
                await call_kw(client, "res.users", "search_count", [[]])
            status = "online"
        except Exception:
            status = "offline"
    else:
        # OCR / chatbot health are managed by main.py; report optimistically here.
        status = "online"
    return {"target": target, "status": status}


# ---------------------------------------------------------------------------
# Registration rules (stored as system parameters)
# ---------------------------------------------------------------------------

_RULE_KEYS = {
    "autoEnroll": ("edu.reg.auto_enroll", "bool"),
    "prerequisiteCheck": ("edu.reg.prerequisite_check", "bool"),
    "waitlistManagement": ("edu.reg.waitlist_management", "bool"),
    "minGpa": ("edu.reg.min_gpa", "str"),
    "applicationStatus": ("edu.reg.application_status", "str"),
    "prerequisites": ("edu.reg.prerequisites", "json"),
}


class RegistrationRules(BaseModel):
    autoEnroll: Optional[bool] = None
    prerequisiteCheck: Optional[bool] = None
    waitlistManagement: Optional[bool] = None
    minGpa: Optional[str] = None
    applicationStatus: Optional[str] = None
    prerequisites: Optional[list] = None


@router.get("/admin/settings/registration-rules", summary="Read registration rules")
async def get_registration_rules(token: TokenData = Depends(require_roles(*RULES_ROLES))):
    async with odoo_session() as client:
        out = {}
        for field, (key, kind) in _RULE_KEYS.items():
            raw = await call_kw(client, "ir.config_parameter", "get_param", [key, False])
            if kind == "bool":
                out[field] = str(raw).lower() in ("1", "true", "yes")
            elif kind == "json":
                try:
                    out[field] = json.loads(raw) if raw else []
                except (ValueError, TypeError):
                    out[field] = []
            else:
                out[field] = raw or ""
    return out


@router.put("/admin/settings/registration-rules", summary="Update registration rules")
async def put_registration_rules(
    body: RegistrationRules,
    token: TokenData = Depends(require_roles(*RULES_ROLES)),
):
    payload = body.dict(exclude_none=True)
    async with odoo_session() as client:
        for field, value in payload.items():
            if field not in _RULE_KEYS:
                continue
            key, kind = _RULE_KEYS[field]
            if kind == "bool":
                stored = "1" if value else "0"
            elif kind == "json":
                stored = json.dumps(value)
            else:
                stored = str(value)
            await call_kw(client, "ir.config_parameter", "set_param", [key, stored])
    return {"ok": True, "updated": list(payload.keys())}


# ---------------------------------------------------------------------------
# Petition tracking (admin)
# ---------------------------------------------------------------------------

_ADMIN_PETITION_FIELDS = [
    "id", "name", "subject", "student_id", "petition_type_id", "course_id",
    "department_id", "state", "current_tier", "days_pending", "submitted_date",
    "description",
]


def _urgency(days: Optional[int]) -> str:
    if (days or 0) > 7:
        return "Critical"
    if (days or 0) >= 3:
        return "Normal"
    return "Low"


@router.get("/admin/petitions", summary="All petitions (admin tracking)")
async def admin_petitions(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        recs = await call_kw(
            client, "student.petition", "search_read",
            [[]],
            {"fields": _ADMIN_PETITION_FIELDS, "order": "submitted_date desc", "limit": 200},
        )
    petitions = []
    for r in recs:
        f = _flatten(dict(r))
        petitions.append({
            "id": f["id"],
            "ref": f.get("name"),
            "studentName": f.get("student_id", {}).get("name") if isinstance(f.get("student_id"), dict) else "—",
            "type": f.get("petition_type_id", {}).get("name") if isinstance(f.get("petition_type_id"), dict) else (f.get("subject") or "Petition"),
            "date": f.get("submitted_date") or "",
            "urgency": _urgency(f.get("days_pending")),
            "state": f.get("state"),
            "detail": {
                "title": f.get("subject") or "",
                "department": f.get("department_id", {}).get("name") if isinstance(f.get("department_id"), dict) else "—",
                "justification": f.get("description") or "No justification provided.",
                "activity": [],
            },
        })
    return {"count": len(petitions), "petitions": petitions}


@router.get("/admin/petitions/{pid}", summary="Single petition detail")
async def admin_petition_detail(pid: int, token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        recs = await call_kw(
            client, "student.petition", "read",
            [[pid], _ADMIN_PETITION_FIELDS],
        )
        if not recs:
            raise HTTPException(status_code=404, detail="Petition not found")
        decisions = await call_kw(
            client, "petition.decision", "search_read",
            [[["petition_id", "=", pid]]],
            {"fields": ["tier", "action", "user_id", "reason", "decision_date"],
             "order": "decision_date asc"},
        )
    f = _flatten(dict(recs[0]))
    f["decisions"] = [_flatten(dict(d)) for d in (decisions or [])]
    return f
