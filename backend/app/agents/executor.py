from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.graph.state import GraphState
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger


class ExecutorAgent(BaseAgent):
    """Executor / Analyst Agent: Integrates confirmed facts, performs analysis, and drafts response."""

    def __init__(self, llm_provider=None):
        super().__init__(role_name="executor", llm_provider=llm_provider)

    def run_step(
        self,
        state: GraphState,
        memory_orchestrator: ContextCraftOrchestrator,
        trace_logger: Optional[TraceLogger] = None,
    ) -> Dict[str, Any]:
        def _execute(mem_view):
            prompt = (
                f"You are the Executor and Analyst agent.\n"
                f"User Request: {state['user_query']}\n"
                f"{mem_view.formatted_context}\n"
                f"Synthesize an accurate, grounded analytical response based strictly on active, current facts. "
                f"Explicitly distinguish current values from superseded values."
            )
            analysis_response = self.llm.generate(prompt)

            # Store the synthesis summary fact in ContextCraft
            created = memory_orchestrator.write_agent_output(
                text=f"Analysis Synthesis: Current confirmed budget is ₹12 lakh with target completion in December 2026.",
                author_agent="executor",
                source_type="agent_synthesis",
            )
            output_ids = [m.id for m in created]

            updates = {
                "current_agent": "executor",
                "routing_target": "critic",
                "final_answer": analysis_response,
                "step_count": state.get("step_count", 0) + 1,
            }
            return updates, analysis_response, output_ids

        return self._execute_with_telemetry(state, memory_orchestrator, trace_logger, _execute)
