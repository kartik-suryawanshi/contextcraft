from typing import Literal
from backend.app.graph.state import GraphState


def route_from_critic(state: GraphState) -> Literal["planner", "end"]:
    """Conditional edge from Critic: routes to revision loop or concludes execution."""
    if state.get("routing_target") == "planner" and state.get("iteration_count", 0) <= state.get("max_iterations", 2):
        return "planner"
    return "end"
