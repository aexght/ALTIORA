/**
 * QuestionnairePage — Main page orchestrating the questionnaire experience.
 *
 * Responsibilities:
 *  1. Fetch questions from GET /api/questions on mount (once).
 *  2. Display loading / error / questionnaire states.
 *  3. Allow user to select assessment length (10, 20, 30, 40).
 *  4. Auto-save every answer to CareerContext (→ localStorage).
 *  5. Preserve current question index across refreshes.
 *  6. Validate all required questions answered before finishing.
 *  7. Submit academic details + answers to POST /predict on finish.
 *  8. On success, save the full response under `prediction` and go to /results.
 *  9. On failure, show a friendly error and stay on the questionnaire.
 *
 * Design: ALTIORA monochrome editorial style.
 */

import { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft, AlertCircle } from 'lucide-react';

import { useCareer } from '../../context/CareerContext';
import { getAssessment } from '../../services/api';
import { submitCareerPrediction, getPredictionErrorMessage } from '../../services/prediction';
import {
  getRecentQuestionIds,
  recordRecentQuestionIds,
} from '../../services/questionHistory';

import { QuestionCard } from '../../components/questionnaire/QuestionCard';
import { QuestionProgress } from '../../components/questionnaire/QuestionProgress';
import { QuestionNavigation } from '../../components/questionnaire/QuestionNavigation';
import { QuestionSidebar } from '../../components/questionnaire/QuestionSidebar';
import { QuestionLoading } from '../../components/questionnaire/QuestionLoading';
import { QuestionError } from '../../components/questionnaire/QuestionError';
import { AssessmentLengthSelector } from '../../components/questionnaire/AssessmentLengthSelector';
import { Button } from '../../components/common/Button';

export function QuestionnairePage() {
  const { state, dispatch } = useCareer();
  const navigate = useNavigate();

  const [assessmentQuestions, setAssessmentQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // ALTIORA: Assessment Length Feature
  const [selectedLength, setSelectedLength] = useState(40);

  const [direction, setDirection] = useState(1); // 1 = forward, -1 = backward
  const [highlightUnanswered, setHighlightUnanswered] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [predictionError, setPredictionError] = useState(null);

  const answers = state.questionnaire?.answers ?? {};
  const currentIndex = state.questionnaire?.currentIndex ?? 0;

  const fetchedRef = useRef(false);
  const submittingRef = useRef(false);

  // ── Fetch a randomized, domain-balanced question selection once ──────
  const fetchAssessment = useCallback(async (length) => {
    setLoading(true);
    setError(null);
    try {
      const recent = getRecentQuestionIds();
      const data = await getAssessment(length, recent);
      setAssessmentQuestions(Array.isArray(data.questions) ? data.questions : []);
    } catch (err) {
      setError(err.message || 'Failed to load assessment');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!fetchedRef.current) {
      fetchedRef.current = true;
      fetchAssessment(selectedLength);
    }
  }, [fetchAssessment, selectedLength]);

  // The selected question set is fixed for the duration of this assessment;
  // navigating between questions must NOT reshuffle it. Changing the length
  // starts a new assessment and fetches a fresh stratified selection.
  const questions = assessmentQuestions;

  const total = questions.length;
  const currentQuestion = questions[currentIndex];
  const isCurrentAnswered = currentQuestion ? answers[currentQuestion.id] !== undefined : false;
  
  // Count only answers for the currently active subset of questions
  const answeredCount = useMemo(() => {
    return questions.filter(q => answers[q.id] !== undefined).length;
  }, [questions, answers]);

  const allAnswered = total > 0 && answeredCount === total;

  // ── Handlers ────────────────────────────────────────────────────
  const handleLengthSelect = useCallback((length) => {
    setSelectedLength(length);
    // Reset index to 0 when changing length to prevent out-of-bounds.
    dispatch({ type: 'SET_QUESTION_INDEX', payload: 0 });
    setHighlightUnanswered(false);
    // A different length is a new assessment: fetch a fresh selection.
    fetchedRef.current = true;
    fetchAssessment(length);
  }, [dispatch, fetchAssessment]);

  const handleSelect = useCallback(
    (questionId, optionId) => {
      dispatch({ type: 'SET_ANSWER', payload: { questionId, optionId } });
      setHighlightUnanswered(false);
    },
    [dispatch]
  );

  const goTo = useCallback(
    (index) => {
      if (isSubmitting) return;
      if (index < 0 || index >= total) return;
      setDirection(index > currentIndex ? 1 : -1);
      dispatch({ type: 'SET_QUESTION_INDEX', payload: index });
    },
    [currentIndex, total, isSubmitting, dispatch]
  );

  const handlePrevious = useCallback(() => {
    if (isSubmitting) return;
    if (currentIndex === 0) {
      navigate('/academic');
      return;
    }
    goTo(currentIndex - 1);
  }, [currentIndex, isSubmitting, goTo, navigate]);

  const handleNext = useCallback(() => {
    goTo(currentIndex + 1);
  }, [currentIndex, goTo]);

  const handleJump = useCallback(
    (index) => {
      goTo(index);
    },
    [goTo]
  );

  const handleJumpToUnanswered = useCallback(() => {
    if (isSubmitting) return;
    const firstUnanswered = questions.findIndex((q) => answers[q.id] === undefined);
    if (firstUnanswered !== -1) {
      setHighlightUnanswered(true);
      goTo(firstUnanswered);
    }
  }, [isSubmitting, questions, answers, goTo]);

  const handleFinish = useCallback(async () => {
    if (!allAnswered) {
      handleJumpToUnanswered();
      return;
    }
    if (submittingRef.current) return;

    setPredictionError(null);
    submittingRef.current = true;
    setIsSubmitting(true);

    try {
      // Create a filtered answers object that only includes answers for the selected length
      const filteredAnswers = {};
      questions.forEach(q => {
        if (answers[q.id] !== undefined) {
          filteredAnswers[q.id] = answers[q.id];
        }
      });

      const data = await submitCareerPrediction(state.academic, filteredAnswers);
      dispatch({ type: 'SET_PREDICTION', payload: data });
      // Anti-repetition: remember which questions were used this assessment so
      // the next one avoids them (separate history, not active answers/state).
      recordRecentQuestionIds(questions.map((q) => q.id));
      navigate('/results');
    } catch (err) {
      setPredictionError(getPredictionErrorMessage(err));
    } finally {
      submittingRef.current = false;
      setIsSubmitting(false);
    }
  }, [allAnswered, handleJumpToUnanswered, state.academic, answers, questions, dispatch, navigate]);

  // ── Loading state ──────────────────────────────────────────────
  if (loading) {
    return (
      <main className="min-h-screen pt-24 pb-16 px-4 sm:px-6 altiora-bg">
        <div className="mx-auto w-full max-w-4xl">
          <QuestionLoading />
        </div>
      </main>
    );
  }

  // ── Error state ────────────────────────────────────────────────
  if (error || assessmentQuestions.length === 0) {
    return (
      <main className="min-h-screen pt-24 pb-16 px-4 sm:px-6 altiora-bg">
        <div className="mx-auto w-full max-w-4xl">
          <QuestionError
            message={error || 'No questions available. Please try again later.'}
            onRetry={() => {
              fetchedRef.current = true;
              fetchAssessment(selectedLength);
            }}
          />
        </div>
      </main>
    );
  }

  // ── Questionnaire ──────────────────────────────────────────────
  return (
    <main className="min-h-screen pt-24 pb-16 px-4 sm:px-6 altiora-bg">
      <motion.div
        className="mx-auto w-full max-w-6xl"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        {/* Header */}
        <div className="mb-8">
          <Button variant="ghost" onClick={() => navigate('/academic')} disabled={isSubmitting} className="mb-4 -ml-2 text-stone-500 hover:text-stone-900">
            <ArrowLeft className="w-4 h-4 mr-1" />
            Back to Academic Details
          </Button>
          <h1 className="text-3xl font-display font-bold text-stone-900 tracking-tight">
            Career Assessment
          </h1>
          <p className="text-stone-500 mt-2 text-sm max-w-2xl">
            Answer the following questions to help us understand your interests and aptitude. 
            There are no right or wrong answers.
          </p>
        </div>

        {/* ALTIORA Assessment Length Selector */}
        <AssessmentLengthSelector 
          selectedCount={selectedLength} 
          onSelect={handleLengthSelect} 
          disabled={isSubmitting} 
        />

        {/* Progress */}
        <QuestionProgress current={currentIndex} total={total} className="mb-8" />

        {/* Main layout: sidebar + card */}
        <div className="flex gap-8 items-start">
          {/* Sidebar — desktop only */}
          <QuestionSidebar
            questions={questions}
            answers={answers}
            currentIndex={currentIndex}
            onJump={handleJump}
          />

          {/* Question area */}
          <div className="flex-1 min-w-0">
            {/* Unanswered warning */}
            {highlightUnanswered && !isCurrentAnswered && (
              <motion.div
                className="mb-4 px-4 py-3 bg-amber-50 border border-amber-200 rounded-xl text-sm text-amber-800 flex items-start gap-2"
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                role="alert"
              >
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>Please answer this question before finishing.</span>
              </motion.div>
            )}

            <QuestionCard
              question={currentQuestion}
              index={currentIndex}
              selectedOptionId={answers[currentQuestion?.id]}
              onSelect={handleSelect}
              direction={direction}
              disabled={isSubmitting}
            />

            <QuestionNavigation
              currentIndex={currentIndex}
              total={total}
              isCurrentAnswered={isCurrentAnswered}
              allAnswered={allAnswered}
              onPrevious={handlePrevious}
              onNext={handleNext}
              onFinish={handleFinish}
              onJumpToUnanswered={handleJumpToUnanswered}
              isSubmitting={isSubmitting}
            />

            {/* Prediction error */}
            {predictionError && (
              <motion.div
                className="mt-4 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 flex items-start gap-2"
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                role="alert"
              >
                <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
                <span>{predictionError}</span>
              </motion.div>
            )}

            {/* Mobile question indicator (compact) */}
            <div className="lg:hidden mt-6 flex items-center justify-center">
              <p className="text-xs text-stone-400">
                {answeredCount} of {total} answered
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </main>
  );
}

export default QuestionnairePage;
