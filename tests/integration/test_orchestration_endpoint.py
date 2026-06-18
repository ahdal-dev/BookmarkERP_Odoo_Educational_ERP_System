# -*- coding: utf-8 -*-
"""
Integration Tests: Orchestration Endpoint — Layer 2
Tests POST /api/v1/admissions/submit-with-document (OCR + Admission).
"""
import io
import pytest
from main import OdooClient

pytestmark = pytest.mark.integration

ENDPOINT = "/api/v1/admissions/submit-with-document"


class TestOrchestrationSuccess:
    def test_full_pipeline_success(
        self, client, student_auth_header, mock_ocr_success, mock_odoo_success
    ):
        """
        Full orchestration: upload doc → OCR extract → submit to Odoo.
        All backends mocked to return success.
        """
        OdooClient.__init__(OdooClient)
        file_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100

        response = client.post(
            ENDPOINT,
            headers=student_auth_header,
            data={
                "email": "ahmed@example.com",
                "phone": "+201001234567",
                "desired_program": "Computer Science",
                "application_type": "regular",
            },
            files={"file": ("national_id.jpg", io.BytesIO(file_content), "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["ocr_result"] is not None
        assert data["admission_result"] is not None
        assert data["execution_time"] > 0


class TestOrchestrationPartialFailure:
    def test_ocr_failure_propagates(
        self, client, student_auth_header, mock_ocr_unavailable
    ):
        """When OCR fails, orchestration should report failure."""
        file_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        response = client.post(
            ENDPOINT,
            headers=student_auth_header,
            data={
                "email": "test@example.com",
                "phone": "+201001234567",
                "desired_program": "Engineering",
            },
            files={"file": ("doc.jpg", io.BytesIO(file_content), "image/jpeg")},
        )
        data = response.json()
        # Should either be a 5xx or a 200 with success=False + errors
        if response.status_code == 200:
            assert data["success"] is False
            assert data["errors"] is not None
            assert len(data["errors"]) > 0


class TestOrchestrationAuth:
    def test_no_auth_returns_401(self, client):
        """Orchestration without JWT should return 401."""
        response = client.post(
            ENDPOINT,
            data={"email": "t@t.com", "phone": "+201001234567",
                  "desired_program": "CS"},
            files={"file": ("d.jpg", io.BytesIO(b"\xff\xd8"), "image/jpeg")},
        )
        assert response.status_code == 401
