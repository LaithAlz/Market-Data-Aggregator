"""
Alpaca REST client — fetches latest trades for all configured symbols.

Used on startup to seed Redis with the last known price so the dashboard
shows a value even when the market is closed.

Endpoint:
    GET https://data.alpaca.markets/v2/stocks/trades/latest
    ?symbols=AAPL,GOOGL,...&feed=iex
"""
import logging
from decimal import Decimal
from typing import Optional

import httpx

from cache.redis_client import set_latest_price
from config import settings
from feed.normalizer import _parse_time

logger = logging.getLogger(__name__)

_ALPACA_DATA_URL = "https://data.alpaca.markets/v2/stocks/trades/latest"


async def seed_latest_prices() -> None:
    """
    Fetch the most recent trade for each symbol from Alpaca's REST API
    and write it to Redis. Runs once on startup so the dashboard always
    shows the last known price (e.g. yesterday's close when market is shut).
    """
    symbols_param = ",".join(settings.symbols)
    headers = {
        "APCA-API-KEY-ID": settings.alpaca_api_key,
        "APCA-API-SECRET-KEY": settings.alpaca_api_secret,
    }
    params = {"symbols": symbols_param, "feed": "iex"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(_ALPACA_DATA_URL, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        logger.warning("Could not fetch latest prices from Alpaca REST API: %s", exc)
        return

    trades = data.get("trades", {})
    seeded = 0

    for symbol, trade in trades.items():
        try:
            price = float(Decimal(str(trade["p"])))
            volume = trade.get("s")
            await set_latest_price(
                symbol=symbol,
                price=price,
                bid=None,
                ask=None,
                volume=volume,
                source="trade",
            )
            seeded += 1
        except Exception as exc:
            logger.warning("Failed to seed price for %s: %s", symbol, exc)

    logger.info("Seeded latest prices for %d/%d symbols from REST API", seeded, len(settings.symbols))
