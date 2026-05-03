# -*- coding: utf-8 -*-
"""
Integration Tests: Auth/Token Endpoint — Layer 2
Tests /api/v1/auth/token via TestClient.
"""
import jwt
import pytest
from main import JWT_SECRET_KEY, JWT_ALGORITHM

pytestmark = pytest.mark.integration


class TestTokenGeneration:
    def test_generate_student_token(self, client):
        """Should generate a valid JWT for a prospective student."""
        response = client.post(
            "/api/v1/auth/token",
            params={"username": "test_student", "role": "prospective_student"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["token_type"] == "bearer"
        assert data["role"] == "prospective_student"
        # Verify the token is decodable
        decoded = jwt.decode(
            data["access_token"], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
        )
        assert decoded["username"] == "test_student"

    def test_generate_admin_token(self, client):
        response = client.post(
            "/api/v1/auth/token",
            params={"username": "admin_user", "role": "admin"},
        )
        assert response.status_code == 200
        assert response.json()["role"] == "admin"

    def test_generate_token_all_roles(self, client):
        """All UserRole values should produce valid tokens."""
        for role in ["prospective_student", "admission_staff", "admin", "system"]:
            resp = client.post(
                "/api/v1/auth/token",
                params={"username": f"user_{role}", "role": role},
            )
            assert resp.status_code == 200, f"Failed for role: {role}"

    def test_invalid_role_rejected(self, client):
        """An unrecognized role should return 422."""
        response = client.post(
            "/api/v1/auth/token",
            params={"username": "bad_user", "role": "superadmin"},
        )
        assert response.status_code == 422
