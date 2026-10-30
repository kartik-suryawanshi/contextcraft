import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { Bot, CheckCircle2, Clock, AlertCircle } from 'lucide-react';

interface AgentNodeData {
  label: string;
  role: string;
  description: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  stepOrder?: number;
  durationMs?: number;
  tokens?: number;
  memoryCount?: number;
  isCurrent?: boolean;
}

export const AgentNode: React.FC<{ data: AgentNodeData }> = ({ data }) => {
  const isSelected = data.isCurrent;

  return (
    <div
      className={`px-3.5 py-3 rounded-lg border bg-white min-w-[220px] max-w-[240px] transition-all cursor-pointer shadow-[0_1px_2px_0_rgba(16,24,40,0.04)] ${
        isSelected
          ? 'border-[#5558D9] ring-2 ring-[#EEF0FD]'
          : 'border-[#E6E8EC] hover:border-[#D0D5DD]'
      }`}
    >
      <Handle type="target" position={Position.Top} className="!bg-[#5558D9] !w-2 !h-2" />

      {/* Header: Name and Step order */}
      <div className="flex items-center justify-between gap-1 mb-1.5">
        <div className="flex items-center gap-1.5 min-w-0">
          <Bot className="w-3.5 h-3.5 text-[#667085] shrink-0" />
          <span className="font-semibold text-xs text-[#20242C] truncate tracking-tight">
            {data.label}
          </span>
        </div>
        {data.stepOrder !== undefined && (
          <span className="font-mono text-[10px] text-[#98A2B3] shrink-0">
            #{data.stepOrder}
          </span>
        )}
      </div>

      {/* Description */}
      <p className="text-[11px] text-[#667085] leading-relaxed line-clamp-2 mb-2">
        {data.description}
      </p>

      {/* Telemetry Row */}
      <div className="flex items-center justify-between pt-2 border-t border-[#F2F4F7] text-[10px] font-mono text-[#667085] tabular-nums">
        <span className="flex items-center gap-1">
          {data.status === 'completed' && <span className="w-1.5 h-1.5 rounded-full bg-[#15966B]" />}
          {data.status === 'running' && <span className="w-1.5 h-1.5 rounded-full bg-[#5558D9] animate-pulse" />}
          {data.status === 'idle' && <span className="w-1.5 h-1.5 rounded-full bg-[#D0D5DD]" />}
          <span className="capitalize">{data.status}</span>
        </span>
        <div className="flex items-center gap-2">
          {data.durationMs !== undefined && <span>{data.durationMs}ms</span>}
          {data.tokens !== undefined && <span>{data.tokens}t</span>}
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-[#5558D9] !w-2 !h-2" />
    </div>
  );
};
