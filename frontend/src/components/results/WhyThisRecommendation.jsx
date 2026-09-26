/**
 * WhyThisRecommendation — Descriptive reasoning section.
 *
 * Replaces the flash-card grid with a coherent, human-readable
 * assessment report explaining why the predicted domain was recommended.
 *
 * Uses only data already available in frontend state:
 * - Academic performance (marks, percentages, stream, electives)
 * - Assessment explanations from prediction_explanation
 * - Top domains and course recommendations
 *
 * Does NOT invent psychological claims or fabricate reasons.
 */

import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { Target, Zap } from 'lucide-react';
import { formatPercent } from '../../utils/formatters';

const PREFIXES = ['Excellent', 'Strong', 'Good'];

function parseAcademicStrengths(academic) {
  if (!academic) return [];

  const strengths = [];

  if (academic.class10Percentage && academic.class10Percentage >= 75) {
    strengths.push({ 
      subject: 'Class 10', 
      mark: Number(academic.class10Percentage),
      value: `${academic.class10Percentage}%`, 
      level: academic.class10Percentage >= 85 ? 'Excellent' : 'Strong' 
    });
  }

  if (academic.class12Percentage && academic.class12Percentage >= 75) {
    strengths.push({ 
      subject: 'Class 12', 
      mark: Number(academic.class12Percentage),
      value: `${academic.class12Percentage}%`, 
      level: academic.class12Percentage >= 85 ? 'Excellent' : 'Strong' 
    });
  }

  if (academic.subjectMarks) {
    Object.entries(academic.subjectMarks).forEach(([subject, mark]) => {
      const numMark = Number(mark);
      if (!isNaN(numMark) && numMark >= 75) {
        const name = subject.replace(/_Marks$/, '').replace(/_/g, ' ');
        strengths.push({ 
          subject: name, 
          mark: numMark,
          value: `${mark}%`, 
          level: numMark >= 85 ? 'Excellent' : 'Strong' 
        });
      }
    });
  }

  // Sort descending by numeric mark to ensure highest-scoring subjects appear first
  strengths.sort((a, b) => b.mark - a.mark);

  return strengths;
}

function extractAssessmentThemes(explanations) {
  if (!explanations || explanations.length === 0) return [];

  const themes = [];
  // Backend returns academic factors using these keywords. We filter them out
  // so they are not misclassified as assessment responses.
  const academicKeywords = ['marks', 'performance'];

  explanations.forEach((line) => {
    const lowerLine = line.toLowerCase();
    if (academicKeywords.some(kw => lowerLine.includes(kw))) {
      return;
    }

    for (const prefix of PREFIXES) {
      if (line.startsWith(prefix + ' ')) {
        const description = line.slice(prefix.length + 1);
        themes.push({ prefix, description });
        break;
      }
    }
  });

  return themes;
}

function getDomainDescription(domain) {
  const descriptions = {
    'Engineering & Technology': 'technical problem-solving, analytical thinking, and innovation',
    'Medical & Health Sciences': 'scientific inquiry, patient care, and biological sciences',
    'Life Sciences & Biotechnology': 'research, laboratory work, and biological innovation',
    'Agriculture Environment & Food': 'environmental stewardship, food systems, and sustainability',
    'Commerce & Finance': 'financial analysis, business strategy, and quantitative reasoning',
    'Management & Business Administration': 'leadership, organizational strategy, and decision-making',
    'Arts Humanities & Social Sciences': 'critical analysis, cultural understanding, and communication',
    'Design Media & Creative Arts': 'creative expression, visual communication, and artistic innovation',
    'Law Public Policy & Governance': 'legal reasoning, policy analysis, and public service',
    'Education Teaching & Training': 'knowledge transfer, mentorship, and curriculum development',
  };
  return descriptions[domain] || 'the skills and interests associated with this field';
}

export function WhyThisRecommendation({
  prediction,
  explanations = [],
  _topDomains = [],
  _recommendedCourses = [],
  academic = {},
  _student = {},
}) {
  const { domain, probability, confidence } = prediction || {};

  const academicStrengths = useMemo(() => parseAcademicStrengths(academic), [academic]);
  const assessmentThemes = useMemo(() => extractAssessmentThemes(explanations), [explanations]);
  const domainDesc = getDomainDescription(domain);

  const hasAcademicStrengths = academicStrengths.length > 0;
  const hasAssessmentThemes = assessmentThemes.length > 0;

  // Build the descriptive paragraphs
  const paragraphs = useMemo(() => {
    const parts = [];

    if (!domain) return ['The recommendation could not be determined from the available data.'];

    // Paragraph 1: Academic foundation
    if (hasAcademicStrengths) {
      const topStrengths = academicStrengths.slice(0, 3);
      const strengthText = topStrengths.map(s => `${s.subject} (${s.value})`).join(', ');
      parts.push(
        `The recommendation is based on your academic performance and assessment responses. Your results indicate particular strengths in ${strengthText}, which provides a strong foundation for ${domain}.`
      );
    } else {
      parts.push(
        `The recommendation is based on your academic performance and assessment responses. Your academic profile provides a foundation for ${domain}.`
      );
    }

    // Paragraph 2: Assessment alignment
    if (hasAssessmentThemes) {
      const themeDescriptions = assessmentThemes
        .slice(0, 3)
        .map(t => t.description.toLowerCase())
        .join('; ');
      parts.push(
        `Your assessment responses also show ${themeDescriptions}, which align with the demands commonly associated with ${domainDesc}.`
      );
    } else {
      parts.push(
        `Your assessment responses align with the interests and aptitudes commonly associated with ${domainDesc}.`
      );
    }

    // Paragraph 3: Synthesis
    parts.push(
      `Taken together, these signals make ${domain} a strong current fit for you. The ${confidence.toLowerCase()} confidence (${formatPercent(probability)}) reflects the degree of alignment between your profile and the typical requirements of this domain.`
    );

    return parts;
  }, [domain, confidence, probability, hasAcademicStrengths, hasAssessmentThemes, academicStrengths, assessmentThemes, domainDesc]);

  // Key factors for the optional subsection
  const keyFactors = useMemo(() => {
    const factors = [];

    if (hasAcademicStrengths) {
      const topSubjects = academicStrengths.slice(0, 3).map(s => s.subject).join(', ');
      factors.push({ label: 'Academic strengths', value: topSubjects });
    }

    if (hasAssessmentThemes) {
      const themeLabels = assessmentThemes.slice(0, 3).map(t => t.prefix).join(', ');
      factors.push({ label: 'Assessment strengths', value: themeLabels });
    }

    factors.push({ label: 'Overall alignment', value: `${confidence} (${formatPercent(probability)})` });

    return factors;
  }, [hasAcademicStrengths, hasAssessmentThemes, academicStrengths, assessmentThemes, confidence, probability]);

  if (!domain) return null;

  return (
    <section aria-labelledby="why-heading" className="space-y-6">
      <div className="flex items-center gap-2 mb-5">
        <Target className="w-5 h-5 text-stone-500" aria-hidden="true" />
        <h2 id="why-heading" className="text-lg font-semibold font-display text-stone-900">
          Why This Recommendation?
        </h2>
      </div>

      <div className="bg-white rounded-xl border border-stone-200 p-6 sm:p-8 prose prose-stone max-w-none">
        {paragraphs.map((paragraph, i) => (
          <motion.p
            key={i}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 * i }}
            className="text-stone-700 leading-relaxed text-base mb-4 last:mb-0"
          >
            {paragraph}
          </motion.p>
        ))}

        {/* Optional Key Factors subsection */}
        {keyFactors.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.3 }}
            className="mt-6 pt-6 border-t border-stone-100"
          >
            <h3 className="text-sm font-semibold text-stone-900 mb-4 flex items-center gap-2">
              <Zap className="w-4 h-4 text-stone-500" aria-hidden="true" />
              Key factors
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {keyFactors.map((factor, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.35 + 0.05 * i }}
                  className="bg-stone-50 rounded-xl p-4"
                >
                  <p className="text-xs font-semibold text-stone-500 uppercase tracking-wider mb-1">
                    {factor.label}
                  </p>
                  <p className="text-sm text-stone-800">{factor.value}</p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </section>
  );
}

export default WhyThisRecommendation;