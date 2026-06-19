"""
Shared dependencies for FastAPI routers.
Provides JWT verification and a reusable Odoo JSON-RPC helper so each
router doesn't duplicate auth or HTTP boilerplate.
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import AsyncGenerator

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError

# Re-read from env so routers work whether imported by main.py or run standalone.
ODOO_URL      = os.getenv("ODOO_URL", "http://odoo:8081")
ODOO_DB       = os.getenv("ODOO_DB", "edu_demo_new")
ODOO_USERNAME = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD") or ""   # validated by main.py fail-fast
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or "" # validated by main.py fail-fast
JWT_ALGORITHM  = os.getenv("JWT_ALGORITHM", "HS256")

logger = logging.getLogger(__name__)
_bearer = HTTPBearer()


# ---------------------------------------------------------------------------
# JWT verification (mirrors RBACChecker decode logic in main.py)
# ---------------------------------------------------------------------------

class TokenData:
    """Lightweight token payload container (not a Pydantic model — avoids
    importing the full main.py UserRole enum here)."""
    def __init__(self, payload: dict):
        self.user_id: int = payload["user_id"]
        self.username: str = payload.get("username", "")
        self.email: str = payload.get("email", "")
        self.role: str = payload.get("role", "student")
        exp_ts = payload.get("exp", 0)
        self.exp: datetime = datetime.utcfromtimestamp(exp_ts) if exp_ts else datetime.utcnow()


def get_current_token(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> TokenData:
    """Decode and validate the Bearer JWT. Raises 401 on any failure."""
    try:
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
        token = TokenData(payload)
        if token.exp < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    except HTTPException:
        raise
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_roles(*allowed: str):
    """Factory that returns a FastAPI dependency enforcing role membership."""
    def checker(token: TokenData = Depends(get_current_token)) -> TokenData:
        if token.role not in allowed:
            logger.warning(
                "Access denied for %s (role=%s) — required one of %s",
                token.username, token.role, allowed,
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{token.role}' is not authorised. "
                       f"Required: {list(allowed)}",
            )
        return token
    return checker


# ---------------------------------------------------------------------------
# Odoo JSON-RPC helpers
# ---------------------------------------------------------------------------

@asynccontextmanager
async def odoo_session() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async context manager that yields an httpx client already authenticated
    as the service-account admin. The session cookie is kept alive for the
    duration of the context so subsequent call_kw requests work."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        auth_resp = await client.post(
            f"{ODOO_URL}/web/session/authenticate",
            json={
                "jsonrpc": "2.0",
                "params": {"db": ODOO_DB, "login": ODOO_USERNAME, "password": ODOO_PASSWORD},
            },
        )
        result = auth_resp.json().get("result", {})
        if not result.get("uid"):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gateway cannot authenticate with Odoo",
            )
        yield client


async def call_kw(
    client: httpx.AsyncClient,
    model: str,
    method: str,
    args: list,
    kwargs: dict | None = None,
) -> object:
    """Send a call_kw JSON-RPC request and return the result value.
    Raises HTTPException(502) if Odoo returns an error object."""
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "model": model,
            "method": method,
            "args": args,
            "kwargs": kwargs or {},
        },
    }
    resp = await client.post(f"{ODOO_URL}/web/dataset/call_kw", json=payload)
    body = resp.json()
    if "error" in body:
        msg = body["error"].get("data", {}).get("message", str(body["error"]))
        logger.error("Odoo call_kw error (%s.%s): %s", model, method, msg)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)
    return body.get("result")


# ---------------------------------------------------------------------------
# Bulk role resolution (group xmlid → canonical role), highest precedence wins.
# Mirrors ODOO_GROUP_TO_ROLE in main.py but resolves many users in 2 calls.
# ---------------------------------------------------------------------------

GROUP_XMLID_TO_ROLE = [
    ("edu_mang_auth", "group_erp_admin", "super_admin"),
    ("base", "group_system", "super_admin"),
    ("edu_mang_auth", "group_erp_registrar", "registrar"),
    ("edu_mang_auth", "group_erp_department_chair", "department_chair"),
    ("edu_mang_auth", "group_erp_academic_advisor", "academic_advisor"),
    ("edu_mang_auth", "group_erp_instructor", "instructor"),
    ("edu_mang_auth", "group_erp_admission_officer", "admission_officer"),
    ("edu_mang_auth", "group_erp_support_technician", "support_technician"),
    ("edu_mang_auth", "group_erp_student", "student"),
    ("edu_mang_auth", "group_erp_prospective_student", "prospective_student"),
]
_ROLE_RANK = {role: i for i, (_, _, role) in enumerate(GROUP_XMLID_TO_ROLE)}


async def resolve_roles_bulk(client: httpx.AsyncClient, users: list[dict]) -> dict:
    """Map each user (dict with 'id', 'group_ids', 'share') → a canonical role
    string. Two Odoo calls total: one already done by the caller (users), and
    one ir.model.data lookup here to translate group xmlids → res.groups ids."""
    names = list({n for _, n, _ in GROUP_XMLID_TO_ROLE})
    modules = list({m for m, _, _ in GROUP_XMLID_TO_ROLE})
    imd = await call_kw(
        client, "ir.model.data", "search_read",
        [[["model", "=", "res.groups"], ["module", "in", modules], ["name", "in", names]]],
        {"fields": ["module", "name", "res_id"]},
    )
    key_to_gid = {(r["module"], r["name"]): r["res_id"] for r in (imd or [])}
    gid_to_role = {}
    for module, name, role in GROUP_XMLID_TO_ROLE:
        gid = key_to_gid.get((module, name))
        if gid is not None and gid not in gid_to_role:
            gid_to_role[gid] = role

    result = {}
    for u in users:
        best, best_rank = None, 999
        for gid in u.get("group_ids", []) or []:
            role = gid_to_role.get(gid)
            if role and _ROLE_RANK[role] < best_rank:
                best, best_rank = role, _ROLE_RANK[role]
        result[u["id"]] = best or ("student" if u.get("share") else "staff")
    return result
