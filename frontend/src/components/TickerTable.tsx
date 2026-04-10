import { useEffect, useRef, useState } from 'react';
import { fetchTickers, type TickerItem } from '../api';

function fmt(v: number | null, d = 2): string {
  if (v == null) return '—';
  return v.toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
}

function fmtTime(iso: string | null): string {
  if (!iso) return '—';
  try {
    return new Date(iso).toLocaleTimeString('en-US', { hour12: false });
  } catch { return '—'; }
}

interface RowState {
  price: number | null;
  open0: number | null;
  flash: 'up' | 'down' | null;
}

interface Props {
  selected: string | null;
  onSelect: (sym: string) => void;
}

export default function TickerTable({ selected, onSelect }: Props) {
  const [tickers, setTickers] = useState<TickerItem[]>([]);
  const [rows,    setRows]    = useState<Record<string, RowState>>({});
  const [error,   setError]   = useState(false);
  const flashTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({});

  useEffect(() => {
    const poll = async () => {
      try {
        const data = await fetchTickers();
        setError(false);
        setTickers(data);
        setRows(prev => {
          const next = { ...prev };
          data.forEach(t => {
            const sym   = t.symbol;
            const price = t.latest_price;
            const cur   = prev[sym];
            const open0 = cur?.open0 ?? price;
            let flash: 'up' | 'down' | null = null;

            if (cur && price != null && cur.price != null) {
              if (price > cur.price) flash = 'up';
              else if (price < cur.price) flash = 'down';
            }

            next[sym] = { price, open0, flash };

            // Clear flash after animation
            if (flash) {
              clearTimeout(flashTimers.current[sym]);
              flashTimers.current[sym] = setTimeout(() => {
                setRows(r => ({ ...r, [sym]: { ...r[sym], flash: null } }));
              }, 800);
            }
          });
          return next;
        });
      } catch {
        setError(true);
      }
    };

    poll();
    const id = setInterval(poll, 1000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex flex-col h-full border-r border-slate-900">
      <table className="w-full border-collapse text-sm">
        <thead className="sticky top-0 z-10 bg-[#070d1a]">
          <tr className="border-b border-slate-900">
            <th className="px-4 py-2.5 text-left   text-xs font-medium text-slate-600 tracking-widest uppercase">Symbol</th>
            <th className="px-4 py-2.5 text-right  text-xs font-medium text-slate-600 tracking-widest uppercase">Price</th>
            <th className="px-4 py-2.5 text-right  text-xs font-medium text-slate-600 tracking-widest uppercase">Change</th>
            <th className="px-4 py-2.5 text-right  text-xs font-medium text-slate-600 tracking-widest uppercase">Updated</th>
          </tr>
        </thead>
        <tbody>
          {tickers.map(t => {
            const sym   = t.symbol;
            const row   = rows[sym];
            const price = row?.price ?? t.latest_price;
            const open0 = row?.open0;
            const flash = row?.flash;

            let pctTxt = '—';
            let pctColor = 'text-slate-500';
            if (price != null && open0 != null) {
              const pct = ((price - open0) / open0) * 100;
              pctTxt = (pct >= 0 ? '+' : '') + pct.toFixed(2) + '%';
              pctColor = pct > 0 ? 'text-emerald-400' : pct < 0 ? 'text-red-400' : 'text-slate-400';
            }

            const priceColor =
              flash === 'up'   ? 'text-emerald-400' :
              flash === 'down' ? 'text-red-400'     : 'text-slate-200';

            const isSelected = selected === sym;

            return (
              <tr
                key={sym}
                onClick={() => onSelect(sym)}
                className={[
                  'border-b border-slate-900/60 cursor-pointer transition-colors duration-100',
                  flash === 'up'   ? 'flash-up'   : '',
                  flash === 'down' ? 'flash-down' : '',
                  isSelected ? 'bg-slate-900/80' : 'hover:bg-slate-900/40',
                ].join(' ')}
              >
                <td className="px-4 py-3 text-sky-300 font-bold">{sym}</td>
                <td className={`px-4 py-3 text-right font-semibold tabular-nums ${priceColor}`}>
                  {fmt(price, 4)}
                </td>
                <td className={`px-4 py-3 text-right tabular-nums ${pctColor}`}>{pctTxt}</td>
                <td className="px-4 py-3 text-right text-slate-500 text-xs tabular-nums">
                  {fmtTime(t.last_updated)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>

      {error && (
        <div className="flex-1 flex items-center justify-center text-slate-700 text-xs p-8 text-center">
          API unreachable — is the server running on localhost:8000?
        </div>
      )}

      {!error && tickers.length === 0 && (
        <div className="flex-1 flex items-center justify-center text-slate-700 text-xs">
          Connecting…
        </div>
      )}
    </div>
  );
}
