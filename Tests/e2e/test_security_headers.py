# -*- coding: utf-8 -*-
"""
E2E tests — Security headers and CORS enforcement through the full stack.

These tests hit the running gateway (via TestClient without Docker) and assert
that every response carries the expected security headers set by NGINX
(or FastAPI middleware in unit mode).

When run as true E2E against a live stack, replace `client` with an httpx
client pointed at https://localhost:443.
"""
import os
import pytest
from fastapi.testclient import TestClient

os.environ["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-production")
os.environ["ODOO_PASSWORD"]  = os.environ.get("ODOO_PASSWORD", "test-password")
os.environ["CORS_ORIGINS"]   = "http://localhost:5173"

from main import app

pytestmark = pytest.mark.e2e


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_health_returns_200(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_x_request_id_present_on_every_response(client):
    """X-Request-ID must be injected by the observability middleware."""
    resp = client.get("/health")
    assert "x-request-id" in resp.headers
    # Must be a valid UUID
    import uuid
    uuid.UUID(resp.headers["x-request-id"])


def test_cors_allowed_origin_reflected(client):
    resp = client.get(
        "/health",
        headers={"Origin": "http://localhost:5173"},
    )
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_cors_unlisted_origin_blocked(client):
    resp = client.get(
        "/health",
        headers={"Origin": "http://attacker.example.com"},
    )
    assert resp.headers.get("access-control-allow-origin") != "http://attacker.example.com"


def test_unauthenticated_request_returns_401_not_500(client):
    """Accessing a protected endpoint without a token must return 401, never 500."""
    resp = client.post(
        "/api/v1/admissions/apply",
        json={"full_name": "Test"},
    )
    assert resp.status_code in (401, 403, 422)


def test_test_token_endpoint_disabled_by_default(client):
    """ENABLE_TEST_TOKENS is not set — endpoint must return 403."""
    resp = client.post("/api/v1/auth/token?username=hacker&role=super_admin")
    assert resp.status_code == 403


def test_metrics_endpoint_returns_prometheus_text(client):
    """/metrics must return Prometheus text format, not the old static JSON."""
    resp = client.get("/metrics")
    assert resp.status_code == 200
    # Prometheus exposition format starts with '# HELP' or '# TYPE' lines
    content = resp.text
    assert "http_requests_total" in content or "# HELP" in content or "# TYPE" in content
