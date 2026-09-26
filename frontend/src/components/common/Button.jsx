import React, { forwardRef } from 'react';
import cn from '../../utils/cn';

/**
 * Button — ALTIORA design system.
 *
 * Primary: dark/black, elegant, subtle elevation + hover lift.
 * Secondary: white surface, dark border, refined hover.
 * Outline/Ghost: restrained treatments.
 * Danger: understated red.
 */
const Button = forwardRef(({ variant = 'primary', size = 'md', disabled, loading, children, className, type = 'button', ...rest }, ref) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-stone-900';

  const variants = {
    primary: 'bg-stone-900 text-white hover:bg-stone-800 hover:-translate-y-px shadow-button active:translate-y-0',
    secondary: 'bg-white text-stone-900 border border-stone-300 hover:border-stone-400 hover:bg-stone-50 shadow-card',
    outline: 'border border-stone-200 text-stone-700 hover:bg-stone-50 hover:border-stone-300',
    ghost: 'text-stone-600 hover:text-stone-900 hover:bg-stone-100',
    danger: 'bg-red-800 text-white hover:bg-red-700 shadow-button focus-visible:ring-red-700'
  };

  const sizes = {
    sm: 'px-3.5 py-1.5 text-[13px] rounded-md gap-1.5',
    md: 'px-5 py-2.5 text-sm rounded-lg gap-2',
    lg: 'px-7 py-3 text-[15px] rounded-lg gap-2 tracking-wide'
  };

  return (
    <button
      ref={ref}
      type={type}
      disabled={disabled || loading}
      className={cn(baseStyles, variants[variant], sizes[size], className)}
      {...rest}
    >
      {loading && (
        <svg className="animate-spin -ml-1 mr-1.5 h-4 w-4 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {children}
    </button>
  );
});

Button.displayName = 'Button';

export { Button };
export default Button;
