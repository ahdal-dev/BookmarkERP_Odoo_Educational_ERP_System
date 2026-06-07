# -*- coding: utf-8 -*-
"""
Unit Tests: OCR Controller — Layer 1
Tests process_uploaded_image() with mocked model dependencies.
Target: services/ocr/app/controllers/ocr_controller.py
"""
import pytest
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.unit


class TestProcessUploadedImage:
    """Test the OCR controller's process_uploaded_image function."""

    @patch('app.controllers.ocr_controller.model_id_card', None)
    @patch('app.controllers.ocr_controller.model_job', MagicMock())
    def test_returns_error_when_id_card_model_is_none(self):
        """Should return error dict when ID card model is not loaded."""
        from app.controllers.ocr_controller import process_uploaded_image

        result = process_uploaded_image("fake_image.png")

        assert isinstance(result, dict)
        assert "error" in result
        assert "ID card detection model" in result["error"]

    @patch('app.controllers.ocr_controller.model_id_card', MagicMock())
    @patch('app.controllers.ocr_controller.model_job', None)
    def test_returns_error_when_job_model_is_none(self):
        """Should return error dict when object detection model is not loaded."""
        from app.controllers.ocr_controller import process_uploaded_image

        result = process_uploaded_image("fake_image.png")

        assert isinstance(result, dict)
        assert "error" in result
        assert "Object detection model" in result["error"]

    @patch('app.controllers.ocr_controller.process_image')
    @patch('app.controllers.ocr_controller.model_job', MagicMock())
    @patch('app.controllers.ocr_controller.model_id_card', MagicMock())
    def test_returns_result_on_success(self, mock_process):
        """Should return process_image result when both models loaded."""
        from app.controllers.ocr_controller import process_uploaded_image

        expected = {"name": "John Doe", "nid": "12345678901234"}
        mock_process.return_value = expected

        result = process_uploaded_image("test_image.png")

        assert result == expected
        mock_process.assert_called_once()

    @patch('app.controllers.ocr_controller.process_image')
    @patch('app.controllers.ocr_controller.model_job', MagicMock())
    @patch('app.controllers.ocr_controller.model_id_card', MagicMock())
    def test_returns_error_on_exception(self, mock_process):
        """Should catch exceptions and return error dict."""
        from app.controllers.ocr_controller import process_uploaded_image

        mock_process.side_effect = RuntimeError("GPU memory error")

        result = process_uploaded_image("test_image.png")

        assert isinstance(result, dict)
        assert "error" in result
        assert "Failed to process image" in result["error"]

    @patch('app.controllers.ocr_controller.process_image')
    @patch('app.controllers.ocr_controller.model_job', MagicMock())
    @patch('app.controllers.ocr_controller.model_id_card', MagicMock())
    def test_returns_error_dict_from_process_image(self, mock_process):
        """Should pass through error dicts from process_image."""
        from app.controllers.ocr_controller import process_uploaded_image

        mock_process.return_value = {"error": "No ID card detected"}

        result = process_uploaded_image("test_image.png")

        assert result == {"error": "No ID card detected"}
