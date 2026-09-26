/**
 * QuestionProgress — Displays current question number, progress bar, and percentage.
 * Reuses the existing ProgressBar layout component.
 */

import { motion } from 'framer-motion';
import cn from '../../utils/cn';

export function QuestionProgress({ current, total, className }) {
  const percentage = Math.min(Math.max(((current + 1) / total) * 100, 0), 100);

  return (
    <div className={cn('w-full', className)}>
      <div className="flex justify-between items-center mb-2">
        <span className="text-sm font-medium text-stone-700">
          Question {current + 1} of {total}
        </span>
        <span className="text-sm text-stone-500">
          {Math.round(percentage)}%
        </span>
      </div>
      <div
        className="h-1.5 bg-stone-200 rounded-full overflow-hidden"
        role="progressbar"
        aria-valuenow={Math.round(percentage)}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-label={`Question ${current + 1} of ${total}`}
      >
        <motion.div
          className="bg-stone-900 h-full rounded-full"
          initial={false}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.35, ease: 'easeOut' }}
        />
      </div>
    </div>
  );
}

export default QuestionProgress;
