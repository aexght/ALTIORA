import React from 'react';
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts';
import { cn } from '../../utils/cn';

export const DomainRadarChart = ({ data, className }) => {
  const chartData = data.map(item => ({
    subject: item.domain.length > 15 ? item.domain.substring(0, 15) + '...' : item.domain,
    A: item.probability
  }));

  return (
    <div className={cn("w-full h-[300px]", className)}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="70%" data={chartData}>
          <PolarGrid stroke="#e2e8f0" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 12 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
          <Radar 
            name="Probability" 
            dataKey="A" 
            stroke="#2563eb" 
            fill="#2563eb" 
            fillOpacity={0.3} 
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default DomainRadarChart;
