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
    <div className="card rounded-xl p-5">
      <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
        <span className="w-8 h-8 rounded-lg bg-indigo-100 flex items-center justify-center text-indigo-600">
          📅
        </span>
        シフト設定
      </h2>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">年</label>
            <input
              type="number"
              min="2025"
              max="2030"
              value={year}
              onChange={(e) => onYearChange(Number(e.target.value))}
              className="w-full px-3 py-2.5 input-field rounded-lg text-sm"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-600 mb-1.5">月</label>
            <input
              type="number"
              min="1"
              max="12"
              value={month}
              onChange={(e) => onMonthChange(Number(e.target.value))}
              className="w-full px-3 py-2.5 input-field rounded-lg text-sm"
            />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-600 mb-1.5">
            常勤の公休数
          </label>
          <input
            type="number"
            min="1"
            max="15"
            value={targetOffDays}
            onChange={(e) => onTargetOffDaysChange(Number(e.target.value))}
            className="w-full px-3 py-2.5 input-field rounded-lg text-sm"
          />
        </div>
      </div>
    </div>
  );
}
