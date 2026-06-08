# -*- coding: utf-8 -*-
"""
Unit Tests: OCR File Validation — Layer 1
Tests the allowed_file() helper from the OCR service.
Target: services/ocr/app/routes.py
"""
import pytest
from app.routes import allowed_file, ALLOWED_EXTENSIONS

pytestmark = pytest.mark.unit


class TestAllowedFile:
    """Test the OCR file extension validation helper."""

    @pytest.mark.parametrize("filename,expected", [
        ("document.png", True),
        ("photo.jpg", True),
        ("photo.jpeg", True),
        ("scan.bmp", True),
        ("scan.tiff", True),
        ("image.webp", True),
        ("PHOTO.PNG", True),       # Case insensitive
        ("My.Photo.JPG", True),    # Multiple dots
    ])
    def test_valid_extensions(self, filename, expected):
        assert allowed_file(filename) == expected

    @pytest.mark.parametrize("filename", [
        "document.pdf",
        "archive.zip",
        "script.py",
        "readme.txt",
        "malware.exe",
        "noextension",
        "",
    ])
    def test_invalid_extensions(self, filename):
        assert allowed_file(filename) is False

    def test_allowed_extensions_constant(self):
        """Verify the set of allowed extensions hasn't changed unexpectedly."""
        assert ALLOWED_EXTENSIONS == {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'}
