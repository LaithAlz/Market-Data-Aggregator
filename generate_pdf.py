"""Generate the comprehensive Market Feed study guide PDF."""
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, Preformatted, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

OUTPUT = "/Users/laith/Desktop/Market_Feed_Study_Guide.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    leftMargin=0.85 * inch,
    rightMargin=0.85 * inch,
    topMargin=0.85 * inch,
    bottomMargin=0.85 * inch,
)

styles = getSampleStyleSheet()

# ── Style definitions ──────────────────────────────────────────────────────────
cover_title = ParagraphStyle("CoverTitle", parent=styles["Title"],
    fontSize=32, textColor=colors.HexColor("#0f172a"),
    spaceAfter=8, alignment=TA_CENTER)

cover_sub = ParagraphStyle("CoverSub", parent=styles["Normal"],
    fontSize=13, textColor=colors.HexColor("#475569"),
    spaceAfter=4, alignment=TA_CENTER)

cover_label = ParagraphStyle("CoverLabel", parent=styles["Normal"],
    fontSize=10, textColor=colors.HexColor("#94a3b8"),
    spaceAfter=2, alignment=TA_CENTER)

h1 = ParagraphStyle("H1", parent=styles["Heading1"],
    fontSize=17, textColor=colors.HexColor("#0f172a"),
    spaceBefore=22, spaceAfter=8,
    borderPad=0, leading=20)

h2 = ParagraphStyle("H2", parent=styles["Heading2"],
    fontSize=13, textColor=colors.HexColor("#1e40af"),
    spaceBefore=14, spaceAfter=5, leading=16)

h3 = ParagraphStyle("H3", parent=styles["Heading3"],
    fontSize=11, textColor=colors.HexColor("#334155"),
    spaceBefore=10, spaceAfter=4, leading=14,
    fontName="Helvetica-Bold")

body = ParagraphStyle("Body", parent=styles["Normal"],
    fontSize=9.5, textColor=colors.HexColor("#1e293b"),
    leading=15, spaceAfter=6, alignment=TA_JUSTIFY)

bullet = ParagraphStyle("Bullet", parent=body,
    leftIndent=18, bulletIndent=6, spaceAfter=3)

subbullet = ParagraphStyle("SubBullet", parent=body,
    leftIndent=34, bulletIndent=22, spaceAfter=2, fontSize=9)

code_s = ParagraphStyle("Code", parent=styles["Code"],
    fontSize=7.8, leading=11,
    textColor=colors.HexColor("#1e293b"),
    backColor=colors.HexColor("#f1f5f9"),
    borderPad=8, leftIndent=8, rightIndent=8,
    spaceAfter=8, spaceBefore=4,
    fontName="Courier")

inline_code = ParagraphStyle("InlineCode", parent=body,
    fontName="Courier", fontSize=8.5,
    backColor=colors.HexColor("#f1f5f9"),
    textColor=colors.HexColor("#0f172a"))

note = ParagraphStyle("Note", parent=body,
    backColor=colors.HexColor("#eff6ff"),
    borderPad=8, leftIndent=10, rightIndent=10,
    spaceBefore=6, spaceAfter=8,
    textColor=colors.HexColor("#1e40af"),
    borderColor=colors.HexColor("#bfdbfe"),
    fontSize=9)

warn = ParagraphStyle("Warn", parent=body,
    backColor=colors.HexColor("#fff7ed"),
    borderPad=8, leftIndent=10, rightIndent=10,
    spaceBefore=6, spaceAfter=8,
    textColor=colors.HexColor("#9a3412"),
    fontSize=9)

qa_q = ParagraphStyle("QAQ", parent=body,
    fontName="Helvetica-Bold", fontSize=10,
    textColor=colors.HexColor("#1e3a5f"),
    spaceBefore=12, spaceAfter=3)

qa_a = ParagraphStyle("QAA", parent=body,
    leftIndent=12, fontSize=9.5,
    textColor=colors.HexColor("#1e293b"),
    spaceAfter=4)

# ── Helper functions ───────────────────────────────────────────────────────────
def P(text, style=None): return Paragraph(text, style or body)
def B(text): return Paragraph(f"<bullet>&bull;</bullet> {text}", bullet)
def BB(text): return Paragraph(f"<bullet>&#8211;</bullet> {text}", subbullet)
def Code(text): return Preformatted(text, code_s)
def SP(n=8): return Spacer(1, n)
def HR(): return HRFlowable(width="100%", thickness=0.5,
    color=colors.HexColor("#e2e8f0"), spaceAfter=6, spaceBefore=6)
def Note(text): return Paragraph(f"<b>Note:</b> {text}", note)
def Warn(text): return Paragraph(f"<b>Important:</b> {text}", warn)
def Q(text): return Paragraph(text, qa_q)
def A(text): return Paragraph(text, qa_a)
def H1(text): return Paragraph(text, h1)
def H2(text): return Paragraph(text, h2)
def H3(text): return Paragraph(text, h3)

def make_table(data, col_widths, header_bg="#1e293b"):
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(-1,0), colors.HexColor(header_bg)),
        ("TEXTCOLOR",    (0,0),(-1,0), colors.white),
        ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.HexColor("#f8fafc"),colors.white]),
        ("GRID",         (0,0),(-1,-1), 0.4, colors.HexColor("#e2e8f0")),
        ("LEFTPADDING",  (0,0),(-1,-1), 7),
        ("RIGHTPADDING", (0,0),(-1,-1), 7),
        ("TOPPADDING",   (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
    ]))
    return t

story = []

# ══════════════════════════════════════════════════════════════════════════════
# COVER
# ══════════════════════════════════════════════════════════════════════════════
story += [
    SP(1.0*inch),
    Paragraph("Market Feed", cover_title),
    Paragraph("Complete System Study Guide", cover_sub),
    SP(6),
    Paragraph("Real-Time Stock Price Aggregator", cover_label),
    SP(0.4*inch),
    HR(),
    SP(0.2*inch),
    P("This document is a complete technical reference for the Market Feed system. "
      "It covers every file, every design decision, every alternative that was considered, "
      "and every question that could come up in an interview or code review. "
      "Read it end to end before any technical presentation on this codebase.", body),
    SP(0.2*inch),
]

toc_data = [
    ["Section", "Topic"],
    ["1", "What Is This System — Business Context"],
    ["2", "Architecture Overview & Data Flow"],
    ["3", "Technology Choices — Full Comparison"],
    ["4", "config.py — Settings & Environment"],
    ["5", "db/models.py — Database Schema & TimescaleDB"],
    ["6", "db/session.py — Connection Pool & Async Driver"],
    ["7", "db/migrations/ — Schema Evolution with Alembic"],
    ["8", "feed/ws_client.py — WebSocket Connection & Reconnect"],
    ["9", "feed/normalizer.py — Message Parsing & Validation"],
    ["10", "feed/ingestor.py — Buffered Write Engine"],
    ["11", "cache/redis_client.py — Redis Caching Layer"],
    ["12", "feed/rest_client.py — Startup Price Seeding"],
    ["13", "api/ — REST Endpoints (all four)"],
    ["14", "main.py — Application Lifespan"],
    ["15", "cli/dashboard.py — Terminal Dashboard"],
    ["16", "Concurrency Model — asyncio Deep Dive"],
    ["17", "End-to-End Trace — One Tick Through the System"],
    ["18", "Interview Q&A — 30 Questions with Full Answers"],
    ["19", "Docker & Docker Compose — Infrastructure as Code"],
    ["20", "Makefile — Developer Workflow Automation"],
    ["21", "Testing Strategy — What's Tested and Why"],
    ["22", "Security — Current Gaps and Production Fixes"],
    ["23", "Deployment & Observability"],
    ["24", "What Production Would Add"],
    ["25", "Glossary"],
]
story.append(make_table(toc_data, [0.5*inch, 5.8*inch]))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 1. WHAT IS THIS SYSTEM
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("1. What Is This System — Business Context"))
story.append(P(
    "Market Feed is a <b>real-time financial data pipeline</b>. It connects to a live "
    "market data source (Alpaca Markets), continuously ingests every trade execution and "
    "quote update for a configured set of stock symbols, stores them in a time-series "
    "database for historical analysis, caches the latest price per symbol for fast reads, "
    "and exposes the data through a REST API. A terminal dashboard provides a live view "
    "of all prices updating in real time."
))
story.append(P(
    "Think of it as a stripped-down version of what Bloomberg Terminal, a hedge fund's "
    "market data infrastructure, or a retail brokerage's pricing engine runs internally. "
    "The core problems it solves are:"
))
story.append(B("<b>High-frequency ingest:</b> markets generate thousands of events per second; naive write-per-event approaches collapse under this load"))
story.append(B("<b>Dual read patterns:</b> 'latest price' (millisecond latency) and 'historical OHLCV' (analytical, range-based) require different storage strategies"))
story.append(B("<b>Resilience:</b> WebSocket feeds drop constantly; the system must reconnect automatically and continue serving data from cache while reconnecting"))
story.append(B("<b>Separation of concerns:</b> ingestion, storage, and serving are decoupled so each can be scaled or replaced independently"))
story.append(SP())
story.append(H2("1.1  What Is Alpaca Markets?"))
story.append(P(
    "Alpaca is a commission-free brokerage that also exposes a developer API. "
    "It offers two data tiers:"
))
story.append(B("<b>IEX feed (free):</b> the Investors Exchange consolidated feed. Real prices but with a slight delay vs. the official tape. Perfect for development and non-trading applications."))
story.append(B("<b>SIP feed (paid):</b> the Securities Information Processor — the official consolidated tape from all US exchanges. Required for production trading systems."))
story.append(P(
    "This system uses the IEX feed. The WebSocket URL is "
    "<code>wss://stream.data.alpaca.markets/v2/iex</code>. "
    "Alpaca streams two event types: <b>trades</b> (actual executions) and "
    "<b>quotes</b> (best bid/offer updates)."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 2. ARCHITECTURE OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("2. Architecture Overview & Data Flow"))
story.append(Code(
"""┌─────────────────────────────────────────────────────────────────────┐
│                        ALPACA MARKETS                               │
│               wss://stream.data.alpaca.markets/v2/iex               │
└──────────────────────────────┬──────────────────────────────────────┘
                               │  WebSocket (persistent TCP connection)
                               │  Messages: trades + quotes, JSON arrays
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  feed/ws_client.py                                                   │
│  • Manages connection lifecycle (auth, subscribe, consume)           │
│  • Exponential backoff on disconnect (1s,2s,4s,8s,16s)              │
│  • Calls normalizer.normalize() on each message                      │
│  • Calls ingestor.enqueue() for valid Ticks                          │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  normalize(raw_dict) -> Tick | None
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  feed/normalizer.py                                                  │
│  • Validates with Pydantic (_TradeMessage, _QuoteMessage)            │
│  • Computes mid-price for quotes: (bid + ask) / 2                   │
│  • Returns Tick dataclass (Decimal prices, UTC datetime)             │
│  • Returns None for control msgs (auth, subscription confirms)       │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  enqueue(tick)  [non-blocking]
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  feed/ingestor.py   asyncio.Queue(maxsize=50_000)                    │
│  • Every 500ms: drain queue -> build batch                           │
│  • Write latest-per-symbol to Redis (fast, in-memory)               │
│  • Bulk INSERT batch into TimescaleDB (ON CONFLICT DO NOTHING)       │
│  • Track metrics: ticks/sec, last ingestion time per symbol          │
└────────────────┬────────────────────────────┬────────────────────────┘
                 │                            │
                 ▼                            ▼
┌───────────────────────────┐    ┌────────────────────────────────────┐
│  Redis                    │    │  TimescaleDB (PostgreSQL)           │
│  Key: price:{SYMBOL}      │    │  Table: ticks (hypertable)         │
│  Type: Hash               │    │  Partitioned by time (7-day chunks) │
│  TTL: none (overwritten)  │    │  Composite PK: (time, symbol)      │
│  Read: ~0.2ms             │    │  Index: (symbol, time DESC)        │
└───────────┬───────────────┘    └──────────────┬─────────────────────┘
            │                                   │
            └──────────────┬────────────────────┘
                           │  reads
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  FastAPI REST API  (api/)                                            │
│  GET /health         -- DB + Redis + feed status                     │
│  GET /tickers        -- all symbols + latest price (Redis pipeline)  │
│  GET /prices/{sym}   -- one symbol (Redis -> DB fallback)            │
│  GET /history/{sym}  -- OHLCV via time_bucket() (TimescaleDB)        │
└──────────────────────────────┬───────────────────────────────────────┘
                               │  HTTP (polling every 1s)
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  cli/dashboard.py  (Rich terminal UI)                                │
│  • Fetches /tickers + /health in parallel                            │
│  • Fetches /prices/{sym} for each symbol in parallel                 │
│  • Renders live table with color-coded price movement               │
└──────────────────────────────────────────────────────────────────────┘"""))

story.append(H2("2.1  Why This Specific Shape?"))
story.append(P(
    "The architecture separates three fundamentally different concerns:"
))
story.append(B("<b>Write path (ingest):</b> WebSocket -> normalizer -> queue -> ingestor -> DB+Redis. Optimized for throughput. The queue decouples the fast WebSocket consumer from the slower DB writer."))
story.append(B("<b>Hot read path (latest price):</b> API -> Redis. Sub-millisecond. Redis holds exactly one value per symbol — always current."))
story.append(B("<b>Cold read path (history):</b> API -> TimescaleDB. Milliseconds to seconds. Full historical record with aggregation."))
story.append(P(
    "This is a classic <b>CQRS-lite pattern</b> (Command Query Responsibility Segregation): "
    "the write path and the read paths are separated. The write path optimizes for ingest speed; "
    "the two read paths optimize for different access patterns independently."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 3. TECHNOLOGY CHOICES
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("3. Technology Choices — Full Comparison"))

story.append(H2("3.1  Why FastAPI and not Flask / Django?"))
table_fw = make_table([
    ["Framework", "Async", "Auto Docs", "Type Safety", "Verdict"],
    ["FastAPI",   "Native (asyncio)", "Yes (OpenAPI)", "Pydantic v2", "Best for async I/O APIs"],
    ["Flask",     "Via extension (messy)", "No", "None built-in", "Sync-first, wrong model here"],
    ["Django",    "Partial (ASGI)", "No", "None built-in", "Heavy ORM, not needed"],
    ["Starlette", "Native", "No", "None built-in", "FastAPI is built on this"],
], [1.1*inch, 1.3*inch, 1.2*inch, 1.2*inch, 1.5*inch])
story.append(table_fw)
story.append(P(
    "FastAPI was chosen because: (1) native async means no thread pool needed for concurrent "
    "requests, (2) Pydantic models define response schemas and auto-generate OpenAPI docs "
    "at <code>/docs</code>, (3) it's built on Starlette which is the fastest Python ASGI framework."
))

story.append(H2("3.2  Why TimescaleDB and not alternatives?"))
table_db = make_table([
    ["Database", "SQL?", "OHLCV agg", "Partitioning", "Ops Complexity", "Best For"],
    ["TimescaleDB", "Yes (PG)", "time_bucket() native", "Auto by time", "Low (PG-compatible)", "THIS PROJECT"],
    ["InfluxDB", "No (Flux)", "Custom", "Auto", "Medium", "Pure metrics/IoT"],
    ["ClickHouse", "Yes", "Native", "Manual", "High", "Analytics at massive scale"],
    ["PostgreSQL", "Yes", "Manual", "Manual", "Low", "Low volume (<1M rows)"],
    ["Cassandra", "CQL", "None", "Manual", "Very High", "Distributed, write-heavy"],
    ["QuestDB", "SQL", "Native", "Auto", "Low", "Similar to TimescaleDB"],
], [1.1*inch, 0.6*inch, 1.2*inch, 1.0*inch, 1.1*inch, 1.2*inch])
story.append(table_db)
story.append(P(
    "<b>The key argument for TimescaleDB:</b> it IS PostgreSQL. Same wire protocol, same SQL, "
    "same ACID guarantees, same drivers, same ecosystem. The team gets hypertable partitioning, "
    "<code>time_bucket()</code>, <code>first()</code>/<code>last()</code> aggregates, and "
    "compression — without learning a new query language or giving up joins, transactions, "
    "or foreign keys. Migrating FROM plain PostgreSQL TO TimescaleDB is one SQL call: "
    "<code>SELECT create_hypertable('ticks', 'time')</code>."
))

story.append(H2("3.3  Why Redis and not alternatives?"))
table_cache = make_table([
    ["Option", "Latency", "Data Structure", "Persistence", "Verdict"],
    ["Redis Hash", "~0.2ms", "Field-value map", "Optional (AOF)", "Ideal: atomic multi-field read"],
    ["Memcached", "~0.2ms", "Key-value only", "None", "No hash type, need serialize/deserialize"],
    ["PostgreSQL query", "1-5ms", "Rows", "Yes (WAL)", "Too slow for hot path"],
    ["In-process dict", "~0.001ms", "Dict", "None (lost on restart)", "Not shared across processes"],
    ["Elasticsearch", "5-20ms", "Documents", "Yes", "Overkill, wrong use case"],
], [1.3*inch, 0.8*inch, 1.3*inch, 1.1*inch, 2.0*inch])
story.append(table_cache)
story.append(P(
    "Redis Hash is perfect here: <code>HGETALL price:AAPL</code> returns all fields "
    "(price, bid, ask, volume, timestamp) atomically in one round-trip. With Memcached "
    "you'd have to serialize the whole object to a string and deserialize on read — "
    "more CPU and less flexible."
))

story.append(H2("3.4  Why asyncpg and not psycopg2?"))
table_pg = make_table([
    ["Driver", "Async?", "Protocol", "Speed", "Notes"],
    ["asyncpg", "Yes (native)", "Direct PG wire protocol", "Fastest", "Used here — no ORM overhead"],
    ["psycopg2", "No (blocking)", "libpq wrapper", "Baseline", "Blocks thread on every query"],
    ["psycopg3", "Yes", "libpq wrapper", "Good", "Newer, not as battle-tested"],
    ["aiopg",   "Yes (wrapper)", "wraps psycopg2", "Slower", "Extra layer of abstraction"],
], [0.9*inch, 1.0*inch, 1.7*inch, 0.9*inch, 2.0*inch])
story.append(table_pg)
story.append(P(
    "asyncpg implements the PostgreSQL wire protocol directly in Python/Cython — "
    "no C library wrapper (libpq). This makes it the fastest Python PostgreSQL driver "
    "and natively async. psycopg2 is blocking: every query parks the calling thread "
    "until the DB responds, which defeats the purpose of an async application."
))

story.append(H2("3.5  Why websockets library and not alternatives?"))
story.append(B("<b>websockets:</b> pure Python, asyncio-native, handles ping/keepalive automatically"))
story.append(B("<b>aiohttp WebSocket:</b> heavier, part of a full HTTP client framework — overkill for a dedicated WebSocket connection"))
story.append(B("<b>httpx WebSocket:</b> doesn't support WebSocket (httpx is HTTP/1.1 + HTTP/2 only)"))
story.append(B("<b>Alpaca Python SDK:</b> exists but it's an abstraction that hides the reconnect logic — we want explicit control over connection lifecycle"))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 4. CONFIG.PY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("4. config.py — Settings & Environment"))
story.append(Code(
"""from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class Settings(BaseSettings):
    # Alpaca credentials — REQUIRED, no default
    alpaca_api_key: str = Field(..., env="ALPACA_API_KEY")
    alpaca_api_secret: str = Field(..., env="ALPACA_API_SECRET")

    # WebSocket endpoint — has a sensible default
    alpaca_ws_url: str = "wss://stream.data.alpaca.markets/v2/iex"

    # Symbols to track — can be overridden in .env
    symbols: List[str] = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

    # PostgreSQL / TimescaleDB
    database_url: str = Field(
        "postgresql+asyncpg://market:market@localhost:5432/marketfeed",
        env="DATABASE_URL",
    )

    # Redis
    redis_url: str = Field("redis://localhost:6379/0", env="REDIS_URL")

    # How often to flush the ingestor batch (milliseconds)
    batch_flush_ms: int = 500

    # App
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()  # module-level singleton"""))

story.append(H2("4.1  Why pydantic-settings?"))
story.append(P(
    "The alternative is <code>os.getenv('ALPACA_API_KEY')</code> everywhere. Problems with that:"
))
story.append(B("No validation — a missing key returns None and causes a cryptic error later when the value is actually used (maybe deep inside a WebSocket auth call)"))
story.append(B("No type coercion — every value from os.getenv is a string; you'd manually convert integers, booleans, lists"))
story.append(B("Scattered — configuration reads are spread across files, not centralized"))
story.append(P(
    "Pydantic Settings gives you: fail-fast validation (missing required field = immediate "
    "startup crash with a clear message), automatic type coercion (the string '500' from "
    "<code>.env</code> becomes the int 500 for <code>batch_flush_ms</code>), and a "
    "single module everyone imports — <code>from config import settings</code>."
))

story.append(H2("4.2  Why a module-level singleton?"))
story.append(P(
    "<code>settings = Settings()</code> runs once when the module is first imported. "
    "Every subsequent <code>from config import settings</code> gets the same object — "
    "Python caches module imports. This means: (1) the .env file is parsed exactly once, "
    "(2) all modules share the same settings object, (3) you can mock it in tests by "
    "patching the module-level variable."
))

story.append(H2("4.3  The Field(...) syntax"))
story.append(P(
    "<code>Field(...)</code> — the <code>...</code> (Ellipsis) means 'required, no default'. "
    "If <code>ALPACA_API_KEY</code> is not set in the environment or .env file, pydantic "
    "raises a ValidationError immediately when <code>Settings()</code> is called. "
    "<code>env='ALPACA_API_KEY'</code> explicitly maps the field to that environment "
    "variable name (useful when the Python attribute name differs from the env var name)."
))

story.append(H2("4.4  Priority order for values"))
story.append(P(
    "Pydantic Settings reads values in this priority order (highest wins):"
))
story.append(B("1. Environment variables set in the shell (export ALPACA_API_KEY=...)"))
story.append(B("2. Values in the .env file"))
story.append(B("3. Default values in the class definition"))
story.append(P(
    "This means production deployments can inject secrets via environment variables "
    "without modifying the .env file — a 12-factor app pattern."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 5. DB/MODELS.PY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("5. db/models.py — Database Schema & TimescaleDB"))
story.append(Code(
"""from sqlalchemy import (BigInteger, Column, DateTime, Index,
                         Integer, Numeric, String, text)
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Ticker(Base):
    __tablename__ = "tickers"
    id       = Column(Integer, primary_key=True, autoincrement=True)
    symbol   = Column(String(16), unique=True, nullable=False, index=True)
    name     = Column(String(128), nullable=True)
    added_at = Column(DateTime(timezone=True), server_default=text("NOW()"))

class Tick(Base):
    __tablename__ = "ticks"
    # Composite primary key required by TimescaleDB hypertables
    time   = Column(DateTime(timezone=True), primary_key=True, nullable=False)
    symbol = Column(String(16), primary_key=True, nullable=False)
    price  = Column(Numeric(18, 6), nullable=False)
    volume = Column(BigInteger, nullable=True)
    bid    = Column(Numeric(18, 6), nullable=True)
    ask    = Column(Numeric(18, 6), nullable=True)
    source = Column(String(8), nullable=True)  # "trade" | "quote"

    __table_args__ = (
        Index("ix_ticks_symbol_time_desc", "symbol", text("time DESC")),
    )"""))

story.append(H2("5.1  Why the composite primary key (time, symbol)?"))
story.append(P(
    "TimescaleDB requires the time partition column to be part of the primary key. "
    "This is because TimescaleDB partitions the table into chunks by time range. "
    "Without the time column in the PK, PostgreSQL cannot enforce uniqueness across chunks. "
    "Adding symbol to the PK also prevents duplicate (time, symbol) pairs — which could "
    "happen if Alpaca sends the same event twice (network retries, reconnects)."
))
story.append(Note(
    "The ON CONFLICT DO NOTHING in the ingestor INSERT handles duplicates gracefully. "
    "If the same (time, symbol) pair arrives twice, the second insert is silently discarded."
))

story.append(H2("5.2  Why Numeric(18, 6) for prices?"))
story.append(P(
    "Numeric(18, 6) means: up to 18 significant digits total, with 6 decimal places. "
    "This gives us prices up to 999,999,999,999.999999 — more than enough for any stock "
    "price (Berkshire Hathaway Class A trades around $700,000). The 6 decimal places "
    "handle sub-penny prices (OTC stocks, forex pairs, crypto)."
))
story.append(P(
    "<b>Why not FLOAT?</b> Floating-point numbers use binary representation. Most decimal "
    "fractions cannot be represented exactly in binary. 182.50 as a double is actually "
    "182.49999999999997158... Numeric/Decimal uses base-10 arithmetic — no precision loss. "
    "In financial systems, using float for prices is a serious bug, not just a style issue."
))

story.append(H2("5.3  Why BigInteger for volume?"))
story.append(P(
    "Regular PostgreSQL INTEGER is 32-bit, max value ~2.1 billion. A single heavily-traded "
    "stock can have more than 2 billion shares traded in a session. BigInteger is 64-bit, "
    "max ~9.2 quintillion. Safe for any realistic volume."
))

story.append(H2("5.4  The composite index explained"))
story.append(Code(
"""Index("ix_ticks_symbol_time_desc", "symbol", text("time DESC"))"""))
story.append(P(
    "This index supports the most common query pattern: "
    "<i>give me the most recent ticks for a specific symbol</i>. "
    "The index orders by symbol first (equality filter), then by time descending "
    "(so the latest rows come first). Without this index, every "
    "<code>ORDER BY time DESC LIMIT 1</code> would be a full table scan. "
    "The <code>time DESC</code> direction matches the query's ORDER BY, so PostgreSQL "
    "can satisfy the query by reading the first few index entries instead of sorting."
))

story.append(H2("5.5  TimescaleDB Hypertables — Deep Dive"))
story.append(P(
    "When the migration runs <code>SELECT create_hypertable('ticks', 'time')</code>, "
    "TimescaleDB transforms the ticks table into a hypertable. Internally, TimescaleDB "
    "creates hidden child tables (chunks), each covering a time range (default: 7 days). "
    "The parent table is a transparent proxy — queries against 'ticks' automatically "
    "route to the right chunks."
))
story.append(P("<b>What this buys you:</b>"))
story.append(B("<b>Chunk exclusion:</b> WHERE time >= '2026-03-25' scans only the chunks that overlap that range. On a 6-month dataset, that's 1-2 chunks instead of 26."))
story.append(B("<b>time_bucket():</b> groups rows into fixed time intervals. time_bucket('1 minute', time) maps every timestamp to its minute boundary. Equivalent to date_trunc but for arbitrary intervals."))
story.append(B("<b>first(price, time):</b> returns price at the minimum time within the group. No equivalent in standard SQL — you'd need a subquery or window function."))
story.append(B("<b>last(price, time):</b> returns price at the maximum time within the group."))
story.append(B("<b>Compression:</b> ALTER TABLE ticks SET (timescaledb.compress = true) compresses old chunks. Typical compression ratio: 90%+ for time-series numerics."))
story.append(B("<b>Retention:</b> SELECT add_retention_policy('ticks', INTERVAL '90 days') auto-drops old chunks. No VACUUM needed."))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 6. DB/SESSION.PY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("6. db/session.py — Connection Pool & Async Driver"))
story.append(Code(
"""from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                     create_async_engine)
from config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=10,           # number of persistent connections
    max_overflow=20,        # burst connections above pool_size
    pool_pre_ping=True,     # verify connection health before use
    echo=False,             # set True to log all SQL (dev only)
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # don't expire objects after commit
    autoflush=False,          # don't auto-flush before queries
    autocommit=False,         # we manage transactions manually
)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()   # auto-commit on success
        except Exception:
            await session.rollback() # auto-rollback on error
            raise"""))

story.append(H2("6.1  Connection Pooling — Why and How"))
story.append(P(
    "Establishing a PostgreSQL connection is expensive: TCP handshake, authentication "
    "exchange, session setup. This takes 20-100ms. Doing this on every API request "
    "would add 20-100ms to every response — unacceptable."
))
story.append(P(
    "The connection pool maintains <b>10 persistent connections</b> (pool_size=10). "
    "When a request needs the DB, it borrows a connection from the pool, uses it, "
    "and returns it. Connection establishment overhead is paid once at startup."
))
story.append(P(
    "<b>max_overflow=20</b> allows up to 20 additional connections beyond pool_size "
    "during traffic spikes. These overflow connections are closed after use "
    "(not returned to the pool). Total max connections: 30."
))
story.append(P(
    "<b>pool_pre_ping=True</b> runs <code>SELECT 1</code> on a connection before handing "
    "it to a query. If the connection is stale (DB restarted, network timeout), the pool "
    "discards it and establishes a new one transparently. Without this, you'd get cryptic "
    "'connection already closed' errors after DB restarts."
))

story.append(H2("6.2  Why expire_on_commit=False?"))
story.append(P(
    "By default, SQLAlchemy expires all attributes on ORM objects after a commit. "
    "This means accessing object.price after a commit would trigger another SELECT "
    "to reload the data. In an async context this is dangerous — the session is "
    "already closed, so the reload fails. Setting expire_on_commit=False keeps "
    "object attributes accessible after the session closes."
))

story.append(H2("6.3  The get_session context manager pattern"))
story.append(P(
    "Usage: <code>async with get_session() as session:</code> gives you a session "
    "that auto-commits on clean exit and auto-rolls back on exception. "
    "This is the <b>Unit of Work</b> pattern — all operations within the block "
    "are either all committed or all rolled back. You never have to call "
    "commit() or rollback() manually."
))

story.append(H2("6.4  Why SQLAlchemy Core for bulk inserts (not ORM)?"))
story.append(P(
    "The ORM is designed for object-at-a-time operations. When you do "
    "<code>session.add(tick_obj)</code> and commit, SQLAlchemy generates "
    "one INSERT per object. For bulk inserts this is catastrophic. "
    "SQLAlchemy Core's <code>insert(TickModel).values(rows)</code> generates "
    "a single <code>INSERT INTO ticks VALUES (r1), (r2), ..., (rN)</code> statement — "
    "exactly what PostgreSQL is optimized for. The ingestor uses Core for this reason."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 7. MIGRATIONS
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("7. db/migrations/ — Schema Evolution with Alembic"))
story.append(Code(
"""# db/migrations/versions/001_initial.py

def upgrade() -> None:
    # Create tickers table
    op.create_table("tickers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("symbol", sa.String(16), nullable=False),
        sa.Column("name", sa.String(128), nullable=True),
        sa.Column("added_at", sa.DateTime(timezone=True),
                  server_default=sa.text("NOW()"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tickers_symbol", "tickers", ["symbol"], unique=True)

    # Create ticks table
    op.create_table("ticks",
        sa.Column("time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("symbol", sa.String(16), nullable=False),
        sa.Column("price", sa.Numeric(18, 6), nullable=False),
        sa.Column("volume", sa.BigInteger(), nullable=True),
        sa.Column("bid", sa.Numeric(18, 6), nullable=True),
        sa.Column("ask", sa.Numeric(18, 6), nullable=True),
        sa.Column("source", sa.String(8), nullable=True),
        sa.PrimaryKeyConstraint("time", "symbol"),
    )

    # THE KEY CALL — converts ticks into a hypertable
    op.execute("SELECT create_hypertable('ticks', 'time', if_not_exists => TRUE)")

    # Composite index for per-ticker queries
    op.create_index("ix_ticks_symbol_time_desc", "ticks",
                    ["symbol", sa.text("time DESC")])

def downgrade() -> None:
    op.drop_index("ix_ticks_symbol_time_desc", table_name="ticks")
    op.drop_table("ticks")
    op.drop_index("ix_tickers_symbol", table_name="tickers")
    op.drop_table("tickers")"""))

story.append(H2("7.1  What is Alembic?"))
story.append(P(
    "Alembic is SQLAlchemy's migration tool. It tracks which migrations have been applied "
    "in an <code>alembic_version</code> table in the database. "
    "<code>alembic upgrade head</code> applies all unapplied migrations in order. "
    "It's idempotent: running it when already at head does nothing. "
    "This is why <code>main.py</code> runs migrations on every startup — safe to always run."
))

story.append(H2("7.2  Why if_not_exists in create_hypertable?"))
story.append(P(
    "If the app restarts and the migration has already run, calling "
    "<code>create_hypertable</code> again would fail without <code>if_not_exists => TRUE</code>. "
    "This flag makes it a no-op if the hypertable already exists."
))

story.append(H2("7.3  Async Alembic — the env.py design"))
story.append(Code(
"""# db/migrations/env.py (simplified)
async def run_async_migrations() -> None:
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = get_url()  # reads from pydantic settings
    connectable = async_engine_from_config(cfg, prefix="sqlalchemy.",
                                           poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())"""))
story.append(P(
    "Alembic is normally synchronous. To work with asyncpg (async), the migrations run "
    "inside <code>asyncio.run()</code> which creates a new event loop in the calling thread. "
    "<code>NullPool</code> is used (no connection pool) because migrations run once and "
    "immediately dispose — no need for a pool."
))
story.append(P(
    "In <code>main.py</code>, this is called inside "
    "<code>await loop.run_in_executor(None, command.upgrade, alembic_cfg, 'head')</code> "
    "which offloads the synchronous Alembic CLI call to a thread pool, preventing it from "
    "blocking the asyncio event loop."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 8. WS_CLIENT.PY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("8. feed/ws_client.py — WebSocket Connection & Reconnect"))
story.append(Code(
"""# Full connection lifecycle
async def _run_feed() -> None:
    async with websockets.connect(
        settings.alpaca_ws_url,
        ping_interval=20,   # send WebSocket ping every 20s
        ping_timeout=20,    # fail if no pong within 20s
        close_timeout=10,   # wait up to 10s for clean close
    ) as ws:
        welcome = json.loads(await ws.recv())  # Alpaca sends welcome msg
        if not await _authenticate(ws):
            raise RuntimeError("Authentication failed")
        await _subscribe(ws)
        await _consume(ws)

async def _authenticate(ws) -> bool:
    await ws.send(json.dumps({
        "action": "auth",
        "key": settings.alpaca_api_key,
        "secret": settings.alpaca_api_secret,
    }))
    response = json.loads(await ws.recv())
    for msg in response:
        if msg.get("T") == "success" and msg.get("msg") == "authenticated":
            return True
        if msg.get("T") == "error":
            logger.error("Auth error: %s", msg)
            return False
    return False

async def _subscribe(ws) -> None:
    await ws.send(json.dumps({
        "action": "subscribe",
        "trades": settings.symbols,
        "quotes": settings.symbols,
    }))
    response = json.loads(await ws.recv())  # confirmation

async def _consume(ws) -> None:
    global _connected
    _connected = True
    async for raw in ws:           # yields each WebSocket frame
        messages = json.loads(raw) # Alpaca batches multiple events per frame
        if not isinstance(messages, list):
            messages = [messages]
        for msg in messages:
            tick = normalize(msg)
            if tick is not None:
                enqueue(tick)"""))

story.append(H2("8.1  The WebSocket protocol with Alpaca"))
story.append(P("The handshake sequence is fixed — Alpaca requires this exact order:"))
story.append(B("1. Connect to wss://stream.data.alpaca.markets/v2/iex"))
story.append(B("2. Receive welcome: [{\"T\":\"success\",\"msg\":\"connected\"}]"))
story.append(B("3. Send auth: {\"action\":\"auth\",\"key\":\"...\",\"secret\":\"...\"}"))
story.append(B("4. Receive auth response: [{\"T\":\"success\",\"msg\":\"authenticated\"}] or error"))
story.append(B("5. Send subscribe: {\"action\":\"subscribe\",\"trades\":[\"AAPL\",...],\"quotes\":[...]}"))
story.append(B("6. Receive subscription confirmation"))
story.append(B("7. Stream: Alpaca pushes trade/quote events continuously"))
story.append(P(
    "If you send subscribe before auth completes, Alpaca returns an error. "
    "The protocol is strictly sequential at the start."
))

story.append(H2("8.2  Exponential backoff — the math and reasoning"))
story.append(Code(
"""max_retries = 5
attempt = 0

while True:
    try:
        await _run_feed()
    except (ConnectionClosed, WebSocketException, OSError) as exc:
        _connected = False
        attempt += 1
        if attempt > max_retries:
            logger.error("Giving up after %d retries", max_retries)
            return
        backoff = 2 ** (attempt - 1)  # 1, 2, 4, 8, 16 seconds
        await asyncio.sleep(backoff)
    except asyncio.CancelledError:
        return  # clean shutdown, no retry
    else:
        # Clean server-side close (not an error), reset attempt counter
        _connected = False
        attempt = 0"""))
story.append(P(
    "<b>Why exponential backoff?</b> If the WebSocket drops because Alpaca's servers are "
    "overloaded and you immediately reconnect, you're hammering an already-overloaded system. "
    "This is how services get rate-banned. Exponential backoff gives the upstream time to recover."
))
story.append(P(
    "<b>Why max 5 retries?</b> Total wait: 1+2+4+8+16 = 31 seconds. Most transient "
    "outages resolve in seconds. If it hasn't recovered in 31 seconds, there's a "
    "structural problem (wrong credentials, Alpaca outage) that manual intervention "
    "is needed for. The system stops trying rather than retrying indefinitely."
))
story.append(P(
    "<b>Why reset attempt on clean close?</b> If Alpaca closes the connection cleanly "
    "(e.g., for maintenance), that's not an error. After reconnecting successfully, "
    "we reset the counter so the next disconnect starts fresh from attempt 1."
))

story.append(H2("8.3  ping_interval and ping_timeout"))
story.append(P(
    "WebSocket connections over the internet can silently die — the TCP connection "
    "appears open but no data flows (the other side is gone). WebSocket has a "
    "built-in Ping/Pong mechanism: the client sends a Ping frame, the server must "
    "respond with a Pong within ping_timeout seconds. If it doesn't, the connection "
    "is declared dead and reconnect logic kicks in. Without this, a silently dead "
    "connection could appear 'connected' indefinitely."
))

story.append(H2("8.4  The _connected module-level flag"))
story.append(P(
    "<code>_connected: bool = False</code> is a module-level variable. "
    "It's set to True when <code>_consume()</code> starts and False on any disconnect. "
    "The health endpoint reads it via <code>is_connected()</code>. "
    "This is simpler than passing state through the call stack — "
    "the WebSocket task owns the connection and directly updates this flag."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 9. NORMALIZER.PY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("9. feed/normalizer.py — Message Parsing & Validation"))
story.append(Code(
"""# Alpaca Trade message example:
# {"T":"t","S":"AAPL","i":123,"x":"C","p":182.50,"s":100,
#  "t":"2024-01-15T14:30:00.123456789Z","c":["@","I"],"z":"C"}

# Alpaca Quote message example:
# {"T":"q","S":"AAPL","ax":"C","ap":182.51,"as":3,
#  "bx":"C","bp":182.49,"bs":2,"t":"2024-01-15T14:30:00.123456789Z","z":"C"}

@dataclass
class Tick:
    time:   datetime
    symbol: str
    price:  Decimal           # NOT float
    volume: Optional[int]
    bid:    Optional[Decimal]
    ask:    Optional[Decimal]
    source: str               # "trade" | "quote"

class _TradeMessage(BaseModel):
    T: str    # message type — validated to be "t"
    S: str    # symbol
    p: Decimal  # price
    s: Optional[int] = None  # size/volume
    t: str    # timestamp (RFC3339 with nanoseconds)

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
    as_: Optional[int] = None      # ask size — "as" is reserved keyword!
    t: str
    model_config = {"populate_by_name": True}"""))

story.append(H2("9.1  Why Pydantic for validation?"))
story.append(P(
    "The alternative is manual validation: <code>if 'p' not in msg or not isinstance(msg['p'], (int, float))</code>. "
    "This gets unwieldy fast. Pydantic defines the expected shape declaratively and handles "
    "all edge cases: missing fields, wrong types, extra fields (ignored by default), "
    "custom validators. If validation fails, it raises ValidationError with a "
    "detailed message describing exactly what's wrong."
))
story.append(P(
    "Pydantic v2 (used here) is implemented in Rust (via pydantic-core) — "
    "validation is ~10-50x faster than Pydantic v1. For a system processing "
    "hundreds of messages per second, this matters."
))

story.append(H2("9.2  The 'as' keyword problem"))
story.append(Code(
"""# Alpaca sends: {"T":"q","S":"AAPL","as":3,"ap":182.51,...}
# "as" is a Python keyword (as in: import X as Y, with X as Y)
# You can't have a Pydantic field named "as"

# Solution: rename it before validation
if "as" in payload:
    payload = {**payload, "as_": payload.pop("as")}
# Now validate with model field named "as_"
msg = _QuoteMessage.model_validate(payload)"""))
story.append(P(
    "This is an unavoidable edge case when the data source uses Python reserved words "
    "as field names. The workaround creates a new dict (doesn't mutate the original) "
    "with the renamed key before Pydantic sees it."
))

story.append(H2("9.3  Timestamp parsing — nanoseconds"))
story.append(Code(
"""def _parse_time(raw: str) -> datetime:
    # Alpaca: "2024-01-15T14:30:00.123456789Z"  (nanoseconds = 9 digits)
    # Python datetime: microsecond precision only (6 digits)
    raw = raw.rstrip("Z")
    if "." in raw:
        base, frac = raw.split(".", 1)
        frac = frac[:6]   # truncate from 9 to 6 decimal places
        raw = f"{base}.{frac}"
    return datetime.fromisoformat(raw).replace(tzinfo=timezone.utc)"""))
story.append(P(
    "Alpaca timestamps have nanosecond precision (9 decimal places). Python's datetime "
    "only supports microseconds (6 decimal places). We truncate — not round — the "
    "last 3 digits. This means we lose up to 999 nanoseconds (< 1 microsecond) of precision. "
    "For a price display system this is completely acceptable."
))

story.append(H2("9.4  Quote mid-price calculation"))
story.append(Code(
"""# Use mid-price as the representative price for quotes
price: Optional[Decimal] = None
if msg.bp is not None and msg.ap is not None:
    price = (msg.bp + msg.ap) / 2   # mid-point
elif msg.bp is not None:
    price = msg.bp                   # only bid available
elif msg.ap is not None:
    price = msg.ap                   # only ask available

if price is None:
    return None  # quote with no prices at all — drop it"""))
story.append(P(
    "Quotes carry bid and ask prices but no single 'trade price'. The mid-point "
    "(bid + ask) / 2 is the standard representation for display purposes. "
    "It's what Bloomberg and most data terminals show. For actual trading you'd "
    "use bid or ask depending on direction, but for display the mid is correct."
))
story.append(P(
    "<b>Why Decimal division?</b> (182.49 + 182.51) / 2 as floats = 182.49999999999997. "
    "As Decimals = 182.500000 exactly. Always use Decimal for financial arithmetic."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 10. INGESTOR.PY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("10. feed/ingestor.py — Buffered Write Engine"))
story.append(Code(
"""# ── Queue ─────────────────────────────────────────────────────────────
_queue: asyncio.Queue[Tick] = asyncio.Queue(maxsize=50_000)
_running: bool = False

def enqueue(tick: Tick) -> None:
    \"\"\"Non-blocking. Drops tick if queue is full (backpressure).\"\"\"
    try:
        _queue.put_nowait(tick)
    except asyncio.QueueFull:
        logger.warning("Queue full — dropping tick for %s", tick.symbol)

# ── Main loop ─────────────────────────────────────────────────────────
async def run_ingestor() -> None:
    global _running
    _running = True
    flush_interval = settings.batch_flush_ms / 1000.0  # 0.5 seconds

    while _running:
        await asyncio.sleep(flush_interval)  # yield control, wait 500ms

        # Drain the queue
        batch: list[Tick] = []
        while not _queue.empty():
            try:
                batch.append(_queue.get_nowait())
            except asyncio.QueueEmpty:
                break

        if not batch:
            continue

        # Write Redis first (fast), then DB (slower)
        await _write_redis_batch(batch)
        await _flush_batch(batch)  # bulk INSERT"""))

story.append(H2("10.1  The queue — why asyncio.Queue?"))
story.append(P(
    "The WebSocket consumer (ws_client.py) and the ingestor (ingestor.py) run as "
    "separate asyncio tasks within the same event loop. They share the queue safely "
    "because asyncio is single-threaded — there are no race conditions. "
    "<code>asyncio.Queue</code> is the standard way for asyncio tasks to communicate."
))
story.append(P(
    "The maxsize=50_000 cap prevents unbounded memory growth. If the ingestor falls "
    "behind (e.g., DB is slow), ticks accumulate in the queue. Without a cap, the "
    "queue would grow until the process runs out of memory. With the cap, once full, "
    "new ticks are dropped — you lose some data but the process stays alive."
))

story.append(H2("10.2  Why put_nowait and not await put?"))
story.append(Code(
"""# put_nowait raises QueueFull immediately if queue is full
# await put() would block until space is available

# In the WebSocket consumer:
async for raw in ws:        # this is called ~500x per second
    enqueue(tick)           # must return immediately

# If enqueue blocked (await put), it would block the entire
# WebSocket consumer — no more messages would be read.
# put_nowait() either succeeds instantly or raises QueueFull."""))

story.append(H2("10.3  The bulk INSERT — ON CONFLICT DO NOTHING"))
story.append(Code(
"""async def _flush_batch(ticks: list[Tick]) -> None:
    rows = [
        {"time": tick.time, "symbol": tick.symbol,
         "price": tick.price, "volume": tick.volume,
         "bid": tick.bid, "ask": tick.ask, "source": tick.source}
        for tick in ticks
    ]
    async with engine.begin() as conn:
        stmt = insert(TickModel).values(rows).on_conflict_do_nothing()
        await conn.execute(stmt)"""))
story.append(P(
    "<code>engine.begin()</code> (not <code>engine.connect()</code>) gives a connection "
    "with a transaction already started. The transaction auto-commits at the end of the "
    "context and auto-rolls back on exception."
))
story.append(P(
    "<code>.on_conflict_do_nothing()</code> handles the case where a (time, symbol) pair "
    "already exists (from a previous insert attempt that partially succeeded before a crash, "
    "or from Alpaca resending messages on reconnect). The duplicate is silently discarded."
))

story.append(H2("10.4  Redis deduplication — latest per symbol"))
story.append(Code(
"""async def _write_redis_batch(ticks: list[Tick]) -> None:
    # If we got 50 AAPL ticks in this batch, only write the latest
    latest: dict[str, Tick] = {}
    for tick in ticks:
        if tick.symbol not in latest or tick.time > latest[tick.symbol].time:
            latest[tick.symbol] = tick

    for symbol, tick in latest.items():
        await set_latest_price(symbol=symbol, price=float(tick.price), ...)"""))
story.append(P(
    "Writing all 50 AAPL ticks to Redis would mean 50 writes to the same key, "
    "each overwriting the last. Only the final write survives. So we deduplicate "
    "in Python first and do one Redis write per symbol per batch. Saves ~49 Redis calls."
))

story.append(H2("10.5  Why write Redis before DB?"))
story.append(P(
    "Redis is written first because the dashboard reads from Redis. "
    "If we wrote DB first and then Redis, there'd be a window where the DB has the data "
    "but Redis doesn't — the dashboard would show stale data. "
    "By writing Redis first, the latest price is available as soon as possible. "
    "The DB write might take a few extra milliseconds, but that only affects historical "
    "queries (which are inherently backward-looking anyway)."
))

story.append(H2("10.6  Metrics tracking"))
story.append(Code(
"""# Rolling 1-second ticks-per-second calculation
_ticks_ingested_total: int = 0
_ticks_this_window: int = 0
_ticks_per_second: float = 0.0
_window_start: float = time.monotonic()

# After each flush:
now = time.monotonic()
elapsed = now - _window_start
_ticks_ingested_total += len(batch)
_ticks_this_window += len(batch)

if elapsed >= 1.0:  # reset window every second
    _ticks_per_second = _ticks_this_window / elapsed
    _ticks_this_window = 0
    _window_start = now"""))
story.append(P(
    "Using <code>time.monotonic()</code> not <code>time.time()</code>. "
    "Monotonic time only moves forward — it's immune to system clock adjustments "
    "(NTP sync, DST changes). For measuring elapsed time intervals, always use monotonic."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 11. REDIS_CLIENT.PY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("11. cache/redis_client.py — Redis Caching Layer"))
story.append(Code(
"""import redis.asyncio as aioredis

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

def _price_key(symbol: str) -> str:
    return f"price:{symbol.upper()}"

async def set_latest_price(symbol, price, bid, ask, volume, source) -> None:
    r = await get_redis()
    mapping = {
        "price": str(price),
        "bid":   str(bid) if bid is not None else "",
        "ask":   str(ask) if ask is not None else "",
        "volume": str(volume) if volume is not None else "",
        "last_updated": datetime.now(tz=timezone.utc).isoformat(),
        "source": source,
    }
    await r.hset(_price_key(symbol), mapping=mapping)

async def get_all_latest_prices(symbols: list[str]) -> dict:
    r = await get_redis()
    async with r.pipeline(transaction=False) as pipe:
        for symbol in symbols:
            pipe.hgetall(_price_key(symbol))
        raw_list = await pipe.execute()
    return {sym: parse(data) for sym, data in zip(symbols, raw_list)}"""))

story.append(H2("11.1  Why Redis Hash and not Redis String?"))
story.append(P(
    "We could store the price data as a JSON string in a Redis String key and serialize/deserialize on each access. "
    "Using a Hash is better because:"
))
story.append(B("<b>Atomic field updates:</b> HSET updates individual fields without touching others. A string requires read-modify-write which is not atomic."))
story.append(B("<b>Partial reads:</b> HGET symbol price reads just the price, not the whole object. With a string you'd deserialize everything even if you only need one field."))
story.append(B("<b>Introspection:</b> redis-cli HGETALL price:AAPL gives a readable output. A JSON blob is opaque."))

story.append(H2("11.2  The lazy singleton pattern"))
story.append(P(
    "<code>_redis = None</code> initially. <code>get_redis()</code> creates the connection "
    "on first call and caches it. This is a lazy singleton — the connection isn't established "
    "at import time but on first use. This is important because the connection needs the "
    "event loop to exist (asyncio), which isn't the case at import time."
))

story.append(H2("11.3  Pipeline for batch reads"))
story.append(Code(
"""# WITHOUT pipeline: 5 round-trips (one per symbol)
for symbol in symbols:
    data = await r.hgetall(f"price:{symbol}")

# WITH pipeline: 1 round-trip (all commands in one TCP write)
async with r.pipeline(transaction=False) as pipe:
    for symbol in symbols:
        pipe.hgetall(f"price:{symbol}")
    results = await pipe.execute()"""))
story.append(P(
    "Redis pipeline batches commands into a single TCP write and reads all responses at once. "
    "For 5 symbols, this is 5x fewer round-trips. At low latency (Redis on same host) "
    "this saves ~1ms. At higher latency (Redis in a different AZ) this can save 25ms+."
))
story.append(P(
    "<code>transaction=False</code> means the pipeline doesn't use MULTI/EXEC (Redis transactions). "
    "We don't need atomicity here — we just want batching. Avoiding MULTI/EXEC removes overhead."
))

story.append(H2("11.4  None values stored as empty strings"))
story.append(P(
    "Redis Hash values must be strings. <code>None</code> doesn't exist in Redis. "
    "We store absent values as empty string <code>''</code>. On read, we check "
    "<code>if data.get('bid')</code> — empty string is falsy in Python, so it "
    "correctly maps back to None."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 12. REST_CLIENT.PY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("12. feed/rest_client.py — Startup Price Seeding"))
story.append(Code(
"""_ALPACA_DATA_URL = "https://data.alpaca.markets/v2/stocks/trades/latest"

async def seed_latest_prices() -> None:
    \"\"\"
    Fetches the most recent trade per symbol from Alpaca REST API
    and writes it to Redis. Called once on startup so the dashboard
    shows prices even when the market is closed.
    \"\"\"
    headers = {
        "APCA-API-KEY-ID":     settings.alpaca_api_key,
        "APCA-API-SECRET-KEY": settings.alpaca_api_secret,
    }
    params = {
        "symbols": ",".join(settings.symbols),
        "feed":    "iex",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(_ALPACA_DATA_URL, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()

    trades = data.get("trades", {})
    for symbol, trade in trades.items():
        price = float(Decimal(str(trade["p"])))
        volume = trade.get("s")
        await set_latest_price(symbol=symbol, price=price,
                               bid=None, ask=None, volume=volume, source="trade")"""))

story.append(H2("12.1  Why REST API instead of WebSocket for this?"))
story.append(P(
    "The WebSocket feed only sends data when the market is open and events occur. "
    "Outside market hours (nights, weekends), no messages flow. The REST API "
    "<code>/v2/stocks/trades/latest</code> returns the last known trade regardless "
    "of when it happened — it could be from yesterday's close. One HTTP call at startup "
    "seeds Redis with real prices so the dashboard is useful immediately."
))

story.append(H2("12.2  Why httpx and not requests?"))
story.append(P(
    "<code>requests</code> is a synchronous library — calling it blocks the asyncio event loop. "
    "<code>httpx</code> has an async client (<code>httpx.AsyncClient</code>) that integrates "
    "with asyncio properly. Using <code>requests</code> in an async application causes the "
    "entire event loop to freeze during the HTTP call."
))

story.append(H2("12.3  Error handling — why just log and continue?"))
story.append(P(
    "If the Alpaca REST API is down, we log a warning and continue startup. "
    "The system works without this data — prices will just show empty until the WebSocket "
    "feed delivers the first ticks. It's a nice-to-have enhancement, not a required startup step. "
    "Crashing on a non-critical initialization step would be wrong."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 13. API
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("13. api/ — REST Endpoints"))

story.append(H2("13.1  GET /health"))
story.append(Code(
"""@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    # Check DB — try to execute SELECT 1
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    redis_ok = await ping_redis()   # sends PING, expects PONG
    feed_ok = is_connected()        # reads module-level flag from ws_client

    status = "healthy" if (db_ok and redis_ok) else "degraded"
    return HealthResponse(
        status=status,
        db_connected=db_ok,
        redis_connected=redis_ok,
        feed_connected=feed_ok,   # feed down != degraded (still serves cache)
        uptime_seconds=round(time.monotonic() - _start_time, 1),
        timestamp=datetime.now(tz=timezone.utc),
    )"""))
story.append(P(
    "<b>Why is feed_connected not included in status?</b> When the market is closed, "
    "the feed is disconnected (no data flows) but the system is fully operational — "
    "it serves cached prices from Redis and historical data from the DB. "
    "Marking the system 'degraded' just because the market is closed would cause "
    "false alarms in monitoring. DB and Redis are required; the feed is expected to "
    "be intermittently disconnected."
))
story.append(P(
    "<b>Why SELECT 1 for DB check?</b> It's the cheapest possible query — no table scan, "
    "no parsing, just a round-trip to verify the connection is alive. "
    "Anything more complex (selecting from a table) could fail for reasons unrelated "
    "to connectivity (table doesn't exist yet, permission issue)."
))

story.append(H2("13.2  GET /prices/{ticker}"))
story.append(Code(
"""@router.get("/prices/{ticker}", response_model=PriceResponse)
async def get_price(ticker: str) -> PriceResponse:
    symbol = ticker.upper()  # normalize: "aapl" -> "AAPL"

    # 1. Try Redis first (sub-millisecond)
    cached = await get_latest_price(symbol)
    if cached:
        return PriceResponse(**cached)

    # 2. Fall back to DB (Redis may be cold/restarted)
    async with get_session() as session:
        result = await session.execute(
            select(Tick)
            .where(Tick.symbol == symbol)
            .order_by(desc(Tick.time))
            .limit(1)
        )
        row = result.scalar_one_or_none()

    if row is None:
        raise HTTPException(status_code=404,
                            detail=f"No price data for {symbol}")

    return PriceResponse(symbol=symbol, price=float(row.price), ...)"""))
story.append(P(
    "The <b>cache-aside pattern</b>: try cache first, on miss go to the source of truth, "
    "return result. The cache is NOT updated here on a DB read — the ingestor is the "
    "only writer to Redis. This avoids a cache update race condition."
))
story.append(P(
    "<b>Why ticker.upper()?</b> URLs are case-sensitive. "
    "<code>/prices/aapl</code> and <code>/prices/AAPL</code> are different URLs. "
    "Normalizing to uppercase means the API accepts either form."
))

story.append(H2("13.3  GET /history/{ticker}"))
story.append(Code(
"""INTERVAL_MAP = {
    "1m":  "1 minute",
    "5m":  "5 minutes",
    "15m": "15 minutes",
    "1h":  "1 hour",
    "1d":  "1 day",
}

sql = text(\"\"\"
    SELECT
        time_bucket(:bucket, time)  AS bucket_time,
        first(price, time)          AS open,
        MAX(price)                  AS high,
        MIN(price)                  AS low,
        last(price, time)           AS close,
        SUM(volume)                 AS volume
    FROM ticks
    WHERE symbol = :symbol
      AND time >= :from_ts
      AND time <  :to_ts
    GROUP BY bucket_time
    ORDER BY bucket_time ASC
\"\"\")"""))
story.append(P(
    "<b>time_bucket(:bucket, time)</b> — rounds each timestamp down to the bucket boundary. "
    "time_bucket('1 minute', '14:30:45') = '14:30:00'. "
    "All ticks in the same minute get the same bucket_time and are grouped together."
))
story.append(P(
    "<b>first(price, time)</b> — TimescaleDB aggregate. Returns the price at the row with "
    "the minimum 'time' within the group. This is the opening price of the candle. "
    "Standard PostgreSQL has no equivalent — you'd need a DISTINCT ON subquery."
))
story.append(P(
    "<b>Why text() and not ORM?</b> This query uses TimescaleDB-specific functions "
    "(time_bucket, first, last) that SQLAlchemy's ORM doesn't know about. "
    "Raw SQL via text() is the right tool here. The parameters (:bucket, :symbol) "
    "are bound parameters — SQLAlchemy's driver safely escapes them, preventing SQL injection."
))
story.append(P(
    "<b>AND time < :to_ts (exclusive upper bound)</b> — standard in time-series queries. "
    "If to='2026-03-26T15:00:00' and a tick lands at exactly 15:00:00, should it be included? "
    "Exclusive upper bound says no — the interval is [from, to). This makes intervals "
    "composable: [14:00, 15:00) + [15:00, 16:00) = [14:00, 16:00) with no gap and no overlap."
))

story.append(H2("13.4  GET /tickers"))
story.append(Code(
"""@router.get("/tickers", response_model=list[TickerResponse])
async def list_tickers() -> list[TickerResponse]:
    async with get_session() as session:
        result = await session.execute(
            select(Ticker).order_by(Ticker.symbol))
        rows = result.scalars().all()

    symbols = [r.symbol for r in rows] if rows else settings.symbols
    prices = await get_all_latest_prices(symbols)  # one Redis pipeline call

    return [
        TickerResponse(
            symbol=sym,
            name=names.get(sym),
            latest_price=prices[sym]["price"] if prices.get(sym) else None,
            last_updated=prices[sym]["last_updated"] if prices.get(sym) else None,
        )
        for sym in symbols
    ]"""))
story.append(P(
    "Note the fallback: <code>symbols = [r.symbol for r in rows] if rows else settings.symbols</code>. "
    "On the very first startup before tickers are seeded, the DB is empty. "
    "Rather than returning an empty list, the endpoint falls back to the configured symbols. "
    "This handles the race condition where the API receives a request before startup finishes seeding."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 14. MAIN.PY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("14. main.py — Application Lifespan"))
story.append(Code(
"""@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────
    await _run_migrations()       # 1. schema up to date
    await _seed_tickers()         # 2. symbols in DB
    await seed_latest_prices()    # 3. Redis has last known prices

    ingestor_task = asyncio.create_task(run_ingestor(), name="ingestor")
    await start_feed()            # 4. background tasks running

    yield  # <-- application serves requests here

    # ── Shutdown (reverse order) ──────────────────────────
    await stop_feed()             # 1. stop WebSocket first
    await stop_ingestor()         # 2. set _running=False
    ingestor_task.cancel()        # 3. cancel the task
    try:
        await ingestor_task
    except asyncio.CancelledError:
        pass

    await engine.dispose()        # 4. close DB connections
    await close_redis()           # 5. close Redis connection
    logger.info("Application shutdown complete")

app = FastAPI(title="Market Feed", lifespan=lifespan)
app.include_router(health.router)
app.include_router(tickers.router)
app.include_router(prices.router)
app.include_router(history.router)"""))

story.append(H2("14.1  Why asynccontextmanager for lifespan?"))
story.append(P(
    "FastAPI's lifespan parameter replaced the old @app.on_event('startup') decorator "
    "in FastAPI 0.93+. The context manager pattern is cleaner: everything before "
    "<code>yield</code> is startup, everything after is shutdown. The same try/finally "
    "semantics apply — shutdown always runs even if startup partially fails."
))

story.append(H2("14.2  Why run migrations on every startup?"))
story.append(P(
    "Alembic's <code>upgrade head</code> is idempotent — it checks the "
    "<code>alembic_version</code> table and only applies migrations that haven't run yet. "
    "If the DB is already at head, it does nothing in milliseconds. "
    "Running it on startup means: deploy new code -> restart -> migrations apply automatically. "
    "No separate migration step needed in the deploy pipeline."
))

story.append(H2("14.3  Why run migrations in an executor?"))
story.append(Code(
"""async def _run_migrations() -> None:
    alembic_cfg = AlembicConfig("alembic.ini")
    loop = asyncio.get_running_loop()
    # command.upgrade is synchronous (blocking)
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")"""))
story.append(P(
    "Alembic's <code>command.upgrade</code> is synchronous — it doesn't know about asyncio. "
    "Calling it directly in an async function would block the event loop, freezing all "
    "other asyncio tasks during migrations. <code>run_in_executor(None, ...)</code> runs "
    "the function in a thread pool, allowing the event loop to continue processing "
    "other events while migrations run."
))

story.append(H2("14.4  create_task vs await for background tasks"))
story.append(Code(
"""# create_task: schedules the coroutine to run, returns immediately
ingestor_task = asyncio.create_task(run_ingestor(), name="ingestor")

# await start_feed() also calls create_task internally
# We don't await run_ingestor() — that would block forever"""))
story.append(P(
    "<code>run_ingestor()</code> is an infinite loop. <code>await run_ingestor()</code> "
    "would block the lifespan coroutine forever. <code>asyncio.create_task()</code> "
    "schedules it to run concurrently and returns immediately. The task runs in the "
    "background while the lifespan <code>yield</code> gives control back to FastAPI."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 15. DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("15. cli/dashboard.py — Terminal Dashboard"))
story.append(Code(
"""async def run_dashboard() -> None:
    async with httpx.AsyncClient() as client:
        with Live(console=console, refresh_per_second=2, screen=True) as live:
            while True:
                # Fetch tickers + health in parallel
                ticker_rows, health_data = await asyncio.gather(
                    _fetch_tickers(client),
                    _fetch_health(client),
                )

                # Fetch individual prices in parallel (not sequentially)
                price_tasks = {
                    t["symbol"]: asyncio.create_task(
                        _fetch_price(client, t["symbol"])
                    )
                    for t in ticker_rows
                }
                price_results = {
                    sym: await task for sym, task in price_tasks.items()
                }

                # Render
                layout = Layout()
                layout.split_column(
                    Layout(_build_header(), name="header", size=3),
                    Layout(_build_table(ticker_rows, price_results), name="table"),
                    Layout(_build_status_bar(health_data), name="status", size=3),
                )
                live.update(layout)
                await asyncio.sleep(REFRESH_INTERVAL)  # 1 second"""))

story.append(H2("15.1  Why asyncio.gather for parallel fetches?"))
story.append(P(
    "<code>asyncio.gather(task1, task2)</code> runs both coroutines concurrently. "
    "Without it (sequential): fetch tickers (200ms) + fetch health (200ms) = 400ms total. "
    "With gather: both run simultaneously = ~200ms total. "
    "The same logic applies to individual price fetches — all 5 symbols are fetched "
    "concurrently, not one after another."
))

story.append(H2("15.2  Color-coded price movement"))
story.append(Code(
"""def _price_style(symbol: str, current: Optional[float]) -> str:
    prev = _prev_prices.get(symbol)
    if prev is None: return "white"
    if current > prev: return "bold green"
    elif current < prev: return "bold red"
    return "white"

def _fmt_change(symbol: str, current: Optional[float]) -> Text:
    open_price = _session_open_prices.get(symbol)
    if open_price is None:
        _session_open_prices[symbol] = current  # first price seen
        return Text("0.00%", style="white")
    pct = ((current - open_price) / open_price) * 100
    ..."""))
story.append(P(
    "Two separate concepts: (1) <b>tick color</b> — green if this refresh's price is "
    "higher than last refresh's price, red if lower. Shows momentum. "
    "(2) <b>% Change</b> — percentage change from the first price seen this session. "
    "This is not the same as the day's open — it's relative to when the dashboard started."
))

story.append(H2("15.3  Why call the REST API and not Redis/DB directly?"))
story.append(P(
    "The dashboard is an external consumer of the system. By calling the REST API, it: "
    "(1) exercises the same code path a mobile app or web client would use, "
    "(2) tests that the API is actually working end-to-end, "
    "(3) stays decoupled from internal implementation details. "
    "If we refactored to a different cache or DB, the dashboard wouldn't need to change."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 16. CONCURRENCY MODEL
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("16. Concurrency Model — asyncio Deep Dive"))
story.append(P(
    "The entire application runs in a <b>single Python thread</b>, "
    "managed by a single asyncio event loop. There are no threads (except "
    "the executor for Alembic migrations and the uvicorn reloader process). "
    "This is fundamentally different from traditional threaded servers."
))
story.append(Code(
"""Single-threaded asyncio event loop:
┌──────────────────────────────────────────────────────┐
│ Event Loop                                           │
│                                                      │
│  Task 1: run_ingestor()  ─── sleeping 500ms          │
│  Task 2: ws_feed()       ─── waiting for WS message  │
│  Task 3: FastAPI request ─── waiting for Redis read  │
│  Task 4: FastAPI request ─── waiting for DB query    │
│                                                      │
│  When task 2 gets a message, it runs briefly,        │
│  calls enqueue(), then yields back to the loop.      │
│  The loop picks the next ready task.                 │
└──────────────────────────────────────────────────────┘"""))

story.append(H2("16.1  How asyncio achieves concurrency without threads"))
story.append(P(
    "Every <code>await</code> is a <b>yield point</b>. When a coroutine hits "
    "<code>await something</code>, it pauses and gives the event loop a chance "
    "to run other ready tasks. The event loop uses the OS's I/O multiplexing "
    "(select/epoll/kqueue) to watch multiple file descriptors (sockets) simultaneously. "
    "When a socket has data, the event loop wakes the waiting coroutine."
))
story.append(P(
    "This is why CPU-bound work must not run in coroutines directly — "
    "it would block the event loop and freeze all other tasks. "
    "Alembic migrations are CPU+I/O bound, so they run in a thread pool via "
    "<code>run_in_executor</code>."
))

story.append(H2("16.2  When does asyncio NOT help?"))
story.append(B("<b>CPU-bound work:</b> data processing, encryption, compression. asyncio doesn't parallelize CPU work — use multiprocessing or concurrent.futures for that."))
story.append(B("<b>Blocking library calls:</b> requests.get(), psycopg2 queries, file I/O without aiofiles. These block the event loop. Always use async alternatives."))
story.append(B("<b>GIL limitation:</b> Python's Global Interpreter Lock means true parallelism requires multiple processes, not threads. asyncio bypasses this by not needing parallelism for I/O."))

story.append(H2("16.3  Task vs Coroutine"))
story.append(Code(
"""# Coroutine: not yet scheduled
coro = run_ingestor()  # just creates the coroutine object, nothing runs

# Task: scheduled on the event loop, will run as soon as possible
task = asyncio.create_task(coro)  # now it's in the event loop's run queue

# await: pause current coroutine until coro completes
result = await coro  # blocks current coroutine (but not the event loop)"""))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 17. END-TO-END TRACE
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("17. End-to-End Trace — One Tick Through the System"))
story.append(P(
    "Let's trace a single AAPL trade from Alpaca to the dashboard. Timestamps are illustrative."
))
story.append(Code(
"""T+0ms    Alpaca pushes a WebSocket frame to our connection:
         [{"T":"t","S":"AAPL","p":182.50,"s":100,
           "t":"2026-03-27T14:30:00.123456789Z"}]

T+0.1ms  ws_client._consume():
         raw = await ws.recv()  # event loop wakes this task
         messages = json.loads(raw)
         for msg in messages:
             tick = normalize(msg)   # calls normalizer

T+0.2ms  normalizer.normalize():
         Validates with _TradeMessage pydantic model
         Parses timestamp: truncates ns -> us
         Returns Tick(time=14:30:00.123456 UTC, symbol="AAPL",
                      price=Decimal("182.50"), volume=100,
                      bid=None, ask=None, source="trade")

T+0.2ms  ingestor.enqueue(tick):
         _queue.put_nowait(tick)   # non-blocking, immediate return
         WebSocket consumer continues processing next frame

T+500ms  ingestor.run_ingestor() wakes from asyncio.sleep(0.5):
         batch = drain queue  # [AAPL tick + maybe others]

T+500.5ms  ingestor._write_redis_batch(batch):
           Redis HSET price:AAPL {price:182.50, source:trade, ...}
           Latency: ~0.3ms

T+501ms  ingestor._flush_batch(batch):
         INSERT INTO ticks VALUES (...) ON CONFLICT DO NOTHING
         PostgreSQL bulk insert latency: ~2-5ms

T+506ms  Next dashboard refresh (every 1000ms from start):
         GET /prices/AAPL
         -> get_latest_price("AAPL")
         -> Redis HGETALL price:AAPL
         -> returns {price: 182.50, ...}
         -> PriceResponse returned in ~1ms
         -> Dashboard renders green "182.5000" for AAPL

Total end-to-end latency (WebSocket frame -> dashboard display):
~500ms (dominated by the batch flush interval)
The 500ms is a deliberate tradeoff: throughput vs. display latency."""))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 18. INTERVIEW Q&A
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("18. Interview Q&A — 30 Questions with Full Answers"))

qas = [
    ("Q1: Why use a queue between the WebSocket consumer and the DB writer?",
     "The WebSocket consumer needs to process messages as fast as they arrive — any "
     "delay in the consumer causes the WebSocket buffer to fill up, eventually causing "
     "the connection to stall. DB writes take 2-5ms. At 500 msgs/second, waiting for "
     "each DB write would mean the consumer falls 1-2.5 seconds behind in real-time. "
     "The queue decouples them: the consumer enqueues instantly, the DB writer works "
     "at its own pace. The queue absorbs burst traffic up to 50,000 ticks."),

    ("Q2: What is the batch_flush_ms setting and what are the tradeoffs?",
     "batch_flush_ms=500 means the ingestor wakes every 500ms to flush accumulated ticks. "
     "Lower value: lower display latency (ticks appear sooner), more frequent DB writes, "
     "more Redis updates. Higher value: higher throughput (larger batches = fewer DB round-trips), "
     "higher display latency. 500ms is a good balance — the display latency is imperceptible "
     "to humans (we don't notice delays under ~1 second) while batching significantly reduces DB load."),

    ("Q3: How does ON CONFLICT DO NOTHING work and when is it needed?",
     "The primary key on ticks is (time, symbol). If the same (time, symbol) pair is inserted twice, "
     "PostgreSQL would normally raise a unique constraint violation. ON CONFLICT DO NOTHING "
     "silently discards the duplicate instead of raising an error. This is needed because: "
     "(1) Alpaca may resend messages on WebSocket reconnect, (2) a partial DB write followed by "
     "a crash could cause the same batch to be reinserted on restart (though the ingestor doesn't "
     "currently persist the queue across restarts)."),

    ("Q4: What happens to ticks in the queue when the process is killed?",
     "They're lost. asyncio.Queue is in-memory. SIGKILL doesn't give the process time to flush. "
     "SIGTERM does trigger the shutdown sequence (FastAPI catches it), which calls stop_ingestor() "
     "and lets the current batch complete. Ticks that arrived between the last flush and SIGTERM "
     "are lost. For a price display system this is acceptable. For a trading system, you'd use "
     "a persistent queue (Redis Streams, Kafka) that survives process restarts."),

    ("Q5: Why is the API stateless?",
     "All state lives in Redis and TimescaleDB. The API process itself holds no data — "
     "it reads from Redis/DB on every request. This means you can run multiple API process instances "
     "behind a load balancer and they all serve the same data. If one crashes, traffic routes "
     "to the others. This is horizontal scalability. The ingestor is NOT stateless (it owns "
     "the WebSocket connection and queue) — it cannot be simply replicated without a message broker."),

    ("Q6: How would you add authentication to the API?",
     "FastAPI has built-in support for OAuth2 (via fastapi.security.OAuth2PasswordBearer) "
     "and API keys (via Header dependencies). The simplest approach: add a dependency function "
     "that reads an Authorization header, validates the token against a users table in PostgreSQL, "
     "and raises HTTPException(401) if invalid. Attach it to routes with Depends(auth_required). "
     "For a production system: JWT tokens, short expiry, refresh token rotation."),

    ("Q7: What is a TimescaleDB continuous aggregate and why would you use one?",
     "A continuous aggregate is a materialized view that TimescaleDB automatically keeps "
     "up-to-date as new data arrives. Instead of running the time_bucket() GROUP BY on raw ticks "
     "for every history request, you'd CREATE MATERIALIZED VIEW ohlcv_1m WITH (timescaledb.continuous) "
     "and query that view instead. The aggregation runs once when data arrives, not on every query. "
     "For heavy history traffic, this reduces query time from seconds to milliseconds."),

    ("Q8: Why does the normalizer use a dataclass for Tick instead of a Pydantic model?",
     "Pydantic models have validation overhead — they run validators on every field assignment. "
     "The Tick dataclass is an internal data transfer object, always created from already-validated "
     "data (the Pydantic _TradeMessage/_QuoteMessage models validate first, then Tick is constructed). "
     "Using a plain dataclass avoids double validation. Pydantic is used at the boundary (incoming "
     "external data); dataclass is used internally (trusted data)."),

    ("Q9: What does pool_pre_ping do and why is it important?",
     "Before handing a connection from the pool to a query, SQLAlchemy sends SELECT 1 to verify "
     "the connection is alive. Without this, a connection that's been idle in the pool might have "
     "been terminated by PostgreSQL's idle_in_transaction_session_timeout, a firewall timeout, "
     "or a DB restart. Using a dead connection would cause a cryptic 'connection already closed' "
     "error. pool_pre_ping detects dead connections and replaces them transparently."),

    ("Q10: What is the GIL and does it affect this system?",
     "The Global Interpreter Lock is a mutex in CPython that prevents multiple threads from "
     "executing Python bytecode simultaneously. For this system, it barely matters because: "
     "(1) asyncio is single-threaded — no threads compete for the GIL, (2) asyncpg and redis-py "
     "release the GIL during I/O (network calls happen in C, not Python). The only thread pool "
     "usage is Alembic migrations (one thread, runs once). A system that needed true CPU parallelism "
     "would use multiprocessing."),

    ("Q11: Explain the producer-consumer pattern in this system.",
     "ws_client.py is the producer: it connects to Alpaca, receives messages, normalizes them, "
     "and calls enqueue() to put Ticks on the asyncio.Queue. ingestor.py is the consumer: "
     "it wakes every 500ms, drains the queue, and writes to Redis and DB. The queue is the "
     "buffer between them. This pattern decouples production rate from consumption rate — "
     "if the consumer is temporarily slow, the queue absorbs the backlog up to maxsize."),

    ("Q12: Why use text() for the history SQL instead of SQLAlchemy ORM query?",
     "The history query uses TimescaleDB-specific SQL functions (time_bucket, first, last) "
     "that SQLAlchemy's ORM dialect doesn't know about. The ORM can only generate SQL using "
     "standard constructs it understands. For database-specific features, raw SQL via text() "
     "is the right tool. The parameters are still properly bound and escaped — text() with "
     "bind parameters is safe from SQL injection."),

    ("Q13: How does Redis pipeline reduce latency?",
     "A Redis pipeline batches multiple commands into one TCP write. Without pipeline: "
     "each HGETALL requires a round-trip (send command, wait for response, send next command). "
     "With pipeline: send all 5 HGETALL commands at once, wait once, receive all 5 responses. "
     "The saving is N-1 round-trips where N is the number of commands. At 0.2ms per round-trip, "
     "5 sequential calls = 1ms, pipelined = ~0.2ms."),

    ("Q14: What is the difference between asyncio.gather and sequential awaits?",
     "Sequential: await f1(); await f2() — f2 starts only after f1 completes. Total time = f1 + f2. "
     "gather: await asyncio.gather(f1(), f2()) — both start immediately and run concurrently. "
     "Total time = max(f1, f2). For I/O-bound operations (HTTP calls, DB queries, Redis reads) "
     "that can overlap, gather dramatically reduces wall-clock time."),

    ("Q15: Why does the dashboard use asyncio.create_task for price fetches instead of gather?",
     "Actually, it creates tasks for each symbol then awaits them sequentially in a dict comprehension: "
     "{sym: await task for sym, task in price_tasks.items()}. This is slightly incorrect — "
     "it creates all tasks (scheduling them for concurrent execution) but then awaits them one by one. "
     "A cleaner approach would be asyncio.gather(*price_tasks.values()). However, since create_task "
     "schedules all tasks immediately, they do run concurrently — the sequential await just collects "
     "results one at a time. The concurrency benefit is still mostly achieved."),

    ("Q16: What is the purpose of the alembic_version table?",
     "Alembic creates and maintains alembic_version in your database. It stores the revision ID "
     "of the last applied migration. When you run 'alembic upgrade head', Alembic reads this table "
     "to know where you currently are, computes which migrations need to run (current -> head), "
     "and applies them in order. Without this table, Alembic would have no way to know which "
     "migrations have already been applied."),

    ("Q17: Could you replace Redis with an in-memory Python dict?",
     "For a single-process deployment, yes — a module-level dict would give even faster reads. "
     "But: (1) the dict is lost on process restart, so the dashboard shows empty until the "
     "first ticks arrive, (2) if you run multiple API processes behind a load balancer, each "
     "has its own dict with potentially different data, (3) Redis gives you introspection tools "
     "(redis-cli, RedisInsight) to debug production data. Redis adds slight complexity but "
     "enables shared state across processes."),

    ("Q18: What does server_default=text('NOW()') mean vs Python-side default?",
     "server_default means PostgreSQL generates the value on INSERT — the Python application "
     "doesn't send it. text('NOW()') tells PostgreSQL to use the current timestamp at insert time. "
     "A Python-side default (default=datetime.utcnow) would be evaluated in Python and sent to "
     "PostgreSQL. The difference: server_default uses the DB's clock (consistent across all app "
     "processes), Python-side uses the app server's clock (potential clock skew across processes)."),

    ("Q19: Why wrap the lifespan in asynccontextmanager instead of using startup/shutdown events?",
     "FastAPI 0.93+ recommends lifespan over @app.on_event('startup'/'shutdown'). The advantage: "
     "startup and shutdown code are in the same function with yield separating them. You can share "
     "local variables between startup and shutdown (e.g., the task reference). The old event-based "
     "approach required module-level variables to pass state between separate startup and shutdown handlers."),

    ("Q20: How does the system handle an Alpaca authentication failure?",
     "_authenticate() returns False if the auth response doesn't contain T='success' and msg='authenticated'. "
     "_run_feed() raises RuntimeError('Authentication failed'). This propagates to _run_with_backoff() "
     "which catches it as a general Exception and applies exponential backoff + retry. "
     "After 5 failed attempts, the feed gives up. The API continues serving cached data from Redis "
     "and DB, but feed_connected will be False in /health. Wrong credentials will always fail — "
     "retrying doesn't help, but the system is designed to not distinguish between transient and "
     "permanent failures at this layer."),

    ("Q21: What is the 'source' field in the ticks table for?",
     "It distinguishes between trades (actual executions) and quotes (bid/ask updates). "
     "This matters because: (1) trade prices are more reliable — they represent actual money changing hands, "
     "(2) quote prices (mid-point of bid/ask) may differ from the last trade price, "
     "(3) consumers of the API can filter by source if they care about the distinction. "
     "For OHLCV calculations in the history endpoint, both types contribute — a quote's "
     "mid-price is treated as a price point for open/high/low/close computation."),

    ("Q22: What would happen if you ran two instances of this service?",
     "Two WebSocket connections to Alpaca with the same credentials — Alpaca allows this "
     "but you'd receive duplicate tick streams. Both ingestors would try to write the same "
     "ticks to the DB — ON CONFLICT DO NOTHING handles the duplicates safely. Both would "
     "write to Redis — the last writer wins (race condition), but the values should be "
     "nearly identical. The API instances would both serve correctly since they read from "
     "shared Redis/DB. In practice, you'd want only one feed process and multiple API-only processes."),

    ("Q23: Why is expire_on_commit=False important in async SQLAlchemy?",
     "By default, SQLAlchemy expires all ORM object attributes after a commit so they're "
     "reloaded from DB on next access. In sync SQLAlchemy this is fine — the session is still open. "
     "In async SQLAlchemy with get_session() context manager, the session closes after the "
     "async with block exits. Accessing an expired attribute after the session closes triggers "
     "a lazy load that fails because there's no session. expire_on_commit=False keeps the "
     "attributes populated after commit, so objects can be safely used after the session closes."),

    ("Q24: How would you add a new symbol (e.g., NVDA) to track?",
     "Two options: (1) Add NVDA to the SYMBOLS list in .env and restart the app — on startup, "
     "_seed_tickers() does INSERT ... ON CONFLICT DO NOTHING for all configured symbols, "
     "so NVDA gets added. The WebSocket subscription also subscribes to all settings.symbols "
     "on connect. (2) Add a POST /tickers endpoint that inserts into the DB and re-subscribes "
     "the WebSocket (would require ws_client to support dynamic subscription). Option 1 is "
     "simpler and sufficient for most cases."),

    ("Q25: What is the difference between engine.begin() and engine.connect()?",
     "engine.connect() gives a connection without an explicit transaction. DML statements "
     "(INSERT, UPDATE, DELETE) start implicit transactions that must be explicitly committed. "
     "engine.begin() gives a connection with a transaction already started — it auto-commits "
     "at the end of the context manager and auto-rolls back on exception. "
     "The ingestor uses engine.begin() for the bulk INSERT because we always want "
     "the entire batch committed atomically. If any row fails, we want the whole batch "
     "to roll back (though ON CONFLICT DO NOTHING handles most failure cases)."),

    ("Q26: Why does the history endpoint use AND time < :to_ts (exclusive) not <=?",
     "Time intervals should be half-open: [from, to). This makes them composable without "
     "gaps or overlaps. If to='15:00:00' and from='15:00:00' for the next interval, "
     "a tick at exactly 15:00:00 belongs to exactly one interval. With inclusive upper "
     "bound (<=), a tick at 15:00:00 would appear in both intervals. This is the "
     "standard convention for time-series bucketing."),

    ("Q27: How does the REST API avoid SQL injection?",
     "The history endpoint uses text() with bound parameters: "
     "text('WHERE symbol = :symbol ... time >= :from_ts') with {symbol: symbol, from_ts: from_}. "
     "SQLAlchemy's driver sends the query and parameters separately — the DB driver escapes "
     "the parameters before interpolation. An attacker setting symbol = 'AAPL; DROP TABLE ticks--' "
     "would result in the literal string being compared as a symbol name, not executed as SQL. "
     "The ticker.upper() call is also safe — it only changes case, no special characters."),

    ("Q28: What is the risk of the Redis-ahead-of-DB write pattern?",
     "Redis is updated first, then the DB. If the process crashes after the Redis write but "
     "before the DB write, Redis has a price that doesn't exist in the DB. Consequences: "
     "(1) /prices/{ticker} returns a price from Redis that isn't backed by DB history, "
     "(2) if Redis is then cleared (restart), the price is permanently lost, "
     "(3) there's no way to 'replay' the tick from the queue (queue is in-memory, also lost). "
     "This is acceptable for a price display system. For auditability or accounting, "
     "you'd write to DB first and update Redis from a DB trigger or change data capture stream."),

    ("Q29: Why does the dashboard call the REST API every second instead of using WebSocket push?",
     "The current system has no push API — the API is purely request/response REST. "
     "Polling is simpler to implement and debug. The 1-second polling interval is "
     "imperceptible to humans and the load is minimal (5 HTTP requests per second). "
     "A WebSocket push endpoint (FastAPI supports WebSockets natively) would reduce latency "
     "from ~1 second to ~500ms (the batch flush interval) and eliminate polling overhead. "
     "It's listed in 'What Production Would Add' as an enhancement."),

    ("Q30: If the DB is down, what still works?",
     "Redis still has the latest price for each symbol. /prices/{ticker} returns from Redis. "
     "/tickers returns latest prices from Redis. /health shows db_connected: false, status: degraded. "
     "/history/{ticker} fails (needs DB). The ingestor continues batching ticks in the queue "
     "and writing to Redis (Redis writes don't go through the DB). When the DB recovers, "
     "the ingestor resumes DB writes — but any ticks that overflowed the queue while DB was "
     "down are lost. The WebSocket feed continues uninterrupted."),
]

for q, a in qas:
    story.append(KeepTogether([
        Q(q),
        A(a),
        SP(4),
    ]))

story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 19. WHAT PRODUCTION WOULD ADD
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("19. Docker & Docker Compose — Infrastructure as Code"))

story.append(P(
    "The project ships a <b>docker-compose.yml</b> that provisions every infrastructure dependency "
    "with a single command: <b>make up</b>. Understanding this file is important for interviews "
    "because it shows you understand production concerns like health checks, data persistence, "
    "and port mapping even in a local dev setup."
))

story.append(H2("19.1  The docker-compose.yml — Line by Line"))
story.append(Code(
"""version: \"3.9\"

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg15   # TimescaleDB on PG 15
    container_name: market_timescaledb         # Fixed name so app can reference it
    environment:
      POSTGRES_DB: marketfeed                  # DB name created on first start
      POSTGRES_USER: market                    # Superuser name
      POSTGRES_PASSWORD: market                # Password (dev only — never in prod)
    ports:
      - \"5432:5432\"                            # host:container port mapping
    volumes:
      - timescale_data:/var/lib/postgresql/data  # Named volume = data survives 'make down'
    healthcheck:
      test: [\"CMD-SHELL\", \"pg_isready -U market -d marketfeed\"]
      interval: 5s     # Check every 5 seconds
      timeout: 5s      # Each check times out after 5s
      retries: 10      # Container is 'healthy' after 10 consecutive successes

  redis:
    image: redis:7-alpine           # Alpine = tiny image (~30MB vs ~110MB full)
    container_name: market_redis
    ports:
      - \"6379:6379\"
    volumes:
      - redis_data:/data            # Persist RDB/AOF files
    command: redis-server --appendonly yes   # Enable AOF persistence
    healthcheck:
      test: [\"CMD\", \"redis-cli\", \"ping\"]  # redis-cli PING returns PONG if healthy
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  timescale_data:   # Docker-managed named volume — survives container restart
  redis_data:"""))

story.append(H2("19.2  Why Docker and not running services natively?"))
story.append(P(
    "The port conflict you encountered (<b>local PostgreSQL on 5432 vs Docker's TimescaleDB on 5432</b>) "
    "is the exact problem Docker is meant to avoid in team settings. With Docker:"
))
story.append(B("Reproducibility — everyone runs identical versions of TimescaleDB and Redis, no 'works on my machine'"))
story.append(B("Isolation — the database is scoped to this project; stopping it with 'make down' doesn't affect other projects"))
story.append(B("Clean state — 'make reset' (docker compose down -v) wipes all data and starts fresh; impossible cleanly with a native install"))
story.append(B("No install sprawl — no native PostgreSQL or Redis installation needed on the developer's machine"))

story.append(H2("19.3  Why health checks?"))
story.append(P(
    "Without health checks, <b>docker compose up -d</b> returns as soon as the container process starts — "
    "but TimescaleDB takes 1–3 seconds to initialize after the process starts. "
    "If your app tries to connect immediately, it gets a connection refused error."
))
story.append(P(
    "The <b>pg_isready</b> command checks whether PostgreSQL is accepting connections. "
    "Only after 10 consecutive successes does Docker mark the container as healthy. "
    "The Makefile's <b>sleep 5</b> is a simpler (less rigorous) approach — "
    "the 'correct' production approach is <b>depends_on: condition: service_healthy</b> in Compose."
))

story.append(H2("19.4  Why named volumes instead of bind mounts?"))
docker_vol_data = [
    ["Type", "Syntax", "Use Case", "Survives 'down -v'?"],
    ["Named volume", "timescale_data:/var/lib/...", "Persistent dev/prod data", "No (with -v flag), Yes (without)"],
    ["Bind mount", "./data:/var/lib/...", "Config files, code (hot reload)", "Yes (it's a local dir)"],
    ["Anonymous volume", "/var/lib/...", "Throwaway data, CI builds", "No"],
]
story.append(make_table(docker_vol_data, [1.1*inch, 1.6*inch, 1.6*inch, 1.3*inch]))
story.append(P(
    "Named volumes are managed by Docker's storage driver, which is optimized for container I/O. "
    "A bind mount to your Mac's filesystem goes through osxfs/VirtioFS and is significantly slower for "
    "database workloads. For a database, always use a named volume."
))

story.append(H2("19.5  Why redis:7-alpine?"))
story.append(P(
    "The <b>alpine</b> variant is built on Alpine Linux, a minimal distro (~5MB base). "
    "The full Redis image is ~110MB; alpine is ~30MB. "
    "For a cache with no special OS dependencies, there's no reason to pull the larger image. "
    "In CI pipelines that pull images on every run, this saves time and bandwidth."
))
story.append(Note(
    "Interview follow-up: 'What's the risk of using :latest tag?' — The image can change "
    "between pulls, breaking reproducibility. Production should pin to a specific version: "
    "timescale/timescaledb:2.14.2-pg15 and redis:7.2.4-alpine."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 20. MAKEFILE
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("20. Makefile — Developer Workflow Automation"))

story.append(P(
    "The Makefile wraps long commands behind short, memorable names. "
    "It's the project's developer interface — the thing a new engineer runs on day one. "
    "Understanding every target shows you read the project end-to-end."
))

story.append(Code(
""".PHONY: up down reset migrate run dashboard test lint

up:
    docker compose up -d       # Start containers in background (detached)
    @sleep 5                   # Give DB time to initialize (@ suppresses echo)

down:
    docker compose down        # Stop containers, preserve volumes

reset:
    docker compose down -v     # Stop AND wipe all data volumes
    docker compose up -d
    @sleep 5
    $(MAKE) migrate            # Re-run migrations on fresh DB

migrate:
    alembic upgrade head       # Apply all pending migrations

migration:
    alembic revision --autogenerate -m "$(msg)"  # Generate new migration

run:
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dashboard:
    python -m cli.dashboard    # Run as module (respects package imports)

test:
    pytest tests/ -v

test-cov:
    pytest tests/ -v --cov=. --cov-report=term-missing

install:
    pip install -r requirements.txt

setup: install up migrate      # Full first-time setup in one command"""))

story.append(H2("20.1  Why .PHONY?"))
story.append(P(
    "Make was originally designed to build files. A target named <b>test</b> would normally mean "
    "'build a file called test'. If a file named <b>test</b> exists in the directory, Make "
    "would think the target is up-to-date and skip it. "
    "<b>.PHONY</b> tells Make these targets are commands, not files — always run them regardless "
    "of what files exist."
))

story.append(H2("20.2  Why 'python -m cli.dashboard' instead of 'python cli/dashboard.py'?"))
story.append(P(
    "Running as a module (<b>-m</b>) adds the project root to sys.path automatically, so "
    "imports like <b>from api import prices</b> resolve correctly. "
    "Running the file directly sets sys.path to the <b>cli/</b> directory, which breaks "
    "all absolute imports from the project root."
))

story.append(H2("20.3  Why --host 0.0.0.0 in make run?"))
story.append(P(
    "By default uvicorn binds to <b>127.0.0.1</b> (loopback only). "
    "Binding to <b>0.0.0.0</b> means 'all network interfaces', so the API is reachable "
    "from other machines on the same network (useful when testing from a phone or another "
    "computer). In production behind a reverse proxy (nginx/Traefik), the app typically "
    "binds to 0.0.0.0 while the proxy handles external TLS termination."
))

story.append(H2("20.4  make reset vs make down"))
reset_data = [
    ["Command", "What It Does", "When to Use"],
    ["make down", "Stop containers, keep volume data", "Pause work, restart later with data intact"],
    ["make reset", "Wipe all data, restart clean, re-migrate", "Schema changed, corrupted data, fresh start"],
    ["docker compose down -v", "Same as reset but without re-migrating", "Manual workflow"],
]
story.append(make_table(reset_data, [1.3*inch, 2.2*inch, 2.2*inch]))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 21. TESTING STRATEGY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("21. Testing Strategy — What's Tested and Why"))

story.append(P(
    "The test suite has 6 test files covering the normalizer, ingestor, and all 4 API endpoints. "
    "All tests are <b>unit tests</b> — they run with no infrastructure (no DB, no Redis, no feed). "
    "Understanding the testing strategy is a common interview topic."
))

story.append(H2("21.1  Test file inventory"))
test_data = [
    ["File", "What It Tests", "Key Technique"],
    ["test_normalizer.py", "normalize() and normalize_batch() — trade/quote/control message parsing", "Pure functions, no mocking needed"],
    ["test_ingestor.py", "enqueue(), _write_redis_batch() dedup, _flush_batch() noop on empty", "patch() to mock Redis and DB"],
    ["test_api_health.py", "GET /health — healthy, degraded, feed disconnected states", "ASGITransport + mocked dependencies"],
    ["test_api_prices.py", "GET /prices/{ticker} — Redis hit, DB fallback, 404", "Mock get_latest_price, mock DB session"],
    ["test_api_history.py", "GET /history/{ticker} — valid/invalid interval, from>=to, 404", "Mock DB returning OHLCV rows"],
    ["test_api_tickers.py", "GET /tickers — symbols with prices, empty Redis fallback", "Mock Redis pipeline"],
    ["conftest.py", "Shared fixtures: in-memory SQLite engine, mocked FastAPI lifespan", "pytest_asyncio, ASGITransport"],
]
story.append(make_table(test_data, [1.4*inch, 2.0*inch, 2.3*inch]))

story.append(H2("21.2  How the FastAPI test client works"))
story.append(Code(
"""# conftest.py
@pytest_asyncio.fixture
async def app():
    with (
        patch(\"main._run_migrations\", new_callable=AsyncMock),
        patch(\"main._seed_tickers\", new_callable=AsyncMock),
        patch(\"main.start_feed\", new_callable=AsyncMock),
        patch(\"main.stop_feed\", new_callable=AsyncMock),
        patch(\"main.run_ingestor\", new_callable=AsyncMock),
        patch(\"main.stop_ingestor\", new_callable=AsyncMock),
        patch(\"main.close_redis\", new_callable=AsyncMock),
    ):
        from main import app as fastapi_app
        yield fastapi_app

@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(
        transport=ASGITransport(app=app),  # In-process — no real HTTP
        base_url=\"http://test\"
    ) as ac:
        yield ac"""))
story.append(P(
    "<b>ASGITransport</b> lets httpx call FastAPI directly in-process without starting a real server. "
    "The lifespan startup (migrations, feed, ingestor) is fully mocked so tests run instantly "
    "without any infrastructure."
))

story.append(H2("21.3  Why unit tests only — no integration tests?"))
story.append(P(
    "The conftest.py comment explains the philosophy: integration tests that need the real DB are "
    "marked with <b>@pytest.mark.integration</b> and skipped unless <b>RUN_INTEGRATION=1</b> is set. "
    "This is a deliberate trade-off:"
))
story.append(B("Unit tests run in milliseconds with no infrastructure — fast CI, no flakiness"))
story.append(B("Integration tests are slower, require Docker, and can fail for infra reasons unrelated to code correctness"))
story.append(B("TimescaleDB-specific SQL (create_hypertable, time_bucket) is not testable with SQLite anyway"))
story.append(Warn(
    "The known risk: mocked tests passed but production migration failed (the kind of incident that "
    "motivates integration test suites). For production, you'd add a CI job that spins up Docker, "
    "runs migrations against real TimescaleDB, and executes the integration-marked tests."
))

story.append(H2("21.4  The normalizer is the most testable module — and why"))
story.append(P(
    "normalize() is a pure function: it takes a dict, returns a Tick or None, touches no external state. "
    "This is why it has the most thorough test coverage — 8 test cases covering trade, quote, "
    "edge cases (bid only, no prices, nanosecond timestamps), control messages, and batch filtering. "
    "Pure functions are always easier to test than code with side effects."
))
story.append(Note(
    "Interview follow-up: 'How would you test the ingestor's DB write path?' — Spin up a real "
    "TimescaleDB in Docker (pytest-docker or testcontainers-python), run migrations, then assert "
    "that after _flush_batch() the rows exist in the ticks table. Mark it @pytest.mark.integration."
))

story.append(H2("21.5  How _write_redis_batch deduplication is tested"))
story.append(Code(
"""async def test_write_redis_batch_deduplicates():
    tick1 = _make_tick(\"AAPL\", 182.00)
    tick2 = Tick(time=tick1.time + timedelta(seconds=1),
                 symbol=\"AAPL\", price=Decimal(\"183.00\"), ...)

    calls = []
    async def mock_set(symbol, price, bid, ask, volume, source):
        calls.append({\"symbol\": symbol, \"price\": price})

    with patch(\"feed.ingestor.set_latest_price\", side_effect=mock_set):
        await ingestor_module._write_redis_batch([tick1, tick2])

    assert len(calls) == 1          # Only written once for AAPL
    assert calls[0][\"price\"] == 183.00  # The later (higher) price wins"""))
story.append(P(
    "This test verifies the deduplication logic: when two ticks for the same symbol arrive in a batch, "
    "only the latest one (by timestamp) gets written to Redis. The mock captures all calls to "
    "set_latest_price and asserts exactly one call happened."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 22. SECURITY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("22. Security — Current Gaps and Production Fixes"))

story.append(P(
    "The project explicitly documents 'No API authentication' as a known limitation. "
    "Security questions are almost guaranteed in an interview for a system that handles financial data. "
    "Here's the full picture of what's missing and what you'd add."
))

story.append(H2("22.1  Current security posture"))
sec_current = [
    ["Area", "Current State", "Risk"],
    ["API authentication", "None — all endpoints public", "Anyone can read price data"],
    ["API authorization", "None — no user concept", "Can't restrict to specific symbols per user"],
    ["Secrets management", ".env file, not committed to git", "Dev-safe; prod needs a secrets manager"],
    ["DB credentials", "Hardcoded in docker-compose.yml (market/market)", "Fine for dev; never in prod"],
    ["TLS/HTTPS", "HTTP only (uvicorn with no SSL)", "Data in transit is unencrypted"],
    ["Rate limiting", "None", "GET /history can be abused to hammer DB"],
    ["Input validation", "Pydantic on WebSocket messages, FastAPI on query params", "Good — covered"],
    ["SQL injection", "SQLAlchemy parameterized queries only", "Protected — no raw string SQL"],
    ["CORS", "FastAPI defaults (allow all origins)", "Permissive for dev; restrict in prod"],
]
story.append(make_table(sec_current, [1.2*inch, 1.9*inch, 2.1*inch]))

story.append(H2("22.2  What you'd add in production"))
story.append(Code(
"""# Option 1: API Key middleware (simplest)
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name=\"X-API-Key\")

async def verify_api_key(key: str = Security(api_key_header)):
    if key not in settings.valid_api_keys:
        raise HTTPException(status_code=403, detail=\"Invalid API key\")

# Apply to all routes:
app = FastAPI(dependencies=[Depends(verify_api_key)])

# Option 2: JWT Bearer tokens (stateless, scalable)
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=\"/auth/token\")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, settings.secret_key, algorithms=[\"HS256\"])
    return payload[\"sub\"]"""))

story.append(H2("22.3  Secrets management"))
story.append(P(
    "In development, secrets live in <b>.env</b> (gitignored). In production:"
))
story.append(B("<b>AWS:</b> Secrets Manager or SSM Parameter Store — secrets injected as env vars at container start"))
story.append(B("<b>GCP:</b> Secret Manager — same pattern"))
story.append(B("<b>Kubernetes:</b> Kubernetes Secrets (base64-encoded, mountable as env vars or files)"))
story.append(B("<b>Fly.io / Railway:</b> Platform-managed env vars set via CLI — never in the repo"))
story.append(P(
    "The key principle: secrets are never in source control and never in Docker images. "
    "They're injected at runtime from a secrets store the platform controls."
))

story.append(H2("22.4  Rate limiting"))
story.append(Code(
"""# slowapi — rate limiting for FastAPI (wraps limits library)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.get(\"/history/{ticker}\")
@limiter.limit(\"30/minute\")   # Max 30 requests per minute per IP
async def get_history(request: Request, ticker: str, ...):
    ..."""))
story.append(P(
    "The <b>/history</b> endpoint is the most expensive: it runs a time_bucket() aggregation over "
    "potentially millions of rows. Without rate limiting, a single client can run the DB out of "
    "connections. 30 requests/minute per IP is a reasonable default for a price history API."
))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 23. DEPLOYMENT & OBSERVABILITY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("23. Deployment & Observability"))

story.append(H2("23.1  How you'd deploy this"))
story.append(P(
    "The project runs locally via <b>make run</b>. A production deployment adds a reverse proxy, "
    "process management, and managed infrastructure:"
))
deploy_data = [
    ["Layer", "Dev", "Production"],
    ["App server", "uvicorn --reload", "uvicorn with gunicorn worker manager (multiple workers)"],
    ["Reverse proxy", "None (direct uvicorn)", "nginx or Traefik — TLS termination, load balancing"],
    ["Database", "Docker TimescaleDB on laptop", "Managed TimescaleDB (Timescale Cloud) or RDS Postgres + extension"],
    ["Redis", "Docker Redis on laptop", "Managed Redis (ElastiCache, Upstash, Redis Cloud)"],
    ["Process mgmt", "Terminal / make run", "systemd, Docker, or Kubernetes Deployment"],
    ["Config/secrets", ".env file", "Environment variables from secrets manager"],
    ["Logs", "stdout (console)", "Structured JSON logs → Datadog, CloudWatch, or Loki"],
]
story.append(make_table(deploy_data, [1.0*inch, 1.4*inch, 3.0*inch]))

story.append(H2("23.2  Why gunicorn + uvicorn workers in production?"))
story.append(Code(
"""# Production command
gunicorn main:app \\
  --worker-class uvicorn.workers.UvicornWorker \\
  --workers 4 \\               # Typically 2 * CPU_cores + 1
  --bind 0.0.0.0:8000 \\
  --timeout 30"""))
story.append(P(
    "A single uvicorn process is single-threaded (one event loop). "
    "If one request blocks the event loop (e.g., CPU-heavy work), all other requests wait. "
    "Running 4 uvicorn worker processes gives you 4 independent event loops, all sharing the "
    "same port via gunicorn's pre-fork model. Each worker handles its own connections independently."
))
story.append(Note(
    "Caveat: the WebSocket feed runs in one process. In a multi-worker deployment, only one worker "
    "would hold the feed connection. The fix is to move the feed to a separate process and communicate "
    "via Redis Streams — the 'WebSocket sharding' item in the production gaps table."
))

story.append(H2("23.3  Observability — what you'd instrument"))
story.append(P(
    "Observability = metrics + logs + traces. The three pillars tell you what's happening, "
    "when it happened, and why."
))

obs_data = [
    ["Signal", "What to Measure", "Tool"],
    ["Metrics", "ticks_ingested_total, queue_depth, ingest_latency_ms, db_write_errors, redis_hit_rate", "Prometheus + Grafana"],
    ["Logs", "Structured JSON with level, timestamp, module, message, context fields", "Python logging → Loki or CloudWatch"],
    ["Traces", "End-to-end latency per API request across Redis + DB calls", "OpenTelemetry + Jaeger or Datadog APM"],
    ["Alerting", "feed_connected=false for >5min, queue_depth>40000, db_write_errors>0", "Prometheus Alertmanager or PagerDuty"],
]
story.append(make_table(obs_data, [0.8*inch, 2.4*inch, 2.0*inch]))

story.append(Code(
"""# Adding Prometheus metrics (prometheus-fastapi-instrumentator)
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
# Exposes GET /metrics with request counts, latency histograms, etc.

# Custom metric example in ingestor.py
from prometheus_client import Counter, Gauge, Histogram

ticks_ingested = Counter(\"ticks_ingested_total\", \"Total ticks processed\")
queue_depth = Gauge(\"ingestor_queue_depth\", \"Current queue size\")
ingest_latency = Histogram(\"ingest_batch_latency_seconds\", \"Batch flush duration\")

# In _flush_batch():
with ingest_latency.time():
    await session.execute(stmt)
ticks_ingested.inc(len(ticks))
queue_depth.set(_queue.qsize())"""))
story.append(PageBreak())

story.append(H1("24. What Production Would Add"))

prod_data = [
    ["Gap", "Production Solution", "Why"],
    ["Single WebSocket process", "Redis Streams / Kafka between feed and N ingestor workers", "Horizontal scaling; one feed failure doesn't stop ingestion"],
    ["No API authentication", "JWT tokens, OAuth2, or API key middleware", "Prevent unauthorized access to price data"],
    ["No OHLCV cache", "TimescaleDB continuous aggregates", "Pre-compute 1m/5m/1h candles; query materialized view not raw ticks"],
    ["Polling dashboard", "FastAPI WebSocket push endpoint", "Lower latency, no polling overhead, works at scale"],
    ["Queue lost on crash", "Persistent queue (Redis Streams, Kafka)", "Survive process restarts without losing ticks"],
    ["No observability", "Prometheus metrics + Grafana", "ticks/sec, queue depth, ingest latency, DB pool usage"],
    ["No alerting", "Alert on feed_connected=false for >5min", "On-call gets paged if feed drops"],
    ["No retry for failed DB writes", "Dead letter queue + retry worker", "Don't silently drop ticks on transient DB errors"],
    ["Single region", "Multi-region DB replica + Redis Sentinel", "HA, disaster recovery"],
    ["No rate limiting", "API rate limiter (slowapi / nginx)", "Prevent abuse of /history endpoint"],
    ["No compression", "TimescaleDB chunk compression after 7 days", "90%+ storage reduction for old data"],
    ["No retention policy", "add_retention_policy('ticks', INTERVAL '90 days')", "Auto-prune old data without manual VACUUM"],
    ["Dashboard read-only", "Price alerts, watchlists, user accounts", "Personalized experience"],
]
story.append(make_table(prod_data, [1.5*inch, 2.1*inch, 2.7*inch]))
story.append(PageBreak())

# ══════════════════════════════════════════════════════════════════════════════
# 20. GLOSSARY
# ══════════════════════════════════════════════════════════════════════════════
story.append(H1("25. Glossary"))

glossary = [
    ["Term", "Definition"],
    ["asyncio", "Python's built-in async I/O framework. Single-threaded concurrency via coroutines and an event loop."],
    ["asyncpg", "Pure-Python async PostgreSQL driver. Speaks the PG wire protocol directly, no libpq wrapper."],
    ["Alembic", "Database migration tool for SQLAlchemy. Tracks applied migrations in alembic_version table."],
    ["Backpressure", "Mechanism to slow/stop a producer when a consumer can't keep up. Here: QueueFull drops ticks."],
    ["CQRS", "Command Query Responsibility Segregation. Separate write path from read path, each optimized differently."],
    ["Exponential backoff", "Increasing wait time between retries: 1s, 2s, 4s, 8s, 16s. Prevents hammering a failing service."],
    ["FastAPI", "Python web framework built on Starlette. Async-native, auto-generates OpenAPI docs from type hints."],
    ["Hypertable", "TimescaleDB abstraction that auto-partitions a table by time into chunks."],
    ["IEX", "Investors Exchange. Free US equity market data source used by Alpaca's free tier."],
    ["Lifespan", "FastAPI context manager replacing startup/shutdown events. Code before yield = startup, after = shutdown."],
    ["Mid-price", "Average of best bid and best ask: (bid + ask) / 2. Used as representative price for quotes."],
    ["OHLCV", "Open, High, Low, Close, Volume. Standard candlestick bar format for financial time series."],
    ["ON CONFLICT DO NOTHING", "PostgreSQL INSERT modifier. Silently discards rows that violate a unique constraint."],
    ["Pipeline (Redis)", "Batch multiple Redis commands into one TCP round-trip."],
    ["Pool pre-ping", "SQLAlchemy feature: validate connection with SELECT 1 before use. Detects stale connections."],
    ["Producer-consumer", "Pattern where one component produces data (WebSocket) and another consumes it (ingestor) via a queue."],
    ["Pydantic", "Python data validation library using type hints. v2 implemented in Rust (pydantic-core)."],
    ["SIP", "Securities Information Processor. The official consolidated US equity tape. Paid on Alpaca."],
    ["time_bucket()", "TimescaleDB function that rounds timestamps to fixed intervals. Enables GROUP BY time period."],
    ["uvicorn", "ASGI server that runs FastAPI apps. Supports async handlers natively."],
    ["WebSocket", "Full-duplex TCP protocol over HTTP upgrade. Enables persistent bidirectional connection for streaming."],
    ["first()/last()", "TimescaleDB aggregate functions. Return the value at the min/max timestamp within a group."],
]
story.append(make_table(glossary, [1.5*inch, 4.8*inch]))
story.append(SP(20))
story.append(HR())
story.append(Paragraph("Market Feed — Complete System Study Guide", cover_label))

# ── Build ──────────────────────────────────────────────────────────────────────
doc.build(story)
print(f"PDF written to: {OUTPUT}")
