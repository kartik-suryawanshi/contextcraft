from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.graph.state import GraphState
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger


class RetrieverAgent(BaseAgent):
    """Retriever Agent: Evaluates memory gaps and retrieves pertinent factual context."""

    def __init__(self, llm_provider=None):
        super().__init__(role_name="retriever", llm_provider=llm_provider)

    def run_step(
        self,
        state: GraphState,
        memory_orchestrator: ContextCraftOrchestrator,
        trace_logger: Optional[TraceLogger] = None,
    ) -> Dict[str, Any]:
        def _execute(mem_view):
            prompt = (
                f"You are the Retriever agent.\n"
                f"Objective: {state['user_query']}\n"
                f"{mem_view.formatted_context}\n"
                f"Identify retrieved factual evidence and verify presence of required parameters."
            )
            response = self.llm.generate(prompt)

            updates = {
                "current_agent": "retriever",
                "routing_target": "executor",
                "step_count": state.get("step_count", 0) + 1,
            }
            return updates, response, []

        return self._execute_with_telemetry(state, memory_orchestrator, trace_logger, _execute)
