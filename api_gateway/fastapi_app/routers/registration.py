"""
Registration catalog + student dashboard data.

Routes
------
GET  /api/v1/registration/courses   Any authenticated user (course catalog)
GET  /api/v1/student/dashboard      Student | Super Admin (own summary)
"""

import logging

from fastapi import APIRouter, Depends

from .deps import TokenData, call_kw, get_current_token, odoo_session, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["registration"])

_COURSE_FIELDS = [
    "name", "code", "available_seats", "total_seats", "schedule",
    "timing_start", "timing_end", "credits", "instructor", "registration_open",
]


@router.get("/registration/courses", summary="Course catalog")
async def list_courses(
    open_only: bool = False,
    token: TokenData = Depends(get_current_token),
):
    domain = [["registration_open", "=", True]] if open_only else []
    async with odoo_session() as client:
        courses = await call_kw(
            client, "education.course", "search_read",
            [domain],
            {"fields": _COURSE_FIELDS, "order": "code"},
        )
    return {"count": len(courses), "courses": courses}


@router.get("/student/dashboard", summary="Authenticated student's dashboard summary")
async def student_dashboard(
    token: TokenData = Depends(require_roles("student", "super_admin")),
):
    """Registered credits, active-petition count, and enrolled course list,
    all scoped to the caller. GPA has no Odoo model yet → returned as null."""
    async with odoo_session() as client:
        # Enrolled registrations for this user (student_id is res.users).
        regs = await call_kw(
            client, "education.registration", "search_read",
            [[["student_id", "=", token.user_id], ["state", "=", "enrolled"]]],
            {"fields": ["course_id", "course_code", "course_name", "course_schedule"]},
        )
        course_ids = [r["course_id"][0] for r in regs if r.get("course_id")]

        courses = []
        if course_ids:
            courses = await call_kw(
                client, "education.course", "search_read",
                [[["id", "in", course_ids]]],
                {"fields": ["code", "name", "credits", "schedule", "timing_start", "timing_end", "instructor"]},
            )

        # Active petitions — petition.student_id is res.partner; resolve partner.
        user = await call_kw(client, "res.users", "read", [[token.user_id], ["partner_id"]])
        partner_id = user[0]["partner_id"][0] if user and user[0].get("partner_id") else None
        active_petitions = 0
        if partner_id:
            active_petitions = await call_kw(
                client, "student.petition", "search_count",
                [[["student_id", "=", partner_id],
                  ["state", "in", ["submitted", "under_review"]]]],
            )

    total_credits = sum((c.get("credits") or 0) for c in courses)
    schedule = [
        {
            "code": c.get("code"),
            "name": c.get("name"),
            "schedule": c.get("schedule"),
            "timing_start": c.get("timing_start"),
            "timing_end": c.get("timing_end"),
            "instructor": c.get("instructor"),
        }
        for c in courses
    ]

    return {
        "gpa": None,  # no GPA model yet
        "registered_credits": total_credits,
        "registered_courses": len(courses),
        "active_petitions": active_petitions,
        "schedule": schedule,
    }
