"""
Advisor & department-chair data.

Routes
------
GET  /api/v1/faculty/advisees                 Advisor | Chair | Admin
GET  /api/v1/faculty/advisees/{user_id}       Advisor | Chair | Admin
GET  /api/v1/faculty/department/students      Chair | Admin
"""

import logging
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException

from .deps import TokenData, call_kw, odoo_session, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["advising"])

ADVISOR_ROLES = ("academic_advisor", "department_chair", "super_admin")
CHAIR_ROLES = ("department_chair", "super_admin")

_STUDENT_FIELDS = ["name", "email", "login", "partner_id", "cumulative_gpa",
                   "academic_standing", "class_year", "earned_credits", "is_on_hold"]


def _student_row(r: dict, active_petitions: int = 0) -> dict:
    return {
        "id": r["id"],
        "name": r.get("name"),
        "email": r.get("email") or r.get("login"),
        "gpa": r.get("cumulative_gpa") or 0.0,
        "standing": r.get("academic_standing") or "new",
        "class_year": r.get("class_year") or "freshman",
        "earned_credits": r.get("earned_credits") or 0,
        "on_hold": bool(r.get("is_on_hold")),
        "active_petitions": active_petitions,
    }


@router.get("/faculty/advisees", summary="Advisees assigned to the calling advisor")
async def advisees(token: TokenData = Depends(require_roles(*ADVISOR_ROLES))):
    async with odoo_session() as client:
        me = await call_kw(client, "res.users", "read", [[token.user_id], ["advisee_ids"]])
        ids = (me[0].get("advisee_ids") if me else []) or []
        if not ids:
            return {"count": 0, "advisees": []}
        rows = await call_kw(client, "res.users", "read", [ids, _STUDENT_FIELDS])
        partners = [r["partner_id"][0] for r in rows if r.get("partner_id")]
        counts = Counter()
        if partners:
            pet = await call_kw(
                client, "student.petition", "search_read",
                [[["student_id", "in", partners], ["state", "in", ["submitted", "under_review"]]]],
                {"fields": ["student_id"]},
            )
            counts = Counter(p["student_id"][0] for p in pet if p.get("student_id"))
    advisees_out = [
        _student_row(r, counts.get(r["partner_id"][0], 0) if r.get("partner_id") else 0)
        for r in rows
    ]
    return {"count": len(advisees_out), "advisees": advisees_out}


@router.get("/faculty/advisees/{user_id}", summary="Advisee profile detail")
async def advisee_profile(user_id: int, token: TokenData = Depends(require_roles(*ADVISOR_ROLES))):
    async with odoo_session() as client:
        rows = await call_kw(client, "res.users", "read", [[user_id], _STUDENT_FIELDS])
        if not rows:
            raise HTTPException(status_code=404, detail="Advisee not found")
        r = rows[0]
        # Graded transcript rows
        regs = await call_kw(
            client, "education.registration", "search_read",
            [[["student_id", "=", user_id], ["is_graded", "=", True]]],
            {"fields": ["course_code", "course_name", "grade"]},
        )
        petitions = []
        partner_id = r["partner_id"][0] if r.get("partner_id") else None
        if partner_id:
            petitions = await call_kw(
                client, "student.petition", "search_read",
                [[["student_id", "=", partner_id]]],
                {"fields": ["name", "subject", "state", "submitted_date"],
                 "order": "submitted_date desc", "limit": 20},
            )
    return {
        "profile": _student_row(r, len([p for p in petitions if p.get("state") in ("submitted", "under_review")])),
        "transcript": regs or [],
        "petitions": petitions or [],
    }


@router.get("/faculty/department/students", summary="Students in the chair's department")
async def department_students(token: TokenData = Depends(require_roles(*CHAIR_ROLES))):
    async with odoo_session() as client:
        depts = await call_kw(
            client, "education.department", "search_read",
            [[["chair_id", "=", token.user_id]]],
            {"fields": ["name", "course_ids"]},
        )
        course_ids = [c for d in depts for c in (d.get("course_ids") or [])]
        students = []
        if course_ids:
            regs = await call_kw(
                client, "education.registration", "search_read",
                [[["course_id", "in", course_ids], ["state", "=", "enrolled"]]],
                {"fields": ["student_id"]},
            )
            uids = sorted({r["student_id"][0] for r in regs if r.get("student_id")})
            if uids:
                rows = await call_kw(client, "res.users", "read", [uids, _STUDENT_FIELDS])
                students = [_student_row(r) for r in rows]
    return {
        "departments": [d.get("name") for d in depts],
        "count": len(students),
        "students": students,
    }
