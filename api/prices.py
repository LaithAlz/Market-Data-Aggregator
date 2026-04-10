from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, desc

from cache.redis_client import get_latest_price
from db.models import Tick
from db.session import get_session

router = APIRouter()


class PriceResponse(BaseModel):
    symbol: str
    price: Optional[float]
    bid: Optional[float]
    ask: Optional[float]
    volume: Optional[int]
    last_updated: Optional[str]
    source: Optional[str]


@router.get("/prices/{ticker}", response_model=PriceResponse)
async def get_price(ticker: str) -> PriceResponse:
    symbol = ticker.upper()

    # 1. Try Redis first (sub-millisecond)
    cached = await get_latest_price(symbol)
    if cached:
        return PriceResponse(**cached)

    # 2. Fall back to TimescaleDB (Redis may be cold / ingestor restarted)
    async with get_session() as session:
        result = await session.execute(
            select(Tick)
            .where(Tick.symbol == symbol)
            .order_by(desc(Tick.time))
            .limit(1)
        )
        row = result.scalar_one_or_none()

    if row is None:
        raise HTTPException(status_code=404, detail=f"No price data for {symbol}")

    return PriceResponse(
        symbol=symbol,
        price=float(row.price),
        bid=float(row.bid) if row.bid is not None else None,
        ask=float(row.ask) if row.ask is not None else None,
        volume=row.volume,
        last_updated=row.time.isoformat(),
        source=row.source,
    )
