from typing import Optional
from langgraph.graph import StateGraph, START, END
from backend.app.graph.state import GraphState
from backend.app.graph.routing import route_from_critic
from backend.app.agents.supervisor import SupervisorAgent
from backend.app.agents.planner import PlannerAgent
from backend.app.agents.retriever import RetrieverAgent
from backend.app.agents.executor import ExecutorAgent
from backend.app.agents.critic import CriticAgent
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger
from backend.app.providers.llm import BaseLLMProvider


def build_contextcraft_graph(
    memory_orchestrator: ContextCraftOrchestrator,
    trace_logger: Optional[TraceLogger] = None,
    llm_provider: Optional[BaseLLMProvider] = None,
):
    """Builds and compiles the 5-agent LangGraph workflow integrated with ContextCraft Memory Orchestrator."""
    supervisor = SupervisorAgent(llm_provider=llm_provider)
    planner = PlannerAgent(llm_provider=llm_provider)
    retriever = RetrieverAgent(llm_provider=llm_provider)
    executor = ExecutorAgent(llm_provider=llm_provider)
    critic = CriticAgent(llm_provider=llm_provider)

    builder = StateGraph(GraphState)

    # Node wrappers
    def supervisor_node(state: GraphState) -> GraphState:
        updates = supervisor.run_step(state, memory_orchestrator, trace_logger)
        return {**state, **updates}

    def planner_node(state: GraphState) -> GraphState:
        updates = planner.run_step(state, memory_orchestrator, trace_logger)
        return {**state, **updates}

    def retriever_node(state: GraphState) -> GraphState:
        updates = retriever.run_step(state, memory_orchestrator, trace_logger)
        return {**state, **updates}

    def executor_node(state: GraphState) -> GraphState:
        updates = executor.run_step(state, memory_orchestrator, trace_logger)
        return {**state, **updates}

    def critic_node(state: GraphState) -> GraphState:
        updates = critic.run_step(state, memory_orchestrator, trace_logger)
        return {**state, **updates}

    # Register nodes
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("planner", planner_node)
    builder.add_node("retriever", retriever_node)
    builder.add_node("executor", executor_node)
    builder.add_node("critic", critic_node)

    # Define graph edges
    builder.add_edge(START, "supervisor")
    builder.add_edge("supervisor", "planner")
    builder.add_edge("planner", "retriever")
    builder.add_edge("retriever", "executor")
    builder.add_edge("executor", "critic")

    # Conditional revision edge from critic
    builder.add_conditional_edges(
        "critic",
        route_from_critic,
        {
            "planner": "planner",
            "end": END,
        },
    )

    return builder.compile()
