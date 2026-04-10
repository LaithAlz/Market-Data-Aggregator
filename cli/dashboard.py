"""
Rich terminal dashboard — auto-refreshes every second.

Run with:
    python -m cli.dashboard

Reads from the REST API (not directly from Redis/DB) so it exercises
the same code path as external consumers.

Layout:
  ┌─────────────────────────────────────────────────────────────────┐
  │               MARKET FEED DASHBOARD  2024-01-15 14:30:01        │
  ├──────┬──────────┬──────────┬──────────┬──────────┬──────────────┤
  │Symbol│  Price   │   Bid    │   Ask    │ Change % │ Last Updated  │
  ├──────┼──────────┼──────────┼──────────┼──────────┼──────────────┤
  │ AAPL │  182.50  │  182.49  │  182.51  │  +0.42%  │ 14:30:00.123 │
  │  ... │   ...    │   ...    │   ...    │    ...   │     ...      │
  └──────┴──────────┴──────────┴──────────┴──────────┴──────────────┘
  Feed: ● CONNECTED   Ticks/s: 42.1   DB: ● OK   Redis: ● OK
"""
import asyncio
import sys
from datetime import datetime, timezone
from typing import Optional

import httpx
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

API_BASE = "http://localhost:8000"
REFRESH_INTERVAL = 1.0  # seconds

console = Console()

# Track previous prices for change % calculation
_prev_prices: dict[str, float] = {}
_session_open_prices: dict[str, float] = {}  # first price seen this session


def _fmt_price(val: Optional[float]) -> str:
    if val is None:
        return "—"
    return f"{val:,.4f}"


def _fmt_change(symbol: str, current: Optional[float]) -> Text:
    if current is None:
        return Text("—", style="dim")

    open_price = _session_open_prices.get(symbol)
    if open_price is None:
        _session_open_prices[symbol] = current
        return Text("0.00%", style="white")

    pct = ((current - open_price) / open_price) * 100
    if pct > 0:
        return Text(f"+{pct:.2f}%", style="bold green")
    elif pct < 0:
        return Text(f"{pct:.2f}%", style="bold red")
    else:
        return Text("0.00%", style="white")


def _price_style(symbol: str, current: Optional[float]) -> str:
    if current is None:
        return "dim"
    prev = _prev_prices.get(symbol)
    if prev is None:
        return "white"
    if current > prev:
        return "bold green"
    elif current < prev:
        return "bold red"
    return "white"


def _fmt_time(iso: Optional[str]) -> str:
    if iso is None:
        return "—"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%H:%M:%S.%f")[:-3]
    except Exception:
        return iso[:19]


async def _fetch_tickers(client: httpx.AsyncClient) -> list[dict]:
    try:
        r = await client.get(f"{API_BASE}/tickers", timeout=2.0)
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


async def _fetch_health(client: httpx.AsyncClient) -> dict:
    try:
        r = await client.get(f"{API_BASE}/health", timeout=2.0)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


async def _fetch_price(client: httpx.AsyncClient, symbol: str) -> Optional[dict]:
    try:
        r = await client.get(f"{API_BASE}/prices/{symbol}", timeout=2.0)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def _build_table(ticker_rows: list[dict], price_data: dict[str, dict]) -> Table:
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="bright_black",
        expand=True,
    )
    table.add_column("Symbol", style="bold white", width=8, justify="center")
    table.add_column("Price", justify="right", width=12)
    table.add_column("Bid", justify="right", width=12)
    table.add_column("Ask", justify="right", width=12)
    table.add_column("Change %", justify="right", width=10)
    table.add_column("Volume", justify="right", width=12)
    table.add_column("Last Updated", justify="right", width=16)

    for ticker in ticker_rows:
        symbol = ticker["symbol"]
        pd = price_data.get(symbol) or {}
        price = pd.get("price")
        bid = pd.get("bid")
        ask = pd.get("ask")
        volume = pd.get("volume")
        last_updated = pd.get("last_updated") or ticker.get("last_updated")

        style = _price_style(symbol, price)
        change_text = _fmt_change(symbol, price)

        table.add_row(
            symbol,
            Text(_fmt_price(price), style=style),
            _fmt_price(bid),
            _fmt_price(ask),
            change_text,
            f"{volume:,}" if volume else "—",
            _fmt_time(last_updated),
        )

        if price is not None:
            _prev_prices[symbol] = price

    return table


def _build_status_bar(health: dict) -> Panel:
    feed_ok = health.get("feed_connected", False)
    db_ok = health.get("db_connected", False)
    redis_ok = health.get("redis_connected", False)
    uptime = health.get("uptime_seconds", 0)

    feed_dot = "[bold green]●[/] CONNECTED" if feed_ok else "[bold red]●[/] DISCONNECTED"
    db_dot = "[bold green]●[/] OK" if db_ok else "[bold red]●[/] DOWN"
    redis_dot = "[bold green]●[/] OK" if redis_ok else "[bold red]●[/] DOWN"

    now = datetime.now(tz=timezone.utc).strftime("%H:%M:%S UTC")
    uptime_str = f"{int(uptime)}s" if uptime < 60 else f"{int(uptime // 60)}m {int(uptime % 60)}s"

    content = (
        f"Feed: {feed_dot}    "
        f"DB: {db_dot}    "
        f"Redis: {redis_dot}    "
        f"Uptime: {uptime_str}    "
        f"Time: {now}"
    )
    return Panel(content, border_style="bright_black", height=3)


def _build_header() -> Panel:
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d  %H:%M:%S UTC")
    title = Text("MARKET FEED DASHBOARD", style="bold white")
    title.append(f"   {now}", style="dim")
    return Panel(title, border_style="cyan", height=3)


async def run_dashboard() -> None:
    async with httpx.AsyncClient() as client:
        with Live(console=console, refresh_per_second=2, screen=True) as live:
            while True:
                # Fetch in parallel
                tickers_task = asyncio.create_task(_fetch_tickers(client))
                health_task = asyncio.create_task(_fetch_health(client))
                ticker_rows, health_data = await asyncio.gather(
                    tickers_task, health_task
                )

                # Fetch individual prices in parallel
                price_tasks = {
                    t["symbol"]: asyncio.create_task(
                        _fetch_price(client, t["symbol"])
                    )
                    for t in ticker_rows
                }
                price_results = {
                    sym: await task for sym, task in price_tasks.items()
                }

                # Build layout
                layout = Layout()
                layout.split_column(
                    Layout(_build_header(), name="header", size=3),
                    Layout(_build_table(ticker_rows, price_results), name="table"),
                    Layout(_build_status_bar(health_data), name="status", size=3),
                )
                live.update(layout)

                await asyncio.sleep(REFRESH_INTERVAL)


def main() -> None:
    try:
        asyncio.run(run_dashboard())
    except KeyboardInterrupt:
        console.print("\n[dim]Dashboard stopped.[/]")


if __name__ == "__main__":
    main()
