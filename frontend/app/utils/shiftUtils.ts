// Utility functions for shift display and validation

export function getShiftStyle(shift: string): string {
  // 希望休は "◎ " (スペース付き) で保存されている
  if (shift === '◎ ') {
    return 'bg-cyan-100 text-cyan-700';
  }
  const val = shift.trim();
  const styles: Record<string, string> = {
    '早': 'bg-amber-100 text-amber-700',
    '日': 'bg-slate-200 text-slate-700',
    '遅': 'bg-orange-100 text-orange-700',
    '夜': 'bg-indigo-200 text-indigo-800',
    '・': 'bg-violet-100 text-violet-700',
    '◎': 'bg-emerald-100 text-emerald-700',
    '有': 'bg-pink-100 text-pink-700',
    'リ休': 'bg-amber-200 text-amber-800',
  };
  return styles[val] || 'bg-slate-100 text-slate-500';
}

export function getDayInfo(day: number, year: number, month: number) {
  const date = new Date(year, month - 1, day);
  const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
  const weekday = weekdays[date.getDay()];
  const isWeekend = date.getDay() === 0 || date.getDay() === 6;
  return { weekday, isWeekend };
}

export function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}
