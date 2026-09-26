/**
 * RecommendationCard — A single course recommendation card.
 *
 * Shows course name, domain, match score, and reason bullets.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { BookOpen } from 'lucide-react';

export function RecommendationCard({ course, index = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay: 0.08 * index }}
      className="bg-white rounded-xl border border-stone-200 p-5 hover:shadow-md transition-shadow duration-200"
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 w-10 h-10 rounded-xl bg-stone-100 flex items-center justify-center">
          <BookOpen className="w-5 h-5 text-stone-900" />
        </div>
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-semibold text-stone-900 mb-1 truncate">{course.course}</h4>
          <p className="text-xs text-stone-500">{course.domain}</p>
        </div>
      </div>

      {course.reason && course.reason.length > 0 && (
        <div className="mt-3 pl-13 space-y-1">
          {course.reason.slice(0, 3).map((r, i) => (
            <p key={i} className="text-xs text-stone-500 flex items-start gap-1.5">
              <span className="text-stone-900 mt-0.5">•</span>
              <span>{r}</span>
            </p>
          ))}
        </div>
      )}
    </motion.div>
  );
}

export default RecommendationCard;
