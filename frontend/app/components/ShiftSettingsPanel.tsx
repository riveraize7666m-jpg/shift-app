// ShiftSettingsPanel component for basic shift configuration

interface ShiftSettingsPanelProps {
  year: number;
  month: number;
  targetOffDays: number;
  onYearChange: (year: number) => void;
  onMonthChange: (month: number) => void;
  onTargetOffDaysChange: (days: number) => void;
}

export function ShiftSettingsPanel({
  year,
  month,
  targetOffDays,
  onYearChange,
  onMonthChange,
  onTargetOffDaysChange,
}: ShiftSettingsPanelProps) {
  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 border-2 border-indigo-100">
      <h2 className="text-xl font-bold text-indigo-900 mb-5 flex items-center gap-2">
        <span className="text-2xl">📅</span>
        シフト設定
      </h2>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">年</label>
            <input
              type="number"
              min="2025"
              max="2030"
              value={year}
              onChange={(e) => onYearChange(Number(e.target.value))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">月</label>
            <input
              type="number"
              min="1"
              max="12"
              value={month}
              onChange={(e) => onMonthChange(Number(e.target.value))}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">
            常勤の公休数
          </label>
          <input
            type="number"
            min="1"
            max="15"
            value={targetOffDays}
            onChange={(e) => onTargetOffDaysChange(Number(e.target.value))}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
        </div>
      </div>
    </div>
  );
}




