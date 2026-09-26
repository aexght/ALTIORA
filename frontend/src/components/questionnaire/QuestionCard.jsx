/**
 * QuestionCard — Displays a single question with its number, text, and options.
 * Wraps QuestionOptions with a card layout and slide animation.
 * ALTIORA Redesign.
 */

import { motion, AnimatePresence } from 'framer-motion';
import { QuestionOptions } from './QuestionOptions';

const slideVariants = {
  enter: (direction) => ({
    x: direction > 0 ? 40 : -40,
    opacity: 0,
  }),
  center: {
    x: 0,
    opacity: 1,
  },
  exit: (direction) => ({
    x: direction > 0 ? -40 : 40,
    opacity: 0,
  }),
};

export function QuestionCard({ question, index, selectedOptionId, onSelect, direction, disabled = false }) {
  if (!question) return null;

  return (
    <AnimatePresence mode="wait" custom={direction}>
      <motion.div
        key={question.id}
        custom={direction}
        variants={slideVariants}
        initial="enter"
        animate="center"
        exit="exit"
        transition={{ duration: 0.25, ease: 'easeInOut' }}
        className="bg-white rounded-xl border border-stone-200 p-6 sm:p-8 shadow-card"
      >
        {/* Question number & text */}
        <div className="mb-6">
          <span className="inline-block text-[11px] font-bold uppercase tracking-widest text-stone-900 bg-stone-100 px-3 py-1 rounded-md mb-4 border border-stone-200/60">
            Q{index + 1}
          </span>
          <h2
            id={`question-${question.id}`}
            className="text-lg sm:text-xl font-medium text-stone-900 leading-relaxed font-display"
          >
            {question.question}
          </h2>
        </div>

        {/* Options */}
        <QuestionOptions
          questionId={question.id}
          options={question.options}
          selectedOptionId={selectedOptionId}
          onSelect={onSelect}
          disabled={disabled}
        />
      </motion.div>
    </AnimatePresence>
  );
}

export default QuestionCard;
