from typing import Dict
from pydantic import BaseModel


class DashboardMetricsResponse(BaseModel):
    total_executions: int
    successful_executions: int
    failed_executions: int
    total_memory_units: int
    current_memory_units: int
    superseded_memory_units: int
    conflicting_memory_units: int
    average_duration_ms: float
    total_estimated_tokens: int
    agent_distribution: Dict[str, int]
    mock_mode: bool
