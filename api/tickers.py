from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import select

from cache.redis_client import get_all_latest_prices
from config import settings
from db.models import Ticker
from db.session import get_session

router = APIRouter()


class TickerResponse(BaseModel):
    symbol: str
    name: Optional[str]
    latest_price: Optional[float]
    last_updated: Optional[str]


@router.get("/tickers", response_model=list[TickerResponse])
async def list_tickers() -> list[TickerResponse]:
    async with get_session() as session:
        result = await session.execute(select(Ticker).order_by(Ticker.symbol))
        rows = result.scalars().all()

    # If DB has no rows yet (first run), fall back to config symbols
    symbols = [r.symbol for r in rows] if rows else settings.symbols
    names = {r.symbol: r.name for r in rows}

    prices = await get_all_latest_prices(symbols)

    return [
        TickerResponse(
            symbol=sym,
            name=names.get(sym),
            latest_price=prices[sym]["price"] if prices.get(sym) else None,
            last_updated=prices[sym]["last_updated"] if prices.get(sym) else None,
        )
        for sym in symbols
    ]
