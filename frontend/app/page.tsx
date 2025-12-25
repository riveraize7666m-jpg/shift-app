'use client';

import { useState } from 'react';
import { StaffData, ShiftResponse } from './types';
import { createShift } from './utils/api';
import { validateSchedule } from './utils/validation';
import { ShiftSettingsPanel } from './components/ShiftSettingsPanel';
import { StaffSettingsPanel } from './components/StaffSettingsPanel';
import { FileSettingsPanel } from './components/FileSettingsPanel';
import { ShiftTable } from './components/ShiftTable';
import { ShiftLegend } from './components/ShiftLegend';
import { ValidationWarnings } from './components/ValidationWarnings';
import { CSVDownloadButton } from './components/CSVDownloadButton';

export default function Home() {
  const [year, setYear] = useState(2026);
  const [month, setMonth] = useState(2);
  const [targetOffDays, setTargetOffDays] = useState(9);
  const [staffList, setStaffList] = useState<StaffData[]>([]);
  const [selectedStaffIndex, setSelectedStaffIndex] = useState<number | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [result, setResult] = useState<ShiftResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openCalendar, setOpenCalendar] = useState<{ field: string; staffIndex: number } | null>(null);

  const addStaff = () => {
    const newStaff: StaffData = {
      name: `スタッフ${staffList.length + 1}`,
      type: 0,
      night_target: 4,
      req_night: [],
      req_early: [],
      req_late: [],
      req_day: [],
      req_off: [],
      req_work: [],
      refresh_days: [],
      paid_leave_days: [],
      prev_shift: "◎",
      prev_streak: 0,
      fixed_shifts: ["", "", ""],
    };
    setStaffList([...staffList, newStaff]);
    setSelectedStaffIndex(staffList.length);
  };

  const removeStaff = (index: number) => {
    const newList = staffList.filter((_, i) => i !== index);
    setStaffList(newList);
    if (selectedStaffIndex === index) {
      setSelectedStaffIndex(null);
    } else if (selectedStaffIndex !== null && selectedStaffIndex > index) {
      setSelectedStaffIndex(selectedStaffIndex - 1);
    }
  };

  const updateStaff = (index: number, updates: Partial<StaffData>) => {
    const newList = [...staffList];
    newList[index] = { ...newList[index], ...updates };
    setStaffList(newList);
  };

  const handleCreateShift = async () => {
    if (staffList.length === 0) {
      setError('スタッフを追加してください');
      return;
    }

    setIsCreating(true);
    setError(null);
    setResult(null);

    try {
      const response = await createShift({
        year,
        month,
        target_off_days: targetOffDays,
        staff_data: staffList,
        max_attempts: 2500,
      });
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'シフトの作成に失敗しました');
    } finally {
      setIsCreating(false);
    }
  };

  const handleOpenCalendar = (field: string, staffIndex: number) => {
    setOpenCalendar({ field, staffIndex });
  };

  const handleCloseCalendar = () => {
    setOpenCalendar(null);
  };

  const getValidationWarnings = () => {
    if (!result) return [];
    return validateSchedule(result, staffList, targetOffDays);
  };

  return (
    <div 
      className="min-h-screen overflow-x-hidden"
      onClick={(e) => {
        if (!(e.target as HTMLElement).closest('.date-selector-container')) {
          setOpenCalendar(null);
        }
      }}
    >
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-10">
          <div className="card rounded-2xl p-8 accent-top-border">
            <div className="flex items-center gap-4 mb-2">
              <div className="w-12 h-12 rounded-xl bg-indigo-600 flex items-center justify-center">
                <span className="text-2xl text-white">✦</span>
              </div>
              <h1 className="text-4xl font-bold text-slate-800 tracking-tight">
                Shift Manager Pro
              </h1>
            </div>
            <p className="text-slate-500 text-base ml-16">
              最適なシフトを、ワンクリックで。
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Settings */}
          <div className="lg:col-span-1 space-y-5">
            <ShiftSettingsPanel
              year={year}
              month={month}
              targetOffDays={targetOffDays}
              onYearChange={setYear}
              onMonthChange={setMonth}
              onTargetOffDaysChange={setTargetOffDays}
            />

            <StaffSettingsPanel
              year={year}
              month={month}
              targetOffDays={targetOffDays}
              staffList={staffList}
              selectedStaffIndex={selectedStaffIndex}
              onSelectStaff={setSelectedStaffIndex}
              onUpdateStaff={updateStaff}
              onAddStaff={addStaff}
              onRemoveStaff={removeStaff}
              openCalendar={openCalendar}
              onOpenCalendar={handleOpenCalendar}
              onCloseCalendar={handleCloseCalendar}
            />

            <FileSettingsPanel
              year={year}
              month={month}
              targetOffDays={targetOffDays}
              staffList={staffList}
              onYearChange={setYear}
              onMonthChange={setMonth}
              onTargetOffDaysChange={setTargetOffDays}
              onStaffListChange={setStaffList}
            />

            {/* シフト作成ボタン */}
            <button
              onClick={handleCreateShift}
              disabled={isCreating || staffList.length === 0}
              className="w-full px-6 py-4 btn-primary rounded-xl font-bold text-lg disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {isCreating ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin">⏳</span>
                  シフト作成中...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <span>🚀</span>
                  シフトを作成
                </span>
              )}
            </button>
          </div>

          {/* Main Content - Results */}
          <div className="lg:col-span-2">
            {error && (
              <div className="card rounded-xl p-5 mb-5 border-l-4 border-l-red-500 bg-red-50">
                <div className="flex items-center gap-3">
                  <span className="text-xl">⚠️</span>
                  <p className="text-red-700 font-medium">{error}</p>
                </div>
              </div>
            )}

            {result && (
              <div className="space-y-5">
                {/* 成功メッセージ */}
                <div className="card rounded-xl p-6 border-l-4 border-l-emerald-500 bg-emerald-50">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-emerald-500 flex items-center justify-center">
                      <span className="text-2xl">🎉</span>
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-slate-800">
                        シフト案を作成しました
                      </h2>
                      <p className="text-emerald-600 font-medium">
                        {result.year}年{result.month}月
                      </p>
                    </div>
                  </div>
                </div>

                {/* バリデーション警告 */}
                <ValidationWarnings 
                  warnings={getValidationWarnings()}
                  errors={result.errors}
                />

                {/* シフト表 */}
                <ShiftTable result={result} />

                {/* 凡例 */}
                <ShiftLegend />

                {/* CSVダウンロードボタン */}
                <CSVDownloadButton result={result} />
              </div>
            )}

            {!result && !error && (
              <div className="card rounded-xl p-12 text-center hover-lift">
                <div className="w-16 h-16 mx-auto mb-4 rounded-xl bg-slate-100 flex items-center justify-center">
                  <span className="text-4xl animate-float">📋</span>
                </div>
                <p className="text-slate-500 text-lg">
                  左側の設定を完了して、<br />
                  <span className="text-indigo-600 font-semibold">「シフトを作成」</span>
                  ボタンをクリックしてください
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
