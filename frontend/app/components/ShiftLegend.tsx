// ShiftLegend component for displaying shift symbol legend

export function ShiftLegend() {
  const legendItems = [
    { symbol: '早', label: '早番', style: 'bg-amber-200 text-amber-900' },
    { symbol: '日', label: '日勤', style: 'bg-slate-300 text-slate-900' },
    { symbol: '遅', label: '遅番', style: 'bg-orange-200 text-orange-900' },
    { symbol: '夜', label: '夜勤', style: 'bg-indigo-300 text-indigo-900' },
    { symbol: '・', label: '明け', style: 'bg-violet-200 text-violet-900' },
    { symbol: '◎', label: '公休', style: 'bg-emerald-200 text-emerald-900' },
    { symbol: '◎', label: '希望休', style: 'bg-cyan-200 text-cyan-900' },
    { symbol: '有', label: '有休', style: 'bg-pink-200 text-pink-900' },
    { symbol: 'リ休', label: 'リ休', style: 'bg-amber-300 text-amber-900' },
  ];

  return (
    <div className="card rounded-xl p-4">
      <h3 className="text-sm font-bold text-slate-700 mb-3">凡例</h3>
      <div className="flex flex-wrap gap-3">
        {legendItems.map((item, idx) => (
          <div key={`${item.label}-${idx}`} className="flex items-center gap-1.5">
            <span className={`px-2.5 py-1 rounded font-black text-sm ${item.style}`}>
              {item.symbol}
            </span>
            <span className="text-xs text-slate-600 font-medium">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
