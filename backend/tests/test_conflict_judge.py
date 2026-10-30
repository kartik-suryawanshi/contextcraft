import pytest
from backend.app.memory.conflict_judge import DeterministicConflictJudge
from backend.app.database.models import MemoryUnitModel


def test_conflict_judge_superseding_revision():
    judge = DeterministicConflictJudge()

    # Existing baseline memory
    baseline = MemoryUnitModel(
        id="mem-orig",
        topic="Project Orion Budget",
        value="10",
        unit="lakh INR",
        fact_text="Project Orion original budget was ₹10 lakh",
        version_date="v1.0 (Original Baseline)",
        confidence=0.95,
        status="current",
        author_agent="user_input",
    )

    # New revised fact
    decisions = judge.evaluate(
        new_fact_topic="Project Orion Budget",
        new_fact_value="12",
        new_fact_version="v2.0 (Revision Amendment)",
        new_fact_confidence=0.98,
        existing_memories=[baseline],
    )

    assert len(decisions) == 1
    d = decisions[0]
    assert d.has_conflict is True
    assert d.is_superseding is True
    assert d.resolution_type == "superseded"
    assert d.superseded_memory_id == "mem-orig"


def test_conflict_judge_matching_agreement():
    judge = DeterministicConflictJudge()

    existing = MemoryUnitModel(
        id="mem-1",
        topic="Project Orion Budget",
        value="12",
        status="current",
        author_agent="executor",
        confidence=0.95,
    )

    decisions = judge.evaluate(
        new_fact_topic="Project Orion Budget",
        new_fact_value="12",
        new_fact_version="v2.1",
        new_fact_confidence=0.95,
        existing_memories=[existing],
    )

    assert len(decisions) == 1
    assert decisions[0].has_conflict is False
    assert decisions[0].resolution_type == "agreed"
