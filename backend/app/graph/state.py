from typing import TypedDict, Optional, List, Dict, Any


class GraphState(TypedDict):
    """LangGraph Control State - strictly maintains lightweight control flow metadata.
    
    CRITICAL ARCHITECTURAL INVARIANT:
    Never append raw documents, historical transcripts, or large facts here.
    All factual memory resides in ContextCraft Memory Store.
    """
    user_query: str
    task_id: str
    execution_id: str
    current_agent: str
    execution_status: str  # "pending", "running", "completed", "revision_required", "failed"
    routing_target: str
    iteration_count: int
    max_iterations: int
    step_count: int
    final_answer: Optional[str]
    error_status: Optional[str]
