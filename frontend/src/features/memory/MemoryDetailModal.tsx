import React from 'react';
import { X, ArrowRight } from 'lucide-react';
import type { MemoryUnit } from '../../types';
import { StatusBadge } from '../../components/StatusBadge';

interface MemoryDetailModalProps {
  memory: MemoryUnit | null;
  onClose: () => void;
  onInspectSuperseding?: (supersededById: string) => void;
}

export const MemoryDetailModal: React.FC<MemoryDetailModalProps> = ({
  memory,
  onClose,
  onInspectSuperseding,
}) => {
  if (!memory) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/30 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white border border-[#E6E8EC] rounded-xl max-w-xl w-full p-6 shadow-xl relative animate-in fade-in duration-100">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[#98A2B3] hover:text-[#20242C] p-1 rounded-md hover:bg-[#F8F9FB] transition"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-2.5 mb-4">
          <span className="font-mono text-xs font-semibold text-[#5558D9]">{memory.id}</span>
          <StatusBadge status={memory.status} size="sm" />
          <span className="text-xs text-[#98A2B3]">·</span>
          <span className="text-xs font-medium text-[#667085]">{memory.topic}</span>
        </div>

        {/* Fact Statement */}
        <div className="bg-[#F8F9FB] rounded-lg p-3.5 border border-[#E6E8EC] mb-4">
          <label className="text-[10px] font-semibold uppercase tracking-wider text-[#98A2B3] block mb-1">
            Atomic Fact Statement
          </label>
          <p className="text-xs font-medium text-[#20242C] leading-relaxed">{memory.fact_text}</p>
        </div>

        {/* Key Values Grid */}
        <div className="grid grid-cols-4 gap-2 mb-4 text-xs">
          <div className="bg-white p-2.5 rounded border border-[#E6E8EC]">
            <span className="text-[10px] text-[#98A2B3] block">Parsed Value</span>
            <span className="font-mono text-xs font-semibold text-[#20242C] mt-0.5 block truncate">
              {memory.value ?? 'None'}
            </span>
          </div>
          <div className="bg-white p-2.5 rounded border border-[#E6E8EC]">
            <span className="text-[10px] text-[#98A2B3] block">Unit</span>
            <span className="font-mono text-xs font-medium text-[#667085] mt-0.5 block truncate">
              {memory.unit ?? 'None'}
            </span>
          </div>
          <div className="bg-white p-2.5 rounded border border-[#E6E8EC]">
            <span className="text-[10px] text-[#98A2B3] block">Confidence</span>
            <span className="font-mono text-xs font-semibold text-[#15966B] mt-0.5 block">
              {(memory.confidence * 100).toFixed(0)}%
            </span>
          </div>
          <div className="bg-white p-2.5 rounded border border-[#E6E8EC]">
            <span className="text-[10px] text-[#98A2B3] block">Tokens</span>
            <span className="font-mono text-xs font-semibold text-[#20242C] mt-0.5 block">
              {memory.token_count}
            </span>
          </div>
        </div>

        {/* Metadata Details */}
        <div className="space-y-2 text-xs divide-y divide-[#F2F4F7] border-y border-[#F2F4F7] py-2 mb-4">
          <div className="flex items-center justify-between pt-1">
            <span className="text-[#667085]">Author Agent</span>
            <span className="font-mono text-[#20242C]">{memory.author_agent}</span>
          </div>
          <div className="flex items-center justify-between pt-1">
            <span className="text-[#667085]">Source Type</span>
            <span className="font-mono text-[#20242C]">{memory.source_type}</span>
          </div>
          <div className="flex items-center justify-between pt-1">
            <span className="text-[#667085]">Version Date / Tag</span>
            <span className="font-mono text-[#20242C]">{memory.version_date || 'None'}</span>
          </div>
          <div className="flex items-center justify-between pt-1">
            <span className="text-[#667085]">Created Timestamp</span>
            <span className="font-mono text-[#98A2B3]">{memory.created_at || 'None'}</span>
          </div>
        </div>

        {/* Superseded Provenance Box */}
        {memory.status === 'superseded' && (
          <div className="bg-[#FBF4E7] border border-[#F6E6C9] rounded-lg p-3 text-xs text-[#C58B24] mb-4">
            <span className="font-semibold block mb-0.5">Superseded Historical Record</span>
            <p className="text-[11px] text-[#7A5413] leading-relaxed">
              {memory.conflict_reason || 'Outdated baseline superseded by a newer revision.'}
            </p>
            {memory.superseded_by && onInspectSuperseding && (
              <div className="mt-2 pt-2 border-t border-[#F6E6C9] flex items-center justify-between text-[11px]">
                <span className="text-[#7A5413]">Superseded by:</span>
                <button
                  onClick={() => onInspectSuperseding(memory.superseded_by!)}
                  className="font-mono text-[#5558D9] font-medium hover:underline inline-flex items-center gap-1"
                >
                  {memory.superseded_by} <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            )}
          </div>
        )}

        {/* Conflicting Warning Box */}
        {memory.status === 'conflicting' && (
          <div className="bg-[#FDEEF0] border border-[#F9D5DA] rounded-lg p-3 text-xs text-[#D84A5B] mb-4">
            <span className="font-semibold block mb-0.5">Unresolved Contradiction</span>
            <p className="text-[11px] text-[#8C2330] leading-relaxed">
              {memory.conflict_reason || 'Contradictory values detected without clear version or confidence precedence.'}
            </p>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-3.5 py-1.5 text-xs font-medium rounded-md bg-[#F2F4F7] hover:bg-[#E4E7EC] text-[#20242C] transition"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
