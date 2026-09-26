/**
 * TopRecommendations — Featured top recommendation + other recommended courses.
 *
 * Shows the #1 recommended course as a featured card, and up to 6 more
 * in a secondary grid.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { Star, BookOpen } from 'lucide-react';
import RecommendationCard from './RecommendationCard';

function FeaturedCourseCard({ course }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-white rounded-xl border-2 border-stone-300 shadow-sm p-6 sm:p-8 mb-8"
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-stone-100 flex items-center justify-center">
          <Star className="w-6 h-6 text-stone-900" />
        </div>
        <div className="flex-1">
          <p className="text-xs font-semibold text-stone-900 uppercase tracking-wider mb-1">
            Top Recommendation
          </p>
          <h3 className="text-xl font-bold text-stone-900 mb-2">{course.course}</h3>
          <p className="text-sm text-stone-500 mb-3">
            Domain: <span className="font-medium text-stone-700">{course.domain}</span>
          </p>
          {course.reason && course.reason.length > 0 && (
            <div className="mt-3 space-y-1.5">
              {course.reason.map((r, i) => (
                <div key={i} className="flex items-start gap-2 text-sm text-stone-600">
                  <span className="text-stone-900 mt-0.5 flex-shrink-0">•</span>
                  <span>{r}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}

export function TopRecommendations({ recommendedCourses = [] }) {
  const topCourse = recommendedCourses[0] || null;
  const additionalCourses = recommendedCourses.slice(1, 7);

  return (
    <section aria-labelledby="recommendations-heading">
      <div className="flex items-center gap-2 mb-5">
        <BookOpen className="w-5 h-5 text-stone-500" aria-hidden="true" />
        <h2 id="recommendations-heading" className="text-lg font-semibold font-display text-stone-900">
          Recommended Courses
        </h2>
      </div>
      
      {/* Featured course */}
      {topCourse && <FeaturedCourseCard course={topCourse} />}
      
      {/* Additional recommended courses */}
      {additionalCourses.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <h3 className="text-md font-semibold text-stone-900 mb-4">More Options to Consider</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {additionalCourses.map((course, i) => (
              <RecommendationCard key={i} course={course} index={i} />
            ))}
          </div>
        </motion.div>
      )}
    </section>
  );
}

export default TopRecommendations;
