from typing import List, Dict, Any, Optional
import uuid
import json
from backend.app.database.models import MemoryUnitModel, MemoryViewLogModel
from backend.app.database.repository import MemoryRepository, TraceRepository
from backend.app.memory.write_path import MemoryWritePipeline
from backend.app.memory.read_path import MemoryReadPipeline
from backend.app.memory.budget_assembler import AssembledMemoryView


class ContextCraftOrchestrator:
    """Unified ContextCraft memory orchestrator service managing both write and read pipelines."""

    def __init__(
        self,
        memory_repo: MemoryRepository,
        trace_repo: Optional[TraceRepository] = None,
        write_pipeline: Optional[MemoryWritePipeline] = None,
        read_pipeline: Optional[MemoryReadPipeline] = None,
    ):
        self.memory_repo = memory_repo
        self.trace_repo = trace_repo
        self.write_pipeline = write_pipeline or MemoryWritePipeline(repository=memory_repo)
        self.read_pipeline = read_pipeline or MemoryReadPipeline(repository=memory_repo)

    def write_agent_output(
        self,
        text: str,
        author_agent: str,
        source_type: str = "agent_inference",
        source_document: Optional[str] = None,
        source_page: Optional[int] = None,
    ) -> List[MemoryUnitModel]:
        """Ingests raw text, extracts facts, resolves conflicts, and persists memory units."""
        return self.write_pipeline.process_and_store(
            text=text,
            author_agent=author_agent,
            source_type=source_type,
            source_document=source_document,
            source_page=source_page,
        )

    def get_memory_view_for_agent(
        self,
        agent_role: str,
        task_query: str,
        execution_id: Optional[str] = None,
        token_budget: Optional[int] = None,
    ) -> AssembledMemoryView:
        """Retrieves and packages role-specific, conflict-free, token-bounded memory view."""
        view = self.read_pipeline.get_role_memory_view(
            role=agent_role,
            task_query=task_query,
            token_budget=token_budget,
        )

        # Log memory view inspection data for observability
        if self.trace_repo and execution_id:
            selected_data = [
                {
                    "id": c.memory_unit.id,
                    "fact_text": c.memory_unit.fact_text,
                    "topic": c.memory_unit.topic,
                    "value": c.memory_unit.value,
                    "relevance_score": round(c.relevance_score, 3),
                    "recency_score": round(c.recency_score, 3),
                    "importance_score": round(c.importance_score, 3),
                    "role_need_score": round(c.role_need_score, 3),
                    "total_score": round(c.total_score, 3),
                    "token_count": c.token_count,
                }
                for c in view.selected_candidates
            ]
            excluded_data = [
                {
                    "id": e.id,
                    "fact_text": e.fact_text,
                    "topic": e.topic,
                    "reason": e.reason,
                    "total_score": round(e.total_score, 3),
                    "token_count": e.token_count,
                }
                for e in view.excluded_units
            ]

            log_entry = MemoryViewLogModel(
                id=f"view-{uuid.uuid4().hex[:10]}",
                execution_id=execution_id,
                agent_name=agent_role,
                token_budget=view.token_budget,
                tokens_consumed=view.tokens_consumed,
                selected_units_json=json.dumps(selected_data),
                excluded_units_json=json.dumps(excluded_data),
            )
            self.trace_repo.create_memory_view_log(log_entry)

        return view
