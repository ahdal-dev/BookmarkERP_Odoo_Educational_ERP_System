# -*- coding: utf-8 -*-
"""
Integration Test Fixtures — Layer 2
Provides FastAPI TestClient, valid JWT tokens, and respx mocks
for Odoo and OCR backends.
"""
import os
from datetime import datetime, timedelta

import jwt
import pytest
import respx
from httpx import Response
from fastapi.testclient import TestClient

# Env vars must be set before importing the app
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-production")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_HOURS", "1")
os.environ.setdefault("OCR_SERVICE_URL", "http://mock-ocr:5000")
os.environ.setdefault("ODOO_URL", "http://mock-odoo:8069")
os.environ.setdefault("ODOO_DB", "test_db")
os.environ.setdefault("ODOO_USERNAME", "admin")
os.environ.setdefault("ODOO_PASSWORD", "admin")

from main import app, JWT_SECRET_KEY, JWT_ALGORITHM

# ============================================================================
# TestClient
# ============================================================================

@pytest.fixture(scope="module")
def client():
    """FastAPI TestClient — shares a single app instance per module."""
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


# ============================================================================
# JWT Tokens for different roles
# ============================================================================

def _make_token(role: str, username: str = "test_user") -> str:
    payload = {
        "user_id": 1, "username": username,
        "email": f"{username}@example.com", "role": role,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


@pytest.fixture
def student_token():
    return _make_token("prospective_student", "test_student")

@pytest.fixture
def admin_token():
    return _make_token("admin", "admin_user")

@pytest.fixture
def staff_token():
    return _make_token("admission_staff", "staff_user")

@pytest.fixture
def student_auth_header(student_token):
    return {"Authorization": f"Bearer {student_token}"}

@pytest.fixture
def admin_auth_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ============================================================================
# respx mocks for external services
# ============================================================================

@pytest.fixture
def mock_ocr_success():
    """Mock the OCR service to return a successful extraction."""
    with respx.mock(assert_all_called=False) as mock:
        mock.post("http://mock-ocr:5000/ocr").mock(
            return_value=Response(200, json={
                "result": {
                    "name": "Ahmed Hassan", "nid": "29901011234567",
                    "date_of_birth": "2000-01-15", "address": "123 Tahrir Street, Downtown Cairo",
                    "city": "Cairo", "qualification": "High School",
                    "graduation_year": "2020", "gpa": "3.5",
                },
                "confidence": 0.92,
            })
        )
        yield mock

@pytest.fixture
def mock_ocr_unavailable():
    """Mock the OCR service to simulate a timeout/connection error."""
    with respx.mock(assert_all_called=False) as mock:
        mock.post("http://mock-ocr:5000/ocr").mock(side_effect=Exception("Connection refused"))
        yield mock

@pytest.fixture
def mock_odoo_success():
    """Mock Odoo auth + create endpoints."""
    with respx.mock(assert_all_called=False) as mock:
        mock.post("http://mock-odoo:8069/web/session/authenticate").mock(
            return_value=Response(200, json={
                "jsonrpc": "2.0", "result": {"uid": 2},
            })
        )
        mock.post("http://mock-odoo:8069/web/dataset/call_kw").mock(
            return_value=Response(200, json={
                "jsonrpc": "2.0", "result": 101,
            })
        )
        yield mock

@pytest.fixture
def mock_odoo_failure():
    """Mock Odoo to simulate a server error."""
    with respx.mock(assert_all_called=False) as mock:
        mock.post("http://mock-odoo:8069/web/session/authenticate").mock(
            return_value=Response(200, json={
                "jsonrpc": "2.0", "result": {"uid": 2},
            })
        )
        mock.post("http://mock-odoo:8069/web/dataset/call_kw").mock(
            return_value=Response(200, json={
                "jsonrpc": "2.0", "error": {"message": "Internal Server Error"},
            })
        )
        yield mock
