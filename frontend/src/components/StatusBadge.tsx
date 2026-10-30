import React from 'react';

interface StatusBadgeProps {
  status: 'current' | 'superseded' | 'conflicting' | 'completed' | 'running' | 'failed' | 'idle' | string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const s = status.toLowerCase();
  const sizeClasses = size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-2.5 py-1 text-xs';

  if (s === 'current' || s === 'completed' || s === 'agreed') {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-md bg-[#E8F7F0] text-[#15966B] font-medium border border-[#D1F0E2] ${sizeClasses}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-[#15966B]"></span>
        <span className="capitalize">{s === 'agreed' ? 'Agreed' : s === 'current' ? 'Current' : 'Completed'}</span>
      </span>
    );
  }

  if (s === 'superseded') {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-md bg-[#FBF4E7] text-[#C58B24] font-medium border border-[#F6E6C9] ${sizeClasses}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-[#C58B24]"></span>
        <span>Superseded</span>
      </span>
    );
  }

  if (s === 'conflicting' || s === 'failed') {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-md bg-[#FDEEF0] text-[#D84A5B] font-medium border border-[#F9D5DA] ${sizeClasses}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-[#D84A5B]"></span>
        <span className="capitalize">{s}</span>
      </span>
    );
  }

  if (s === 'running') {
    return (
      <span className={`inline-flex items-center gap-1.5 rounded-md bg-[#EEF0FD] text-[#5558D9] font-medium border border-[#D6DAFB] ${sizeClasses}`}>
        <span className="w-1.5 h-1.5 rounded-full bg-[#5558D9] animate-pulse"></span>
        <span>Running</span>
      </span>
    );
  }

  return (
    <span className={`inline-flex items-center gap-1.5 rounded-md bg-[#F2F4F7] text-[#667085] font-medium border border-[#E4E7EC] ${sizeClasses}`}>
      <span className="capitalize">{status}</span>
    </span>
  );
};
