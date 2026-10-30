import pytest
from backend.app.memory.scorer import MemoryScorer
from backend.app.database.models import MemoryUnitModel


def test_memory_scorer_role_preferences():
    scorer = MemoryScorer()

    fact_quantitative = MemoryUnitModel(
        id="mem-quant",
        topic="Project Orion Budget",
        value="12",
        unit="lakh INR",
        fact_text="Project Orion budget is 12 lakh INR",
        status="current",
        author_agent="user_input",
        importance=0.9,
    )

    fact_summary = MemoryUnitModel(
        id="mem-sum",
        topic="Project Orion Status Summary",
        value=None,
        fact_text="Project Orion overall status summary and governance overview",
        status="current",
        author_agent="supervisor",
        importance=0.7,
    )

    # For Executor, quantitative confirmed fact should score higher than general summary
    executor_scores = scorer.score_candidates(
        memories=[fact_summary, fact_quantitative],
        role="executor",
        task_query="What is the current budget?",
    )
    assert executor_scores[0].memory_unit.id == "mem-quant"

    # For Supervisor, high-level summary should receive strong role need weighting
    supervisor_scores = scorer.score_candidates(
        memories=[fact_quantitative, fact_summary],
        role="supervisor",
        task_query="Provide high level project overview and status",
    )
    sum_score = next(s for s in supervisor_scores if s.memory_unit.id == "mem-sum")
    assert sum_score.role_need_score >= 0.8
