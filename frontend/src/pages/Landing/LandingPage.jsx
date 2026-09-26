/**
 * LandingPage — Composes all landing page sections in order.
 *
 * This page has its own footer (LandingFooter) and does not use
 * the global Navbar or Footer (they are hidden on '/' in App.jsx).
 */

import Hero from '../../components/landing/Hero';
import HowItWorks from '../../components/landing/HowItWorks';
import Features from '../../components/landing/Features';
import Statistics from '../../components/landing/Statistics';
import WhyChooseUs from '../../components/landing/WhyChooseUs';
import CTASection from '../../components/landing/CTASection';
import LandingFooter from '../../components/landing/LandingFooter';

export function LandingPage() {
  return (
    <div className="bg-stone-50 min-h-screen">
      <Hero />
      <HowItWorks />
      <Features />
      <Statistics />
      <WhyChooseUs />
      <CTASection />
      <LandingFooter />
    </div>
  );
}

export default LandingPage;
