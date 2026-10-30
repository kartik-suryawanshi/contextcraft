from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import time
from backend.app.graph.state import GraphState
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger
from backend.app.providers.llm import BaseLLMProvider, MockLLMProvider


class BaseAgent(ABC):
    """Abstract base class for all specialized LangGraph agents in ContextCraft."""

    def __init__(self, role_name: str, llm_provider: Optional[BaseLLMProvider] = None):
        self.role_name = role_name
        self.llm = llm_provider or MockLLMProvider()

    @abstractmethod
    def run_step(
        self,
        state: GraphState,
        memory_orchestrator: ContextCraftOrchestrator,
        trace_logger: Optional[TraceLogger] = None,
    ) -> Dict[str, Any]:
        """Executes the agent's task, querying memory views and logging traces."""
        pass

    def _execute_with_telemetry(
        self,
        state: GraphState,
        memory_orchestrator: ContextCraftOrchestrator,
        trace_logger: Optional[TraceLogger],
        execute_fn,
    ) -> Dict[str, Any]:
        start_time = datetime.now(timezone.utc)
        t0 = time.perf_counter()

        # Step 1: Read role-specific memory view from ContextCraft
        mem_view = memory_orchestrator.get_memory_view_for_agent(
            agent_role=self.role_name,
            task_query=state["user_query"],
            execution_id=state.get("execution_id"),
        )
        input_ids = [c.memory_unit.id for c in mem_view.selected_candidates]

        error_info = None
        result_text = ""
        output_ids = []
        updates = {}

        try:
            updates, result_text, output_ids = execute_fn(mem_view)
        except Exception as ex:
            error_info = str(ex)
            updates = {"error_status": error_info, "execution_status": "failed"}

        t1 = time.perf_counter()
        end_time = datetime.now(timezone.utc)
        duration_ms = (t1 - t0) * 1000.0

        # Step 2: Log trace telemetry
        if trace_logger and state.get("execution_id"):
            trace_logger.log_agent_step(
                execution_id=state["execution_id"],
                agent_name=self.role_name,
                execution_status="failed" if error_info else "completed",
                start_time=start_time,
                end_time=end_time,
                duration_ms=duration_ms,
                input_memory_ids=input_ids,
                output_memory_ids=output_ids,
                memory_view_size=len(input_ids),
                estimated_token_count=mem_view.tokens_consumed,
                agent_execution_result=result_text,
                error_info=error_info,
                step_order=state.get("step_count", 0) + 1,
            )

        return updates
