import React from 'react';
import { cn } from '../../utils/cn';

export function ProgressBar({ current, total, label, className }) {
  const percentage = Math.min(Math.max((current / total) * 100, 0), 100);

  return (
    <div className={cn('w-full', className)}>
      <div className="flex justify-between items-center mb-2">
        {label && <span className="text-xs font-medium uppercase tracking-wider text-stone-500">{label}</span>}
        <span className="text-sm text-stone-500 ml-auto">
          {current}/{total}
        </span>
      </div>
      <div className="h-1.5 bg-stone-100 rounded-full overflow-hidden">
        <div
          className="bg-stone-900 h-full rounded-full transition-all duration-500 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export default ProgressBar;
