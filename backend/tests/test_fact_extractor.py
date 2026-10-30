import pytest
from backend.app.memory.fact_extractor import FactExtractor


def test_fact_extractor_project_orion():
    extractor = FactExtractor()
    text = (
        "Prepare an analysis of Project Orion. Its original budget was ₹10 lakh, "
        "the deadline was December 2026, and the project budget was later revised to ₹12 lakh. "
        "Explain the current project status using the available information."
    )
    facts = extractor.extract_facts(text, author_agent="user_input")
    assert len(facts) >= 3

    # Check original budget fact
    orig = next((f for f in facts if f.value == "10"), None)
    assert orig is not None
    assert orig.topic == "Project Orion Budget"
    assert "lakh" in orig.unit.lower()

    # Check revised budget fact
    rev = next((f for f in facts if f.value == "12"), None)
    assert rev is not None
    assert rev.topic == "Project Orion Budget"
    assert "Revision" in rev.version_date

    # Check deadline fact
    dl = next((f for f in facts if "December 2026" in str(f.value)), None)
    assert dl is not None
    assert dl.topic == "Project Orion Timeline"


def test_fact_extractor_generic_fallback():
    extractor = FactExtractor()
    text = "The system components must communicate over encrypted TLS channels."
    facts = extractor.extract_facts(text, author_agent="user_input")
    assert len(facts) == 1
    assert "TLS" in facts[0].fact_text
