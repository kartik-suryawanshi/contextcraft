from typing import List, Optional
import uuid
import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import ExecutionModel
from backend.app.database.repository import ExecutionRepository, MemoryRepository, TraceRepository
from backend.app.memory.orchestrator import ContextCraftOrchestrator
from backend.app.observability.trace_logger import TraceLogger
from backend.app.graph.workflow import build_contextcraft_graph
from backend.app.providers.llm import MockLLMProvider, ConfigurableLLMProvider
from backend.app.api.schemas.execution import (
    ExecutionCreateRequest,
    ExecutionResponse,
    TraceResponse,
    MemoryViewLogResponse,
)

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.post("", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
def create_execution(request: ExecutionCreateRequest, db: Session = Depends(get_db)):
    exec_repo = ExecutionRepository(db)
    mem_repo = MemoryRepository(db)
    trace_repo = TraceRepository(db)

    execution_id = f"exec-{uuid.uuid4().hex[:10]}"
    task_id = f"task-{uuid.uuid4().hex[:8]}"

    # Persist initial record
    new_exec = ExecutionModel(
        id=execution_id,
        user_query=request.query,
        status="running",
        iteration_count=0,
        total_duration_ms=0.0,
        total_tokens_estimated=0,
    )
    exec_repo.create(new_exec)

    # Initialize ContextCraft Orchestrator & Tracing
    orchestrator = ContextCraftOrchestrator(memory_repo=mem_repo, trace_repo=trace_repo)
    trace_logger = TraceLogger(trace_repo=trace_repo)

    # Configure provider
    llm = MockLLMProvider() if request.mock_mode else ConfigurableLLMProvider()

    # Build LangGraph workflow
    graph = build_contextcraft_graph(
        memory_orchestrator=orchestrator,
        trace_logger=trace_logger,
        llm_provider=llm,
    )

    t0 = time.perf_counter()
    error_msg = None
    final_state = {}

    try:
        initial_state = {
            "user_query": request.query,
            "task_id": task_id,
            "execution_id": execution_id,
            "current_agent": "supervisor",
            "execution_status": "running",
            "routing_target": "supervisor",
            "iteration_count": 0,
            "max_iterations": request.max_iterations,
            "step_count": 0,
            "final_answer": None,
            "error_status": None,
        }
        final_state = graph.invoke(initial_state)
    except Exception as ex:
        error_msg = str(ex)

    t1 = time.perf_counter()
    wall_duration_ms = (t1 - t0) * 1000.0

    # Aggregate telemetry from persisted traces
    traces = trace_repo.get_traces_for_execution(execution_id)
    total_tokens = sum(t.estimated_token_count for t in traces)

    status_str = "failed" if error_msg else "completed"
    final_ans = final_state.get("final_answer")

    updated_exec = exec_repo.update(
        execution_id=execution_id,
        status=status_str,
        iteration_count=final_state.get("iteration_count", 0),
        final_answer=final_ans,
        total_duration_ms=round(wall_duration_ms, 2),
        total_tokens_estimated=total_tokens,
        error_status=error_msg,
    )

    if not updated_exec:
        raise HTTPException(status_code=500, detail="Failed to retrieve execution record")

    return updated_exec.to_dict()


@router.get("", response_model=List[ExecutionResponse])
def list_executions(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    exec_repo = ExecutionRepository(db)
    executions = exec_repo.get_all(limit=limit, offset=offset)
    return [e.to_dict() for e in executions]


@router.get("/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: str, db: Session = Depends(get_db)):
    exec_repo = ExecutionRepository(db)
    record = exec_repo.get_by_id(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution not found")
    return record.to_dict()


@router.get("/{execution_id}/traces", response_model=List[TraceResponse])
def get_execution_traces(execution_id: str, db: Session = Depends(get_db)):
    trace_repo = TraceRepository(db)
    traces = trace_repo.get_traces_for_execution(execution_id)
    return [t.to_dict() for t in traces]


@router.get("/{execution_id}/memory-views", response_model=List[MemoryViewLogResponse])
def get_execution_memory_views(execution_id: str, db: Session = Depends(get_db)):
    trace_repo = TraceRepository(db)
    views = trace_repo.get_memory_view_logs(execution_id)
    return [v.to_dict() for v in views]
