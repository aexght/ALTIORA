import React from 'react';
import { GraduationCap, ClipboardList, Brain, Compass } from 'lucide-react';
import { motion } from 'framer-motion';

/**
 * HowItWorks Section Component
 * @returns {React.JSX.Element}
 */
export const HowItWorks = () => {
  const steps = [
    {
      id: 1,
      icon: GraduationCap,
      title: 'Academic Details',
      description: 'Provide your academic information including marks and stream.',
    },
    {
      id: 2,
      icon: ClipboardList,
      title: 'Career Assessment',
      description: 'Answer 40 carefully designed questions about your interests and aptitude.',
    },
    {
      id: 3,
      icon: Brain,
      title: 'AI Analysis',
      description: 'Our machine learning model evaluates your complete profile.',
    },
    {
      id: 4,
      icon: Compass,
      title: 'Recommendations',
      description: 'Receive personalised career domains, courses, and colleges.',
    },
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.12,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
  };

  return (
    <section id="how-it-works" className="py-20 lg:py-24 max-w-7xl mx-auto px-6 altiora-bg">
      <div className="text-center mb-16">
        <h2 className="text-3xl md:text-4xl font-bold text-stone-900 mb-4 font-display">How It Works</h2>
        <p className="text-lg text-stone-600 max-w-2xl mx-auto">
          Complete four simple steps to receive your personalised recommendations.
        </p>
      </div>

      <motion.div
        className="relative"
        variants={containerVariants}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
      >
        {/* Mobile vertical line */}
        <div className="absolute left-6 top-8 bottom-8 w-px border-l-2 border-dashed border-stone-200 md:hidden" />

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 md:gap-4 relative">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <motion.div key={step.id} variants={itemVariants} className="relative flex md:flex-col md:items-center pl-16 md:pl-0">
                {/* Connector for desktop */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-3.5 left-1/2 w-full h-px border-t-2 border-dashed border-stone-200 z-0" />
                )}
                
                <div className="absolute left-0 top-0 md:relative md:mb-5 z-10 flex flex-col items-center">
                  <div className="w-7 h-7 bg-stone-900 text-white text-xs font-semibold flex items-center justify-center rounded-md mb-4 shadow-sm relative">
                    {step.id}
                  </div>
                  <Icon className="w-10 h-10 text-stone-900 hidden md:block" />
                </div>
                
                <div className="md:mt-0 md:text-center z-10 flex flex-col md:items-center">
                  <Icon className="w-8 h-8 text-stone-900 mb-3 md:hidden block" />
                  <h3 className="text-base font-semibold text-stone-900">{step.title}</h3>
                  <p className="text-sm text-stone-600 mt-1">{step.description}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </section>
  );
};

export default HowItWorks;
