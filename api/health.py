import time
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from cache.redis_client import ping_redis
from db.session import engine
from feed.ws_client import is_connected

router = APIRouter()

_start_time = time.monotonic()


class HealthResponse(BaseModel):
    status: str
    db_connected: bool
    redis_connected: bool
    feed_connected: bool
    uptime_seconds: float
    timestamp: datetime


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    # Check DB
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    # Check Redis
    redis_ok = await ping_redis()

    # Feed status
    feed_ok = is_connected()

    all_ok = db_ok and redis_ok
    status = "healthy" if all_ok else "degraded"

    return HealthResponse(
        status=status,
        db_connected=db_ok,
        redis_connected=redis_ok,
        feed_connected=feed_ok,
        uptime_seconds=round(time.monotonic() - _start_time, 1),
        timestamp=datetime.now(tz=timezone.utc),
    )
