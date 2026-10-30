from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ExecutionCreateRequest(BaseModel):
    query: str = Field(..., description="User task or complex query to execute")
    max_iterations: int = Field(2, ge=1, le=5, description="Maximum revision iterations")
    mock_mode: bool = Field(True, description="Whether to run in deterministic mock mode")


class ExecutionResponse(BaseModel):
    id: str
    user_query: str
    status: str
    iteration_count: int
    final_answer: Optional[str] = None
    total_duration_ms: float
    total_tokens_estimated: int
    error_status: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TraceResponse(BaseModel):
    id: str
    execution_id: str
    agent_name: str
    execution_status: str
    start_timestamp: Optional[str] = None
    end_timestamp: Optional[str] = None
    duration_ms: float
    input_memory_ids: List[str]
    output_memory_ids: List[str]
    memory_view_size: int
    estimated_token_count: int
    agent_execution_result: Optional[str] = None
    error_info: Optional[str] = None
    step_order: int


class MemoryViewItem(BaseModel):
    id: str
    fact_text: str
    topic: str
    value: Optional[str] = None
    relevance_score: float
    recency_score: float
    importance_score: float
    role_need_score: float
    total_score: float
    token_count: int


class ExcludedMemoryItem(BaseModel):
    id: str
    fact_text: str
    topic: str
    reason: str
    total_score: float
    token_count: int


class MemoryViewLogResponse(BaseModel):
    id: str
    execution_id: str
    agent_name: str
    token_budget: int
    tokens_consumed: int
    selected_units: List[Dict[str, Any]]
    excluded_units: List[Dict[str, Any]]
    created_at: Optional[str] = None
