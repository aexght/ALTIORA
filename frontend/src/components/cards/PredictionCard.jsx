import React from 'react';
import { formatPercent } from '../../utils/formatters';
import { Badge } from '../common/Badge';

export const PredictionCard = ({ domain, probability, confidence }) => {
  const getBadgeVariant = (conf) => {
    switch (conf) {
      case 'Very High':
      case 'High':
        return 'success';
      case 'Moderate':
        return 'warning';
      case 'Low':
      case 'Very Low':
        return 'danger';
      default:
        return 'primary';
    }
  };

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200 shadow-sm">
      <Badge variant={getBadgeVariant(confidence)}>{confidence} Confidence</Badge>
      <h2 className="text-xl font-semibold text-slate-900 mt-3">{domain}</h2>
      <div className="text-3xl font-bold text-primary mt-2">
        {formatPercent(probability)}
      </div>
      <div className="w-full bg-slate-100 h-2 rounded-full mt-4 overflow-hidden">
        <div 
          className="bg-primary h-full rounded-full transition-all duration-500"
          style={{ width: `${Math.min(100, Math.max(0, probability))}%` }}
        />
      </div>
    </div>
  );
};

export default PredictionCard;
