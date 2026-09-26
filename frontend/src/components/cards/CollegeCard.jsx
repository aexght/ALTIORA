import React from 'react';
import { isUnverified, formatCurrency } from '../../utils/formatters';
import { cn } from '../../utils/cn';
import { ExternalLink, MapPin } from 'lucide-react';

export const CollegeCard = ({
  name,
  location,
  naacGrade,
  nirfRank,
  ownership,
  websiteUrl,
  fee,
  hostelAvailable,
  hostelFee,
  scholarship,
  placement,
  reasons = [],
  className
}) => {
  return (
    <div className={cn("bg-white rounded-2xl p-5 border border-slate-200 shadow-sm", className)}>
      <h3 className="text-base font-semibold text-slate-900">{name}</h3>
      
      {!isUnverified(location) && (
        <div className="flex items-center gap-1.5 text-sm text-slate-600 mt-2">
          <MapPin className="w-4 h-4" />
          <span>{location}</span>
        </div>
      )}

      <div className="grid grid-cols-2 gap-3 mt-4 text-sm">
        {!isUnverified(naacGrade) && (
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">NAAC Grade</div>
            <div className="text-slate-900 font-medium">{naacGrade}</div>
          </div>
        )}
        
        {!isUnverified(nirfRank) && (
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">NIRF Rank</div>
            <div className="text-slate-900 font-medium">{nirfRank}</div>
          </div>
        )}
        
        {!isUnverified(ownership) && (
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">Ownership</div>
            <div className="text-slate-900 font-medium">{ownership}</div>
          </div>
        )}
        
        {!isUnverified(fee) && (
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">Annual Fee</div>
            <div className="text-slate-900 font-medium">{formatCurrency(fee)}</div>
          </div>
        )}
        
        {!isUnverified(hostelAvailable) && (
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">Hostel</div>
            <div className="text-slate-900 font-medium">{hostelAvailable}</div>
          </div>
        )}
        
        {!isUnverified(hostelFee) && (
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">Hostel Fee</div>
            <div className="text-slate-900 font-medium">{formatCurrency(hostelFee)}</div>
          </div>
        )}
        
        {!isUnverified(scholarship) && (
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">Scholarship</div>
            <div className="text-slate-900 font-medium">{scholarship}</div>
          </div>
        )}
        
        {!isUnverified(placement) && (
          <div>
            <div className="text-xs text-slate-400 uppercase tracking-wide">Placement</div>
            <div className="text-slate-900 font-medium">{placement}</div>
          </div>
        )}
      </div>

      {reasons && reasons.length > 0 && (
        <div className="mt-4 space-y-2">
          {reasons.map((reason, idx) => (
            <div key={idx} className="flex items-start gap-2 text-sm text-slate-600">
              <span className="w-1.5 h-1.5 rounded-full bg-success shrink-0 mt-1.5"></span>
              <span>{reason}</span>
            </div>
          ))}
        </div>
      )}

      {websiteUrl && !isUnverified(websiteUrl) && (
        <a 
          href={websiteUrl} 
          target="_blank" 
          rel="noopener noreferrer"
          className="mt-5 flex items-center justify-center gap-2 w-full py-2 px-4 rounded-xl border border-slate-200 text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors"
        >
          <ExternalLink className="w-4 h-4" />
          Official Website
        </a>
      )}
    </div>
  );
};

export default CollegeCard;
