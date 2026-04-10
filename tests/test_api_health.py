"""Unit tests for GET /health."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_health_all_ok(client):
    with (
        patch("api.health.engine") as mock_engine,
        patch("api.health.ping_redis", new_callable=AsyncMock, return_value=True),
        patch("api.health.is_connected", return_value=True),
    ):
        # Mock DB connection
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)
        mock_conn.execute = AsyncMock()
        mock_engine.connect.return_value = mock_conn

        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["db_connected"] is True
    assert data["redis_connected"] is True
    assert data["feed_connected"] is True
    assert "uptime_seconds" in data
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_health_db_down(client):
    with (
        patch("api.health.engine") as mock_engine,
        patch("api.health.ping_redis", new_callable=AsyncMock, return_value=True),
        patch("api.health.is_connected", return_value=False),
    ):
        mock_engine.connect.side_effect = Exception("connection refused")

        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["db_connected"] is False


@pytest.mark.asyncio
async def test_health_redis_down(client):
    with (
        patch("api.health.engine") as mock_engine,
        patch("api.health.ping_redis", new_callable=AsyncMock, return_value=False),
        patch("api.health.is_connected", return_value=True),
    ):
        mock_conn = AsyncMock()
        mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
        mock_conn.__aexit__ = AsyncMock(return_value=False)
        mock_conn.execute = AsyncMock()
        mock_engine.connect.return_value = mock_conn

        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["redis_connected"] is False
