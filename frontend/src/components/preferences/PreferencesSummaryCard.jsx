import React from 'react';
import { motion } from 'framer-motion';
import { ClipboardList } from 'lucide-react';
import { PLACEMENT_IMPORTANCE_LABELS } from '../../utils/constants';
import { formatCurrency } from '../../utils/formatters';

export function PreferencesSummaryCard({ preferences }) {
  const {
    state: preferredState,
    district,
    ownership,
    maxFee,
    hostel,
    collegeType,
    placementImportance,
    travelPreference,
  } = preferences;

  const placementLabel = (value) =>
    PLACEMENT_IMPORTANCE_LABELS[value] || String(value); 

  const rows = [
    { label: 'Preferred State', value: preferredState },
    { label: 'Preferred District', value: district },
    { label: 'College Ownership', value: ownership },
    { label: 'Fee Budget', value: formatCurrency(maxFee) },
    { label: 'Hostel', value: hostel },
    { label: 'College Type', value: collegeType },
    { label: 'Placement Importance', value: placementLabel(placementImportance) },
    { label: 'Travel Preference', value: travelPreference },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="mt-6 bg-white rounded-xl border border-stone-200 shadow-card p-6 sm:p-8"
    >
      <h3 className="text-lg font-bold text-stone-900 mb-4 flex items-center gap-2">
        <ClipboardList className="w-5 h-5 text-stone-900" />
        Your Preferences
      </h3>

      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4">
        {rows.map((row) => (
          <div key={row.label} className="flex flex-col min-w-0">
            <dt className="text-xs font-medium text-stone-500">{row.label}</dt>
            <dd className="text-sm font-semibold text-stone-900 truncate" title={row.value || ''}>
              {row.value || '--'}
            </dd>
          </div>
        ))}
      </dl>
    </motion.div>
  );
}

export default PreferencesSummaryCard;