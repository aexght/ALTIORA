/**
 * QuestionSidebar — Desktop-only sidebar with numbered question buttons.
 * ALTIORA Redesign.
 */

import cn from '../../utils/cn';

export function QuestionSidebar({ questions, answers, currentIndex, onJump, className }) {
  return (
    <aside
      className={cn(
        'hidden lg:flex flex-col w-64 shrink-0 bg-white border border-stone-200 rounded-xl p-5 self-start sticky top-24 shadow-card',
        className
      )}
      aria-label="Question navigator"
    >
      <h3 className="text-xs font-medium uppercase tracking-wider text-stone-500 mb-4">
        Questions
      </h3>
      <div className="grid grid-cols-5 gap-2">
        {questions.map((q, index) => {
          const isAnswered = answers[q.id] !== undefined;
          const isCurrent = index === currentIndex;

          return (
            <button
              key={q.id}
              type="button"
              onClick={() => onJump(index)}
              aria-label={`Go to question ${index + 1}${isAnswered ? ', answered' : ''}${isCurrent ? ', current' : ''}`}
              aria-current={isCurrent ? 'step' : undefined}
              className={cn(
                'w-9 h-9 flex items-center justify-center rounded-md text-xs font-medium transition-all duration-200 cursor-pointer border',
                isCurrent
                  ? 'border-stone-900 text-stone-900 bg-stone-50 shadow-sm'
                  : isAnswered
                    ? 'border-stone-200 bg-stone-900 text-white hover:bg-stone-800'
                    : 'border-transparent bg-stone-100 text-stone-400 hover:bg-stone-200 hover:text-stone-600'
              )}
            >
              {index + 1}
            </button>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-5 pt-4 border-t border-stone-100">
        <p className="text-xs text-stone-400">
          <span className="font-medium text-stone-600">
            {Object.keys(answers).filter(id => questions.some(q => String(q.id) === id)).length}
          </span>{' '}
          of {questions.length} answered
        </p>
      </div>
    </aside>
  );
}

export default QuestionSidebar;
