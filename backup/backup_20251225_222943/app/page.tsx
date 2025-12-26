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
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showHelp, setShowHelp] = useState(false);

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
    setSidebarOpen(false);

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
      className="min-h-screen bg-slate-100"
      onClick={(e) => {
        if (!(e.target as HTMLElement).closest('.date-selector-container')) {
          setOpenCalendar(null);
        }
      }}
    >
      {/* ヘッダー */}
      <header className="bg-white border-b border-slate-200 px-4 py-3 flex items-center justify-between fixed top-0 left-0 right-0 z-30">
        <div className="flex items-center gap-3">
          {/* ハンバーガーメニュー */}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-slate-100 rounded-lg transition-colors"
            aria-label="メニュー"
          >
            <svg className="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          {/* ロゴ */}
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
              <span className="text-white text-sm font-bold">✦</span>
            </div>
            <span className="text-lg font-bold text-slate-800 hidden sm:inline">Shift Manager Pro</span>
          </div>
        </div>

        {/* グローバルメニュー */}
        <nav className="flex items-center gap-2">
          <button
            onClick={() => {
              if (staffList.length === 0) {
                setSidebarOpen(true);
              } else {
                handleCreateShift();
              }
            }}
            disabled={isCreating}
            className="px-4 py-2 btn-primary rounded-lg font-medium text-sm disabled:opacity-40"
          >
            {isCreating ? '作成中...' : 'シフトを作成'}
          </button>
          <button
            onClick={() => setShowHelp(true)}
            className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg font-medium text-sm transition-colors"
          >
            使い方
          </button>
        </nav>
      </header>

      {/* サイドバー（オーバーレイ） */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/30 z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* サイドバー - 常にオーバーレイとして表示 */}
      <aside 
        className={`
          fixed top-0 left-0 bottom-0 z-50
          w-80 bg-white border-r border-slate-200 
          transform transition-transform duration-300 ease-in-out
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          flex flex-col
        `}
      >
        {/* サイドバーヘッダー */}
        <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-white">
          <span className="font-bold text-slate-800">設定</span>
          <button
            onClick={() => setSidebarOpen(false)}
            className="p-2 hover:bg-slate-100 rounded-lg"
          >
            <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* サイドバーコンテンツ - スクロール可能 */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
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
        </div>

        {/* サイドバーフッター - シフト作成ボタン */}
        <div className="p-4 border-t border-slate-200 bg-white">
          <button
            onClick={handleCreateShift}
            disabled={isCreating || staffList.length === 0}
            className="w-full px-4 py-3 btn-primary rounded-lg font-bold text-base disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isCreating ? (
              <span className="flex items-center justify-center gap-2">
                <span className="animate-spin">⏳</span>
                作成中...
              </span>
            ) : (
              <span className="flex items-center justify-center gap-2">
                <span>🚀</span>
                シフトを作成
              </span>
            )}
          </button>
        </div>
      </aside>

      {/* メインコンテンツ - 常にフル幅 */}
      <main className="pt-16 min-h-screen">
        <div className="p-4 lg:p-6 max-w-7xl mx-auto">
          {/* 処理中表示 */}
          {isCreating && (
            <div className="card rounded-xl p-8 mb-4">
              <div className="flex flex-col items-center justify-center">
                <div className="w-16 h-16 mb-4 rounded-full bg-indigo-100 flex items-center justify-center">
                  <svg className="w-8 h-8 text-indigo-600 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-slate-800 mb-1">シフト表を作成中...</h3>
                <p className="text-slate-500 text-sm">最適なシフトを計算しています</p>
              </div>
            </div>
          )}

          {error && !isCreating && (
            <div className="card rounded-xl p-4 mb-4 border-l-4 border-l-red-500 bg-red-50">
              <div className="flex items-center gap-3">
                <span className="text-xl">⚠️</span>
                <p className="text-red-700 font-medium">{error}</p>
              </div>
            </div>
          )}

          {result && !isCreating && (
            <div className="space-y-4">
              {/* 成功メッセージ */}
              <div className="card rounded-xl p-4 border-l-4 border-l-emerald-500 bg-emerald-50">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎉</span>
                  <div>
                    <h2 className="text-xl font-bold text-slate-800">
                      シフト案を作成しました
                    </h2>
                    <p className="text-emerald-600 font-medium text-sm">
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

          {!result && !error && !isCreating && (
            <div className="card rounded-xl p-16 text-center max-w-xl mx-auto">
              <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-slate-100 flex items-center justify-center">
                <span className="text-5xl animate-float">📋</span>
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-2">シフト表を作成</h2>
              <p className="text-slate-500 mb-6">
                スタッフの情報を設定して、最適なシフト表を自動生成します
              </p>
              <button
                onClick={() => setSidebarOpen(true)}
                className="px-8 py-3 btn-primary rounded-xl font-bold text-lg"
              >
                設定を開始する
              </button>
            </div>
          )}
        </div>
      </main>

      {/* 使い方モーダル */}
      {showHelp && (
        <>
          <div 
            className="fixed inset-0 bg-black/50 z-50"
            onClick={() => setShowHelp(false)}
          />
          <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 bg-white rounded-2xl p-6 w-[90%] max-w-lg max-h-[80vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-slate-800">使い方</h2>
              <button
                onClick={() => setShowHelp(false)}
                className="p-2 hover:bg-slate-100 rounded-lg"
              >
                <svg className="w-5 h-5 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="space-y-4 text-slate-600">
              <div>
                <h3 className="font-bold text-slate-800 mb-1">1. シフト設定</h3>
                <p className="text-sm">年月と常勤スタッフの公休数を設定します。</p>
              </div>
              <div>
                <h3 className="font-bold text-slate-800 mb-1">2. スタッフ追加</h3>
                <p className="text-sm">「+ 追加」ボタンでスタッフを追加し、名前・属性・希望シフトを設定します。</p>
              </div>
              <div>
                <h3 className="font-bold text-slate-800 mb-1">3. シフト作成</h3>
                <p className="text-sm">「シフトを作成」ボタンを押すと、ルールに基づいてシフト表が自動生成されます。</p>
              </div>
              <div>
                <h3 className="font-bold text-slate-800 mb-1">4. CSVダウンロード</h3>
                <p className="text-sm">作成したシフト表はCSVファイルでダウンロードできます。</p>
              </div>
              <div className="pt-2 border-t border-slate-200">
                <h3 className="font-bold text-slate-800 mb-1">💡 ヒント</h3>
                <p className="text-sm">設定ファイルを保存しておくと、翌月のシフト作成が楽になります。</p>
              </div>
            </div>
            <button
              onClick={() => setShowHelp(false)}
              className="w-full mt-6 px-4 py-2.5 btn-primary rounded-lg font-semibold"
            >
              閉じる
            </button>
          </div>
        </>
      )}
    </div>
  );
}
