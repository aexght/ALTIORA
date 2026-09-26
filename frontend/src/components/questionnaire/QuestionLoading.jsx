/**
 * QuestionLoading — Full-page loading state while questions are being fetched.
 * Reuses the existing LoadingSpinner component.
 */

import { motion } from 'framer-motion';
import { LoadingSpinner } from '../layout/LoadingSpinner';

export function QuestionLoading() {
  return (
    <motion.div
      className="flex flex-col items-center justify-center py-32 gap-4"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
      role="status"
      aria-label="Loading questions"
    >
      <LoadingSpinner size="lg" />
      <p className="text-sm text-stone-500 mt-2">Loading questions…</p>
    </motion.div>
  );
}

export default QuestionLoading;
