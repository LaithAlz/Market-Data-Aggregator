y# Market Feed

A real-time stock price aggregator that ingests live data via WebSocket, stores it in TimescaleDB, serves it via REST API, and renders a terminal dashboard.

## Components

| Component | File | Description |
|---|---|---|
| WebSocket client | `feed/ws_client.py` | Connects to Alpaca IEX stream, authenticates, subscribes to trades + quotes |
| Normalizer | `feed/normalizer.py` | Maps raw Alpaca payloads to internal `Tick` dataclass, validates with Pydantic |
| Ingestor | `feed/ingestor.py` | Buffers ticks for 500ms then bulk-inserts into TimescaleDB; writes latest price to Redis |
| REST API | `api/` | FastAPI routes for health, tickers, latest prices, and OHLCV history |
| CLI dashboard | `cli/dashboard.py` | Rich terminal UI that auto-refreshes every second |
| Config | `config.py` | Pydantic Settings loaded from `.env` |

---

## Why TimescaleDB instead of plain PostgreSQL?

TimescaleDB extends PostgreSQL with time-series specific optimizations:

**Hypertables and automatic partitioning.** When you call `SELECT create_hypertable('ticks', 'time')`, TimescaleDB transparently partitions the table into "chunks" by time range (default: 7 days per chunk). A query with `WHERE time >= '2024-01-15'` only scans the relevant chunk — not the full table. On a table with months of tick data this is the difference between a millisecond scan and a full sequential scan.

**`time_bucket()` for OHLCV aggregation.** The history endpoint uses:
```sql
SELECT time_bucket('1 minute', time) AS bucket_time,
       first(price, time) AS open,
       MAX(price)         AS high,
       MIN(price)         AS low,
       last(price, time)  AS close,
       SUM(volume)        AS volume
FROM ticks
WHERE symbol = 'AAPL' AND time >= :from AND time < :to
GROUP BY bucket_time
ORDER BY bucket_time
```
`first()` and `last()` are TimescaleDB aggregate functions that return the value at the earliest/latest timestamp in a bucket — standard PostgreSQL has no equivalent. Doing this in Python would require fetching all raw rows and aggregating in memory.

**Chunk-based compression.** Chunks older than a configurable threshold can be compressed with `ALTER TABLE ticks SET (timescaledb.compress = true)`, reducing storage by 90%+ for numerical time-series data.

**Automatic retention policies.** `SELECT add_retention_policy('ticks', INTERVAL '90 days')` auto-drops old chunks without locking the table.

**When plain PostgreSQL is fine:** If you have low tick volume (< 1000/day), no aggregation queries, and retention isn't a concern, plain PostgreSQL works. The added operational complexity of TimescaleDB is only worth it at scale or when you need the aggregation functions.

---

## Why Redis for latest price?

The read pattern for latest price is extreme: every dashboard refresh (1/second × N clients) and every `/prices/{ticker}` API call needs exactly one value per symbol.

A PostgreSQL query for the latest row:
```sql
SELECT * FROM ticks WHERE symbol = 'AAPL' ORDER BY time DESC LIMIT 1
```
requires a DB round-trip, connection pool slot, and index scan — even with the `(symbol, time DESC)` index, that's ~1–5ms under load.

Redis keeps the latest price as a hash in memory, returning it in ~0.2ms with no connection overhead beyond an open socket.

**The tradeoff.** Redis can be up to one 500ms batch window ahead of TimescaleDB (in-flight writes). If the ingestor crashes mid-batch, Redis holds prices that aren't in the DB. For a price display use case this is acceptable — you're showing a human a number, not executing a trade. The `/prices/{ticker}` endpoint falls back to the DB if Redis is empty, so a Redis restart doesn't break anything.

---

## Why batch writes instead of writing every tick?

At market open, liquid stocks like AAPL or TSLA generate hundreds of trades and quotes per second. Writing each tick individually means:
- One database round-trip per tick
- One connection pool slot held per concurrent insert
- PostgreSQL WAL write per row

At 500 ticks/second this saturates a typical PostgreSQL connection pool within seconds.

Batching over 500ms windows:
- Reduces 500 individual inserts to a single `INSERT ... VALUES (row1), (row2), ..., (rowN)` statement
- Amortizes connection overhead across the batch
- PostgreSQL can log one WAL entry per batch instead of one per row

The latency cost is negligible for a price display system: a tick lands in Redis immediately (sub-millisecond) and appears in the dashboard on the next 1-second refresh. The 500ms batch delay only affects historical queries, which are inherently backward-looking anyway.

---

## Why exponential backoff on reconnect?

Immediately retrying a failed WebSocket connection is the fastest way to get banned by the upstream provider.

After a failure, the endpoint may be:
- Overloaded (hammering it makes it worse)
- Restarting (connecting too early gets you another immediate failure)
- Rate-limiting you for previous rapid reconnects

Exponential backoff (1s → 2s → 4s → 8s → 16s, max 5 retries) gives Alpaca's infrastructure time to recover while not leaving you disconnected indefinitely. The total wait before giving up is 31 seconds — enough time for a transient outage to resolve without burning through retries in seconds.

---

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for deep-dives on async design, the Redis + DB dual-write pattern, and OHLCV aggregation.

---

## API Reference

### `GET /health`

Returns connectivity status of all system components.

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "db_connected": true,
  "redis_connected": true,
  "feed_connected": true,
  "uptime_seconds": 142.3,
  "timestamp": "2024-01-15T14:30:01.234567Z"
}
```

`status` is `"healthy"` when DB and Redis are both up; `"degraded"` otherwise.

---

### `GET /tickers`

Lists all tracked symbols with their latest cached prices.

```bash
curl http://localhost:8000/tickers
```

```json
[
  {
    "symbol": "AAPL",
    "name": null,
    "latest_price": 182.50,
    "last_updated": "2024-01-15T14:30:00.123456+00:00"
  },
  {
    "symbol": "GOOGL",
    "name": null,
    "latest_price": 175.20,
    "last_updated": "2024-01-15T14:30:00.456789+00:00"
  }
]
```

---

### `GET /prices/{ticker}`

Returns the latest price for a single symbol. Reads from Redis (sub-millisecond); falls back to TimescaleDB if Redis is cold.

```bash
curl http://localhost:8000/prices/AAPL
```

```json
{
  "symbol": "AAPL",
  "price": 182.50,
  "bid": 182.49,
  "ask": 182.51,
  "volume": 100,
  "last_updated": "2024-01-15T14:30:00.123456+00:00",
  "source": "trade"
}
```

`source` is `"trade"` or `"quote"`. Returns `404` if no data exists for the symbol.

---

### `GET /history/{ticker}?from=&to=&interval=`

Returns OHLCV bars aggregated by `time_bucket()`. Requires TimescaleDB.

**Parameters:**

| Param | Type | Required | Description |
|---|---|---|---|
| `from` | ISO8601 datetime | Yes | Start of range (inclusive) |
| `to` | ISO8601 datetime | No | End of range (exclusive). Defaults to now. |
| `interval` | string | No | Bucket size: `1m`, `5m`, `15m`, `1h`, `1d`. Default: `1m` |

```bash
curl "http://localhost:8000/history/AAPL?from=2024-01-15T14:30:00Z&to=2024-01-15T14:35:00Z&interval=1m"
```

```json
[
  {
    "time": "2024-01-15T14:30:00Z",
    "open": 182.00,
    "high": 183.20,
    "low": 181.80,
    "close": 182.80,
    "volume": 24300
  },
  {
    "time": "2024-01-15T14:31:00Z",
    "open": 182.80,
    "high": 184.00,
    "low": 182.50,
    "close": 183.50,
    "volume": 18700
  }
]
```

Returns `400` for invalid interval or when `from >= to`. Returns `404` if no data in range.

---

## Running Locally

### 1. Get an Alpaca API key

Sign up for a free account at [alpaca.markets](https://alpaca.markets). Navigate to **Paper Trading → API Keys** and create a key pair. The free tier includes access to the IEX real-time feed.

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in ALPACA_API_KEY and ALPACA_API_SECRET
```

### 3. Start infrastructure

```bash
make up
```

This starts TimescaleDB (port 5432) and Redis (port 6379) via Docker Compose and waits for health checks to pass.

### 4. Run migrations

```bash
make migrate
```

Creates the `tickers` and `ticks` tables, converts `ticks` to a TimescaleDB hypertable, and adds the composite index.

### 5. Start the API + feed

```bash
make run
```

This runs `uvicorn main:app --reload`. On startup the app:
- Runs any pending Alembic migrations
- Seeds the `tickers` table with symbols from `.env`
- Starts the ingestor background loop
- Connects to the Alpaca WebSocket feed

### 6. Verify connectivity

```bash
curl http://localhost:8000/health
```

Wait 5–10 seconds for the feed to connect and ingest initial ticks, then:

```bash
curl http://localhost:8000/tickers
curl http://localhost:8000/prices/AAPL
curl "http://localhost:8000/history/AAPL?from=2024-01-15T14:00:00Z&interval=1m"
```

### 7. Launch the dashboard

In a separate terminal:

```bash
make dashboard
```

The dashboard polls the API every second and renders a live table. Press `Ctrl+C` to exit.

### 8. Run tests

```bash
make test
```

Tests are unit tests only — no running infrastructure required.

---

## Known Limitations

- **IEX feed only (free tier).** The Alpaca IEX feed is a consolidated best-bid/offer feed, not the full NYSE/NASDAQ tape. Trade prices are real but may not match the NBBO.
- **No API authentication.** All endpoints are publicly accessible. In production, add OAuth2 or API key middleware.
- **Single WebSocket connection per process.** The feed runs as one asyncio task in one process. You cannot scale horizontally without adding a message queue (e.g., Redis Streams or Kafka) between the feed and the ingestor.
- **Dashboard is read-only.** No ordering, filtering, or alerting from the terminal UI.
- **No continuous aggregates.** OHLCV queries scan raw tick data on every request. For production, use TimescaleDB continuous aggregates to pre-compute buckets.

---

## What Production Would Add

- **WebSocket sharding.** Split symbol subscriptions across multiple feed processes, publish to Redis Streams or Kafka, and have N ingestor workers consuming from the queue.
- **Per-user watchlists.** Store user-defined symbol lists in PostgreSQL; the dashboard API personalizes responses per authenticated user.
- **Order book data.** Alpaca's paid tier includes full order book snapshots. Store as JSONB in a separate hypertable.
- **Price threshold alerts.** A background worker polling Redis for price crossings, publishing events to a notification service.
- **TimescaleDB continuous aggregates.** Pre-compute 1m/5m/1h OHLCV via `CREATE MATERIALIZED VIEW ... WITH (timescaledb.continuous)`. History queries hit the materialized view instead of raw ticks.
- **WebSocket push API.** A FastAPI WebSocket endpoint that streams price updates to browser clients, eliminating polling.
- **Observability.** Prometheus metrics (ticks/sec, ingest latency, queue depth), Grafana dashboards, and alerting on feed disconnection.
