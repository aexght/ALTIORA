import React from 'react';
import { cn } from '../../utils/cn';

export function Footer({ className }) {
  return (
    <footer className={cn('border-t border-stone-200/60 mt-auto', className)}>
      <div className="py-8 max-w-7xl mx-auto px-6">
        <p className="text-center text-sm text-stone-400">
          &copy; {new Date().getFullYear()} ALTIORA. Built for academic purposes.
        </p>
      </div>
    </footer>
  );
}

export default Footer;
