import React, { useState, useEffect } from 'react';
import {
  Search,
  RefreshCw,
  ArrowRight,
  Filter,
} from 'lucide-react';
import { api } from '../../services/api';
import type { MemoryUnit, ConflictAuditEvent } from '../../types';
import { StatusBadge } from '../../components/StatusBadge';
import { MemoryDetailModal } from './MemoryDetailModal';

export const MemoryExplorerScreen: React.FC = () => {
  const [memories, setMemories] = useState<MemoryUnit[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [searchTopic, setSearchTopic] = useState<string>('');
  const [selectedMemory, setSelectedMemory] = useState<MemoryUnit | null>(null);
  const [conflictAudits, setConflictAudits] = useState<ConflictAuditEvent[]>([]);
  const [activeTab, setActiveTab] = useState<'memories' | 'audits'>('memories');
  const [loading, setLoading] = useState(false);

  const loadMemories = async () => {
    setLoading(true);
    try {
      const [res, auditsRes] = await Promise.all([
        api.getMemories(statusFilter || undefined, searchTopic || undefined),
        api.getConflictAudits(30),
      ]);
      setMemories(res.items);
      setTotalCount(res.total);
      setConflictAudits(auditsRes);
    } catch (err) {
      console.error('Failed to load memories', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMemories();
  }, [statusFilter, searchTopic]);

  const handleInspectSuperseding = async (supersededById: string) => {
    try {
      const unit = await api.getMemory(supersededById);
      setSelectedMemory(unit);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2">
        <div>
          <h1 className="text-xl font-semibold text-[#20242C] tracking-tight">Memory Explorer</h1>
          <p className="text-xs text-[#667085] mt-1">
            Inspect structured facts stored by ContextCraft.
          </p>
        </div>
        <button
          onClick={loadMemories}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-white border border-[#E6E8EC] text-[#20242C] hover:bg-[#F8F9FB] transition shadow-xs disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-[#667085] ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      {/* Controls Bar: Sub-tabs and Search */}
      <div className="bg-white rounded-lg border border-[#E6E8EC] p-3 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
        {/* Sub-tabs */}
        <div className="flex items-center gap-1 bg-[#F8F9FB] p-1 rounded-md border border-[#E6E8EC]">
          <button
            onClick={() => setActiveTab('memories')}
            className={`px-3 py-1 text-xs font-medium rounded transition ${
              activeTab === 'memories'
                ? 'bg-white text-[#20242C] font-semibold shadow-2xs'
                : 'text-[#667085] hover:text-[#20242C]'
            }`}
          >
            Stored Units ({totalCount})
          </button>
          <button
            onClick={() => setActiveTab('audits')}
            className={`px-3 py-1 text-xs font-medium rounded transition ${
              activeTab === 'audits'
                ? 'bg-white text-[#20242C] font-semibold shadow-2xs'
                : 'text-[#667085] hover:text-[#20242C]'
            }`}
          >
            Conflict Audits ({conflictAudits.length})
          </button>
        </div>

        {/* Search & Filters */}
        <div className="flex items-center gap-2">
          {activeTab === 'memories' && (
            <div className="flex items-center gap-1">
              {[
                { id: '', label: 'All' },
                { id: 'current', label: 'Current' },
                { id: 'superseded', label: 'Superseded' },
                { id: 'conflicting', label: 'Conflicting' },
              ].map((f) => (
                <button
                  key={f.id}
                  onClick={() => setStatusFilter(f.id)}
                  className={`px-2.5 py-1 text-xs rounded-md transition font-medium ${
                    statusFilter === f.id
                      ? 'bg-[#20242C] text-white'
                      : 'bg-[#F8F9FB] text-[#667085] hover:text-[#20242C] border border-[#E6E8EC]'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>
          )}

          <div className="relative min-w-[200px]">
            <Search className="w-3.5 h-3.5 absolute left-2.5 top-2 text-[#98A2B3]" />
            <input
              type="text"
              placeholder="Search topic or fact..."
              value={searchTopic}
              onChange={(e) => setSearchTopic(e.target.value)}
              className="w-full bg-[#F8F9FB] border border-[#E6E8EC] rounded-md pl-8 pr-2.5 py-1 text-xs text-[#20242C] placeholder-[#98A2B3] focus:outline-none focus:border-[#5558D9] focus:bg-white"
            />
          </div>
        </div>
      </div>

      {/* Main Table View */}
      {activeTab === 'memories' ? (
        <div className="bg-white rounded-lg border border-[#E6E8EC] overflow-hidden shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-[#F8F9FB] text-[11px] font-medium text-[#667085] border-b border-[#E6E8EC]">
                <tr>
                  <th className="px-5 py-2.5 font-medium">ID</th>
                  <th className="px-5 py-2.5 font-medium">Topic</th>
                  <th className="px-5 py-2.5 font-medium">Fact Statement</th>
                  <th className="px-5 py-2.5 font-medium">Value / Unit</th>
                  <th className="px-5 py-2.5 font-medium">Status</th>
                  <th className="px-5 py-2.5 font-medium">Author</th>
                  <th className="px-5 py-2.5 text-right font-medium">Tokens</th>
                  <th className="px-5 py-2.5 text-right font-medium">Detail</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#F2F4F7]">
                {memories.length > 0 ? (
                  memories.map((mem) => (
                    <tr
                      key={mem.id}
                      onClick={() => setSelectedMemory(mem)}
                      className="hover:bg-[#F8F9FB] transition-colors cursor-pointer"
                    >
                      <td className="px-5 py-3 font-mono text-[11px] font-medium text-[#5558D9]">
                        {mem.id}
                      </td>
                      <td className="px-5 py-3 font-medium text-[#20242C] max-w-[140px] truncate">
                        {mem.topic}
                      </td>
                      <td className="px-5 py-3 max-w-sm truncate text-[#667085]" title={mem.fact_text}>
                        {mem.fact_text}
                      </td>
                      <td className="px-5 py-3 font-mono text-[#20242C] whitespace-nowrap">
                        {mem.value ? `${mem.value} ${mem.unit ?? ''}` : '—'}
                      </td>
                      <td className="px-5 py-3">
                        <StatusBadge status={mem.status} size="sm" />
                      </td>
                      <td className="px-5 py-3 font-mono text-[11px] text-[#667085]">
                        {mem.author_agent}
                      </td>
                      <td className="px-5 py-3 text-right font-mono tabular-nums text-[#667085]">
                        {mem.token_count}
                      </td>
                      <td className="px-5 py-3 text-right">
                        <span className="text-xs font-medium text-[#5558D9] hover:underline inline-flex items-center gap-1">
                          Inspect <ArrowRight className="w-3 h-3" />
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={8} className="px-5 py-8 text-center text-xs text-[#98A2B3]">
                      No memory units found matching filter criteria.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Conflict Audits Log */
        <div className="bg-white rounded-lg border border-[#E6E8EC] overflow-hidden shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
          <div className="px-5 py-3.5 border-b border-[#E6E8EC]">
            <h2 className="text-xs font-semibold text-[#20242C] uppercase tracking-tight">
              Conflict Resolution Audit Log
            </h2>
            <p className="text-xs text-[#667085] mt-0.5">
              Auditable records of write-time contradiction detection and superseding decisions
            </p>
          </div>

          <div className="divide-y divide-[#F2F4F7]">
            {conflictAudits.length > 0 ? (
              conflictAudits.map((audit) => (
                <div key={audit.id} className="p-4 hover:bg-[#F8F9FB] transition-colors flex flex-col sm:flex-row sm:items-start justify-between gap-3 text-xs">
                  <div className="space-y-1 max-w-2xl">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-[#20242C]">{audit.topic}</span>
                      <StatusBadge status={audit.resolution_type} size="sm" />
                    </div>
                    <p className="text-xs text-[#667085] leading-relaxed">{audit.explanation}</p>
                    <div className="flex items-center gap-3 text-[11px] font-mono text-[#98A2B3] pt-0.5">
                      <span>Winning ID: <strong className="text-[#15966B]">{audit.winning_memory_id}</strong></span>
                      {audit.superseded_memory_id && (
                        <span>Superseded ID: <strong className="text-[#C58B24]">{audit.superseded_memory_id}</strong></span>
                      )}
                    </div>
                  </div>
                  <span className="font-mono text-[10px] text-[#98A2B3] shrink-0">
                    {audit.created_at || 'Recorded'}
                  </span>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-xs text-[#98A2B3]">
                No conflict resolution events recorded.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Slide-over Detail Modal */}
      <MemoryDetailModal
        memory={selectedMemory}
        onClose={() => setSelectedMemory(null)}
        onInspectSuperseding={handleInspectSuperseding}
      />
    </div>
  );
};
