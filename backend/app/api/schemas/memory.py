from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class MemoryUnitResponse(BaseModel):
    id: str
    fact_text: str
    topic: str
    value: Optional[str] = None
    unit: Optional[str] = None
    source_document: Optional[str] = None
    source_page: Optional[int] = None
    version_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    author_agent: str
    source_type: str
    confidence: float
    importance: float
    status: str
    token_count: int
    embedding: Optional[List[float]] = None
    superseded_by: Optional[str] = None
    conflict_reason: Optional[str] = None


class MemoryListResponse(BaseModel):
    total: int
    items: List[MemoryUnitResponse]


class ConflictAuditResponse(BaseModel):
    id: str
    topic: str
    winning_memory_id: str
    superseded_memory_id: Optional[str] = None
    conflicting_memory_id: Optional[str] = None
    resolution_type: str
    explanation: str
    created_at: Optional[str] = None
