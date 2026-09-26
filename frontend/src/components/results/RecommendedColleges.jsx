/**
 * RecommendedColleges — Displays college recommendations from the master dataset.
 *
 * Shows colleges relevant to the predicted course and student location.
 * Each card displays college name, area, recommended course, and location match.
 */

import React from 'react';
import { motion } from 'framer-motion';
import { MapPin, GraduationCap, ExternalLink, ShieldCheck, Building } from 'lucide-react';

const LOCATION_LABELS = {
  district: { label: "Near your district", icon: MapPin, color: "text-emerald-600", bg: "bg-emerald-50", border: "border-emerald-200" },
  state: { label: "Within your state", icon: MapPin, color: "text-blue-600", bg: "bg-blue-50", border: "border-blue-200" },
  other: { label: "Other options", icon: MapPin, color: "text-stone-500", bg: "bg-stone-50", border: "border-stone-200" },
};

export function RecommendedColleges({ colleges = [] }) {
  if (!colleges || colleges.length === 0) {
    return (
      <section aria-labelledby="colleges-heading" className="space-y-6">
        <div className="flex items-center gap-2 mb-2">
          <GraduationCap className="w-5 h-5 text-stone-500" aria-hidden="true" />
          <h2 id="colleges-heading" className="text-lg font-semibold font-display text-stone-900">
            Recommended Colleges
          </h2>
        </div>
        <p className="text-sm text-stone-500 mb-5">Colleges offering courses aligned with your recommendation.</p>
        <div className="bg-white rounded-xl border border-stone-200 p-8 text-center">
          <p className="text-stone-600 mb-2">
            No verified college matches found for your recommended course and location.
          </p>
          <p className="text-sm text-stone-500">
            This may be because the course has limited availability in your area, or the dataset doesn't yet cover your region.
          </p>
        </div>
      </section>
    );
  }

  return (
    <section aria-labelledby="colleges-heading" className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-2">
          <GraduationCap className="w-5 h-5 text-stone-500" aria-hidden="true" />
          <h2 id="colleges-heading" className="text-lg font-semibold font-display text-stone-900">
            Recommended Colleges
          </h2>
        </div>
        <p className="text-sm text-stone-500 mb-5">Colleges offering courses aligned with your recommendation.</p>
      </div>

      <div className="space-y-4">
        {colleges.map((college, idx) => {
          const locationInfo = LOCATION_LABELS[college.location_match] || LOCATION_LABELS.other;
          const Icon = locationInfo.icon;
          

          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.05 * idx }}
              className="bg-white rounded-xl border border-stone-200 p-6 shadow-sm hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-start mb-3 gap-4">
                    <div className="flex items-center gap-2 mb-1 flex-wrap">
                      <h3 className="text-lg font-semibold text-stone-900 truncate">
                        {college.college_name}
                      </h3>
                      {college.website && (
                        <a href={college.website} target="_blank" rel="noopener noreferrer" className="text-stone-400 hover:text-stone-600">
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex flex-wrap items-center gap-3 text-sm text-stone-600 mb-3">
                    <span className="flex items-center gap-1.5">
                      <MapPin className="w-3.5 h-3.5" aria-hidden="true" />
                      {college.area}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <GraduationCap className="w-3.5 h-3.5" aria-hidden="true" />
                      <strong className="text-stone-900">{college.course}</strong>
                    </span>
                  </div>
                  
                  {/* Tags */}
                  <div className="flex flex-wrap items-center gap-2 mt-2">
                     <span className="inline-flex items-center px-2 py-1 bg-indigo-50 border border-indigo-100 text-indigo-700 text-xs font-medium rounded" title="This institution offers your recommended course">
                       Course Fit
                     </span>
                     {college.naac && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-stone-50 border border-stone-200 text-stone-600 text-xs font-medium rounded">
                          <ShieldCheck className="w-3 h-3" />
                          NAAC {college.naac}
                        </span>
                     )}
                     {college.ownership && (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-stone-50 border border-stone-200 text-stone-600 text-xs font-medium rounded">
                          <Building className="w-3 h-3" />
                          {college.ownership}
                        </span>
                     )}
                  </div>
                </div>

                <div className="flex-shrink-0">
                  <div className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl border ${locationInfo.bg} ${locationInfo.border}`}>
                    <Icon className={`w-3.5 h-3.5 ${locationInfo.color}`} aria-hidden="true" />
                    <span className={`text-xs font-medium ${locationInfo.color}`}>
                      {locationInfo.label}
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </section>
  );
}

export default RecommendedColleges;