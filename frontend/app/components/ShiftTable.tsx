// ShiftTable component for displaying the shift schedule

import { ShiftResponse } from '../types';
import { getShiftStyle, getDayInfo } from '../utils/shiftUtils';

interface ShiftTableProps {
  result: ShiftResponse;
}

export function ShiftTable({ result }: ShiftTableProps) {
  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden border-2 border-indigo-100">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-slate-800 text-white">
              <th className="sticky left-0 z-10 bg-slate-800 px-4 py-3 text-left font-bold min-w-[120px] border-r border-slate-700">
                スタッフ
              </th>
              {Array.from({ length: result.days }, (_, i) => {
                const day = i + 1;
                const { weekday, isWeekend } = getDayInfo(day, result.year, result.month);
                return (
                  <th
                    key={day}
                    className={`px-2 py-3 text-center text-xs font-semibold min-w-[50px] ${
                      isWeekend ? 'bg-slate-700' : ''
                    }`}
                  >
                    {day}
                    <br />
                    <span className="text-slate-300">({weekday})</span>
                  </th>
                );
              })}
              <th className="px-4 py-3 text-center font-bold bg-indigo-700">夜勤</th>
              <th className="px-4 py-3 text-center font-bold bg-green-700">公休</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(result.schedule).map(([name, shifts]) => {
              const nightCount = shifts.filter(s => s.trim() === '夜').length;
              const offCount = shifts.filter(s => s.trim() === '◎' || s.trim() === '◎ ').length;
              return (
                <tr key={name} className="border-b border-slate-200 hover:bg-slate-50">
                  <td className="sticky left-0 z-10 bg-white px-4 py-3 font-semibold text-slate-800 border-r border-slate-200">
                    {name}
                  </td>
                  {shifts.map((shift, idx) => (
                    <td
                      key={idx}
                      className={`px-2 py-3 text-center text-sm font-semibold ${getShiftStyle(shift)}`}
                    >
                      {shift === '◎ ' ? '◎' : shift.trim() || ''}
                    </td>
                  ))}
                  <td className="px-4 py-3 text-center font-bold text-indigo-800 bg-indigo-50">
                    {nightCount}
                  </td>
                  <td className="px-4 py-3 text-center font-bold text-green-800 bg-green-50">
                    {offCount}
                  </td>
                </tr>
              );
            })}
            {/* 日勤帯合計行 */}
            <tr className="bg-slate-100 font-semibold">
              <td className="sticky left-0 z-10 bg-slate-100 px-4 py-2 text-slate-700 border-r border-slate-300">
                日勤計
              </td>
              {Array.from({ length: result.days }, (_, i) => {
                const dayShifts = Object.values(result.schedule).map(shifts => shifts[i]?.trim() || '');
                const count = dayShifts.filter(s => ['早', '日', '遅'].includes(s)).length;
                return (
                  <td
                    key={i}
                    className={`px-2 py-2 text-center text-sm ${
                      count < 3 ? 'bg-red-100 text-red-800' : 'text-slate-700'
                    }`}
                  >
                    {count}
                  </td>
                );
              })}
              <td className="px-4 py-2"></td>
              <td className="px-4 py-2"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}




