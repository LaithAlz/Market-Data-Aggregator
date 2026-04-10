"""
Alpaca WebSocket client — connects to the IEX real-time feed,
authenticates, subscribes to trades + quotes, and feeds ticks
to the ingestor queue.

Reconnect strategy: exponential backoff, max 5 retries.
  Attempt 1 → wait 1s
  Attempt 2 → wait 2s
  Attempt 3 → wait 4s
  Attempt 4 → wait 8s
  Attempt 5 → wait 16s
"""
import asyncio
import json
import logging
from typing import Optional

import websockets
from websockets.exceptions import ConnectionClosed, WebSocketException

from config import settings
from feed.ingestor import enqueue
from feed.normalizer import normalize

logger = logging.getLogger(__name__)

# ── Connection state exposed for /health ──────────────────────────────────────

_connected: bool = False
_task: Optional[asyncio.Task] = None


def is_connected() -> bool:
    return _connected


# ── Internal helpers ──────────────────────────────────────────────────────────

async def _authenticate(ws) -> bool:
    """Send auth message and wait for success response."""
    await ws.send(json.dumps({
        "action": "auth",
        "key": settings.alpaca_api_key,
        "secret": settings.alpaca_api_secret,
    }))
    response = json.loads(await ws.recv())
    # Alpaca sends a list; first item indicates auth result
    if isinstance(response, list):
        for msg in response:
            if msg.get("T") == "success" and msg.get("msg") == "authenticated":
                logger.info("Alpaca WebSocket authenticated")
                return True
            if msg.get("T") == "error":
                logger.error("Auth error from Alpaca: %s", msg)
                return False
    logger.error("Unexpected auth response: %s", response)
    return False


async def _subscribe(ws) -> None:
    """Subscribe to trades and quotes for all configured symbols."""
    payload = {
        "action": "subscribe",
        "trades": settings.symbols,
        "quotes": settings.symbols,
    }
    await ws.send(json.dumps(payload))
    response = json.loads(await ws.recv())
    logger.info("Subscription response: %s", response)


async def _consume(ws) -> None:
    """Read messages from the WebSocket and push ticks to the ingestor."""
    global _connected
    _connected = True
    async for raw in ws:
        messages = json.loads(raw)
        if not isinstance(messages, list):
            messages = [messages]
        for msg in messages:
            tick = normalize(msg)
            if tick is not None:
                enqueue(tick)


async def _run_feed() -> None:
    """
    Single connection lifecycle: connect → auth → subscribe → consume.
    Raises on failure so the retry wrapper can handle backoff.
    """
    logger.info("Connecting to Alpaca WebSocket: %s", settings.alpaca_ws_url)
    async with websockets.connect(
        settings.alpaca_ws_url,
        ping_interval=20,
        ping_timeout=20,
        close_timeout=10,
    ) as ws:
        # Alpaca sends a welcome message on connect
        welcome = json.loads(await ws.recv())
        logger.debug("Welcome message: %s", welcome)

        if not await _authenticate(ws):
            raise RuntimeError("Authentication failed")

        await _subscribe(ws)
        await _consume(ws)


async def _run_with_backoff() -> None:
    """Connect and reconnect with exponential backoff (max 5 retries)."""
    global _connected

    max_retries = 5
    attempt = 0

    while True:
        try:
            await _run_feed()
        except (ConnectionClosed, WebSocketException, OSError) as exc:
            _connected = False
            attempt += 1
            if attempt > max_retries:
                logger.error(
                    "WebSocket feed failed after %d retries. Giving up.", max_retries
                )
                return

            backoff = 2 ** (attempt - 1)  # 1, 2, 4, 8, 16 seconds
            logger.warning(
                "WebSocket disconnected (%s). Retrying in %ds (attempt %d/%d)...",
                exc,
                backoff,
                attempt,
                max_retries,
            )
            await asyncio.sleep(backoff)
        except asyncio.CancelledError:
            _connected = False
            logger.info("WebSocket feed task cancelled")
            return
        except Exception as exc:
            _connected = False
            logger.error("Unexpected feed error: %s", exc, exc_info=True)
            attempt += 1
            if attempt > max_retries:
                return
            backoff = 2 ** (attempt - 1)
            await asyncio.sleep(backoff)
        else:
            # Clean exit (server closed connection), reset attempt counter
            _connected = False
            attempt = 0


# ── Public API ────────────────────────────────────────────────────────────────

async def start_feed() -> None:
    """Launch the WebSocket feed as a background asyncio task."""
    global _task
    _task = asyncio.create_task(_run_with_backoff(), name="ws_feed")
    logger.info("WebSocket feed task started")


async def stop_feed() -> None:
    """Cancel the WebSocket feed task."""
    global _task, _connected
    if _task is not None and not _task.done():
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
    _connected = False
    _task = None
    logger.info("WebSocket feed task stopped")
