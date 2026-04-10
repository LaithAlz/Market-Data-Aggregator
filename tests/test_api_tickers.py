"""Unit tests for GET /tickers."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.asyncio
async def test_tickers_returns_list(client):
    mock_ticker = MagicMock()
    mock_ticker.symbol = "AAPL"
    mock_ticker.name = "Apple Inc."

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_ticker]

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    price_data = {
        "AAPL": {
            "symbol": "AAPL",
            "price": 182.50,
            "last_updated": "2024-01-15T14:30:00+00:00",
        }
    }

    with (
        patch("api.tickers.get_session", return_value=mock_session),
        patch(
            "api.tickers.get_all_latest_prices",
            new_callable=AsyncMock,
            return_value=price_data,
        ),
    ):
        response = await client.get("/tickers")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["symbol"] == "AAPL"
    assert data[0]["name"] == "Apple Inc."
    assert data[0]["latest_price"] == 182.50


@pytest.mark.asyncio
async def test_tickers_falls_back_to_config_when_db_empty(client):
    """If no rows in tickers table, fall back to config.symbols."""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=False)

    from config import settings
    price_data = {sym: None for sym in settings.symbols}

    with (
        patch("api.tickers.get_session", return_value=mock_session),
        patch(
            "api.tickers.get_all_latest_prices",
            new_callable=AsyncMock,
            return_value=price_data,
        ),
    ):
        response = await client.get("/tickers")

    assert response.status_code == 200
    data = response.json()
    symbols = [t["symbol"] for t in data]
    for sym in settings.symbols:
        assert sym in symbols
