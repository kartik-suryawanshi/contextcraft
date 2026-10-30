from typing import List, Dict, Any, Optional
import re
import uuid


class ExtractedFact:
    def __init__(
        self,
        fact_text: str,
        topic: str,
        value: Optional[str] = None,
        unit: Optional[str] = None,
        version_date: Optional[str] = None,
        confidence: float = 0.9,
        importance: float = 0.5,
        source_type: str = "agent_inference",
        source_document: Optional[str] = None,
        source_page: Optional[int] = None,
    ):
        self.fact_text = fact_text.strip()
        self.topic = topic.strip()
        self.value = value
        self.unit = unit
        self.version_date = version_date
        self.confidence = confidence
        self.importance = importance
        self.source_type = source_type
        self.source_document = source_document
        self.source_page = source_page

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fact_text": self.fact_text,
            "topic": self.topic,
            "value": self.value,
            "unit": self.unit,
            "version_date": self.version_date,
            "confidence": self.confidence,
            "importance": self.importance,
            "source_type": self.source_type,
            "source_document": self.source_document,
            "source_page": self.source_page,
        }


class FactExtractor:
    """Extracts atomic, structured facts from unstructured natural language text."""

    def __init__(self):
        # Compiled regex patterns for entity & value recognition
        self.budget_revised_pattern = re.compile(
            r"(?:revised|updated|increased|amended)\s+(?:to\s+)?(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(lakh|cr|crore|k|million|billion)?(?:\s*inr)?",
            re.IGNORECASE,
        )
        self.budget_original_pattern = re.compile(
            r"(?:original|initial|allocated|initial\s+budget)\s+(?:budget\s+)?(?:was|of)?\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(lakh|cr|crore|k|million|billion)?(?:\s*inr)?",
            re.IGNORECASE,
        )
        self.deadline_pattern = re.compile(
            r"(?:deadline|completion|delivery|target\s+date)\s+(?:was|is)?\s*([a-zA-Z]+\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{4})",
            re.IGNORECASE,
        )
        self.project_pattern = re.compile(
            r"(?:project\s+([A-Z][a-zA-Z0-9_\-]+))",
            re.IGNORECASE,
        )

    def extract_facts(
        self,
        text: str,
        author_agent: str = "system",
        source_type: str = "user_input",
        source_document: Optional[str] = None,
    ) -> List[ExtractedFact]:
        facts: List[ExtractedFact] = []
        if not text:
            return facts

        # Extract Project Name context
        proj_match = self.project_pattern.search(text)
        project_name = f"Project {proj_match.group(1)}" if proj_match else "General Project"

        # Check for original budget
        orig_match = self.budget_original_pattern.search(text)
        if orig_match:
            val = orig_match.group(1)
            scale = orig_match.group(2) or "INR"
            unit = f"{scale} INR" if scale != "INR" else "INR"
            facts.append(
                ExtractedFact(
                    fact_text=f"{project_name} original baseline budget was ₹{val} {scale}".strip(),
                    topic=f"{project_name} Budget",
                    value=val,
                    unit=unit,
                    version_date="v1.0 (Original Baseline)",
                    confidence=0.95,
                    importance=0.7,
                    source_type=source_type,
                    source_document=source_document,
                )
            )

        # Check for revised budget
        rev_match = self.budget_revised_pattern.search(text)
        if rev_match:
            val = rev_match.group(1)
            scale = rev_match.group(2) or "INR"
            unit = f"{scale} INR" if scale != "INR" else "INR"
            facts.append(
                ExtractedFact(
                    fact_text=f"{project_name} budget was revised to ₹{val} {scale}".strip(),
                    topic=f"{project_name} Budget",
                    value=val,
                    unit=unit,
                    version_date="v2.0 (Revision Amendment)",
                    confidence=0.98,
                    importance=0.95,
                    source_type=source_type,
                    source_document=source_document,
                )
            )

        # Check for deadline
        dl_match = self.deadline_pattern.search(text)
        if dl_match:
            val = dl_match.group(1).strip()
            facts.append(
                ExtractedFact(
                    fact_text=f"{project_name} delivery deadline is scheduled for {val}",
                    topic=f"{project_name} Timeline",
                    value=val,
                    unit="date",
                    version_date="v1.0 (Target Milestone)",
                    confidence=0.95,
                    importance=0.85,
                    source_type=source_type,
                    source_document=source_document,
                )
            )

        # If no specific patterns matched, perform sentence-level atomic extraction
        if not facts:
            sentences = [s.strip() for s in re.split(r"[.!?]\s+", text) if len(s.strip()) > 10]
            for s in sentences:
                facts.append(
                    ExtractedFact(
                        fact_text=s,
                        topic="General Task Context",
                        confidence=0.85,
                        importance=0.5,
                        source_type=source_type,
                        source_document=source_document,
                    )
                )

        return facts
