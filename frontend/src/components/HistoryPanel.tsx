import { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, LineSeries } from 'lightweight-charts';
import { fetchRawTicks, type RawTick } from '../api';

function fmt(v: number, d = 2) {
  return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
}

function fmtTime(iso: string) {
  try {
    return new Date(iso).toLocaleTimeString('en-US', { hour12: false });
  } catch { return iso; }
}

function fmtDate(iso: string) {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
      + ' ' + d.toLocaleTimeString('en-US', { hour12: false });
  } catch { return iso; }
}

export default function HistoryPanel({ symbol }: { symbol: string }) {
  const [ticks, setTicks] = useState<RawTick[]>([]);
  const [loading, setLoading] = useState(true);
  const [noData, setNoData] = useState(false);

  const chartWrap = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const chartRef  = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const lineRef   = useRef<any>(null);

  // Init chart once
  useEffect(() => {
    if (!chartWrap.current) return;
    const chart = createChart(chartWrap.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#070d1a' },
        textColor: '#475569',
        fontFamily: 'monospace',
        fontSize: 11,
      },
      grid: { vertLines: { color: '#0d1626' }, horzLines: { color: '#0d1626' } },
      rightPriceScale: { borderColor: '#0d1626' },
      timeScale: { borderColor: '#0d1626', timeVisible: true, secondsVisible: true },
      crosshair: { vertLine: { labelBackgroundColor: '#0e7490' }, horzLine: { labelBackgroundColor: '#0e7490' } },
      width:  chartWrap.current.clientWidth,
      height: chartWrap.current.clientHeight,
    });

    const line = chart.addSeries(LineSeries, {
      color: '#38bdf8',
      lineWidth: 2,
      priceLineVisible: true,
      lastValueVisible: true,
    });

    chartRef.current = chart;
    lineRef.current  = line;

    const ro = new ResizeObserver(() => {
      if (chartWrap.current)
        chart.applyOptions({ width: chartWrap.current.clientWidth, height: chartWrap.current.clientHeight });
    });
    ro.observe(chartWrap.current);

    return () => { ro.disconnect(); chart.remove(); chartRef.current = null; lineRef.current = null; };
  }, []);

  // Load + refresh data
  useEffect(() => {
    let alive = true;

    const load = async () => {
      try {
        const data = await fetchRawTicks(symbol, 300);
        if (!alive) return;

        setTicks(data);
        setNoData(data.length === 0);
        setLoading(false);

        if (lineRef.current && data.length > 0) {
          // Deduplicate by second — keep last tick per second (lightweight-charts needs strictly increasing timestamps)
          const seen = new Map<number, number>();
          for (const t of data) {
            const sec = Math.floor(new Date(t.time).getTime() / 1000);
            seen.set(sec, t.price);
          }
          const lineData = Array.from(seen.entries())
            .map(([time, value]) => ({ time, value }))
            .sort((a, b) => a.time - b.time);
          lineRef.current.setData(lineData);
          chartRef.current?.timeScale().fitContent();
        }
      } catch {
        if (alive) setLoading(false);
      }
    };

    setLoading(true);
    setNoData(false);
    load();
    const id = setInterval(load, 5000); // refresh every 5s
    return () => { alive = false; clearInterval(id); };
  }, [symbol]);

  return (
    <div className="flex flex-col flex-1 overflow-hidden border-l border-slate-900 min-w-0">

      {/* Header */}
      <div className="flex items-center justify-between px-5 h-11 border-b border-slate-900 flex-shrink-0">
        <span className="text-sky-300 font-bold text-sm tracking-wider">{symbol} — Price History</span>
        <span className="text-slate-600 text-xs">{ticks.length > 0 ? `${ticks.length} entries` : ''}</span>
      </div>

      {/* Line chart */}
      <div className="relative flex-shrink-0" style={{ height: 220 }} ref={chartWrap}>
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-700 text-xs z-10">
            Loading…
          </div>
        )}
        {noData && !loading && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-700 text-xs z-10">
            No data yet — waiting for ticks
          </div>
        )}
      </div>

      {/* Divider */}
      <div className="border-t border-slate-900 flex-shrink-0" />

      {/* Scrollable tick list */}
      <div className="flex-1 overflow-y-auto">
        {/* Column headers */}
        <div className="sticky top-0 bg-[#070d1a] grid grid-cols-4 gap-2 px-4 py-2 border-b border-slate-900 text-slate-600 text-xs uppercase tracking-wider">
          <span>Time</span>
          <span className="text-right">Price</span>
          <span className="text-right">Bid / Ask</span>
          <span className="text-right">Source</span>
        </div>

        {[...ticks].reverse().map((t, i) => {
          const next = [...ticks].reverse()[i + 1];
          const up   = next ? t.price > next.price : null;
          const priceColor = up === true ? 'text-emerald-400' : up === false ? 'text-red-400' : 'text-slate-300';

          return (
            <div
              key={t.time + i}
              className="grid grid-cols-4 gap-2 px-4 py-2 border-b border-slate-900/40 text-xs hover:bg-slate-900/30 transition-colors"
            >
              <span className="text-slate-500 tabular-nums">{fmtDate(t.time)}</span>
              <span className={`text-right tabular-nums font-semibold ${priceColor}`}>${fmt(t.price, 4)}</span>
              <span className="text-right text-slate-500 tabular-nums">
                {t.bid != null ? fmt(t.bid, 4) : '—'} / {t.ask != null ? fmt(t.ask, 4) : '—'}
              </span>
              <span className={`text-right ${t.source === 'trade' ? 'text-sky-600' : 'text-slate-600'}`}>
                {t.source}
              </span>
            </div>
          );
        })}

        {!loading && ticks.length === 0 && (
          <div className="p-8 text-center text-slate-700 text-xs">
            No price history yet. Ticks will appear here as they arrive.
          </div>
        )}
      </div>
    </div>
  );
}
