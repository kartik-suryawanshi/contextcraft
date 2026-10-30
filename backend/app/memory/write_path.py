from typing import List, Dict, Any, Optional
import uuid
from backend.app.database.models import MemoryUnitModel, ConflictAuditEventModel
from backend.app.database.repository import MemoryRepository
from backend.app.memory.fact_extractor import FactExtractor, ExtractedFact
from backend.app.memory.conflict_judge import ConflictJudge, DeterministicConflictJudge, ConflictDecision
from backend.app.providers.embeddings import BaseEmbeddingProvider, DeterministicEmbeddingProvider
import json


def estimate_tokens(text: str) -> int:
    """Estimates token count using standard word/character heuristics (approx 1.3 tokens per word, min 4)."""
    words = text.split()
    return max(4, int(len(words) * 1.35) + 2)


class MemoryWritePipeline:
    """Encapsulates the Write Path: fact extraction, atomic conversion, conflict checking, and persistence."""

    def __init__(
        self,
        repository: MemoryRepository,
        extractor: Optional[FactExtractor] = None,
        conflict_judge: Optional[ConflictJudge] = None,
        embedding_provider: Optional[BaseEmbeddingProvider] = None,
    ):
        self.repository = repository
        self.extractor = extractor or FactExtractor()
        self.conflict_judge = conflict_judge or DeterministicConflictJudge()
        self.embedding_provider = embedding_provider or DeterministicEmbeddingProvider()

    def process_and_store(
        self,
        text: str,
        author_agent: str = "system",
        source_type: str = "agent_inference",
        source_document: Optional[str] = None,
        source_page: Optional[int] = None,
    ) -> List[MemoryUnitModel]:
        # 1. Extract atomic facts
        extracted_facts = self.extractor.extract_facts(
            text=text,
            author_agent=author_agent,
            source_type=source_type,
            source_document=source_document,
        )

        persisted_units: List[MemoryUnitModel] = []

        # 2. Process each fact through conflict detection
        for fact in extracted_facts:
            new_id = f"mem-{uuid.uuid4().hex[:10]}"
            # Query existing active memories for same topic
            existing_active = self.repository.get_active_by_topic(fact.topic)

            # Evaluate with conflict judge
            conflict_decisions = self.conflict_judge.evaluate(
                new_fact_topic=fact.topic,
                new_fact_value=fact.value,
                new_fact_version=fact.version_date,
                new_fact_confidence=fact.confidence,
                existing_memories=existing_active,
            )

            status = "current"
            conflict_reason = None

            for decision in conflict_decisions:
                if decision.is_superseding and decision.superseded_memory_id:
                    # Mark existing record as superseded
                    self.repository.update_status(
                        memory_id=decision.superseded_memory_id,
                        new_status="superseded",
                        superseded_by=new_id,
                        conflict_reason=decision.explanation,
                    )
                    # Log conflict audit event
                    audit_event = ConflictAuditEventModel(
                        id=f"audit-{uuid.uuid4().hex[:10]}",
                        topic=fact.topic,
                        winning_memory_id=new_id,
                        superseded_memory_id=decision.superseded_memory_id,
                        conflicting_memory_id=None,
                        resolution_type="superseded",
                        explanation=decision.explanation,
                    )
                    self.repository.record_conflict_audit(audit_event)

                elif decision.resolution_type == "conflicting":
                    status = "conflicting"
                    conflict_reason = decision.explanation
                    # Flag existing as conflicting too
                    if decision.conflicting_memory_id:
                        self.repository.update_status(
                            memory_id=decision.conflicting_memory_id,
                            new_status="conflicting",
                            conflict_reason=decision.explanation,
                        )
                    # Record audit event
                    audit_event = ConflictAuditEventModel(
                        id=f"audit-{uuid.uuid4().hex[:10]}",
                        topic=fact.topic,
                        winning_memory_id=new_id,
                        superseded_memory_id=None,
                        conflicting_memory_id=decision.conflicting_memory_id,
                        resolution_type="conflicting",
                        explanation=decision.explanation,
                    )
                    self.repository.record_conflict_audit(audit_event)

            # 3. Compute tokens & embeddings
            token_count = estimate_tokens(fact.fact_text)
            embedding_vec = self.embedding_provider.embed_text(fact.fact_text)

            # 4. Construct model and persist
            memory_unit = MemoryUnitModel(
                id=new_id,
                fact_text=fact.fact_text,
                topic=fact.topic,
                value=fact.value,
                unit=fact.unit,
                source_document=fact.source_document or source_document,
                source_page=fact.source_page or source_page,
                version_date=fact.version_date,
                author_agent=author_agent,
                source_type=fact.source_type,
                confidence=fact.confidence,
                importance=fact.importance,
                status=status,
                token_count=token_count,
                embedding=json.dumps(embedding_vec) if embedding_vec else None,
                conflict_reason=conflict_reason,
            )

            saved_unit = self.repository.create(memory_unit)
            persisted_units.append(saved_unit)

        return persisted_units
