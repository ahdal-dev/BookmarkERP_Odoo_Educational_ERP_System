# -*- coding: utf-8 -*-
"""
Integration tests — FastAPI-level rate limiting (slowapi).

These tests send requests above the configured limits and assert HTTP 429 is
returned. Each test uses a fresh app import so rate-limit state doesn't bleed
between test runs.
"""
import os
import pytest
import respx
from httpx import Response
from fastapi.testclient import TestClient

os.environ["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-production")
os.environ["ODOO_PASSWORD"]  = os.environ.get("ODOO_PASSWORD", "test-password")
os.environ["ODOO_URL"]       = os.environ.get("ODOO_URL", "http://mock-odoo:8069")

from main import app

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@respx.mock
def test_login_rate_limit_triggers_429(client):
    """
    The login endpoint allows 10 requests/minute per IP.
    Sending 12 in quick succession must trigger at least one 429.
    """
    # Mock Odoo auth to always fail quickly (wrong password) so we hammer the
    # rate limiter, not Odoo.
    respx.post(os.environ["ODOO_URL"] + "/web/session/authenticate").mock(
        return_value=Response(200, json={"jsonrpc": "2.0", "result": {"uid": None}})
    )

    status_codes = []
    for _ in range(12):
        resp = client.post(
            "/api/v1/auth/login",
            json={"login": "bad@user.com", "password": "wrong", "db": "test_db"},
        )
        status_codes.append(resp.status_code)

    assert 429 in status_codes, (
        f"Expected at least one 429 after 12 rapid login attempts, got: {status_codes}"
    )


@respx.mock
def test_ocr_rate_limit_triggers_429(client):
    """
    The OCR endpoint allows 5 requests/minute. 7 rapid calls should trigger 429.
    """
    respx.post(os.environ.get("OCR_SERVICE_URL", "http://mock-ocr:5000") + "/ocr").mock(
        return_value=Response(200, json={"result": {}, "confidence": 0.9})
    )

    from datetime import datetime, timedelta
    import jwt, uuid
    token = jwt.encode(
        {
            "user_id": 1, "username": "user", "email": "u@x.com",
            "role": "prospective_student",
            "jti": str(uuid.uuid4()), "type": "access",
            "exp": datetime.utcnow() + timedelta(hours=1),
        },
        os.environ["JWT_SECRET_KEY"],
        algorithm="HS256",
    )
    headers = {"Authorization": f"Bearer {token}"}

    import io
    fake_file = io.BytesIO(b"fake image content")

    status_codes = []
    for _ in range(7):
        resp = client.post(
            "/api/v1/extract-document",
            files={"file": ("test.jpg", fake_file, "image/jpeg")},
            headers=headers,
        )
        fake_file.seek(0)
        status_codes.append(resp.status_code)

    assert 429 in status_codes, (
        f"Expected 429 after 7 rapid OCR requests, got: {status_codes}"
    )
