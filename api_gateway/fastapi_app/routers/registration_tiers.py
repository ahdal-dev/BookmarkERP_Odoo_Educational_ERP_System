"""
Registration tiers / windows — seniority-based registration windows backed by
the education.registration.tier model.

Routes
------
GET  /api/v1/registration/tiers             Any authenticated user
GET  /api/v1/student/registration-window    Student | Super Admin (own eligibility)
"""

import logging

from fastapi import APIRouter, Depends

from .deps import TokenData, call_kw, get_current_token, odoo_session, require_roles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["registration-tiers"])

_TIER_FIELDS = ["name", "sequence", "color", "min_credits", "max_credits",
                "registration_start", "registration_end"]


def _credit_range(t: dict) -> str:
    lo = t.get("min_credits") or 0
    hi = t.get("max_credits") or 0
    return f"{lo}+ credits" if not hi else f"{lo}–{hi} credits"


async def _fetch_tiers(client):
    tiers = await call_kw(
        client, "education.registration.tier", "search_read",
        [[]], {"fields": _TIER_FIELDS, "order": "sequence"},
    )
    # is_open_now() needs a record; compute via a single read of ids is overkill —
    # derive open state from dates in Python (today within window).
    from datetime import date
    today = date.today().isoformat()
    for t in tiers:
        start = t.get("registration_start")
        end = t.get("registration_end")
        t["open_now"] = (not start or start <= today) and (not end or today <= end)
        t["credit_range"] = _credit_range(t)
    return tiers


@router.get("/registration/tiers", summary="Registration tiers / windows")
async def list_tiers(token: TokenData = Depends(get_current_token)):
    async with odoo_session() as client:
        tiers = await _fetch_tiers(client)
    return {"count": len(tiers), "tiers": tiers}


@router.get("/student/registration-window", summary="Caller's eligible registration tier")
async def my_window(token: TokenData = Depends(require_roles("student", "super_admin"))):
    async with odoo_session() as client:
        user = await call_kw(
            client, "res.users", "read",
            [[token.user_id], ["earned_credits", "class_year"]],
        )
        earned = (user[0].get("earned_credits") if user else 0) or 0
        tiers = await _fetch_tiers(client)

    eligible = next(
        (t for t in tiers
         if earned >= (t.get("min_credits") or 0)
         and (not t.get("max_credits") or earned <= t["max_credits"])),
        None,
    )
    return {
        "earned_credits": earned,
        "class_year": user[0].get("class_year") if user else None,
        "tier": eligible,
        "is_open": bool(eligible and eligible.get("open_now")),
    }
