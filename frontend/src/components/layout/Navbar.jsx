/**
 * Navbar — ALTIORA design system.
 *
 * Elegant serif wordmark with generous letter-spacing.
 * Refined step indicator: past = dark check, current = dark emphasis, future = muted.
 */

import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Check } from 'lucide-react';
import { cn } from '../../utils/cn';
import { STEPS } from '../../utils/constants';

export function Navbar({ className }) {
  const location = useLocation();

  return (
    <nav className={cn('sticky top-0 z-50 bg-white/90 backdrop-blur-sm border-b border-stone-200/60 h-16 px-6', className)}>
      <div className="max-w-7xl mx-auto h-full flex items-center justify-between">
        <div className="flex-shrink-0">
          <Link to="/" className="font-display text-2xl md:text-3xl font-bold text-stone-900 tracking-[0.15em] uppercase leading-none">
            ALTIORA
          </Link>
        </div>

        <div className="flex items-center gap-1">
          {STEPS?.map((step, index) => {
            const isCurrent = location.pathname === step.path;
            const isPast = STEPS.findIndex(s => s.path === location.pathname) > index;

            return (
              <div key={step.id || index} className={cn("flex items-center", !isCurrent && "hidden md:flex")}>
                <div className="flex items-center gap-2 px-3 py-1.5">
                  <div
                    className={cn(
                      'flex items-center justify-center w-6 h-6 rounded-full text-xs font-medium transition-colors',
                      isPast ? 'bg-stone-900 text-white' : isCurrent ? 'bg-stone-900 text-white' : 'bg-stone-100 text-stone-400'
                    )}
                  >
                    {isPast ? <Check className="w-3.5 h-3.5" /> : index + 1}
                  </div>
                  <span
                    className={cn(
                      'text-sm transition-colors',
                      isCurrent ? 'font-semibold text-stone-900' : isPast ? 'font-medium text-stone-700' : 'text-stone-400'
                    )}
                  >
                    {step.label}
                  </span>
                </div>
                {index < STEPS.length - 1 && (
                  <div className={cn('w-6 h-px transition-colors hidden md:block', isPast ? 'bg-stone-400' : 'bg-stone-200')} />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
