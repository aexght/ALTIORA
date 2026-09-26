import React from 'react';
import { cn } from '../../utils/cn';

export function FormField({
  label,
  htmlFor,
  error,
  required,
  description,
  children,
  className,
}) {
  return (
    <div className={cn('mb-5', className)}>
      {label && (
        <label htmlFor={htmlFor} className="block text-sm font-medium text-slate-700">
          {label}
          {required && <span className="text-danger ml-0.5">*</span>}
        </label>
      )}
      {description && (
        <p className="text-xs text-slate-400 mt-0.5">{description}</p>
      )}
      <div className="mt-1.5">
        {children}
      </div>
      {error && (
        <p role="alert" className="text-sm text-danger mt-1.5">
          {error}
        </p>
      )}
    </div>
  );
}

export default FormField;
