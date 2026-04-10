import { useState } from 'react';
import Header from './components/Header';
import PriceBoard from './components/PriceBoard';
import HistoryPanel from './components/HistoryPanel';

export default function App() {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className="flex flex-col h-screen bg-[#070d1a] text-slate-200">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <PriceBoard selected={selected} onSelect={setSelected} />
        {selected && <HistoryPanel symbol={selected} />}
      </div>
    </div>
  );
}
