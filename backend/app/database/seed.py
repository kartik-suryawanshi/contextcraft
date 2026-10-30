import time
import uuid
from sqlalchemy.orm import Session

from backend.app.database.models import ExecutionModel
from backend.app.database.repository import MemoryRepository, TraceRepository, ExecutionRepository
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger
from backend.app.graph.workflow import build_contextcraft_graph
from backend.app.providers.llm import MockLLMProvider


def seed_demo_data_if_empty(db: Session) -> None:
    """
    Automatically seeds initial multi-agent workflow executions and structured memories
    if the database is newly initialized or running in an ephemeral cloud environment.
    """
    exec_repo = ExecutionRepository(db)
    if exec_repo.count() > 0:
        return

    mem_repo = MemoryRepository(db)
    trace_repo = TraceRepository(db)
    orchestrator = ContextCraftOrchestrator(mem_repo, trace_repo)
    logger = TraceLogger(trace_repo)
    llm = MockLLMProvider()
    graph = build_contextcraft_graph(orchestrator, logger, llm)

    sample_queries = [
        (
            "Prepare an analysis of Project Orion. Its original budget was ₹10 lakh, "
            "the deadline was December 2026, and the project budget was later revised to ₹12 lakh. "
            "Explain the current project status using the available information."
        ),
        (
            "Review Project Orion milestone delivery risks and timeline constraints for December 2026."
        ),
    ]

    for query in sample_queries:
        exec_id = f"exec-{uuid.uuid4().hex[:10]}"
        exec_repo.create(ExecutionModel(
            id=exec_id,
            user_query=query,
            status="running",
        ))

        state = {
            "user_query": query,
            "task_id": f"task-{uuid.uuid4().hex[:8]}",
            "execution_id": exec_id,
            "current_agent": "supervisor",
            "execution_status": "running",
            "routing_target": "supervisor",
            "iteration_count": 0,
            "max_iterations": 2,
            "step_count": 0,
            "final_answer": None,
            "error_status": None,
        }

        start_time = time.time()
        try:
            final_state = graph.invoke(state)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            traces = trace_repo.get_by_execution(exec_id)
            total_tokens = sum(t.estimated_token_count for t in traces)

            exec_repo.update_status(
                execution_id=exec_id,
                status=final_state.get("execution_status", "completed"),
                final_answer=final_state.get("final_answer"),
                duration_ms=duration_ms,
                total_tokens=total_tokens,
                iteration_count=final_state.get("iteration_count", 0),
            )
        except Exception as e:
            exec_repo.update_status(execution_id=exec_id, status="failed", error_status=str(e))
