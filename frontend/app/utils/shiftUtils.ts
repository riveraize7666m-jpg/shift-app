// Utility functions for shift display and validation

export function getShiftStyle(shift: string): string {
  // 希望休は "◎ " (スペース付き) で保存されている
  if (shift === '◎ ') {
    return 'bg-gradient-to-br from-cyan-200 to-teal-200 text-cyan-900 font-bold shadow-sm';
  }
  const val = shift.trim();
  const styles: Record<string, string> = {
    '早': 'bg-gradient-to-br from-yellow-200 to-yellow-300 text-yellow-900 font-bold',
    '日': 'bg-gray-100 text-gray-800 font-semibold',
    '遅': 'bg-gradient-to-br from-orange-200 to-orange-300 text-orange-900 font-bold',
    '夜': 'bg-gradient-to-br from-indigo-400 to-purple-400 text-indigo-900 font-bold',
    '・': 'bg-indigo-100 text-indigo-800 font-semibold',
    '◎': 'bg-green-200 text-green-900 font-semibold', // 通常公休
    '有': 'bg-gradient-to-br from-pink-200 to-pink-300 text-pink-900 font-semibold',
    'リ休': 'bg-gradient-to-br from-amber-200 to-orange-200 text-amber-900 font-semibold',
  };
  return styles[val] || 'bg-gray-200 text-gray-600';
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




