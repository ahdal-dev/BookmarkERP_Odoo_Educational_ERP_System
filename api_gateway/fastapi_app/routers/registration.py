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
    "prerequisite_course_ids",
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
        # Resolve prerequisite ids → {id, code} in one extra read.
        prereq_ids = sorted({pid for c in courses for pid in (c.get("prerequisite_course_ids") or [])})
        names = {}
        if prereq_ids:
            rows = await call_kw(
                client, "education.course", "read", [prereq_ids, ["code", "name"]],
            )
            names = {r["id"]: (r.get("code") or r.get("name")) for r in rows}
        for c in courses:
            c["prerequisites"] = [
                {"id": pid, "code": names.get(pid, str(pid))}
                for pid in (c.get("prerequisite_course_ids") or [])
            ]
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

        # Academic standing + active petitions (petition.student_id is res.partner).
        user = await call_kw(
            client, "res.users", "read",
            [[token.user_id], ["partner_id", "cumulative_gpa", "academic_standing", "class_year"]],
        )
        u = user[0] if user else {}
        partner_id = u["partner_id"][0] if u.get("partner_id") else None
        active_petitions = 0
        if partner_id:
            active_petitions = await call_kw(
                client, "student.petition", "search_count",
                [[["student_id", "=", partner_id],
                  ["state", "in", ["submitted", "under_review"]]]],
            )

    total_credits = sum((c.get("credits") or 0) for c in courses)
    has_grades = u.get("academic_standing") not in (False, "new", None)
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
        "gpa": u.get("cumulative_gpa") if has_grades else None,
        "registered_credits": total_credits,
        "registered_courses": len(courses),
        "active_petitions": active_petitions,
        "schedule": schedule,
    }


_STANDING_LABELS = {
    "new": "New", "deans_list": "Dean's List", "good": "Good Standing",
    "probation": "Academic Probation",
}
_CLASS_LABELS = {
    "freshman": "Freshman", "sophomore": "Sophomore",
    "junior": "Junior", "senior": "Senior",
}


@router.get("/student/grades", summary="Authenticated student's grades + GPA by term")
async def student_grades(
    token: TokenData = Depends(require_roles("student", "super_admin")),
):
    async with odoo_session() as client:
        user = await call_kw(
            client, "res.users", "read",
            [[token.user_id], ["cumulative_gpa", "earned_credits", "academic_standing", "class_year"]],
        )
        u = user[0] if user else {}

        regs = await call_kw(
            client, "education.registration", "search_read",
            [[["student_id", "=", token.user_id], ["is_graded", "=", True]]],
            {"fields": ["course_id", "course_code", "course_name", "grade", "grade_points"]},
        )
        course_ids = [r["course_id"][0] for r in regs if r.get("course_id")]
        courses = {}
        if course_ids:
            crows = await call_kw(
                client, "education.course", "search_read",
                [[["id", "in", course_ids]]],
                {"fields": ["credits", "semester", "year"]},
            )
            courses = {c["id"]: c for c in crows}

    # Group graded registrations into terms.
    terms = {}
    for r in regs:
        cid = r["course_id"][0] if r.get("course_id") else None
        c = courses.get(cid, {})
        credits = c.get("credits") or 0
        sem = (c.get("semester") or "").title() or "Other"
        year = c.get("year") or ""
        term_key = f"{sem} {year}".strip()
        bucket = terms.setdefault(term_key, {"term": term_key, "courses": [], "_qp": 0.0, "_cr": 0})
        bucket["courses"].append({
            "code": r.get("course_code"),
            "name": r.get("course_name"),
            "credits": credits,
            "grade": r.get("grade"),
            "status": "Completed",
        })
        bucket["_qp"] += (r.get("grade_points") or 0) * credits
        bucket["_cr"] += credits

    term_list = []
    for t in terms.values():
        gpa = round(t["_qp"] / t["_cr"], 2) if t["_cr"] else 0.0
        term_list.append({
            "term": t["term"], "credits": t["_cr"], "gpa": gpa, "courses": t["courses"],
        })

    return {
        "cumulative_gpa": u.get("cumulative_gpa") or 0.0,
        "earned_credits": u.get("earned_credits") or 0,
        "academic_standing": _STANDING_LABELS.get(u.get("academic_standing"), "New"),
        "class_year": _CLASS_LABELS.get(u.get("class_year"), "Freshman"),
        "terms": term_list,
    }
