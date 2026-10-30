from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent
from backend.app.graph.state import GraphState
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger


class SupervisorAgent(BaseAgent):
    """Supervisor / Router Agent: Evaluates user query and coordinates workflow routing."""

    def __init__(self, llm_provider=None):
        super().__init__(role_name="supervisor", llm_provider=llm_provider)

    def run_step(
        self,
        state: GraphState,
        memory_orchestrator: ContextCraftOrchestrator,
        trace_logger: Optional[TraceLogger] = None,
    ) -> Dict[str, Any]:
        def _execute(mem_view):
            output_ids = []
            # On first step, ingest the user query into ContextCraft Write Pipeline
            if state.get("step_count", 0) == 0:
                created_memories = memory_orchestrator.write_agent_output(
                    text=state["user_query"],
                    author_agent="user_input",
                    source_type="user_query",
                )
                output_ids = [m.id for m in created_memories]

            prompt = (
                f"You are the Supervisor and Router agent.\n"
                f"User Objective: {state['user_query']}\n"
                f"{mem_view.formatted_context}\n"
                f"Determine the immediate next action and routing target."
            )
            response = self.llm.generate(prompt)

            updates = {
                "current_agent": "supervisor",
                "routing_target": "planner",
                "step_count": state.get("step_count", 0) + 1,
                "execution_status": "running",
            }
            return updates, response, output_ids

        return self._execute_with_telemetry(state, memory_orchestrator, trace_logger, _execute)
