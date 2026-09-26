import React from 'react';
import { cn } from '../../utils/cn';

export function LoadingSpinner({ size = 'md', className }) {
  const sizeClasses = {
    sm: 'w-5 h-5',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
  };

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div
        className={cn(
          'animate-spin border-2 border-slate-200 border-t-primary rounded-full',
          sizeClasses[size] || sizeClasses.md
        )}
      />
    </div>
  );
}

export default LoadingSpinner;
