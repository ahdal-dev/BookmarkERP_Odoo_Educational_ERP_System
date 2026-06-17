# -*- coding: utf-8 -*-
"""
Unit Tests: OdooClient — Layer 1
Tests authenticate, create_admission_application with mocked HTTP.
"""
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import pytest
from fastapi import HTTPException
from main import OdooClient, AdmissionApplicationData

pytestmark = pytest.mark.unit

@pytest.fixture
def odoo_client():
    client = OdooClient()
    client._uid = None
    return client

@pytest.fixture
def admission_data():
    return AdmissionApplicationData(
        full_name="Test Student", national_id="29901011234567",
        email="test@example.com", phone="+201001234567",
        date_of_birth=datetime(2000, 1, 15),
        address="123 Test Street, Cairo, Egypt", city="Cairo",
        country="Egypt", previous_qualification="High School",
        graduation_year=2020, gpa=3.5,
        desired_program="Computer Science", application_type="regular",
    )

def _mock_response(json_data, status_code=200):
    response = MagicMock(spec=httpx.Response)
    response.status_code = status_code
    response.json.return_value = json_data
    response.raise_for_status = MagicMock()
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Error", request=MagicMock(), response=response)
    return response

class TestOdooClientAuthenticate:
    @pytest.mark.asyncio
    async def test_authenticate_success(self, odoo_client, sample_odoo_auth_response):
        mock_resp = _mock_response(sample_odoo_auth_response)
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        with patch("httpx.AsyncClient") as MC:
            MC.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MC.return_value.__aexit__ = AsyncMock(return_value=False)
            uid = await odoo_client.authenticate()
            assert uid == 2
            assert odoo_client._uid == 2

    @pytest.mark.asyncio
    async def test_authenticate_returns_cached_uid(self, odoo_client):
        odoo_client._uid = 99
        assert await odoo_client.authenticate() == 99

    @pytest.mark.asyncio
    async def test_authenticate_failure_raises_503(self, odoo_client):
        mock_resp = _mock_response({"jsonrpc": "2.0", "result": {}})
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        with patch("httpx.AsyncClient") as MC:
            MC.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MC.return_value.__aexit__ = AsyncMock(return_value=False)
            with pytest.raises(HTTPException) as exc_info:
                await odoo_client.authenticate()
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_authenticate_network_error_raises_503(self, odoo_client):
        mock_client = AsyncMock()
        mock_client.post.side_effect = httpx.ConnectTimeout("timeout")
        with patch("httpx.AsyncClient") as MC:
            MC.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MC.return_value.__aexit__ = AsyncMock(return_value=False)
            with pytest.raises(HTTPException) as exc_info:
                await odoo_client.authenticate()
            assert exc_info.value.status_code == 503

class TestOdooClientCreateApplication:
    @pytest.mark.asyncio
    async def test_create_application_success(self, odoo_client, admission_data, sample_odoo_create_response):
        odoo_client._uid = 2
        mock_resp = _mock_response(sample_odoo_create_response)
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        with patch("httpx.AsyncClient") as MC:
            MC.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MC.return_value.__aexit__ = AsyncMock(return_value=False)
            result = await odoo_client.create_admission_application(admission_data)
            assert result["application_id"] == 101
            assert result["status"] == "draft"

    @pytest.mark.asyncio
    async def test_create_application_odoo_error_raises_500(self, odoo_client, admission_data):
        odoo_client._uid = 2
        mock_resp = _mock_response({"jsonrpc": "2.0", "error": {"message": "Access Denied"}})
        mock_client = AsyncMock()
        mock_client.post.return_value = mock_resp
        with patch("httpx.AsyncClient") as MC:
            MC.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MC.return_value.__aexit__ = AsyncMock(return_value=False)
            with pytest.raises(HTTPException) as exc_info:
                await odoo_client.create_admission_application(admission_data)
            assert exc_info.value.status_code == 500

class TestOdooClientHelpers:
    @pytest.mark.asyncio
    async def test_get_country_id_falls_back_to_65_on_error(self):
        """When Odoo is unreachable, _get_country_id falls back to 65 (Egypt)."""
        from main import _get_country_id
        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("connection refused")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        with patch("main.httpx.AsyncClient", return_value=mock_client):
            result = await _get_country_id("Egypt")
        assert result == 65
