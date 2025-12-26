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
      <label className="block text-xs text-slate-500 mb-1">{label}</label>
      <div className="flex gap-1">
        <input
          type="text"
          readOnly
          value={selectedDays.length > 0 ? selectedDays.join(',') : ''}
          placeholder="選択..."
          className="flex-1 px-2.5 py-2 text-sm input-field rounded-lg cursor-pointer"
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
          className="px-2.5 py-2 bg-indigo-50 text-indigo-600 rounded-lg hover:bg-indigo-100 transition-colors text-sm font-medium"
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
