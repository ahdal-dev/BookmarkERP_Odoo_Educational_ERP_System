# -*- coding: utf-8 -*-
"""
Integration Tests: Admission Application Endpoint — Layer 2
Tests POST /api/v1/admissions/apply via TestClient with mocked Odoo.
"""
import pytest
from main import OdooClient

pytestmark = pytest.mark.integration

ENDPOINT = "/api/v1/admissions/apply"

VALID_APPLICATION = {
    "full_name": "Ahmed Mohamed Hassan",
    "national_id": "29901011234567",
    "email": "ahmed@example.com",
    "phone": "+201001234567",
    "date_of_birth": "2000-01-15T00:00:00",
    "address": "123 Tahrir Street, Downtown Cairo, Egypt",
    "city": "Cairo",
    "country": "Egypt",
    "previous_qualification": "High School Diploma",
    "graduation_year": 2020,
    "gpa": 3.75,
    "desired_program": "Computer Science",
    "application_type": "regular",
}


class TestAdmissionSubmitSuccess:
    def test_valid_submission_returns_200(
        self, client, student_auth_header, mock_odoo_success
    ):
        """Valid application data should create an admission record."""
        # Reset cached uid so the mock auth is used
        OdooClient.__init__(OdooClient)
        response = client.post(
            ENDPOINT, json=VALID_APPLICATION, headers=student_auth_header,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["application_id"] == 101
        assert data["status"] == "draft"
        assert isinstance(data["next_steps"], list)

    def test_admin_can_submit(self, client, admin_auth_header, mock_odoo_success):
        """Admin role should also be allowed to submit applications."""
        OdooClient.__init__(OdooClient)
        response = client.post(
            ENDPOINT, json=VALID_APPLICATION, headers=admin_auth_header,
        )
        assert response.status_code == 200


class TestAdmissionSubmitValidation:
    def test_missing_required_field_returns_422(self, client, student_auth_header):
        """Missing full_name should return 422 Unprocessable Entity."""
        bad_data = VALID_APPLICATION.copy()
        del bad_data["full_name"]
        response = client.post(
            ENDPOINT, json=bad_data, headers=student_auth_header,
        )
        assert response.status_code == 422

    def test_invalid_national_id_returns_422(self, client, student_auth_header):
        """NID that doesn't match the 14-digit pattern should fail."""
        bad_data = VALID_APPLICATION.copy()
        bad_data["national_id"] = "123"
        response = client.post(
            ENDPOINT, json=bad_data, headers=student_auth_header,
        )
        assert response.status_code == 422

    def test_invalid_gpa_returns_422(self, client, student_auth_header):
        """GPA above 4.0 should fail validation."""
        bad_data = VALID_APPLICATION.copy()
        bad_data["gpa"] = 5.0
        response = client.post(
            ENDPOINT, json=bad_data, headers=student_auth_header,
        )
        assert response.status_code == 422


class TestAdmissionSubmitAuth:
    def test_no_auth_returns_403(self, client):
        response = client.post(ENDPOINT, json=VALID_APPLICATION)
        assert response.status_code == 403


class TestAdmissionBackendFailure:
    def test_odoo_error_returns_500(
        self, client, student_auth_header, mock_odoo_failure
    ):
        """When Odoo returns an error, should propagate as 500."""
        OdooClient.__init__(OdooClient)
        response = client.post(
            ENDPOINT, json=VALID_APPLICATION, headers=student_auth_header,
        )
        assert response.status_code == 500
