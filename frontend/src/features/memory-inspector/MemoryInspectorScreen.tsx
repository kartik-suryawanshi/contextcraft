import React, { useState, useEffect } from 'react';
import {
  Coins,
  Bot,
  AlertCircle,
  CheckCircle2,
  Ban,
} from 'lucide-react';
import { api } from '../../services/api';
import type { ExecutionRecord, MemoryViewLog } from '../../types';

interface MemoryInspectorScreenProps {
  selectedExecutionId?: string | null;
}

export const MemoryInspectorScreen: React.FC<MemoryInspectorScreenProps> = ({
  selectedExecutionId,
}) => {
  const [executions, setExecutions] = useState<ExecutionRecord[]>([]);
  const [activeExecId, setActiveExecId] = useState<string | null>(selectedExecutionId || null);
  const [memoryViews, setMemoryViews] = useState<MemoryViewLog[]>([]);
  const [selectedRole, setSelectedRole] = useState<string>('executor');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getExecutions(10).then((res) => {
      setExecutions(res);
      if (!activeExecId && res.length > 0) {
        setActiveExecId(res[0].id);
      }
    });
  }, []);

  useEffect(() => {
    if (selectedExecutionId) {
      setActiveExecId(selectedExecutionId);
    }
  }, [selectedExecutionId]);

  useEffect(() => {
    if (!activeExecId) return;
    setLoading(true);
    api.getExecutionMemoryViews(activeExecId)
      .then((views) => {
        setMemoryViews(views);
        if (views.length > 0 && !views.some((v) => v.agent_name.toLowerCase() === selectedRole)) {
          setSelectedRole(views[0].agent_name.toLowerCase());
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [activeExecId]);

  const activeView = memoryViews.find(
    (v) => v.agent_name.toLowerCase() === selectedRole.toLowerCase()
  );

  const budgetRemaining = activeView ? Math.max(0, activeView.token_budget - activeView.tokens_consumed) : 0;
  const budgetPercent = activeView ? Math.min(100, Math.round((activeView.tokens_consumed / activeView.token_budget) * 100)) : 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2">
        <div>
          <h1 className="text-xl font-semibold text-[#20242C] tracking-tight">Memory View Inspector</h1>
          <p className="text-xs text-[#667085] mt-1">
            Explainable context delivery: inspect role scoring, token budgeting, and fact exclusion.
          </p>
        </div>

        {/* Execution Selector */}
        <div className="flex items-center gap-2 text-xs">
          <label className="text-[#667085] font-medium">Execution:</label>
          <select
            value={activeExecId || ''}
            onChange={(e) => setActiveExecId(e.target.value)}
            className="bg-[#F8F9FB] border border-[#E6E8EC] rounded-md px-2.5 py-1 text-xs text-[#20242C] focus:outline-none focus:border-[#5558D9] font-mono"
          >
            {executions.map((e) => (
              <option key={e.id} value={e.id}>
                {e.id} - {e.user_query.slice(0, 30)}...
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Role Selector Tabs */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
        {['supervisor', 'planner', 'retriever', 'executor', 'critic'].map((role) => {
          const viewForRole = memoryViews.find((v) => v.agent_name.toLowerCase() === role);
          const isSelected = selectedRole === role;

          return (
            <button
              key={role}
              onClick={() => setSelectedRole(role)}
              className={`px-3 py-1.5 text-xs font-medium rounded-md border transition flex items-center gap-1.5 ${
                isSelected
                  ? 'bg-[#20242C] border-[#20242C] text-white font-semibold'
                  : 'bg-white border-[#E6E8EC] text-[#667085] hover:text-[#20242C] hover:bg-[#F8F9FB]'
              }`}
            >
              <Bot className="w-3.5 h-3.5" />
              <span className="capitalize">{role}</span>
              {viewForRole && (
                <span className={`text-[10px] font-mono px-1 py-0.2 rounded ${
                  isSelected ? 'bg-white/20 text-white' : 'bg-[#F2F4F7] text-[#667085]'
                }`}>
                  {viewForRole.tokens_consumed}/{viewForRole.token_budget}t
                </span>
              )}
            </button>
          );
        })}
      </div>

      {activeView ? (
        <div className="space-y-6">
          {/* Token Budget Utilization Bar */}
          <div className="bg-white rounded-lg border border-[#E6E8EC] p-5 shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-semibold text-[#20242C] uppercase tracking-tight">
                Token Budget Utilization ({selectedRole.toUpperCase()})
              </span>
              <span className="text-xs font-mono text-[#667085] tabular-nums">
                Budget: <strong className="text-[#20242C]">{activeView.token_budget}</strong> tokens · Used:{' '}
                <strong className="text-[#5558D9]">{activeView.tokens_consumed}</strong> ({budgetPercent}%) · Remaining:{' '}
                <strong className="text-[#15966B]">{budgetRemaining}</strong> tokens
              </span>
            </div>

            <div className="w-full bg-[#F2F4F7] rounded-full h-2 overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-300 ${
                  activeView.tokens_consumed > activeView.token_budget
                    ? 'bg-[#D84A5B]'
                    : 'bg-[#5558D9]'
                }`}
                style={{ width: `${budgetPercent}%` }}
              />
            </div>

            <div className="flex items-center justify-between text-[11px] text-[#667085] mt-2.5">
              <span>{activeView.selected_units.length} memory units selected into agent view</span>
              <span>{activeView.excluded_units.length} memory units excluded</span>
            </div>
          </div>

          {/* Selected Memory Units */}
          <div className="bg-white rounded-lg border border-[#E6E8EC] overflow-hidden shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
            <div className="px-5 py-3.5 border-b border-[#E6E8EC]">
              <h2 className="text-xs font-semibold text-[#20242C] uppercase tracking-tight">
                Selected Memory Units in Context Payload
              </h2>
              <p className="text-xs text-[#667085] mt-0.5">
                Evaluated and ranked using: Total Score = Relevance + Recency + Importance + Role Need
              </p>
            </div>

            <div className="divide-y divide-[#F2F4F7]">
              {activeView.selected_units.length > 0 ? (
                activeView.selected_units.map((unit) => (
                  <div key={unit.id} className="p-4 hover:bg-[#F8F9FB] transition-colors space-y-2">
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-xs font-semibold text-[#5558D9]">{unit.id}</span>
                          <span className="text-[11px] font-medium text-[#667085] bg-[#F2F4F7] px-2 py-0.5 rounded border border-[#E4E7EC]">
                            {unit.topic}
                          </span>
                        </div>
                        <p className="text-xs font-medium text-[#20242C] leading-relaxed">{unit.fact_text}</p>
                      </div>

                      <div className="text-right shrink-0">
                        <span className="text-[10px] text-[#98A2B3] block">Total Score</span>
                        <span className="font-mono text-sm font-semibold text-[#15966B] tabular-nums">
                          {unit.total_score}
                        </span>
                      </div>
                    </div>

                    {/* Component Scores Table / Pills */}
                    <div className="grid grid-cols-5 gap-2 pt-1.5 text-[11px] font-mono text-[#667085] tabular-nums">
                      <div className="bg-[#F8F9FB] px-2 py-1 rounded border border-[#E6E8EC]">
                        <span className="text-[#98A2B3] text-[9px] block">Relevance</span>
                        <span className="text-[#20242C] font-medium">{unit.relevance_score}</span>
                      </div>
                      <div className="bg-[#F8F9FB] px-2 py-1 rounded border border-[#E6E8EC]">
                        <span className="text-[#98A2B3] text-[9px] block">Recency</span>
                        <span className="text-[#20242C] font-medium">{unit.recency_score}</span>
                      </div>
                      <div className="bg-[#F8F9FB] px-2 py-1 rounded border border-[#E6E8EC]">
                        <span className="text-[#98A2B3] text-[9px] block">Importance</span>
                        <span className="text-[#20242C] font-medium">{unit.importance_score}</span>
                      </div>
                      <div className="bg-[#F8F9FB] px-2 py-1 rounded border border-[#E6E8EC]">
                        <span className="text-[#98A2B3] text-[9px] block">Role Need</span>
                        <span className="text-[#20242C] font-medium">{unit.role_need_score}</span>
                      </div>
                      <div className="bg-[#F8F9FB] px-2 py-1 rounded border border-[#E6E8EC]">
                        <span className="text-[#98A2B3] text-[9px] block">Token Cost</span>
                        <span className="text-[#20242C] font-medium">{unit.token_count} tok</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-xs text-[#98A2B3]">
                  No memory units selected into context.
                </div>
              )}
            </div>
          </div>

          {/* Excluded Memory Units */}
          {activeView.excluded_units.length > 0 && (
            <div className="bg-white rounded-lg border border-[#E6E8EC] overflow-hidden shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
              <div className="px-5 py-3.5 border-b border-[#E6E8EC]">
                <h2 className="text-xs font-semibold text-[#20242C] uppercase tracking-tight">
                  Excluded Memory Units
                </h2>
                <p className="text-xs text-[#667085] mt-0.5">
                  Facts filtered out due to role token limits or redundant topic information
                </p>
              </div>

              <div className="divide-y divide-[#F2F4F7]">
                {activeView.excluded_units.map((unit, idx) => (
                  <div key={unit.id || idx} className="p-3.5 hover:bg-[#F8F9FB] transition-colors flex items-center justify-between gap-3 text-xs">
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-[11px] text-[#98A2B3]">{unit.id}</span>
                        <span className="font-medium text-[10px] uppercase px-1.5 py-0.2 rounded bg-[#FDEEF0] text-[#D84A5B] border border-[#F9D5DA]">
                          {unit.reason === 'budget_exceeded' ? 'Budget Exceeded' : 'Duplicate Skipped'}
                        </span>
                      </div>
                      <p className="text-[#667085] text-xs">{unit.fact_text}</p>
                    </div>

                    <div className="flex items-center gap-4 text-right font-mono text-[11px] text-[#667085] tabular-nums shrink-0">
                      <div>
                        <span className="text-[#98A2B3] text-[9px] block">Score</span>
                        <span>{unit.total_score}</span>
                      </div>
                      <div>
                        <span className="text-[#98A2B3] text-[9px] block">Tokens</span>
                        <span>{unit.token_count}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-lg border border-[#E6E8EC] p-12 text-center text-xs text-[#98A2B3]">
          {loading ? 'Loading memory view data...' : 'No memory views available for this execution.'}
        </div>
      )}
    </div>
  );
};
