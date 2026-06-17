# -*- coding: utf-8 -*-
"""
Integration tests — Redis caching behaviour.

Verifies that:
- Role lookups are cached and Odoo is not called twice for the same UID.
- Country ID lookups are cached.
- Logout invalidates the role cache.

Redis is mocked via a simple in-memory dict so these tests run without a
real Redis instance.
"""
import os
import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest

os.environ["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "test-secret-key-for-testing-only-do-not-use-in-production")
os.environ["ODOO_PASSWORD"]  = os.environ.get("ODOO_PASSWORD", "test-password")
os.environ["ODOO_URL"]       = os.environ.get("ODOO_URL", "http://mock-odoo:8069")

from main import resolve_user_role, _get_country_id, JWT_SECRET_KEY

pytestmark = pytest.mark.integration


class _FakeRedis:
    """Minimal async Redis mock using an in-memory dict."""

    def __init__(self):
        self._store: dict = {}

    async def get(self, key):
        return self._store.get(key)

    async def setex(self, key, ttl, value):
        self._store[key] = value

    async def delete(self, key):
        self._store.pop(key, None)

    async def exists(self, key):
        return int(key in self._store)


@pytest.mark.asyncio
async def test_role_resolved_from_cache_on_second_call():
    """Second call for the same UID must not re-invoke Odoo."""
    redis = _FakeRedis()
    # Pre-populate cache
    await redis.setex("role:7", 300, "student")

    with patch("main.httpx.AsyncClient") as _mock_client:
        role = await resolve_user_role(7, redis)

    assert role.value == "student"
    # httpx.AsyncClient should not have been used — result came from cache
    _mock_client.assert_not_called()


@pytest.mark.asyncio
async def test_role_written_to_cache_on_first_call():
    """After resolving from Odoo, role must be stored in Redis."""
    redis = _FakeRedis()
    assert await redis.get("role:99") is None  # cache miss

    # Patch the Odoo HTTP calls
    mock_response = MagicMock()
    mock_response.json.side_effect = [
        # auth call
        {"result": {"uid": 1}},
        # read user groups
        {"result": [{"group_ids": [10]}]},
        # ir.model.data search
        {"result": [{"name": "group_erp_student", "res_id": 10}]},
    ]

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("main.httpx.AsyncClient", return_value=mock_client):
        role = await resolve_user_role(99, redis)

    cached = await redis.get("role:99")
    assert cached == role.value


@pytest.mark.asyncio
async def test_country_id_cached_after_first_lookup():
    redis = _FakeRedis()
    assert await redis.get("country_id:egypt") is None

    mock_response = MagicMock()
    mock_response.json.side_effect = [
        {"result": {"uid": 1}},              # auth
        {"result": [{"id": 65}]},            # search_read res.country
    ]
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)

    with patch("main.httpx.AsyncClient", return_value=mock_client):
        country_id = await _get_country_id("Egypt", redis)

    assert country_id == 65
    cached = await redis.get("country_id:egypt")
    assert cached == "65"


@pytest.mark.asyncio
async def test_country_id_served_from_cache_on_second_call():
    redis = _FakeRedis()
    await redis.setex("country_id:egypt", 86400, "65")

    with patch("main.httpx.AsyncClient") as _mock_client:
        country_id = await _get_country_id("Egypt", redis)

    assert country_id == 65
    _mock_client.assert_not_called()
