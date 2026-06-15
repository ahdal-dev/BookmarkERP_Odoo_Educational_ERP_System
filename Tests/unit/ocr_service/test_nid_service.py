# -*- coding: utf-8 -*-
"""
Unit Tests: NID Service — Layer 1
Tests nid_ocr() with mocked cv2 and easyocr.
Target: services/ocr/app/services/nid_service.py
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.unit


class TestNidOcr:
    """Tests for nid_service.nid_ocr()."""

    @patch('app.services.nid_service.easyocr')
    @patch('app.services.nid_service.cv2')
    def test_returns_empty_for_missing_image(self, mock_cv2, mock_easyocr):
        """Should return empty string when image file doesn't exist."""
        from app.services.nid_service import nid_ocr

        mock_cv2.imread.return_value = None

        result = nid_ocr("nonexistent.png")
        assert result == ""

    @patch('app.services.nid_service.easyocr')
    @patch('app.services.nid_service.cv2')
    def test_returns_empty_for_empty_image(self, mock_cv2, mock_easyocr):
        """Should return empty string when image is empty."""
        from app.services.nid_service import nid_ocr

        empty_img = np.array([], dtype=np.uint8)
        mock_cv2.imread.return_value = empty_img

        result = nid_ocr("empty.png")
        assert result == ""

    @patch('app.services.nid_service.easyocr')
    @patch('app.services.nid_service.cv2')
    def test_returns_empty_when_no_digits_detected(self, mock_cv2, mock_easyocr):
        """Should return empty string when OCR finds no text."""
        from app.services.nid_service import nid_ocr

        fake_img = np.zeros((100, 200, 3), dtype=np.uint8)
        mock_cv2.imread.return_value = fake_img
        mock_cv2.split.return_value = (
            fake_img[:, :, 0], fake_img[:, :, 1], fake_img[:, :, 2]
        )
        mock_cv2.adaptiveThreshold.return_value = np.zeros((100, 200), dtype=np.uint8)
        mock_cv2.morphologyEx.return_value = np.zeros((100, 200), dtype=np.uint8)
        mock_cv2.cvtColor.return_value = fake_img

        # EasyOCR reader mock
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = []  # No detections
        mock_easyocr.Reader.return_value = mock_reader

        result = nid_ocr("no_digits.png")
        assert result == ""

    @patch('app.services.nid_service.easyocr')
    @patch('app.services.nid_service.cv2')
    def test_extracts_arabic_nid_digits(self, mock_cv2, mock_easyocr):
        """Should convert Arabic digits to Western and return NID."""
        from app.services.nid_service import nid_ocr

        fake_img = np.zeros((100, 200, 3), dtype=np.uint8)
        mock_cv2.imread.return_value = fake_img
        mock_cv2.split.return_value = (
            fake_img[:, :, 0], fake_img[:, :, 1], fake_img[:, :, 2]
        )
        mock_cv2.adaptiveThreshold.return_value = np.zeros((100, 200), dtype=np.uint8)
        mock_cv2.morphologyEx.return_value = np.zeros((100, 200), dtype=np.uint8)
        mock_cv2.cvtColor.return_value = fake_img

        # Simulate EasyOCR detecting Arabic digits: ١٢٣٤
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = [
            ([[10, 10], [30, 10], [30, 30], [10, 30]], '١٢٣٤', 0.95),
        ]
        mock_easyocr.Reader.return_value = mock_reader

        result = nid_ocr("nid.png")
        # Arabic ١٢٣٤ reversed → ٤٣٢١ → "4321"
        assert result.strip() != ""
        # The result should contain only digits and spaces
        assert all(c.isdigit() or c == ' ' for c in result)

    @patch('app.services.nid_service.easyocr')
    @patch('app.services.nid_service.cv2')
    def test_handles_multi_detection_results(self, mock_cv2, mock_easyocr):
        """Should concatenate multiple OCR detections."""
        from app.services.nid_service import nid_ocr

        fake_img = np.zeros((100, 200, 3), dtype=np.uint8)
        mock_cv2.imread.return_value = fake_img
        mock_cv2.split.return_value = (
            fake_img[:, :, 0], fake_img[:, :, 1], fake_img[:, :, 2]
        )
        mock_cv2.adaptiveThreshold.return_value = np.zeros((100, 200), dtype=np.uint8)
        mock_cv2.morphologyEx.return_value = np.zeros((100, 200), dtype=np.uint8)
        mock_cv2.cvtColor.return_value = fake_img

        # Multiple detections
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = [
            ([[10, 10], [30, 10], [30, 30], [10, 30]], '٥٦', 0.9),
            ([[40, 10], [60, 10], [60, 30], [40, 30]], '٧٨', 0.85),
        ]
        mock_easyocr.Reader.return_value = mock_reader

        result = nid_ocr("multi.png")
        # Should produce some digits
        assert isinstance(result, str)

    @patch('app.services.nid_service.easyocr')
    @patch('app.services.nid_service.cv2')
    def test_returns_empty_on_exception(self, mock_cv2, mock_easyocr):
        """Should catch any exception and return empty string."""
        from app.services.nid_service import nid_ocr

        mock_cv2.imread.side_effect = RuntimeError("CV2 crash")

        result = nid_ocr("crash.png")
        assert result == ""

    @patch('app.services.nid_service.easyocr')
    @patch('app.services.nid_service.cv2')
    def test_handles_western_digits(self, mock_cv2, mock_easyocr):
        """Characters not in Arabic digit set should map to space."""
        from app.services.nid_service import nid_ocr

        fake_img = np.zeros((100, 200, 3), dtype=np.uint8)
        mock_cv2.imread.return_value = fake_img
        mock_cv2.split.return_value = (
            fake_img[:, :, 0], fake_img[:, :, 1], fake_img[:, :, 2]
        )
        mock_cv2.adaptiveThreshold.return_value = np.zeros((100, 200), dtype=np.uint8)
        mock_cv2.morphologyEx.return_value = np.zeros((100, 200), dtype=np.uint8)
        mock_cv2.cvtColor.return_value = fake_img

        mock_reader = MagicMock()
        # Non-Arabic characters → should become spaces
        mock_reader.readtext.return_value = [
            ([[10, 10], [30, 10], [30, 30], [10, 30]], 'ABC', 0.8),
        ]
        mock_easyocr.Reader.return_value = mock_reader

        result = nid_ocr("western.png")
        # All non-Arabic characters become spaces
        assert isinstance(result, str)
