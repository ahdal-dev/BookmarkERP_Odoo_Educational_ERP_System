# -*- coding: utf-8 -*-
"""
============================================================================
Root conftest.py — Educational ERP Testing Pyramid
============================================================================
Provides path setup so test files can import from the application modules
(api_gateway.fastapi_app.main, services.ocr.app, etc.) without installing
them as packages.

This file is auto-discovered by pytest before any test collection begins.
============================================================================
"""

import sys
import os

import pytest


# ============================================================================
# Path Setup — Make application modules importable
# ============================================================================

# Project root (c:\Odoo)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add project root so 'api_gateway.fastapi_app.main' is importable
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Add FastAPI app directory so 'main' is importable directly
FASTAPI_APP_DIR = os.path.join(PROJECT_ROOT, "api_gateway", "fastapi_app")
if FASTAPI_APP_DIR not in sys.path:
    sys.path.insert(0, FASTAPI_APP_DIR)

# Add OCR service directory so 'app.routes' is importable
OCR_SERVICE_DIR = os.path.join(PROJECT_ROOT, "services", "ocr")
if OCR_SERVICE_DIR not in sys.path:
    sys.path.insert(0, OCR_SERVICE_DIR)


# ---------------------------------------------------------------------------
# Environment bootstrap — MUST come before any test file or sub-conftest
# imports main.py, because main.py reads these at import time as module-level
# globals.  When `Tests/` is collected as a single path pytest processes
# subdirectories alphabetically (e2e → integration → unit), so e2e test
# files are imported before integration/conftest.py runs.  Setting these
# here (in the root conftest, which always runs first) guarantees a
# consistent environment regardless of collection order.
# ---------------------------------------------------------------------------
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-production")
os.environ.setdefault("ODOO_URL", "http://mock-odoo:8069")
os.environ.setdefault("ODOO_PASSWORD", "test-password")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173,http://allowed.example.com")
os.environ.setdefault("OCR_SERVICE_URL", "http://mock-ocr:5000")

# Import main now so its module-level globals (ODOO_URL, CORS_ORIGINS,
# OCR_SERVICE_URL, etc.) are frozen with the values above.  Any later test
# file that does `os.environ[...] = "..."` then `from main import app` will
# receive the cached module — the globals cannot be changed after first import.
from main import app  # noqa: F401 — side-effect import only


# ============================================================================
# Shared Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def project_root():
    """Return the absolute path to the project root directory."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def jwt_secret_key():
    """
    Deterministic JWT secret for testing.
    Overrides the env var so all tests use the same key.
    """
    key = "test-secret-key-for-testing-only-do-not-use-in-production"
    os.environ["JWT_SECRET_KEY"] = key
    return key
