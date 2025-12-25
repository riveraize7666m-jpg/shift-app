// CSVDownloadButton component for downloading shift schedule as CSV

import { ShiftResponse } from '../types';

interface CSVDownloadButtonProps {
  result: ShiftResponse;
}

export function CSVDownloadButton({ result }: CSVDownloadButtonProps) {
  const handleDownload = () => {
    const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
    const csvRows: string[] = [];
    
    const header = ['スタッフ', ...Array.from({ length: result.days }, (_, i) => {
      const date = new Date(result.year, result.month - 1, i + 1);
      const weekday = weekdays[date.getDay()];
      return `${i + 1}(${weekday})`;
    }), '夜勤', '公休'];
    csvRows.push(header.join(','));
    
    Object.entries(result.schedule).forEach(([name, shifts]) => {
      const nightCount = shifts.filter(s => s.trim() === '夜').length;
      const offCount = shifts.filter(s => s.trim() === '◎' || s.trim() === '◎ ').length;
      const row = [name, ...shifts.map(s => s === '◎ ' ? '◎' : s.trim() || ''), nightCount.toString(), offCount.toString()];
      csvRows.push(row.join(','));
    });
    
    const csvContent = '\uFEFF' + csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `shift_${result.year}_${result.month}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="card rounded-xl p-5">
      <button
        onClick={handleDownload}
        className="w-full px-5 py-3 bg-emerald-500 text-white rounded-lg font-bold hover:bg-emerald-600 transition-colors flex items-center justify-center gap-2"
      >
        <span>📥</span>
        <span>CSVでダウンロード</span>
      </button>
    </div>
  );
}
