from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import json
import uuid
from backend.app.database.models import ExecutionTraceModel, utc_now
from backend.app.database.repository import TraceRepository


class TraceLogger:
    """Logs and persists step-by-step agent execution traces."""

    def __init__(self, trace_repo: TraceRepository):
        self.trace_repo = trace_repo

    def log_agent_step(
        self,
        execution_id: str,
        agent_name: str,
        execution_status: str,
        start_time: datetime,
        end_time: datetime,
        duration_ms: float,
        input_memory_ids: List[str],
        output_memory_ids: List[str],
        memory_view_size: int,
        estimated_token_count: int,
        agent_execution_result: Optional[str] = None,
        error_info: Optional[str] = None,
        step_order: int = 0,
    ) -> ExecutionTraceModel:
        trace = ExecutionTraceModel(
            id=f"trc-{uuid.uuid4().hex[:10]}",
            execution_id=execution_id,
            agent_name=agent_name,
            execution_status=execution_status,
            start_timestamp=start_time,
            end_timestamp=end_time,
            duration_ms=round(duration_ms, 2),
            input_memory_ids=json.dumps(input_memory_ids),
            output_memory_ids=json.dumps(output_memory_ids),
            memory_view_size=memory_view_size,
            estimated_token_count=estimated_token_count,
            agent_execution_result=agent_execution_result,
            error_info=error_info,
            step_order=step_order,
        )
        return self.trace_repo.create_trace(trace)
