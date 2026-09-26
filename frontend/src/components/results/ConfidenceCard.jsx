/**
 * ConfidenceCard — Sidebar card displaying confidence metrics.
 *
 * Shows prediction confidence, probability, visual gauge,
 * quick stats, and a static confidence explanation.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Shield, BarChart3, Info } from 'lucide-react';
import { formatPercent } from '../../utils/formatters';

const CONFIDENCE_COLORS = {
  'Very High': { ring: 'text-emerald-600', bg: 'bg-emerald-50', text: 'text-emerald-700' },
  'High': { ring: 'text-blue-600', bg: 'bg-blue-50', text: 'text-blue-700' },
  'Moderate': { ring: 'text-stone-600', bg: 'bg-stone-50', text: 'text-stone-700' },
  'Low': { ring: 'text-stone-500', bg: 'bg-stone-50', text: 'text-stone-600' },
  'Very Low': { ring: 'text-stone-400', bg: 'bg-stone-50', text: 'text-stone-500' },
};

const CONFIDENCE_EXPLANATIONS = {
  'Very High': 'The model is very confident this domain strongly aligns with your academic profile and aptitude scores.',
  'High': 'The model found a strong alignment between your profile and this career domain.',
  'Moderate': 'The model found a reasonable match, but other domains also scored competitively.',
  'Low': 'The model detected some alignment, but the prediction may benefit from additional information.',
  'Very Low': 'The model was uncertain. Consider exploring multiple career options.',
};

export function ConfidenceCard({ prediction, topDomains = [] }) {
  const { probability, confidence } = prediction;
  const colors = CONFIDENCE_COLORS[confidence] || CONFIDENCE_COLORS['Moderate'];
  const topCount = Math.min(topDomains.length, 3);
  const explanation = CONFIDENCE_EXPLANATIONS[confidence] || CONFIDENCE_EXPLANATIONS['Moderate'];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="bg-white rounded-xl shadow-card p-6 sticky top-24"
    >
      {/* Confidence gauge */}
      <div className="text-center mb-6">
        <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-stone-50 mb-3">
          <Shield className={`w-7 h-7 ${colors.ring}`} aria-hidden="true" />
        </div>
        <p className="text-3xl font-bold text-stone-900">{formatPercent(probability)}</p>
        <span className={`inline-block mt-1.5 text-xs font-semibold px-3 py-1 rounded-full ${colors.bg} ${colors.text}`}>
          {confidence}
        </span>
      </div>

      {/* Confidence explanation */}
      <div className="flex items-start gap-2 mb-5 p-3 rounded-xl bg-stone-50">
        <Info className="w-4 h-4 text-stone-400 flex-shrink-0 mt-0.5" aria-hidden="true" />
        <p className="text-xs text-stone-500 leading-relaxed">{explanation}</p>
      </div>

      {/* Probability bar */}
      <div className="mb-5">
        <div className="flex justify-between text-xs font-medium text-stone-400 mb-1.5">
          <span>Match Score</span>
          <span>{formatPercent(probability)}</span>
        </div>
        <div className="h-2 bg-stone-100 rounded-full overflow-hidden">
          <motion.div
            className={`h-full rounded-full bg-stone-900`}
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(Number(probability), 100)}%` }}
            transition={{ duration: 0.8, delay: 0.5 }}
          />
        </div>
      </div>

      {/* Divider */}
      <div className="h-px bg-stone-100 mb-5" />

      {/* Quick stats */}
      <div className="space-y-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-stone-500 flex items-center gap-2">
            <BarChart3 className="w-4 h-4" aria-hidden="true" /> Domains Analysed
          </span>
          <span className="font-semibold text-stone-900">{topDomains.length}</span>
        </div>
        {topCount > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-stone-500">Top Matches</span>
            <span className="font-semibold text-stone-900">{topCount}</span>
          </div>
        )}
      </div>
    </motion.div>
  );
}

export default ConfidenceCard;
