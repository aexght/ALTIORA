import React from 'react';
import cn from '../../utils/cn';

/**
 * Reusable range slider with a live value readout.
 *
 * Uses a native `<input type="range">` for keyboard accessibility and
 * large touch targets, with Tailwind styling and a visible focus ring.
 *
 * @param {string} label - Slider label
 * @param {string} name - Slider name
 * @param {number} value - Current value
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @param {number} step - Step size
 * @param {function} onChange - Handler called with (value, name)
 * @param {function} formatValue - Optional (value) => display string
 * @param {string} minLabel - Optional label shown at the low end
 * @param {string} maxLabel - Optional label shown at the high end
 * @param {string} description - Optional helper text
 * @param {boolean} disabled - Disabled state
 * @param {boolean} required - Required state
 * @param {string} className - Additional classes
 */
const Slider = ({
  label,
  name,
  value,
  min,
  max,
  step = 1,
  onChange,
  formatValue,
  minLabel,
  maxLabel,
  description,
  disabled,
  required,
  className,
}) => {
  const display = formatValue ? formatValue(value) : String(value);

  const handleChange = (e) => {
    if (onChange) onChange(Number(e.target.value), name);
  };

  return (
    <div className={cn('w-full mb-5', className)}>
      <div className="mb-1.5 flex items-center justify-between gap-4">
        {label ? (
          <label htmlFor={name} className="block text-sm font-medium text-slate-700">
            {label}
            {required && <span className="text-danger ml-0.5">*</span>}
          </label>
        ) : (
          <span />
        )}
        <span
          className="text-sm font-semibold text-primary tabular-nums"
          aria-live="polite"
        >
          {display}
        </span>
      </div>

      {description && (
        <p className="text-xs text-slate-400 mb-1.5">{description}</p>
      )}

      <input
        id={name}
        name={name}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={handleChange}
        disabled={disabled}
        aria-label={label || name}
        className={cn(
          'w-full h-2 rounded-full appearance-none cursor-pointer bg-slate-200',
          'accent-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-primary',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      />

      {(minLabel || maxLabel) && (
        <div className="mt-1 flex justify-between text-xs text-slate-500">
          <span>{minLabel}</span>
          <span>{maxLabel}</span>
        </div>
      )}
    </div>
  );
};

export { Slider };
export default Slider;