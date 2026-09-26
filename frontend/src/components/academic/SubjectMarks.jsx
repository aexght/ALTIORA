/**
 * SubjectMarks — Renders mark inputs for core + selected elective subjects.
 *
 * Core subjects are always shown. Elective marks appear only when selected,
 * with a Framer Motion fade/slide animation.
 * All subject names are resolved to backend mark keys via SUBJECT_MARK_KEY.
 */

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import FormSection from '../forms/FormSection';
import { Input } from '../common/Input';
import { STREAM_SUBJECTS, SUBJECT_MARK_KEY } from '../../utils/constants';

export const SubjectMarks = ({ values, errors, onMarkChange, onBlur }) => {
  const { stream, electives = [], subjectMarks = {} } = values;

  const config = STREAM_SUBJECTS[stream];
  if (!config) return null;

  // Build the ordered list: core subjects first, then selected electives
  const coreSubjects = config.core;
  const selectedElectives = electives;
  const allSubjects = [...coreSubjects, ...selectedElectives];

  if (allSubjects.length === 0) return null;

  return (
    <FormSection title="Subject Marks" description="Enter your marks out of 100 for each subject.">

      {/* Core subjects — always visible */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {coreSubjects.map((subject) => {
          const markKey = SUBJECT_MARK_KEY[subject];
          if (!markKey) return null;
          return (
            <Input
              key={markKey}
              id={`mark-input-${markKey}`}
              name={markKey}
              label={subject}
              type="number"
              min="0"
              max="100"
              placeholder="0–100"
              value={subjectMarks[markKey] ?? ''}
              error={errors?.[markKey]}
              onChange={(e) => onMarkChange(markKey, e.target.value)}
              onBlur={(e) => onBlur && onBlur(markKey, e.target.value)}
            />
          );
        })}
      </div>

      {/* Elective subjects — animated in/out */}
      <AnimatePresence>
        {selectedElectives.length > 0 && (
          <motion.div
            key="elective-marks"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="border-t border-stone-100 pt-4 mt-2">
              <p className="text-xs font-medium text-stone-400 uppercase tracking-wider mb-3">
                Elective Subjects
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <AnimatePresence>
                  {selectedElectives.map((subject) => {
                    const markKey = SUBJECT_MARK_KEY[subject];
                    if (!markKey) return null;
                    return (
                      <motion.div
                        key={markKey}
                        initial={{ opacity: 0, y: 12 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -12 }}
                        transition={{ duration: 0.25 }}
                      >
                        <Input
                          id={`mark-input-${markKey}`}
                          name={markKey}
                          label={subject}
                          type="number"
                          min="0"
                          max="100"
                          placeholder="0–100"
                          value={subjectMarks[markKey] ?? ''}
                          error={errors?.[markKey]}
                          onChange={(e) => onMarkChange(markKey, e.target.value)}
                          onBlur={(e) => onBlur && onBlur(markKey, e.target.value)}
                        />
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </FormSection>
  );
};

export default SubjectMarks;
