// MiniCalendar component for date selection

interface MiniCalendarProps {
  year: number;
  month: number;
  selectedDays: number[];
  onSelect: (days: number[]) => void;
  onClose: () => void;
}

export function MiniCalendar({ year, month, selectedDays, onSelect, onClose }: MiniCalendarProps) {
  const getDaysInMonth = (year: number, month: number) => {
    return new Date(year, month, 0).getDate();
  };

  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = new Date(year, month - 1, 1).getDay();
  const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
  const days: (number | null)[] = Array(firstDay).fill(null);
  for (let i = 1; i <= daysInMonth; i++) {
    days.push(i);
  }

  const toggleDay = (day: number) => {
    if (selectedDays.includes(day)) {
      onSelect(selectedDays.filter(d => d !== day));
    } else {
      onSelect([...selectedDays, day].sort((a, b) => a - b));
    }
  };

  return (
    <>
      {/* オーバーレイ */}
      <div 
        className="fixed inset-0 bg-black/20 z-40"
        onClick={onClose}
      />
      {/* カレンダー本体 - 固定位置で中央表示 */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-white rounded-xl shadow-2xl border-2 border-indigo-200 p-3 w-[240px]">
        <div className="flex items-center justify-between mb-2">
          <div className="font-bold text-indigo-900 text-sm">
            {year}年{month}月
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-700 text-lg leading-none w-6 h-6 flex items-center justify-center"
          >
            ×
          </button>
        </div>
        <div className="grid grid-cols-7 gap-0.5 mb-1.5">
          {weekdays.map(day => (
            <div key={day} className="text-center text-[10px] font-semibold text-slate-600 py-0.5">
              {day}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-0.5">
          {days.map((day, idx) => (
            <button
              key={idx}
              onClick={() => day && toggleDay(day)}
              disabled={!day}
              className={`
                aspect-square text-xs rounded transition-all min-w-[28px] h-[28px] flex items-center justify-center
                ${!day ? 'cursor-default' : 'cursor-pointer hover:bg-indigo-50'}
                ${day && selectedDays.includes(day)
                  ? 'bg-indigo-600 text-white font-bold'
                  : day
                    ? 'text-slate-700 hover:bg-indigo-50'
                    : ''
                }
              `}
            >
              {day || ''}
            </button>
          ))}
        </div>
        <div className="mt-2 pt-2 border-t border-slate-200">
          <div className="text-[10px] text-slate-600 mb-1.5">
            選択: {selectedDays.length > 0 ? selectedDays.join(', ') : 'なし'}
          </div>
          <div className="flex gap-1.5">
            <button
              onClick={() => onSelect([])}
              className="flex-1 px-2 py-1 text-xs bg-slate-100 text-slate-700 rounded-lg hover:bg-slate-200 transition-colors"
            >
              クリア
            </button>
            <button
              onClick={onClose}
              className="flex-1 px-2 py-1 text-xs bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold"
            >
              決定
            </button>
          </div>
        </div>
      </div>
    </>
  );
}




