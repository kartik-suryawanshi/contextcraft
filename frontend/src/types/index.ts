export interface MemoryUnit {
  id: string;
  fact_text: string;
  topic: string;
  value?: string | null;
  unit?: string | null;
  source_document?: string | null;
  source_page?: number | null;
  version_date?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  author_agent: string;
  source_type: string;
  confidence: number;
  importance: number;
  status: 'current' | 'superseded' | 'conflicting';
  token_count: number;
  embedding?: number[] | null;
  superseded_by?: string | null;
  conflict_reason?: string | null;
}

export interface MemoryListResponse {
  total: number;
  items: MemoryUnit[];
}

export interface ConflictAuditEvent {
  id: string;
  topic: string;
  winning_memory_id: string;
  superseded_memory_id?: string | null;
  conflicting_memory_id?: string | null;
  resolution_type: string;
  explanation: string;
  created_at?: string | null;
}

export interface ExecutionRecord {
  id: string;
  user_query: string;
  status: 'running' | 'completed' | 'failed';
  iteration_count: number;
  final_answer?: string | null;
  total_duration_ms: number;
  total_tokens_estimated: number;
  error_status?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface TraceRecord {
  id: string;
  execution_id: string;
  agent_name: string;
  execution_status: string;
  start_timestamp?: string | null;
  end_timestamp?: string | null;
  duration_ms: number;
  input_memory_ids: string[];
  output_memory_ids: string[];
  memory_view_size: number;
  estimated_token_count: number;
  agent_execution_result?: string | null;
  error_info?: string | null;
  step_order: number;
}

export interface SelectedUnitScoring {
  id: string;
  fact_text: string;
  topic: string;
  value?: string | null;
  relevance_score: number;
  recency_score: number;
  importance_score: number;
  role_need_score: number;
  total_score: number;
  token_count: number;
}

export interface ExcludedUnit {
  id: string;
  fact_text: string;
  topic: string;
  reason: 'budget_exceeded' | 'duplicate';
  total_score: number;
  token_count: number;
}

export interface MemoryViewLog {
  id: string;
  execution_id: string;
  agent_name: string;
  token_budget: number;
  tokens_consumed: number;
  selected_units: SelectedUnitScoring[];
  excluded_units: ExcludedUnit[];
  created_at?: string | null;
}

export interface DashboardMetrics {
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  total_memory_units: number;
  current_memory_units: number;
  superseded_memory_units: number;
  conflicting_memory_units: number;
  average_duration_ms: number;
  total_estimated_tokens: number;
  agent_distribution: Record<string, number>;
  mock_mode: boolean;
}

export interface HealthStatus {
  status: string;
  service: string;
  database: string;
  mock_mode: boolean;
}
