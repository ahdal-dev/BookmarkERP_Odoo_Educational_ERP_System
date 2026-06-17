# -*- coding: utf-8 -*-
"""
Integration Tests: Auth/Token Endpoint — Layer 2
Tests /api/v1/auth/token via TestClient.
"""
import jwt
import pytest
from unittest.mock import patch

import main
from main import JWT_SECRET_KEY, JWT_ALGORITHM

pytestmark = pytest.mark.integration

_VALID_ROLES = [
    "prospective_student",
    "admission_officer",
    "student",
    "instructor",
    "academic_advisor",
    "department_chair",
    "registrar",
    "support_technician",
    "super_admin",
]


class TestTokenGeneration:
    def test_generate_student_token(self, client):
        """Should generate a valid JWT for a prospective student when enabled."""
        with patch.object(main, "ENABLE_TEST_TOKENS", True):
            response = client.post(
                "/api/v1/auth/token",
                params={"username": "test_student", "role": "prospective_student"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["role"] == "prospective_student"
        decoded = jwt.decode(
            data["access_token"], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
        assert decoded["username"] == "test_student"

    def test_generate_super_admin_token(self, client):
        with patch.object(main, "ENABLE_TEST_TOKENS", True):
            response = client.post(
                "/api/v1/auth/token",
                params={"username": "admin_user", "role": "super_admin"},
            )
        assert response.status_code == 200
        assert response.json()["role"] == "super_admin"

    def test_generate_token_all_roles(self, client):
        """All UserRole values should produce valid tokens when the endpoint is enabled."""
        with patch.object(main, "ENABLE_TEST_TOKENS", True):
            for role in _VALID_ROLES:
                resp = client.post(
                    "/api/v1/auth/token",
                    params={"username": f"user_{role}", "role": role},
                )
                assert resp.status_code == 200, f"Failed for role: {role}"

    def test_endpoint_disabled_by_default(self, client):
        """Without ENABLE_TEST_TOKENS the endpoint must return 403."""
        with patch.object(main, "ENABLE_TEST_TOKENS", False):
            response = client.post(
                "/api/v1/auth/token",
                params={"username": "any", "role": "prospective_student"},
            )
        assert response.status_code == 403

    def test_invalid_role_rejected(self, client):
        """An unrecognised role string should return 422 (enum validation)."""
        with patch.object(main, "ENABLE_TEST_TOKENS", True):
            response = client.post(
                "/api/v1/auth/token",
                params={"username": "bad_user", "role": "superadmin"},
            )
        assert response.status_code == 422
