import React from 'react';
import cn from '../../utils/cn';

/**
 * Single checkbox with label
 * 
 * @param {string} label - Checkbox label
 * @param {string} id - Checkbox id
 * @param {string} name - Checkbox name
 * @param {boolean} checked - Checked state
 * @param {function} onChange - Change handler
 * @param {boolean} disabled - Disabled state
 * @param {string} className - Additional classes
 */
const Checkbox = ({ label, id, name, checked, onChange, disabled, className }) => {
  const checkboxId = id || name;
  return (
    <div className={cn("flex items-center", className)}>
      <input
        id={checkboxId}
        name={name}
        type="checkbox"
        checked={checked}
        onChange={onChange}
        disabled={disabled}
        className="w-4 h-4 rounded border-slate-300 text-primary focus:ring-primary/20 accent-primary disabled:opacity-50 disabled:cursor-not-allowed"
      />
      {label && (
        <label
          htmlFor={checkboxId}
          className={cn(
            "ml-2 block text-sm text-slate-700 cursor-pointer",
            disabled && "opacity-50 cursor-not-allowed"
          )}
        >
          {label}
        </label>
      )}
    </div>
  );
};

export { Checkbox };
export default Checkbox;
