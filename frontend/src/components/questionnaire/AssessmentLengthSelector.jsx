/**
 * AssessmentLengthSelector — Lets users choose how many questions to answer.
 *
 * Options: 10 (Quick), 20 (Balanced), 30 (Detailed), 40 (Full, default).
 * Uses refined selectable cards — not generic radio buttons.
 * Changing selection resets questionnaire state to prevent stale answers.
 */

import { motion } from 'framer-motion';
import cn from '../../utils/cn';

const ASSESSMENT_LENGTHS = [
  { count: 10, label: 'Quick', description: '~3 minutes' },
  { count: 20, label: 'Balanced', description: '~5 minutes' },
  { count: 30, label: 'Detailed', description: '~7 minutes' },
  { count: 40, label: 'Full', description: '~10 minutes' },
];

export function AssessmentLengthSelector({ selectedCount, onSelect, disabled = false }) {
  return (
    <section className="mb-10" aria-labelledby="assessment-length-heading">
      <div className="mb-5">
        <h2 id="assessment-length-heading" className="text-lg font-semibold text-stone-900">
          Assessment Length
        </h2>
        <p className="text-sm text-stone-500 mt-1">
          Choose how many questions you'd like to answer.
        </p>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {ASSESSMENT_LENGTHS.map(({ count, label, description }) => {
          const isSelected = selectedCount === count;
          const isDefault = count === 40;

          return (
            <motion.button
              key={count}
              type="button"
              disabled={disabled}
              onClick={() => onSelect(count)}
              whileTap={disabled ? undefined : { scale: 0.98 }}
              className={cn(
                'relative flex flex-col items-center justify-center p-4 rounded-xl border transition-all duration-200 cursor-pointer',
                disabled && 'opacity-50 cursor-not-allowed',
                isSelected
                  ? 'border-stone-900 bg-stone-900 text-white shadow-button'
                  : 'border-stone-200 bg-white text-stone-700 hover:border-stone-400'
              )}
              aria-pressed={isSelected}
              aria-label={`${count} questions — ${label} assessment`}
            >
              <span className={cn(
                'text-2xl font-bold',
                isSelected ? 'text-white' : 'text-stone-900'
              )}>
                {count}
              </span>
              <span className={cn(
                'text-xs font-medium mt-1',
                isSelected ? 'text-white/80' : 'text-stone-500'
              )}>
                {label}
              </span>
              <span className={cn(
                'text-[11px] mt-0.5',
                isSelected ? 'text-white/60' : 'text-stone-400'
              )}>
                {description}
              </span>
              {isDefault && !isSelected && (
                <span className="absolute -top-2 right-2 text-[10px] font-medium bg-stone-100 text-stone-500 px-1.5 py-0.5 rounded">
                  Default
                </span>
              )}
            </motion.button>
          );
        })}
      </div>
    </section>
  );
}

export default AssessmentLengthSelector;
