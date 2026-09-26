/**
 * QuestionNavigation — Previous / Next / Finish buttons.
 * ALTIORA Redesign.
 */

import { ArrowLeft, ArrowRight, CheckCircle } from 'lucide-react';
import { Button } from '../common/Button';

export function QuestionNavigation({
  currentIndex,
  total,
  isCurrentAnswered,
  allAnswered,
  onPrevious,
  onNext,
  onFinish,
  onJumpToUnanswered,
  isSubmitting = false,
}) {
  const isFirst = currentIndex === 0;
  const isLast = currentIndex === total - 1;

  const handleFinishClick = () => {
    if (isSubmitting) return;
    if (!allAnswered) {
      onJumpToUnanswered();
      return;
    }
    onFinish();
  };

  return (
    <div className="flex items-center justify-between mt-8 pt-6 border-t border-stone-100">
      <Button
        variant="secondary"
        disabled={isFirst || isSubmitting}
        onClick={onPrevious}
        aria-label="Previous question"
      >
        <ArrowLeft className="w-4 h-4" />
        Previous
      </Button>

      {isLast ? (
        <Button
          onClick={handleFinishClick}
          disabled={!isCurrentAnswered || isSubmitting}
          loading={isSubmitting}
          aria-label="Finish questionnaire"
          size="md"
          className={allAnswered && !isSubmitting ? 'ring-2 ring-stone-400 ring-offset-2' : ''}
        >
          {!isSubmitting && <CheckCircle className="w-4 h-4" />}
          Finish
        </Button>
      ) : (
        <Button
          onClick={onNext}
          disabled={!isCurrentAnswered || isSubmitting}
          aria-label="Next question"
        >
          Next
          <ArrowRight className="w-4 h-4" />
        </Button>
      )}
    </div>
  );
}

export default QuestionNavigation;
