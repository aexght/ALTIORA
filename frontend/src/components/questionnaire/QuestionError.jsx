/**
 * QuestionError — Error state with retry capability.
 * Displayed when the questions API fails to load.
 */

import { motion } from 'framer-motion';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '../common/Button';

export function QuestionError({ message, onRetry }) {
  return (
    <motion.div
      className="flex flex-col items-center justify-center py-32 gap-4 text-center px-4"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      role="alert"
    >
      <div className="w-14 h-14 rounded-full bg-red-50 border border-red-100 flex items-center justify-center">
        <AlertTriangle className="w-7 h-7 text-red-600" />
      </div>
      <h2 className="text-lg font-medium font-display text-stone-900 mt-2">
        Failed to load questions
      </h2>
      <p className="text-sm text-stone-500 max-w-md">
        {message || 'Something went wrong while loading the questionnaire. Please try again.'}
      </p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry} className="mt-2">
          <RefreshCw className="w-4 h-4 mr-2" />
          Try Again
        </Button>
      )}
    </motion.div>
  );
}

export default QuestionError;
