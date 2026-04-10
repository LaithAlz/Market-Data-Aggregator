import { useEffect, useRef, useState } from 'react';
import {
  createChart,
  ColorType,
  CrosshairMode,
  CandlestickSeries,
  HistogramSeries,
} from 'lightweight-charts';
import { fetchHistory, fetchPrice, type PriceDetail } from '../api';

// ── Constants ──────────────────────────────────────────────────────────────────
const INTERVALS = ['1m', '5m', '15m', '1h', '1d'] as const;
const RANGES = [
  { label: '1H',  hours: 1   },
  { label: '4H',  hours: 4   },
  { label: '1D',  hours: 24  },
  { label: '1W',  hours: 168 },
  { label: '1M',  hours: 720 },
] as const;

type Interval = typeof INTERVALS[number];

// ── Helpers ────────────────────────────────────────────────────────────────────
function fmt(v: number | null, d = 2) {
  if (v == null) return '—';
  return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
}

// ── BtnGroup ───────────────────────────────────────────────────────────────────
function BtnGroup<T extends string | number>({
  options, active, onSelect,
}: {
  options: readonly { label: string; value: T }[];
  active: T;
  onSelect: (v: T) => void;
}) {
  return (
    <div className="flex border border-slate-800 rounded-md overflow-hidden">
      {options.map(({ label, value }) => (
        <button
          key={label}
          onClick={() => onSelect(value)}
          className={[
            'px-2.5 py-1 text-xs font-mono transition-colors duration-100',
            active === value
              ? 'bg-sky-800 text-white'
              : 'bg-transparent text-slate-500 hover:bg-slate-800 hover:text-slate-300',
          ].join(' ')}
        >
          {label}
        </button>
      ))}
    </div>
  );
}

// ── ChartPanel ─────────────────────────────────────────────────────────────────
interface Props {
  symbol: string | null;
}

export default function ChartPanel({ symbol }: Props) {
  const [interval, setIntervalVal] = useState<Interval>('1m');
  const [hours,    setHours]       = useState(24);
  const [detail,   setDetail]      = useState<PriceDetail | null>(null);
  const [noData,   setNoData]      = useState(false);
  const [loading,  setLoading]     = useState(false);
  const [periodChg, setPeriodChg]  = useState<{ pct: number; close: number } | null>(null);

  const wrapRef  = useRef<HTMLDivElement>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const chartRef = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const cRef     = useRef<any>(null);
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const vRef     = useRef<any>(null);

  // ── Init chart once ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!wrapRef.current) return;

    const chart = createChart(wrapRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#070d1a' },
        textColor: '#4a6080',
        fontFamily: "'SF Mono','Fira Code','Consolas',monospace",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: '#0d1626' },
        horzLines: { color: '#0d1626' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
        vertLine: { color: '#2d4a6e', labelBackgroundColor: '#0e6490' },
        horzLine: { color: '#2d4a6e', labelBackgroundColor: '#0e6490' },
      },
      rightPriceScale: { borderColor: '#0d1626' },
      timeScale: {
        borderColor: '#0d1626',
        timeVisible: true,
        secondsVisible: true,
      },
      width:  wrapRef.current.clientWidth,
      height: wrapRef.current.clientHeight,
    });

    // v5 API: addSeries(SeriesType, options)
    const candles = chart.addSeries(CandlestickSeries, {
      upColor:         '#34d399',
      downColor:       '#f87171',
      borderUpColor:   '#34d399',
      borderDownColor: '#f87171',
      wickUpColor:     '#34d399',
      wickDownColor:   '#f87171',
    });

    const volumes = chart.addSeries(HistogramSeries, {
      priceFormat:  { type: 'volume' },
      priceScaleId: 'vol',
    });
    chart.priceScale('vol').applyOptions({
      scaleMargins: { top: 0.82, bottom: 0 },
    });

    chartRef.current = chart;
    cRef.current     = candles;
    vRef.current     = volumes;

    const ro = new ResizeObserver(() => {
      if (wrapRef.current)
        chart.applyOptions({ width: wrapRef.current.clientWidth, height: wrapRef.current.clientHeight });
    });
    ro.observe(wrapRef.current);

    return () => {
      ro.disconnect();
      chart.remove();
      chartRef.current = null;
      cRef.current     = null;
      vRef.current     = null;
    };
  }, []);

  // ── Load price detail ────────────────────────────────────────────────────────
  useEffect(() => {
    if (!symbol) return;
    setDetail(null);
    fetchPrice(symbol).then(setDetail).catch(() => {});
  }, [symbol]);

  // ── Load chart data ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!symbol || !cRef.current || !vRef.current) return;

    setLoading(true);
    setNoData(false);
    setPeriodChg(null);

    fetchHistory(symbol, interval, hours)
      .then(bars => {
        if (!cRef.current || !vRef.current) return;

        if (bars.length === 0) {
          cRef.current.setData([]);
          vRef.current.setData([]);
          setNoData(true);
          setLoading(false);
          return;
        }

        const cData = bars.map(b => ({
          time:  Math.floor(new Date(b.time).getTime() / 1000),
          open:  b.open, high: b.high, low: b.low, close: b.close,
        }));
        const vData = bars.map(b => ({
          time:  Math.floor(new Date(b.time).getTime() / 1000),
          value: b.volume ?? 0,
          color: b.close >= b.open ? '#14532d' : '#7f1d1d',
        }));

        cRef.current.setData(cData);
        vRef.current.setData(vData);
        chartRef.current?.timeScale().fitContent();

        const last = bars[bars.length - 1];
        const pct  = ((last.close - bars[0].open) / bars[0].open) * 100;
        setPeriodChg({ pct, close: last.close });
        setNoData(false);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [symbol, interval, hours]);

  const intervalOptions = INTERVALS.map(iv => ({ label: iv, value: iv as Interval }));
  const rangeOptions    = RANGES.map(r  => ({ label: r.label, value: r.hours as number }));

  return (
    <div className="flex flex-col h-full min-w-0">

      {/* Panel header */}
      <div className="flex items-center justify-between px-5 h-14 border-b border-slate-900 bg-[#070d1a] flex-shrink-0">
        <div className="flex items-baseline gap-3 min-w-0">
          <span className="text-xl font-bold text-slate-100 tracking-wide">
            {symbol ?? '—'}
          </span>
          {periodChg && (
            <>
              <span className="text-slate-300 tabular-nums font-semibold">
                ${fmt(periodChg.close, 4)}
              </span>
              <span className={`text-sm tabular-nums font-medium ${periodChg.pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {periodChg.pct >= 0 ? '+' : ''}{periodChg.pct.toFixed(2)}%
              </span>
            </>
          )}
          {detail && (
            <span className="text-slate-600 text-xs truncate">
              {[
                detail.bid   != null ? `Bid ${fmt(detail.bid, 4)}`   : null,
                detail.ask   != null ? `Ask ${fmt(detail.ask, 4)}`   : null,
                detail.source ? detail.source.toUpperCase()           : null,
              ].filter(Boolean).join('  ·  ')}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2 flex-shrink-0">
          <BtnGroup options={intervalOptions} active={interval} onSelect={v => setIntervalVal(v)} />
          <BtnGroup options={rangeOptions}    active={hours}    onSelect={v => setHours(v)}       />
        </div>
      </div>

      {/* Chart */}
      <div className="relative flex-1 min-h-0" ref={wrapRef}>
        {!symbol && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-700 text-sm z-10 pointer-events-none">
            ← Select a ticker to view chart
          </div>
        )}
        {symbol && noData && !loading && (
          <div className="absolute inset-0 flex items-center justify-center text-slate-600 text-sm z-10 pointer-events-none">
            No data for {symbol} in this range — market may be closed
          </div>
        )}
        {loading && (
          <div className="absolute top-3 right-4 text-slate-700 text-xs z-10 pointer-events-none">
            Loading…
          </div>
        )}
      </div>
    </div>
  );
}
