# -*- coding: utf-8 -*-
"""
============================================================================
Unit Test Fixtures — Layer 1
============================================================================
Provides mock objects and sample data for unit tests.
All external dependencies (HTTP, database, Odoo) are mocked here.
No network calls, no database, no Docker required.
============================================================================
"""

import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import jwt


# ============================================================================
# Ensure deterministic env vars for all unit tests
# ============================================================================

# Set BEFORE any application imports so module-level globals pick them up
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-production")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_HOURS", "1")
os.environ.setdefault("OCR_SERVICE_URL", "http://mock-ocr:5000")
os.environ.setdefault("ODOO_URL", "http://mock-odoo:8069")
os.environ.setdefault("ODOO_DB", "test_db")
os.environ.setdefault("ODOO_USERNAME", "admin")
os.environ.setdefault("ODOO_PASSWORD", "admin")


# ============================================================================
# JWT Token Fixtures
# ============================================================================

JWT_SECRET = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]


@pytest.fixture
def valid_jwt_payload():
    """Return a valid JWT payload dict for a prospective student."""
    return {
        "user_id": 42,
        "username": "test_student",
        "email": "test_student@example.com",
        "role": "prospective_student",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }


@pytest.fixture
def admin_jwt_payload():
    """Return a valid JWT payload dict for a super-admin user."""
    return {
        "user_id": 1,
        "username": "admin_user",
        "email": "admin@example.com",
        "role": "super_admin",
        "exp": datetime.utcnow() + timedelta(hours=1),
    }


@pytest.fixture
def expired_jwt_payload():
    """Return an expired JWT payload (exp in the past)."""
    return {
        "user_id": 42,
        "username": "expired_user",
        "email": "expired@example.com",
        "role": "prospective_student",
        "exp": datetime.utcnow() - timedelta(hours=1),
    }


@pytest.fixture
def valid_jwt_token(valid_jwt_payload):
    """Return an encoded JWT token string for a prospective student."""
    return jwt.encode(valid_jwt_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@pytest.fixture
def admin_jwt_token(admin_jwt_payload):
    """Return an encoded JWT token string for an admin."""
    return jwt.encode(admin_jwt_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@pytest.fixture
def expired_jwt_token(expired_jwt_payload):
    """Return an encoded but expired JWT token string."""
    return jwt.encode(expired_jwt_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# ============================================================================
# Sample Application Data Fixtures
# ============================================================================

@pytest.fixture
def sample_admission_data():
    """Return a dict matching AdmissionApplicationData schema."""
    return {
        "full_name": "Ahmed Mohamed Hassan",
        "national_id": "29901011234567",
        "email": "ahmed.hassan@example.com",
        "phone": "+201234567890",
        "date_of_birth": "2000-01-15T00:00:00",
        "address": "123 Tahrir Street, Downtown Cairo, Egypt",
        "city": "Cairo",
        "country": "Egypt",
        "previous_qualification": "High School Diploma (Thanaweya Amma)",
        "graduation_year": 2020,
        "gpa": 3.75,
        "desired_program": "Computer Science",
        "application_type": "regular",
    }


@pytest.fixture
def sample_ocr_response():
    """Return a mock OCR service response payload."""
    return {
        "result": {
            "name": "Ahmed Mohamed Hassan",
            "nid": "29901011234567",
            "date_of_birth": "2000-01-15",
            "address": "123 Tahrir Street, Downtown Cairo",
            "city": "Cairo",
            "qualification": "High School Diploma",
            "graduation_year": "2020",
            "gpa": "3.75",
        },
        "confidence": 0.95,
    }


@pytest.fixture
def sample_odoo_auth_response():
    """Return a mock Odoo authentication response."""
    return {
        "jsonrpc": "2.0",
        "result": {
            "uid": 2,
            "session_id": "fake-session-id-12345",
        },
    }


@pytest.fixture
def sample_odoo_create_response():
    """Return a mock Odoo record creation response."""
    return {
        "jsonrpc": "2.0",
        "result": 101,  # Created record ID
    }


# ============================================================================
# HTTP Client Mocks
# ============================================================================

@pytest.fixture
def mock_httpx_client():
    """
    Provide a mock httpx.AsyncClient for patching network calls.

    Usage in tests:
        async with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            ...
    """
    client = AsyncMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    return client
