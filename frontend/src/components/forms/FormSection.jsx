import React from 'react';
import { cn } from '../../utils/cn';

export function FormSection({ title, description, children, className }) {
  return (
    <section className={cn('mb-8', className)}>
      {(title || description) && (
        <div className="mb-6">
          {title && <h2 className="text-lg font-semibold text-stone-900">{title}</h2>}
          {description && <p className="text-sm text-stone-500 mt-1">{description}</p>}
        </div>
      )}
      <div className={cn(title ? 'mt-6' : 'mt-4')}>
        {children}
      </div>
    </section>
  );
}

export default FormSection;
