from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from backend.app.database.models import (
    MemoryUnitModel,
    ExecutionModel,
    ExecutionTraceModel,
    MemoryViewLogModel,
    ConflictAuditEventModel,
)


class MemoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, memory: MemoryUnitModel) -> MemoryUnitModel:
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def get_by_id(self, memory_id: str) -> Optional[MemoryUnitModel]:
        return self.db.query(MemoryUnitModel).filter(MemoryUnitModel.id == memory_id).first()

    def get_all(
        self,
        status: Optional[str] = None,
        topic: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[MemoryUnitModel]:
        query = self.db.query(MemoryUnitModel)
        if status:
            query = query.filter(MemoryUnitModel.status == status)
        if topic:
            query = query.filter(MemoryUnitModel.topic.ilike(f"%{topic}%"))
        if author:
            query = query.filter(MemoryUnitModel.author_agent == author)
        return query.order_by(desc(MemoryUnitModel.created_at)).offset(offset).limit(limit).all()

    def count(self, status: Optional[str] = None, topic: Optional[str] = None) -> int:
        query = self.db.query(func.count(MemoryUnitModel.id))
        if status:
            query = query.filter(MemoryUnitModel.status == status)
        if topic:
            query = query.filter(MemoryUnitModel.topic.ilike(f"%{topic}%"))
        return query.scalar() or 0

    def get_active(self, limit: int = 100) -> List[MemoryUnitModel]:
        return (
            self.db.query(MemoryUnitModel)
            .filter(MemoryUnitModel.status == "current")
            .order_by(desc(MemoryUnitModel.created_at))
            .limit(limit)
            .all()
        )

    def get_active_by_topic(self, topic: str) -> List[MemoryUnitModel]:
        return (
            self.db.query(MemoryUnitModel)
            .filter(MemoryUnitModel.status == "current", MemoryUnitModel.topic == topic)
            .all()
        )

    def update_status(
        self,
        memory_id: str,
        new_status: str,
        superseded_by: Optional[str] = None,
        conflict_reason: Optional[str] = None,
    ) -> Optional[MemoryUnitModel]:
        mem = self.get_by_id(memory_id)
        if mem:
            mem.status = new_status
            if superseded_by:
                mem.superseded_by = superseded_by
            if conflict_reason:
                mem.conflict_reason = conflict_reason
            self.db.commit()
            self.db.refresh(mem)
        return mem

    def record_conflict_audit(self, event: ConflictAuditEventModel) -> ConflictAuditEventModel:
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_conflict_audits(self, limit: int = 20) -> List[ConflictAuditEventModel]:
        return (
            self.db.query(ConflictAuditEventModel)
            .order_by(desc(ConflictAuditEventModel.created_at))
            .limit(limit)
            .all()
        )


class ExecutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, execution: ExecutionModel) -> ExecutionModel:
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution

    def get_by_id(self, execution_id: str) -> Optional[ExecutionModel]:
        return self.db.query(ExecutionModel).filter(ExecutionModel.id == execution_id).first()

    def get_all(self, limit: int = 20, offset: int = 0) -> List[ExecutionModel]:
        return (
            self.db.query(ExecutionModel)
            .order_by(desc(ExecutionModel.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count(self) -> int:
        return self.db.query(func.count(ExecutionModel.id)).scalar() or 0

    def count_by_status(self, status: str) -> int:
        return (
            self.db.query(func.count(ExecutionModel.id))
            .filter(ExecutionModel.status == status)
            .scalar()
            or 0
        )

    def update(
        self,
        execution_id: str,
        status: Optional[str] = None,
        iteration_count: Optional[int] = None,
        final_answer: Optional[str] = None,
        total_duration_ms: Optional[float] = None,
        total_tokens_estimated: Optional[int] = None,
        error_status: Optional[str] = None,
    ) -> Optional[ExecutionModel]:
        exec_record = self.get_by_id(execution_id)
        if exec_record:
            if status is not None:
                exec_record.status = status
            if iteration_count is not None:
                exec_record.iteration_count = iteration_count
            if final_answer is not None:
                exec_record.final_answer = final_answer
            if total_duration_ms is not None:
                exec_record.total_duration_ms = total_duration_ms
            if total_tokens_estimated is not None:
                exec_record.total_tokens_estimated = total_tokens_estimated
            if error_status is not None:
                exec_record.error_status = error_status
            self.db.commit()
            self.db.refresh(exec_record)
        return exec_record

    def get_total_tokens(self) -> int:
        total = self.db.query(func.sum(ExecutionModel.total_tokens_estimated)).scalar()
        return int(total) if total else 0

    def get_avg_duration_ms(self) -> float:
        avg = self.db.query(func.avg(ExecutionModel.total_duration_ms)).scalar()
        return round(float(avg), 2) if avg else 0.0


class TraceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_trace(self, trace: ExecutionTraceModel) -> ExecutionTraceModel:
        self.db.add(trace)
        self.db.commit()
        self.db.refresh(trace)
        return trace

    def get_traces_for_execution(self, execution_id: str) -> List[ExecutionTraceModel]:
        return (
            self.db.query(ExecutionTraceModel)
            .filter(ExecutionTraceModel.execution_id == execution_id)
            .order_by(ExecutionTraceModel.step_order.asc())
            .all()
        )

    def create_memory_view_log(self, log: MemoryViewLogModel) -> MemoryViewLogModel:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_memory_view_logs(self, execution_id: str) -> List[MemoryViewLogModel]:
        return (
            self.db.query(MemoryViewLogModel)
            .filter(MemoryViewLogModel.execution_id == execution_id)
            .order_by(MemoryViewLogModel.created_at.asc())
            .all()
        )

    def get_agent_execution_counts(self) -> Dict[str, int]:
        results = (
            self.db.query(ExecutionTraceModel.agent_name, func.count(ExecutionTraceModel.id))
            .group_by(ExecutionTraceModel.agent_name)
            .all()
        )
        return {agent: count for agent, count in results}
