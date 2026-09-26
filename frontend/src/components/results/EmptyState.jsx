/**
 * EmptyState — Shown when no prediction data is available.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FileQuestion } from 'lucide-react';
import { Button } from '../common/Button';

export function EmptyState() {
  const navigate = useNavigate();

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col items-center justify-center text-center py-20"
    >
      <div className="w-16 h-16 rounded-xl bg-stone-100 flex items-center justify-center mb-6">
        <FileQuestion className="w-8 h-8 text-stone-400" />
      </div>

      <h2 className="text-xl font-bold font-display text-stone-900 mb-2">
        No Assessment Completed
      </h2>
      <p className="text-stone-500 mb-8 max-w-md">
        Complete the career assessment questionnaire to receive your personalised prediction and course recommendations.
      </p>

      <Button size="lg" onClick={() => navigate('/')}>
        Start Career Assessment
      </Button>
    </motion.div>
  );
}

export default EmptyState;
