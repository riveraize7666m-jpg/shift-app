// ShiftTable component for displaying the shift schedule

import { ShiftResponse } from '../types';
import { getShiftStyle, getDayInfo } from '../utils/shiftUtils';

interface ShiftTableProps {
  result: ShiftResponse;
}

export function ShiftTable({ result }: ShiftTableProps) {
  return (
    <div className="card rounded-xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full border-collapse shift-table">
          <thead>
            <tr>
              <th className="sticky left-0 z-10 bg-slate-100 px-4 py-3 text-left font-bold text-slate-700 min-w-[130px] border-r border-slate-200">
                スタッフ
              </th>
              {Array.from({ length: result.days }, (_, i) => {
                const day = i + 1;
                const { weekday, isWeekend } = getDayInfo(day, result.year, result.month);
                return (
                  <th
                    key={day}
                    className={`px-1.5 py-2 text-center text-xs font-medium min-w-[44px] ${
                      isWeekend ? 'bg-slate-100' : 'bg-slate-50'
                    }`}
                  >
                    <div className="text-slate-700 font-bold">{day}</div>
                    <div className={`text-[10px] ${isWeekend ? 'text-indigo-500' : 'text-slate-400'}`}>
                      {weekday}
                    </div>
                  </th>
                );
              })}
              <th className="px-3 py-2 text-center font-bold bg-indigo-100 text-indigo-700 min-w-[50px]">
                夜勤
              </th>
              <th className="px-3 py-2 text-center font-bold bg-emerald-100 text-emerald-700 min-w-[50px]">
                公休
              </th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(result.schedule).map(([name, shifts], rowIdx) => {
              const nightCount = shifts.filter(s => s.trim() === '夜').length;
              const offCount = shifts.filter(s => s.trim() === '◎' || s.trim() === '◎ ').length;
              return (
                <tr 
                  key={name} 
                  className={`border-b border-slate-100 ${rowIdx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'} hover:bg-indigo-50/50`}
                >
                  <td className="sticky left-0 z-10 bg-white px-4 py-2.5 font-medium text-slate-700 border-r border-slate-200">
                    {name}
                  </td>
                  {shifts.map((shift, idx) => (
                    <td
                      key={idx}
                      className="px-0.5 py-1.5 text-center"
                    >
                      <span className={`inline-block min-w-[32px] py-1 rounded text-xs font-bold ${getShiftStyle(shift)}`}>
                        {shift === '◎ ' ? '◎' : shift.trim() || ''}
                      </span>
                    </td>
                  ))}
                  <td className="px-3 py-2.5 text-center font-bold text-indigo-700 bg-indigo-50/50">
                    {nightCount}
                  </td>
                  <td className="px-3 py-2.5 text-center font-bold text-emerald-700 bg-emerald-50/50">
                    {offCount}
                  </td>
                </tr>
              );
            })}
            {/* 日勤帯合計行 */}
            <tr className="bg-slate-100 font-medium border-t-2 border-slate-200">
              <td className="sticky left-0 z-10 bg-slate-100 px-4 py-2 text-slate-600 border-r border-slate-200">
                日勤計
              </td>
              {Array.from({ length: result.days }, (_, i) => {
                const dayShifts = Object.values(result.schedule).map(shifts => shifts[i]?.trim() || '');
                const count = dayShifts.filter(s => ['早', '日', '遅'].includes(s)).length;
                return (
                  <td
                    key={i}
                    className={`px-1.5 py-2 text-center text-xs font-bold ${
                      count < 3 
                        ? 'bg-red-100 text-red-600' 
                        : 'text-slate-600'
                    }`}
                  >
                    {count}
                  </td>
                );
              })}
              <td className="px-3 py-2 bg-indigo-50/30"></td>
              <td className="px-3 py-2 bg-emerald-50/30"></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
}
