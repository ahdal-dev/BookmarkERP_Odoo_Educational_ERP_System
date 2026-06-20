"""Network-segmentation / ACL middleware for the API gateway.

Adds four request-time controls on top of the existing per-route ``require_roles``
dependencies (defense in depth):

1. **IP allowlist** for ``/api/v1/admin/*`` (env ``ADMIN_IP_ALLOWLIST``; empty =
   allow all, so a mis-set value never locks admins out by accident).
2. **Per-role Redis sliding-window rate limiting** (admin 10/min, faculty 60/min,
   student 120/min), keyed per (identity, endpoint) so a page's normal fan-out of
   distinct calls is never throttled — only rapid repeats of one endpoint are.
3. **Origin/Referer validation** for state-changing methods (env ``ALLOWED_ORIGINS``).
4. **Coarse RBAC path map** restricting admin/registrar/faculty prefixes to the
   appropriate roles; denied attempts are written to ``audit.log``.

All checks skip CORS pre-flight (OPTIONS) and a public allowlist, and fail open
if Redis/decoding is unavailable so the gateway never hard-breaks on infra hiccups.
"""
import ipaddress
import logging
import os
import time
import uuid

import jwt
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") or ""
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PUBLIC_PREFIXES = (
    "/health", "/metrics", "/docs", "/redoc", "/api/openapi.json",
    "/api/v1/auth/login", "/api/v1/auth/refresh", "/api/v1/auth/mfa",
    "/api/v1/extract-document", "/api/v1/admissions",
)

# Role tiers for rate limiting (requests per minute).
_ADMIN_ROLES = {"super_admin", "admin"}
_FACULTY_ROLES = {"instructor", "academic_advisor", "department_chair", "registrar"}
RATE_LIMITS = {
    "admin": int(os.getenv("RATE_LIMIT_ADMIN", "10")),
    "faculty": int(os.getenv("RATE_LIMIT_FACULTY", "60")),
    "student": int(os.getenv("RATE_LIMIT_STUDENT", "120")),
}
RATE_WINDOW_SECONDS = 60

# Coarse RBAC: prefix -> roles allowed (super_admin always allowed). Only
# unambiguously single-tier prefixes are listed so mixed-access routers
# (support, registration, advising) keep their per-endpoint require_roles guards.
RBAC_PREFIX_ROLES = {
    "/api/v1/admin": _ADMIN_ROLES,
    "/api/v1/registrar": _ADMIN_ROLES | {"registrar"},
    "/api/v1/faculty": _ADMIN_ROLES | _FACULTY_ROLES,
}


def _parse_allowlist(raw: str):
    nets = []
    for item in (raw or "").split(","):
        item = item.strip()
        if not item:
            continue
        try:
            nets.append(ipaddress.ip_network(item, strict=False))
        except ValueError:
            logger.warning("Ignoring invalid ADMIN_IP_ALLOWLIST entry: %s", item)
    return nets


ADMIN_IP_NETS = _parse_allowlist(os.getenv("ADMIN_IP_ALLOWLIST", ""))
ALLOWED_ORIGINS = {
    o.strip().rstrip("/")
    for o in os.getenv("ALLOWED_ORIGINS", os.getenv("CORS_ORIGINS", "http://localhost:5173")).split(",")
    if o.strip()
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _is_public(path: str) -> bool:
    return any(path == p or path.startswith(p) for p in PUBLIC_PREFIXES)


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _decode_token(request: Request):
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    try:
        return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except Exception:
        return None


def _role_tier(role: str) -> str:
    if role in _ADMIN_ROLES:
        return "admin"
    if role in _FACULTY_ROLES:
        return "faculty"
    return "student"


async def _audit_deny(event: str, request: Request, payload, detail: str):
    """Best-effort write to audit.log (structured log always; DB row if possible)."""
    ip = _client_ip(request)
    audit_logger.warning('{"event": "%s", "path": "%s", "ip": "%s", "detail": "%s"}'
                         % (event, request.url.path, ip, detail))
    try:
        from routers import audit as audit_router
        uid = (payload or {}).get("user_id")
        login = (payload or {}).get("username")
        await audit_router.record_audit_event(
            event, "warning", user_id=uid, actor_login=login, ip=ip, detail=detail)
    except Exception:
        pass


async def _sliding_window_exceeded(redis, key: str, limit: int) -> bool:
    """Return True if this hit pushes the count over ``limit`` in the window.
    Fail open (return False) on any Redis error."""
    if redis is None:
        return False
    now = time.time()
    try:
        pipe = redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - RATE_WINDOW_SECONDS)
        pipe.zadd(key, {f"{now}:{uuid.uuid4().hex}": now})
        pipe.zcard(key)
        pipe.expire(key, RATE_WINDOW_SECONDS)
        results = await pipe.execute()
        count = results[2]
        return count > limit
    except Exception:
        logger.debug("rate-limit check failed; allowing", exc_info=True)
        return False


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------
def register_security_middleware(app):

    @app.middleware("http")
    async def security_gate(request: Request, call_next):
        path = request.url.path
        method = request.method

        # Never gate pre-flight or public paths.
        if method == "OPTIONS" or _is_public(path):
            return await call_next(request)

        payload = _decode_token(request)
        role = (payload or {}).get("role", "")
        identity = str((payload or {}).get("user_id") or _client_ip(request))

        # --- 1. IP allowlist for admin endpoints --------------------------
        if path.startswith("/api/v1/admin") and ADMIN_IP_NETS:
            ip = _client_ip(request)
            try:
                addr = ipaddress.ip_address(ip)
                allowed = any(addr in net for net in ADMIN_IP_NETS)
            except ValueError:
                allowed = False
            if not allowed:
                await _audit_deny("admin_ip_denied", request, payload,
                                  f"ip={ip} not in allowlist")
                return JSONResponse(status_code=403,
                                    content={"detail": "Admin access is restricted by IP allowlist."})

        # --- 2. Origin / Referer validation (state-changing methods) ------
        if method in ("POST", "PUT", "PATCH", "DELETE"):
            origin = request.headers.get("origin") or request.headers.get("referer")
            if origin:
                host = origin.rstrip("/")
                # Match scheme+host prefix against the allowlist.
                if not any(host == a or host.startswith(a) for a in ALLOWED_ORIGINS):
                    await _audit_deny("origin_denied", request, payload,
                                      f"origin={origin}")
                    return JSONResponse(status_code=403,
                                        content={"detail": "Request origin is not allowed."})

        # --- 3. Coarse RBAC path map --------------------------------------
        for prefix, roles in RBAC_PREFIX_ROLES.items():
            if path.startswith(prefix):
                if role and role not in roles:
                    await _audit_deny("rbac_denied", request, payload,
                                      f"role={role} blocked from {prefix}")
                    return JSONResponse(status_code=403,
                                        content={"detail": f"Role '{role}' may not access {prefix}."})
                break

        # --- 4. Per-role sliding-window rate limit ------------------------
        redis = getattr(request.app.state, "redis", None)
        limit = RATE_LIMITS[_role_tier(role)]
        rl_key = f"ratelimit:{identity}:{method}:{path}"
        if await _sliding_window_exceeded(redis, rl_key, limit):
            await _audit_deny("rate_limited", request, payload,
                              f"tier={_role_tier(role)} limit={limit}/min")
            return JSONResponse(status_code=429,
                                content={"detail": "Rate limit exceeded. Slow down."})

        return await call_next(request)

    logger.info("Security middleware registered (IP ACL, origin, RBAC, rate limit)")
