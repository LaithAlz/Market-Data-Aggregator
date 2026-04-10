"""Unit tests for the ingestor module."""
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from feed.ingestor import enqueue, get_ticks_per_second, get_total_ticks
from feed.normalizer import Tick


def _make_tick(symbol: str = "AAPL", price: float = 182.50) -> Tick:
    return Tick(
        time=datetime(2024, 1, 15, 14, 30, 0, tzinfo=timezone.utc),
        symbol=symbol,
        price=Decimal(str(price)),
        volume=100,
        bid=Decimal(str(price - 0.01)),
        ask=Decimal(str(price + 0.01)),
        source="trade",
    )


def test_enqueue_does_not_raise():
    tick = _make_tick()
    enqueue(tick)  # Should not raise


def test_get_ticks_per_second_returns_float():
    result = get_ticks_per_second()
    assert isinstance(result, float)
    assert result >= 0.0


@pytest.mark.asyncio
async def test_write_redis_batch_deduplicates():
    """Only the latest tick per symbol should be written to Redis."""
    from datetime import timedelta
    import feed.ingestor as ingestor_module

    tick1 = _make_tick("AAPL", 182.00)
    tick2 = Tick(
        time=tick1.time + timedelta(seconds=1),
        symbol="AAPL",
        price=Decimal("183.00"),
        volume=200,
        bid=Decimal("182.99"),
        ask=Decimal("183.01"),
        source="trade",
    )

    calls = []

    async def mock_set(symbol, price, bid, ask, volume, source):
        calls.append({"symbol": symbol, "price": price})

    with patch("feed.ingestor.set_latest_price", side_effect=mock_set):
        await ingestor_module._write_redis_batch([tick1, tick2])

    # Should only write once for AAPL (the latest one)
    assert len(calls) == 1
    assert calls[0]["price"] == 183.00


@pytest.mark.asyncio
async def test_flush_batch_empty_is_noop():
    """Flushing an empty batch should not hit the DB."""
    import feed.ingestor as ingestor_module

    with patch("feed.ingestor.engine") as mock_engine:
        await ingestor_module._flush_batch([])
        mock_engine.begin.assert_not_called()
