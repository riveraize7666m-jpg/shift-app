// CSVDownloadButton component for downloading shift schedule as CSV

import { ShiftResponse } from '../types';

interface CSVDownloadButtonProps {
  result: ShiftResponse;
}

export function CSVDownloadButton({ result }: CSVDownloadButtonProps) {
  const handleDownload = () => {
    // CSVデータを作成
    const weekdays = ['日', '月', '火', '水', '木', '金', '土'];
    const csvRows: string[] = [];
    
    // ヘッダー行
    const header = ['スタッフ', ...Array.from({ length: result.days }, (_, i) => {
      const date = new Date(result.year, result.month - 1, i + 1);
      const weekday = weekdays[date.getDay()];
      return `${i + 1}(${weekday})`;
    }), '夜勤', '公休'];
    csvRows.push(header.join(','));
    
    // データ行
    Object.entries(result.schedule).forEach(([name, shifts]) => {
      const nightCount = shifts.filter(s => s.trim() === '夜').length;
      const offCount = shifts.filter(s => s.trim() === '◎' || s.trim() === '◎ ').length;
      // 希望休（"◎ "）は通常の公休（"◎"）に変換
      const row = [name, ...shifts.map(s => s === '◎ ' ? '◎' : s.trim() || ''), nightCount.toString(), offCount.toString()];
      csvRows.push(row.join(','));
    });
    
    // BOM付きUTF-8でエンコード
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
    <div className="bg-white rounded-2xl shadow-xl p-6 border-2 border-indigo-100">
      <button
        onClick={handleDownload}
        className="w-full px-6 py-4 bg-emerald-600 text-white rounded-2xl font-bold text-lg shadow-xl hover:bg-emerald-700 transition-all transform hover:scale-105"
      >
        📥 CSVでダウンロード
      </button>
    </div>
  );
}




