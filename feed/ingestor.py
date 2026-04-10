"""
Ingestor — buffers ticks for 500ms then bulk-writes to TimescaleDB.
Also writes each tick's latest price to Redis immediately.

Design:
  - asyncio.Queue feeds an ingest loop
  - Every BATCH_FLUSH_MS the loop drains the queue and bulk-inserts via
    SQLAlchemy core (not ORM) for maximum throughput
  - Metrics are tracked in-memory and exposed via module-level accessors
"""
import asyncio
import logging
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.dialects.postgresql import insert

from cache.redis_client import set_latest_price
from config import settings
from db.models import Tick as TickModel
from db.session import engine
from feed.normalizer import Tick

logger = logging.getLogger(__name__)

# ── Metrics ───────────────────────────────────────────────────────────────────

_ticks_ingested_total: int = 0
_ticks_this_window: int = 0
_ticks_per_second: float = 0.0
_window_start: float = time.monotonic()
_last_ingestion_time: dict[str, datetime] = {}

# ── Queue ─────────────────────────────────────────────────────────────────────

_queue: asyncio.Queue[Tick] = asyncio.Queue(maxsize=50_000)
_running: bool = False


def enqueue(tick: Tick) -> None:
    """Non-blocking enqueue. Drops tick if queue is full (backpressure)."""
    try:
        _queue.put_nowait(tick)
    except asyncio.QueueFull:
        logger.warning("Ingestor queue full — dropping tick for %s", tick.symbol)


# ── Metrics accessors ─────────────────────────────────────────────────────────

def get_ticks_per_second() -> float:
    return round(_ticks_per_second, 1)


def get_last_ingestion_time(symbol: str) -> Optional[datetime]:
    return _last_ingestion_time.get(symbol)


def get_total_ticks() -> int:
    return _ticks_ingested_total


# ── Main ingest loop ──────────────────────────────────────────────────────────

async def _flush_batch(ticks: list[Tick]) -> None:
    """Bulk-insert a list of ticks into TimescaleDB."""
    if not ticks:
        return

    rows = [
        {
            "time": tick.time,
            "symbol": tick.symbol,
            "price": tick.price,
            "volume": tick.volume,
            "bid": tick.bid,
            "ask": tick.ask,
            "source": tick.source,
        }
        for tick in ticks
    ]

    async with engine.begin() as conn:
        # ON CONFLICT DO NOTHING — duplicate (time, symbol) pairs are discarded
        stmt = insert(TickModel).values(rows).on_conflict_do_nothing()
        await conn.execute(stmt)


async def _write_redis_batch(ticks: list[Tick]) -> None:
    """Write latest price for each symbol to Redis. For each symbol, only
    the most recent tick in this batch is written."""
    # Deduplicate: keep the latest tick per symbol
    latest: dict[str, Tick] = {}
    for tick in ticks:
        if tick.symbol not in latest or tick.time > latest[tick.symbol].time:
            latest[tick.symbol] = tick

    for symbol, tick in latest.items():
        await set_latest_price(
            symbol=symbol,
            price=float(tick.price),
            bid=float(tick.bid) if tick.bid is not None else None,
            ask=float(tick.ask) if tick.ask is not None else None,
            volume=tick.volume,
            source=tick.source,
        )


async def run_ingestor() -> None:
    """
    Continuously drain the queue in BATCH_FLUSH_MS windows.
    Runs until _running is set to False.
    """
    global _running, _ticks_ingested_total, _ticks_this_window
    global _ticks_per_second, _window_start

    _running = True
    flush_interval = settings.batch_flush_ms / 1000.0
    logger.info("Ingestor started (flush interval: %dms)", settings.batch_flush_ms)

    while _running:
        await asyncio.sleep(flush_interval)

        batch: list[Tick] = []
        while not _queue.empty():
            try:
                batch.append(_queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        if not batch:
            continue

        try:
            # Write to Redis first (fast, in-memory)
            await _write_redis_batch(batch)

            # Bulk insert into TimescaleDB
            await _flush_batch(batch)

            # Update metrics
            now = time.monotonic()
            elapsed = now - _window_start
            _ticks_ingested_total += len(batch)
            _ticks_this_window += len(batch)

            if elapsed >= 1.0:
                _ticks_per_second = _ticks_this_window / elapsed
                _ticks_this_window = 0
                _window_start = now

            for tick in batch:
                _last_ingestion_time[tick.symbol] = tick.time

            logger.debug("Flushed %d ticks to DB", len(batch))

        except Exception as exc:
            logger.error("Ingestor flush error: %s", exc, exc_info=True)


async def stop_ingestor() -> None:
    global _running
    _running = False
    logger.info("Ingestor stopped")
