"""Unit tests for GET /history/{ticker}."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch


def _make_row(bucket_time, open_, high, low, close, volume):
    row = MagicMock()
    row.bucket_time = bucket_time
    row.open = open_
    row.high = high
    row.low = low
    row.close = close
    row.volume = volume
    return row


@pytest.mark.asyncio
async def test_history_valid_request(client):
    rows = [
        _make_row(
            datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc),
            182.00, 183.00, 181.50, 182.80, 10000,
        ),
        _make_row(
            datetime(2024, 1, 15, 14, 31, 0, tzinfo=timezone.utc),
            182.80, 184.00, 182.50, 183.50, 8500,
        ),
    ]

    mock_result = MagicMock()
    mock_result.fetchall.return_value = rows

    mock_conn = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_conn.execute = AsyncMock(return_value=mock_result)

    with patch("api.history.engine") as mock_engine:
        mock_engine.connect.return_value = mock_conn
        response = await client.get(
            "/history/AAPL"
            "?from=2024-01-15T14:30:00Z"
            "&to=2024-01-15T14:32:00Z"
            "&interval=1m"
        )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["open"] == 182.00
    assert data[0]["high"] == 183.00
    assert data[0]["volume"] == 10000


@pytest.mark.asyncio
async def test_history_invalid_interval(client):
    response = await client.get(
        "/history/AAPL?from=2024-01-15T14:30:00Z&to=2024-01-15T15:30:00Z&interval=99x"
    )
    assert response.status_code == 400
    assert "interval" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_history_from_after_to_returns_400(client):
    response = await client.get(
        "/history/AAPL?from=2024-01-15T15:00:00Z&to=2024-01-15T14:00:00Z"
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_history_no_data_returns_404(client):
    mock_result = MagicMock()
    mock_result.fetchall.return_value = []

    mock_conn = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_conn.execute = AsyncMock(return_value=mock_result)

    with patch("api.history.engine") as mock_engine:
        mock_engine.connect.return_value = mock_conn
        response = await client.get(
            "/history/UNKNOWN?from=2024-01-15T14:00:00Z&to=2024-01-15T15:00:00Z"
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_history_all_valid_intervals(client):
    """All supported intervals should be accepted."""
    rows = [
        _make_row(
            datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc),
            100.0, 101.0, 99.0, 100.5, 5000,
        )
    ]
    mock_result = MagicMock()
    mock_result.fetchall.return_value = rows

    mock_conn = AsyncMock()
    mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
    mock_conn.__aexit__ = AsyncMock(return_value=False)
    mock_conn.execute = AsyncMock(return_value=mock_result)

    intervals = ["1m", "5m", "15m", "1h", "1d"]
    with patch("api.history.engine") as mock_engine:
        mock_engine.connect.return_value = mock_conn
        for interval in intervals:
            r = await client.get(
                f"/history/AAPL"
                f"?from=2024-01-15T00:00:00Z"
                f"&to=2024-01-16T00:00:00Z"
                f"&interval={interval}"
            )
            assert r.status_code == 200, f"interval={interval} returned {r.status_code}"
