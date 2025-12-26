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
    <div className="lg:col-span-1 space-y-6">
      {/* シフト設定 */}
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
                onChange={(e) => {/* handled by parent */}}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                readOnly
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">月</label>
              <input
                type="number"
                min="1"
                max="12"
                value={month}
                onChange={(e) => {/* handled by parent */}}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                readOnly
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
              onChange={(e) => {/* handled by parent */}}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              readOnly
            />
          </div>
        </div>
      </div>

      {/* スタッフ管理 */}
      <div className="bg-white rounded-2xl shadow-xl p-6 border-2 border-indigo-100">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-xl font-bold text-indigo-900 flex items-center gap-2">
            <span className="text-2xl">👥</span>
            スタッフ管理
            <span className="text-sm font-normal text-slate-500">
              ({staffList.length}名)
            </span>
          </h2>
          <button
            onClick={onAddStaff}
            className="px-5 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all font-semibold text-sm shadow-lg hover:shadow-xl transform hover:scale-105"
          >
            + 追加
          </button>
        </div>

        <div className="space-y-2 max-h-64 overflow-y-auto">
          {staffList.map((staff, index) => (
            <div
              key={index}
              className={`p-3 rounded-lg border-2 cursor-pointer transition-all ${
                selectedStaffIndex === index
                  ? 'border-indigo-500 bg-indigo-50'
                  : 'border-slate-200 bg-slate-50 hover:border-slate-300'
              }`}
              onClick={() => onSelectStaff(index)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-lg">
                    {STAFF_TYPES.find(t => t.value === staff.type)?.icon || '🔵'}
                  </span>
                  <span className="font-medium text-slate-800">{staff.name}</span>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onRemoveStaff(index);
                  }}
                  className="text-red-500 hover:text-red-700 text-sm px-2 py-1"
                >
                  削除
                </button>
              </div>
            </div>
          ))}
          {staffList.length === 0 && (
            <p className="text-sm text-slate-500 text-center py-4">
              スタッフを追加してください
            </p>
          )}
        </div>
      </div>

      {/* 選択中のスタッフの詳細設定 */}
      {selectedStaffIndex !== null && staffList[selectedStaffIndex] && (
        <div className="bg-white rounded-2xl shadow-xl p-6 border-2 border-indigo-100">
          <h2 className="text-xl font-bold text-indigo-900 mb-5 flex items-center gap-2">
            <span className="text-2xl">👤</span>
            個人設定
          </h2>
          {(() => {
            const staff = staffList[selectedStaffIndex];
            return (
              <>
                <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">名前</label>
                    <input
                      type="text"
                      value={staff.name}
                      onChange={(e) => onUpdateStaff(selectedStaffIndex, { name: e.target.value })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-1">属性</label>
                    <select
                      value={staff.type}
                      onChange={(e) => onUpdateStaff(selectedStaffIndex, { type: Number(e.target.value) })}
                      className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                    >
                      {STAFF_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.icon} {type.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">前月末シフト</label>
                      <select
                        value={staff.prev_shift}
                        onChange={(e) => onUpdateStaff(selectedStaffIndex, { prev_shift: e.target.value })}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      >
                        {SHIFT_OPTIONS.map((opt) => (
                          <option key={opt} value={opt}>{opt}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">連勤日数</label>
                      <input
                        type="number"
                        min="0"
                        max="10"
                        value={staff.prev_streak}
                        onChange={(e) => onUpdateStaff(selectedStaffIndex, { prev_streak: Number(e.target.value) })}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  </div>

                  {staff.type === 0 && (
                    <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">
                        🌙 夜勤目標回数
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="10"
                        value={staff.night_target}
                        onChange={(e) => onUpdateStaff(selectedStaffIndex, { night_target: Number(e.target.value) })}
                        className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                      />
                    </div>
                  )}

                  <div className="border-t-2 border-indigo-100 pt-5">
                    <label className="block text-sm font-medium text-indigo-900 mb-3">希望シフト</label>
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

                  <div className="border-t-2 border-indigo-100 pt-5">
                    <label className="block text-sm font-medium text-indigo-900 mb-3">休暇設定</label>
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

                {/* 決定ボタン - スクロール領域の外 */}
                <div className="border-t-2 border-indigo-100 pt-5 mt-4">
                  <button
                    onClick={() => onSelectStaff(null)}
                    className="w-full px-6 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all font-bold shadow-lg hover:shadow-xl transform hover:scale-105"
                  >
                    ✓ 決定
                  </button>
                </div>
              </>
            );
          })()}
        </div>
      )}
    </div>
  );
}




