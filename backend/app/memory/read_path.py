from typing import List, Dict, Any, Optional
from backend.app.database.repository import MemoryRepository
from backend.app.memory.scorer import MemoryScorer, ScoredCandidate
from backend.app.memory.budget_assembler import TokenBudgetAssembler, AssembledMemoryView
from backend.app.core.config import settings


class MemoryReadPipeline:
    """Encapsulates the Read Path: candidate retrieval, role scoring, ranking, deduplication, and budget assembly."""

    def __init__(
        self,
        repository: MemoryRepository,
        scorer: Optional[MemoryScorer] = None,
        budget_assembler: Optional[TokenBudgetAssembler] = None,
    ):
        self.repository = repository
        self.scorer = scorer or MemoryScorer()
        self.budget_assembler = budget_assembler or TokenBudgetAssembler()

    def get_role_memory_view(
        self,
        role: str,
        task_query: str,
        token_budget: Optional[int] = None,
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> AssembledMemoryView:
        role_key = role.lower()
        budget = token_budget or settings.ROLE_TOKEN_BUDGETS.get(role_key, 250)

        # 1. Retrieve active (current) memory units
        active_memories = self.repository.get_active(limit=100)

        # 2. Evaluate candidates using role scoring
        ranked_candidates = self.scorer.score_candidates(
            memories=active_memories,
            role=role_key,
            task_query=task_query,
            custom_weights=custom_weights,
        )

        # 3. Assemble memory view with budget and near-duplicate filtering
        memory_view = self.budget_assembler.assemble(
            ranked_candidates=ranked_candidates,
            role=role_key,
            token_budget=budget,
        )

        return memory_view
