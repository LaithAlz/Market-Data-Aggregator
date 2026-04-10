const BASE = 'http://localhost:8000';

export interface TickerItem {
  symbol: string;
  name: string | null;
  latest_price: number | null;
  last_updated: string | null;
}

export interface PriceDetail {
  symbol: string;
  price: number | null;
  bid: number | null;
  ask: number | null;
  volume: number | null;
  last_updated: string | null;
  source: string | null;
}

export interface HealthData {
  status: string;
  db_connected: boolean;
  redis_connected: boolean;
  feed_connected: boolean;
  uptime_seconds: number;
  timestamp: string;
}

export interface OHLCVBar {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
}

export async function fetchTickers(): Promise<TickerItem[]> {
  const r = await fetch(`${BASE}/tickers`);
  if (!r.ok) throw new Error('tickers fetch failed');
  return r.json();
}

export async function fetchHealth(): Promise<HealthData> {
  const r = await fetch(`${BASE}/health`);
  if (!r.ok) throw new Error('health fetch failed');
  return r.json();
}

export async function fetchPrice(symbol: string): Promise<PriceDetail> {
  const r = await fetch(`${BASE}/prices/${symbol}`);
  if (!r.ok) throw new Error(`price fetch failed for ${symbol}`);
  return r.json();
}

export interface RawTick {
  time: string;
  price: number;
  bid: number | null;
  ask: number | null;
  volume: number | null;
  source: string;
}

export async function fetchRawTicks(symbol: string, limit = 200): Promise<RawTick[]> {
  const r = await fetch(`${BASE}/ticks/${symbol}?limit=${limit}`);
  if (r.status === 404) return [];
  if (!r.ok) throw new Error('ticks fetch failed');
  return r.json();
}

export async function fetchHistory(
  symbol: string,
  interval: string,
  hours: number,
): Promise<OHLCVBar[]> {
  const to   = new Date();
  const from = new Date(to.getTime() - hours * 3_600_000);
  const url  = `${BASE}/history/${symbol}?from=${from.toISOString()}&to=${to.toISOString()}&interval=${interval}`;
  const r = await fetch(url);
  if (r.status === 404) return [];
  if (!r.ok) throw new Error('history fetch failed');
  return r.json();
}
