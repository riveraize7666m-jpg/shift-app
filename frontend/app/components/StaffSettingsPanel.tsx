// StaffSettingsPanel component for staff management and settings

import { StaffData } from '../types';
import { SHIFT_OPTIONS, STAFF_TYPES } from '../constants';
import { DateSelectorField } from './DateSelectorField';

interface StaffSettingsPanelProps {
  year: number;
  month: number;
  targetOffDays: number;
  staffList: StaffData[];
  selectedStaffIndex: number | null;
  onSelectStaff: (index: number | null) => void;
  onUpdateStaff: (index: number, updates: Partial<StaffData>) => void;
  onAddStaff: () => void;
  onRemoveStaff: (index: number) => void;
  openCalendar: { field: string; staffIndex: number } | null;
  onOpenCalendar: (field: string, staffIndex: number) => void;
  onCloseCalendar: () => void;
}

export function StaffSettingsPanel({
  year,
  month,
  targetOffDays,
  staffList,
  selectedStaffIndex,
  onSelectStaff,
  onUpdateStaff,
  onAddStaff,
  onRemoveStaff,
  openCalendar,
  onOpenCalendar,
  onCloseCalendar,
}: StaffSettingsPanelProps) {
  return (
    <>
      {/* スタッフ管理 */}
      <div className="card rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-cyan-100 flex items-center justify-center text-cyan-600">
              👥
            </span>
            スタッフ管理
            <span className="text-sm font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
              {staffList.length}名
            </span>
          </h2>
          <button
            onClick={onAddStaff}
            className="px-4 py-2 btn-primary rounded-lg text-sm font-semibold"
          >
            + 追加
          </button>
        </div>

        <div className="space-y-2 max-h-60 overflow-y-auto">
          {staffList.map((staff, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg cursor-pointer transition-all ${
                selectedStaffIndex === index
                  ? 'bg-indigo-50 border-2 border-indigo-300'
                  : 'bg-slate-50 border-2 border-transparent hover:bg-slate-100'
              }`}
              onClick={() => onSelectStaff(index)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">
                    {STAFF_TYPES.find(t => t.value === staff.type)?.icon || '🔵'}
                  </span>
                  <span className="font-medium text-slate-700">{staff.name}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveStaff(index);
                  }}
                  className="text-red-500 hover:text-red-600 text-sm px-2 py-1 rounded hover:bg-red-50 transition-colors"
                >
                  削除
                </button>
              </div>
            </div>
          ))}
          {staffList.length === 0 && (
            <div className="text-center py-6">
              <div className="w-12 h-12 mx-auto mb-3 rounded-xl bg-slate-100 flex items-center justify-center">
                <span className="text-2xl opacity-40">👤</span>
              </div>
              <p className="text-sm text-slate-400">
                スタッフを追加してください
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 選択中のスタッフの詳細設定 */}
      {selectedStaffIndex !== null && staffList[selectedStaffIndex] && (
        <div className="card rounded-xl p-5">
          <h2 className="text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
            <span className="w-8 h-8 rounded-lg bg-purple-100 flex items-center justify-center text-purple-600">
              👤
            </span>
            個人設定
          </h2>
          {(() => {
            const staff = staffList[selectedStaffIndex];
            return (
              <>
                <div className="space-y-4 max-h-[380px] overflow-y-auto pr-1">
                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">名前</label>
                    <input
                      type="text"
                      value={staff.name}
                      onChange={(e) => onUpdateStaff(selectedStaffIndex, { name: e.target.value })}
                      className="w-full px-3 py-2.5 input-field rounded-lg text-sm"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-600 mb-1.5">属性</label>
                    <select
                      value={staff.type}
                      onChange={(e) => onUpdateStaff(selectedStaffIndex, { type: Number(e.target.value) })}
                      className="w-full px-3 py-2.5 input-field rounded-lg text-sm"
                    >
                      {STAFF_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.icon} {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-slate-600 mb-1.5">前月末シフト</label>
                      <select
                        value={staff.prev_shift}
                        onChange={(e) => onUpdateStaff(selectedStaffIndex, { prev_shift: e.target.value })}
                        className="w-full px-3 py-2.5 input-field rounded-lg text-sm"
                      >
                        {SHIFT_OPTIONS.map((opt) => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-600 mb-1.5">連勤日数</label>
                      <input
                        type="number"
                        min="0"
                        max="10"
                        value={staff.prev_streak}
                        onChange={(e) => onUpdateStaff(selectedStaffIndex, { prev_streak: Number(e.target.value) })}
                        className="w-full px-3 py-2.5 input-field rounded-lg text-sm"
                      />
                    </div>
                  </div>

                  {staff.type === 0 && (
                    <div>
                      <label className="block text-sm font-medium text-slate-600 mb-1.5">
                        🌙 夜勤目標回数
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="10"
                        value={staff.night_target}
                        onChange={(e) => onUpdateStaff(selectedStaffIndex, { night_target: Number(e.target.value) })}
                        className="w-full px-3 py-2.5 input-field rounded-lg text-sm"
                      />
                    </div>
                  )}

                  <div className="border-t border-slate-200 pt-4">
                    <label className="block text-sm font-semibold text-indigo-600 mb-3">希望シフト</label>
                    <div className="grid grid-cols-2 gap-3">
                      <DateSelectorField
                        label="夜勤希望"
                        field="req_night"
                        staffIndex={selectedStaffIndex}
                        selectedDays={staff.req_night}
                        onUpdate={(days) => onUpdateStaff(selectedStaffIndex, { req_night: days })}
                        year={year}
                        month={month}
                        isOpen={openCalendar?.field === 'req_night' && openCalendar?.staffIndex === selectedStaffIndex}
                        onOpen={() => onOpenCalendar('req_night', selectedStaffIndex)}
                        onClose={onCloseCalendar}
                      />
                      <DateSelectorField
                        label="早番希望"
                        field="req_early"
                        staffIndex={selectedStaffIndex}
                        selectedDays={staff.req_early}
                        onUpdate={(days) => onUpdateStaff(selectedStaffIndex, { req_early: days })}
                        year={year}
                        month={month}
                        isOpen={openCalendar?.field === 'req_early' && openCalendar?.staffIndex === selectedStaffIndex}
                        onOpen={() => onOpenCalendar('req_early', selectedStaffIndex)}
                        onClose={onCloseCalendar}
                      />
                      <DateSelectorField
                        label="遅番希望"
                        field="req_late"
                        staffIndex={selectedStaffIndex}
                        selectedDays={staff.req_late}
                        onUpdate={(days) => onUpdateStaff(selectedStaffIndex, { req_late: days })}
                        year={year}
                        month={month}
                        isOpen={openCalendar?.field === 'req_late' && openCalendar?.staffIndex === selectedStaffIndex}
                        onOpen={() => onOpenCalendar('req_late', selectedStaffIndex)}
                        onClose={onCloseCalendar}
                      />
                      <DateSelectorField
                        label="日勤希望"
                        field="req_day"
                        staffIndex={selectedStaffIndex}
                        selectedDays={staff.req_day}
                        onUpdate={(days) => onUpdateStaff(selectedStaffIndex, { req_day: days })}
                        year={year}
                        month={month}
                        isOpen={openCalendar?.field === 'req_day' && openCalendar?.staffIndex === selectedStaffIndex}
                        onOpen={() => onOpenCalendar('req_day', selectedStaffIndex)}
                        onClose={onCloseCalendar}
                      />
                    </div>
                  </div>

                  <div className="border-t border-slate-200 pt-4">
                    <label className="block text-sm font-semibold text-cyan-600 mb-3">休暇設定</label>
                    <div className="grid grid-cols-2 gap-3">
                      <DateSelectorField
                        label="希望休"
                        field="req_off"
                        staffIndex={selectedStaffIndex}
                        selectedDays={staff.req_off}
                        onUpdate={(days) => onUpdateStaff(selectedStaffIndex, { req_off: days })}
                        year={year}
                        month={month}
                        isOpen={openCalendar?.field === 'req_off' && openCalendar?.staffIndex === selectedStaffIndex}
                        onOpen={() => onOpenCalendar('req_off', selectedStaffIndex)}
                        onClose={onCloseCalendar}
                      />
                      <DateSelectorField
                        label="有休"
                        field="paid_leave_days"
                        staffIndex={selectedStaffIndex}
                        selectedDays={staff.paid_leave_days}
                        onUpdate={(days) => onUpdateStaff(selectedStaffIndex, { paid_leave_days: days })}
                        year={year}
                        month={month}
                        isOpen={openCalendar?.field === 'paid_leave_days' && openCalendar?.staffIndex === selectedStaffIndex}
                        onOpen={() => onOpenCalendar('paid_leave_days', selectedStaffIndex)}
                        onClose={onCloseCalendar}
                      />
                      <DateSelectorField
                        label="出勤希望"
                        field="req_work"
                        staffIndex={selectedStaffIndex}
                        selectedDays={staff.req_work}
                        onUpdate={(days) => onUpdateStaff(selectedStaffIndex, { req_work: days })}
                        year={year}
                        month={month}
                        isOpen={openCalendar?.field === 'req_work' && openCalendar?.staffIndex === selectedStaffIndex}
                        onOpen={() => onOpenCalendar('req_work', selectedStaffIndex)}
                        onClose={onCloseCalendar}
                      />
                      <DateSelectorField
                        label="リ休"
                        field="refresh_days"
                        staffIndex={selectedStaffIndex}
                        selectedDays={staff.refresh_days}
                        onUpdate={(days) => onUpdateStaff(selectedStaffIndex, { refresh_days: days })}
                        year={year}
                        month={month}
                        isOpen={openCalendar?.field === 'refresh_days' && openCalendar?.staffIndex === selectedStaffIndex}
                        onOpen={() => onOpenCalendar('refresh_days', selectedStaffIndex)}
                        onClose={onCloseCalendar}
                      />
                    </div>
                  </div>
                </div>

                {/* 決定ボタン */}
                <div className="border-t border-slate-200 pt-4 mt-4">
                  <button
                    onClick={() => onSelectStaff(null)}
                    className="w-full px-4 py-2.5 bg-emerald-500 text-white rounded-lg font-semibold hover:bg-emerald-600 transition-colors"
                  >
                    ✓ 決定
                  </button>
                </div>
              </>
            );
          })()}
        </div>
      )}
    </>
  );
}
