// ShiftLegend component for displaying shift symbol meanings

export function ShiftLegend() {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 border-2 border-indigo-100">
      <h3 className="font-bold text-slate-800 mb-4">📋 シフト記号の意味</h3>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { symbol: '早', label: '早番', style: 'bg-gradient-to-br from-yellow-200 to-yellow-300 text-yellow-900' },
          { symbol: '日', label: '日勤', style: 'bg-gray-100 text-gray-800' },
          { symbol: '遅', label: '遅番', style: 'bg-gradient-to-br from-orange-200 to-orange-300 text-orange-900' },
          { symbol: '夜', label: '夜勤', style: 'bg-gradient-to-br from-indigo-400 to-purple-400 text-indigo-900' },
          { symbol: '・', label: '明け', style: 'bg-indigo-100 text-indigo-800' },
          { symbol: '◎', label: '公休', style: 'bg-green-200 text-green-900' },
          { symbol: '◎ ', label: '希望休', style: 'bg-gradient-to-br from-cyan-200 to-teal-200 text-cyan-900' },
          { symbol: '有', label: '有休', style: 'bg-gradient-to-br from-pink-200 to-pink-300 text-pink-900' },
          { symbol: 'リ休', label: 'リ休', style: 'bg-gradient-to-br from-amber-200 to-orange-200 text-amber-900' },
        ].map((item, idx) => (
          <div key={`${item.label}-${idx}`} className="flex items-center gap-2">
            <span className={`px-3 py-1.5 rounded font-semibold ${item.style}`}>
              {item.symbol.trim() || '◎'}
            </span>
            <span className="text-sm text-slate-700">{item.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}




