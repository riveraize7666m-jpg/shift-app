// ShiftLegend component for displaying shift symbol meanings

export function ShiftLegend() {
  const legendItems = [
    { symbol: '早', label: '早番', bgClass: 'bg-amber-100', textClass: 'text-amber-700' },
    { symbol: '日', label: '日勤', bgClass: 'bg-slate-200', textClass: 'text-slate-700' },
    { symbol: '遅', label: '遅番', bgClass: 'bg-orange-100', textClass: 'text-orange-700' },
    { symbol: '夜', label: '夜勤', bgClass: 'bg-indigo-200', textClass: 'text-indigo-800' },
    { symbol: '・', label: '明け', bgClass: 'bg-violet-100', textClass: 'text-violet-700' },
    { symbol: '◎', label: '公休', bgClass: 'bg-emerald-100', textClass: 'text-emerald-700' },
    { symbol: '◎ ', label: '希望休', bgClass: 'bg-cyan-100', textClass: 'text-cyan-700' },
    { symbol: '有', label: '有休', bgClass: 'bg-pink-100', textClass: 'text-pink-700' },
    { symbol: 'リ休', label: 'リ休', bgClass: 'bg-amber-200', textClass: 'text-amber-800' },
  ];

  return (
    <div className="card rounded-xl p-5">
      <h3 className="font-bold text-slate-700 mb-3 text-sm">📋 シフト記号の意味</h3>
      <div className="grid grid-cols-3 md:grid-cols-5 gap-2">
        {legendItems.map((item, idx) => (
          <div 
            key={`${item.label}-${idx}`} 
            className="flex items-center gap-2 bg-slate-50 rounded-lg p-2"
          >
            <span className={`px-2 py-1 rounded text-xs font-bold ${item.bgClass} ${item.textClass}`}>
              {item.symbol.trim() || '◎'}
            </span>
            <span className="text-xs text-slate-600">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
