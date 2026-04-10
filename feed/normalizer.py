"""
Normalize raw Alpaca WebSocket payloads to internal Tick dataclass.

Alpaca message types we care about:
  T  — trade
  Q  — quote
  A  — bar (aggregate, ignored here)
  error / subscription  — control messages

Trade payload example:
  {"T":"t","S":"AAPL","i":123,"x":"C","p":182.50,"s":100,
   "t":"2024-01-15T14:30:00.123456789Z","c":["@","I"],"z":"C"}

Quote payload example:
  {"T":"q","S":"AAPL","ax":"C","ap":182.51,"as":3,
   "bx":"C","bp":182.49,"bs":2,"t":"2024-01-15T14:30:00.123456789Z","z":"C"}
"""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, field_validator, ValidationError

logger = logging.getLogger(__name__)


# ── Internal schema ────────────────────────────────────────────────────────────

@dataclass
class Tick:
    time: datetime
    symbol: str
    price: Decimal
    volume: Optional[int]
    bid: Optional[Decimal]
    ask: Optional[Decimal]
    source: str  # "trade" | "quote"


# ── Pydantic validators ────────────────────────────────────────────────────────

class _TradeMessage(BaseModel):
    T: str
    S: str
    p: Decimal          # price
    s: Optional[int] = None  # size / volume
    t: str              # timestamp (RFC3339)

    @field_validator("T")
    @classmethod
    def must_be_trade(cls, v: str) -> str:
        if v != "t":
            raise ValueError("not a trade message")
        return v


class _QuoteMessage(BaseModel):
    T: str
    S: str
    bp: Optional[Decimal] = None   # bid price
    ap: Optional[Decimal] = None   # ask price
    bs: Optional[int] = None       # bid size
    as_: Optional[int] = None      # ask size — aliased because 'as' is reserved
    t: str

    model_config = {"populate_by_name": True}

    @field_validator("T")
    @classmethod
    def must_be_quote(cls, v: str) -> str:
        if v != "q":
            raise ValueError("not a quote message")
        return v


def _parse_time(raw: str) -> datetime:
    """Parse Alpaca RFC3339 timestamps including nanoseconds."""
    # Truncate nanoseconds to microseconds for Python compatibility
    raw = raw.rstrip("Z")
    if "." in raw:
        base, frac = raw.split(".", 1)
        frac = frac[:6]
        raw = f"{base}.{frac}"
    return datetime.fromisoformat(raw).replace(tzinfo=timezone.utc)


def normalize(payload: dict[str, Any]) -> Optional[Tick]:
    """
    Convert a single Alpaca message dict to a Tick.
    Returns None and logs a warning for unrecognised or malformed messages.
    """
    msg_type = payload.get("T")

    if msg_type == "t":
        try:
            msg = _TradeMessage.model_validate(payload)
            return Tick(
                time=_parse_time(msg.t),
                symbol=msg.S,
                price=msg.p,
                volume=msg.s,
                bid=None,
                ask=None,
                source="trade",
            )
        except (ValidationError, Exception) as exc:
            logger.warning("Dropping malformed trade message: %s | %s", payload, exc)
            return None

    elif msg_type == "q":
        try:
            # 'as' is a Python keyword; Alpaca sends it as-is in JSON
            if "as" in payload:
                payload = {**payload, "as_": payload.pop("as")}
            msg = _QuoteMessage.model_validate(payload)
            # Use mid-price as the representative price
            price: Optional[Decimal] = None
            if msg.bp is not None and msg.ap is not None:
                price = (msg.bp + msg.ap) / 2
            elif msg.bp is not None:
                price = msg.bp
            elif msg.ap is not None:
                price = msg.ap

            if price is None:
                logger.warning("Quote has no bid or ask price, dropping: %s", payload)
                return None

            return Tick(
                time=_parse_time(msg.t),
                symbol=msg.S,
                price=price,
                volume=None,
                bid=msg.bp,
                ask=msg.ap,
                source="quote",
            )
        except (ValidationError, Exception) as exc:
            logger.warning("Dropping malformed quote message: %s | %s", payload, exc)
            return None

    # Control messages (subscription confirmations, errors, bar aggregates, etc.)
    return None


def normalize_batch(messages: list[dict[str, Any]]) -> list[Tick]:
    """Normalize a list of raw messages, silently dropping None results."""
    ticks = []
    for msg in messages:
        tick = normalize(msg)
        if tick is not None:
            ticks.append(tick)
    return ticks
