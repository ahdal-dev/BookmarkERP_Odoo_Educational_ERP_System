# -*- coding: utf-8 -*-
"""
============================================================================
Unit Tests: JWT Helpers & RBAC — Layer 1
============================================================================
Tests JWT token creation, decoding, expiry detection, and RBACChecker
role enforcement. All tests run without network or database.

Target source: api_gateway/fastapi_app/main.py
  - RBACChecker class
  - generate_test_token endpoint logic
  - JWT_SECRET_KEY / JWT_ALGORITHM globals
============================================================================
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from fastapi import HTTPException

from main import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    RBACChecker,
    UserRole,
    TokenData,
)

pytestmark = pytest.mark.unit


# ============================================================================
# JWT Encoding / Decoding
# ============================================================================

class TestJWTEncoding:
    """Test JWT token encoding and decoding logic."""

    def test_encode_and_decode_roundtrip(self, valid_jwt_payload):
        """A token we encode should decode back to the same payload."""
        token = jwt.encode(valid_jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        assert decoded["user_id"] == valid_jwt_payload["user_id"]
        assert decoded["username"] == valid_jwt_payload["username"]
        assert decoded["email"] == valid_jwt_payload["email"]
        assert decoded["role"] == valid_jwt_payload["role"]

    def test_decode_with_wrong_secret_raises(self, valid_jwt_payload):
        """Decoding with the wrong secret key must raise."""
        token = jwt.encode(valid_jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        with pytest.raises(jwt.exceptions.InvalidSignatureError):
            jwt.decode(token, "wrong-secret-key", algorithms=[JWT_ALGORITHM])

    def test_decode_with_wrong_algorithm_raises(self, valid_jwt_payload):
        """Decoding with a mismatched algorithm must raise."""
        token = jwt.encode(valid_jwt_payload, JWT_SECRET_KEY, algorithm="HS256")

        with pytest.raises(jwt.exceptions.InvalidAlgorithmError):
            jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS384"])

    def test_malformed_token_raises(self):
        """A garbage string should not decode."""
        with pytest.raises(jwt.exceptions.DecodeError):
            jwt.decode("not.a.valid.token", JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


# ============================================================================
# JWT Expiry
# ============================================================================

class TestJWTExpiry:
    """Test JWT expiration handling."""

    def test_expired_token_raises(self, expired_jwt_payload):
        """Tokens with exp in the past should raise ExpiredSignatureError."""
        token = jwt.encode(expired_jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        with pytest.raises(jwt.exceptions.ExpiredSignatureError):
            jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

    def test_token_with_future_exp_is_valid(self, valid_jwt_payload):
        """Tokens with exp in the future should decode successfully."""
        token = jwt.encode(valid_jwt_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        decoded = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

        assert decoded["username"] == valid_jwt_payload["username"]

    def test_token_without_exp_decodes(self):
        """Tokens without exp should decode when leeway allows."""
        payload = {
            "user_id": 1,
            "username": "no_exp_user",
            "email": "noexp@example.com",
            "role": "admin",
        }
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        decoded = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM],
            options={"verify_exp": False}
        )
        assert decoded["username"] == "no_exp_user"


# ============================================================================
# RBACChecker
# ============================================================================

class TestRBACChecker:
    """Test the RBACChecker dependency class."""

    @pytest.fixture
    def mock_request(self):
        """Create a minimal mock FastAPI Request with no Redis state."""
        req = MagicMock()
        req.app.state.redis = None
        req.url.path = "/api/v1/test"
        return req

    @pytest.fixture
    def mock_credentials(self, valid_jwt_token):
        """Create mock HTTPAuthorizationCredentials for a prospective student."""
        creds = MagicMock()
        creds.credentials = valid_jwt_token
        return creds

    @pytest.fixture
    def mock_admin_credentials(self, admin_jwt_token):
        """Create mock HTTPAuthorizationCredentials for a super-admin."""
        creds = MagicMock()
        creds.credentials = admin_jwt_token
        return creds

    @pytest.fixture
    def mock_expired_credentials(self, expired_jwt_token):
        """Create mock expired HTTPAuthorizationCredentials."""
        creds = MagicMock()
        creds.credentials = expired_jwt_token
        return creds

    @pytest.mark.asyncio
    async def test_valid_student_with_allowed_role(self, mock_request, mock_credentials):
        """Prospective student token should pass when role is allowed."""
        checker = RBACChecker([UserRole.PROSPECTIVE_STUDENT, UserRole.SUPER_ADMIN])
        token_data = await checker(mock_request, mock_credentials)

        assert isinstance(token_data, TokenData)
        assert token_data.username == "test_student"
        assert token_data.role == UserRole.PROSPECTIVE_STUDENT

    @pytest.mark.asyncio
    async def test_admin_with_admin_only_role(self, mock_request, mock_admin_credentials):
        """Super-admin token should pass when super_admin role is required."""
        checker = RBACChecker([UserRole.SUPER_ADMIN])
        token_data = await checker(mock_request, mock_admin_credentials)

        assert token_data.role == UserRole.SUPER_ADMIN

    @pytest.mark.asyncio
    async def test_student_denied_admin_only_endpoint(self, mock_request, mock_credentials):
        """Student token should be rejected (403) on admin-only endpoints."""
        checker = RBACChecker([UserRole.SUPER_ADMIN])

        with pytest.raises(HTTPException) as exc_info:
            await checker(mock_request, mock_credentials)

        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self, mock_request):
        """A garbage token should trigger a 401 response."""
        creds = MagicMock()
        creds.credentials = "garbage.token.string"
        checker = RBACChecker([UserRole.PROSPECTIVE_STUDENT])

        with pytest.raises(HTTPException) as exc_info:
            await checker(mock_request, creds)

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_expired_token_returns_401(self, mock_request, mock_expired_credentials):
        """Expired tokens should trigger a 401 response."""
        checker = RBACChecker([UserRole.PROSPECTIVE_STUDENT])

        with pytest.raises(HTTPException) as exc_info:
            await checker(mock_request, mock_expired_credentials)

        assert exc_info.value.status_code == 401


# ============================================================================
# UserRole Enum
# ============================================================================

class TestUserRoleEnum:
    """Test the UserRole enum values."""

    def test_all_roles_exist(self):
        """All 9 canonical RBAC roles must be defined."""
        assert UserRole.PROSPECTIVE_STUDENT.value == "prospective_student"
        assert UserRole.ADMISSION_OFFICER.value  == "admission_officer"
        assert UserRole.STUDENT.value            == "student"
        assert UserRole.INSTRUCTOR.value         == "instructor"
        assert UserRole.ACADEMIC_ADVISOR.value   == "academic_advisor"
        assert UserRole.DEPARTMENT_CHAIR.value   == "department_chair"
        assert UserRole.REGISTRAR.value          == "registrar"
        assert UserRole.SUPPORT_TECHNICIAN.value == "support_technician"
        assert UserRole.SUPER_ADMIN.value        == "super_admin"

    def test_invalid_role_raises(self):
        """An unknown role string should raise ValueError."""
        with pytest.raises(ValueError):
            UserRole("nonexistent_role")
