/**
 * AssessmentRecap — Summary of the student's assessment inputs.
 *
 * Reads student and academic from CareerContext.
 * Displays a clean summary grid. Does NOT expose questionnaire answers.
 * Only renders fields that have non-empty values.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { ClipboardList } from 'lucide-react';
import { useCareer } from '../../context/CareerContext';

function RecapRow({ label, value }) {
  if (!value || (Array.isArray(value) && value.length === 0)) return null;
  const display = Array.isArray(value) ? value.join(', ') : String(value);

  return (
    <div className="flex items-center justify-between py-3 px-5">
      <span className="text-sm text-stone-500">{label}</span>
      <span className="text-sm font-medium text-stone-900 text-right max-w-[60%] truncate">
        {display}
      </span>
    </div>
  );
}

export function AssessmentRecap() {
  const { state } = useCareer();
  const { student = {}, academic = {} } = state || {};

  // Build recap entries — only include fields that have values
  const entries = [
    { label: 'Name', value: student.name },
    { label: 'Age', value: student.age },
    { label: 'Gender', value: student.gender },
    { label: 'State', value: student.state },
    { label: 'Category', value: student.category },
    { label: 'Class 10', value: academic.class10Percentage ? `${academic.class10Percentage}%` : '' },
    { label: 'Class 12', value: academic.class12Percentage ? `${academic.class12Percentage}%` : '' },
    { label: 'Stream', value: academic.stream },
    { label: 'Electives', value: academic.electives },
  ].filter((e) => {
    if (!e.value) return false;
    if (Array.isArray(e.value) && e.value.length === 0) return false;
    return true;
  });

  if (entries.length === 0) return null;

  return (
    <section aria-labelledby="recap-heading">
      <div className="flex items-center gap-2 mb-5">
        <ClipboardList className="w-5 h-5 text-stone-400" aria-hidden="true" />
        <h2 id="recap-heading" className="text-lg font-semibold font-display text-stone-900">
          Assessment Recap
        </h2>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.35, delay: 0.15 }}
        className="bg-white rounded-xl border border-stone-200 divide-y divide-stone-100"
      >
        {entries.map((e, i) => (
          <RecapRow key={i} label={e.label} value={e.value} />
        ))}
      </motion.div>
    </section>
  );
}

export default AssessmentRecap;
