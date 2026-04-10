import { useEffect, useState } from 'react';
import { fetchHealth, type HealthData } from '../api';

function Dot({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span className="flex items-center gap-1.5 text-xs">
      <span
        className="inline-block w-2 h-2 rounded-full"
        style={{ background: ok ? '#22c55e' : '#ef4444', boxShadow: ok ? '0 0 6px #22c55e88' : '0 0 6px #ef444488' }}
      />
      <span className="text-slate-400">{label}</span>
    </span>
  );
}

function Clock() {
  const [time, setTime] = useState('');
  useEffect(() => {
    const tick = () => {
      const n = new Date();
      const p = (x: number) => String(x).padStart(2, '0');
      setTime(`${p(n.getUTCHours())}:${p(n.getUTCMinutes())}:${p(n.getUTCSeconds())} UTC`);
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);
  return <span className="text-slate-600 text-xs tabular-nums">{time}</span>;
}

function fmtUptime(s: number): string {
  if (s < 60)   return `${~~s}s`;
  if (s < 3600) return `${~~(s / 60)}m ${~~(s % 60)}s`;
  return `${~~(s / 3600)}h ${~~((s % 3600) / 60)}m`;
}

export default function Header() {
  const [health, setHealth] = useState<HealthData | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => {});
    const id = setInterval(() => fetchHealth().then(setHealth).catch(() => {}), 5000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="flex items-center justify-between px-5 h-11 border-b border-slate-900 bg-[#070d1a] flex-shrink-0 z-10">
      {/* Logo */}
      <div className="flex items-center gap-2.5">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" strokeWidth="2.5">
          <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
          <polyline points="16 7 22 7 22 13" />
        </svg>
        <span className="text-cyan-400 font-bold text-sm tracking-widest">MARKET FEED</span>
      </div>

      {/* Right: health + clock */}
      <div className="flex items-center gap-5">
        <Dot ok={health?.feed_connected  ?? false} label="Feed"  />
        <Dot ok={health?.db_connected    ?? false} label="DB"    />
        <Dot ok={health?.redis_connected ?? false} label="Redis" />
        {health && (
          <span className="text-slate-700 text-xs">{fmtUptime(health.uptime_seconds)} uptime</span>
        )}
        <Clock />
      </div>
    </header>
  );
}
