import {
  DashboardMetrics,
  ExecutionRecord,
  HealthStatus,
  MemoryListResponse,
  MemoryUnit,
  MemoryViewLog,
  TraceRecord,
  ConflictAuditEvent,
} from '../types';

const ENV_API_BASE = import.meta.env.VITE_API_BASE_URL ? import.meta.env.VITE_API_BASE_URL.replace(/\/$/, '') : '';
const API_BASE = `${ENV_API_BASE}/api/v1`;

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error ${response.status}: ${errorText || response.statusText}`);
  }

  return response.json();
}

export const api = {
  getHealth: () => fetchJson<HealthStatus>(`${API_BASE}/health`),

  getDashboardMetrics: () => fetchJson<DashboardMetrics>(`${API_BASE}/dashboard/metrics`),

  seedDemoData: () => fetchJson<{ status: string; message: string }>(`${API_BASE}/dashboard/seed`, { method: 'POST' }),

  getExecutions: (limit = 20, offset = 0) =>
    fetchJson<ExecutionRecord[]>(`${API_BASE}/executions?limit=${limit}&offset=${offset}`),

  getExecution: (id: string) => fetchJson<ExecutionRecord>(`${API_BASE}/executions/${id}`),

  getExecutionTraces: (id: string) =>
    fetchJson<TraceRecord[]>(`${API_BASE}/executions/${id}/traces`),

  getExecutionMemoryViews: (id: string) =>
    fetchJson<MemoryViewLog[]>(`${API_BASE}/executions/${id}/memory-views`),

  createExecution: (query: string, maxIterations = 2, mockMode = true) =>
    fetchJson<ExecutionRecord>(`${API_BASE}/executions`, {
      method: 'POST',
      body: JSON.stringify({ query, max_iterations: maxIterations, mock_mode: mockMode }),
    }),

  getMemories: (status?: string, topic?: string, author?: string, limit = 50, offset = 0) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (topic) params.append('topic', topic);
    if (author) params.append('author', author);
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    return fetchJson<MemoryListResponse>(`${API_BASE}/memories?${params.toString()}`);
  },

  getMemory: (id: string) => fetchJson<MemoryUnit>(`${API_BASE}/memories/${id}`),

  getConflictAudits: (limit = 20) =>
    fetchJson<ConflictAuditEvent[]>(`${API_BASE}/memories/audits/conflicts?limit=${limit}`),
};
