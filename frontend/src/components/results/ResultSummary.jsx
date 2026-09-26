/**
 * ResultSummary — Renders the prediction explanation returned by the backend.
 *
 * Only renders if prediction_explanation array has entries.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Lightbulb } from 'lucide-react';

export function ResultSummary({ explanations = [] }) {
  if (!explanations || explanations.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.4 }}
      className="mt-10"
    >
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-5 h-5 text-stone-500" />
        <h2 className="text-lg font-semibold text-stone-900">How We Reached This Prediction</h2>
      </div>
      <div className="bg-white rounded-xl border border-stone-200 p-6">
        <ul className="space-y-3">
          {explanations.map((line, i) => (
            <li key={i} className="flex items-start gap-3 text-sm text-stone-600 leading-relaxed">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-stone-100 flex items-center justify-center text-xs font-semibold text-stone-500 mt-0.5">
                {i + 1}
              </span>
              <span>{line}</span>
            </li>
          ))}
        </ul>
      </div>
    </motion.div>
  );
}

export default ResultSummary;
