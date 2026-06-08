# -*- coding: utf-8 -*-
"""
Unit Tests: OCR Routes — Layer 1
Tests the FastAPI /ocr, /health endpoints with mocked OCR processing.
Target: services/ocr/app/routes.py
"""
import os
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

pytestmark = pytest.mark.unit


@pytest.fixture
def client(tmp_path):
    """Create a test client with mocked dependencies."""
    # Patch dependencies BEFORE importing the app
    with patch('app.services.detection_service.YOLO', MagicMock()), \
         patch('app.services.detection_service.os.path.exists', return_value=False), \
         patch('app.routes.UPLOAD_FOLDER', str(tmp_path)), \
         patch('app.routes.templates') as mock_templates:

            mock_templates.TemplateResponse.return_value = "<html>Mock</html>"

            from app import create_app
            app = create_app()

            yield TestClient(app)


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client):
        data = response = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["service"] == "ocr-microservice"


class TestOCREndpointValidation:
    """Tests for POST /ocr input validation."""

    def test_no_file_returns_422(self, client):
        """Missing file param returns 422 (FastAPI validation)."""
        response = client.post("/ocr")
        assert response.status_code == 422

    def test_invalid_extension_returns_400(self, client):
        """Non-image file should return 400."""
        response = client.post(
            "/ocr",
            files={"file": ("document.pdf", b"fake pdf content", "application/pdf")}
        )
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_empty_file_returns_400(self, client):
        """Empty file should return 400."""
        response = client.post(
            "/ocr",
            files={"file": ("empty.png", b"", "image/png")}
        )
        assert response.status_code == 400
        assert "Empty file" in response.json()["detail"]


class TestOCREndpointProcessing:
    """Tests for POST /ocr processing paths."""

    @patch('app.routes.process_uploaded_image')
    def test_successful_ocr_returns_200(self, mock_process, client, tmp_path):
        """Valid image with successful OCR returns 200 with result."""
        mock_process.return_value = {"name": "Ahmed", "nid": "12345"}

        with patch('app.routes.UPLOAD_FOLDER', str(tmp_path)):
            response = client.post(
                "/ocr",
                files={"file": ("id_card.jpg", b"\xff\xd8\xff\xe0fake_jpg", "image/jpeg")}
            )

        assert response.status_code == 200
        data = response.json()
        assert "result" in data
        assert data["result"]["name"] == "Ahmed"

    @patch('app.routes.process_uploaded_image')
    def test_ocr_error_result_returns_400(self, mock_process, client, tmp_path):
        """OCR processing that returns an error dict should return 400."""
        mock_process.return_value = {"error": "No ID card detected"}

        with patch('app.routes.UPLOAD_FOLDER', str(tmp_path)):
            response = client.post(
                "/ocr",
                files={"file": ("photo.png", b"\x89PNG\r\n\x1a\nfake", "image/png")}
            )

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"] == "No ID card detected"

    @patch('app.routes.process_uploaded_image')
    def test_ocr_exception_returns_500(self, mock_process, client, tmp_path):
        """Unexpected exception during processing should return 500."""
        mock_process.side_effect = RuntimeError("Unexpected GPU crash")

        with patch('app.routes.UPLOAD_FOLDER', str(tmp_path)):
            response = client.post(
                "/ocr",
                files={"file": ("card.jpg", b"\xff\xd8\xff\xe0fake_jpg", "image/jpeg")}
            )

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert "Processing failed" in data["error"]

    @patch('app.routes.process_uploaded_image')
    def test_uploaded_file_is_cleaned_up(self, mock_process, client, tmp_path):
        """Uploaded file should be removed after processing."""
        mock_process.return_value = {"name": "Test"}

        with patch('app.routes.UPLOAD_FOLDER', str(tmp_path)):
            client.post(
                "/ocr",
                files={"file": ("cleanup_test.jpg", b"\xff\xd8\xff\xe0fake", "image/jpeg")}
            )

        # After request, uploaded files should be cleaned up
        remaining = [f for f in os.listdir(tmp_path) if not f.startswith('.')]
        assert len(remaining) == 0, f"Files not cleaned up: {remaining}"
