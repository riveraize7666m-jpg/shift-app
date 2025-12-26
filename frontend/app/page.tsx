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

  // 新しいスタッフを追加
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

  // スタッフを削除
  const removeStaff = (index: number) => {
    const newList = staffList.filter((_, i) => i !== index);
    setStaffList(newList);
    if (selectedStaffIndex === index) {
      setSelectedStaffIndex(null);
    } else if (selectedStaffIndex !== null && selectedStaffIndex > index) {
      setSelectedStaffIndex(selectedStaffIndex - 1);
    }
  };

  // スタッフの設定を更新
  const updateStaff = (index: number, updates: Partial<StaffData>) => {
    const newList = [...staffList];
    newList[index] = { ...newList[index], ...updates };
    setStaffList(newList);
  };

  // シフトを作成
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

  // カレンダーを開く
  const handleOpenCalendar = (field: string, staffIndex: number) => {
    setOpenCalendar({ field, staffIndex });
  };

  // カレンダーを閉じる
  const handleCloseCalendar = () => {
    setOpenCalendar(null);
  };

  // バリデーション警告を取得
  const getValidationWarnings = () => {
    if (!result) return [];
    return validateSchedule(result, staffList, targetOffDays);
  };

  return (
    <div 
      className="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-indigo-50 overflow-x-hidden"
      onClick={(e) => {
        // カレンダー外をクリックしたら閉じる
        if (!(e.target as HTMLElement).closest('.date-selector-container')) {
          setOpenCalendar(null);
        }
      }}
    >
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="mb-10">
          <div className="bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 rounded-2xl p-8 shadow-xl mb-6">
            <h1 className="text-5xl font-bold text-white mb-3">
              ✦ Shift Manager Pro
            </h1>
            <p className="text-indigo-100 text-lg">最適なシフトを、ワンクリックで。</p>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Sidebar - Settings */}
          <div className="lg:col-span-1 space-y-6">
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
              className="w-full px-6 py-5 bg-gradient-to-r from-indigo-600 via-indigo-700 to-purple-600 text-white rounded-2xl font-bold text-lg shadow-xl hover:shadow-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-105 disabled:transform-none"
            >
              {isCreating ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="animate-spin">⏳</span>
                  シフト作成中...
                </span>
              ) : (
                '🚀 シフトを作成'
              )}
            </button>
          </div>

          {/* Main Content - Results */}
          <div className="lg:col-span-2">
            {error && (
              <div className="bg-red-50 border-2 border-red-300 rounded-2xl p-5 mb-6 shadow-lg">
                <p className="text-red-800 font-semibold text-lg">❌ {error}</p>
              </div>
            )}

            {result && (
              <div className="space-y-6">
                {/* 成功メッセージ */}
                <div className="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-2xl p-8 shadow-xl">
                  <h2 className="text-3xl font-bold mb-2">
                    🎉 シフト案を作成しました
                  </h2>
                  <p className="text-emerald-100 text-lg">
                    {result.year}年{result.month}月
                  </p>
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
              <div className="bg-white rounded-2xl shadow-xl p-12 text-center border-2 border-indigo-100">
                <p className="text-slate-600 text-lg font-medium">
                  左側の設定を完了して、「シフトを作成」ボタンをクリックしてください
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
