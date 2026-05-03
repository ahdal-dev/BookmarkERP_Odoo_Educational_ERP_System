# -*- coding: utf-8 -*-
"""
Integration Tests: Health & Metrics Endpoints — Layer 2
Tests /health and /metrics via TestClient.
"""
import pytest

pytestmark = pytest.mark.integration


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        data = client.get("/health").json()
        assert data["status"] == "healthy"
        assert data["service"] == "api_gateway"
        assert "timestamp" in data
        assert data["version"] == "1.0.0"


class TestMetricsEndpoint:
    def test_metrics_returns_200(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_response_structure(self, client):
        data = client.get("/metrics").json()
        assert data["service"] == "api_gateway"
        assert "uptime" in data
