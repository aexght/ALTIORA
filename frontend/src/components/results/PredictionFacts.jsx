/**
 * PredictionFacts — Quick facts panel about the prediction.
 *
 * Displays:
 *   - Model confidence label
 *   - Predicted domain
 *   - Number of evaluated domains (from top_domains length)
 *   - Prediction timestamp (frontend-only, captured on render)
 *
 * Only fields that exist are shown.
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Info, Calendar, Target, Shield } from 'lucide-react';
import { formatPercent } from '../../utils/formatters';

export function PredictionFacts({ prediction, topDomainsCount: _topDomainsCount = 0 }) {
  const timestamp = useMemo(() => {
    return new Date().toLocaleString('en-IN', {
      dateStyle: 'medium',
      timeStyle: 'short',
    });
  }, []);

  if (!prediction) return null;

  const { domain, probability, confidence } = prediction;

  const facts = [
    { icon: Target, label: 'Predicted Domain', value: domain },
    { icon: Shield, label: 'Confidence', value: `${confidence} (${formatPercent(probability)})` },
    { icon: Calendar, label: 'Prediction Date', value: timestamp },
  ].filter(Boolean);

  return (
    <section aria-labelledby="facts-heading">
      <div className="flex items-center gap-2 mb-5">
        <Info className="w-5 h-5 text-stone-400" aria-hidden="true" />
        <h2 id="facts-heading" className="text-lg font-semibold font-display text-stone-900">
          Prediction Facts
        </h2>
      </div>

      <div className="bg-white rounded-xl border border-stone-200 divide-y divide-stone-100">
        {facts.map((fact, i) => {
          const Icon = fact.icon;
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.08 * i }}
              className="flex items-center gap-3 px-5 py-4"
            >
              <Icon className="w-4 h-4 text-stone-400 flex-shrink-0" aria-hidden="true" />
              <span className="text-sm text-stone-500 flex-1">{fact.label}</span>
              <span className="text-sm font-semibold text-stone-900 text-right">{fact.value}</span>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}

export default PredictionFacts;
