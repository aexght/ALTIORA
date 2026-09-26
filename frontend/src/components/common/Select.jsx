import React, { forwardRef } from 'react';
import cn from '../../utils/cn';

/**
 * Select — ALTIORA design system.
 */
const Select = forwardRef(({ label, id, name, value, onChange, options = [], placeholder, error, disabled, required, className, ...rest }, ref) => {
  const selectId = id || name;
  return (
    <div className={cn("w-full", className)}>
      {label && (
        <label htmlFor={selectId} className="block text-xs font-medium uppercase tracking-wider text-stone-500 mb-2">
          {label} {required && <span className="text-danger">*</span>}
        </label>
      )}
      <select
        ref={ref}
        id={selectId}
        name={name}
        value={value}
        onChange={onChange}
        disabled={disabled}
        required={required}
        className={cn(
          "w-full px-4 py-3 rounded-lg border bg-white text-stone-900 text-sm outline-none transition-all duration-200 appearance-none",
          error
            ? "border-red-300 focus:border-red-500 focus:ring-2 focus:ring-red-100"
            : "border-stone-200 focus:border-stone-900 focus:ring-2 focus:ring-stone-900/10",
          disabled && "bg-stone-50 text-stone-400 cursor-not-allowed"
        )}
        style={{ backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%2378716c'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E")`, backgroundRepeat: 'no-repeat', backgroundPosition: 'right 1rem center', backgroundSize: '1.2em 1.2em' }}
        {...rest}
      >
        {placeholder && (
          <option value="" disabled={required}>
            {placeholder}
          </option>
        )}
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
      {error && <p className="mt-1.5 text-sm text-danger">{error}</p>}
    </div>
  );
});

Select.displayName = 'Select';

export { Select };
export default Select;
