from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.graph.state import GraphState
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger


class PlannerAgent(BaseAgent):
    """Planner Agent: Breaks down tasks, defines constraints, and identifies information needs."""

    def __init__(self, llm_provider=None):
        super().__init__(role_name="planner", llm_provider=llm_provider)

    def run_step(
        self,
        state: GraphState,
        memory_orchestrator: ContextCraftOrchestrator,
        trace_logger: Optional[TraceLogger] = None,
    ) -> Dict[str, Any]:
        def _execute(mem_view):
            prompt = (
                f"You are the Planner agent.\n"
                f"User Objective: {state['user_query']}\n"
                f"{mem_view.formatted_context}\n"
                f"Break down the task, identify constraints, and determine what facts must be retrieved."
            )
            plan_response = self.llm.generate(prompt)

            # Store plan requirements as context memory unit
            created = memory_orchestrator.write_agent_output(
                text=f"Task Breakdown Plan: Verify budget revisions and delivery milestones for {state['user_query'][:50]}.",
                author_agent="planner",
                source_type="agent_plan",
            )
            output_ids = [m.id for m in created]

            updates = {
                "current_agent": "planner",
                "routing_target": "retriever",
                "step_count": state.get("step_count", 0) + 1,
            }
            return updates, plan_response, output_ids

        return self._execute_with_telemetry(state, memory_orchestrator, trace_logger, _execute)
