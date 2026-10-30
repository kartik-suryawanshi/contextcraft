import React, { useState } from 'react';
import {
  Play,
  RotateCcw,
  Clock,
  Coins,
  CheckCircle2,
  AlertCircle,
  ArrowRight,
  Layers,
  Bot,
  ExternalLink,
} from 'lucide-react';
import { api } from '../../services/api';
import type { ExecutionRecord, TraceRecord } from '../../types';
import { StatusBadge } from '../../components/StatusBadge';

const DEMO_ORION_PROMPT =
  'Prepare an analysis of Project Orion. Its original budget was ₹10 lakh, the deadline was December 2026, and the project budget was later revised to ₹12 lakh. Explain the current project status using the available information.';

interface ExecutionPlaygroundScreenProps {
  onInspectWorkflow?: (executionId: string) => void;
  onInspectMemoryViews?: (executionId: string) => void;
}

export const ExecutionPlaygroundScreen: React.FC<ExecutionPlaygroundScreenProps> = ({
  onInspectWorkflow,
  onInspectMemoryViews,
}) => {
  const [query, setQuery] = useState(DEMO_ORION_PROMPT);
  const [maxIterations, setMaxIterations] = useState(2);
  const [mockMode, setMockMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [executionResult, setExecutionResult] = useState<ExecutionRecord | null>(null);
  const [traces, setTraces] = useState<TraceRecord[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleRunExecution = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setExecutionResult(null);
    setTraces([]);

    try {
      const res = await api.createExecution(query, maxIterations, mockMode);
      setExecutionResult(res);

      const traceLogs = await api.getExecutionTraces(res.id);
      setTraces(traceLogs);
    } catch (err: any) {
      setError(err.message || 'Execution failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="pb-2">
        <h1 className="text-xl font-semibold text-[#20242C] tracking-tight">Workflow Playground</h1>
        <p className="text-xs text-[#667085] mt-1">
          Execute multi-agent workflows and test ContextCraft in-session memory orchestration.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Main Area: Query Input & Execution Progress */}
        <div className="lg:col-span-8 space-y-4">
          <div className="bg-white rounded-lg border border-[#E6E8EC] p-5 shadow-[0_1px_2px_0_rgba(16,24,40,0.04)] space-y-4">
            <div className="flex items-center justify-between">
              <label className="text-xs font-semibold uppercase tracking-tight text-[#20242C]">
                Task Objective & Context
              </label>
              <button
                type="button"
                onClick={() => setQuery(DEMO_ORION_PROMPT)}
                className="text-xs text-[#5558D9] hover:underline font-medium inline-flex items-center gap-1"
              >
                Load Orion MVP Demo
              </button>
            </div>

            <textarea
              rows={5}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter complex task, facts, or revision parameters..."
              className="w-full bg-[#F8F9FB] border border-[#E6E8EC] rounded-md p-3 text-xs text-[#20242C] placeholder-[#98A2B3] focus:outline-none focus:border-[#5558D9] focus:bg-white leading-relaxed font-sans"
            />

            <div className="flex items-center justify-between pt-2 border-t border-[#F2F4F7]">
              <div className="flex items-center gap-4 text-xs text-[#667085]">
                <div className="flex items-center gap-1.5">
                  <span>Max Iterations:</span>
                  <select
                    value={maxIterations}
                    onChange={(e) => setMaxIterations(Number(e.target.value))}
                    className="bg-[#F8F9FB] border border-[#E6E8EC] rounded px-2 py-0.5 text-xs text-[#20242C] focus:outline-none focus:border-[#5558D9]"
                  >
                    <option value={1}>1 (Single pass)</option>
                    <option value={2}>2 (Standard)</option>
                    <option value={3}>3 (Max)</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleRunExecution}
                disabled={loading || !query.trim()}
                className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-md bg-[#5558D9] text-white hover:bg-[#484BC4] transition shadow-xs disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Clock className="w-3.5 h-3.5 animate-spin" />
                    <span>Executing Workflow...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-3.5 h-3.5 fill-current" />
                    <span>Execute Workflow</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3.5 rounded-lg bg-[#FDEEF0] border border-[#F9D5DA] text-[#D84A5B] text-xs flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Execution Progress & Output */}
          {executionResult && (
            <div className="bg-white rounded-lg border border-[#E6E8EC] p-5 shadow-[0_1px_2px_0_rgba(16,24,40,0.04)] space-y-4">
              {/* Agent Progression Horizontal Bar */}
              <div>
                <span className="text-xs font-semibold text-[#20242C] uppercase tracking-tight block mb-2">
                  Agent Execution Sequence
                </span>
                <div className="grid grid-cols-5 gap-2">
                  {['supervisor', 'planner', 'retriever', 'executor', 'critic'].map((agentName) => {
                    const trace = traces.find((t) => t.agent_name.toLowerCase() === agentName);
                    const isDone = !!trace;
                    return (
                      <div
                        key={agentName}
                        className={`p-2.5 rounded border text-center text-xs transition ${
                          isDone
                            ? 'bg-[#F8F9FB] border-[#D1F0E2]'
                            : 'bg-[#F8F9FB] border-[#E6E8EC] opacity-40'
                        }`}
                      >
                        <div className="flex items-center justify-center mb-1">
                          {isDone ? (
                            <span className="w-2 h-2 rounded-full bg-[#15966B]" />
                          ) : (
                            <span className="w-2 h-2 rounded-full bg-[#D0D5DD]" />
                          )}
                        </div>
                        <span className="font-medium text-[#20242C] capitalize block truncate">
                          {agentName}
                        </span>
                        {trace && (
                          <span className="font-mono text-[10px] text-[#667085] block mt-0.5">
                            {trace.duration_ms}ms
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Final Answer Block */}
              <div>
                <span className="text-xs font-semibold text-[#20242C] uppercase tracking-tight block mb-1.5">
                  Final Grounded Synthesis
                </span>
                <div className="bg-[#F8F9FB] rounded-lg p-4 border border-[#E6E8EC] font-sans text-xs text-[#20242C] leading-relaxed whitespace-pre-wrap">
                  {executionResult.final_answer || 'No output recorded.'}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Side Panel: Telemetry & Controls */}
        <div className="lg:col-span-4 space-y-4">
          <div className="bg-white rounded-lg border border-[#E6E8EC] p-5 shadow-[0_1px_2px_0_rgba(16,24,40,0.04)] space-y-4">
            <h2 className="text-xs font-semibold text-[#20242C] uppercase tracking-tight pb-2 border-b border-[#F2F4F7]">
              Execution Telemetry
            </h2>

            <div className="space-y-3 text-xs">
              <div className="flex items-center justify-between">
                <span className="text-[#667085]">Inference Mode</span>
                <button
                  type="button"
                  onClick={() => setMockMode(!mockMode)}
                  className="font-mono text-[11px] px-2 py-0.5 rounded bg-[#F8F9FB] border border-[#E6E8EC] hover:bg-white text-[#20242C] transition"
                >
                  {mockMode ? 'Mock (Deterministic)' : 'Live LLM API'}
                </button>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#667085]">Status</span>
                <StatusBadge status={executionResult ? executionResult.status : 'idle'} size="sm" />
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#667085]">Execution Latency</span>
                <span className="font-mono text-[#20242C] tabular-nums">
                  {executionResult ? `${executionResult.total_duration_ms} ms` : '—'}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#667085]">Token Consumption</span>
                <span className="font-mono text-[#20242C] tabular-nums">
                  {executionResult ? `${executionResult.total_tokens_estimated} tokens` : '—'}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[#667085]">Iterations</span>
                <span className="font-mono text-[#20242C]">
                  {executionResult ? executionResult.iteration_count : '—'}
                </span>
              </div>
            </div>

            {/* Quick Navigation to Inspect */}
            {executionResult && (
              <div className="pt-3 border-t border-[#F2F4F7] space-y-2">
                {onInspectWorkflow && (
                  <button
                    onClick={() => onInspectWorkflow(executionResult.id)}
                    className="w-full py-1.5 px-3 rounded text-xs font-medium bg-[#F8F9FB] hover:bg-[#F2F4F7] text-[#20242C] border border-[#E6E8EC] flex items-center justify-between transition"
                  >
                    <span>View in Agent Workflow</span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#667085]" />
                  </button>
                )}
                {onInspectMemoryViews && (
                  <button
                    onClick={() => onInspectMemoryViews(executionResult.id)}
                    className="w-full py-1.5 px-3 rounded text-xs font-medium bg-[#EEF0FD] hover:bg-[#E0E4FA] text-[#5558D9] border border-[#D6DAFB] flex items-center justify-between transition"
                  >
                    <span>Inspect Memory Views</span>
                    <ArrowRight className="w-3.5 h-3.5 text-[#5558D9]" />
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Architecture Reminder */}
          <div className="bg-[#F8F9FB] rounded-lg border border-[#E6E8EC] p-4 text-xs text-[#667085] space-y-1.5">
            <span className="font-semibold text-[#20242C] block">ContextCraft Invariant:</span>
            <p className="leading-relaxed">
              LangGraph State retains zero raw dialogue. Facts extracted during ingestion are persisted in SQLite, and agents receive role-budgeted views.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
