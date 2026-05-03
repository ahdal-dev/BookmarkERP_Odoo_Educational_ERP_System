# -*- coding: utf-8 -*-
"""
Integration Tests: OCR Document Extraction Endpoint — Layer 2
Tests POST /api/v1/extract-document via TestClient with mocked OCR backend.
"""
import io
import pytest

pytestmark = pytest.mark.integration

ENDPOINT = "/api/v1/extract-document"


class TestExtractDocumentSuccess:
    def test_valid_jpeg_upload(self, client, student_auth_header, mock_ocr_success):
        """Valid JPEG upload should return OCR extraction results."""
        file_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # Minimal JPEG header
        response = client.post(
            ENDPOINT,
            headers=student_auth_header,
            files={"file": ("test_id.jpg", io.BytesIO(file_content), "image/jpeg")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "extracted_data" in data
        assert data["extracted_data"]["name"] == "Ahmed Hassan"

    def test_valid_png_upload(self, client, admin_auth_header, mock_ocr_success):
        """Admin should also be able to upload documents."""
        file_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        response = client.post(
            ENDPOINT,
            headers=admin_auth_header,
            files={"file": ("scan.png", io.BytesIO(file_content), "image/png")},
        )
        assert response.status_code == 200


class TestExtractDocumentValidation:
    def test_invalid_file_type_returns_400(self, client, student_auth_header):
        """Uploading a .txt file should return 400."""
        response = client.post(
            ENDPOINT,
            headers=student_auth_header,
            files={"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")},
        )
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_oversized_file_returns_413(self, client, student_auth_header):
        """File over 10MB should return 413."""
        big_file = b"\x00" * (10 * 1024 * 1024 + 1)
        response = client.post(
            ENDPOINT,
            headers=student_auth_header,
            files={"file": ("huge.jpg", io.BytesIO(big_file), "image/jpeg")},
        )
        assert response.status_code == 413


class TestExtractDocumentAuth:
    def test_missing_jwt_returns_403(self, client):
        """Request without Authorization header should return 403."""
        response = client.post(
            ENDPOINT,
            files={"file": ("test.jpg", io.BytesIO(b"\xff\xd8"), "image/jpeg")},
        )
        assert response.status_code == 403

    def test_invalid_jwt_returns_401(self, client):
        """Garbage JWT token should return 401."""
        response = client.post(
            ENDPOINT,
            headers={"Authorization": "Bearer garbage.token.here"},
            files={"file": ("test.jpg", io.BytesIO(b"\xff\xd8"), "image/jpeg")},
        )
        assert response.status_code == 401


class TestExtractDocumentBackendFailure:
    def test_ocr_service_unavailable_returns_error(
        self, client, student_auth_header, mock_ocr_unavailable
    ):
        """When OCR service is down, should return 5xx or error response."""
        file_content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
        response = client.post(
            ENDPOINT,
            headers=student_auth_header,
            files={"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")},
        )
        # Should be 503 or 500 depending on error handling
        assert response.status_code >= 500
