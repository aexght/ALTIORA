/**
 * PredictionInsights — "Why this recommendation?" section.
 *
 * Renders each prediction_explanation entry as an animated numbered card.
 * Replaces the simpler ResultSummary with a more visual presentation.
 * Gracefully hides if no explanations are available.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

const cardVariants = {
  hidden: { opacity: 0, y: 16 },
  visible: (i) => ({
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, delay: 0.1 * i },
  }),
};

export function PredictionInsights({ explanations = [] }) {
  if (!explanations || explanations.length === 0) return null;

  return (
    <section aria-labelledby="insights-heading">
      <div className="flex items-center gap-2 mb-5">
        <Sparkles className="w-5 h-5 text-stone-500" aria-hidden="true" />
        <h2 id="insights-heading" className="text-lg font-semibold text-stone-900">
          Why This Recommendation?
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {explanations.map((line, i) => (
          <motion.div
            key={i}
            custom={i}
            initial="hidden"
            animate="visible"
            variants={cardVariants}
            className="bg-white rounded-xl border border-stone-200 p-5 flex items-start gap-4 hover:shadow-sm transition-shadow duration-200"
          >
            {/* Numbered circle */}
            <span
              className="flex-shrink-0 w-8 h-8 rounded-full bg-stone-100 flex items-center justify-center text-sm font-bold text-stone-900"
              aria-hidden="true"
            >
              {i + 1}
            </span>

            {/* Explanation text */}
            <p className="text-sm text-stone-700 leading-relaxed">{line}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export default PredictionInsights;
