# -*- coding: utf-8 -*-
"""
Unit Tests: Processing Service — Layer 1
Tests detect_id_card() and process_image() with mocked YOLO/cv2.
Target: services/ocr/app/services/processing_service.py
"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock, PropertyMock
import os

pytestmark = pytest.mark.unit


def _make_fake_image(h=200, w=300):
    return np.zeros((h, w, 3), dtype=np.uint8)


def _make_mock_box(x1, y1, x2, y2, class_id=0, class_name="name"):
    """Create a mock YOLO detection box."""
    box = MagicMock()
    box.xyxy = [MagicMock()]
    box.xyxy[0].tolist.return_value = [x1, y1, x2, y2]
    box.cls = [class_id]
    return box


def _make_mock_result(boxes=None, names=None):
    """Create a mock YOLO result object."""
    result = MagicMock()
    if boxes is None:
        result.boxes = None
    else:
        result.boxes = boxes
    result.names = names or {}
    return result


class TestDetectIdCard:
    """Tests for detect_id_card()."""

    @patch('app.services.processing_service.cv2')
    @patch('app.services.processing_service.os.path.exists', return_value=False)
    def test_returns_none_for_missing_image(self, mock_exists, mock_cv2):
        from app.services.processing_service import detect_id_card

        model = MagicMock()
        image, bboxes = detect_id_card("missing.png", model)

        assert image is None
        assert bboxes == []

    @patch('app.services.processing_service.cv2')
    @patch('app.services.processing_service.os.path.exists', return_value=True)
    def test_returns_none_when_cv2_cannot_read(self, mock_exists, mock_cv2):
        from app.services.processing_service import detect_id_card

        mock_cv2.imread.return_value = None
        model = MagicMock()
        model.return_value = []

        image, bboxes = detect_id_card("corrupt.png", model)

        assert image is None
        assert bboxes == []

    @patch('app.services.processing_service.cv2')
    @patch('app.services.processing_service.os.path.exists', return_value=True)
    def test_returns_image_and_bboxes_on_success(self, mock_exists, mock_cv2):
        from app.services.processing_service import detect_id_card

        fake_img = _make_fake_image()
        mock_cv2.imread.return_value = fake_img

        box = _make_mock_box(10, 20, 200, 150)
        result = _make_mock_result(boxes=[box])
        model = MagicMock(return_value=[result])

        image, bboxes = detect_id_card("test.png", model)

        assert image is not None
        assert len(bboxes) == 1
        assert bboxes[0] == [10, 20, 200, 150]

    @patch('app.services.processing_service.cv2')
    @patch('app.services.processing_service.os.path.exists', return_value=True)
    def test_returns_empty_bboxes_when_no_detection(self, mock_exists, mock_cv2):
        from app.services.processing_service import detect_id_card

        mock_cv2.imread.return_value = _make_fake_image()
        result = _make_mock_result(boxes=None)
        model = MagicMock(return_value=[result])

        image, bboxes = detect_id_card("no_card.png", model)

        assert image is not None
        assert bboxes == []

    @patch('app.services.processing_service.cv2')
    @patch('app.services.processing_service.os.path.exists', return_value=True)
    def test_handles_exception(self, mock_exists, mock_cv2):
        from app.services.processing_service import detect_id_card

        model = MagicMock(side_effect=RuntimeError("Model crash"))

        image, bboxes = detect_id_card("crash.png", model)

        assert image is None
        assert bboxes == []


class TestProcessImage:
    """Tests for process_image()."""

    @patch('app.services.processing_service.detect_id_card')
    def test_returns_error_when_image_none(self, mock_detect):
        from app.services.processing_service import process_image

        mock_detect.return_value = (None, [])
        model_id = MagicMock()
        model_job = MagicMock()

        result = process_image("test.png", model_id, model_job)

        assert "error" in result
        assert "Failed to read" in result["error"]

    @patch('app.services.processing_service.detect_id_card')
    def test_returns_error_when_no_id_card(self, mock_detect):
        from app.services.processing_service import process_image

        mock_detect.return_value = (_make_fake_image(), [])
        model_id = MagicMock()
        model_job = MagicMock()

        result = process_image("test.png", model_id, model_job)

        assert "error" in result
        assert "No ID card detected" in result["error"]

    @patch('app.services.processing_service.detect_id_card')
    def test_returns_error_for_invalid_bbox(self, mock_detect):
        from app.services.processing_service import process_image

        # Invalid bbox: x1 >= x2
        mock_detect.return_value = (_make_fake_image(), [[150, 10, 50, 100]])
        model_id = MagicMock()
        model_job = MagicMock()

        result = process_image("test.png", model_id, model_job)

        assert "error" in result
        assert "Invalid" in result["error"]

    @patch('app.services.processing_service.extract_text')
    @patch('app.services.processing_service.detect_id_card')
    def test_extracts_text_for_non_nid_fields(self, mock_detect, mock_extract):
        from app.services.processing_service import process_image

        fake_img = _make_fake_image(300, 400)
        mock_detect.return_value = (fake_img, [[10, 10, 280, 180]])

        # Mock model_job to return a "name" detection
        box = _make_mock_box(5, 5, 100, 30, class_id=0)
        result_obj = _make_mock_result(boxes=[box], names={0: "name"})
        model_job = MagicMock(return_value=[result_obj])
        model_id = MagicMock()

        mock_extract.return_value = "Ahmed Mohamed"

        result = process_image("test.png", model_id, model_job)

        assert "name" in result
        assert result["name"] == "Ahmed Mohamed"

    @patch('app.services.processing_service.nid_ocr')
    @patch('app.services.processing_service.cv2')
    @patch('app.services.processing_service.detect_id_card')
    def test_extracts_nid_for_nid_field(self, mock_detect, mock_cv2, mock_nid):
        from app.services.processing_service import process_image

        fake_img = _make_fake_image(300, 400)
        mock_detect.return_value = (fake_img, [[10, 10, 280, 180]])

        box = _make_mock_box(5, 5, 100, 30, class_id=0)
        result_obj = _make_mock_result(boxes=[box], names={0: "nid"})
        model_job = MagicMock(return_value=[result_obj])
        model_id = MagicMock()

        mock_cv2.imwrite.return_value = True
        mock_nid.return_value = "12345678901234"

        with patch('app.services.processing_service.os.path.exists', return_value=True), \
             patch('app.services.processing_service.os.remove'):
            result = process_image("test.png", model_id, model_job)

        assert "nid" in result
        assert result["nid"] == "12345678901234"

    @patch('app.services.processing_service.detect_id_card')
    def test_returns_error_when_no_text_extracted(self, mock_detect):
        from app.services.processing_service import process_image

        fake_img = _make_fake_image(300, 400)
        mock_detect.return_value = (fake_img, [[10, 10, 280, 180]])

        # model_job returns result with no boxes
        result_obj = _make_mock_result(boxes=None)
        model_job = MagicMock(return_value=[result_obj])
        model_id = MagicMock()

        result = process_image("test.png", model_id, model_job)

        assert "error" in result
        assert "No text extracted" in result["error"]

    @patch('app.services.processing_service.detect_id_card')
    def test_returns_error_on_exception(self, mock_detect):
        from app.services.processing_service import process_image

        mock_detect.side_effect = RuntimeError("Fatal error")
        model_id = MagicMock()
        model_job = MagicMock()

        result = process_image("test.png", model_id, model_job)

        assert "error" in result
        assert "Processing failed" in result["error"]

    @patch('app.services.processing_service.extract_text')
    @patch('app.services.processing_service.detect_id_card')
    def test_skips_invalid_inner_bbox(self, mock_detect, mock_extract):
        from app.services.processing_service import process_image

        fake_img = _make_fake_image(300, 400)
        mock_detect.return_value = (fake_img, [[10, 10, 280, 180]])

        # Invalid inner bbox (x1 >= x2)
        box = MagicMock()
        box.xyxy = [MagicMock()]
        box.xyxy[0].tolist.return_value = [100, 10, 50, 30]
        box.cls = [0]

        result_obj = _make_mock_result(boxes=[box], names={0: "name"})
        model_job = MagicMock(return_value=[result_obj])
        model_id = MagicMock()

        result = process_image("test.png", model_id, model_job)

        # Invalid bbox skipped → no text extracted → error
        assert "error" in result

    @patch('app.services.processing_service.extract_text')
    @patch('app.services.processing_service.detect_id_card')
    def test_handles_empty_text_result(self, mock_detect, mock_extract):
        from app.services.processing_service import process_image

        fake_img = _make_fake_image(300, 400)
        mock_detect.return_value = (fake_img, [[10, 10, 280, 180]])

        box = _make_mock_box(5, 5, 100, 30, class_id=0)
        result_obj = _make_mock_result(boxes=[box], names={0: "address"})
        model_job = MagicMock(return_value=[result_obj])
        model_id = MagicMock()

        mock_extract.return_value = ""

        result = process_image("test.png", model_id, model_job)

        assert "address" in result
        assert result["address"] == ""
