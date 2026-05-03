# -*- coding: utf-8 -*-
"""
============================================================================
Unit Tests: Pydantic Models — Layer 1
============================================================================
Tests schema validation for all Pydantic request/response models.
Verifies field constraints, regex patterns, and custom validators.

Target source: api_gateway/fastapi_app/main.py
  - AdmissionApplicationData
  - OCRResponse
  - AdmissionResponse
  - OrchestrationRequest / OrchestrationResponse
============================================================================
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from main import (
    AdmissionApplicationData,
    OCRResponse,
    AdmissionResponse,
    OrchestrationRequest,
    OrchestrationResponse,
)

pytestmark = pytest.mark.unit


# ============================================================================
# AdmissionApplicationData Validation
# ============================================================================

class TestAdmissionApplicationData:
    """Test the main admission application schema."""

    def test_valid_data_passes(self, sample_admission_data):
        """Valid Egyptian applicant data should parse without errors."""
        app = AdmissionApplicationData(**sample_admission_data)

        assert app.full_name == "Ahmed Mohamed Hassan"
        assert app.national_id == "29901011234567"
        assert app.gpa == 3.75
        assert app.country == "Egypt"

    # ── National ID validation ──────────────────────────────────────────────

    def test_national_id_must_be_14_digits(self, sample_admission_data):
        """Egyptian NID must be exactly 14 digits."""
        data = sample_admission_data.copy()
        data["national_id"] = "123"  # Too short

        with pytest.raises(ValidationError) as exc_info:
            AdmissionApplicationData(**data)

        assert "national_id" in str(exc_info.value)

    def test_national_id_rejects_letters(self, sample_admission_data):
        """NID with letters should fail the ^\d{14}$ regex."""
        data = sample_admission_data.copy()
        data["national_id"] = "2990101123456A"

        with pytest.raises(ValidationError):
            AdmissionApplicationData(**data)

    def test_national_id_14_digits_passes(self, sample_admission_data):
        """Exactly 14 digits should be accepted."""
        data = sample_admission_data.copy()
        data["national_id"] = "12345678901234"

        app = AdmissionApplicationData(**data)
        assert app.national_id == "12345678901234"

    # ── GPA boundaries ──────────────────────────────────────────────────────

    def test_gpa_zero_is_valid(self, sample_admission_data):
        """GPA of 0.0 (minimum) should be accepted."""
        data = sample_admission_data.copy()
        data["gpa"] = 0.0

        app = AdmissionApplicationData(**data)
        assert app.gpa == 0.0

    def test_gpa_four_is_valid(self, sample_admission_data):
        """GPA of 4.0 (maximum) should be accepted."""
        data = sample_admission_data.copy()
        data["gpa"] = 4.0

        app = AdmissionApplicationData(**data)
        assert app.gpa == 4.0

    def test_gpa_negative_rejected(self, sample_admission_data):
        """Negative GPA should fail ge=0.0 constraint."""
        data = sample_admission_data.copy()
        data["gpa"] = -0.1

        with pytest.raises(ValidationError) as exc_info:
            AdmissionApplicationData(**data)

        assert "gpa" in str(exc_info.value).lower()

    def test_gpa_above_four_rejected(self, sample_admission_data):
        """GPA > 4.0 should fail le=4.0 constraint."""
        data = sample_admission_data.copy()
        data["gpa"] = 4.01

        with pytest.raises(ValidationError):
            AdmissionApplicationData(**data)

    # ── Graduation year validator ───────────────────────────────────────────

    def test_graduation_year_in_past_is_valid(self, sample_admission_data):
        """A past graduation year should be accepted."""
        data = sample_admission_data.copy()
        data["graduation_year"] = 2018

        app = AdmissionApplicationData(**data)
        assert app.graduation_year == 2018

    def test_graduation_year_current_is_valid(self, sample_admission_data):
        """Current year should be accepted."""
        data = sample_admission_data.copy()
        data["graduation_year"] = datetime.now().year

        app = AdmissionApplicationData(**data)
        assert app.graduation_year == datetime.now().year

    def test_graduation_year_future_rejected(self, sample_admission_data):
        """Future graduation year should fail the custom validator."""
        data = sample_admission_data.copy()
        data["graduation_year"] = datetime.now().year + 5

        with pytest.raises(ValidationError) as exc_info:
            AdmissionApplicationData(**data)

        assert "future" in str(exc_info.value).lower()

    def test_graduation_year_below_1950_rejected(self, sample_admission_data):
        """Year before 1950 should fail ge=1950 constraint."""
        data = sample_admission_data.copy()
        data["graduation_year"] = 1949

        with pytest.raises(ValidationError):
            AdmissionApplicationData(**data)

    # ── Phone number validation ─────────────────────────────────────────────

    def test_valid_egyptian_phone(self, sample_admission_data):
        """Egyptian phone format +20XXXXXXXXXX should pass."""
        data = sample_admission_data.copy()
        data["phone"] = "+201001234567"

        app = AdmissionApplicationData(**data)
        assert app.phone == "+201001234567"

    def test_phone_too_short_rejected(self, sample_admission_data):
        """Phone with fewer than 10 digits should be rejected."""
        data = sample_admission_data.copy()
        data["phone"] = "123"

        with pytest.raises(ValidationError):
            AdmissionApplicationData(**data)

    # ── Email validation ────────────────────────────────────────────────────

    def test_valid_email(self, sample_admission_data):
        """Standard email should be accepted."""
        data = sample_admission_data.copy()
        data["email"] = "student@university.edu.eg"

        app = AdmissionApplicationData(**data)
        assert app.email == "student@university.edu.eg"

    def test_invalid_email_rejected(self, sample_admission_data):
        """String without @ should fail EmailStr validation."""
        data = sample_admission_data.copy()
        data["email"] = "not-an-email"

        with pytest.raises(ValidationError):
            AdmissionApplicationData(**data)

    # ── Required fields ─────────────────────────────────────────────────────

    def test_missing_full_name_rejected(self, sample_admission_data):
        """full_name is required (Field(...))."""
        data = sample_admission_data.copy()
        del data["full_name"]

        with pytest.raises(ValidationError):
            AdmissionApplicationData(**data)

    def test_full_name_too_short_rejected(self, sample_admission_data):
        """full_name must be at least 2 characters."""
        data = sample_admission_data.copy()
        data["full_name"] = "A"

        with pytest.raises(ValidationError):
            AdmissionApplicationData(**data)

    # ── Default values ──────────────────────────────────────────────────────

    def test_default_country_is_egypt(self, sample_admission_data):
        """Country should default to 'Egypt' if not provided."""
        data = sample_admission_data.copy()
        del data["country"]

        app = AdmissionApplicationData(**data)
        assert app.country == "Egypt"

    def test_default_application_type_is_regular(self, sample_admission_data):
        """Application type should default to 'regular'."""
        data = sample_admission_data.copy()
        del data["application_type"]

        app = AdmissionApplicationData(**data)
        assert app.application_type == "regular"


# ============================================================================
# OCRResponse
# ============================================================================

class TestOCRResponse:
    """Test the OCR response schema."""

    def test_valid_ocr_response(self):
        """Full OCR response with all fields should parse."""
        resp = OCRResponse(
            success=True,
            extracted_data={"name": "Test", "nid": "12345678901234"},
            confidence=0.95,
            processing_time=2.3,
        )
        assert resp.success is True
        assert resp.confidence == 0.95

    def test_ocr_response_optional_fields_default_none(self):
        """Confidence and processing_time are optional."""
        resp = OCRResponse(success=False, extracted_data={})
        assert resp.confidence is None
        assert resp.processing_time is None


# ============================================================================
# AdmissionResponse
# ============================================================================

class TestAdmissionResponse:
    """Test the admission response schema."""

    def test_successful_admission_response(self):
        """All fields populated for a successful submission."""
        resp = AdmissionResponse(
            success=True,
            application_id=101,
            student_id=42,
            status="draft",
            message="Application submitted successfully",
            next_steps=["Check email", "Wait for review"],
        )
        assert resp.application_id == 101
        assert len(resp.next_steps) == 2

    def test_failed_admission_response(self):
        """Failed response with no IDs should still parse."""
        resp = AdmissionResponse(
            success=False,
            status="error",
            message="Submission failed",
        )
        assert resp.success is False
        assert resp.application_id is None


# ============================================================================
# OrchestrationRequest / OrchestrationResponse
# ============================================================================

class TestOrchestrationModels:
    """Test the orchestration workflow models."""

    def test_orchestration_request_valid(self):
        """Valid orchestration request should parse."""
        req = OrchestrationRequest(
            email="test@example.com",
            phone="+201001234567",
            desired_program="Computer Science",
        )
        assert req.application_type == "regular"  # default

    def test_orchestration_response_with_errors(self):
        """Orchestration response can carry partial results + errors."""
        resp = OrchestrationResponse(
            success=False,
            execution_time=5.2,
            errors=["OCR extraction failed: timeout", "Odoo submission skipped"],
        )
        assert resp.success is False
        assert len(resp.errors) == 2
        assert resp.ocr_result is None
