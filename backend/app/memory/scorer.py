from typing import Dict, Any, List
from datetime import datetime, timezone
from dataclasses import dataclass
from backend.app.database.models import MemoryUnitModel
from backend.app.providers.retrieval import BaseRetrievalProvider, LexicalRetrievalProvider
from backend.app.core.config import settings


@dataclass
class ScoredCandidate:
    memory_unit: MemoryUnitModel
    relevance_score: float
    recency_score: float
    importance_score: float
    role_need_score: float
    total_score: float
    token_count: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.memory_unit.id,
            "fact_text": self.memory_unit.fact_text,
            "topic": self.memory_unit.topic,
            "value": self.memory_unit.value,
            "unit": self.memory_unit.unit,
            "status": self.memory_unit.status,
            "token_count": self.token_count,
            "relevance_score": round(self.relevance_score, 3),
            "recency_score": round(self.recency_score, 3),
            "importance_score": round(self.importance_score, 3),
            "role_need_score": round(self.role_need_score, 3),
            "total_score": round(self.total_score, 3),
        }


class MemoryScorer:
    """Evaluates and ranks memory units using role-specific weighted multi-factor scoring."""

    def __init__(self, retrieval_provider: Optional[BaseRetrievalProvider] = None):
        self.retrieval = retrieval_provider or LexicalRetrievalProvider()

    def _calculate_recency(self, memory: MemoryUnitModel) -> float:
        """Calculates normalized recency score between 0.1 and 1.0 based on created_at or version."""
        if not memory.created_at:
            return 0.5

        # Check version indicators
        ver = (memory.version_date or "").lower()
        if "revision" in ver or "v2" in ver or "updated" in ver:
            return 1.0
        if "baseline" in ver or "v1" in ver or "original" in ver:
            return 0.6

        # Time-based decay (within 1 hour = 0.9, within 1 day = 0.8, etc.)
        now = datetime.now(timezone.utc)
        created = memory.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        diff_hours = (now - created).total_seconds() / 3600.0
        return max(0.2, min(1.0, 1.0 - (diff_hours / 24.0) * 0.5))

    def _calculate_role_need(self, memory: MemoryUnitModel, role: str) -> float:
        """Calculates role alignment score based on memory unit characteristics and role needs."""
        role_lower = role.lower()
        topic_lower = memory.topic.lower()
        fact_lower = memory.fact_text.lower()
        has_value = bool(memory.value)

        if role_lower == "supervisor":
            # Prefers high-level summaries and task context
            if "status" in topic_lower or "context" in topic_lower or "summary" in fact_lower:
                return 0.95
            if not has_value:
                return 0.8
            return 0.5  # Raw individual numbers are less needed by supervisor

        elif role_lower == "planner":
            # Prefers requirements, timeline, milestones, constraints
            if "timeline" in topic_lower or "deadline" in fact_lower or "constraint" in fact_lower:
                return 0.95
            if "plan" in topic_lower or "requirement" in fact_lower:
                return 0.90
            return 0.65

        elif role_lower == "retriever":
            # Prefers missing facts, original queries, knowledge gap hints
            if "gap" in fact_lower or "missing" in fact_lower or "query" in topic_lower:
                return 0.95
            return 0.60

        elif role_lower == "executor":
            # Strongly prefers confirmed active facts with quantitative values and units
            if has_value and memory.status == "current":
                return 1.0
            if "budget" in topic_lower or "cost" in topic_lower or "timeline" in topic_lower:
                return 0.90
            return 0.70

        elif role_lower == "critic":
            # Prefers verified figures, citations, draft claims, baseline comparisons
            if has_value or "budget" in topic_lower or "timeline" in topic_lower:
                return 0.95
            if memory.source_document:
                return 0.90
            return 0.70

        return 0.5

    def score_candidates(
        self,
        memories: List[MemoryUnitModel],
        role: str,
        task_query: str,
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> List[ScoredCandidate]:
        scored_list: List[ScoredCandidate] = []
        role_key = role.lower()
        weights = custom_weights or settings.ROLE_WEIGHTS.get(
            role_key,
            {"relevance": 0.35, "recency": 0.20, "importance": 0.25, "role_need": 0.20},
        )

        w_rel = weights.get("relevance", 0.35)
        w_rec = weights.get("recency", 0.20)
        w_imp = weights.get("importance", 0.25)
        w_role = weights.get("role_need", 0.20)

        for mem in memories:
            rel = self.retrieval.calculate_relevance(task_query, mem.fact_text, mem.topic)
            rec = self._calculate_recency(mem)
            imp = mem.importance
            role_need = self._calculate_role_need(mem, role_key)

            total = (w_rel * rel) + (w_rec * rec) + (w_imp * imp) + (w_role * role_need)
            token_count = mem.token_count if (mem.token_count is not None and mem.token_count > 0) else max(10, len(mem.fact_text.split()) * 2)

            scored_list.append(
                ScoredCandidate(
                    memory_unit=mem,
                    relevance_score=rel,
                    recency_score=rec,
                    importance_score=imp,
                    role_need_score=role_need,
                    total_score=total,
                    token_count=token_count,
                )
            )

        # Sort descending by total score
        scored_list.sort(key=lambda x: x.total_score, reverse=True)
        return scored_list
