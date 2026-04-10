# Architecture

## Why Time-Series Databases Exist

A relational database like PostgreSQL optimizes for random access by primary key: given a row ID, find the row in O(log N) via a B-tree index. This is ideal for OLTP workloads — looking up a user by ID, fetching an order by number.

Time-series workloads are fundamentally different:

1. **Append-heavy.** New data is always newer than existing data. You never update a past tick. Inserts are sequential by time.
2. **Query by time range.** "Give me all ticks for AAPL between 14:30 and 15:00." No lookups by arbitrary primary key.
3. **Aggregate constantly.** "Give me the high price in each 1-minute bucket." Almost no queries return raw rows.

Plain PostgreSQL can handle this, but:

- A `WHERE time >= X AND time <= Y` query scans the full table (or the index, but the index covers all time). As the table grows to hundreds of millions of rows, this gets slow.
- There's no built-in `first(value, order_key)` or `last()` aggregate, so OHLCV requires a subquery or window function that's verbose and slower than it needs to be.

**TimescaleDB's hypertable solution:**

When you run `SELECT create_hypertable('ticks', 'time')`, TimescaleDB wraps the table in a partition manager. Internally it creates child tables ("chunks"), each covering a fixed time range (default 7 days). The parent table is a transparent router.

```
ticks (parent)
├── _hyper_1_1_chunk  [2024-01-08 → 2024-01-15)
├── _hyper_1_2_chunk  [2024-01-15 → 2024-01-22)
└── _hyper_1_3_chunk  [2024-01-22 → 2024-01-29)
```

A query `WHERE time >= '2024-01-15T14:00:00'` goes directly to chunk 2. The planner doesn't touch chunks 1 or 3 at all — this is called **chunk exclusion**. On a table with years of data, this turns a full scan into a scan of the relevant chunk only.

The `time_bucket()` function and `first()`/`last()` aggregates are implemented in C inside TimescaleDB, running faster than equivalent SQL expressions.

---

## The Redis + DB Dual-Write Pattern

Every tick that arrives from Alpaca is written to two stores:

```
Tick
 ├── Redis:  SET price:AAPL {price, bid, ask, ...}    (immediate, ~0.2ms)
 └── Queue → Batch flush every 500ms → TimescaleDB    (delayed, ~50ms)
```

**Why write to both?**

Redis answers the question "what is AAPL trading at right now?" in sub-millisecond time. TimescaleDB answers "what did AAPL trade at between 2:30pm and 3:00pm last Tuesday?" Redis has no history; TimescaleDB has all of it.

**The inconsistency window.**

At any given moment, Redis may be up to 500ms ahead of TimescaleDB. The ingestor buffers ticks in memory, so ticks in the current batch exist in Redis but not yet in the DB.

This is acceptable for price display: a human looking at a dashboard doesn't notice 500ms of lag. It is **not acceptable** for an order execution system, where the price in the DB must be the authoritative record before any trade is committed.

**Redis ahead of DB (normal case):**
```
tick arrives at T=0
  → Redis updated at T=0ms (price:AAPL = 182.50)
  → DB insert at T=0ms to T=500ms (buffering)
  → DB committed at T=500ms

Query at T=200ms:
  → Redis returns 182.50 ✓
  → DB returns 182.49 (last committed value) — stale but not wrong
```

**Ingestor crash mid-batch:**
```
Ticks 1-10 arrive, written to Redis
Ingestor crashes before batch flush
Redis: price:AAPL = 182.50 (latest value from crashed batch)
DB: last committed = 182.45 (10 ticks ago)

On restart:
  → Redis serves 182.50 from memory (correct)
  → Ticks 1-10 are lost from DB (no persistence)
  → DB falls behind until next flush succeeds
```

The `/prices/{ticker}` endpoint handles this: it reads from Redis first, and falls back to TimescaleDB if Redis is empty. Redis being ahead is fine; Redis being empty (cold start or flush) falls back gracefully.

---

## Async Architecture

The entire system runs on a single asyncio event loop, shared between FastAPI, the WebSocket client, and the ingestor.

```
asyncio event loop
├── uvicorn (HTTP server)          — handles incoming API requests
├── ws_feed task                   — receives WebSocket messages from Alpaca
└── ingestor task                  — sleeps 500ms, wakes, drains queue, writes DB
```

**Why async matters here.**

The WebSocket client does `async for raw in ws:` — it yields control to the event loop between each message. While waiting for the next Alpaca message (which may not come for milliseconds), the event loop can service an incoming API request.

If the DB write in the ingestor were synchronous (blocking), it would freeze the entire event loop for the duration of the write — including the WebSocket receiver. Missed messages pile up in the Alpaca stream buffer, and you fall behind real-time.

`asyncpg` solves this: it implements the PostgreSQL wire protocol using Python's `asyncio`, so database I/O is non-blocking. The ingestor's bulk insert yields control back to the loop while waiting for the network round-trip to PostgreSQL.

**Why not threads?**

Python's GIL means threads don't give true parallelism for CPU-bound work. For I/O-bound work like network and DB calls, asyncio is lower-overhead than threads because context switches are explicit (at `await` points) rather than preemptive, and there's no need for locks on shared state within a single coroutine.

The queue between the WebSocket client and the ingestor (`asyncio.Queue`) is thread-safe by design and requires no locking.

---

## OHLCV Aggregation with `time_bucket()`

The history endpoint runs this query against TimescaleDB:

```sql
SELECT
    time_bucket('1 minute', time)  AS bucket_time,
    first(price, time)             AS open,
    MAX(price)                     AS high,
    MIN(price)                     AS low,
    last(price, time)              AS close,
    SUM(volume)                    AS volume
FROM ticks
WHERE
    symbol = 'AAPL'
    AND time >= '2024-01-15T14:30:00Z'
    AND time <  '2024-01-15T15:30:00Z'
GROUP BY bucket_time
ORDER BY bucket_time ASC;
```

**`time_bucket('1 minute', time)`** truncates each timestamp to the nearest 1-minute boundary. `14:30:42.123` becomes `14:30:00.000`. All rows in the same minute map to the same bucket.

**`first(price, time)`** returns the `price` value at the row with the smallest `time` in the bucket — the opening price. Standard PostgreSQL has no `first()` aggregate; you'd need:
```sql
(array_agg(price ORDER BY time))[1]  -- slow, allocates array
```
TimescaleDB's `first()` is implemented in C and only tracks a single running minimum without materializing the array.

**`last(price, time)`** analogously returns the value at the maximum timestamp — the closing price.

**Why this is faster in the DB than in Python:**

- The `WHERE symbol = 'AAPL'` clause, combined with the `(symbol, time DESC)` index and chunk exclusion, means the DB touches only the rows it needs.
- `GROUP BY bucket_time` aggregation runs inside the DB process with no serialization overhead.
- Returning N OHLCV rows over the wire is orders of magnitude cheaper than returning M raw ticks (where M >> N for any meaningful time range).

Doing this in Python would require:
1. `SELECT price, time, volume FROM ticks WHERE symbol=... AND time BETWEEN ...`
2. Fetching all raw rows over the network
3. Grouping them by minute in Python
4. Computing min/max/first/last in Python

For 1 hour of AAPL data at 200 ticks/minute, that's 12,000 rows vs. 60 OHLCV rows. The network transfer and Python iteration cost dominate.

---

## Latency Budget

End-to-end latency from a real market event to the dashboard rendering:

| Stage | Latency | Notes |
|---|---|---|
| NYSE/NASDAQ → Alpaca | ~1–3ms | Alpaca's market data infrastructure |
| Alpaca → ws_client (network) | ~5–15ms | Depends on your internet connection and Alpaca's PoP |
| `normalizer.normalize()` | ~0.1ms | Pydantic validation + timestamp parsing |
| `ingestor.enqueue()` | <0.01ms | Non-blocking queue put |
| Redis write (`set_latest_price`) | ~0.2–0.5ms | Local loopback if Redis is on the same host |
| TimescaleDB batch write | ~20–80ms | Amortized over the batch; does not block Redis read |
| Dashboard API call | ~1–3ms | FastAPI → Redis read → JSON serialize |
| Dashboard render (Rich) | ~2ms | Terminal output |

**Total for dashboard display:** ~10–25ms after the market event reaches Alpaca.

The 500ms batch window means TimescaleDB sees data up to 500ms later than Redis. For history queries, the most recent 500ms of data may not yet be committed. This is a known and documented limitation.

The Redis write is on the critical path for dashboard latency; the TimescaleDB write is not (it's asynchronous behind the buffer). This is why the architecture separates the two stores rather than writing to TimescaleDB first and reading from it for the dashboard.
