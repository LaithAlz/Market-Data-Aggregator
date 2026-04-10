"""
GET /history/{ticker}?from=...&to=...&interval=1m

Returns OHLCV bars aggregated by TimescaleDB's time_bucket() function.

Supported intervals: 1m, 5m, 15m, 1h, 1d
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from db.session import engine

router = APIRouter()

INTERVAL_MAP = {
    "1m":  timedelta(minutes=1),
    "5m":  timedelta(minutes=5),
    "15m": timedelta(minutes=15),
    "1h":  timedelta(hours=1),
    "1d":  timedelta(days=1),
}


class OHLCVBar(BaseModel):
    time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: Optional[int]


@router.get("/history/{ticker}", response_model=list[OHLCVBar])
async def get_history(
    ticker: str,
    from_: datetime = Query(alias="from"),
    to: datetime = Query(default=None),
    interval: str = Query(default="1m"),
) -> list[OHLCVBar]:
    symbol = ticker.upper()

    if interval not in INTERVAL_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid interval '{interval}'. Supported: {', '.join(INTERVAL_MAP)}",
        )

    bucket = INTERVAL_MAP[interval]

    if to is None:
        to = datetime.now(tz=timezone.utc)

    if from_.tzinfo is None:
        from_ = from_.replace(tzinfo=timezone.utc)
    if to.tzinfo is None:
        to = to.replace(tzinfo=timezone.utc)

    if from_ >= to:
        raise HTTPException(status_code=400, detail="'from' must be before 'to'")

    # time_bucket_gapfill would fill empty buckets, but requires TimescaleDB
    # Toolkit. We use plain time_bucket for compatibility with the base image.
    #
    # first() and last() are TimescaleDB aggregate functions that return the
    # value at the minimum/maximum time within each bucket respectively.
    sql = text("""
        SELECT
            time_bucket(:bucket, time)        AS bucket_time,
            first(price, time)                AS open,
            MAX(price)                        AS high,
            MIN(price)                        AS low,
            last(price, time)                 AS close,
            SUM(volume)                       AS volume
        FROM ticks
        WHERE
            symbol = :symbol
            AND time >= :from_ts
            AND time <  :to_ts
        GROUP BY bucket_time
        ORDER BY bucket_time ASC
    """)

    async with engine.connect() as conn:
        result = await conn.execute(
            sql,
            {
                "bucket": bucket,
                "symbol": symbol,
                "from_ts": from_,
                "to_ts": to,
            },
        )
        rows = result.fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail=f"No history for {symbol} in the requested range",
        )

    return [
        OHLCVBar(
            time=row.bucket_time,
            open=float(row.open),
            high=float(row.high),
            low=float(row.low),
            close=float(row.close),
            volume=int(row.volume) if row.volume is not None else None,
        )
        for row in rows
    ]
