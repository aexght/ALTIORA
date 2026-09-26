/**
 * AcademicDetailsPage — Step 2 of the assessment.
 *
 * Collects academic percentages, stream, elective subjects, and subject marks.
 * The frontend sends { stream, electives, subjectMarks } — the backend
 * derives the ML subject combination via subject_combination_mapper.py.
 *
 * The SubjectCombination dropdown has been replaced with a dynamic
 * ElectiveSelector (card-based UI).
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useCareer } from '../../context/CareerContext';
import { PageContainer } from '../../components/layout/PageContainer';
import { ProgressBar } from '../../components/layout/ProgressBar';
import { Badge } from '../../components/common/Badge';
import { StudentNavigation } from '../../components/student/StudentNavigation';
import { validateForm, validateClass10Percentage, validateMarks } from '../../utils/validators';
import { STREAM_SUBJECTS, SUBJECT_MARK_KEY, MAX_ELECTIVES } from '../../utils/constants';

import AcademicPerformance from '../../components/academic/AcademicPerformance';
import StreamSelection from '../../components/academic/StreamSelection';
import ElectiveSelector from '../../components/academic/ElectiveSelector';
import SubjectMarks from '../../components/academic/SubjectMarks';
import AcademicSummaryCard from '../../components/academic/AcademicSummaryCard';

export default function AcademicDetailsPage() {
  const { state, dispatch } = useCareer();
  const navigate = useNavigate();
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const academic = state?.academic || {};
  const stream = academic.stream || '';
  const electives = academic.electives || [];
  const subjectMarks = academic.subjectMarks || {};

  // Derive which mark keys are required (core + selected electives)
  const config = STREAM_SUBJECTS[stream];
  const coreSubjects = config ? config.core : [];
  const allSubjects = [...coreSubjects, ...electives];
  const requiredMarkKeys = allSubjects.map((s) => SUBJECT_MARK_KEY[s]).filter(Boolean);

  // ── Build validation rules dynamically ─────────────────────────
  const validationRules = {
    class10Percentage: validateClass10Percentage,
    stream: (v) => (!v ? 'Stream is required' : null),
    electives: () => {
      if (!stream) return null; // don't validate until stream is chosen
      if (electives.length < 1) return 'Select at least one elective subject.';
      if (electives.length > MAX_ELECTIVES) return `You can select up to ${MAX_ELECTIVES} elective subjects.`;
      return null;
    },
  };

  // Add mark validation for every required subject
  requiredMarkKeys.forEach((markKey) => {
    validationRules[markKey] = (v) => validateMarks(v, 'Marks');
  });

  // Flatten data for validation
  const validationData = {
    class10Percentage: academic.class10Percentage,
    class12Percentage: academic.class12Percentage,
    stream,
    electives,
    ...subjectMarks,
  };

  const { isValid, errors: currentErrors } = validateForm(validationData, validationRules);

  // ── Handlers ───────────────────────────────────────────────────

  const handleChange = (name, value) => {
    let updates = { [name]: value };

    // Reset dependents when stream changes
    if (name === 'stream' && value !== stream) {
      updates.electives = [];
      updates.subjectMarks = {};
      // Clear touched for all mark-related and elective fields
      setTouched((prev) => {
        const next = { ...prev };
        delete next.electives;
        requiredMarkKeys.forEach((f) => delete next[f]);
        return next;
      });
    }

    dispatch({ type: 'SET_ACADEMIC', payload: updates });
    setTouched((prev) => ({ ...prev, [name]: true }));
  };

  const handleElectivesChange = (newElectives) => {
    // Find removed electives and clean their marks
    const removed = electives.filter((e) => !newElectives.includes(e));
    const cleanedMarks = { ...subjectMarks };
    removed.forEach((e) => {
      const key = SUBJECT_MARK_KEY[e];
      if (key) delete cleanedMarks[key];
    });

    // Clear touched state for removed elective mark fields
    if (removed.length > 0) {
      setTouched((prev) => {
        const next = { ...prev };
        removed.forEach((e) => {
          const key = SUBJECT_MARK_KEY[e];
          if (key) delete next[key];
        });
        return next;
      });
    }

    dispatch({
      type: 'SET_ACADEMIC',
      payload: { electives: newElectives, subjectMarks: cleanedMarks },
    });
    setTouched((prev) => ({ ...prev, electives: true }));
  };

  const handleMarkChange = (markKey, value) => {
    dispatch({
      type: 'SET_ACADEMIC',
      payload: {
        subjectMarks: { ...subjectMarks, [markKey]: value },
      },
    });
    setTouched((prev) => ({ ...prev, [markKey]: true }));
  };

  const handleBlur = (name, value) => {
    if (typeof value === 'string' && name === 'class10Percentage') {
      dispatch({ type: 'SET_ACADEMIC', payload: { [name]: value.trim() } });
    }
  };

  const handleMarkBlur = (markKey, value) => {
    if (typeof value === 'string') {
      dispatch({
        type: 'SET_ACADEMIC',
        payload: { subjectMarks: { ...subjectMarks, [markKey]: value.trim() } },
      });
    }
  };

  // ── Compute Class 12 Percentage ────────────────────────────────
  const filledMarks = requiredMarkKeys.filter(k => subjectMarks[k] !== undefined && subjectMarks[k] !== '');
  const isClass12Complete = requiredMarkKeys.length > 0 && filledMarks.length === requiredMarkKeys.length;
  const computedClass12Percentage = isClass12Complete
    ? (requiredMarkKeys.reduce((sum, k) => sum + Number(subjectMarks[k]), 0) / requiredMarkKeys.length).toFixed(1)
    : '';

  const handleSubmit = (e) => {
    e?.preventDefault();

    // Mark all as touched
    const allTouched = Object.keys(validationRules).reduce((acc, key) => {
      acc[key] = true;
      return acc;
    }, {});
    setTouched(allTouched);

    if (isValid) {
      // If the user hasn't filled all subjects, they shouldn't be able to proceed. 
      // But validateMarks already handles this. We just ensure we send a valid number.
      setIsSubmitting(true);

      // Normalize numeric values before dispatch
      const normalizedPayload = {
        class10Percentage: Number(academic.class10Percentage),
        class12Percentage: Number(computedClass12Percentage),
        stream,
        electives,
        subjectMarks: Object.entries(subjectMarks).reduce((acc, [k, v]) => {
          acc[k] = Number(v);
          return acc;
        }, {}),
      };

      dispatch({ type: 'SET_ACADEMIC', payload: normalizedPayload });
      navigate('/questionnaire');
    } else {
      // Focus first invalid field
      const firstInvalid = Object.keys(currentErrors)[0];
      if (firstInvalid) {
        const el = document.getElementsByName(firstInvalid)[0];
        if (el) el.focus();
      }
    }
  };

  // Only show errors for touched fields
  const displayErrors = Object.keys(currentErrors).reduce((acc, key) => {
    if (touched[key]) acc[key] = currentErrors[key];
    return acc;
  }, {});

  return (
    <PageContainer maxWidth="xl">
      <div className="max-w-6xl mx-auto w-full">

        {/* Header */}
        <div className="mb-8">
          <Badge variant="primary" className="mb-4">Step 2 of 4</Badge>
          <h1 className="text-3xl sm:text-4xl font-bold text-stone-900 mb-3">Academic Details</h1>
          <p className="text-stone-600 mb-8 text-lg max-w-2xl">
            Provide your academic performance and subject choices to help the AI model align courses with your background.
          </p>
          <div className="max-w-3xl">
            <ProgressBar current={2} total={4} label="50%" />
          </div>
        </div>

        {/* 2-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

          {/* Main Form Column (8 cols) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="lg:col-span-8 bg-white rounded-xl border border-stone-200 shadow-card p-6 sm:p-10"
          >
            <form onSubmit={handleSubmit} noValidate>

              <AcademicPerformance
                values={academic}
                errors={displayErrors}
                onChange={handleChange}
                onBlur={handleBlur}
                computedClass12={computedClass12Percentage}
                isClass12Complete={isClass12Complete}
              />

              <div className="h-px bg-stone-100 w-full my-8" />

              <StreamSelection
                values={academic}
                errors={displayErrors}
                onChange={handleChange}
              />

              {stream && (
                <ElectiveSelector
                  stream={stream}
                  electives={electives}
                  onChange={handleElectivesChange}
                  error={displayErrors.electives}
                />
              )}

              <SubjectMarks
                values={academic}
                errors={displayErrors}
                onMarkChange={handleMarkChange}
                onBlur={handleMarkBlur}
              />

              <button type="submit" className="hidden" aria-hidden="true" />

              <StudentNavigation
                onBack={() => navigate('/student')}
                onContinue={handleSubmit}
                isValid={isValid}
                isSubmitting={isSubmitting}
              />
            </form>
          </motion.div>

          {/* Summary Card Column (4 cols) */}
          <div className="lg:col-span-4">
            <AcademicSummaryCard academic={academic} computedClass12={computedClass12Percentage} />
          </div>

        </div>
      </div>
    </PageContainer>
  );
}
