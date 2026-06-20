"""
Account self-service routes.

Routes
------
POST  /api/v1/auth/change-password   Any authenticated user (changes own password)

Enforces the password policy (length + character classes, no name/email reuse,
no reuse of the last 5 passwords) and stamps password_changed_at for expiry.
Also accepts a short-lived ``pwreset`` token from the login expiry flow.
"""
import logging
from datetime import datetime

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from password_policy import (
    append_history,
    matches_any_history,
    parse_history,
    validate_password_strength,
)
from .deps import (
    ODOO_DB,
    ODOO_URL,
    TokenData,
    call_kw,
    get_current_token,
    odoo_session,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["account"])


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    new_password:     str = Field(..., min_length=1, max_length=128)


@router.post("/auth/change-password", summary="Change the authenticated user's password")
async def change_password(
    body: ChangePasswordRequest,
    token: TokenData = Depends(get_current_token),
):
    """Verify the caller's current password by re-authenticating as them, enforce
    the password policy, then write the new password using the service account."""
    if body.new_password == body.current_password:
        raise HTTPException(status_code=400, detail="New password must differ from the current one")

    # 1. Verify the current password (throwaway session — login is token.username).
    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            verify = await c.post(
                f"{ODOO_URL}/web/session/authenticate",
                json={"jsonrpc": "2.0", "params": {
                    "db": ODOO_DB, "login": token.username, "password": body.current_password,
                }},
            )
        if not verify.json().get("result", {}).get("uid"):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
    except HTTPException:
        raise
    except Exception:
        logger.error("change_password verify step failed", exc_info=True)
        raise HTTPException(status_code=502, detail="Could not verify current password")

    # 2. Policy enforcement + history-aware write (all as the service account).
    async with odoo_session() as client:
        rows = await call_kw(
            client, "res.users", "read",
            [[token.user_id], ["name", "login", "email", "password_history"]],
        )
        user = rows[0] if rows else {}
        identity_email = user.get("email") or user.get("login") or token.username

        ok, errors = validate_password_strength(
            body.new_password, user.get("name", ""), identity_email)
        if not ok:
            raise HTTPException(status_code=400, detail="; ".join(errors))

        history = parse_history(user.get("password_history"))
        if matches_any_history(body.new_password, history):
            raise HTTPException(status_code=400,
                                detail="Password must not match any of your last 5 passwords")

        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        await call_kw(
            client, "res.users", "write",
            [[token.user_id], {
                "password": body.new_password,
                "password_history": append_history(body.new_password, history),
                "password_changed_at": now,
            }],
        )

    logger.info("Password changed for uid=%s", token.user_id)
    return {"success": True, "message": "Password updated successfully"}
