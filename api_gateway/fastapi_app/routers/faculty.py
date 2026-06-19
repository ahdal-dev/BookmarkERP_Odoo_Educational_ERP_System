"""
Faculty dashboard data — assigned courses, enrollment, class rosters.

Routes
------
GET  /api/v1/faculty/courses              Instructor | Advisor | Chair | Admin
GET  /api/v1/faculty/dashboard            Instructor | Advisor | Chair | Admin
GET  /api/v1/faculty/courses/{id}/roster  Instructor | Advisor | Chair | Admin
"""

import logging

from fastapi import APIRouter, Depends

from .deps import TokenData, call_kw, odoo_session, require_roles
from .petitions import FACULTY_ROLES, _build_domain

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["faculty"])

_COURSE_FIELDS = ["name", "code", "total_seats", "available_seats", "schedule"]


def _with_enrolled(course: dict) -> dict:
    enrolled = (course.get("total_seats") or 0) - (course.get("available_seats") or 0)
    return {**course, "enrolled": max(0, enrolled), "capacity": course.get("total_seats") or 0}


async def _fetch_courses(client, uid: int) -> list:
    courses = await call_kw(
        client, "education.course", "search_read",
        [[["instructor_user_id", "=", uid]]],
        {"fields": _COURSE_FIELDS, "order": "code"},
    )
    return [_with_enrolled(c) for c in courses]


@router.get("/faculty/courses", summary="Courses assigned to the calling instructor")
async def faculty_courses(token: TokenData = Depends(require_roles(*FACULTY_ROLES))):
    async with odoo_session() as client:
        courses = await _fetch_courses(client, token.user_id)
    return {"count": len(courses), "courses": courses}


@router.get("/faculty/dashboard", summary="Faculty dashboard aggregates")
async def faculty_dashboard(token: TokenData = Depends(require_roles(*FACULTY_ROLES))):
    async with odoo_session() as client:
        courses = await _fetch_courses(client, token.user_id)
        pending = await call_kw(
            client, "student.petition", "search_count",
            [_build_domain(token, ["submitted", "under_review"])],
        )
    total_students = sum(c["enrolled"] for c in courses)
    return {
        "courses": courses,
        "total_students": total_students,
        "assigned_courses": len(courses),
        "pending_petitions": pending,
    }


@router.get("/faculty/courses/{course_id}/roster", summary="Enrolled students for a course")
async def course_roster(course_id: int, token: TokenData = Depends(require_roles(*FACULTY_ROLES))):
    async with odoo_session() as client:
        course = await call_kw(
            client, "education.course", "read",
            [[course_id], ["name", "code", "total_seats", "available_seats"]],
        )
        roster = await call_kw(
            client, "education.registration", "search_read",
            [[["course_id", "=", course_id], ["state", "=", "enrolled"]]],
            {"fields": ["student_name", "registration_date", "state"], "order": "student_name"},
        )
    return {
        "course": _with_enrolled(course[0]) if course else None,
        "roster": roster or [],
    }
