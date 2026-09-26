import React from 'react';
import cn from '../../utils/cn';

/**
 * Badge — ALTIORA design system.
 */
const Badge = ({ variant = 'primary', size = 'sm', children, className }) => {
  const baseStyles = 'inline-flex items-center font-medium rounded-md';

  const variants = {
    primary: 'bg-stone-100 text-stone-700',
    success: 'bg-success-light text-green-800',
    warning: 'bg-warning-light text-amber-800',
    danger: 'bg-danger-light text-red-800',
    neutral: 'bg-stone-100 text-stone-500'
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm'
  };

  return (
    <span className={cn(baseStyles, variants[variant], sizes[size], className)}>
      {children}
    </span>
  );
};

export { Badge };
export default Badge;
