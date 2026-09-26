import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Button } from '../common/Button';
import { useCareer } from '../../context/CareerContext';

export const CTASection = () => {
  const navigate = useNavigate();
  const { dispatch } = useCareer();

  const handleStart = () => {
    dispatch({ type: 'START_ASSESSMENT' });
    navigate('/student');
  };

  return (
    <section className="py-24 lg:py-32 altiora-bg">
      <motion.div 
        className="max-w-2xl mx-auto px-6"
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
      >
        <div className="bg-stone-100 p-12 lg:p-16 rounded-xl border border-stone-200 text-center shadow-card">
          <h2 className="text-3xl sm:text-4xl font-bold text-stone-900 font-display">
            Ready to Discover Your Future?
          </h2>
          <p className="text-lg text-stone-600 mt-4 leading-relaxed">
            Begin your personalised career assessment and explore opportunities aligned with your strengths.
          </p>
          <div className="mt-8 flex justify-center">
            <Button size="lg" onClick={handleStart}>
              Start Career Assessment
              <ArrowRight className="ml-2 w-5 h-5" />
            </Button>
          </div>
        </div>
      </motion.div>
    </section>
  );
};

export default CTASection;
