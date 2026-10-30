from datetime import datetime, timezone
import json
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    Index,
)
from backend.app.database.connection import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MemoryUnitModel(Base):
    __tablename__ = "memory_units"

    id = Column(String(64), primary_key=True, index=True)
    fact_text = Column(Text, nullable=False)
    topic = Column(String(128), nullable=False, index=True)
    value = Column(String(128), nullable=True)
    unit = Column(String(64), nullable=True)
    source_document = Column(String(256), nullable=True)
    source_page = Column(Integer, nullable=True)
    version_date = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    author_agent = Column(String(64), nullable=False, index=True)
    source_type = Column(String(64), default="agent_inference", nullable=False)
    confidence = Column(Float, default=1.0, nullable=False)
    importance = Column(Float, default=0.5, nullable=False)
    status = Column(String(32), default="current", nullable=False, index=True)  # current, superseded, conflicting
    token_count = Column(Integer, default=0, nullable=False)
    embedding = Column(Text, nullable=True)  # JSON-encoded float array or null
    superseded_by = Column(String(64), nullable=True)
    conflict_reason = Column(Text, nullable=True)

    __table_args__ = (
        Index("idx_memory_topic_status", "topic", "status"),
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "fact_text": self.fact_text,
            "topic": self.topic,
            "value": self.value,
            "unit": self.unit,
            "source_document": self.source_document,
            "source_page": self.source_page,
            "version_date": self.version_date,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "author_agent": self.author_agent,
            "source_type": self.source_type,
            "confidence": self.confidence,
            "importance": self.importance,
            "status": self.status,
            "token_count": self.token_count,
            "embedding": json.loads(self.embedding) if self.embedding else None,
            "superseded_by": self.superseded_by,
            "conflict_reason": self.conflict_reason,
        }


class ExecutionModel(Base):
    __tablename__ = "executions"

    id = Column(String(64), primary_key=True, index=True)
    user_query = Column(Text, nullable=False)
    status = Column(String(32), default="running", nullable=False)  # running, completed, failed
    iteration_count = Column(Integer, default=0, nullable=False)
    final_answer = Column(Text, nullable=True)
    total_duration_ms = Column(Float, default=0.0, nullable=False)
    total_tokens_estimated = Column(Integer, default=0, nullable=False)
    error_status = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_query": self.user_query,
            "status": self.status,
            "iteration_count": self.iteration_count,
            "final_answer": self.final_answer,
            "total_duration_ms": self.total_duration_ms,
            "total_tokens_estimated": self.total_tokens_estimated,
            "error_status": self.error_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ExecutionTraceModel(Base):
    __tablename__ = "execution_traces"

    id = Column(String(64), primary_key=True, index=True)
    execution_id = Column(String(64), ForeignKey("executions.id"), nullable=False, index=True)
    agent_name = Column(String(64), nullable=False)
    execution_status = Column(String(32), default="completed", nullable=False)
    start_timestamp = Column(DateTime, default=utc_now, nullable=False)
    end_timestamp = Column(DateTime, default=utc_now, nullable=False)
    duration_ms = Column(Float, default=0.0, nullable=False)
    input_memory_ids = Column(Text, default="[]", nullable=False)  # JSON list
    output_memory_ids = Column(Text, default="[]", nullable=False)  # JSON list
    memory_view_size = Column(Integer, default=0, nullable=False)
    estimated_token_count = Column(Integer, default=0, nullable=False)
    agent_execution_result = Column(Text, nullable=True)
    error_info = Column(Text, nullable=True)
    step_order = Column(Integer, default=0, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "agent_name": self.agent_name,
            "execution_status": self.execution_status,
            "start_timestamp": self.start_timestamp.isoformat() if self.start_timestamp else None,
            "end_timestamp": self.end_timestamp.isoformat() if self.end_timestamp else None,
            "duration_ms": self.duration_ms,
            "input_memory_ids": json.loads(self.input_memory_ids) if self.input_memory_ids else [],
            "output_memory_ids": json.loads(self.output_memory_ids) if self.output_memory_ids else [],
            "memory_view_size": self.memory_view_size,
            "estimated_token_count": self.estimated_token_count,
            "agent_execution_result": self.agent_execution_result,
            "error_info": self.error_info,
            "step_order": self.step_order,
        }


class MemoryViewLogModel(Base):
    __tablename__ = "memory_view_logs"

    id = Column(String(64), primary_key=True, index=True)
    execution_id = Column(String(64), ForeignKey("executions.id"), nullable=False, index=True)
    agent_name = Column(String(64), nullable=False)
    token_budget = Column(Integer, default=300, nullable=False)
    tokens_consumed = Column(Integer, default=0, nullable=False)
    selected_units_json = Column(Text, default="[]", nullable=False)
    excluded_units_json = Column(Text, default="[]", nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "agent_name": self.agent_name,
            "token_budget": self.token_budget,
            "tokens_consumed": self.tokens_consumed,
            "selected_units": json.loads(self.selected_units_json) if self.selected_units_json else [],
            "excluded_units": json.loads(self.excluded_units_json) if self.excluded_units_json else [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ConflictAuditEventModel(Base):
    __tablename__ = "conflict_audit_events"

    id = Column(String(64), primary_key=True, index=True)
    topic = Column(String(128), nullable=False, index=True)
    winning_memory_id = Column(String(64), nullable=False)
    superseded_memory_id = Column(String(64), nullable=True)
    conflicting_memory_id = Column(String(64), nullable=True)
    resolution_type = Column(String(32), nullable=False)  # superseded, conflicting, agreed
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "winning_memory_id": self.winning_memory_id,
            "superseded_memory_id": self.superseded_memory_id,
            "conflicting_memory_id": self.conflicting_memory_id,
            "resolution_type": self.resolution_type,
            "explanation": self.explanation,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
