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

  if (errors.length > 0 && warnings.length === 0) {
    return (
      <div className="card rounded-xl p-5">
        <h3 className="font-bold text-slate-700 mb-3 text-sm flex items-center gap-2">
          ⚠️ 確認ポイント
        </h3>
        <div className="space-y-1.5">
          {errors.slice(0, 20).map((err, idx) => (
            <div key={idx} className="text-sm text-red-600 font-medium flex items-start gap-2 bg-red-50 rounded-lg p-2">
              <span>🔴</span>
              <span>{err}</span>
            </div>
          ))}
          {errors.length > 20 && (
            <div className="text-sm text-slate-500 font-medium pl-6">
              ...他 {errors.length - 20} 件
            </div>
          )}
        </div>
      </div>
    );
  }

  const errorWarnings = warnings.filter(w => w.type === 'error');
  const warnWarnings = warnings.filter(w => w.type === 'warning');
  const infoWarnings = warnings.filter(w => w.type === 'info');

  return (
    <div className="card rounded-xl p-5">
      <h3 className="font-bold text-slate-700 mb-3 text-sm flex items-center gap-2">
        📋 確認ポイント
        <span className="text-xs font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
          {warnings.length}件
        </span>
      </h3>
      <div className="space-y-1.5">
        {errorWarnings.map((w, idx) => (
          <div key={`error-${idx}`} className="text-sm text-red-600 font-medium flex items-start gap-2 bg-red-50 rounded-lg p-2 border border-red-100">
            <span>🔴</span>
            <span>{w.message}</span>
          </div>
        ))}
        {warnWarnings.map((w, idx) => (
          <div key={`warn-${idx}`} className="text-sm text-amber-600 font-medium flex items-start gap-2 bg-amber-50 rounded-lg p-2 border border-amber-100">
            <span>⚠️</span>
            <span>{w.message}</span>
          </div>
        ))}
        {infoWarnings.map((w, idx) => (
          <div key={`info-${idx}`} className="text-sm text-blue-600 font-medium flex items-start gap-2 bg-blue-50 rounded-lg p-2 border border-blue-100">
            <span>ℹ️</span>
            <span>{w.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
