import React from 'react';
import { Link } from 'react-router-dom';

export const LandingFooter = () => {
  return (
    <footer className="border-t border-stone-200 bg-white">
      <div className="py-10 px-6 max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 items-center text-center md:text-left">
        
        {/* Left Column */}
        <div className="flex flex-col items-center md:items-start">
          <h3 className="text-lg font-bold font-display text-stone-900">ALTIORA</h3>
          <p className="text-sm text-stone-500 mt-1">
            AI-powered career guidance for students.
          </p>
        </div>

        {/* Center Column */}
        <div className="flex gap-6 justify-center md:text-center text-sm text-stone-500">
          <a href="#" className="hover:text-stone-900 transition-colors">About</a>
          <Link to="/student" className="hover:text-stone-900 transition-colors">Assessment</Link>
          <a href="#" className="hover:text-stone-900 transition-colors">GitHub</a>
          <a href="#" className="hover:text-stone-900 transition-colors">Contact</a>
        </div>

        {/* Right Column */}
        <div className="md:text-right text-sm text-stone-400 text-center">
          &copy; 2025 ALTIORA. Built for academic purposes.
        </div>
      </div>
    </footer>
  );
};

export default LandingFooter;
