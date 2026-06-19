"""
Petition routes — multi-tier Instructor → Advisor → Chair workflow.

Routes
------
POST  /api/v1/petitions/new                      Any authenticated user (student submits)
GET   /api/v1/faculty/petitions                  Instructor | Advisor | Chair | Admin
POST  /api/v1/faculty/petitions/{id}/action      Instructor | Advisor | Chair | Admin
POST  /api/v1/faculty/petitions/{id}/override    Chair | Admin only
"""

import logging
from typing import Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from .deps import TokenData, call_kw, get_current_token, odoo_session, require_roles
from mq import QUEUE_NOTIFICATION, try_publish

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["petitions"])

FACULTY_ROLES = ("instructor", "academic_advisor", "department_chair", "super_admin")
CHAIR_ROLES   = ("department_chair", "super_admin")


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class NewPetitionRequest(BaseModel):
    petition_type_id: int
    subject:          str = Field(..., min_length=3, max_length=200)
    description:      str = Field(..., min_length=10, max_length=5000)
    course_id:        Optional[int] = None
    requested_date:   Optional[str] = None


class TierActionRequest(BaseModel):
    action: Literal["approve", "reject", "escalate"]
    reason: Optional[str] = Field(default=None, max_length=2000)


class OverrideRequest(BaseModel):
    decision: Literal["approve", "reject"]
    reason:   str = Field(..., min_length=5, max_length=2000)


# ---------------------------------------------------------------------------
# Route 1 — Student (or any role) submits a petition
# ---------------------------------------------------------------------------

@router.post("/petitions/new", summary="Submit a new petition")
async def submit_petition(
    body: NewPetitionRequest,
    token: TokenData = Depends(get_current_token),
):
    """
    Create a ``student.petition`` record on behalf of the calling user.
    The gateway service account runs the create, but student_id is set to the
    caller's ``res.partner`` (fetched by uid from the JWT).
    """
    async with odoo_session() as client:
        # Resolve caller's partner_id
        user_data = await call_kw(
            client, "res.users", "read",
            [[token.user_id], ["partner_id"]],
        )
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found in Odoo")
        partner_id = user_data[0]["partner_id"][0]

        vals: dict = {
            "petition_type_id": body.petition_type_id,
            "subject": body.subject,
            "description": body.description,
            "student_id": partner_id,
        }
        if body.course_id:
            vals["course_id"] = body.course_id
        if body.requested_date:
            vals["requested_date"] = body.requested_date

        # Use sudo-level create via service account (student model restriction
        # is enforced at the portal level; gateway is trusted internal service)
        petition_id = await call_kw(client, "student.petition", "create", [vals])

        # Auto-submit so it enters the workflow immediately
        await call_kw(client, "student.petition", "action_submit", [[petition_id]])

        # Read back reference name
        record = await call_kw(
            client, "student.petition", "read",
            [[petition_id], ["name", "state", "current_tier"]],
        )
        r = record[0] if record else {}
        return {
            "petition_id": petition_id,
            "reference": r.get("name"),
            "state": r.get("state"),
            "current_tier": r.get("current_tier"),
        }


# ---------------------------------------------------------------------------
# Route 2 — Faculty queue (role-scoped)
# ---------------------------------------------------------------------------

_PETITION_FIELDS = [
    "id", "name", "subject", "student_id", "petition_type_id",
    "course_id", "department_id", "current_tier", "state",
    "days_pending", "submitted_date", "is_escalated", "requested_date",
]

def _build_domain(token: TokenData, states: list[str]) -> list:
    """Build an Odoo search domain scoped to the caller's faculty tier."""
    role = token.role
    uid  = token.user_id
    state_filter = [("state", "in", states)]

    if role == "instructor":
        return state_filter + [
            ("current_tier", "=", "instructor"),
            ("course_id.instructor_user_id", "=", uid),
        ]
    if role == "academic_advisor":
        return state_filter + [
            ("current_tier", "=", "advisor"),
            ("student_id.user_ids.advisor_id", "=", uid),
        ]
    if role == "department_chair":
        return state_filter + [
            ("current_tier", "=", "chair"),
            ("department_id.chair_id", "=", uid),
        ]
    # super_admin — no scope restriction
    return state_filter


@router.get("/faculty/petitions", summary="Faculty petition queue (role-filtered)")
async def faculty_petition_queue(
    states: str = Query(default="submitted,under_review",
                        description="Comma-separated state filter"),
    limit: int = Query(default=50, ge=1, le=200),
    token: TokenData = Depends(require_roles(*FACULTY_ROLES)),
):
    state_list = [s.strip() for s in states.split(",") if s.strip()]
    domain = _build_domain(token, state_list)

    async with odoo_session() as client:
        records = await call_kw(
            client, "student.petition", "search_read",
            [domain],
            {"fields": _PETITION_FIELDS, "limit": limit, "order": "submitted_date asc"},
        )

    # Flatten Many2one tuples → {id, name} dicts for JSON serialisation
    def flatten(rec: dict) -> dict:
        for key, val in rec.items():
            if isinstance(val, (list, tuple)) and len(val) == 2 and isinstance(val[0], int):
                rec[key] = {"id": val[0], "name": val[1]}
        return rec

    return {"count": len(records), "petitions": [flatten(r) for r in (records or [])]}


# ---------------------------------------------------------------------------
# Route 3 — Tier action (approve / reject / escalate)
# ---------------------------------------------------------------------------

_ACTION_TO_METHOD = {
    "approve":  "tier_approve",
    "reject":   "tier_reject",
    "escalate": "action_escalate",
}


@router.post(
    "/faculty/petitions/{petition_id}/action",
    summary="Approve, reject, or escalate a petition at the current tier",
)
async def petition_tier_action(
    petition_id: int,
    body: TierActionRequest,
    token: TokenData = Depends(require_roles(*FACULTY_ROLES)),
):
    method = _ACTION_TO_METHOD.get(body.action)
    if not method:
        raise HTTPException(status_code=400, detail=f"Unknown action: {body.action}")

    async with odoo_session() as client:
        await call_kw(
            client, "student.petition", method,
            [[petition_id]],
            {"acting_user_id": token.user_id, "reason": body.reason},
        )
        record = await call_kw(
            client, "student.petition", "read",
            [[petition_id], ["state", "current_tier", "is_escalated"]],
        )
        r = record[0] if record else {}

    await try_publish(QUEUE_NOTIFICATION, {
        "user_id": token.user_id,
        "event": "petition.action_taken",
        "petition_id": petition_id,
        "action": body.action,
        "new_state": r.get("state"),
    })
    return {
        "success": True,
        "petition_id": petition_id,
        "action": body.action,
        "new_state": r.get("state"),
        "current_tier": r.get("current_tier"),
        "is_escalated": r.get("is_escalated"),
    }


# ---------------------------------------------------------------------------
# Route 4 — Chair override (final ruling, bypasses tier sequence)
# ---------------------------------------------------------------------------

@router.post(
    "/faculty/petitions/{petition_id}/override",
    summary="Department Chair override — final ruling regardless of prior decisions",
)
async def petition_chair_override(
    petition_id: int,
    body: OverrideRequest,
    token: TokenData = Depends(require_roles(*CHAIR_ROLES)),
):
    async with odoo_session() as client:
        await call_kw(
            client, "student.petition", "chair_override",
            [[petition_id]],
            {
                "acting_user_id": token.user_id,
                "decision": body.decision,
                "reason": body.reason,
            },
        )
        record = await call_kw(
            client, "student.petition", "read",
            [[petition_id], ["state", "current_tier", "override_reason"]],
        )
        r = record[0] if record else {}

    await try_publish(QUEUE_NOTIFICATION, {
        "user_id": token.user_id,
        "event": "petition.chair_override",
        "petition_id": petition_id,
        "decision": body.decision,
        "final_state": r.get("state"),
    })
    return {
        "success": True,
        "petition_id": petition_id,
        "decision": body.decision,
        "final_state": r.get("state"),
        "override_reason": r.get("override_reason"),
    }
