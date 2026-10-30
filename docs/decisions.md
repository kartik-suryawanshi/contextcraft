# Architectural Decision Records (ADRs)

## ADR-001: Separation of Control State vs. Factual Memory
- **Status**: Accepted
- **Context**: Passing full chat histories or large factual document chunks through LangGraph's shared state causes token explosion, loss of grounding, and cascading hallucinations.
- **Decision**: Restrict LangGraph's shared state strictly to control metadata (user query, routing targets, current step, execution status, iteration count, final answer). Store all factual knowledge in an external structured repository (`MemoryUnit` SQLite table) mediated by the ContextCraft Memory Orchestrator.
- **Consequences**: Agents only receive tailored, token-bounded slices of facts (`RoleMemoryView`). Eliminates state bloat and preserves auditability.

## ADR-002: Repository Pattern for Persistence
- **Status**: Accepted
- **Context**: MVP uses SQLite for zero-setup execution, but production will require PostgreSQL with pgvector for high concurrency and vector similarity indexing.
- **Decision**: Define clean repository interfaces (`MemoryRepository`, `TraceRepository`, `ExecutionRepository`) with SQLAlchemy implementations.
- **Consequences**: Switching from SQLite to Postgres in Phase 2 requires no changes to agent or memory orchestration code.

## ADR-003: Deterministic Write-Time Conflict Resolution
- **Status**: Accepted
- **Context**: Multi-agent systems encounter conflicting statements across multiple iterations or revised facts (e.g., "Budget is 10L" vs "Budget revised to 12L").
- **Decision**: Perform conflict checking on the Write Path before facts become active. Contradicted prior facts transition to `superseded` status, never deleted. Unresolvable contradictions transition to `conflicting`.
- **Consequences**: Agents querying active memory only receive current facts, while historical provenance is preserved for audits.

## ADR-004: Multi-Factor Read-Time Scoring & Greedy Budget Assembly
- **Status**: Accepted
- **Context**: Semantic similarity alone is inadequate for multi-agent workflows (e.g., planners need task constraints, executors need figures and values).
- **Decision**: Calculate Total Score = $w_{\text{rel}} \cdot \text{Relevance} + w_{\text{rec}} \cdot \text{Recency} + w_{\text{imp}} \cdot \text{Importance} + w_{\text{role}} \cdot \text{RoleNeed}$. Assemble memory views within strict per-agent token limits using greedy selection and near-duplicate filtering.
- **Consequences**: Every agent receives optimal context density without exceeding token caps.

## ADR-005: Deterministic Mock LLM Provider for Zero-Cost Testing
- **Status**: Accepted
- **Context**: The project must run without requiring paid API keys while maintaining full support for real LLM backends via environment variables.
- **Decision**: Implement `MockLLMProvider` alongside `ConfigurableLLMProvider`. Flag mock mode clearly in the UI and API responses.
- **Consequences**: Reproducible local testing, continuous integration without credentials, and instant demonstration capabilities.
