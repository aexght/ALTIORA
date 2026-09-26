/**
 * Hero — Full-viewport landing hero section.
 *
 * Left column: badge → heading → description → CTAs → time estimate.
 * Right column: HeroIllustration (hidden on mobile, visible lg+).
 */

import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Clock } from 'lucide-react';
import { Button } from '../common/Button';
import { Badge } from '../common/Badge';
import HeroIllustration from './HeroIllustration';
import { useCareer } from '../../context/CareerContext';

export function Hero() {
  const navigate = useNavigate();
  const { dispatch } = useCareer();

  const handleStart = () => {
    dispatch({ type: 'START_ASSESSMENT' });
    navigate('/student');
  };

  const handleLearnMore = () => {
    document
      .getElementById('how-it-works')
      ?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <section
      aria-label="Hero"
      className="relative min-h-screen flex items-center altiora-bg"
    >
      {/* ALTIORA Wordmark / Navbar */}
      <div className="absolute top-0 left-0 w-full px-6 py-8 md:px-12 md:py-10 z-20 flex justify-start">
        <span className="font-display text-2xl md:text-3xl font-bold text-stone-900 tracking-[0.15em] uppercase">
          ALTIORA
        </span>
      </div>

      <div className="w-full max-w-6xl mx-auto px-6 py-24 lg:py-0">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">

          {/* ── Text column ──────────────────────────── */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {/* Badge */}
            <Badge variant="primary" size="md">
              AI-Powered Career Guidance
            </Badge>

            {/* Heading */}
            <h1 className="mt-6 text-4xl sm:text-5xl lg:text-[3.5rem] font-bold leading-[1.12] tracking-tight text-stone-900 font-display">
              Find the Career Path{' '}
              <span className="text-stone-900 italic font-display">That Fits You Best</span>
            </h1>

            {/* Description */}
            <p className="mt-5 text-lg text-stone-600 leading-relaxed max-w-xl">
              Discover personalised course and college recommendations based on
              your academic background and aptitude assessment.
            </p>

            {/* CTAs */}
            <div className="mt-8 flex flex-wrap gap-3">
              <Button size="lg" onClick={handleStart}>
                Start Career Assessment
                <ArrowRight className="ml-2 w-4 h-4" />
              </Button>
              <Button variant="outline" size="lg" onClick={handleLearnMore}>
                Learn More
              </Button>
            </div>

            {/* Time estimate */}
            <div className="mt-6 flex items-center gap-2 text-sm text-stone-500">
              <Clock className="w-4 h-4" />
              <span>Estimated assessment time: 8–10 minutes</span>
            </div>
          </motion.div>

          {/* ── Illustration column ──────────────────── */}
          <motion.div
            className="hidden lg:flex justify-end"
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.15 }}
          >
            <HeroIllustration className="w-full max-w-xs md:max-w-md xl:max-w-lg" />
          </motion.div>
        </div>
      </div>
    </section>
  );
}

export default Hero;
