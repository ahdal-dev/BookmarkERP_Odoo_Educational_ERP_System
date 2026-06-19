"""
Admin / officer data — admissions pipeline, user directory, registration
rules, petition tracking, and live admin dashboard endpoints.

Routes
------
GET    /api/v1/admin/admissions/pipeline           Admission Officer | Admin
PATCH  /api/v1/admin/admissions/{id}/stage         Admission Officer | Admin
GET    /api/v1/admin/users                         Super Admin
POST   /api/v1/admin/users                         Super Admin
GET    /api/v1/admin/users/{uid}                   Super Admin
GET    /api/v1/admin/settings/registration-rules   Registrar | Admin
PUT    /api/v1/admin/settings/registration-rules   Registrar | Admin
GET    /api/v1/admin/petitions                     Super Admin
GET    /api/v1/admin/petitions/{id}                Super Admin
GET    /api/v1/admin/stats                         Super Admin
GET    /api/v1/admin/analytics                     Super Admin
GET    /api/v1/admin/roles-summary                 Super Admin
GET    /api/v1/admin/health                        Super Admin
GET    /api/v1/admin/ai/services                   Super Admin
GET    /api/v1/admin/system/feature-flags          Super Admin
PATCH  /api/v1/admin/system/feature-flags/{key}   Super Admin
GET    /api/v1/admin/knowledge-base/documents      Super Admin
"""

import json
import logging
import os
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .deps import TokenData, call_kw, odoo_session, require_roles, resolve_roles_bulk
from mq import QUEUE_ADMISSION_EMAIL, QUEUE_NOTIFICATION, try_publish

OCR_URL     = os.getenv("OCR_SERVICE_URL", "http://ocr-service:8001")
CHATBOT_URL = os.getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:8002")

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


@router.get("/admin/users/{uid}", summary="Single user detail")
async def get_user(uid: int, token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        users = await call_kw(
            client, "res.users", "read",
            [[uid]],
            {"fields": ["name", "login", "email", "active", "group_ids", "create_date", "write_date"]},
        )
        if not users:
            raise HTTPException(status_code=404, detail="User not found")
        u = users[0]
        roles = await resolve_roles_bulk(client, [u])
    return {
        "id": u["id"],
        "name": u.get("name"),
        "email": u.get("email") or u.get("login"),
        "role": roles.get(u["id"], "staff"),
        "status": "Active" if u.get("active") else "Inactive",
        "createdAt": str(u.get("create_date", ""))[:10],
        "lastLogin": str(u.get("write_date", ""))[:10],
    }


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


# ---------------------------------------------------------------------------
# Admin Dashboard KPIs
# ---------------------------------------------------------------------------

@router.get("/admin/stats", summary="Admin dashboard KPIs")
async def admin_stats(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        total_users = await call_kw(client, "res.users", "search_count", [[]])
        active_users = await call_kw(client, "res.users", "search_count", [[["active", "=", True]]])
        try:
            total_apps   = await call_kw(client, "school.admission", "search_count", [[]])
            admitted     = await call_kw(client, "school.admission", "search_count", [[["state", "=", "accepted"]]])
            in_review    = await call_kw(client, "school.admission", "search_count", [[["state", "=", "under_review"]]])
            missing_docs = await call_kw(client, "school.admission", "search_count", [[["state", "=", "submitted"]]])
        except Exception:
            total_apps = admitted = in_review = missing_docs = 0
        try:
            pending_petitions = await call_kw(
                client, "student.petition", "search_count",
                [[["state", "not in", ["approved", "rejected"]]]],
            )
        except Exception:
            pending_petitions = 0
    return {
        "totalUsers": total_users,
        "activeUsers": active_users,
        "totalApplications": total_apps,
        "admittedApplications": admitted,
        "inReviewApplications": in_review,
        "missingDocs": missing_docs,
        "pendingPetitions": pending_petitions,
        "systemUptime": 99.8,
    }


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@router.get("/admin/analytics", summary="User growth and admission counts over time")
async def admin_analytics(period: str = "monthly", token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        user_groups = await call_kw(
            client, "res.users", "read_group",
            [[], ["id:count"], ["create_date:month"]],
            {"limit": 12, "orderby": "create_date asc"},
        )
        try:
            adm_groups = await call_kw(
                client, "school.admission", "read_group",
                [[], ["id:count"], ["application_date:month"]],
                {"limit": 12, "orderby": "application_date asc"},
            )
        except Exception:
            adm_groups = []

    def _label(g: dict) -> str:
        raw = g.get("create_date:month") or g.get("application_date:month") or ""
        return str(raw)[:7] if raw else "Unknown"

    user_data = [{"month": _label(g), "users": g.get("id_count", 0)} for g in user_groups]
    adm_map   = {str(g.get("application_date:month", ""))[:7]: g.get("id_count", 0) for g in adm_groups}

    merged = [{"month": d["month"], "users": d["users"], "applications": adm_map.get(d["month"], 0)}
              for d in user_data]

    return {"period": period, "data": merged}


# ---------------------------------------------------------------------------
# Roles summary
# ---------------------------------------------------------------------------

@router.get("/admin/roles-summary", summary="Roles with user counts")
async def admin_roles_summary(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        users = await call_kw(
            client, "res.users", "search_read",
            [[]],
            {"fields": ["id", "group_ids"], "limit": 1000},
        )
        role_map = await resolve_roles_bulk(client, users)

    counts: dict[str, int] = Counter(role_map.values())
    ROLE_META = {
        "super_admin":        {"label": "Super Admin",        "color": "#e53935"},
        "registrar":          {"label": "Registrar",          "color": "#8e24aa"},
        "admission_officer":  {"label": "Admission Officer",  "color": "#1e88e5"},
        "instructor":         {"label": "Instructor",         "color": "#43a047"},
        "academic_advisor":   {"label": "Academic Advisor",   "color": "#fb8c00"},
        "department_chair":   {"label": "Department Chair",   "color": "#6d4c41"},
        "support_technician": {"label": "Support Technician", "color": "#00897b"},
        "student":            {"label": "Student",            "color": "#757575"},
        "staff":              {"label": "Staff",              "color": "#546e7a"},
    }
    roles = [
        {"id": slug, "label": meta["label"], "color": meta["color"], "userCount": counts.get(slug, 0)}
        for slug, meta in ROLE_META.items()
    ]
    return {"roles": roles, "total": len(users)}


# ---------------------------------------------------------------------------
# System health
# ---------------------------------------------------------------------------

async def _ping(url: str, name: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{url}/health")
        status = "Healthy" if r.status_code < 300 else "Degraded"
        latency = int(r.elapsed.total_seconds() * 1000) if hasattr(r, "elapsed") and r.elapsed else 0
    except Exception:
        status, latency = "Offline", 0
    return {"name": name, "status": status, "latency": latency}


@router.get("/admin/health", summary="Service health status")
async def admin_health(token: TokenData = Depends(require_roles("super_admin"))):
    import asyncio
    odoo_url = os.getenv("ODOO_URL", "http://host.docker.internal:8081")
    results = await asyncio.gather(
        _ping(odoo_url, "Odoo Backend"),
        _ping(OCR_URL, "OCR Service"),
        _ping(CHATBOT_URL, "Chatbot Service"),
    )
    overall = "Healthy" if all(s["status"] == "Healthy" for s in results) else "Degraded"
    return {"overall": overall, "services": list(results)}


# ---------------------------------------------------------------------------
# AI services status
# ---------------------------------------------------------------------------

@router.get("/admin/ai/services", summary="AI service status")
async def admin_ai_services(token: TokenData = Depends(require_roles("super_admin"))):
    import asyncio
    results = await asyncio.gather(
        _ping(OCR_URL, "OCR Service"),
        _ping(CHATBOT_URL, "Chatbot / RAG Service"),
    )
    return {"services": list(results)}


# ---------------------------------------------------------------------------
# Feature flags (ir.config_parameter)
# ---------------------------------------------------------------------------

_FLAG_PREFIX = "edu.feature."

class FeatureFlagPatch(BaseModel):
    enabled: bool


@router.get("/admin/system/feature-flags", summary="List feature flags")
async def list_feature_flags(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        params = await call_kw(
            client, "ir.config_parameter", "search_read",
            [[["key", "like", _FLAG_PREFIX]]],
            {"fields": ["key", "value"]},
        )
    flags = [
        {
            "key": p["key"].removeprefix(_FLAG_PREFIX),
            "label": p["key"].removeprefix(_FLAG_PREFIX).replace("_", " ").replace(".", " ").title(),
            "enabled": str(p.get("value", "0")).lower() in ("1", "true", "yes"),
        }
        for p in params
    ]
    return {"flags": flags}


@router.patch("/admin/system/feature-flags/{key}", summary="Toggle a feature flag")
async def patch_feature_flag(
    key: str,
    body: FeatureFlagPatch,
    token: TokenData = Depends(require_roles("super_admin")),
):
    full_key = f"{_FLAG_PREFIX}{key}"
    async with odoo_session() as client:
        await call_kw(
            client, "ir.config_parameter", "set_param",
            [full_key, "1" if body.enabled else "0"],
        )
    return {"ok": True, "key": key, "enabled": body.enabled}


# ---------------------------------------------------------------------------
# Knowledge base documents (chatbot.rag.document)
# ---------------------------------------------------------------------------

@router.get("/admin/knowledge-base/documents", summary="List RAG knowledge-base documents")
async def list_kb_documents(token: TokenData = Depends(require_roles("super_admin"))):
    async with odoo_session() as client:
        try:
            docs = await call_kw(
                client, "chatbot.rag.document", "search_read",
                [[]],
                {"fields": ["id", "name", "doc_type", "state", "create_date", "write_date"],
                 "order": "write_date desc", "limit": 200},
            )
        except Exception:
            docs = []
    return {
        "count": len(docs),
        "documents": [
            {
                "id": d["id"],
                "title": d.get("name") or f"Document {d['id']}",
                "type": d.get("doc_type") or "Document",
                "status": (d.get("state") or "indexed").capitalize(),
                "lastUpdated": str(d.get("write_date", ""))[:10],
                "uploadedAt": str(d.get("create_date", ""))[:10],
            }
            for d in docs
        ],
    }


# ---------------------------------------------------------------------------
# Password change (admin self-service)
# ---------------------------------------------------------------------------

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)


@router.post("/admin/change-password", summary="Admin change own password")
async def admin_change_password(
    body: PasswordChangeRequest,
    token: TokenData = Depends(require_roles("super_admin")),
):
    async with odoo_session() as client:
        try:
            await call_kw(
                client, "res.users", "change_password",
                [body.current_password, body.new_password],
            )
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True}
