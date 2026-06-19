"""
Account self-service routes.

Routes
------
POST  /api/v1/auth/change-password   Any authenticated user (changes own password)
"""

import logging

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

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
    new_password:     str = Field(..., min_length=8, max_length=128)


@router.post("/auth/change-password", summary="Change the authenticated user's password")
async def change_password(
    body: ChangePasswordRequest,
    token: TokenData = Depends(get_current_token),
):
    """Verify the caller's current password by re-authenticating as them, then
    write the new password using the gateway service account."""
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

    # 2. Write the new password as the service account.
    async with odoo_session() as client:
        await call_kw(
            client, "res.users", "write",
            [[token.user_id], {"password": body.new_password}],
        )

    logger.info("Password changed for uid=%s", token.user_id)
    return {"success": True, "message": "Password updated successfully"}
