"""Unit tests for the normalizer — no infrastructure required."""
from decimal import Decimal

import pytest

from feed.normalizer import normalize, normalize_batch


# ── Trade messages ─────────────────────────────────────────────────────────────

def test_normalize_trade_basic():
    payload = {
        "T": "t",
        "S": "AAPL",
        "p": "182.50",
        "s": 100,
        "t": "2024-01-15T14:30:00.123456789Z",
        "x": "C",
    }
    tick = normalize(payload)
    assert tick is not None
    assert tick.symbol == "AAPL"
    assert tick.price == Decimal("182.50")
    assert tick.volume == 100
    assert tick.bid is None
    assert tick.ask is None
    assert tick.source == "trade"
    assert tick.time.year == 2024


def test_normalize_trade_missing_price_returns_none():
    payload = {
        "T": "t",
        "S": "AAPL",
        "t": "2024-01-15T14:30:00Z",
    }
    tick = normalize(payload)
    assert tick is None


# ── Quote messages ─────────────────────────────────────────────────────────────

def test_normalize_quote_basic():
    payload = {
        "T": "q",
        "S": "MSFT",
        "bp": "415.10",
        "ap": "415.12",
        "bs": 5,
        "as": 3,
        "t": "2024-01-15T14:30:00.000000000Z",
        "z": "C",
    }
    tick = normalize(payload)
    assert tick is not None
    assert tick.symbol == "MSFT"
    assert tick.bid == Decimal("415.10")
    assert tick.ask == Decimal("415.12")
    # Mid-price
    assert tick.price == (Decimal("415.10") + Decimal("415.12")) / 2
    assert tick.source == "quote"


def test_normalize_quote_bid_only():
    payload = {
        "T": "q",
        "S": "TSLA",
        "bp": "220.00",
        "t": "2024-01-15T14:30:00Z",
    }
    tick = normalize(payload)
    assert tick is not None
    assert tick.price == Decimal("220.00")
    assert tick.ask is None


def test_normalize_quote_no_prices_returns_none():
    payload = {
        "T": "q",
        "S": "AMZN",
        "t": "2024-01-15T14:30:00Z",
    }
    tick = normalize(payload)
    assert tick is None


# ── Control messages ───────────────────────────────────────────────────────────

def test_normalize_subscription_message_returns_none():
    payload = {"T": "subscription", "trades": ["AAPL"], "quotes": ["AAPL"]}
    assert normalize(payload) is None


def test_normalize_error_message_returns_none():
    payload = {"T": "error", "code": 400, "msg": "invalid syntax"}
    assert normalize(payload) is None


def test_normalize_unknown_type_returns_none():
    payload = {"T": "A", "S": "AAPL", "o": 182.0, "h": 183.0, "l": 181.0, "c": 182.5}
    assert normalize(payload) is None


# ── Batch normalizer ───────────────────────────────────────────────────────────

def test_normalize_batch_filters_nones():
    messages = [
        {"T": "t", "S": "AAPL", "p": "182.50", "s": 50, "t": "2024-01-15T14:30:00Z"},
        {"T": "error", "code": 400, "msg": "bad"},
        {"T": "q", "S": "GOOGL", "bp": "175.00", "ap": "175.02", "t": "2024-01-15T14:30:00Z"},
        {"T": "subscription"},
    ]
    ticks = normalize_batch(messages)
    assert len(ticks) == 2
    assert ticks[0].symbol == "AAPL"
    assert ticks[1].symbol == "GOOGL"


# ── Timestamp parsing ──────────────────────────────────────────────────────────

def test_nanosecond_timestamp_parsed_correctly():
    payload = {
        "T": "t",
        "S": "AAPL",
        "p": "100.00",
        "s": 1,
        "t": "2024-06-01T09:30:00.123456789Z",
    }
    tick = normalize(payload)
    assert tick is not None
    assert tick.time.microsecond == 123456  # nanoseconds truncated to microseconds
