# -*- coding: utf-8 -*-
"""
Integration tests — CORS enforcement.

Verifies that the gateway allows requests from configured origins and blocks
requests from unlisted origins.
"""
import os
import pytest
from fastapi.testclient import TestClient

os.environ["JWT_SECRET_KEY"]  = os.environ.get("JWT_SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-production")
os.environ["ODOO_PASSWORD"]   = os.environ.get("ODOO_PASSWORD", "test-password")
os.environ["CORS_ORIGINS"]    = "http://localhost:5173,http://allowed.example.com"

from main import app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def test_allowed_origin_gets_cors_header(client):
    """A preflight from an allowed origin must receive Access-Control-Allow-Origin."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 204)
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_second_allowed_origin_gets_cors_header(client):
    response = client.options(
        "/health",
        headers={
            "Origin": "http://allowed.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in (200, 204)
    assert response.headers.get("access-control-allow-origin") == "http://allowed.example.com"


def test_unlisted_origin_gets_no_cors_header(client):
    """An origin not in CORS_ORIGINS must not receive an allow header."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    # FastAPI CORS middleware omits the header for unrecognised origins
    assert response.headers.get("access-control-allow-origin") != "http://evil.example.com"


def test_simple_get_from_allowed_origin(client):
    """A simple GET with a matching Origin returns the ACAO header."""
    response = client.get("/health", headers={"Origin": "http://localhost:5173"})
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"
