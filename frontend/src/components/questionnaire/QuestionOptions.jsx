/**
 * QuestionOptions — Renders radio options for a single question.
 * ALTIORA Redesign.
 */

import { motion } from 'framer-motion';
import cn from '../../utils/cn';

export function QuestionOptions({ questionId, options, selectedOptionId, onSelect, disabled = false }) {
  return (
    <div className="flex flex-col gap-3" role="radiogroup" aria-labelledby={`question-${questionId}`}>
      {options.map((option) => {
        const isSelected = selectedOptionId === option.id;
        const radioId = `${questionId}-${option.id}`;

        return (
          <motion.label
            key={option.id}
            htmlFor={radioId}
            className={cn(
              'flex items-start p-4 border rounded-lg transition-all duration-200',
              disabled && 'opacity-60 cursor-not-allowed',
              !disabled && 'cursor-pointer',
              isSelected
                ? 'border-stone-900 bg-stone-50'
                : 'border-stone-200 bg-white hover:border-stone-300 hover:bg-stone-50/50'
            )}
            whileTap={disabled ? undefined : { scale: 0.99 }}
          >
            <div className="flex items-center h-5 mt-0.5 relative">
              <input
                id={radioId}
                name={questionId}
                type="radio"
                value={option.id}
                checked={isSelected}
                disabled={disabled}
                onChange={() => onSelect(questionId, option.id)}
                className="sr-only" // visually hidden but accessible
              />
              {/* Custom ALTIORA radio button */}
              <div className={cn(
                "w-4 h-4 rounded-full border flex items-center justify-center transition-colors",
                isSelected ? "border-stone-900 bg-stone-900" : "border-stone-300 bg-white"
              )}>
                {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
              </div>
            </div>
            <div className="ml-4 flex flex-col">
              <span
                className={cn(
                  'block text-sm font-medium',
                  isSelected ? 'text-stone-900' : 'text-stone-700'
                )}
              >
                {option.id}.
              </span>
              <span className={cn(
                'block text-sm mt-0.5',
                isSelected ? 'text-stone-700' : 'text-stone-500'
              )}>
                {option.text}
              </span>
            </div>
          </motion.label>
        );
      })}
    </div>
  );
}

export default QuestionOptions;
