# ContextCraft System Architecture

## 1. Executive Summary

ContextCraft is an intelligent memory-orchestration middleware designed for multi-agent LLM systems implemented in LangGraph. Rather than allowing conversation history to bloat within a shared graph state (leading to Token Explosion, Cognitive Overload, and Hallucination Cascades), ContextCraft maintains atomic, structured memory units in a persistent store and delivers role-specific, conflict-aware, token-budgeted memory views to each agent.

## 2. Decoupled Architectural Layers

The architecture consists of five decoupled layers:

```
┌────────────────────────────────────────────────────────────────────────┐
│ Layer 1: LangGraph Multi-Agent Workflow (Control Plane)                 │
│   Supervisor ──> Planner ──> Retriever ──> Executor ──> Critic ──> End │
│   (Maintains ONLY lightweight control metadata; no heavy fact dumping)   │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │ Intercepts Read/Write Ops
┌─────────────────────────────────▼──────────────────────────────────────┐
│ Layer 2: ContextCraft Memory Orchestrator                              │
│   ┌───────────────────────────────┐ ┌────────────────────────────────┐ │
│   │ WRITE PATH                    │ │ READ PATH                      │ │
│   │ 1. Fact Extraction            │ │ 1. Active Memories Query       │ │
│   │ 2. Unit Structuring           │ │ 2. Multi-factor Scoring        │ │
│   │ 3. Metadata & Confidence      │ │ 3. Role Preferences Weighting │ │
│   │ 4. Deterministic Conflict Jdg │ │ 4. Deduplication & Ranking     │ │
│   │ 5. Supersede / Conflict Status│ │ 5. Token Budget Assembly       │ │
│   └──────────────┬────────────────┘ └───────────────▲────────────────┘ │
└──────────────────┼──────────────────────────────────┼──────────────────┘
                   │ Commits                          │ Queries
┌──────────────────▼──────────────────────────────────┴──────────────────┐
│ Layer 3: Persistent Memory Store (SQLite + Repository Pattern)         │
│   - Memory Units (id, topic, fact_text, value, unit, status, etc.)    │
│   - Statuses: current | superseded | conflicting                       │
│   - Execution Traces & Audit Logs                                      │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │
┌─────────────────────────────────┴──────────────────────────────────────┐
│ Layer 4: External Models and Tool Abstractions                         │
│   - LLM Provider (Configurable Real API + Deterministic Mock Provider) │
│   - Embedding Provider (Deterministic Vector/Lexical Generator)        │
│   - Conflict Judge (Contradiction & Update Resolution)                 │
│   - Document / Lexical Retrieval Provider                              │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼──────────────────────────────────────┐
│ Layer 5: Observability & Evaluation                                    │
│   - Execution Tracing (Step durations, Memory IDs, Token usage)        │
│   - Memory View Inspection (Per-agent scores, excluded facts, budget)  │
│   - Dashboard Telemetry APIs                                           │
└────────────────────────────────────────────────────────────────────────┘
```

## 3. Control State vs. Factual Memory

A core architectural invariant in ContextCraft is the strict separation between:

- **Shared Graph State (Control Plane)**: Contains only operational control variables:
  - `user_query`: str
  - `task_id`: str
  - `execution_id`: str
  - `current_agent`: str
  - `execution_status`: str ("pending" | "running" | "completed" | "failed")
  - `routing_target`: str
  - `iteration_count`: int
  - `max_iterations`: int
  - `final_answer`: Optional[str]
  - `error_status`: Optional[str]

- **Substantive Factual Memory (Data Plane)**:
  - Resides entirely inside the ContextCraft Memory Store (`MemoryUnit` records).
  - Agents NEVER read raw SQL rows directly or carry past conversational histories.
  - Agents receive a dedicated `RoleMemoryView` generated dynamically by ContextCraft's Read Path.

## 4. Role Profiles and Scoring Formula

For each candidate active memory unit $m$ and target role $R$, ContextCraft evaluates:

$$\text{Total Score}(m, R) = w_{\text{rel}} \cdot S_{\text{relevance}}(m, q) + w_{\text{rec}} \cdot S_{\text{recency}}(m) + w_{\text{imp}} \cdot S_{\text{importance}}(m) + w_{\text{role}} \cdot S_{\text{role\_need}}(m, R)$$

Where:
- $S_{\text{relevance}}$: Lexical / semantic similarity to current task.
- $S_{\text{recency}}$: Exponential or linear decay based on creation/version date.
- $S_{\text{importance}}$: Intrinsic importance rating (0.0 to 1.0).
- $S_{\text{role\_need}}$: Preference matrix matching agent role requirements:
  - **Supervisor**: Summaries, high-level task status, constraints.
  - **Planner**: Task decomposition, constraints, prerequisites.
  - **Retriever**: Questions, gaps, missing information.
  - **Executor**: Verified facts, concrete values, units, current status.
  - **Critic**: Draft outputs, citations, source references.

## 5. Conflict Resolution Strategy

When newly extracted memory units arrive during the Write Path:
1. Topic Match: Check existing records with matching or overlapping normalized topic keys.
2. Contradiction Detection: If values, dates, or qualitative states differ, invoke the `ConflictJudge`.
3. Reliability & Versioning: Compare `version_date`, source authority, and confidence scores.
4. Status Lifecycle:
   - Winning fact remains `current`.
   - Confirmed outdated fact transitions to `superseded` (historical record preserved; never physically deleted).
   - Unresolved ambiguities become `conflicting` and trigger verification review.
