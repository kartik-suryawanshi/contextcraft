# ContextCraft Development Roadmap

## Phase 0: Foundation & Environment (Completed in Current Session)
- [x] Monorepo layout and workspace structure.
- [x] Python 3.12+ backend virtual environment and FastAPI server skeleton.
- [x] SQLite database schema with SQLAlchemy models & Repository Pattern.
- [x] React + TypeScript + Vite frontend setup with Tailwind CSS.
- [x] System documentation (Architecture, API specs, ADRs).
- [x] Health check endpoints and CORS configuration.

## Phase 1: Initial MVP (Completed in Current Session)
- [x] **LangGraph Multi-Agent Workflow**:
  - Supervisor (Router)
  - Planner (Decomposer)
  - Retriever (Gap Identifier & Fetcher)
  - Executor (Synthesis & Calculation)
  - Critic (Verification & Revision Loop)
- [x] **ContextCraft Memory Orchestration**:
  - Write Path: Atomic fact extraction, metadata annotation, token estimation, persistence.
  - Read Path: Role-specific memory views, multi-factor scoring (Relevance + Recency + Importance + Role Need), greedy budget assembler.
  - Deterministic conflict detection and supersede lifecycle.
- [x] **Observability & Tracing**:
  - Step-by-step agent trace logging in SQLite.
  - Granular Memory View inspection telemetry (scoring weights, chosen vs. excluded facts).
- [x] **Professional UI Dashboard**:
  - Live Overview Metrics.
  - Interactive LangGraph Flow Visualization (React Flow).
  - Searchable Memory Explorer with status filters.
  - Execution Playground with step-by-step progress.
  - Role-Specific Memory View Inspector.
- [x] **Automated Test Suite**:
  - Fact extraction, scoring, conflict detection, repository CRUD, end-to-end execution.

---

## Phase 2: NLI, Vector Indexing & Hybrid RAG (Future Roadmap)
- [ ] Integration of transformer-based NLI model (DeBERTa-v3 or similar) for non-deterministic logical contradiction detection.
- [ ] Vector database migration (PostgreSQL + pgvector).
- [ ] Dense semantic embedding generation (OpenAI text-embedding-3 or local BGE models).
- [ ] External document ingestion pipeline (PDF table extraction, chunking, and source page indexing).
- [ ] Comparative baseline benchmark suite (ContextCraft vs. Full-History Baseline token and hallucination comparison).

## Phase 3: Production & Distributed Agent Mesh (Future Roadmap)
- [ ] Distributed message queue for parallel agent execution.
- [ ] Multi-tenant organization isolation and access control.
- [ ] Enterprise audit trail export and compliance logging.
- [ ] Dynamic adaptive role weights learned via reinforcement from human feedback (RLHF).
