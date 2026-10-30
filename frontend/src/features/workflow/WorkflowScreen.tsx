import React, { useState, useEffect, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  type Node,
  type Edge,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { AgentNode } from '../../components/AgentNode';
import { api } from '../../services/api';
import type { ExecutionRecord, TraceRecord } from '../../types';
import { Bot, Clock, Coins, Database, Layers, X } from 'lucide-react';
import { StatusBadge } from '../../components/StatusBadge';

interface WorkflowScreenProps {
  selectedExecutionId?: string | null;
}

const nodeTypes = {
  agentNode: AgentNode,
};

export const WorkflowScreen: React.FC<WorkflowScreenProps> = ({ selectedExecutionId }) => {
  const [executions, setExecutions] = useState<ExecutionRecord[]>([]);
  const [activeExecId, setActiveExecId] = useState<string | null>(selectedExecutionId || null);
  const [traces, setTraces] = useState<TraceRecord[]>([]);
  const [selectedAgentTrace, setSelectedAgentTrace] = useState<TraceRecord | null>(null);
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
    api.getExecutionTraces(activeExecId)
      .then((res) => {
        setTraces(res);
        if (res.length > 0) {
          setSelectedAgentTrace(res[0]);
        }
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [activeExecId]);

  const traceMap = useMemo(() => {
    const map = new Map<string, TraceRecord>();
    traces.forEach((t) => map.set(t.agent_name.toLowerCase(), t));
    return map;
  }, [traces]);

  // Clean horizontal or structured vertical layout
  const nodes: Node[] = useMemo(() => {
    const agentConfigs = [
      {
        id: 'supervisor',
        label: 'Supervisor',
        role: 'supervisor',
        description: 'Evaluates task objective and directs routing flow',
        pos: { x: 240, y: 30 },
      },
      {
        id: 'planner',
        label: 'Planner',
        role: 'planner',
        description: 'Breaks down task, defines constraints & info gaps',
        pos: { x: 240, y: 170 },
      },
      {
        id: 'retriever',
        label: 'Retriever',
        role: 'retriever',
        description: 'Fetches relevant active facts from memory store',
        pos: { x: 240, y: 310 },
      },
      {
        id: 'executor',
        label: 'Executor / Analyst',
        role: 'executor',
        description: 'Synthesizes verified facts into grounded draft',
        pos: { x: 240, y: 450 },
      },
      {
        id: 'critic',
        label: 'Critic / Verifier',
        role: 'critic',
        description: 'Audits claims, detects omissions & triggers revision',
        pos: { x: 240, y: 590 },
      },
      {
        id: 'final_response',
        label: 'Final Response',
        role: 'output',
        description: 'Grounded answer delivered with verified citations',
        pos: { x: 240, y: 730 },
      },
    ];

    return agentConfigs.map((cfg) => {
      const trace = traceMap.get(cfg.role);
      const isCompleted = !!trace;

      return {
        id: cfg.id,
        type: 'agentNode',
        position: cfg.pos,
        data: {
          label: cfg.label,
          role: cfg.role,
          description: cfg.description,
          status: isCompleted ? 'completed' : 'idle',
          stepOrder: trace?.step_order,
          durationMs: trace?.duration_ms,
          tokens: trace?.estimated_token_count,
          memoryCount: trace?.memory_view_size,
          isCurrent: selectedAgentTrace?.agent_name.toLowerCase() === cfg.role,
        },
      };
    });
  }, [traceMap, selectedAgentTrace]);

  const edges: Edge[] = useMemo(() => {
    return [
      {
        id: 'e-sup-plan',
        source: 'supervisor',
        target: 'planner',
        style: { stroke: '#94A3B8', strokeWidth: 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#94A3B8' },
      },
      {
        id: 'e-plan-ret',
        source: 'planner',
        target: 'retriever',
        style: { stroke: '#94A3B8', strokeWidth: 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#94A3B8' },
      },
      {
        id: 'e-ret-exec',
        source: 'retriever',
        target: 'executor',
        style: { stroke: '#94A3B8', strokeWidth: 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#94A3B8' },
      },
      {
        id: 'e-exec-crit',
        source: 'executor',
        target: 'critic',
        style: { stroke: '#94A3B8', strokeWidth: 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#94A3B8' },
      },
      {
        id: 'e-crit-out',
        source: 'critic',
        target: 'final_response',
        label: 'Passed Audit',
        labelStyle: { fill: '#15966B', fontSize: 10, fontWeight: 500 },
        labelBgStyle: { fill: '#FFFFFF', rx: 3, ry: 3, stroke: '#E6E8EC' },
        style: { stroke: '#15966B', strokeWidth: 1.5 },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#15966B' },
      },
      {
        id: 'e-crit-revision',
        source: 'critic',
        target: 'planner',
        type: 'smoothstep',
        label: 'Revision Loop (if audit fails)',
        labelStyle: { fill: '#D84A5B', fontSize: 10, fontWeight: 500 },
        labelBgStyle: { fill: '#FFFFFF', rx: 3, ry: 3, stroke: '#E6E8EC' },
        style: { stroke: '#D84A5B', strokeWidth: 1.5, strokeDasharray: '4,4' },
        markerEnd: { type: MarkerType.ArrowClosed, color: '#D84A5B' },
      },
    ];
  }, []);

  const handleNodeClick = (_: any, node: Node) => {
    const trace = traceMap.get(node.data.role as string);
    if (trace) {
      setSelectedAgentTrace(trace);
    }
  };

  const currentExecution = executions.find((e) => e.id === activeExecId);

  return (
    <div className="space-y-4">
      {/* Top Bar */}
      <div className="bg-white rounded-lg border border-[#E6E8EC] px-5 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
        <div>
          <h1 className="text-sm font-semibold text-[#20242C]">Agent Workflow Architecture</h1>
          <p className="text-xs text-[#667085] mt-0.5">
            Supervisor → Planner → Retriever → Executor → Critic with isolated memory views
          </p>
        </div>

        <div className="flex items-center gap-2 text-xs">
          <label className="text-[#667085] font-medium">Execution:</label>
          <select
            value={activeExecId || ''}
            onChange={(e) => setActiveExecId(e.target.value)}
            className="bg-[#F8F9FB] border border-[#E6E8EC] rounded-md px-2.5 py-1 text-xs text-[#20242C] focus:outline-none focus:border-[#5558D9] font-mono"
          >
            {executions.map((e) => (
              <option key={e.id} value={e.id}>
                {e.id} ({e.status})
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Area: React Flow Canvas & Side Detail Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[720px]">
        {/* Canvas */}
        <div className="lg:col-span-8 bg-white rounded-lg border border-[#E6E8EC] overflow-hidden relative shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            nodeTypes={nodeTypes}
            onNodeClick={handleNodeClick}
            fitView
            fitViewOptions={{ padding: 0.15 }}
            minZoom={0.5}
            maxZoom={1.5}
          >
            <Background color="#E2E8F0" gap={18} size={1} />
            <Controls className="!bg-white !border-[#E6E8EC] !text-[#667085]" />
          </ReactFlow>

          <div className="absolute top-3 left-3 bg-white/95 px-2.5 py-1 rounded border border-[#E6E8EC] text-[11px] text-[#667085] shadow-xs">
            Click any agent node to inspect telemetry and memory views
          </div>
        </div>

        {/* Side Panel: Agent Telemetry Drawer */}
        <div className="lg:col-span-4 bg-white rounded-lg border border-[#E6E8EC] p-5 flex flex-col justify-between overflow-y-auto shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
          <div>
            <div className="flex items-center justify-between pb-3 border-b border-[#F2F4F7]">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-[#5558D9]" />
                <h2 className="text-xs font-semibold text-[#20242C] uppercase tracking-tight">
                  {selectedAgentTrace ? selectedAgentTrace.agent_name : 'Agent Detail'}
                </h2>
              </div>
              {selectedAgentTrace && (
                <span className="font-mono text-[10px] text-[#98A2B3]">
                  Step #{selectedAgentTrace.step_order}
                </span>
              )}
            </div>

            {selectedAgentTrace ? (
              <div className="mt-4 space-y-4 text-xs">
                {/* Latency & Tokens Stats */}
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-[#F8F9FB] p-2.5 rounded border border-[#E6E8EC]">
                    <span className="text-[10px] text-[#98A2B3] block">Duration</span>
                    <span className="font-mono text-xs font-semibold text-[#20242C]">
                      {selectedAgentTrace.duration_ms} ms
                    </span>
                  </div>
                  <div className="bg-[#F8F9FB] p-2.5 rounded border border-[#E6E8EC]">
                    <span className="text-[10px] text-[#98A2B3] block">Tokens</span>
                    <span className="font-mono text-xs font-semibold text-[#20242C]">
                      {selectedAgentTrace.estimated_token_count}
                    </span>
                  </div>
                  <div className="bg-[#F8F9FB] p-2.5 rounded border border-[#E6E8EC]">
                    <span className="text-[10px] text-[#98A2B3] block">Memories</span>
                    <span className="font-mono text-xs font-semibold text-[#20242C]">
                      {selectedAgentTrace.memory_view_size}
                    </span>
                  </div>
                </div>

                {/* Input Context Memory IDs */}
                <div>
                  <span className="text-[11px] font-medium text-[#667085] block mb-1">
                    Input Memory Units Received:
                  </span>
                  <div className="flex flex-wrap gap-1">
                    {selectedAgentTrace.input_memory_ids.length > 0 ? (
                      selectedAgentTrace.input_memory_ids.map((id) => (
                        <span key={id} className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-[#F2F4F7] text-[#20242C] border border-[#E4E7EC]">
                          {id}
                        </span>
                      ))
                    ) : (
                      <span className="text-[#98A2B3] text-[11px] italic">None (initial turn)</span>
                    )}
                  </div>
                </div>

                {/* Newly Produced Memory Units */}
                {selectedAgentTrace.output_memory_ids.length > 0 && (
                  <div>
                    <span className="text-[11px] font-medium text-[#667085] block mb-1">
                      Committed Memory Units:
                    </span>
                    <div className="flex flex-wrap gap-1">
                      {selectedAgentTrace.output_memory_ids.map((id) => (
                        <span key={id} className="font-mono text-[10px] px-1.5 py-0.5 rounded bg-[#E8F7F0] text-[#15966B] border border-[#D1F0E2]">
                          {id}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Agent Reasoning Output */}
                <div>
                  <span className="text-[11px] font-medium text-[#667085] block mb-1">
                    Agent Execution Output:
                  </span>
                  <div className="bg-[#F8F9FB] rounded border border-[#E6E8EC] p-3 font-mono text-[11px] text-[#20242C] leading-relaxed max-h-60 overflow-y-auto whitespace-pre-wrap">
                    {selectedAgentTrace.agent_execution_result || 'No output recorded'}
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-16 text-center text-[#98A2B3] text-xs">
                Select an agent node in the workflow canvas.
              </div>
            )}
          </div>

          {currentExecution && (
            <div className="pt-3 border-t border-[#F2F4F7] text-xs text-[#98A2B3]">
              <span className="font-medium text-[#667085]">Task Objective:</span>
              <p className="mt-0.5 line-clamp-2 text-[#667085]">{currentExecution.user_query}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
