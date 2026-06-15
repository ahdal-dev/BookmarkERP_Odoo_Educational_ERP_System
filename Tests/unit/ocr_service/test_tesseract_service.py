# -*- coding: utf-8 -*-
"""
Unit Tests: Tesseract Service — Layer 1
Tests extract_text() with mocked cv2 and pytesseract.
Target: services/ocr/app/services/tesseract_service.py
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock

pytestmark = pytest.mark.unit


# Create a fake image (100x200 BGR)
def _make_fake_image(height=100, width=200):
    return np.zeros((height, width, 3), dtype=np.uint8)


class TestExtractText:
    """Tests for tesseract_service.extract_text()."""

    @patch('app.services.tesseract_service.pytesseract')
    @patch('app.services.tesseract_service.cv2')
    def test_returns_empty_for_none_image(self, mock_cv2, mock_tess):
        from app.services.tesseract_service import extract_text

        result = extract_text(None, [0, 0, 50, 50])
        assert result == ""

    @patch('app.services.tesseract_service.pytesseract')
    @patch('app.services.tesseract_service.cv2')
    def test_returns_empty_for_empty_image(self, mock_cv2, mock_tess):
        from app.services.tesseract_service import extract_text

        empty_img = np.array([], dtype=np.uint8)
        result = extract_text(empty_img, [0, 0, 50, 50])
        assert result == ""

    @patch('app.services.tesseract_service.pytesseract')
    @patch('app.services.tesseract_service.cv2')
    def test_returns_empty_for_invalid_bbox(self, mock_cv2, mock_tess):
        from app.services.tesseract_service import extract_text

        img = _make_fake_image()
        # x1 >= x2 → invalid
        result = extract_text(img, [100, 0, 50, 50])
        assert result == ""

    @patch('app.services.tesseract_service.pytesseract')
    @patch('app.services.tesseract_service.cv2')
    def test_returns_empty_for_inverted_y_bbox(self, mock_cv2, mock_tess):
        from app.services.tesseract_service import extract_text

        img = _make_fake_image()
        # y1 >= y2 → invalid
        result = extract_text(img, [0, 80, 50, 10])
        assert result == ""

    @patch('app.services.tesseract_service.pytesseract')
    @patch('app.services.tesseract_service.cv2')
    def test_successful_text_extraction(self, mock_cv2, mock_tess):
        from app.services.tesseract_service import extract_text

        img = _make_fake_image(100, 200)
        cropped = _make_fake_image(50, 50)
        gray = np.zeros((50, 50), dtype=np.uint8)
        thresh = np.zeros((50, 50), dtype=np.uint8)

        # Mock cv2 pipeline
        mock_cv2.cvtColor.return_value = gray
        mock_cv2.threshold.return_value = (127, thresh)

        mock_tess.image_to_string.return_value = "  Ahmed Mohamed  "

        result = extract_text(img, [10, 10, 60, 60])

        assert result == "Ahmed Mohamed"
        mock_tess.image_to_string.assert_called_once()

    @patch('app.services.tesseract_service.pytesseract')
    @patch('app.services.tesseract_service.cv2')
    def test_returns_empty_when_cropped_image_is_empty(self, mock_cv2, mock_tess):
        from app.services.tesseract_service import extract_text

        # Create image where crop coordinates result in empty slice
        img = _make_fake_image(10, 10)
        # bbox is clamped to image bounds: max(0,0)=0 to min(10,5)=5 → valid
        # But then cropped_image.size == 0 if the crop slice is somehow empty
        # We need to test the empty crop path

        mock_cv2.cvtColor.side_effect = Exception("empty image")

        result = extract_text(img, [0, 0, 5, 5])
        # Should catch the exception and return ""
        assert result == ""

    @patch('app.services.tesseract_service.pytesseract')
    @patch('app.services.tesseract_service.cv2')
    def test_returns_empty_on_tesseract_exception(self, mock_cv2, mock_tess):
        from app.services.tesseract_service import extract_text

        img = _make_fake_image()
        mock_cv2.cvtColor.return_value = np.zeros((50, 50), dtype=np.uint8)
        mock_cv2.threshold.return_value = (127, np.zeros((50, 50), dtype=np.uint8))
        mock_tess.image_to_string.side_effect = RuntimeError("Tesseract not found")

        result = extract_text(img, [10, 10, 60, 60])
        assert result == ""

    @patch('app.services.tesseract_service.pytesseract')
    @patch('app.services.tesseract_service.cv2')
    def test_bbox_clamped_to_image_bounds(self, mock_cv2, mock_tess):
        from app.services.tesseract_service import extract_text

        img = _make_fake_image(50, 50)
        mock_cv2.cvtColor.return_value = np.zeros((50, 50), dtype=np.uint8)
        mock_cv2.threshold.return_value = (127, np.zeros((50, 50), dtype=np.uint8))
        mock_tess.image_to_string.return_value = "Test"

        # bbox extends beyond image bounds
        result = extract_text(img, [-10, -10, 100, 100])
        assert result == "Test"

    @patch('app.services.tesseract_service.pytesseract')
    @patch('app.services.tesseract_service.cv2')
    def test_custom_language(self, mock_cv2, mock_tess):
        from app.services.tesseract_service import extract_text

        img = _make_fake_image()
        mock_cv2.cvtColor.return_value = np.zeros((50, 50), dtype=np.uint8)
        mock_cv2.threshold.return_value = (127, np.zeros((50, 50), dtype=np.uint8))
        mock_tess.image_to_string.return_value = "English Text"

        result = extract_text(img, [10, 10, 60, 60], lang='eng')
        assert result == "English Text"
        # Verify the language was passed to tesseract
        call_kwargs = mock_tess.image_to_string.call_args
        assert call_kwargs[1]['lang'] == 'eng'
