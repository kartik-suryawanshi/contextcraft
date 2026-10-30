from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.graph.state import GraphState
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger


class CriticAgent(BaseAgent):
    """Critic / Verifier Agent: Audits draft responses for factual grounding and triggers bounded revision loops."""

    def __init__(self, llm_provider=None):
        super().__init__(role_name="critic", llm_provider=llm_provider)

    def run_step(
        self,
        state: GraphState,
        memory_orchestrator: ContextCraftOrchestrator,
        trace_logger: Optional[TraceLogger] = None,
    ) -> Dict[str, Any]:
        def _execute(mem_view):
            current_draft = state.get("final_answer", "")
            iteration = state.get("iteration_count", 0)
            max_iter = state.get("max_iterations", 2)

            prompt = (
                f"You are the Critic and Verifier agent.\n"
                f"Original Objective: {state['user_query']}\n"
                f"Candidate Draft Answer: {current_draft}\n"
                f"{mem_view.formatted_context}\n"
                f"Audit this answer for factual consistency and citation accuracy. "
                f"Confirm that superseded values are not cited as current."
            )
            audit_report = self.llm.generate(prompt)

            # Determine if revision is required (e.g. if audit reports critical omission and within max iterations)
            needs_revision = "re-plan" in audit_report.lower() or "revision required" in audit_report.lower()

            if needs_revision and iteration < max_iter:
                routing_target = "planner"
                execution_status = "revision_required"
                next_iteration = iteration + 1
            else:
                routing_target = "final_response"
                execution_status = "completed"
                next_iteration = iteration

            updates = {
                "current_agent": "critic",
                "routing_target": routing_target,
                "execution_status": execution_status,
                "iteration_count": next_iteration,
                "step_count": state.get("step_count", 0) + 1,
            }
            return updates, audit_report, []

        return self._execute_with_telemetry(state, memory_orchestrator, trace_logger, _execute)
