"""
============================================================================
FastAPI API Gateway for Educational ERP System
============================================================================
Purpose:       Central API Gateway — authentication, RBAC, service orchestration
Security:      JWT (HS256) + RBAC + Redis-backed token blocklist
Observability: Prometheus metrics, structured JSON logs, X-Request-ID headers
============================================================================
"""

import os
import json
import uuid
import time
import logging
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

from fastapi import (
    FastAPI, HTTPException, Depends, UploadFile, File,
    status, Request, Form,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, EmailStr, validator
import httpx
import jwt
from jwt.exceptions import InvalidTokenError

from prometheus_client import Counter, Histogram, make_asgi_app

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

import redis.asyncio as aioredis

# ============================================================================
# Configuration
# ============================================================================

OCR_SERVICE_URL = os.getenv("OCR_SERVICE_URL", "http://ocr_microservice:5000")
ODOO_URL        = os.getenv("ODOO_URL", "http://odoo:8081")
ODOO_DB         = os.getenv("ODOO_DB", "edu_demo_new")
ODOO_USERNAME   = os.getenv("ODOO_USERNAME", "admin")
ODOO_PASSWORD   = os.getenv("ODOO_PASSWORD")   # required — no default
JWT_SECRET_KEY  = os.getenv("JWT_SECRET_KEY")  # required — no default
JWT_ALGORITHM                = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS         = int(os.getenv("JWT_EXPIRATION_HOURS", "1"))
JWT_REFRESH_EXPIRATION_DAYS  = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", "7"))
CORS_ORIGINS    = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")]
ENABLE_TEST_TOKENS = os.getenv("ENABLE_TEST_TOKENS", "").lower() in ("1", "true", "yes")

_REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
_REDIS_HOST     = os.getenv("REDIS_HOST", "redis")
_REDIS_PORT     = os.getenv("REDIS_PORT", "6379")
REDIS_URL = os.getenv(
    "REDIS_URL",
    f"redis://:{_REDIS_PASSWORD}@{_REDIS_HOST}:{_REDIS_PORT}/0",
)

# Fail-fast — crash immediately if critical secrets are missing
for _var, _val in {"JWT_SECRET_KEY": JWT_SECRET_KEY, "ODOO_PASSWORD": ODOO_PASSWORD}.items():
    if not _val:
        raise RuntimeError(
            f"Required environment variable {_var!r} is not set. "
            "Add it to your .env file before starting the gateway."
        )

# ============================================================================
# Logging — structured JSON
# ============================================================================

class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        data: Dict[str, Any] = {
            "ts":      datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level":   record.levelname,
            "logger":  record.name,
            "msg":     record.getMessage(),
        }
        if record.exc_info:
            data["exc"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False)


_handler = logging.StreamHandler()
_handler.setFormatter(_JsonFormatter())
logging.root.handlers = [_handler]
logging.root.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
logger       = logging.getLogger(__name__)
audit_logger = logging.getLogger("audit")

# ============================================================================
# Prometheus Metrics
# ============================================================================

REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)
ODOO_ERRORS  = Counter("odoo_proxy_errors_total",  "Odoo proxy error count", ["endpoint"])
AUTH_COUNTER = Counter("auth_login_attempts_total", "Auth login attempts",    ["outcome"])

# ============================================================================
# Circuit Breaker
# ============================================================================

class _CircuitBreaker:
    """Three-state circuit breaker: closed → open → half-open."""
    CLOSED    = "closed"
    OPEN      = "open"
    HALF_OPEN = "half_open"

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout  = recovery_timeout
        self._state            = self.CLOSED
        self._failures         = 0
        self._opened_at: float = 0.0

    def success(self) -> None:
        self._failures = 0
        self._state    = self.CLOSED

    def failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._state     = self.OPEN
            self._opened_at = time.monotonic()

    @property
    def is_open(self) -> bool:
        if self._state == self.OPEN:
            if time.monotonic() - self._opened_at >= self.recovery_timeout:
                self._state = self.HALF_OPEN
                return False
            return True
        return False


_odoo_breaker = _CircuitBreaker()
_ocr_breaker  = _CircuitBreaker()

# ============================================================================
# Rate Limiter
# ============================================================================

limiter = Limiter(key_func=get_remote_address)

# ============================================================================
# Shared HTTP client (connection pool, set by lifespan)
# ============================================================================

_http_client: Optional[httpx.AsyncClient] = None


def _client() -> httpx.AsyncClient:
    """Return the shared async HTTP client (raises if lifespan has not run)."""
    if _http_client is None:
        raise RuntimeError("Shared HTTP client is not initialised. Is lifespan running?")
    return _http_client

# ============================================================================
# Pydantic Models
# ============================================================================

class UserRole(str, Enum):
    """
    9 canonical RBAC roles — mirrors Odoo groups (edu_mang_auth/security/security.xml)
    and the frontend ROLES map (bookmark-frontend/src/config/roles.js).
    """
    PROSPECTIVE_STUDENT = "prospective_student"
    ADMISSION_OFFICER   = "admission_officer"
    STUDENT             = "student"
    INSTRUCTOR          = "instructor"
    ACADEMIC_ADVISOR    = "academic_advisor"
    DEPARTMENT_CHAIR    = "department_chair"
    REGISTRAR           = "registrar"
    SUPPORT_TECHNICIAN  = "support_technician"
    SUPER_ADMIN         = "super_admin"


# Maps Odoo XML group IDs → canonical role.  Ordered by precedence (highest first).
ODOO_GROUP_TO_ROLE = [
    ("group_erp_admin",              UserRole.SUPER_ADMIN),
    ("group_erp_registrar",          UserRole.REGISTRAR),
    ("group_erp_department_chair",   UserRole.DEPARTMENT_CHAIR),
    ("group_erp_academic_advisor",   UserRole.ACADEMIC_ADVISOR),
    ("group_erp_instructor",         UserRole.INSTRUCTOR),
    ("group_erp_admission_officer",  UserRole.ADMISSION_OFFICER),
    ("group_erp_support_technician", UserRole.SUPPORT_TECHNICIAN),
    ("group_erp_student",            UserRole.STUDENT),
    ("group_erp_prospective_student", UserRole.PROSPECTIVE_STUDENT),
]


class TokenData(BaseModel):
    user_id:  int
    username: str
    email:    EmailStr
    role:     UserRole
    exp:      datetime
    jti:      Optional[str] = None   # JWT ID — used for token blocklist


class OCRResponse(BaseModel):
    success:         bool
    extracted_data:  Dict[str, Any]
    confidence:      Optional[float] = None
    processing_time: Optional[float] = None


class AdmissionApplicationData(BaseModel):
    full_name:              str   = Field(..., min_length=2,  max_length=200)
    national_id:            str   = Field(..., pattern=r'^\d{14}$')
    email:                  EmailStr
    phone:                  str   = Field(..., pattern=r'^\+?[0-9]{10,15}$')
    date_of_birth:          datetime
    address:                str   = Field(..., min_length=10, max_length=500)
    city:                   str   = Field(..., max_length=100)
    country:                str   = Field(default="Egypt",   max_length=100)
    previous_qualification: str   = Field(..., max_length=200)
    graduation_year:        int   = Field(..., ge=1950, le=2030)
    gpa:                    float = Field(..., ge=0.0,  le=4.0)
    desired_program:        str   = Field(..., max_length=200)
    application_type:       str   = Field(default="regular", max_length=50)

    @validator("graduation_year")
    def _no_future_year(cls, v: int) -> int:
        if v > datetime.now().year:
            raise ValueError("Graduation year cannot be in the future")
        return v


class AdmissionResponse(BaseModel):
    success:        bool
    application_id: Optional[int]       = None
    student_id:     Optional[int]       = None
    status:         str
    message:        str
    next_steps:     Optional[List[str]] = None


class OrchestrationRequest(BaseModel):
    email:            EmailStr
    phone:            str
    desired_program:  str
    application_type: str = "regular"


class OrchestrationResponse(BaseModel):
    success:          bool
    ocr_result:       Optional[OCRResponse]       = None
    admission_result: Optional[AdmissionResponse] = None
    execution_time:   float
    errors:           Optional[List[str]]          = None

# ============================================================================
# JWT / RBAC
# ============================================================================

security = HTTPBearer()


class RBACChecker:
    """Validates the Bearer JWT and enforces role-based access control."""

    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> TokenData:
        token = credentials.credentials
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            token_data = TokenData(
                user_id  = payload["user_id"],
                username = payload.get("username", ""),
                email    = payload.get("email", ""),
                role     = UserRole(payload["role"]),
                exp      = datetime.fromtimestamp(payload["exp"]),
                jti      = payload.get("jti"),
            )

            if token_data.exp < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # Blocklist check (requires Redis)
            redis_conn = getattr(request.app.state, "redis", None)
            if redis_conn and token_data.jti:
                if await redis_conn.exists(f"blocklist:{token_data.jti}"):
                    audit_logger.warning(json.dumps({
                        "event": "revoked_token_used",
                        "jti": token_data.jti,
                        "user_id": token_data.user_id,
                    }))
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has been revoked",
                        headers={"WWW-Authenticate": "Bearer"},
                    )

            if token_data.role not in self.allowed_roles:
                audit_logger.warning(json.dumps({
                    "event": "access_denied",
                    "user_id": token_data.user_id,
                    "role": token_data.role.value,
                    "path": request.url.path,
                }))
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            logger.info({"msg": "Authenticated", "user": token_data.username, "role": token_data.role.value})
            return token_data

        except HTTPException:
            raise
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception:
            logger.error("Authentication error", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

# ============================================================================
# Odoo helpers
# ============================================================================

async def _odoo_service_auth(client: httpx.AsyncClient) -> None:
    """Authenticate the gateway service account with Odoo on the given client."""
    await client.post(
        f"{ODOO_URL}/web/session/authenticate",
        json={"jsonrpc": "2.0", "params": {
            "db": ODOO_DB, "login": ODOO_USERNAME, "password": ODOO_PASSWORD,
        }},
    )


async def _get_country_id(country_name: str, redis_conn=None) -> int:
    """Return the Odoo res.country id for *country_name*, with 24-hour Redis cache."""
    cache_key = f"country_id:{country_name.lower()}"
    if redis_conn:
        cached = await redis_conn.get(cache_key)
        if cached:
            return int(cached)

    try:
        async with httpx.AsyncClient(timeout=10.0) as c:
            await _odoo_service_auth(c)
            resp = await c.post(
                f"{ODOO_URL}/web/dataset/call_kw",
                json={"jsonrpc": "2.0", "method": "call", "params": {
                    "model": "res.country", "method": "search_read",
                    "args": [[["name", "ilike", country_name]]],
                    "kwargs": {"fields": ["id"], "limit": 1},
                }},
            )
            result = resp.json().get("result", [])
            country_id = result[0]["id"] if result else 65  # Egypt fallback
    except Exception:
        logger.warning("Country ID lookup failed, using fallback 65", exc_info=True)
        country_id = 65

    if redis_conn:
        await redis_conn.setex(cache_key, 86400, str(country_id))
    return country_id


async def _resolve_role_with_client(client: httpx.AsyncClient, uid: int) -> UserRole:
    """Resolve an Odoo user's canonical role from their security groups."""
    await _odoo_service_auth(client)

    user_resp = await client.post(
        f"{ODOO_URL}/web/dataset/call_kw",
        json={"jsonrpc": "2.0", "method": "call", "params": {
            "model": "res.users", "method": "read",
            "args": [[uid], ["group_ids"]], "kwargs": {},
        }},
    )
    user_result = user_resp.json().get("result", [])
    if not user_result:
        return UserRole.STUDENT
    user_group_ids = set(user_result[0].get("group_ids", []))

    data_resp = await client.post(
        f"{ODOO_URL}/web/dataset/call_kw",
        json={"jsonrpc": "2.0", "method": "call", "params": {
            "model": "ir.model.data", "method": "search_read",
            "args": [[
                "|",
                "&", ["module", "=", "edu_mang_auth"],
                     ["name", "in", [g for g, _ in ODOO_GROUP_TO_ROLE]],
                "&", ["module", "=", "base"],
                     ["name", "=", "group_system"],
            ]],
            "kwargs": {"fields": ["module", "name", "res_id"]},
        }},
    )
    name_to_resid = {r["name"]: r["res_id"] for r in data_resp.json().get("result", [])}

    system_gid = name_to_resid.get("group_system")
    if system_gid and system_gid in user_group_ids:
        return UserRole.SUPER_ADMIN

    for group_name, role in ODOO_GROUP_TO_ROLE:
        gid = name_to_resid.get(group_name)
        if gid and gid in user_group_ids:
            return role

    return UserRole.STUDENT


async def resolve_user_role(uid: int, redis_conn=None) -> UserRole:
    """Resolve role with 5-minute Redis cache."""
    cache_key = f"role:{uid}"
    if redis_conn:
        cached = await redis_conn.get(cache_key)
        if cached:
            return UserRole(cached)
    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            role = await _resolve_role_with_client(c, uid)
        if redis_conn:
            await redis_conn.setex(cache_key, 300, role.value)
        logger.info({"msg": "Role resolved", "uid": uid, "role": role.value})
        return role
    except Exception:
        logger.error("Role resolution failed for uid %s", uid, exc_info=True)
        return UserRole.STUDENT


# ============================================================================
# OdooClient — admission operations
# ============================================================================

class OdooClient:
    """Service-account Odoo client for admission operations."""

    def __init__(self):
        self._uid: Optional[int] = None

    async def authenticate(self) -> int:
        if self._uid:
            return self._uid
        try:
            async with httpx.AsyncClient(timeout=30.0) as c:
                resp = await c.post(
                    f"{ODOO_URL}/web/session/authenticate",
                    json={"jsonrpc": "2.0", "params": {
                        "db": ODOO_DB, "login": ODOO_USERNAME, "password": ODOO_PASSWORD,
                    }},
                )
                result = resp.json()
                if result.get("result", {}).get("uid"):
                    self._uid = result["result"]["uid"]
                    return self._uid
                raise Exception("No UID in Odoo auth response")
        except Exception as e:
            logger.error("Odoo service-account auth failed: %s", e)
            raise HTTPException(status_code=503, detail="ERP system unavailable")

    async def create_admission_application(
        self,
        data: AdmissionApplicationData,
        redis_conn=None,
    ) -> Dict[str, Any]:
        if _odoo_breaker.is_open:
            raise HTTPException(
                status_code=503,
                detail="ERP system is temporarily unavailable. Please try again shortly.",
            )
        await self.authenticate()
        try:
            country_id = await _get_country_id(data.country, redis_conn)
            values = {
                "name":                   data.full_name,
                "national_id":            data.national_id,
                "email":                  data.email,
                "phone":                  data.phone,
                "date_of_birth":          data.date_of_birth.strftime("%Y-%m-%d"),
                "street":                 data.address,
                "city":                   data.city,
                "country_id":             country_id,
                "previous_qualification": data.previous_qualification,
                "graduation_year":        data.graduation_year,
                "gpa":                    data.gpa,
                "desired_program":        data.desired_program,
                "application_type":       data.application_type,
                "state":                  "draft",
            }
            async with httpx.AsyncClient(timeout=60.0) as c:
                await _odoo_service_auth(c)
                resp = await c.post(
                    f"{ODOO_URL}/web/dataset/call_kw",
                    json={"jsonrpc": "2.0", "method": "call", "params": {
                        "model": "op.admission", "method": "create",
                        "args": [values], "kwargs": {},
                    }, "id": 1},
                )
                result = resp.json()
            if "result" in result:
                _odoo_breaker.success()
                app_id = result["result"]
                logger.info({"msg": "Admission created", "application_id": app_id})
                return {"application_id": app_id, "status": "draft",
                        "message": "Application submitted successfully"}
            raise Exception("No result field in Odoo response")
        except HTTPException:
            raise
        except Exception:
            _odoo_breaker.failure()
            ODOO_ERRORS.labels(endpoint="create_admission").inc()
            logger.error("Admission creation failed", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to submit application to ERP system")


odoo_client = OdooClient()

# ============================================================================
# FastAPI Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _http_client
    logger.info("Starting FastAPI API Gateway...")

    _http_client = httpx.AsyncClient(
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        timeout=httpx.Timeout(30.0),
    )

    try:
        _redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        await _redis.ping()
        app.state.redis = _redis
        logger.info("Redis connected")
    except Exception as exc:
        logger.warning({"msg": "Redis unavailable — caching/blocklist disabled", "err": str(exc)})
        app.state.redis = None

    try:
        await odoo_client.authenticate()
        logger.info("Odoo connection verified on startup")
    except Exception as exc:
        logger.warning({"msg": "Odoo not reachable on startup", "err": str(exc)})

    yield

    logger.info("Shutting down API Gateway...")
    await _http_client.aclose()
    _http_client = None
    if getattr(app.state, "redis", None):
        await app.state.redis.aclose()

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Educational ERP API Gateway",
    description="Central API Gateway for Educational ERP Microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS — restricted to configured origins (no wildcard)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics at /metrics (separate ASGI app)
app.mount("/metrics", make_asgi_app())

# Petition multi-tier workflow router
from routers import petitions as petitions_router
app.include_router(petitions_router.router)

# Academic Agent (chatbot) proxy router
from routers import chatbot as chatbot_router
app.include_router(chatbot_router.router)

# Account self-service (change password)
from routers import account as account_router
app.include_router(account_router.router)

# Registrar dashboard aggregates
from routers import registrar as registrar_router
app.include_router(registrar_router.router)

# In-app notifications feed
from routers import notifications as notifications_router
app.include_router(notifications_router.router)

# Registration catalog + student/faculty/admin data
from routers import registration as registration_router
app.include_router(registration_router.router)
from routers import registration_tiers as registration_tiers_router
app.include_router(registration_tiers_router.router)
from routers import faculty as faculty_router
app.include_router(faculty_router.router)
from routers import admin as admin_router
app.include_router(admin_router.router)

# ============================================================================
# Middleware — observability and audit logging
# ============================================================================

@app.middleware("http")
async def _observability(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    t0 = time.monotonic()

    response = await call_next(request)

    elapsed  = time.monotonic() - t0
    endpoint = request.url.path
    REQUEST_COUNT.labels(
        method=request.method, endpoint=endpoint,
        status_code=str(response.status_code),
    ).inc()
    REQUEST_LATENCY.labels(method=request.method, endpoint=endpoint).observe(elapsed)
    response.headers["X-Request-ID"] = request_id
    return response


_AUDIT_PREFIXES = ("/api/v1/auth/", "/api/v1/admin/")

@app.middleware("http")
async def _audit(request: Request, call_next):
    response = await call_next(request)
    path = request.url.path
    if (
        any(path.startswith(p) for p in _AUDIT_PREFIXES)
        or response.status_code in (401, 403)
    ):
        audit_logger.info(json.dumps({
            "event":      "security",
            "method":     request.method,
            "path":       path,
            "status":     response.status_code,
            "ip":         request.client.host if request.client else "unknown",
            "request_id": getattr(request.state, "request_id", None),
        }))
    return response

# ============================================================================
# Health
# ============================================================================

@app.get("/health")
async def health_check():
    return {
        "status":    "healthy",
        "service":   "api_gateway",
        "timestamp": datetime.utcnow().isoformat(),
        "version":   "1.0.0",
    }

# ============================================================================
# OCR Endpoint
# ============================================================================

_ALLOWED_MIME = {"image/jpeg", "image/png", "image/jpg", "application/pdf"}
_MAX_UPLOAD   = 10 * 1024 * 1024  # 10 MB


@app.post("/api/v1/extract-document", response_model=OCRResponse,
          summary="Extract data from uploaded document using OCR")
@limiter.limit("5/minute")
async def extract_document(
    request: Request,
    file: UploadFile = File(...),
    user: TokenData = Depends(RBACChecker([
        UserRole.PROSPECTIVE_STUDENT, UserRole.ADMISSION_OFFICER, UserRole.SUPER_ADMIN,
    ])),
):
    if _ocr_breaker.is_open:
        raise HTTPException(status_code=503, detail="OCR service temporarily unavailable")

    if file.content_type not in _ALLOWED_MIME:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file.content_type}'. Allowed: {sorted(_ALLOWED_MIME)}",
        )

    content = await file.read()
    if len(content) > _MAX_UPLOAD:
        raise HTTPException(status_code=413, detail="File exceeds 10 MB limit")

    t0 = datetime.utcnow()
    logger.info({"msg": "OCR request", "user": user.username, "size": len(content)})

    try:
        async with httpx.AsyncClient(timeout=90.0) as c:
            resp = await c.post(
                f"{OCR_SERVICE_URL}/ocr",
                files={"file": (file.filename, content, file.content_type)},
            )
            resp.raise_for_status()
            ocr_data = resp.json()
        _ocr_breaker.success()
    except httpx.HTTPError:
        _ocr_breaker.failure()
        logger.error("OCR service HTTP error", exc_info=True)
        raise HTTPException(status_code=503, detail="OCR service is currently unavailable")
    except Exception:
        _ocr_breaker.failure()
        logger.error("OCR processing failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Document processing failed")

    return OCRResponse(
        success=True,
        extracted_data=ocr_data.get("result", {}),
        confidence=ocr_data.get("confidence", 0.0),
        processing_time=(datetime.utcnow() - t0).total_seconds(),
    )

# ============================================================================
# Admission Endpoints
# ============================================================================

@app.post("/api/v1/admissions/apply", response_model=AdmissionResponse,
          summary="Submit an admission application to the ERP")
async def submit_admission_application(
    request: Request,
    application: AdmissionApplicationData,
    user: TokenData = Depends(RBACChecker([
        UserRole.PROSPECTIVE_STUDENT, UserRole.ADMISSION_OFFICER, UserRole.SUPER_ADMIN,
    ])),
):
    redis_conn = getattr(request.app.state, "redis", None)
    try:
        logger.info({"msg": "Admission apply", "name": application.full_name, "by": user.username})
        result = await odoo_client.create_admission_application(application, redis_conn)
        return AdmissionResponse(
            success=True,
            application_id=result["application_id"],
            status=result["status"],
            message=result["message"],
            next_steps=[
                "Check your email for confirmation",
                "Wait for admission committee review",
                "Track application status in the student portal",
            ],
        )
    except HTTPException:
        raise
    except Exception:
        logger.error("Admission apply failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Application submission failed")


@app.get("/api/v1/admissions", summary="List the authenticated user's admission applications")
async def list_my_admissions(
    request: Request,
    user: TokenData = Depends(RBACChecker([
        UserRole.PROSPECTIVE_STUDENT, UserRole.STUDENT,
        UserRole.ADMISSION_OFFICER, UserRole.SUPER_ADMIN,
    ])),
):
    """Returns school.admission records for the authenticated user's email address."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            await _odoo_service_auth(c)
            resp = await c.post(
                f"{ODOO_URL}/web/dataset/call_kw",
                json={"jsonrpc": "2.0", "method": "call", "params": {
                    "model": "school.admission", "method": "search_read",
                    "args": [[["email", "=", user.email]]],
                    "kwargs": {
                        "fields": ["name", "email", "state", "reference",
                                   "application_date", "program_id"],
                        "order": "application_date desc",
                    },
                }},
            )
        records = resp.json().get("result", [])
        return {"count": len(records), "applications": records}
    except HTTPException:
        raise
    except Exception:
        logger.error("list_my_admissions failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to retrieve applications")


@app.get("/api/v1/admissions/status/{reference}",
         summary="Public status check by application reference number")
async def get_admission_status(reference: str):
    """Public endpoint — does not require authentication."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            await _odoo_service_auth(c)
            resp = await c.post(
                f"{ODOO_URL}/web/dataset/call_kw",
                json={"jsonrpc": "2.0", "method": "call", "params": {
                    "model": "school.admission", "method": "search_read",
                    "args": [[["reference", "=", reference]]],
                    "kwargs": {
                        "fields": ["reference", "state", "application_date", "name"],
                        "limit": 1,
                    },
                }},
            )
        result = resp.json().get("result", [])
        if not result:
            raise HTTPException(status_code=404, detail="Application not found")
        rec = result[0]
        return {
            "reference":      rec["reference"],
            "applicant_name": rec["name"],
            "status":         rec["state"],
            "applied_on":     rec["application_date"],
        }
    except HTTPException:
        raise
    except Exception:
        logger.error("get_admission_status failed for ref=%s", reference, exc_info=True)
        raise HTTPException(status_code=500, detail="Status lookup failed")


@app.post("/api/v1/admissions/submit-with-document", response_model=OrchestrationResponse,
          summary="Orchestrated workflow: OCR extraction + ERP admission submission")
@limiter.limit("2/minute")
async def submit_with_document(
    request: Request,
    file: UploadFile = File(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    desired_program: str = Form(...),
    application_type: str = Form("regular"),
    user: TokenData = Depends(RBACChecker([
        UserRole.PROSPECTIVE_STUDENT, UserRole.ADMISSION_OFFICER, UserRole.SUPER_ADMIN,
    ])),
):
    t0            = datetime.utcnow()
    errors: List[str] = []
    ocr_result    = None
    adm_result    = None

    try:
        logger.info({"msg": "Orchestrated workflow", "user": user.username})

        # Step 1 — OCR
        try:
            content = await file.read()
            async with httpx.AsyncClient(timeout=90.0) as c:
                resp = await c.post(
                    f"{OCR_SERVICE_URL}/ocr",
                    files={"file": (file.filename, content, file.content_type)},
                )
                resp.raise_for_status()
                ocr_data = resp.json()
            ocr_result = OCRResponse(
                success=True,
                extracted_data=ocr_data.get("result", {}),
                confidence=ocr_data.get("confidence", 0.0),
            )
        except Exception:
            logger.error("OCR step failed", exc_info=True)
            errors.append("OCR extraction failed")
            raise

        # Step 2 — map
        try:
            ex = ocr_result.extracted_data
            app_data = AdmissionApplicationData(
                full_name              = ex.get("name", "Unknown"),
                national_id            = ex.get("nid", "00000000000000"),
                email                  = email,
                phone                  = phone,
                date_of_birth          = datetime.strptime(
                    ex.get("date_of_birth", "2000-01-01"), "%Y-%m-%d"
                ),
                address                = ex.get("address", "Not provided"),
                city                   = ex.get("city", "Cairo"),
                country                = "Egypt",
                previous_qualification = ex.get("qualification", "High School"),
                graduation_year        = int(ex.get("graduation_year", 2020)),
                gpa                    = float(ex.get("gpa", 3.0)),
                desired_program        = desired_program,
                application_type       = application_type,
            )
        except Exception:
            logger.error("OCR data mapping failed", exc_info=True)
            errors.append("Data mapping from OCR result failed")
            raise HTTPException(
                status_code=400, detail="Failed to map extracted data to application format"
            )

        # Step 3 — submit to Odoo
        try:
            redis_conn = getattr(request.app.state, "redis", None)
            odoo_res = await odoo_client.create_admission_application(app_data, redis_conn)
            adm_result = AdmissionResponse(
                success=True,
                application_id=odoo_res["application_id"],
                status=odoo_res["status"],
                message=odoo_res["message"],
                next_steps=["Document verified via OCR", "Application submitted", "Check email for updates"],
            )
        except Exception:
            logger.error("Odoo submission step failed", exc_info=True)
            errors.append("ERP submission failed")
            raise

        return OrchestrationResponse(
            success=True, ocr_result=ocr_result, admission_result=adm_result,
            execution_time=(datetime.utcnow() - t0).total_seconds(),
        )

    except HTTPException:
        raise
    except Exception:
        logger.error("Orchestrated workflow failed", exc_info=True)
        return OrchestrationResponse(
            success=False, ocr_result=ocr_result, admission_result=adm_result,
            execution_time=(datetime.utcnow() - t0).total_seconds(),
            errors=errors or ["Workflow failed unexpectedly"],
        )

# ============================================================================
# Auth Endpoints
# ============================================================================

class LoginRequest(BaseModel):
    login:    str
    password: str
    db:       str = "edu_demo_new"


def _make_tokens(uid: int, login: str, email: str, role: UserRole) -> dict:
    """Issue an access token (1 h) and a refresh token (7 d)."""
    now            = datetime.utcnow()
    jti_access     = str(uuid.uuid4())
    jti_refresh    = str(uuid.uuid4())
    access_payload = {
        "user_id": uid, "username": login, "email": email,
        "role": role.value, "jti": jti_access, "type": "access",
        "exp": now + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    refresh_payload = {
        "user_id": uid, "username": login, "email": email,
        "role": role.value, "jti": jti_refresh, "type": "refresh",
        "exp": now + timedelta(days=JWT_REFRESH_EXPIRATION_DAYS),
    }
    return {
        "access_token":  jwt.encode(access_payload,  JWT_SECRET_KEY, algorithm=JWT_ALGORITHM),
        "refresh_token": jwt.encode(refresh_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM),
        "token_type":    "bearer",
        "expires_in":    JWT_EXPIRATION_HOURS * 3600,
    }


@app.post("/api/v1/auth/login", summary="Authenticate and receive JWT access + refresh tokens")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    redis_conn = getattr(request.app.state, "redis", None)
    try:
        async with httpx.AsyncClient(timeout=30.0) as c:
            resp = await c.post(
                f"{ODOO_URL}/web/session/authenticate",
                json={"jsonrpc": "2.0", "params": {
                    "db": body.db, "login": body.login, "password": body.password,
                }},
            )
            result = resp.json()

        if not result.get("result", {}).get("uid"):
            AUTH_COUNTER.labels(outcome="failure").inc()
            audit_logger.warning(json.dumps({
                "event": "login_failed",
                "login": body.login,
                "ip":    request.client.host if request.client else None,
            }))
            raise HTTPException(status_code=401, detail="Invalid credentials")

        uid   = result["result"]["uid"]
        name  = result["result"].get("name", body.login)
        role  = await resolve_user_role(uid, redis_conn)
        tokens = _make_tokens(uid, body.login, body.login, role)

        AUTH_COUNTER.labels(outcome="success").inc()
        audit_logger.info(json.dumps({"event": "login_success", "user_id": uid, "role": role.value}))
        return {**tokens, "user_id": uid, "user_name": name, "role": role.value}

    except HTTPException:
        raise
    except Exception:
        logger.error("Login error", exc_info=True)
        raise HTTPException(status_code=500, detail="Authentication service error")


@app.post("/api/v1/auth/refresh", summary="Obtain new tokens using a refresh token")
async def refresh_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    redis_conn = getattr(request.app.state, "redis", None)
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Not a refresh token")
        if datetime.fromtimestamp(payload["exp"]) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Refresh token expired")

        jti = payload.get("jti")
        if redis_conn and jti and await redis_conn.exists(f"blocklist:{jti}"):
            raise HTTPException(status_code=401, detail="Refresh token has been revoked")

        # Single-use: blocklist the consumed refresh token
        if redis_conn and jti:
            remaining = int((datetime.fromtimestamp(payload["exp"]) - datetime.utcnow()).total_seconds())
            if remaining > 0:
                await redis_conn.setex(f"blocklist:{jti}", remaining, "1")

        uid   = payload["user_id"]
        login = payload.get("username", "")
        email = payload.get("email", login)
        role  = UserRole(payload["role"])
        return _make_tokens(uid, login, email, role)

    except HTTPException:
        raise
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@app.post("/api/v1/auth/logout", summary="Revoke the current access token")
async def logout(
    request: Request,
    user: TokenData = Depends(RBACChecker(list(UserRole))),
):
    redis_conn = getattr(request.app.state, "redis", None)
    if redis_conn and user.jti:
        remaining = int((user.exp - datetime.utcnow()).total_seconds())
        if remaining > 0:
            await redis_conn.setex(f"blocklist:{user.jti}", remaining, "1")
        await redis_conn.delete(f"role:{user.user_id}")
    audit_logger.info(json.dumps({"event": "logout", "user_id": user.user_id}))
    return {"success": True, "message": "Logged out successfully"}


@app.get("/api/v1/auth/session", summary="Validate JWT and return user info")
async def check_session(user: TokenData = Depends(RBACChecker(list(UserRole)))):
    return {
        "valid":    True,
        "user_id":  user.user_id,
        "username": user.username,
        "email":    user.email,
        "role":     user.role.value,
    }

# ============================================================================
# Admin — Module Management
# ============================================================================

@app.get("/api/v1/admin/modules", summary="List Odoo modules (super_admin only)")
async def list_modules(user: TokenData = Depends(RBACChecker([UserRole.SUPER_ADMIN]))):
    await odoo_client.authenticate()
    async with httpx.AsyncClient(timeout=30.0) as c:
        await _odoo_service_auth(c)
        resp = await c.post(
            f"{ODOO_URL}/web/dataset/call_kw",
            json={"jsonrpc": "2.0", "method": "call", "params": {
                "model": "ir.module.module", "method": "search_read",
                "args": [[["state", "in", ["installed", "uninstalled"]]]],
                "kwargs": {"fields": ["name", "shortdesc", "state", "summary"], "limit": 200},
            }},
        )
        return resp.json().get("result", [])


class InstallModuleRequest(BaseModel):
    module_name: str


@app.post("/api/v1/admin/modules/install", summary="Install an Odoo module (super_admin only)")
async def install_module(
    body: InstallModuleRequest,
    user: TokenData = Depends(RBACChecker([UserRole.SUPER_ADMIN])),
):
    await odoo_client.authenticate()
    async with httpx.AsyncClient(timeout=120.0) as c:
        await _odoo_service_auth(c)
        search = await c.post(
            f"{ODOO_URL}/web/dataset/call_kw",
            json={"jsonrpc": "2.0", "method": "call", "params": {
                "model": "ir.module.module", "method": "search_read",
                "args": [[["name", "=", body.module_name]]],
                "kwargs": {"fields": ["id", "state"], "limit": 1},
            }},
        )
        mods = search.json().get("result", [])
        if not mods:
            raise HTTPException(status_code=404, detail=f"Module '{body.module_name}' not found")
        if mods[0]["state"] == "installed":
            return {"success": True, "message": f"Module '{body.module_name}' is already installed"}
        await c.post(
            f"{ODOO_URL}/web/dataset/call_kw",
            json={"jsonrpc": "2.0", "method": "call", "params": {
                "model": "ir.module.module", "method": "button_immediate_install",
                "args": [[mods[0]["id"]]], "kwargs": {},
            }},
        )
        return {"success": True, "message": f"Module '{body.module_name}' installed successfully"}

# ============================================================================
# Test Token Endpoint (disabled in production)
# ============================================================================

@app.post("/api/v1/auth/token", summary="Generate test JWT (disabled unless ENABLE_TEST_TOKENS=1)")
async def generate_test_token(username: str, role: UserRole = UserRole.PROSPECTIVE_STUDENT):
    if not ENABLE_TEST_TOKENS:
        raise HTTPException(status_code=403, detail="Test token endpoint is disabled in this environment")
    payload = {
        "user_id": 1, "username": username,
        "email": f"{username}@example.com",
        "role": role.value,
        "jti": str(uuid.uuid4()), "type": "access",
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
    }
    return {
        "access_token": jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM),
        "token_type":   "bearer",
        "expires_in":   JWT_EXPIRATION_HOURS * 3600,
        "role":         role.value,
    }

# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
