"""
Pytest configuration and shared fixtures for all tests.
"""
import pytest


# ─────────────────────────────────────────────────────────────────────────────
# Test Markers
# ─────────────────────────────────────────────────────────────────────────────

def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
