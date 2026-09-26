/**
 * AcademicSummaryCard — Live read-only summary of academic form progress.
 *
 * Calculates completion from core + selected elective subjects,
 * displaying stream, elective count, subjects filled, and a
 * completion bar with a "Ready" / "Incomplete" indicator.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle, BookOpen, GraduationCap, BarChart } from 'lucide-react';
import { STREAM_SUBJECTS, SUBJECT_MARK_KEY } from '../../utils/constants';

export const AcademicSummaryCard = ({ academic, computedClass12 }) => {
  const {
    class10Percentage,
    stream,
    electives = [],
    subjectMarks = {},
  } = academic;

  // Determine expected mark fields from core + selected electives
  const config = STREAM_SUBJECTS[stream];
  const coreSubjects = config ? config.core : [];
  const allSubjects = [...coreSubjects, ...electives];
  const expectedMarkKeys = allSubjects.map((s) => SUBJECT_MARK_KEY[s]).filter(Boolean);
  const subjectsLoaded = expectedMarkKeys.length;

  // Count filled marks
  const filledSubjects = expectedMarkKeys.filter((key) => {
    const val = subjectMarks[key];
    return val !== undefined && val !== null && String(val).trim() !== '';
  }).length;

  // Completion: 10th + 12th + stream + ≥1 elective + all marks
  const hasElective = electives.length >= 1;
  let totalRequired = 3 + subjectsLoaded; // 10th, 12th, stream + marks
  if (stream) totalRequired += 1; // elective selection step
  let totalFilled = 0;
  if (class10Percentage) totalFilled++;
  if (computedClass12 !== '') totalFilled++;
  if (stream) totalFilled++;
  if (hasElective) totalFilled++;
  totalFilled += filledSubjects;

  const completionPercentage = totalRequired > 0
    ? Math.min(Math.round((totalFilled / totalRequired) * 100), 100)
    : 0;

  const isComplete = completionPercentage === 100;

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white rounded-xl border border-stone-200 shadow-card p-6 sticky top-24"
    >
      <h3 className="text-lg font-bold text-stone-900 mb-4 flex items-center gap-2">
        <BarChart className="w-5 h-5 text-stone-900" />
        Academic Summary
      </h3>

      <div className="space-y-4 mb-6">
        <div className="flex justify-between items-center text-sm">
          <span className="text-stone-500 flex items-center gap-2">
            <GraduationCap className="w-4 h-4" /> Class 10
          </span>
          <span className="font-medium text-stone-900">{class10Percentage ? `${class10Percentage}%` : '--'}</span>
        </div>

        <div className="flex justify-between items-center text-sm">
          <span className="text-stone-500 flex items-center gap-2">
            <GraduationCap className="w-4 h-4" /> Class 12
          </span>
          <span className="font-medium text-stone-900">{computedClass12 !== '' ? `${computedClass12}%` : '--'}</span>
        </div>

        <div className="flex justify-between items-center text-sm">
          <span className="text-stone-500">Stream</span>
          <span className="font-medium text-stone-900">{stream || '--'}</span>
        </div>

        <div className="flex justify-between items-center text-sm">
          <span className="text-stone-500">Electives</span>
          <span className="font-medium text-stone-900">
            {electives.length > 0 ? electives.join(', ') : '--'}
          </span>
        </div>

        <div className="flex justify-between items-center text-sm border-t border-stone-100 pt-4">
          <span className="text-stone-500 flex items-center gap-2">
            <BookOpen className="w-4 h-4" /> Marks Filled
          </span>
          <span className="font-medium text-stone-900">
            {subjectsLoaded > 0 ? `${filledSubjects} / ${subjectsLoaded}` : '0'}
          </span>
        </div>
      </div>

      <div className="mb-2 flex justify-between items-center text-xs font-semibold">
        <span className="text-stone-500">Completion</span>
        <span className="text-stone-900">{completionPercentage}%</span>
      </div>
      <div className="h-2 bg-stone-100 rounded-full overflow-hidden mb-4">
        <div
          className="h-full bg-stone-900 transition-all duration-500"
          style={{ width: `${completionPercentage}%` }}
        />
      </div>

      <div className={`flex items-center gap-2 text-sm font-medium ${isComplete ? 'text-stone-900' : 'text-stone-400'}`}>
        {isComplete ? (
          <>
            <CheckCircle2 className="w-4 h-4" /> Ready for Next Step
          </>
        ) : (
          <>
            <Circle className="w-4 h-4" /> Incomplete
          </>
        )}
      </div>
    </motion.div>
  );
};

export default AcademicSummaryCard;
