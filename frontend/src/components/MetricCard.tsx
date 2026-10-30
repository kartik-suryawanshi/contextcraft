import React from 'react';

interface MetricCardProps {
  label: string;
  value: string | number;
  secondaryInfo?: string;
  badge?: React.ReactNode;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  secondaryInfo,
  badge,
}) => {
  return (
    <div className="bg-white border border-[#E6E8EC] rounded-lg p-5 shadow-[0_1px_2px_0_rgba(16,24,40,0.04)] hover:border-[#D0D5DD] transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-medium text-[#667085] tracking-tight">{label}</span>
        {badge}
      </div>
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-semibold tracking-tight text-[#20242C] font-mono tabular-nums">
          {value}
        </span>
      </div>
      {secondaryInfo && (
        <p className="mt-1.5 text-xs text-[#98A2B3] leading-relaxed truncate">
          {secondaryInfo}
        </p>
      )}
    </div>
  );
};
