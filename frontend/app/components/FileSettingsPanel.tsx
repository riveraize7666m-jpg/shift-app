// FileSettingsPanel component for file import/export functionality

import { StaffData } from '../types';
import { parseDays } from '../utils/api';

interface FileSettingsPanelProps {
  year: number;
  month: number;
  targetOffDays: number;
  staffList: StaffData[];
  onYearChange: (year: number) => void;
  onMonthChange: (month: number) => void;
  onTargetOffDaysChange: (days: number) => void;
  onStaffListChange: (staffList: StaffData[]) => void;
}

export function FileSettingsPanel({
  year,
  month,
  targetOffDays,
  staffList,
  onYearChange,
  onMonthChange,
  onTargetOffDaysChange,
  onStaffListChange,
}: FileSettingsPanelProps) {
  const handleFileImport = (file: File) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target?.result as string);
        if (data.staff_list_save) {
          // スタッフリストを復元
          const loadedStaff: StaffData[] = data.staff_list_save.map((s: any) => ({
            name: s.name,
            type: s.type,
            night_target: data[`night_${s.name}`] ?? 4,
            req_night: parseDays(data[`req_n_${s.name}`] ?? ''),
            req_early: parseDays(data[`req_e_${s.name}`] ?? ''),
            req_late: parseDays(data[`req_l_${s.name}`] ?? ''),
            req_day: parseDays(data[`req_d_${s.name}`] ?? ''),
            req_off: parseDays(data[`off_${s.name}`] ?? ''),
            req_work: parseDays(data[`work_${s.name}`] ?? ''),
            refresh_days: parseDays(data[`ref_${s.name}`] ?? ''),
            paid_leave_days: parseDays(data[`paid_${s.name}`] ?? ''),
            prev_shift: data[`prev_${s.name}`] ?? '◎',
            prev_streak: data[`streak_${s.name}`] ?? 0,
            fixed_shifts: [
              data[`f1_${s.name}`] ?? '',
              data[`f2_${s.name}`] ?? '',
              data[`f3_${s.name}`] ?? '',
            ],
          }));
          onStaffListChange(loadedStaff);
          // その他の設定も復元
          if (data.input_year) onYearChange(data.input_year);
          if (data.input_month) onMonthChange(data.input_month);
          if (data.target_off) onTargetOffDaysChange(data.target_off);
          alert('✓ 設定を復元しました');
        }
      } catch (err) {
        alert('エラー: ファイルの読み込みに失敗しました');
      }
    };
    reader.readAsText(file);
  };

  const handleExportStaffOnly = () => {
    const data = {
      save_type: 'staff_only',
      staff_list_save: staffList.map(s => ({ name: s.name, type: s.type })),
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'staff_list.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportFull = () => {
    const data: any = {
      save_type: 'full',
      input_year: year,
      input_month: month,
      target_off: targetOffDays,
      staff_list_save: staffList.map(s => ({ name: s.name, type: s.type })),
    };
    // 各スタッフの詳細設定を追加
    staffList.forEach(s => {
      data[`prev_${s.name}`] = s.prev_shift;
      data[`streak_${s.name}`] = s.prev_streak;
      data[`night_${s.name}`] = s.night_target;
      data[`req_n_${s.name}`] = s.req_night.join(',');
      data[`req_e_${s.name}`] = s.req_early.join(',');
      data[`req_l_${s.name}`] = s.req_late.join(',');
      data[`req_d_${s.name}`] = s.req_day.join(',');
      data[`off_${s.name}`] = s.req_off.join(',');
      data[`work_${s.name}`] = s.req_work.join(',');
      data[`ref_${s.name}`] = s.refresh_days.join(',');
      data[`paid_${s.name}`] = s.paid_leave_days.join(',');
      data[`f1_${s.name}`] = s.fixed_shifts[0] || '';
      data[`f2_${s.name}`] = s.fixed_shifts[1] || '';
      data[`f3_${s.name}`] = s.fixed_shifts[2] || '';
    });
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `shift_settings_full_${year}_${month}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 border-2 border-indigo-100">
      <h2 className="text-xl font-bold text-indigo-900 mb-5 flex items-center gap-2">
        <span className="text-2xl">💾</span>
        設定の保存・読込
      </h2>
      <div className="space-y-4">
        {/* ファイル読み込み */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            設定ファイルを読み込み
          </label>
          <input
            type="file"
            accept=".json"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                handleFileImport(file);
              }
            }}
            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
          />
        </div>

        {/* ファイル保存 */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            設定ファイルを保存
          </label>
          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={handleExportStaffOnly}
              className="px-4 py-2.5 bg-slate-600 text-white rounded-xl hover:bg-slate-700 transition-all text-sm font-semibold shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={staffList.length === 0}
            >
              👥 名前のみ
            </button>
            <button
              onClick={handleExportFull}
              className="px-4 py-2.5 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-all text-sm font-semibold shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={staffList.length === 0}
            >
              📋 全設定
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-2">
            「名前のみ」: 翌月用 / 「全設定」: バックアップ用
          </p>
        </div>
      </div>
    </div>
  );
}




