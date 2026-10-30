from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.repository import MemoryRepository
from backend.app.api.schemas.memory import (
    MemoryUnitResponse,
    MemoryListResponse,
    ConflictAuditResponse,
)

router = APIRouter(prefix="/memories", tags=["Memories"])


@router.get("", response_model=MemoryListResponse)
def list_memories(
    status: Optional[str] = Query(None, description="Filter by status: current, superseded, conflicting"),
    topic: Optional[str] = Query(None, description="Filter by topic keyword"),
    author: Optional[str] = Query(None, description="Filter by author agent"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    mem_repo = MemoryRepository(db)
    items = mem_repo.get_all(status=status, topic=topic, author=author, limit=limit, offset=offset)
    total = mem_repo.count(status=status, topic=topic)
    return {
        "total": total,
        "items": [m.to_dict() for m in items],
    }


@router.get("/audits/conflicts", response_model=List[ConflictAuditResponse])
def get_conflict_audits(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    mem_repo = MemoryRepository(db)
    audits = mem_repo.get_conflict_audits(limit=limit)
    return [a.to_dict() for a in audits]


@router.get("/{memory_id}", response_model=MemoryUnitResponse)
def get_memory(memory_id: str, db: Session = Depends(get_db)):
    mem_repo = MemoryRepository(db)
    mem = mem_repo.get_by_id(memory_id)
    if not mem:
        raise HTTPException(status_code=404, detail="Memory unit not found")
    return mem.to_dict()
