import React, { useEffect, useState } from 'react';
import {
  RefreshCw,
  ArrowRight,
  Database,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { MetricCard } from '../../components/MetricCard';
import { StatusBadge } from '../../components/StatusBadge';
import { api } from '../../services/api';
import type { DashboardMetrics, ExecutionRecord } from '../../types';

interface DashboardScreenProps {
  onNavigateToExecution?: (id: string) => void;
}

export const DashboardScreen: React.FC<DashboardScreenProps> = ({ onNavigateToExecution }) => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [recentExecutions, setRecentExecutions] = useState<ExecutionRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [m, execs] = await Promise.all([
        api.getDashboardMetrics(),
        api.getExecutions(8),
      ]);
      setMetrics(m);
      setRecentExecutions(execs);
    } catch (err) {
      console.error('Failed to load dashboard metrics', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    try {
      await api.seedDemoData();
      await loadData();
    } catch (err) {
      console.error('Failed to seed demo data', err);
    } finally {
      setSeeding(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const agentChartData = metrics?.agent_distribution
    ? ['supervisor', 'planner', 'retriever', 'executor', 'critic'].map((role) => ({
        name: role.charAt(0).toUpperCase() + role.slice(1),
        count: metrics.agent_distribution[role] || 0,
      }))
    : [];

  const memoryStatusData = metrics
    ? [
        { name: 'Current', value: metrics.current_memory_units, color: '#15966B' },
        { name: 'Superseded', value: metrics.superseded_memory_units, color: '#C58B24' },
        { name: 'Conflicting', value: metrics.conflicting_memory_units, color: '#D84A5B' },
      ].filter((d) => d.value > 0)
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2">
        <div>
          <h1 className="text-xl font-semibold text-[#20242C] tracking-tight">Overview</h1>
          <p className="text-xs text-[#667085] mt-1">
            Monitor agent execution, memory lifecycle and context efficiency.
          </p>
        </div>
        <div className="flex items-center gap-2">
          {(!metrics || metrics.total_executions === 0) && (
            <button
              onClick={handleSeed}
              disabled={seeding}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-[#5558D9] text-white hover:bg-[#4346B8] transition shadow-xs disabled:opacity-50"
            >
              <Database className="w-3.5 h-3.5" />
              <span>{seeding ? 'Seeding Data...' : 'Seed Demo Data'}</span>
            </button>
          )}
          <button
            onClick={loadData}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-md bg-white border border-[#E6E8EC] text-[#20242C] hover:bg-[#F8F9FB] transition shadow-xs disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#667085] ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* KPI Section */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          label="Total Executions"
          value={metrics?.total_executions ?? 0}
          secondaryInfo={`${metrics?.successful_executions ?? 0} successful · ${metrics?.failed_executions ?? 0} failed`}
        />
        <MetricCard
          label="Active Memories"
          value={metrics?.current_memory_units ?? 0}
          secondaryInfo={`${metrics?.current_memory_units ?? 0} active of ${metrics?.total_memory_units ?? 0} total stored facts`}
        />
        <MetricCard
          label="Superseded Facts"
          value={metrics?.superseded_memory_units ?? 0}
          secondaryInfo="Historical records preserved without deletion"
        />
        <MetricCard
          label="Tokens Managed"
          value={metrics ? metrics.total_estimated_tokens.toLocaleString() : '0'}
          secondaryInfo={`Avg execution latency: ${metrics?.average_duration_ms ?? 0} ms`}
        />
      </div>

      {/* Analytics Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Agent Execution Distribution */}
        <div className="lg:col-span-7 bg-white rounded-lg border border-[#E6E8EC] p-5 shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
          <div className="mb-4">
            <h2 className="text-xs font-semibold text-[#20242C] tracking-tight uppercase">
              Agent Execution Distribution
            </h2>
            <p className="text-xs text-[#667085] mt-0.5">
              Invocations across specialized LangGraph agent nodes
            </p>
          </div>
          <div className="h-56 w-full">
            {agentChartData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={agentChartData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <XAxis dataKey="name" stroke="#98A2B3" fontSize={11} tickLine={false} axisLine={{ stroke: '#E6E8EC' }} />
                  <YAxis stroke="#98A2B3" fontSize={11} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip
                    cursor={{ fill: '#F8F9FB' }}
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      border: '1px solid #E6E8EC',
                      borderRadius: '6px',
                      fontSize: '11px',
                      boxShadow: '0 2px 4px rgba(16, 24, 40, 0.06)',
                    }}
                    labelStyle={{ color: '#20242C', fontWeight: 600 }}
                  />
                  <Bar dataKey="count" fill="#5558D9" radius={[4, 4, 0, 0]} maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-[#98A2B3]">
                No trace data available yet.
              </div>
            )}
          </div>
        </div>

        {/* Right: Memory Lifecycle */}
        <div className="lg:col-span-5 bg-white rounded-lg border border-[#E6E8EC] p-5 shadow-[0_1px_2px_0_rgba(16,24,40,0.04)] flex flex-col justify-between">
          <div>
            <h2 className="text-xs font-semibold text-[#20242C] tracking-tight uppercase">
              Memory Lifecycle Status
            </h2>
            <p className="text-xs text-[#667085] mt-0.5">
              Active facts vs. superseded revisions vs. unresolved conflicts
            </p>
          </div>

          <div className="h-44 w-full my-auto">
            {memoryStatusData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={memoryStatusData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={46}
                    outerRadius={66}
                    paddingAngle={3}
                  >
                    {memoryStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#FFFFFF',
                      border: '1px solid #E6E8EC',
                      borderRadius: '6px',
                      fontSize: '11px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-[#98A2B3]">
                No memory records stored.
              </div>
            )}
          </div>

          <div className="grid grid-cols-3 gap-2 pt-3 border-t border-[#F2F4F7] text-xs">
            <div className="flex flex-col">
              <span className="flex items-center gap-1.5 text-[#15966B] font-medium">
                <span className="w-2 h-2 rounded-full bg-[#15966B]" /> Current
              </span>
              <span className="text-sm font-semibold text-[#20242C] font-mono mt-0.5">
                {metrics?.current_memory_units ?? 0}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="flex items-center gap-1.5 text-[#C58B24] font-medium">
                <span className="w-2 h-2 rounded-full bg-[#C58B24]" /> Superseded
              </span>
              <span className="text-sm font-semibold text-[#20242C] font-mono mt-0.5">
                {metrics?.superseded_memory_units ?? 0}
              </span>
            </div>
            <div className="flex flex-col">
              <span className="flex items-center gap-1.5 text-[#D84A5B] font-medium">
                <span className="w-2 h-2 rounded-full bg-[#D84A5B]" /> Conflicting
              </span>
              <span className="text-sm font-semibold text-[#20242C] font-mono mt-0.5">
                {metrics?.conflicting_memory_units ?? 0}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Executions Table */}
      <div className="bg-white rounded-lg border border-[#E6E8EC] overflow-hidden shadow-[0_1px_2px_0_rgba(16,24,40,0.04)]">
        <div className="px-5 py-3.5 border-b border-[#E6E8EC] flex items-center justify-between">
          <div>
            <h2 className="text-xs font-semibold text-[#20242C] uppercase tracking-tight">
              Recent Executions
            </h2>
            <p className="text-xs text-[#667085] mt-0.5">
              Recent multi-agent workflow runs and recorded telemetry
            </p>
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-[#F8F9FB] text-[11px] font-medium text-[#667085] border-b border-[#E6E8EC]">
              <tr>
                <th className="px-5 py-2.5">Execution ID</th>
                <th className="px-5 py-2.5">User Query</th>
                <th className="px-5 py-2.5">Status</th>
                <th className="px-5 py-2.5 text-right">Tokens Used</th>
                <th className="px-5 py-2.5 text-right">Duration</th>
                <th className="px-5 py-2.5 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#F2F4F7]">
              {recentExecutions.length > 0 ? (
                recentExecutions.map((exec) => (
                  <tr
                    key={exec.id}
                    onClick={() => onNavigateToExecution?.(exec.id)}
                    className="hover:bg-[#F8F9FB] transition-colors cursor-pointer"
                  >
                    <td className="px-5 py-3 font-mono text-[11px] font-medium text-[#5558D9]">
                      {exec.id}
                    </td>
                    <td className="px-5 py-3 max-w-sm truncate text-[#20242C]" title={exec.user_query}>
                      {exec.user_query}
                    </td>
                    <td className="px-5 py-3">
                      <StatusBadge status={exec.status} size="sm" />
                    </td>
                    <td className="px-5 py-3 text-right font-mono tabular-nums text-[#667085]">
                      {exec.total_tokens_estimated.toLocaleString()}
                    </td>
                    <td className="px-5 py-3 text-right font-mono tabular-nums text-[#667085]">
                      {exec.total_duration_ms} ms
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
                  <td colSpan={6} className="px-5 py-8 text-center text-xs text-[#98A2B3]">
                    No executions recorded. Run a query in the Playground.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
