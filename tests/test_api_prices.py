"""Unit tests for GET /prices/{ticker}."""
import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_price_from_redis_cache(client):
    cached = {
        "symbol": "AAPL",
        "price": 182.50,
        "bid": 182.49,
        "ask": 182.51,
        "volume": 100,
        "last_updated": "2024-01-15T14:30:00+00:00",
        "source": "trade",
    }
    with patch(
        "api.prices.get_latest_price", new_callable=AsyncMock, return_value=cached
    ):
        response = await client.get("/prices/AAPL")

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["price"] == 182.50
    assert data["bid"] == 182.49
    assert data["ask"] == 182.51
    assert data["source"] == "trade"


@pytest.mark.asyncio
async def test_price_falls_back_to_db(client):
    """When Redis has no data, should fall back to TimescaleDB."""
    mock_tick = MagicMock()
    mock_tick.symbol = "TSLA"
    mock_tick.price = Decimal("220.50")
    mock_tick.bid = Decimal("220.48")
    mock_tick.ask = Decimal("220.52")
    mock_tick.volume = 500
    mock_tick.time = datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc)
    mock_tick.source = "trade"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_tick

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("api.prices.get_latest_price", new_callable=AsyncMock, return_value=None),
        patch("api.prices.get_session", return_value=mock_session),
    ):
        response = await client.get("/prices/TSLA")

    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "TSLA"
    assert data["price"] == 220.50


@pytest.mark.asyncio
async def test_price_not_found(client):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    with (
        patch("api.prices.get_latest_price", new_callable=AsyncMock, return_value=None),
        patch("api.prices.get_session", return_value=mock_session),
    ):
        response = await client.get("/prices/UNKNOWN")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_price_symbol_uppercased(client):
    """Ticker in URL should be case-insensitive."""
    cached = {
        "symbol": "MSFT",
        "price": 415.10,
        "bid": 415.09,
        "ask": 415.11,
        "volume": None,
        "last_updated": "2024-01-15T14:30:00+00:00",
        "source": "quote",
    }
    with patch(
        "api.prices.get_latest_price", new_callable=AsyncMock, return_value=cached
    ):
        response = await client.get("/prices/msft")

    assert response.status_code == 200
    assert response.json()["symbol"] == "MSFT"
