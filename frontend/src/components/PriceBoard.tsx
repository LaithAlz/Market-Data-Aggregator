import { useEffect, useRef, useState } from 'react';
import { fetchTickers, type TickerItem } from '../api';

function fmt(v: number | null, d = 2) {
  if (v == null) return '—';
  return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
}

function fmtTime(iso: string | null) {
  if (!iso) return '—';
  try { return new Date(iso).toLocaleTimeString('en-US', { hour12: false }); }
  catch { return '—'; }
}

interface RowState { price: number | null; open0: number | null; flash: 'up' | 'down' | null; }

export default function PriceBoard({
  selected, onSelect,
}: { selected: string | null; onSelect: (s: string) => void }) {
  const [tickers, setTickers] = useState<TickerItem[]>([]);
  const [rows, setRows] = useState<Record<string, RowState>>({});
  const timers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  useEffect(() => {
    const poll = async () => {
      try {
        const data = await fetchTickers();
        setTickers(data);
        setRows(prev => {
          const next = { ...prev };
          data.forEach(t => {
            const { symbol: sym, latest_price: price } = t;
            const cur = prev[sym];
            const open0 = cur?.open0 ?? price;
            let flash: 'up' | 'down' | null = null;
            if (cur && price != null && cur.price != null) {
              if (price > cur.price) flash = 'up';
              else if (price < cur.price) flash = 'down';
            }
            next[sym] = { price, open0, flash };
            if (flash) {
              clearTimeout(timers.current[sym]);
              timers.current[sym] = setTimeout(() =>
                setRows(r => ({ ...r, [sym]: { ...r[sym], flash: null } })), 700);
            }
          });
          return next;
        });
      } catch {}
    };
    poll();
    const id = setInterval(poll, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className={`flex flex-col border-r border-slate-900 overflow-y-auto ${selected ? 'w-80 flex-shrink-0' : 'flex-1'}`}>
      {tickers.map(t => {
        const sym = t.symbol;
        const row = rows[sym];
        const price = row?.price ?? t.latest_price;
        const open0 = row?.open0;
        const flash = row?.flash;
        const isSelected = selected === sym;

        let pct = 0, pctTxt = '—', pctPos = true;
        if (price != null && open0 != null) {
          pct = ((price - open0) / open0) * 100;
          pctTxt = (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%';
          pctPos = pct >= 0;
        }

        const priceCol = flash === 'up' ? 'text-emerald-400' : flash === 'down' ? 'text-red-400' : 'text-slate-100';

        return (
          <div
            key={sym}
            onClick={() => onSelect(sym)}
            className={[
              'flex items-center justify-between px-5 py-4 border-b border-slate-900/60 cursor-pointer transition-colors',
              flash === 'up'   ? 'flash-up'   : '',
              flash === 'down' ? 'flash-down' : '',
              isSelected ? 'bg-slate-800/60' : 'hover:bg-slate-900/40',
            ].join(' ')}
          >
            {/* Symbol */}
            <span className="text-sky-300 font-bold text-base w-14">{sym}</span>

            {/* Price */}
            <span className={`font-semibold tabular-nums text-sm ${priceCol} flex-1 text-right`}>
              {price != null ? `$${fmt(price, 2)}` : '—'}
            </span>

            {/* Change */}
            <span className={`tabular-nums text-sm w-20 text-right ${open0 != null && price != null ? (pctPos ? 'text-emerald-400' : 'text-red-400') : 'text-slate-600'}`}>
              {pctTxt}
            </span>

            {/* Time */}
            <span className="text-slate-600 text-xs w-20 text-right">{fmtTime(t.last_updated)}</span>
          </div>
        );
      })}

      {tickers.length === 0 && (
        <div className="flex-1 flex items-center justify-center text-slate-700 text-xs">
          Connecting…
        </div>
      )}
    </div>
  );
}
