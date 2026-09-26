import React from 'react';
import { motion } from 'framer-motion';
import { UserCheck, ShieldCheck, Zap } from 'lucide-react';
import { cn } from '../../utils/cn';

export const WhyChooseUs = () => {
  const features = [
    {
      icon: UserCheck,
      title: 'Personalised Guidance',
      description: 'Recommendations tailored to your unique academic profile, interests, and aptitude scores — not generic advice.'
    },
    {
      icon: ShieldCheck,
      title: 'Explainable AI',
      description: 'Every prediction comes with clear reasoning. Understand why a domain was recommended, not just what was recommended.'
    },
    {
      icon: Zap,
      title: 'Lightweight Assessment',
      description: 'Complete the entire assessment in under 10 minutes. No lengthy exams — just 40 focused questions.'
    }
  ];

  return (
    <section className="py-20 lg:py-24 max-w-5xl mx-auto px-6 altiora-bg">
      <motion.div 
        className="text-center mb-16"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <h2 className="text-3xl font-bold text-stone-900 font-display">Why Choose This System</h2>
        <p className="text-lg text-stone-600 mt-4 max-w-2xl mx-auto">
          Designed with clarity, accuracy, and accessibility in mind.
        </p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {features.map((feature, index) => {
          const Icon = feature.icon;
          return (
            <motion.div 
              key={index}
              className="text-left md:text-center"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="w-14 h-14 rounded-lg bg-stone-100 flex items-center justify-center mx-0 md:mx-auto">
                <Icon className="w-7 h-7 text-stone-900" />
              </div>
              <h3 className="text-lg font-semibold text-stone-900 mt-4">{feature.title}</h3>
              <p className="text-sm text-stone-600 mt-2 leading-relaxed max-w-xs mx-0 md:mx-auto">
                {feature.description}
              </p>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
};

export default WhyChooseUs;
