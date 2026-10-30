import React from 'react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  variant?: 'cyan' | 'indigo' | 'emerald' | 'amber' | 'rose' | 'default';
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  variant = 'default',
}) => {
  const borderVariants = {
    cyan: 'border-cyan-500/30 hover:border-cyan-500/50',
    indigo: 'border-indigo-500/30 hover:border-indigo-500/50',
    emerald: 'border-emerald-500/30 hover:border-emerald-500/50',
    amber: 'border-amber-500/30 hover:border-amber-500/50',
    rose: 'border-rose-500/30 hover:border-rose-500/50',
    default: 'border-slate-800 hover:border-slate-700',
  };

  const iconVariants = {
    cyan: 'bg-cyan-500/10 text-cyan-400',
    indigo: 'bg-indigo-500/10 text-indigo-400',
    emerald: 'bg-emerald-500/10 text-emerald-400',
    amber: 'bg-amber-500/10 text-amber-400',
    rose: 'bg-rose-500/10 text-rose-400',
    default: 'bg-slate-800 text-slate-300',
  };

  return (
    <div className={`bg-slate-900/80 backdrop-blur-md rounded-xl border p-5 transition-all duration-200 shadow-lg ${borderVariants[variant]}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        <div className={`p-2 rounded-lg ${iconVariants[variant]}`}>
          {icon}
        </div>
      </div>
      <div className="mt-3 flex items-baseline gap-2">
        <span className="text-2xl font-bold tracking-tight text-white">{value}</span>
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
};
