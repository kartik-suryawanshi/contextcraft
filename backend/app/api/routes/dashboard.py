from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.repository import ExecutionRepository, MemoryRepository, TraceRepository
from backend.app.core.config import settings
from backend.app.api.schemas.dashboard import DashboardMetricsResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/metrics", response_model=DashboardMetricsResponse)
def get_dashboard_metrics(db: Session = Depends(get_db)):
    exec_repo = ExecutionRepository(db)
    mem_repo = MemoryRepository(db)
    trace_repo = TraceRepository(db)

    total_execs = exec_repo.count()
    successful_execs = exec_repo.count_by_status("completed")
    failed_execs = exec_repo.count_by_status("failed")

    total_memories = mem_repo.count()
    current_memories = mem_repo.count(status="current")
    superseded_memories = mem_repo.count(status="superseded")
    conflicting_memories = mem_repo.count(status="conflicting")

    avg_duration = exec_repo.get_avg_duration_ms()
    total_tokens = exec_repo.get_total_tokens()
    agent_distribution = trace_repo.get_agent_execution_counts()

    return {
        "total_executions": total_execs,
        "successful_executions": successful_execs,
        "failed_executions": failed_execs,
        "total_memory_units": total_memories,
        "current_memory_units": current_memories,
        "superseded_memory_units": superseded_memories,
        "conflicting_memory_units": conflicting_memories,
        "average_duration_ms": avg_duration,
        "total_estimated_tokens": total_tokens,
        "agent_distribution": agent_distribution,
        "mock_mode": settings.MOCK_MODE,
    }
