import React, { forwardRef } from 'react';
import cn from '../../utils/cn';

/**
 * Input — ALTIORA design system.
 *
 * Clean, restrained border, subtle focus treatment.
 * Labels are small-caps-like with generous spacing.
 */
const Input = forwardRef(({ label, id, name, type = 'text', value, onChange, placeholder, error, disabled, required, className, ...rest }, ref) => {
  const inputId = id || name;
  return (
    <div className={cn("w-full", className)}>
      {label && (
        <label htmlFor={inputId} className="block text-xs font-medium uppercase tracking-wider text-stone-500 mb-2">
          {label} {required && <span className="text-danger">*</span>}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        name={name}
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        className={cn(
          "w-full px-4 py-3 rounded-lg border bg-white text-stone-900 text-sm placeholder:text-stone-400 outline-none transition-all duration-200",
          error
            ? "border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-100"
            : "border-stone-200 focus:border-stone-900 focus:ring-2 focus:ring-stone-900/10",
          disabled && "bg-stone-50 text-stone-400 cursor-not-allowed"
        )}
        {...rest}
      />
      {error && <p className="mt-1.5 text-sm text-danger">{error}</p>}
    </div>
  );
});

Input.displayName = 'Input';

export { Input };
export default Input;
