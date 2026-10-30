import pytest
from backend.app.memory.budget_assembler import TokenBudgetAssembler
from backend.app.memory.scorer import ScoredCandidate
from backend.app.database.models import MemoryUnitModel


def test_budget_assembler_enforces_budget_limit():
    assembler = TokenBudgetAssembler()

    mem1 = MemoryUnitModel(id="m1", topic="Topic A", fact_text="Fact A1", value="1", status="current")
    mem2 = MemoryUnitModel(id="m2", topic="Topic B", fact_text="Fact B1", value="2", status="current")
    mem3 = MemoryUnitModel(id="m3", topic="Topic C", fact_text="Fact C1", value="3", status="current")

    candidates = [
        ScoredCandidate(mem1, relevance_score=0.9, recency_score=0.9, importance_score=0.9, role_need_score=0.9, total_score=0.9, token_count=50),
        ScoredCandidate(mem2, relevance_score=0.8, recency_score=0.8, importance_score=0.8, role_need_score=0.8, total_score=0.8, token_count=50),
        ScoredCandidate(mem3, relevance_score=0.7, recency_score=0.7, importance_score=0.7, role_need_score=0.7, total_score=0.7, token_count=50),
    ]

    # Budget of 110 tokens should allow m1 (50) and m2 (50) = 100 tokens, excluding m3
    view = assembler.assemble(candidates, role="executor", token_budget=110)

    assert len(view.selected_candidates) == 2
    assert view.tokens_consumed == 100
    assert len(view.excluded_units) == 1
    assert view.excluded_units[0].id == "m3"
    assert view.excluded_units[0].reason == "budget_exceeded"


def test_budget_assembler_skips_duplicates():
    assembler = TokenBudgetAssembler()

    mem1 = MemoryUnitModel(id="m1", topic="Budget", fact_text="Budget is 12L", value="12", status="current")
    mem2 = MemoryUnitModel(id="m2", topic="Budget", fact_text="Budget is 12L confirmed", value="12", status="current")

    candidates = [
        ScoredCandidate(mem1, relevance_score=0.9, recency_score=0.9, importance_score=0.9, role_need_score=0.9, total_score=0.9, token_count=20),
        ScoredCandidate(mem2, relevance_score=0.85, recency_score=0.85, importance_score=0.85, role_need_score=0.85, total_score=0.85, token_count=20),
    ]

    view = assembler.assemble(candidates, role="executor", token_budget=200)

    assert len(view.selected_candidates) == 1
    assert len(view.excluded_units) == 1
    assert view.excluded_units[0].reason == "duplicate"
