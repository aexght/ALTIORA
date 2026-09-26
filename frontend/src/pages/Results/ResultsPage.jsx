/**
 * ResultsPage — Phase 6B + 6C Results Dashboard.
 *
 * Reads the prediction object from CareerContext (stored by Phase 6A)
 * and renders it using decomposed result components.
 *
 * Response shape (from POST /predict, stored as state.prediction):
 * {
 *   prediction: { domain, probability, confidence },
 *   top_domains: [{ domain, probability }, ...],
 *   recommended_courses: [{ course, domain, score, reason: [...] }, ...],
 *   prediction_explanation: [string, ...]
 * }
 *
 * Phase 6C additions:
 *   - PredictionInsights (why this recommendation — numbered insight cards)
 *   - StrengthCard (strength badges parsed from explanation prefixes)
 *   - PredictionFacts (prediction metadata fact sheet)
 *   - AssessmentRecap (summary of student inputs, no questionnaire answers)
 *   - Enhanced ConfidenceCard (confidence explanation + probability bar)
 */

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useCareer } from '../../context/CareerContext';
import { PageContainer } from '../../components/layout/PageContainer';
import { Button } from '../../components/common/Button';

import ResultHero from '../../components/results/ResultHero';
import TopRecommendations from '../../components/results/TopRecommendations';
import WhyThisRecommendation from '../../components/results/WhyThisRecommendation';
import StrengthCard from '../../components/results/StrengthCard';
import PredictionFacts from '../../components/results/PredictionFacts';
import AssessmentRecap from '../../components/results/AssessmentRecap';
import RecommendedColleges from '../../components/results/RecommendedColleges';
import EmptyState from '../../components/results/EmptyState';

import { RotateCcw, Download } from 'lucide-react';
import { generateCareerReportPDF } from '../../services/pdfGenerator';

export default function ResultsPage() {
  const { state, dispatch } = useCareer();
  const navigate = useNavigate();
  const predictionData = state?.prediction;
  
  const [isGenerating, setIsGenerating] = useState(false);
  const [pdfError, setPdfError] = useState(null);

  // Empty state — no prediction available
  if (!predictionData) {
    return (
      <PageContainer maxWidth="lg">
        <EmptyState />
      </PageContainer>
    );
  }

  // Destructure the response
  const {
    prediction,
    top_domains: topDomains = [],
    recommended_courses: recommendedCourses = [],
    prediction_explanation: explanations = [],
    recommended_colleges: recommendedColleges = [],
    assessment_profile: _assessmentProfile = [],
    reasoning: _reasoning = {},
  } = predictionData;

  // Safety check — prediction sub-object must exist
  if (!prediction || !prediction.domain) {
    return (
      <PageContainer maxWidth="lg">
        <EmptyState />
      </PageContainer>
    );
  }

  const handleRetake = () => {
    dispatch({ type: 'RESET' });
    dispatch({ type: 'START_ASSESSMENT' });
    navigate('/student');
  };

  const handleDownloadReport = async () => {
    if (isGenerating) return;
    setIsGenerating(true);
    setPdfError(null);
    try {
      await generateCareerReportPDF(state);
    } catch (err) {
      setPdfError("We couldn't generate the report right now. Your results are still available above. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <PageContainer maxWidth="xl">
      <div className="max-w-4xl mx-auto w-full">

        {/* Section 1: Hero — Predicted domain + confidence */}
        <ResultHero prediction={prediction} />

        {/* Single-column vertical layout */}
        <div className="space-y-12 mt-8">

          {/* Strength Highlights (parsed from explanations) */}
          <StrengthCard explanations={explanations} />

          {/* Top recommendation and additional courses */}
          <TopRecommendations recommendedCourses={recommendedCourses} />

          {/* Why This Recommendation — descriptive reasoning section */}
          <WhyThisRecommendation
            prediction={prediction}
            explanations={explanations}
            topDomains={topDomains}
            recommendedCourses={recommendedCourses}
            academic={state?.academic}
            student={state?.student}
            preferences={state?.preferences}
          />

          {/* Recommended Colleges */}
          <RecommendedColleges colleges={recommendedColleges} />

          {/* Prediction Facts */}
          <PredictionFacts
            prediction={prediction}
            topDomainsCount={topDomains.length}
          />

          {/* Assessment Recap */}
          <AssessmentRecap />

          {/* Action buttons */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="flex flex-col pt-6 pb-4 border-t border-stone-100"
          >
            {pdfError && (
              <div className="mb-4 text-red-600 text-sm font-medium">
                {pdfError}
              </div>
            )}
            
            <div className="flex flex-col sm:flex-row items-center gap-4">
              <Button
                variant="outline"
                onClick={handleDownloadReport}
                disabled={isGenerating}
                className="flex items-center gap-2 border-stone-200 hover:bg-stone-50 text-stone-700 w-full sm:w-auto justify-center"
              >
                <Download className="w-4 h-4" />
                {isGenerating ? 'Generating PDF...' : 'Download Career Report'}
              </Button>
              <Button
                variant="ghost"
                onClick={handleRetake}
                className="flex items-center gap-2 w-full sm:w-auto justify-center"
              >
                <RotateCcw className="w-4 h-4" />
                Retake Assessment
              </Button>
              <Button
                variant="primary"
                onClick={() => navigate('/')}
                className="w-full sm:w-auto justify-center"
              >
                Back to Home
              </Button>
            </div>
            <p className="text-stone-400 text-xs mt-3 text-center sm:text-left">
              Get your personalized ALTIORA career report as a free PDF.
            </p>
          </motion.div>
        </div>
      </div>
    </PageContainer>
  );
}
