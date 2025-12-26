// DateSelectorField component for date input with calendar

import { MiniCalendar } from './MiniCalendar';

interface DateSelectorFieldProps {
  label: string;
  field: string;
  staffIndex: number;
  selectedDays: number[];
  onUpdate: (days: number[]) => void;
  year: number;
  month: number;
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
}

export function DateSelectorField({
  label,
  field,
  staffIndex,
  selectedDays,
  onUpdate,
  year,
  month,
  isOpen,
  onOpen,
  onClose,
}: DateSelectorFieldProps) {
  return (
    <div className="relative date-selector-container">
      <label className="block text-xs text-slate-600 mb-1">{label}</label>
      <div className="flex gap-1">
        <input
          type="text"
          readOnly
          value={selectedDays.length > 0 ? selectedDays.join(',') : ''}
          placeholder="カレンダーから選択"
          className="flex-1 px-2 py-1.5 text-sm border border-slate-300 rounded focus:ring-2 focus:ring-indigo-500 focus:border-transparent bg-white cursor-pointer"
          onClick={(e) => {
            e.stopPropagation();
            onOpen();
          }}
        />
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            isOpen ? onClose() : onOpen();
          }}
          className="px-3 py-1.5 bg-indigo-100 text-indigo-700 rounded hover:bg-indigo-200 transition-colors text-sm font-semibold"
        >
          📅
        </button>
      </div>
      {isOpen && (
        <div onClick={(e) => e.stopPropagation()}>
          <MiniCalendar
            year={year}
            month={month}
            selectedDays={selectedDays}
            onSelect={onUpdate}
            onClose={onClose}
          />
        </div>
      )}
    </div>
  );
}




