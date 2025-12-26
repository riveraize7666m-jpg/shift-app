// Validation functions for shift schedules

import { StaffData, ShiftResponse } from '../types';

export interface ValidationWarning {
  type: 'error' | 'warning' | 'info';
  message: string;
}

export function validateSchedule(
  result: ShiftResponse,
  staffList: StaffData[],
  targetOffDays: number
): ValidationWarning[] {
  const warnings: ValidationWarning[] = [];
  const weekdays = ['日', '月', '火', '水', '木', '金', '土'];

  for (let day = 1; day <= result.days; day++) {
    const dayIndex = day - 1;
    const date = new Date(result.year, result.month - 1, day);
    const weekday = weekdays[date.getDay()];
    const dateStr = `${result.month}/${day}(${weekday})`;

    // 各日のシフトを集計
    const dayShifts: string[] = [];
    Object.values(result.schedule).forEach(shifts => {
      const shift = shifts[dayIndex]?.trim() || '';
      if (shift) dayShifts.push(shift);
    });

    // 早番のチェック
    const earlyCount = dayShifts.filter(s => s === '早').length;
    if (earlyCount === 0) {
      warnings.push({ type: 'error', message: `${dateStr}: 早番がいません` });
    }

    // 遅番のチェック
    const lateCount = dayShifts.filter(s => s === '遅').length;
    if (lateCount === 0) {
      warnings.push({ type: 'error', message: `${dateStr}: 遅番がいません` });
    }

    // 夜勤のチェック
    const nightCount = dayShifts.filter(s => s === '夜').length;
    if (nightCount === 0) {
      warnings.push({ type: 'error', message: `${dateStr}: 夜勤がいません` });
    }

    // 日勤帯（早・日・遅）のチェック
    const dayShiftCount = dayShifts.filter(s => ['早', '日', '遅'].includes(s)).length;
    if (dayShiftCount < 3) {
      warnings.push({ 
        type: 'warning', 
        message: `${dateStr}: 日勤帯が${dayShiftCount}名です` 
      });
    }
  }

  // 各スタッフの公休数と夜勤回数のチェック
  staffList.forEach(staff => {
    const shifts = result.schedule[staff.name] || [];
    
    if (staff.type === 0) {
      // 常勤スタッフの公休数チェック
      const offCount = shifts.filter(s => s.trim() === '◎' || s.trim() === '◎ ').length;
      if (offCount !== targetOffDays) {
        warnings.push({
          type: 'info',
          message: `${staff.name}: 公休${offCount}日（目標${targetOffDays}日）`
        });
      }
    }

    // 夜勤目標のチェック（常勤スタッフのみ）
    if (staff.type === 0 && staff.night_target > 0) {
      const nightCount = shifts.filter(s => s.trim() === '夜').length;
      if (nightCount !== staff.night_target) {
        warnings.push({
          type: 'info',
          message: `${staff.name}: 夜勤${nightCount}回（目標${staff.night_target}回）`
        });
      }
    }
  });

  return warnings;
}



