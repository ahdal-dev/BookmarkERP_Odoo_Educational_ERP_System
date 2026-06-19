"""
Registrar dashboard aggregates — derived entirely from live Odoo records.

Routes
------
GET  /api/v1/registrar/dashboard   Registrar | Super Admin
"""

import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from .deps import TokenData, call_kw, odoo_session, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["registrar"])


async def _count_active_users(redis_conn) -> int | None:
    """Distinct uids with a live session key (active_session:{uid}:{jti})."""
    if not redis_conn:
        return None
    try:
        uids = set()
        async for key in redis_conn.scan_iter(match="active_session:*"):
            k = key.decode() if isinstance(key, (bytes, bytearray)) else key
            parts = k.split(":")
            if len(parts) >= 2:
                uids.add(parts[1])
        return len(uids)
    except Exception:
        return None


def _fmt_window(course: dict) -> str:
    start = course.get("registration_start") or "—"
    end = course.get("registration_end") or "—"
    return f"{start} → {end}"


@router.get("/registrar/dashboard", summary="Live registrar dashboard aggregates")
async def registrar_dashboard(
    request: Request,
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

    active_users = await _count_active_users(getattr(request.app.state, "redis", None))

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
            "active_concurrent_users": active_users,
        },
        "capacity_utilization": utilization,
        "windows": windows,
        "recent_activity": events,
    }


class PrerequisiteUpdate(BaseModel):
    prerequisite_ids: list[int]


@router.patch("/registrar/courses/{course_id}/prerequisites", summary="Set a course's prerequisites")
async def set_course_prerequisites(
    course_id: int,
    body: PrerequisiteUpdate,
    token: TokenData = Depends(require_roles("registrar", "super_admin")),
):
    async with odoo_session() as client:
        await call_kw(
            client, "education.course", "write",
            [[course_id], {"prerequisite_course_ids": [(6, 0, body.prerequisite_ids)]}],
        )
    return {"ok": True, "course_id": course_id, "prerequisite_ids": body.prerequisite_ids}
