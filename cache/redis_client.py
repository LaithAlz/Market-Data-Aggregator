"""
Redis client — stores latest price per ticker as a hash.

Key schema:
    price:{SYMBOL}  →  hash with fields: price, bid, ask, volume, last_updated, source
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import redis.asyncio as aioredis

from config import settings

logger = logging.getLogger(__name__)

_redis: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,
            socket_keepalive=True,
        )
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


def _price_key(symbol: str) -> str:
    return f"price:{symbol.upper()}"


async def set_latest_price(
    symbol: str,
    price: float,
    bid: Optional[float],
    ask: Optional[float],
    volume: Optional[int],
    source: str,
) -> None:
    r = await get_redis()
    now = datetime.now(tz=timezone.utc).isoformat()
    mapping = {
        "price": str(price),
        "bid": str(bid) if bid is not None else "",
        "ask": str(ask) if ask is not None else "",
        "volume": str(volume) if volume is not None else "",
        "last_updated": now,
        "source": source,
    }
    await r.hset(_price_key(symbol), mapping=mapping)


async def get_latest_price(symbol: str) -> Optional[dict]:
    r = await get_redis()
    data = await r.hgetall(_price_key(symbol))
    if not data:
        return None
    return {
        "symbol": symbol.upper(),
        "price": float(data["price"]) if data.get("price") else None,
        "bid": float(data["bid"]) if data.get("bid") else None,
        "ask": float(data["ask"]) if data.get("ask") else None,
        "volume": int(data["volume"]) if data.get("volume") else None,
        "last_updated": data.get("last_updated"),
        "source": data.get("source"),
    }


async def get_all_latest_prices(symbols: list[str]) -> dict[str, Optional[dict]]:
    r = await get_redis()
    results = {}
    # Use pipeline for batched reads
    async with r.pipeline(transaction=False) as pipe:
        for symbol in symbols:
            pipe.hgetall(_price_key(symbol))
        raw_list = await pipe.execute()

    for symbol, data in zip(symbols, raw_list):
        if data:
            results[symbol] = {
                "symbol": symbol.upper(),
                "price": float(data["price"]) if data.get("price") else None,
                "bid": float(data["bid"]) if data.get("bid") else None,
                "ask": float(data["ask"]) if data.get("ask") else None,
                "volume": int(data["volume"]) if data.get("volume") else None,
                "last_updated": data.get("last_updated"),
                "source": data.get("source"),
            }
        else:
            results[symbol] = None
    return results


async def ping_redis() -> bool:
    try:
        r = await get_redis()
        return await r.ping()
    except Exception as exc:
        logger.warning("Redis ping failed: %s", exc)
        return False
