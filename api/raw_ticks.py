"""
GET /ticks/{ticker}?limit=200

Returns the most recent raw tick records for a symbol — each row is one
price event (trade or quote) with its exact timestamp.
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text

from db.session import engine

router = APIRouter()


class RawTick(BaseModel):
    time: datetime
    price: float
    bid: Optional[float]
    ask: Optional[float]
    volume: Optional[int]
    source: str


@router.get("/ticks/{ticker}", response_model=list[RawTick])
async def get_raw_ticks(
    ticker: str,
    limit: int = Query(default=200, ge=1, le=2000),
) -> list[RawTick]:
    symbol = ticker.upper()

    sql = text("""
        SELECT time, price, bid, ask, volume, source
        FROM ticks
        WHERE symbol = :symbol
        ORDER BY time DESC
        LIMIT :limit
    """)

    async with engine.connect() as conn:
        result = await conn.execute(sql, {"symbol": symbol, "limit": limit})
        rows = result.fetchall()

    if not rows:
        raise HTTPException(status_code=404, detail=f"No tick data for {symbol}")

    # Return chronological order (oldest first)
    return [
        RawTick(
            time=row.time,
            price=float(row.price),
            bid=float(row.bid) if row.bid is not None else None,
            ask=float(row.ask) if row.ask is not None else None,
            volume=row.volume,
            source=row.source,
        )
        for row in reversed(rows)
    ]
