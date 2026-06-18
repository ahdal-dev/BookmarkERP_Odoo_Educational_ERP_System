# -*- coding: utf-8 -*-
"""
E2E Test Fixtures — Layer 3
Provides gateway URL, HTTP session, and Playwright browser context.
These tests require the full Docker Compose stack to be running.
"""
import os
import ssl

import httpx
import pytest

# ============================================================================
# Configuration
# ============================================================================

GATEWAY_URL = os.getenv("E2E_GATEWAY_URL", "https://localhost")
VERIFY_SSL = os.getenv("E2E_VERIFY_SSL", "false").lower() == "true"


def _gateway_is_reachable() -> bool:
    """Check if the Nginx gateway is accessible."""
    try:
        ctx = None if VERIFY_SSL else ssl.create_default_context()
        if not VERIFY_SSL and ctx:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
        r = httpx.get(
            f"{GATEWAY_URL}/health",
            verify=VERIFY_SSL, timeout=5.0,
        )
        return r.status_code in (200, 301, 302)
    except Exception:
        return False


gateway_available = pytest.mark.skipif(
    not _gateway_is_reachable(),
    reason=f"E2E gateway not reachable at {GATEWAY_URL}"
)

# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def gateway_url():
    """Base URL for the Nginx API gateway."""
    return GATEWAY_URL

@pytest.fixture(scope="session")
def http_client():
    """Shared httpx client for E2E API tests (skips SSL verification)."""
    with httpx.Client(
        base_url=GATEWAY_URL,
        verify=VERIFY_SSL,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        yield client

@pytest.fixture
def auth_token(http_client):
    """
    Obtain a real JWT token from the running gateway.
    This hits the /api/v1/auth/token endpoint through Nginx.
    """
    response = http_client.post(
        "/api/v1/auth/token",
        params={"username": "e2e_test_student", "role": "prospective_student"},
    )
    assert response.status_code == 200, f"Token generation failed: {response.text}"
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    """Authorization headers with a valid JWT token."""
    return {"Authorization": f"Bearer {auth_token}"}


# ============================================================================
# Playwright Fixtures (for UI tests)
# ============================================================================

@pytest.fixture(scope="session")
def browser_context():
    """Playwright browser context for UI E2E tests."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        pytest.skip("Playwright not installed")

    headless = os.getenv("PLAYWRIGHT_HEADLESS", "true").lower() == "true"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1280, "height": 720},
        )
        yield context
        context.close()
        browser.close()

@pytest.fixture
def page(browser_context):
    """Fresh browser page for each test."""
    page = browser_context.new_page()
    yield page
    page.close()
