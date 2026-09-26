import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

export function PageContainer({
  title,
  subtitle,
  maxWidth = 'lg',
  children,
  className,
}) {
  const maxWidthClasses = {
    sm: 'max-w-lg',
    md: 'max-w-2xl',
    lg: 'max-w-4xl',
    xl: 'max-w-6xl',
  };

  return (
    <main className={cn('min-h-screen pt-24 pb-16 px-4 sm:px-6 altiora-bg', className)}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className={cn('mx-auto w-full', maxWidthClasses[maxWidth] || maxWidthClasses.lg)}
      >
        {(title || subtitle) && (
          <div className="mb-8">
            {title && <h1 className="text-2xl sm:text-3xl font-bold text-stone-900 font-display">{title}</h1>}
            {subtitle && <p className="text-stone-500 mt-2">{subtitle}</p>}
          </div>
        )}
        <div className={cn((title || subtitle) ? 'mt-8' : '')}>
          {children}
        </div>
      </motion.div>
    </main>
  );
}

export default PageContainer;
