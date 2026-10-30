from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os


class BaseLLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Generates a text completion given a prompt."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the provider name and model identifier."""
        pass


class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock provider for zero-cost, reproducible local testing."""

    def __init__(self, model_name: str = "mock-contextcraft-v1"):
        self.model_name = model_name

    def get_provider_name(self) -> str:
        return f"Mock Provider ({self.model_name})"

    def generate(self, prompt: str, system_message: Optional[str] = None) -> str:
        prompt_lower = prompt.lower()

        # Handle specific agent prompts deterministically
        if "supervisor" in prompt_lower or "routing" in prompt_lower:
            return "Task received. Routing to Planner to decompose project requirements and identify required factual context."

        if "planner" in prompt_lower or "decompose" in prompt_lower:
            return (
                "Task Decomposition Plan:\n"
                "1. Identify project identity and constraints (Project Orion).\n"
                "2. Determine baseline financial metrics (original budget: 10 lakh INR).\n"
                "3. Check for updates, revisions, or amendments (revised budget: 12 lakh INR).\n"
                "4. Identify milestones and delivery timeline (deadline: December 2026).\n"
                "5. Synthesize current status and report verified figures."
            )

        if "retriever" in prompt_lower or "retrieve" in prompt_lower:
            return (
                "Retriever Analysis: Querying active memory store for Project Orion. "
                "Factual gaps identified: initial budget, revision amendments, timeline."
            )

        if "executor" in prompt_lower or "analyst" in prompt_lower:
            return (
                "Project Orion Status Analysis:\n\n"
                "• Current Budget: ₹12 lakh (revised from initial baseline of ₹10 lakh).\n"
                "• Timeline / Milestone: December 2026 delivery.\n"
                "• Operational Status: The project is progressing towards its December 2026 deadline with an approved revised expenditure budget of ₹12 lakh. "
                "The original allocation of ₹10 lakh has been formally superseded."
            )

        if "critic" in prompt_lower or "verifier" in prompt_lower:
            return (
                "Critic Verification Report:\n"
                "Status: VALIDATED\n"
                "1. Factual Grounding: All statements match verified active memory units (₹12 lakh current budget, Dec 2026 deadline).\n"
                "2. Conflict Audit: Superseded ₹10 lakh baseline is properly contextualized and not conflated with active budget.\n"
                "3. Recommendation: Pass to Final Response."
            )

        # Fallback generic completion
        return f"Processed query: {prompt[:120]}..."


class ConfigurableLLMProvider(BaseLLMProvider):
    """Configurable LLM provider supporting OpenAI-compatible APIs with fallback to MockLLMProvider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("CONTEXTCRAFT_OPENAI_API_KEY", "")
        self.model = model
        self.mock_fallback = MockLLMProvider()

    def get_provider_name(self) -> str:
        if self.api_key:
            return f"OpenAI ({self.model})"
        return f"Mock Provider (Fallback: No API key configured)"

    def generate(self, prompt: str, system_message: Optional[str] = None) -> str:
        if not self.api_key:
            return self.mock_fallback.generate(prompt, system_message)

        try:
            from langchain_core.messages import SystemMessage, HumanMessage
            from langchain_openai import ChatOpenAI
            
            chat = ChatOpenAI(model=self.model, api_key=self.api_key, temperature=0.1)
            messages = []
            if system_message:
                messages.append(SystemMessage(content=system_message))
            messages.append(HumanMessage(content=prompt))
            response = chat.invoke(messages)
            return str(response.content)
        except Exception:
            # Safe graceful fallback to mock provider
            return self.mock_fallback.generate(prompt, system_message)
