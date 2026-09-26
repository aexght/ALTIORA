import React from 'react';
import { formatPercent } from '../../utils/formatters';
import { Badge } from '../common/Badge';
import { CheckCircle2 } from 'lucide-react';

export const CourseCard = ({ course, domain, score, reasons = [] }) => {
  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200 shadow-sm hover:shadow-md transition-shadow duration-200">
      <Badge variant="primary">{domain}</Badge>
      <h3 className="text-base font-semibold text-slate-900 mt-3">{course}</h3>
      <p className="text-sm text-slate-600 mt-1">{formatPercent(score)} match score</p>
      
      {reasons && reasons.length > 0 && (
        <ul className="mt-4 space-y-2">
          {reasons.map((reason, idx) => (
            <li key={idx} className="flex items-start gap-2 text-sm text-slate-600">
              <CheckCircle2 className="w-4 h-4 text-success shrink-0 mt-0.5" />
              <span>{reason}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default CourseCard;
