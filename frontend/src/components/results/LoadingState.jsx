/**
 * LoadingState — Skeleton loaders for the results page.
 *
 * Shown while the prediction is being loaded/processed.
 * Matches the results page layout to prevent layout jumps.
 */

import React from 'react';

function SkeletonPulse({ className = '' }) {
  return <div className={`animate-pulse bg-stone-200 rounded-lg ${className}`} />;
}

export function LoadingState() {
  return (
    <div className="max-w-4xl mx-auto w-full">
      {/* Hero skeleton */}
      <div className="text-center py-10 space-y-4">
        <SkeletonPulse className="w-16 h-16 rounded-xl mx-auto" />
        <SkeletonPulse className="w-40 h-4 mx-auto" />
        <SkeletonPulse className="w-72 h-10 mx-auto" />
        <div className="flex items-center justify-center gap-3">
          <SkeletonPulse className="w-16 h-8" />
          <SkeletonPulse className="w-32 h-7 rounded-full" />
        </div>
        <SkeletonPulse className="w-96 h-3 mx-auto max-w-full rounded-full" />
      </div>

      {/* Featured card skeleton */}
      <div className="rounded-xl border border-stone-200 p-8 mb-8 space-y-4">
        <div className="flex items-start gap-4">
          <SkeletonPulse className="w-12 h-12 rounded-xl flex-shrink-0" />
          <div className="flex-1 space-y-3">
            <SkeletonPulse className="w-32 h-3" />
            <SkeletonPulse className="w-64 h-6" />
            <SkeletonPulse className="w-40 h-3" />
            <SkeletonPulse className="w-full h-3" />
            <SkeletonPulse className="w-3/4 h-3" />
          </div>
        </div>
      </div>

      {/* Domain cards skeleton */}
      <div className="space-y-4">
        <SkeletonPulse className="w-56 h-5" />
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="rounded-xl border border-stone-200 p-5 space-y-3">
              <div className="flex items-center justify-between">
                <SkeletonPulse className="w-40 h-4" />
                <SkeletonPulse className="w-12 h-4" />
              </div>
              <SkeletonPulse className="w-full h-1.5 rounded-full" />
            </div>
          ))}
        </div>
      </div>

      {/* Explanation skeleton */}
      <div className="mt-10 space-y-4">
        <SkeletonPulse className="w-64 h-5" />
        <div className="rounded-xl border border-stone-200 p-6 space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-start gap-3">
              <SkeletonPulse className="w-6 h-6 rounded-full flex-shrink-0" />
              <SkeletonPulse className="w-full h-3" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default LoadingState;
