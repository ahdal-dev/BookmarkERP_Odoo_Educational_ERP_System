"""
HTTP client for the FastAPI API gateway.

Used by agent tools that need gateway-only endpoints — e.g., Redis-backed active
session stats, the OCR document-verification microservice, or any future endpoint
that lives in the gateway tier rather than Odoo. Student-scoped data (grades,
registrations, petitions) is still fetched via direct Odoo XML-RPC (odoo_client.py)
because the gateway scopes those responses to the JWT holder's user_id, which would
be the admin's — not the individual student's.

Auth: a single admin JWT obtained on first use and reused for the process lifetime.
A 401 from the gateway causes a one-time token refresh before re-raising.

Environment variables
---------------------
GATEWAY_URL          Base URL of the FastAPI gateway (default: http://gateway:8000)
GATEWAY_TIMEOUT      HTTP timeout in seconds (default: 15)
ODOO_USERNAME        Username for the admin login call (default: admin)
ODOO_PASSWORD        Password for the admin login call (default: admin)
"""
from __future__ import annotations

import os
import threading
from typing import Any, Optional

try:
    import httpx as _httpx
    _HTTPX_AVAILABLE = True
except ImportError:
    _httpx = None  # type: ignore[assignment]
    _HTTPX_AVAILABLE = False

GATEWAY_URL: str = os.getenv("GATEWAY_URL", "http://gateway:8000").rstrip("/")
GATEWAY_TIMEOUT: float = float(os.getenv("GATEWAY_TIMEOUT", "15"))

_ODOO_USERNAME: str = os.getenv("ODOO_USERNAME", "admin")
_ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD", "admin")

_lock = threading.Lock()
_token: Optional[str] = None


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class GatewayError(Exception):
    """Business / HTTP error from the gateway — safe to surface to the user."""


class GatewayUnavailable(GatewayError):
    """Gateway is unreachable or returned a 5xx — map to SYSTEM_DOWN_MSG."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _available() -> bool:
    return _HTTPX_AVAILABLE and bool(GATEWAY_URL)


def _get_token() -> str:
    """Return a cached admin JWT, refreshing it when the cache is empty."""
    global _token
    if not _available():
        raise GatewayUnavailable("httpx not installed or GATEWAY_URL is not configured")
    with _lock:
        if _token:
            return _token
        try:
            resp = _httpx.post(
                f"{GATEWAY_URL}/api/v1/auth/login",
                json={"username": _ODOO_USERNAME, "password": _ODOO_PASSWORD},
                timeout=GATEWAY_TIMEOUT,
            )
            resp.raise_for_status()
        except _httpx.RequestError as exc:
            raise GatewayUnavailable(f"Gateway unreachable during auth: {exc}") from exc
        except _httpx.HTTPStatusError as exc:
            raise GatewayUnavailable(
                f"Gateway auth failed (HTTP {exc.response.status_code})"
            ) from exc
        data = resp.json()
        tok: str = data.get("access_token") or data.get("token") or ""
        if not tok:
            raise GatewayUnavailable("Gateway login succeeded but returned no token")
        _token = tok
        return _token


def _invalidate_token() -> None:
    global _token
    with _lock:
        _token = None


def _auth_header() -> dict[str, str]:
    return {"Authorization": f"Bearer {_get_token()}"}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def gateway_get(path: str, params: Optional[dict] = None) -> Any:
    """Authenticated GET to the gateway; returns parsed JSON.

    Raises GatewayUnavailable (network / 5xx) or GatewayError (4xx).
    """
    if not _available():
        raise GatewayUnavailable("Gateway client not available (httpx missing or no GATEWAY_URL)")
    try:
        resp = _httpx.get(
            f"{GATEWAY_URL}{path}",
            params=params,
            headers=_auth_header(),
            timeout=GATEWAY_TIMEOUT,
        )
        if resp.status_code == 401:
            _invalidate_token()
            raise GatewayUnavailable("Gateway token expired; retry the request")
        resp.raise_for_status()
        return resp.json()
    except _httpx.RequestError as exc:
        raise GatewayUnavailable(f"Gateway unreachable: {exc}") from exc
    except _httpx.HTTPStatusError as exc:
        detail = exc.response.text[:300]
        raise GatewayError(
            f"Gateway returned HTTP {exc.response.status_code}: {detail}"
        ) from exc


def gateway_post(path: str, body: dict) -> Any:
    """Authenticated POST to the gateway; returns parsed JSON.

    Raises GatewayUnavailable (network / 5xx) or GatewayError (4xx).
    """
    if not _available():
        raise GatewayUnavailable("Gateway client not available (httpx missing or no GATEWAY_URL)")
    try:
        resp = _httpx.post(
            f"{GATEWAY_URL}{path}",
            json=body,
            headers=_auth_header(),
            timeout=GATEWAY_TIMEOUT,
        )
        if resp.status_code == 401:
            _invalidate_token()
            raise GatewayUnavailable("Gateway token expired; retry the request")
        resp.raise_for_status()
        return resp.json()
    except _httpx.RequestError as exc:
        raise GatewayUnavailable(f"Gateway unreachable: {exc}") from exc
    except _httpx.HTTPStatusError as exc:
        detail = exc.response.text[:300]
        raise GatewayError(
            f"Gateway returned HTTP {exc.response.status_code}: {detail}"
        ) from exc


def gateway_patch(path: str, body: Optional[dict] = None) -> Any:
    """Authenticated PATCH to the gateway; returns parsed JSON."""
    if not _available():
        raise GatewayUnavailable("Gateway client not available")
    try:
        resp = _httpx.patch(
            f"{GATEWAY_URL}{path}",
            json=body or {},
            headers=_auth_header(),
            timeout=GATEWAY_TIMEOUT,
        )
        if resp.status_code == 401:
            _invalidate_token()
            raise GatewayUnavailable("Gateway token expired; retry the request")
        resp.raise_for_status()
        return resp.json()
    except _httpx.RequestError as exc:
        raise GatewayUnavailable(f"Gateway unreachable: {exc}") from exc
    except _httpx.HTTPStatusError as exc:
        detail = exc.response.text[:300]
        raise GatewayError(
            f"Gateway returned HTTP {exc.response.status_code}: {detail}"
        ) from exc
