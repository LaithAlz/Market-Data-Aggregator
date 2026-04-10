"""
Test fixtures.

Tests use an in-memory SQLite DB via the async SQLAlchemy engine so they
don't require a running PostgreSQL. TimescaleDB-specific SQL (create_hypertable,
time_bucket) is mocked or skipped in unit tests.

Integration tests that need the real DB are marked with @pytest.mark.integration
and are skipped unless RUN_INTEGRATION=1 is set.
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Point to a throw-away SQLite DB so unit tests need no infrastructure
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture
async def app():
    """Return a FastAPI test app with mocked startup side-effects."""
    with (
        patch("main._run_migrations", new_callable=AsyncMock),
        patch("main._seed_tickers", new_callable=AsyncMock),
        patch("main.start_feed", new_callable=AsyncMock),
        patch("main.stop_feed", new_callable=AsyncMock),
        patch("main.run_ingestor", new_callable=AsyncMock),
        patch("main.stop_ingestor", new_callable=AsyncMock),
        patch("main.close_redis", new_callable=AsyncMock),
    ):
        from main import app as fastapi_app
        yield fastapi_app


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
