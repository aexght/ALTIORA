/**
 * StrengthCard — Strength Highlights section.
 *
 * Parses prediction_explanation entries to extract strength prefixes
 * (Excellent, Strong, Good) and displays them as visual strength badges.
 *
 * If the backend doesn't provide explanations, or no entries have
 * recognised prefixes, this entire section is hidden.
 * Never fabricates data.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Zap } from 'lucide-react';

const STRENGTH_CONFIG = {
  Excellent: { bg: 'bg-stone-50', text: 'text-stone-900', border: 'border-stone-200' },
  Strong: { bg: 'bg-stone-50', text: 'text-stone-900', border: 'border-stone-200' },
  Good: { bg: 'bg-stone-50', text: 'text-stone-900', border: 'border-stone-200' },
};

const PREFIXES = ['Excellent', 'Strong', 'Good'];

function parseStrengths(explanations) {
  if (!explanations || explanations.length === 0) return [];

  return explanations
    .map((line) => {
      for (const prefix of PREFIXES) {
        if (line.startsWith(prefix + ' ')) {
          const description = line.slice(prefix.length + 1);
          return { prefix, description, config: STRENGTH_CONFIG[prefix] };
        }
      }
      return null;
    })
    .filter(Boolean);
}

export function StrengthCard({ explanations = [] }) {
  const strengths = parseStrengths(explanations);

  if (strengths.length === 0) return null;

  return (
    <section aria-labelledby="strengths-heading">
      <div className="flex items-center gap-2 mb-5">
        <Zap className="w-5 h-5 text-stone-500" aria-hidden="true" />
        <h2 id="strengths-heading" className="text-lg font-semibold font-display text-stone-900">
          Your Strengths
        </h2>
      </div>

      <div className="flex flex-wrap gap-3">
        {strengths.map((s, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.08 * i }}
            className={`inline-flex items-center gap-2 px-4 py-2.5 rounded-xl border ${s.config.bg} ${s.config.border}`}
          >
            <div>
              <span className={`text-xs font-bold uppercase tracking-wider ${s.config.text}`}>
                {s.prefix}
              </span>
              <p className="text-sm font-medium text-stone-700">{s.description}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}

export default StrengthCard;
