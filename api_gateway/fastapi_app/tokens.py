"""Shared JWT issuance/decoding so login (main.py) and the MFA router produce
identical, compatible tokens. All claims and the signing secret are read from
the same environment the rest of the gateway uses."""
import os
import uuid
from datetime import datetime, timedelta

import jwt

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or ""
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "1"))
JWT_REFRESH_EXPIRATION_DAYS = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))


def make_access_refresh(uid: int, login: str, email: str, role: str) -> dict:
    """Issue an access token + refresh token (mirrors the original login flow)."""
    now = datetime.utcnow()
    access_payload = {
        "user_id": uid, "username": login, "email": email,
        "role": role, "jti": str(uuid.uuid4()), "type": "access",
        "exp": now + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    refresh_payload = {
        "user_id": uid, "username": login, "email": email,
        "role": role, "jti": str(uuid.uuid4()), "type": "refresh",
        "exp": now + timedelta(days=JWT_REFRESH_EXPIRATION_DAYS),
    }
    return {
        "access_token": jwt.encode(access_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM),
        "refresh_token": jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM),
        "token_type": "bearer",
        "expires_in": JWT_EXPIRATION_HOURS * 3600,
    }


def make_short_token(uid: int, login: str, email: str, role: str,
                     ttype: str, minutes: int = 5) -> str:
    """Issue a short-lived, single-purpose token (``mfa`` / ``mfa_setup`` /
    ``pwreset``). Not accepted by normal protected routes."""
    payload = {
        "user_id": uid, "username": login, "email": email, "role": role,
        "jti": str(uuid.uuid4()), "type": ttype,
        "exp": datetime.utcnow() + timedelta(minutes=minutes),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode(token: str) -> dict:
    """Decode + verify a token. Raises jwt exceptions on failure."""
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


async def track_active_session(redis_conn, uid: int, access_token: str) -> None:
    """Record an active session keyed by the access token's jti (best-effort)."""
    if not redis_conn:
        return
    try:
        payload = decode(access_token)
        jti = payload.get("jti")
        if jti:
            await redis_conn.setex(
                f"active_session:{uid}:{jti}", JWT_EXPIRATION_HOURS * 3600, "1")
    except Exception:
        pass
