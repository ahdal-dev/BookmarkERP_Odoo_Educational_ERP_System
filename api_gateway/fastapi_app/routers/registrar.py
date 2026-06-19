"""
Registrar dashboard aggregates — derived entirely from live Odoo records.

Routes
------
GET  /api/v1/registrar/dashboard   Registrar | Super Admin
"""

import logging

from fastapi import APIRouter, Depends

from .deps import TokenData, call_kw, odoo_session, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["registrar"])


def _fmt_window(course: dict) -> str:
    start = course.get("registration_start") or "—"
    end = course.get("registration_end") or "—"
    return f"{start} → {end}"


@router.get("/registrar/dashboard", summary="Live registrar dashboard aggregates")
async def registrar_dashboard(
    token: TokenData = Depends(require_roles("registrar", "super_admin")),
):
    """Aggregate enrollment, seat, and activity metrics from
    education.registration / education.course. Cards without a backing model
    (e.g. concurrent users, registration tiers) are intentionally omitted."""
    async with odoo_session() as client:
        total_enrolled = await call_kw(
            client, "education.registration", "search_count",
            [[["state", "=", "enrolled"]]],
        )
        waitlisted = await call_kw(
            client, "education.registration", "search_count",
            [[["state", "=", "waitlist"]]],
        )
        open_courses = await call_kw(
            client, "education.course", "search_count",
            [[["registration_open", "=", True]]],
        )

        # Seat capacity across all courses (computed available_seats is reliable).
        courses = await call_kw(
            client, "education.course", "search_read",
            [[]],
            {"fields": ["name", "total_seats", "available_seats",
                        "registration_open", "registration_start", "registration_end"]},
        )

        # Recent enrollment activity → event feed.
        recent = await call_kw(
            client, "education.registration", "search_read",
            [[]],
            {"fields": ["student_name", "course_code", "state", "registration_date"],
             "order": "registration_date desc", "limit": 12},
        )

    total_seats = sum((c.get("total_seats") or 0) for c in courses)
    open_seats = sum((c.get("available_seats") or 0) for c in courses if c.get("registration_open"))
    utilization = round((total_enrolled / total_seats) * 100) if total_seats else 0

    windows = [
        {
            "name": c.get("name"),
            "window": _fmt_window(c),
            "status": "Open" if c.get("registration_open") else "Upcoming",
            "available_seats": c.get("available_seats") or 0,
        }
        for c in courses if c.get("registration_open")
    ][:8]

    events = []
    for r in recent:
        verb = {"enrolled": "enrolled in", "dropped": "dropped", "waitlist": "joined waitlist for"}.get(
            r.get("state"), "updated")
        who = r.get("student_name") or "A student"
        what = r.get("course_code") or "a course"
        events.append({"text": f"{who} {verb} {what}", "at": r.get("registration_date")})

    return {
        "stats": {
            "total_enrolled": total_enrolled,
            "open_seats": open_seats,
            "open_courses": open_courses,
            "waitlisted": waitlisted,
        },
        "capacity_utilization": utilization,
        "windows": windows,
        "recent_activity": events,
    }
