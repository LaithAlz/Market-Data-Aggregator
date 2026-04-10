"""
FastAPI application entry point.

Startup sequence:
  1. Run Alembic migrations
  2. Seed tickers table from config
  3. Start ingestor loop (background asyncio task)
  4. Start WebSocket feed (background asyncio task)

Shutdown sequence:
  1. Stop WebSocket feed (cancel task, close connection)
  2. Stop ingestor (flush remaining buffer, then exit loop)
  3. Close DB engine + Redis connection
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config as AlembicConfig
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import insert, select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from api import health, history, prices, raw_ticks, tickers
from cache.redis_client import close_redis
from config import settings
from db.models import Ticker
from db.session import engine, get_session
from feed.ingestor import run_ingestor, stop_ingestor
from feed.rest_client import seed_latest_prices
from feed.ws_client import start_feed, stop_feed

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


async def _run_migrations() -> None:
    alembic_cfg = AlembicConfig("alembic.ini")
    # Run in thread pool so we don't block the event loop
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
    logger.info("Database migrations applied")


async def _seed_tickers() -> None:
    """Insert tracked symbols into the tickers table if they don't exist."""
    async with get_session() as session:
        for symbol in settings.symbols:
            stmt = (
                pg_insert(Ticker)
                .values(symbol=symbol, name=None)
                .on_conflict_do_nothing(index_elements=["symbol"])
            )
            await session.execute(stmt)
    logger.info("Tickers seeded: %s", settings.symbols)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    # await _run_migrations()  # migrations already applied
    await _seed_tickers()

    await seed_latest_prices()

    ingestor_task = asyncio.create_task(run_ingestor(), name="ingestor")
    await start_feed()

    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    await stop_feed()
    await stop_ingestor()
    ingestor_task.cancel()
    try:
        await ingestor_task
    except asyncio.CancelledError:
        pass

    await engine.dispose()
    await close_redis()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Market Feed",
    description="Real-time stock price aggregator backed by TimescaleDB + Redis",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(tickers.router)
app.include_router(prices.router)
app.include_router(history.router)
app.include_router(raw_ticks.router)


@app.get("/", include_in_schema=False)
async def serve_ui() -> FileResponse:
    return FileResponse("ui/index.html")
