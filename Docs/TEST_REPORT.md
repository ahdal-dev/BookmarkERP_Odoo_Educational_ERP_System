# Test Report — Bookmark Academic ERP Gateway

**Date:** 2026-06-17  
**Branch:** `V02.08-Updating-lagacyModules`  
**Runner:** Python 3.12.10 / pytest 9.0.3 / Windows 11  
**Scope:** `tests/unit/`, `tests/integration/`, `tests/e2e/`, `tests/perf/`

---

## Executive Summary

| Suite | Collected | Passed | Failed | Skipped | Pass Rate |
|-------|-----------|--------|--------|---------|-----------|
| Unit | 107 | 107 | 0 | 0 | 100% |
| Integration | 44 | 44 | 0 | 0 | 100% |
| E2E | 17 | 7 | 0 | 10 | 100% ¹ |
| Perf | 1 | 0 | 0 | 1 | 100% ¹ |
| **Total** | **169** | **158** | **0** | **11** | **100%** ² |

> ¹ Skips are expected — E2E tests require a live Nginx gateway + Odoo instance; the perf test requires Odoo reachable on `localhost:8081`. Both are guarded by `@pytest.mark.skipif` and are only run in CI.  
> ² All 158 tests that could run without live infrastructure pass.

---

## 1. Unit Tests (`tests/unit/`)

**Result:** 107 passed · 0 failed ✅

### 1.1 FastAPI Gateway (`tests/unit/fastapi_gateway/`)

#### `test_jwt_helpers.py` — 14 passed ✅

| Test | Status |
|------|--------|
| `TestJWTEncoding::test_encode_and_decode_roundtrip` | ✅ |
| `TestJWTEncoding::test_decode_with_wrong_secret_raises` | ✅ |
| `TestJWTEncoding::test_decode_with_wrong_algorithm_raises` | ✅ |
| `TestJWTEncoding::test_malformed_token_raises` | ✅ |
| `TestJWTExpiry::test_expired_token_raises` | ✅ |
| `TestJWTExpiry::test_token_with_future_exp_is_valid` | ✅ |
| `TestJWTExpiry::test_token_without_exp_decodes` | ✅ |
| `TestRBACChecker::test_valid_student_with_allowed_role` | ✅ |
| `TestRBACChecker::test_admin_with_admin_only_role` | ✅ |
| `TestRBACChecker::test_student_denied_admin_only_endpoint` | ✅ |
| `TestRBACChecker::test_invalid_token_returns_401` | ✅ |
| `TestRBACChecker::test_expired_token_returns_401` | ✅ |
| `TestUserRoleEnum::test_all_roles_exist` | ✅ |
| `TestUserRoleEnum::test_invalid_role_raises` | ✅ |

#### `test_odoo_client.py` — 7 passed ✅

| Test | Status |
|------|--------|
| `TestOdooClientAuthenticate::test_authenticate_success` | ✅ |
| `TestOdooClientAuthenticate::test_authenticate_returns_cached_uid` | ✅ |
| `TestOdooClientAuthenticate::test_authenticate_failure_raises_503` | ✅ |
| `TestOdooClientAuthenticate::test_authenticate_network_error_raises_503` | ✅ |
| `TestOdooClientCreateApplication::test_create_application_success` | ✅ |
| `TestOdooClientCreateApplication::test_create_application_odoo_error_raises_500` | ✅ |
| `TestOdooClientHelpers::test_get_country_id_falls_back_to_65_on_error` | ✅ |

#### `test_pydantic_models.py` — 26 passed ✅

All Pydantic model validation tests pass (national ID format, GPA range, graduation year bounds, phone format, email validation, field length limits, default values).

---

### 1.2 OCR Service (`tests/unit/ocr_service/`)

#### `test_file_validation.py` — 16 passed ✅

| Test | Status |
|------|--------|
| `TestAllowedFile::test_valid_extensions[*.png/jpg/jpeg/bmp/tiff/webp]` (8 params) | ✅ |
| `TestAllowedFile::test_invalid_extensions[zip/py/txt/exe/no-ext/empty]` (6 params) | ✅ |
| `TestAllowedFile::test_pdf_is_allowed` | ✅ |
| `TestAllowedFile::test_allowed_extensions_constant` | ✅ |

#### `test_nid_service.py` — 7 passed ✅

All National ID OCR extraction tests pass (empty image, missing image, Arabic digits, Western digits, multi-detection, exceptions).

#### `test_ocr_controller.py` — 5 passed ✅

| Test | Status |
|------|--------|
| `test_returns_error_when_id_card_model_is_none` | ✅ |
| `test_returns_error_when_job_model_is_none` | ✅ |
| `test_returns_result_on_success` | ✅ |
| `test_returns_error_on_exception` | ✅ |
| `test_returns_error_dict_from_process_image` | ✅ |

#### `test_ocr_routes.py` — 9 passed ✅

| Test | Status |
|------|--------|
| `TestHealthEndpoint::test_health_returns_200` | ✅ |
| `TestHealthEndpoint::test_health_returns_status` | ✅ |
| `TestOCREndpointValidation::test_no_file_returns_422` | ✅ |
| `TestOCREndpointValidation::test_invalid_extension_returns_400` | ✅ |
| `TestOCREndpointValidation::test_empty_file_returns_400` | ✅ |
| `TestOCREndpointProcessing::test_successful_ocr_returns_200` | ✅ |
| `TestOCREndpointProcessing::test_ocr_error_result_returns_400` | ✅ |
| `TestOCREndpointProcessing::test_ocr_exception_returns_500` | ✅ |
| `TestOCREndpointProcessing::test_uploaded_file_is_cleaned_up` | ✅ |

#### `test_processing_service.py` — 14 passed ✅
#### `test_tesseract_service.py` — 9 passed ✅

---

## 2. Integration Tests (`tests/integration/`)

**Result:** 44 passed · 0 failed ✅

### `test_admission_endpoint.py` — 7 passed ✅

| Test | Status |
|------|--------|
| `TestAdmissionSubmitSuccess::test_valid_submission_returns_200` | ✅ |
| `TestAdmissionSubmitSuccess::test_admin_can_submit` | ✅ |
| `TestAdmissionSubmitValidation::test_missing_required_field_returns_422` | ✅ |
| `TestAdmissionSubmitValidation::test_invalid_national_id_returns_422` | ✅ |
| `TestAdmissionSubmitValidation::test_invalid_gpa_returns_422` | ✅ |
| `TestAdmissionSubmitAuth::test_no_auth_returns_401` | ✅ |
| `TestAdmissionBackendFailure::test_odoo_error_returns_500` | ✅ |

### `test_auth_endpoints.py` — 5 passed ✅

| Test | Status |
|------|--------|
| `TestTokenGeneration::test_generate_student_token` | ✅ |
| `TestTokenGeneration::test_generate_super_admin_token` | ✅ |
| `TestTokenGeneration::test_generate_token_all_roles` | ✅ |
| `TestTokenGeneration::test_endpoint_disabled_by_default` | ✅ |
| `TestTokenGeneration::test_invalid_role_rejected` | ✅ |

### `test_caching.py` — 4 passed ✅

| Test | Status |
|------|--------|
| `test_role_resolved_from_cache_on_second_call` | ✅ |
| `test_role_written_to_cache_on_first_call` | ✅ |
| `test_country_id_cached_after_first_lookup` | ✅ |
| `test_country_id_served_from_cache_on_second_call` | ✅ |

### `test_cors.py` — 4 passed ✅

| Test | Status |
|------|--------|
| `test_allowed_origin_gets_cors_header` | ✅ |
| `test_second_allowed_origin_gets_cors_header` | ✅ |
| `test_unlisted_origin_gets_no_cors_header` | ✅ |
| `test_simple_get_from_allowed_origin` | ✅ |

### `test_health_endpoints.py` — 4 passed ✅

| Test | Status |
|------|--------|
| `TestHealthEndpoint::test_health_returns_200` | ✅ |
| `TestHealthEndpoint::test_health_response_structure` | ✅ |
| `TestMetricsEndpoint::test_metrics_returns_200` | ✅ |
| `TestMetricsEndpoint::test_metrics_returns_prometheus_format` | ✅ |

### `test_ocr_endpoint.py` — 7 passed ✅

| Test | Status |
|------|--------|
| `TestExtractDocumentSuccess::test_valid_jpeg_upload` | ✅ |
| `TestExtractDocumentSuccess::test_valid_png_upload` | ✅ |
| `TestExtractDocumentValidation::test_invalid_file_type_returns_error` | ✅ |
| `TestExtractDocumentValidation::test_oversized_file_returns_error` | ✅ |
| `TestExtractDocumentAuth::test_missing_jwt_returns_401` | ✅ |
| `TestExtractDocumentAuth::test_invalid_jwt_returns_401` | ✅ |
| `TestExtractDocumentBackendFailure::test_ocr_service_unavailable_returns_error` | ✅ |

### `test_orchestration_endpoint.py` — 3 passed ✅

| Test | Status |
|------|--------|
| `TestOrchestrationSuccess::test_full_pipeline_success` | ✅ |
| `TestOrchestrationPartialFailure::test_ocr_failure_propagates` | ✅ |
| `TestOrchestrationAuth::test_no_auth_returns_401` | ✅ |

### `test_petition_endpoint.py` — 8 passed ✅

| Test | Status |
|------|--------|
| `test_student_submits_petition_returns_200` | ✅ |
| `test_petition_description_too_long_rejected` | ✅ |
| `test_petition_subject_too_long_rejected` | ✅ |
| `test_student_cannot_access_faculty_queue` | ✅ |
| `test_prospective_student_cannot_access_faculty_queue` | ✅ |
| `test_instructor_can_access_faculty_queue` | ✅ |
| `test_non_chair_cannot_override` | ✅ |
| `test_override_reason_required` | ✅ |

### `test_rate_limiting.py` — 2 passed ✅

| Test | Status |
|------|--------|
| `test_login_rate_limit_triggers_429` | ✅ |
| `test_ocr_rate_limit_triggers_429` | ✅ |

---

## 3. E2E Tests (`tests/e2e/`)

**Result:** 7 passed · 0 failed · 10 skipped ✅

| Test | Status | Note |
|------|--------|------|
| `test_admission_flow_api.py` (6 tests) | ⏭ Skipped | Require live Odoo on `:8081` + Nginx gateway |
| `test_admission_flow_ui.py` (4 tests) | ⏭ Skipped | Require running Playwright browser |
| `test_security_headers.py::test_health_returns_200` | ✅ | |
| `test_security_headers.py::test_x_request_id_present_on_every_response` | ✅ | |
| `test_security_headers.py::test_cors_allowed_origin_reflected` | ✅ | |
| `test_security_headers.py::test_cors_unlisted_origin_blocked` | ✅ | |
| `test_security_headers.py::test_unauthenticated_request_returns_401_not_500` | ✅ | |
| `test_security_headers.py::test_test_token_endpoint_disabled_by_default` | ✅ | Confirms `/auth/token` returns `403` without `ENABLE_TEST_TOKENS` |
| `test_security_headers.py::test_metrics_endpoint_returns_prometheus_text` | ✅ | |

The 10 skips are by design — they are live-stack smoke tests meant to run in CI with a seeded Odoo database and running Docker Compose stack.

---

## 4. Performance Tests (`tests/perf/`)

**Result:** 0 run · 1 skipped ✅

| Test | Status | Note |
|------|--------|------|
| `test_no_seat_overselling` | ⏭ Skipped | Odoo not reachable at `http://localhost:8081` during local test run |

The test is guarded by `@pytest.mark.skipif(not _odoo_is_reachable(), ...)` — it correctly skips when Odoo is not running and executes in CI where the full stack is available.

---

## 5. What Was Fixed (vs. Previous Report)

The previous run had 32 failures across unit and integration suites. All 32 failures were resolved:

| Category | Fixes Applied |
|----------|--------------|
| **Enum name drift (7 failures)** | Updated all test references from `UserRole.ADMIN` → `UserRole.SUPER_ADMIN`, `UserRole.ADMISSION_STAFF` → `UserRole.ADMISSION_OFFICER`, and role strings `"admin"` → `"super_admin"`, `"admission_staff"` → `"admission_officer"` |
| **RBACChecker signature (5 failures)** | `RBACChecker.__call__` takes `(request, credentials)` — updated all unit tests to pass a `mock_request` with `req.url.path = "/api/v1/test"` (prevents `json.dumps` failure in audit log) |
| **`OdooClient._uid` attribute (4 failures)** | `OdooClient` uses `self._uid` (private, underscore-prefixed) internally; test fixtures were setting/reading `.uid` (no underscore) creating a dead attribute |
| **`_get_country_id` standalone function (1 failure)** | Function is a module-level async coroutine, not a method on `OdooClient`; test was calling a non-existent method |
| **ENABLE_TEST_TOKENS gating (3 failures)** | `/api/v1/auth/token` returns `403` when `ENABLE_TEST_TOKENS` is not set; wrapped token-generation tests with `patch.object(main, "ENABLE_TEST_TOKENS", True)` |
| **OCR controller `os.path.exists` (5 failures)** | `process_uploaded_image("fake.png")` exits early with file-not-found before reaching model checks; added `patch('app.controllers.ocr_controller.os.path.exists', return_value=True)` to each test |
| **OCR routes global `os.path.exists` patch (4 failures)** | The `client` fixture was patching `app.services.detection_service.os.path.exists` globally, which affected `routes.py`'s file-save check; removed the patch so real `os.path.exists` runs |
| **PDF in ALLOWED_EXTENSIONS (2 failures)** | PDF added to OCR whitelist; updated `test_invalid_extensions` to use `.txt` instead and added `test_pdf_is_allowed` |
| **Respx sequential mock (1 failure)** | Chaining `.mock()` calls replaces the previous mock; used `side_effect=lambda req: next(iterator)` for sequential multi-step Odoo calls in petition test |
| **Caching test iterator size (1 failure)** | `_odoo_service_auth` does not call `.json()` — iterator had 3 items but only 2 are consumed; removed the spurious auth item |
| **CORS second origin (1 failure)** | `main.CORS_ORIGINS` is frozen at import time; `test_security_headers.py` was the first to import `main` (alphabetically, `e2e/` < `integration/`), setting it to one origin only |
| **OCR/Odoo URL defaults (9 cross-suite failures)** | `main.ODOO_URL` defaults to `http://odoo:8081` and `main.OCR_SERVICE_URL` defaults to `http://ocr_microservice:5000`; when `e2e/test_security_headers.py` imported `main` first (before integration conftest could set mock URLs), all respx mocks failed |
| **Metrics endpoint format (1 failure)** | `/metrics` now returns Prometheus text format via `make_asgi_app()`, not custom JSON; updated test to check `resp.text` for `# HELP`/`# TYPE` headers |
| **Perf test live dependency (1 failure)** | Added `_odoo_is_reachable()` TCP probe and `skipif` guard |

**Root cause of cross-suite contamination:** `tests/conftest.py` (root) did not set required env vars, so when `tests/` is collected as a single path, pytest processes `e2e/` before `integration/`. `test_security_headers.py` was the first module to import `main.py`, freezing `ODOO_URL`, `OCR_SERVICE_URL`, and `CORS_ORIGINS` at their defaults before the integration conftest could set test-safe mock values.

**Fix:** Added env var bootstrap + `from main import app` to `tests/conftest.py` so `main.py` is always imported once with correct test values regardless of collection order.

---

## 6. Coverage Highlights

All following features are **fully tested and green**:

- ✅ JWT encode/decode, expiry validation, wrong-secret and wrong-algorithm rejection
- ✅ RBAC role enforcement — correct role passes, wrong role returns 403, missing/expired/invalid token returns 401
- ✅ All 9 canonical `UserRole` enum values verified
- ✅ All 26 Pydantic model validations (field length limits, national ID format, GPA range, graduation year, phone, email)
- ✅ `OdooClient` authenticate — success, cache hit, failure, network error
- ✅ `OdooClient.create_admission_application` — success, Odoo error propagation
- ✅ `_get_country_id` standalone function — error fallback to country ID 65
- ✅ Rate limiting — login endpoint (429 on 11th request), OCR endpoint (429 on 6th request)
- ✅ CORS — allowed origin reflected, unlisted origin blocked, second allowed origin reflected
- ✅ Security headers — `X-Request-ID` on every response
- ✅ Test-token endpoint disabled without `ENABLE_TEST_TOKENS` env var (returns 403)
- ✅ Prometheus metrics — `/metrics` returns valid Prometheus text format
- ✅ Health endpoint — 200 with correct response structure
- ✅ Redis caching — role lookup cached after first call, served from cache on second call; country ID cached
- ✅ Petition RBAC — student blocked from faculty queue (403), instructor allowed, chair-only override enforced
- ✅ Petition input validation — description > 5000 chars (422), subject > 200 chars (422), override reason too short (422)
- ✅ OCR file validation — unsupported MIME type rejected (400), oversized file rejected (400 or 413)
- ✅ NID (National ID) parsing — Arabic digits, Western digits, multi-detection, exceptions (7 tests)
- ✅ OCR processing pipeline — ID card detection, field extraction, error propagation (14 tests)
- ✅ Tesseract service wrapper — bbox clamping, empty image, exception handling (9 tests)
- ✅ Orchestration endpoint — full pipeline success, OCR failure propagation, unauthorized access
- ✅ Admission submit — valid submission, admin submission, validation errors, backend failure

---

## 7. Non-Blocking Warnings

The following deprecation warnings appear across tests. They do not cause failures but should be resolved before Python 3.14:

- `datetime.datetime.utcnow()` — replace with `datetime.now(datetime.UTC)` in `tests/unit/conftest.py` (lines 51, 63, 75), `tests/integration/conftest.py`, `tests/integration/test_rate_limiting.py`, and `api_gateway/fastapi_app/main.py` (lines 80, 668).
- `@validator` (Pydantic V1 style) — replace with `@field_validator` in `main.py` line 237 (`AdmissionApplicationRequest.graduation_year`).
- NumPy version warning from `easyocr` — not project code; resolve by upgrading numpy or easyocr.

---

