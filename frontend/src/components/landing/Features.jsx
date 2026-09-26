import React from 'react';
import { Sparkles, MessageSquareText, BookOpen, Building2 } from 'lucide-react';
import { motion } from 'framer-motion';

/**
 * Features Section Component
 * @returns {React.JSX.Element}
 */
export const Features = () => {
  const features = [
    {
      id: 1,
      icon: Sparkles,
      title: 'AI Career Prediction',
      description: 'Uses machine learning to identify the career domains that best match your academic profile and interests.',
    },
    {
      id: 2,
      icon: MessageSquareText,
      title: 'Explainable Recommendations',
      description: 'Transparent reasoning behind every recommendation — no black-box decisions.',
    },
    {
      id: 3,
      icon: BookOpen,
      title: 'Course Discovery',
      description: 'Find undergraduate courses that align with your strengths, interests, and career goals.',
    },
    {
      id: 4,
      icon: Building2,
      title: 'College Explorer',
      description: 'Browse colleges filtered by location, type, and your predicted career domain.',
    },
  ];

  return (
    <section className="py-20 lg:py-24 max-w-4xl mx-auto px-6 altiora-bg">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-stone-900 mb-4 font-display">What You Get</h2>
        <p className="text-lg text-stone-600 max-w-2xl mx-auto">
          Powerful tools designed to guide your career journey.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <motion.div
              key={feature.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1, duration: 0.5 }}
              className="bg-white rounded-xl border border-stone-200 p-6 shadow-card hover:shadow-card-hover transition-all duration-300"
            >
              <div className="w-12 h-12 rounded-lg bg-stone-100 flex items-center justify-center mb-4">
                <Icon className="w-6 h-6 text-stone-900" />
              </div>
              <h3 className="text-base font-semibold text-stone-900 mt-4">{feature.title}</h3>
              <p className="text-sm text-stone-600 mt-2 leading-relaxed">{feature.description}</p>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
};

export default Features;
