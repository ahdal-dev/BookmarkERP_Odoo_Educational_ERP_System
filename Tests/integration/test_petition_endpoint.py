# -*- coding: utf-8 -*-
"""
Integration tests — Petition API endpoints.

Tests cover:
- Student petition submission (201)
- Role-based queue access (FACULTY_ROLES)
- Unauthorized role rejection (403)
- Chair override
- Input size limits (max_length enforcement)
"""
import os
import uuid
from datetime import datetime, timedelta

import jwt
import pytest
import respx
from httpx import Response
from fastapi.testclient import TestClient

os.environ["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-production")
os.environ["ODOO_PASSWORD"]  = os.environ.get("ODOO_PASSWORD", "test-password")
os.environ["ODOO_URL"]       = os.environ.get("ODOO_URL", "http://mock-odoo:8069")

from main import app, JWT_SECRET_KEY

pytestmark = pytest.mark.integration

_ODOO_URL = os.environ["ODOO_URL"]


@pytest.fixture(scope="module")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


def _token(role: str, uid: int = 1) -> str:
    return jwt.encode(
        {
            "user_id": uid, "username": f"{role}_user",
            "email": f"{role}@test.com", "role": role,
            "jti": str(uuid.uuid4()), "type": "access",
            "exp": datetime.utcnow() + timedelta(hours=1),
        },
        JWT_SECRET_KEY, algorithm="HS256",
    )


def _auth(role: str) -> dict:
    return {"Authorization": f"Bearer {_token(role)}"}


# ---------------------------------------------------------------------------
# Submit petition
# ---------------------------------------------------------------------------

@respx.mock
def test_student_submits_petition_returns_200(client):
    respx.post(_ODOO_URL + "/web/session/authenticate").mock(
        return_value=Response(200, json={"jsonrpc": "2.0", "result": {"uid": 2}})
    )
    respx.post(_ODOO_URL + "/web/dataset/call_kw").mock(
        return_value=Response(200, json={"jsonrpc": "2.0", "result": [{"partner_id": [5, "Test Student"]}]})
    ).mock(
        return_value=Response(200, json={"jsonrpc": "2.0", "result": 42})
    ).mock(
        return_value=Response(200, json={"jsonrpc": "2.0", "result": None})
    ).mock(
        return_value=Response(200, json={"jsonrpc": "2.0", "result": [
            {"name": "PET/001", "state": "submitted", "current_tier": "instructor"}
        ]})
    )
    resp = client.post(
        "/api/v1/petitions/new",
        json={
            "petition_type_id": 1,
            "subject": "Grade Appeal",
            "description": "I believe my grade was incorrectly assigned for the midterm exam.",
        },
        headers=_auth("student"),
    )
    assert resp.status_code == 200


def test_petition_description_too_long_rejected(client):
    """Description exceeding 5000 chars must return 422 from Pydantic validation."""
    resp = client.post(
        "/api/v1/petitions/new",
        json={
            "petition_type_id": 1,
            "subject": "Test",
            "description": "x" * 5001,
        },
        headers=_auth("student"),
    )
    assert resp.status_code == 422


def test_petition_subject_too_long_rejected(client):
    resp = client.post(
        "/api/v1/petitions/new",
        json={
            "petition_type_id": 1,
            "subject": "s" * 201,
            "description": "Valid description that is long enough to pass validation checks.",
        },
        headers=_auth("student"),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Faculty queue — role enforcement
# ---------------------------------------------------------------------------

def test_student_cannot_access_faculty_queue(client):
    resp = client.get("/api/v1/faculty/petitions", headers=_auth("student"))
    assert resp.status_code == 403


def test_prospective_student_cannot_access_faculty_queue(client):
    resp = client.get("/api/v1/faculty/petitions", headers=_auth("prospective_student"))
    assert resp.status_code == 403


@respx.mock
def test_instructor_can_access_faculty_queue(client):
    respx.post(_ODOO_URL + "/web/session/authenticate").mock(
        return_value=Response(200, json={"jsonrpc": "2.0", "result": {"uid": 2}})
    )
    respx.post(_ODOO_URL + "/web/dataset/call_kw").mock(
        return_value=Response(200, json={"jsonrpc": "2.0", "result": []})
    )
    resp = client.get("/api/v1/faculty/petitions", headers=_auth("instructor"))
    assert resp.status_code == 200
    assert "petitions" in resp.json()


# ---------------------------------------------------------------------------
# Override — chair only
# ---------------------------------------------------------------------------

def test_non_chair_cannot_override(client):
    resp = client.post(
        "/api/v1/faculty/petitions/1/override",
        json={"decision": "approve", "reason": "Approved after review"},
        headers=_auth("instructor"),
    )
    assert resp.status_code == 403


def test_override_reason_required(client):
    """reason field must be at least 5 chars (min_length from schema)."""
    resp = client.post(
        "/api/v1/faculty/petitions/1/override",
        json={"decision": "approve", "reason": "hi"},
        headers=_auth("department_chair"),
    )
    assert resp.status_code == 422
