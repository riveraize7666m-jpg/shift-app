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
        className="fixed inset-0 bg-black/30 z-40"
        onClick={onClose}
      />
      {/* カレンダー本体 */}
      <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-white rounded-xl p-5 w-[280px] shadow-2xl border border-slate-200">
        <div className="flex items-center justify-between mb-4">
          <div className="font-bold text-slate-800 text-lg flex items-center gap-2">
            <span className="text-indigo-500">📅</span>
            {year}年{month}月
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 text-xl w-8 h-8 flex items-center justify-center rounded-lg hover:bg-slate-100 transition-colors"
          >
            ×
          </button>
        </div>
        <div className="grid grid-cols-7 gap-1 mb-2">
          {weekdays.map((day, idx) => (
            <div 
              key={day} 
              className={`text-center text-xs font-semibold py-1.5 ${
                idx === 0 ? 'text-red-500' : idx === 6 ? 'text-blue-500' : 'text-slate-500'
              }`}
            >
              {day}
            </div>
          ))}
        </div>
        <div className="grid grid-cols-7 gap-1">
          {days.map((day, idx) => {
            const dayOfWeek = idx % 7;
            const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
            const isSelected = day && selectedDays.includes(day);
            
            return (
              <button
                key={idx}
                onClick={() => day && toggleDay(day)}
                disabled={!day}
                className={`
                  aspect-square text-sm rounded-lg transition-all font-medium flex items-center justify-center
                  ${!day ? 'cursor-default' : 'cursor-pointer'}
                  ${isSelected
                    ? 'bg-indigo-500 text-white'
                    : day
                      ? `${isWeekend ? 'text-slate-500' : 'text-slate-700'} hover:bg-slate-100`
                      : ''
                  }
                `}
              >
                {day || ''}
              </button>
            );
          })}
        </div>
        <div className="mt-4 pt-4 border-t border-slate-200">
          <div className="text-xs text-slate-500 mb-3 flex items-center gap-2">
            <span className="text-indigo-500 font-medium">選択中:</span>
            <span className="text-slate-700">
              {selectedDays.length > 0 ? selectedDays.join(', ') + '日' : 'なし'}
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onSelect([])}
              className="flex-1 px-4 py-2 text-sm btn-secondary rounded-lg font-medium"
            >
              クリア
            </button>
            <button
              onClick={onClose}
              className="flex-1 px-4 py-2 text-sm btn-primary rounded-lg font-semibold"
            >
              決定
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
