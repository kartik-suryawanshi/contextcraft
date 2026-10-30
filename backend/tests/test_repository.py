import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.database.connection import Base
from backend.app.database.models import MemoryUnitModel, ExecutionModel
from backend.app.database.repository import MemoryRepository, ExecutionRepository


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()


def test_memory_repository_crud(in_memory_db):
    repo = MemoryRepository(in_memory_db)

    mem = MemoryUnitModel(
        id="mem-test-1",
        fact_text="Test fact text",
        topic="Testing Topic",
        value="100",
        unit="units",
        status="current",
        author_agent="tester",
        confidence=0.9,
        importance=0.8,
        token_count=15,
    )
    saved = repo.create(mem)
    assert saved.id == "mem-test-1"

    fetched = repo.get_by_id("mem-test-1")
    assert fetched is not None
    assert fetched.topic == "Testing Topic"

    # Status update to superseded
    repo.update_status("mem-test-1", "superseded", superseded_by="mem-test-2")
    updated = repo.get_by_id("mem-test-1")
    assert updated.status == "superseded"
    assert updated.superseded_by == "mem-test-2"

    # Verify superseded is not in active
    active = repo.get_active()
    assert len(active) == 0


def test_execution_repository_crud(in_memory_db):
    repo = ExecutionRepository(in_memory_db)

    exec_record = ExecutionModel(
        id="exec-test-1",
        user_query="Run test task",
        status="running",
    )
    repo.create(exec_record)

    fetched = repo.get_by_id("exec-test-1")
    assert fetched is not None
    assert fetched.status == "running"

    repo.update(
        "exec-test-1",
        status="completed",
        final_answer="Test complete",
        total_duration_ms=120.5,
        total_tokens_estimated=350,
    )

    updated = repo.get_by_id("exec-test-1")
    assert updated.status == "completed"
    assert updated.final_answer == "Test complete"
    assert updated.total_tokens_estimated == 350
