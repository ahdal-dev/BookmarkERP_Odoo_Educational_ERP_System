"""TOTP Multi-Factor Authentication (RFC 6238).

Enrolment + challenge endpoints. TOTP verification happens here in the gateway;
Odoo only persists the encrypted secret / hashed backup codes (edu_mang_security).

Routes
------
POST /api/v1/auth/mfa/setup          access OR mfa_setup token  -> secret + QR
POST /api/v1/auth/mfa/verify-setup   access OR mfa_setup token  -> enable + backup codes
POST /api/v1/auth/mfa/verify         public (mfa_token + code)  -> full JWTs
POST /api/v1/auth/mfa/disable        access token + password+code
GET  /api/v1/auth/mfa/status         access token
"""
import base64
import hashlib
import io
import json
import logging
import secrets

import httpx
import pyotp
import qrcode
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field

import tokens
import crypto_utils
from .deps import ODOO_DB, ODOO_URL, TokenData, call_kw, get_current_token, odoo_session

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth/mfa", tags=["mfa"])

_bearer = HTTPBearer()
ENFORCED_MFA_ROLES = {"super_admin", "registrar"}
ISSUER = "Bookmark Academic ERP"


# ---------------------------------------------------------------------------
# Principal resolution — setup endpoints accept a full access token OR a
# short-lived mfa/mfa_setup token (needed for enforced first-login enrolment).
# ---------------------------------------------------------------------------
class Principal:
    def __init__(self, payload: dict):
        self.user_id = payload["user_id"]
        self.username = payload.get("username", "")
        self.email = payload.get("email", self.username)
        self.role = payload.get("role", "student")


def setup_principal(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> Principal:
    try:
        payload = tokens.decode(creds.credentials)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    if payload.get("type") not in ("access", "mfa", "mfa_setup"):
        raise HTTPException(status_code=401, detail="Token not valid for MFA setup")
    return Principal(payload)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def _read_user(client, uid: int, fields: list) -> dict:
    rows = await call_kw(client, "res.users", "read", [[uid], fields])
    return rows[0] if rows else {}


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.strip().upper().encode("utf-8")).hexdigest()


def _gen_backup_codes(n: int = 10) -> list:
    return ["%s-%s" % (secrets.token_hex(2).upper(), secrets.token_hex(2).upper())
            for _ in range(n)]


def _qr_png_base64(uri: str) -> str:
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class CodeBody(BaseModel):
    code: str = Field(..., min_length=4, max_length=20)


class VerifyBody(BaseModel):
    mfa_token: str
    code: str = Field(..., min_length=4, max_length=20)


class DisableBody(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=128)
    code: str = Field(..., min_length=4, max_length=20)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@router.post("/setup", summary="Begin MFA enrolment — returns secret + QR code")
async def mfa_setup(principal: Principal = Depends(setup_principal)):
    if not crypto_utils.field_key_available():
        raise HTTPException(status_code=503, detail="Field encryption key not configured")
    secret = pyotp.random_base32()
    uri = pyotp.TOTP(secret).provisioning_uri(name=principal.username, issuer_name=ISSUER)
    async with odoo_session() as client:
        await call_kw(client, "res.users", "write",
                      [[principal.user_id], {"mfa_secret": crypto_utils.field_encrypt(secret)}])
    return {"otpauth_uri": uri, "qr_png_base64": _qr_png_base64(uri), "secret": secret}


@router.post("/verify-setup", summary="Confirm MFA enrolment — enable + return backup codes")
async def mfa_verify_setup(body: CodeBody, principal: Principal = Depends(setup_principal)):
    async with odoo_session() as client:
        user = await _read_user(client, principal.user_id, ["mfa_secret"])
        secret = crypto_utils.field_decrypt(user.get("mfa_secret") or "")
        if not secret:
            raise HTTPException(status_code=400, detail="Start setup first")
        if not pyotp.TOTP(secret).verify(body.code, valid_window=1):
            raise HTTPException(status_code=400, detail="Invalid verification code")
        plain_codes = _gen_backup_codes()
        hashed = [_hash_code(c) for c in plain_codes]
        await call_kw(client, "res.users", "write", [[principal.user_id], {
            "mfa_enabled": True,
            "mfa_backup_codes": json.dumps(hashed),
        }])
    logger.info("MFA enabled for uid=%s", principal.user_id)
    return {"success": True, "backup_codes": plain_codes}


@router.post("/verify", summary="Complete login MFA challenge — returns full JWTs")
async def mfa_verify(body: VerifyBody, request: Request):
    try:
        payload = tokens.decode(body.mfa_token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired MFA token")
    if payload.get("type") != "mfa":
        raise HTTPException(status_code=401, detail="Not an MFA challenge token")

    uid = payload["user_id"]
    login = payload.get("username", "")
    email = payload.get("email", login)
    role = payload.get("role", "student")

    async with odoo_session() as client:
        user = await _read_user(client, uid, ["mfa_secret", "mfa_backup_codes", "mfa_enabled"])
        secret = crypto_utils.field_decrypt(user.get("mfa_secret") or "")
        ok = bool(secret) and pyotp.TOTP(secret).verify(body.code, valid_window=1)
        if not ok:
            # Try backup codes.
            stored = []
            try:
                stored = json.loads(user.get("mfa_backup_codes") or "[]")
            except (ValueError, TypeError):
                stored = []
            candidate = _hash_code(body.code)
            if candidate in stored:
                stored.remove(candidate)
                await call_kw(client, "res.users", "write",
                              [[uid], {"mfa_backup_codes": json.dumps(stored)}])
                ok = True
        if not ok:
            raise HTTPException(status_code=400, detail="Invalid MFA code")

    issued = tokens.make_access_refresh(uid, login, email, role)
    redis_conn = getattr(request.app.state, "redis", None)
    await tokens.track_active_session(redis_conn, uid, issued["access_token"])
    logger.info("MFA challenge passed for uid=%s", uid)
    try:
        from routers import audit as audit_router
        await audit_router.record_audit_event(
            "mfa_login", "info", user_id=uid, actor_login=login, detail=f"role={role}")
    except Exception:
        pass
    return {**issued, "user_id": uid, "user_name": login, "role": role}


@router.post("/disable", summary="Disable MFA (requires password + valid code)")
async def mfa_disable(body: DisableBody, token: TokenData = Depends(get_current_token)):
    # Verify current password.
    async with httpx.AsyncClient(timeout=30.0) as c:
        verify = await c.post(
            f"{ODOO_URL}/web/session/authenticate",
            json={"jsonrpc": "2.0", "params": {
                "db": ODOO_DB, "login": token.username, "password": body.current_password}},
        )
    if not verify.json().get("result", {}).get("uid"):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    async with odoo_session() as client:
        user = await _read_user(client, token.user_id, ["mfa_secret", "mfa_enabled"])
        if not user.get("mfa_enabled"):
            raise HTTPException(status_code=400, detail="MFA is not enabled")
        secret = crypto_utils.field_decrypt(user.get("mfa_secret") or "")
        if not secret or not pyotp.TOTP(secret).verify(body.code, valid_window=1):
            raise HTTPException(status_code=400, detail="Invalid MFA code")
        await call_kw(client, "res.users", "write", [[token.user_id], {
            "mfa_enabled": False, "mfa_secret": False, "mfa_backup_codes": False,
        }])
    try:
        from routers import audit as audit_router
        await audit_router.record_audit_event(
            "mfa_disabled", "warning", user_id=token.user_id, actor_login=token.username)
    except Exception:
        pass
    return {"success": True, "message": "MFA disabled"}


@router.get("/status", summary="Current user's MFA status")
async def mfa_status(token: TokenData = Depends(get_current_token)):
    async with odoo_session() as client:
        user = await _read_user(client, token.user_id, ["mfa_enabled"])
    return {
        "mfa_enabled": bool(user.get("mfa_enabled")),
        "enforced": token.role in ENFORCED_MFA_ROLES,
    }
