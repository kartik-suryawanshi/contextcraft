import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.connection import Base
from backend.app.database.repository import MemoryRepository, TraceRepository, ExecutionRepository
from backend.app.database.models import ExecutionModel
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger
from backend.app.graph.workflow import build_contextcraft_graph
from backend.app.providers.llm import MockLLMProvider


@pytest.fixture
def workflow_setup():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    mem_repo = MemoryRepository(db)
    trace_repo = TraceRepository(db)
    exec_repo = ExecutionRepository(db)
    orchestrator = ContextCraftOrchestrator(mem_repo, trace_repo)
    logger = TraceLogger(trace_repo)
    llm = MockLLMProvider()

    graph = build_contextcraft_graph(orchestrator, logger, llm)
    yield db, mem_repo, trace_repo, exec_repo, graph

    db.close()


def test_full_project_orion_workflow_execution(workflow_setup):
    db, mem_repo, trace_repo, exec_repo, graph = workflow_setup

    query = (
        "Prepare an analysis of Project Orion. Its original budget was ₹10 lakh, "
        "the deadline was December 2026, and the project budget was later revised to ₹12 lakh. "
        "Explain the current project status using the available information."
    )
    execution_id = "exec-test-orion"
    exec_repo.create(ExecutionModel(id=execution_id, user_query=query, status="running"))

    state = {
        "user_query": query,
        "task_id": "task-test",
        "execution_id": execution_id,
        "current_agent": "supervisor",
        "execution_status": "running",
        "routing_target": "supervisor",
        "iteration_count": 0,
        "max_iterations": 2,
        "step_count": 0,
        "final_answer": None,
        "error_status": None,
    }

    final_state = graph.invoke(state)

    # Verify workflow concluded cleanly
    assert final_state["execution_status"] == "completed"
    assert final_state["current_agent"] == "critic"
    assert final_state["final_answer"] is not None

    # Verify traces were captured for all 5 agents
    traces = trace_repo.get_traces_for_execution(execution_id)
    agents_executed = [t.agent_name for t in traces]
    assert "supervisor" in agents_executed
    assert "planner" in agents_executed
    assert "retriever" in agents_executed
    assert "executor" in agents_executed
    assert "critic" in agents_executed

    # Verify memory units and conflict handling
    all_memories = mem_repo.get_all()
    assert len(all_memories) >= 3

    # Check that older budget (10L) is superseded
    orig_budget = next((m for m in all_memories if m.value == "10"), None)
    assert orig_budget is not None
    assert orig_budget.status == "superseded"
    assert orig_budget.superseded_by is not None

    # Check that revised budget (12L) is current
    revised_budget = next((m for m in all_memories if m.value == "12"), None)
    assert revised_budget is not None
    assert revised_budget.status == "current"

    # Check deadline memory
    deadline_mem = next((m for m in all_memories if "December 2026" in str(m.value)), None)
    assert deadline_mem is not None
    assert deadline_mem.status == "current"

    # Check that conflict audit event was recorded
    audits = mem_repo.get_conflict_audits()
    assert len(audits) >= 1
    assert audits[0].resolution_type == "superseded"
