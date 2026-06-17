# -*- coding: utf-8 -*-
"""
============================================================================
E2E Test: Admission Flow via Browser (Playwright) — Layer 3
============================================================================
Uses Playwright to interact with the system via a real browser.
Tests the Swagger/OpenAPI docs UI as an integration point.

Requires:
  - Full Docker Compose stack running
  - Playwright installed: pip install playwright && playwright install chromium

Skips gracefully when the gateway is unreachable or Playwright not installed.
============================================================================
"""
import os
import pytest
from .conftest import gateway_available, GATEWAY_URL

pytestmark = [pytest.mark.e2e, gateway_available]


class TestSwaggerDocsUI:
    """
    Test the FastAPI Swagger documentation UI served through Nginx.
    This validates that:
    - Nginx correctly proxies to FastAPI
    - The OpenAPI docs load in a browser
    - Interactive elements are rendered
    """

    def test_swagger_docs_load(self, page):
        """
        Navigate to /docs and verify the Swagger UI renders.
        The page should contain the API title and endpoint listings.
        """
        page.goto(f"{GATEWAY_URL}/docs", wait_until="networkidle")

        # The page title should contain the API name
        title = page.title()
        assert "Educational ERP" in title or "Swagger" in title or "FastAPI" in title

        # The Swagger UI should render at least one endpoint
        # Look for common Swagger UI elements
        page.wait_for_selector(".swagger-ui", timeout=10000)

        # Verify the main heading is present
        heading = page.locator("h2").first
        assert heading is not None

    def test_swagger_shows_api_endpoints(self, page):
        """
        Verify that key API endpoints are listed in the Swagger UI.
        
        TODO: Add your business-specific endpoint checks here.
        For example, verify that /api/v1/admissions/apply is visible.
        """
        page.goto(f"{GATEWAY_URL}/docs", wait_until="networkidle")
        page.wait_for_selector(".swagger-ui", timeout=10000)

        # Get the page content and check for endpoint paths
        content = page.content()

        # These endpoints should be documented in the Swagger UI
        expected_endpoints = [
            "/health",
            "/api/v1/extract-document",
            "/api/v1/admissions/apply",
        ]

        for endpoint in expected_endpoints:
            assert endpoint in content, \
                f"Endpoint {endpoint} not found in Swagger docs"

    def test_redoc_loads(self, page):
        """
        Verify that the ReDoc alternative documentation page loads.
        ReDoc is served at /redoc by FastAPI.
        """
        page.goto(f"{GATEWAY_URL}/redoc", wait_until="networkidle")

        # ReDoc should render the API title
        page.wait_for_selector("h1", timeout=10000)
        content = page.content()
        assert "Educational ERP" in content or "API Gateway" in content


class TestOdooPortalUI:
    """
    Test the Odoo web interface served through the gateway.
    
    NOTE: These tests require Odoo to be fully initialized and accessible
    through the Docker Compose stack. They test the portal/web client UI.
    
    TODO: Extend these tests to cover:
    - Student portal login
    - Admission form submission via web
    - Document upload via portal
    """

    @pytest.mark.skip(reason="Odoo portal not exposed through Nginx by default — enable when /web route is configured")
    def test_odoo_login_page_loads(self, page):
        """
        Navigate to the Odoo web client login page.
        
        This test is skipped by default because the current Nginx config
        does not proxy Odoo's /web route. Enable it when you add:
          location /web { proxy_pass http://odoo_backend; }
        """
        page.goto(f"{GATEWAY_URL}/web/login", wait_until="networkidle")
        
        # Odoo login page should have a login form
        login_form = page.locator("form.oe_login_form")
        assert login_form.count() > 0

        # Should have username and password fields
        assert page.locator("input[name='login']").count() > 0
        assert page.locator("input[name='password']").count() > 0
