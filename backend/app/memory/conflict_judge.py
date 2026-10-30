from abc import ABC, abstractmethod
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from backend.app.database.models import MemoryUnitModel


@dataclass
class ConflictDecision:
    has_conflict: bool
    is_superseding: bool
    winning_fact: Optional[Any]  # ExtractedFact or MemoryUnitModel
    superseded_memory_id: Optional[str]
    conflicting_memory_id: Optional[str]
    resolution_type: str  # "none", "superseded", "conflicting", "agreed"
    explanation: str


class ConflictJudge(ABC):
    @abstractmethod
    def evaluate(
        self,
        new_fact_topic: str,
        new_fact_value: Optional[str],
        new_fact_version: Optional[str],
        new_fact_confidence: float,
        existing_memories: List[MemoryUnitModel],
    ) -> List[ConflictDecision]:
        """Evaluates whether the candidate fact conflicts with or supersedes any existing memory."""
        pass


class DeterministicConflictJudge(ConflictJudge):
    """Deterministic conflict judge using topic semantics, temporal versions, and confidence thresholds."""

    def evaluate(
        self,
        new_fact_topic: str,
        new_fact_value: Optional[str],
        new_fact_version: Optional[str],
        new_fact_confidence: float,
        existing_memories: List[MemoryUnitModel],
    ) -> List[ConflictDecision]:
        decisions: List[ConflictDecision] = []

        for existing in existing_memories:
            # Check topic match (case-insensitive normalized)
            if existing.topic.strip().lower() != new_fact_topic.strip().lower():
                continue

            # If both have quantitative/discrete values
            if existing.value and new_fact_value:
                existing_val = existing.value.strip().lower()
                new_val = new_fact_value.strip().lower()

                if existing_val == new_val:
                    # Values agree: reinforce confidence, no conflict
                    decisions.append(
                        ConflictDecision(
                            has_conflict=False,
                            is_superseding=False,
                            winning_fact=None,
                            superseded_memory_id=None,
                            conflicting_memory_id=None,
                            resolution_type="agreed",
                            explanation=f"Values agree for topic '{new_fact_topic}' ({new_val}).",
                        )
                    )
                else:
                    # Contradicting values on the same topic!
                    # Check for explicit revision indicators in version_date or text
                    new_ver_str = (new_fact_version or "").lower()
                    existing_ver_str = (existing.version_date or "").lower()

                    is_new_revision = any(
                        keyword in new_ver_str
                        for keyword in ["revision", "amendment", "v2", "updated", "later"]
                    )
                    is_existing_baseline = any(
                        keyword in existing_ver_str
                        for keyword in ["baseline", "original", "initial", "v1"]
                    )

                    # If new fact is an explicit revision or has higher confidence/later version
                    if is_new_revision or (is_existing_baseline and new_fact_confidence >= existing.confidence):
                        decisions.append(
                            ConflictDecision(
                                has_conflict=True,
                                is_superseding=True,
                                winning_fact=None,
                                superseded_memory_id=existing.id,
                                conflicting_memory_id=None,
                                resolution_type="superseded",
                                explanation=(
                                    f"Contradiction detected for '{new_fact_topic}'. "
                                    f"Newer revision ({new_val}) supersedes older baseline ({existing_val}) "
                                    f"based on revision provenance and confidence ({new_fact_confidence:.2f} >= {existing.confidence:.2f})."
                                ),
                            )
                        )
                    else:
                        # Unresolved contradiction
                        decisions.append(
                            ConflictDecision(
                                has_conflict=True,
                                is_superseding=False,
                                winning_fact=None,
                                superseded_memory_id=None,
                                conflicting_memory_id=existing.id,
                                resolution_type="conflicting",
                                explanation=(
                                    f"Contradiction between values '{new_val}' and '{existing_val}' "
                                    f"for topic '{new_fact_topic}' lacks definitive version precedence. Flagged as conflicting."
                                ),
                            )
                        )

        return decisions
