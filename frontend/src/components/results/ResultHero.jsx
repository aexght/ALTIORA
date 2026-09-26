/**
 * ResultHero — The hero section at the top of the results page.
 *
 * Displays the predicted career domain, probability, and confidence badge.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Target } from 'lucide-react';
import { formatPercent } from '../../utils/formatters';

const CONFIDENCE_COLORS = {
  'Very High': 'bg-emerald-50 text-emerald-700 border border-emerald-200',
  'High': 'bg-blue-50 text-blue-700 border border-blue-200',
  'Moderate': 'bg-stone-100 text-stone-700 border border-stone-300',
  'Low': 'bg-stone-100 text-stone-700 border border-stone-300',
  'Very Low': 'bg-stone-50 text-stone-600 border border-stone-200',
};

export function ResultHero({ prediction }) {
  const { domain, probability, confidence } = prediction;
  const colorClass = CONFIDENCE_COLORS[confidence] || CONFIDENCE_COLORS['Moderate'];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="text-center py-10 border-t border-stone-200 mt-2"
    >
      {/* Icon */}
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-xl bg-stone-100 border border-stone-200 mb-6">
        <Target className="w-8 h-8 text-stone-900" />
      </div>

      {/* Label */}
      <p className="text-sm font-medium text-stone-500 uppercase tracking-wider mb-2">
        Your Predicted Career Domain
      </p>

      {/* Domain name */}
      <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-stone-900 mb-4">
        {domain}
      </h1>

      {/* Probability + confidence */}
      <div className="flex items-center justify-center gap-3 flex-wrap">
        <span className="text-2xl font-bold text-stone-900">{formatPercent(probability)}</span>
        <span className={`text-sm font-semibold px-3 py-1 rounded-full ${colorClass}`}>
          {confidence} Confidence
        </span>
      </div>

      {/* Confidence bar */}
      <div className="mt-6 max-w-sm mx-auto">
        <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-stone-900 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(Number(probability), 100)}%` }}
            transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
          />
        </div>
      </div>
    </motion.div>
  );
}

export default ResultHero;
