// ValidationWarnings component for displaying schedule validation issues

import { ValidationWarning } from '../utils/validation';

interface ValidationWarningsProps {
  warnings: ValidationWarning[];
  errors?: string[];
}

export function ValidationWarnings({ warnings, errors = [] }: ValidationWarningsProps) {
  if (warnings.length === 0 && errors.length === 0) {
    return null;
  }

  // errorsがあってwarningsがない場合（後方互換性）
  if (errors.length > 0 && warnings.length === 0) {
    return (
      <div className="bg-slate-50 border-2 border-slate-300 rounded-2xl p-5 shadow-lg">
        <h3 className="font-bold text-slate-800 mb-3 text-lg flex items-center gap-2">
          <span>📋</span>
          確認ポイント
        </h3>
        <div className="space-y-2">
          {errors.slice(0, 20).map((err, idx) => (
            <div key={idx} className="text-sm text-red-700 font-medium flex items-start gap-2">
              <span>🔴</span>
              <span>{err}</span>
            </div>
          ))}
          {errors.length > 20 && (
            <div className="text-sm text-slate-600 font-semibold">
              ...他 {errors.length - 20} 件
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-50 border-2 border-slate-300 rounded-2xl p-5 shadow-lg">
      <h3 className="font-bold text-slate-800 mb-4 text-lg flex items-center gap-2">
        <span>📋</span>
        確認ポイント
      </h3>
      <div className="space-y-2">
        {warnings.map((w, idx) => {
          let icon = '🔴';
          let textColor = 'text-red-700';
          
          if (w.type === 'warning') {
            icon = '⚠️';
            textColor = 'text-amber-700';
          } else if (w.type === 'info') {
            icon = 'ℹ️';
            textColor = 'text-blue-700';
          }
          
          return (
            <div key={idx} className={`text-sm ${textColor} font-medium flex items-start gap-2`}>
              <span>{icon}</span>
              <span>{w.message}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}




