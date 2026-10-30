from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from backend.app.memory.scorer import ScoredCandidate
from backend.app.database.models import MemoryUnitModel


@dataclass
class ExcludedMemory:
    id: str
    fact_text: str
    topic: str
    total_score: float
    token_count: int
    reason: str  # "budget_exceeded" | "duplicate"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "fact_text": self.fact_text,
            "topic": self.topic,
            "total_score": round(self.total_score, 3),
            "token_count": self.token_count,
            "reason": self.reason,
        }


@dataclass
class AssembledMemoryView:
    role: str
    token_budget: int
    tokens_consumed: int
    selected_candidates: List[ScoredCandidate]
    excluded_units: List[ExcludedMemory]
    formatted_context: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "token_budget": self.token_budget,
            "tokens_consumed": self.tokens_consumed,
            "selected_units": [c.to_dict() for c in self.selected_candidates],
            "excluded_units": [e.to_dict() for e in self.excluded_units],
            "formatted_context": self.formatted_context,
        }


class TokenBudgetAssembler:
    """Assembles role-specific memory views by greedy selection within strict token limits and deduplication."""

    def assemble(
        self,
        ranked_candidates: List[ScoredCandidate],
        role: str,
        token_budget: int,
    ) -> AssembledMemoryView:
        selected: List[ScoredCandidate] = []
        excluded: List[ExcludedMemory] = []
        current_tokens = 0
        seen_topic_values = set()

        for candidate in ranked_candidates:
            mem = candidate.memory_unit
            # Near-duplicate check: same topic and same value
            topic_val_key = f"{mem.topic.lower()}::{str(mem.value).lower() if mem.value else mem.fact_text.lower()[:30]}"
            if topic_val_key in seen_topic_values:
                excluded.append(
                    ExcludedMemory(
                        id=mem.id,
                        fact_text=mem.fact_text,
                        topic=mem.topic,
                        total_score=candidate.total_score,
                        token_count=candidate.token_count,
                        reason="duplicate",
                    )
                )
                continue

            # Check if fits within token budget
            if current_tokens + candidate.token_count <= token_budget:
                selected.append(candidate)
                current_tokens += candidate.token_count
                seen_topic_values.add(topic_val_key)
            else:
                excluded.append(
                    ExcludedMemory(
                        id=mem.id,
                        fact_text=mem.fact_text,
                        topic=mem.topic,
                        total_score=candidate.total_score,
                        token_count=candidate.token_count,
                        reason="budget_exceeded",
                    )
                )

        # Format context payload for agent consumption
        context_lines = [f"=== CONTEXTCRAFT MEMORY VIEW FOR {role.upper()} ==="]
        if not selected:
            context_lines.append("No active memory units currently matched.")
        else:
            for idx, item in enumerate(selected, 1):
                mem = item.memory_unit
                val_str = f" [Value: {mem.value} {mem.unit or ''}]" if mem.value else ""
                ver_str = f" [Version: {mem.version_date}]" if mem.version_date else ""
                src_str = f" (Source: {mem.source_type})" if mem.source_type else ""
                context_lines.append(
                    f"{idx}. [{mem.topic}] {mem.fact_text}{val_str}{ver_str}{src_str}"
                )
        context_lines.append("==================================================")
        formatted_context = "\n".join(context_lines)

        return AssembledMemoryView(
            role=role,
            token_budget=token_budget,
            tokens_consumed=current_tokens,
            selected_candidates=selected,
            excluded_units=excluded,
            formatted_context=formatted_context,
        )
