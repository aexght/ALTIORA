import React from 'react';
import cn from '../../utils/cn';

/**
 * Radio button group with optional card-style layout
 * 
 * @param {string} label - Group label
 * @param {string} name - Radio group name
 * @param {string} value - Selected value
 * @param {function} onChange - Change handler
 * @param {Array} options - Array of {value, label, description?}
 * @param {string} error - Error message
 * @param {string} variant - 'default'|'card'
 * @param {string} className - Additional classes
 */
const RadioGroup = ({ label, name, value, onChange, options = [], error, variant = 'default', className }) => {
  return (
    <div className={cn("w-full", className)} role="radiogroup" aria-labelledby={name ? `${name}-label` : undefined}>
      {label && (
        <div id={name ? `${name}-label` : undefined} className="block text-sm font-medium text-slate-700 mb-2">
          {label}
        </div>
      )}
      <div className={cn(
        variant === 'card' ? "grid gap-3" : "flex flex-col gap-2"
      )}>
        {options.map((opt) => {
          const isSelected = value === opt.value;
          const radioId = `${name}-${opt.value}`;

          if (variant === 'card') {
            return (
              <label 
                key={opt.value} 
                htmlFor={radioId}
                className={cn(
                  "flex items-start p-4 border rounded-xl cursor-pointer transition-all duration-200",
                  isSelected 
                    ? "border-primary bg-primary-light" 
                    : "border-slate-200 bg-white hover:border-slate-300"
                )}
              >
                <div className="flex items-center h-5">
                  <input
                    id={radioId}
                    name={name}
                    type="radio"
                    value={opt.value}
                    checked={isSelected}
                    onChange={onChange}
                    className="w-4 h-4 text-primary bg-white border-slate-300 focus:ring-primary/20 accent-primary"
                  />
                </div>
                <div className="ml-3 flex flex-col">
                  <span className={cn("block text-sm font-medium", isSelected ? "text-primary" : "text-slate-900")}>
                    {opt.label}
                  </span>
                  {opt.description && (
                    <span className="block text-sm text-slate-500 mt-0.5">
                      {opt.description}
                    </span>
                  )}
                </div>
              </label>
            );
          }

          return (
            <label key={opt.value} htmlFor={radioId} className="flex items-center cursor-pointer">
              <input
                id={radioId}
                name={name}
                type="radio"
                value={opt.value}
                checked={isSelected}
                onChange={onChange}
                className="w-4 h-4 text-primary bg-white border-slate-300 focus:ring-primary/20 accent-primary"
              />
              <span className="ml-2 text-sm text-slate-700">{opt.label}</span>
            </label>
          );
        })}
      </div>
      {error && <p className="mt-1.5 text-sm text-danger">{error}</p>}
    </div>
  );
};

export { RadioGroup };
export default RadioGroup;
