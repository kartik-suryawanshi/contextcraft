# ContextCraft 🧠

**Intelligent Memory-Orchestration Middleware for LangGraph Multi-Agent Systems**

[![Tests](https://img.shields.io/badge/pytest-13%20passed-emerald)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-teal)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2%2B-orange)](https://github.com/langchain-ai/langgraph)
[![React](https://img.shields.io/badge/React-19-cyan)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-sky)](https://tailwindcss.com)

---

## 1. Executive Summary

ContextCraft is an intelligent memory-orchestration middleware that sits between specialized agents in a LangGraph multi-agent workflow.

In conventional multi-agent Retrieval-Augmented Generation (RAG) and LangGraph systems, agents share an unfiltered, continuously appending conversation history. As a multi-agent session progresses, this induces three critical architectural pathologies:

1. **Token Explosion**: Agents repeatedly receive irrelevant historical dialogue and intermediate scratchpad noise, drastically inflating token consumption and execution costs.
2. **Cognitive Overload ("Lost in the Middle")**: Crucial operational constraints and facts become buried in large, unstructured context windows, degrading agent reasoning quality.
3. **Hallucination Cascades**: Outdated, contradictory, or superseded facts propagate forward between agents unchecked.

### The ContextCraft Solution
ContextCraft acts as a dedicated **first-class graph middleware node** and external memory orchestrator. It maintains structured, atomic memory units in persistent storage (SQLite in MVP, scalable to PostgreSQL + pgvector) and guarantees that:
- **Write Path**: Agent outputs are decomposed into atomic, metadata-rich facts, subjected to deterministic conflict and superseding checks, and stored with full provenance.
- **Read Path**: Each agent receives a role-specific, conflict-free, token-budgeted memory view calculated using multi-factor scoring (Relevance + Recency + Importance + Role Need) and greedy budget assembly.
- **Control State Decoupling**: LangGraph's shared state contains **strictly lightweight routing variables** (zero document chunks or conversational clutter).

---

## 2. Decoupled 5-Layer Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│ Layer 1: LangGraph Multi-Agent Workflow (Control Plane)                 │
│   Supervisor ──> Planner ──> Retriever ──> Executor ──> Critic ──> End │
│   (Lightweight routing state only; no raw document or chat history)    │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │ Intercepts Read/Write Ops
┌─────────────────────────────────▼──────────────────────────────────────┐
│ Layer 2: ContextCraft Memory Orchestrator                              │
│   ┌───────────────────────────────┐ ┌────────────────────────────────┐ │
│   │ WRITE PATH                    │ │ READ PATH                      │ │
│   │ 1. Atomic Fact Extraction     │ │ 1. Active Memory Retrieval     │ │
│   │ 2. Metadata & Confidence      │ │ 2. Multi-Factor Role Scoring   │ │
│   │ 3. Deterministic Conflict Jdg │ │ 3. Deduplication & Ranking     │ │
│   │ 4. Supersede / Conflicting    │ │ 4. Token Budget Assembly       │ │
│   └──────────────┬────────────────┘ └───────────────▲────────────────┘ │
└──────────────────┼──────────────────────────────────┼──────────────────┘
                   │ Commits                          │ Queries
┌──────────────────▼──────────────────────────────────┴──────────────────┐
│ Layer 3: Persistent Memory Store (SQLite + Repository Pattern)         │
│   - Memory Units (id, topic, fact_text, value, unit, status, tokens)   │
│   - Statuses: current | superseded | conflicting                       │
│   - Conflict Audit Events & Execution Traces                           │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │
┌─────────────────────────────────┴──────────────────────────────────────┐
│ Layer 4: External Models & Tool Abstractions                           │
│   - BaseLLMProvider (Deterministic MockLLMProvider + Configurable API) │
│   - BaseEmbeddingProvider (Deterministic Vector Generator)             │
│   - ConflictJudge Interface (Deterministic Conflict Checker)           │
│   - BaseRetrievalProvider (Lexical Relevance & Keyword Matching)       │
└─────────────────────────────────┬──────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼──────────────────────────────────────┐
│ Layer 5: Observability & Evaluation                                    │
│   - Step-by-step trace logging (durations, memory IDs, token counts)   │
│   - Memory View telemetry (component scores, accepted vs. excluded)    │
│   - Real-time dashboard telemetry APIs                                 │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### Backend
- **Python**: 3.12+ (tested on Python 3.14.7)
- **Framework**: FastAPI (REST endpoints & CORS)
- **Workflow Engine**: LangGraph & LangChain Core (StateGraph with conditional loops)
- **Validation**: Pydantic v2 & Pydantic-Settings
- **ORM & Database**: SQLAlchemy 2.0 with SQLite (Repository Pattern for future Postgres migration)
- **Testing**: Pytest & Httpx TestClient

### Frontend
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Vanilla Tailwind CSS v4 (Modern developer dark mode aesthetic)
- **Workflow Visualization**: `@xyflow/react` (React Flow v12)
- **Telemetry Charts**: Recharts
- **Icons**: Lucide-React

---

## 4. Directory Structure

```
contextcraft/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application & lifespan
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── executions.py       # Workflow execution endpoints
│   │   │   │   ├── memories.py         # Memory explorer & audit endpoints
│   │   │   │   ├── dashboard.py        # Real-time metrics endpoints
│   │   │   │   └── health.py           # Health check & connectivity
│   │   │   └── schemas/
│   │   │       ├── execution.py        # Pydantic execution schemas
│   │   │       ├── memory.py           # Pydantic memory schemas
│   │   │       └── dashboard.py        # Dashboard metrics schema
│   │   ├── agents/
│   │   │   ├── base.py                 # BaseAgent with telemetry
│   │   │   ├── supervisor.py           # Supervisor / Router agent
│   │   │   ├── planner.py              # Task decomposer agent
│   │   │   ├── retriever.py            # Memory gap retriever agent
│   │   │   ├── executor.py             # Analytical synthesizer agent
│   │   │   └── critic.py               # Grounding audit & revision agent
│   │   ├── graph/
│   │   │   ├── state.py                # Lightweight control StateGraph state
│   │   │   ├── workflow.py             # Graph assembly & node definitions
│   │   │   └── routing.py              # Conditional edges & revision loop
│   │   ├── memory/
│   │   │   ├── orchestrator.py         # Unified ContextCraft orchestrator
│   │   │   ├── write_path.py           # Fact extraction & ingestion pipeline
│   │   │   ├── read_path.py            # Role context delivery pipeline
│   │   │   ├── fact_extractor.py       # Atomic fact extraction engine
│   │   │   ├── scorer.py               # Role multi-factor scoring formula
│   │   │   ├── budget_assembler.py     # Token budget & deduplication assembler
│   │   │   └── conflict_judge.py       # Deterministic conflict judge
│   │   ├── database/
│   │   │   ├── connection.py           # SQLite connection & sessionmaker
│   │   │   ├── models.py               # SQLAlchemy models
│   │   │   └── repository.py           # Repository Pattern implementations
│   │   ├── providers/
│   │   │   ├── llm.py                  # Mock & Configurable LLM providers
│   │   │   ├── embeddings.py           # Deterministic embeddings provider
│   │   │   └── retrieval.py            # Lexical BM25 retrieval provider
│   │   ├── observability/
│   │   │   └── trace_logger.py         # Step-by-step trace logger
│   │   └── core/
│   │       └── config.py               # Pydantic v2 application settings
│   ├── tests/
│   │   ├── test_fact_extractor.py      # Unit tests for fact extraction
│   │   ├── test_conflict_judge.py      # Unit tests for conflict resolution
│   │   ├── test_scorer.py              # Unit tests for multi-factor scoring
│   │   ├── test_budget_assembler.py    # Unit tests for budget enforcement
│   │   ├── test_repository.py          # Integration tests for SQLite repositories
│   │   ├── test_workflow.py            # Integration tests for LangGraph execution
│   │   └── test_api.py                 # Integration tests for REST APIs
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx              # System status & tab navigation
│   │   │   ├── StatCard.tsx            # KPI metric cards
│   │   │   ├── StatusBadge.tsx         # Current, superseded, conflicting badges
│   │   │   └── AgentNode.tsx           # React Flow custom node component
│   │   ├── features/
│   │   │   ├── dashboard/              # Screen 1: Dashboard
│   │   │   ├── workflow/               # Screen 2: Interactive React Flow
│   │   │   ├── memory/                 # Screen 3: Memory Explorer & Modal
│   │   │   ├── executions/             # Screen 4: Execution Playground
│   │   │   └── memory-inspector/       # Screen 5: Role Memory Inspector
│   │   ├── services/
│   │   │   └── api.ts                  # Typed REST API client
│   │   ├── types/
│   │   │   └── index.ts                # TypeScript entity definitions
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── docs/
│   ├── architecture.md                 # System architecture documentation
│   ├── api.md                          # REST API specification
│   ├── development-roadmap.md          # Multi-phase roadmap
│   └── decisions.md                    # Architectural Decision Records (ADRs)
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.12+ (Python 3.14 compatible)
- Node.js 18+ (Node.js 24 compatible) & npm

### Backend Setup
```bash
# Navigate to repository root
cd d:/Kartik/Purvesh

# Activate or create virtual environment
python -m venv backend/.venv
# On Windows PowerShell:
.\backend\.venv\Scripts\Activate.ps1
# On Linux/macOS:
# source backend/.venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run automated tests
pytest backend/tests/ -v

# Start FastAPI backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be available at: `http://127.0.0.1:8000`
Interactive API Docs (Swagger): `http://127.0.0.1:8000/docs`

### Frontend Setup
```bash
# In a new terminal, navigate to frontend directory
cd d:/Kartik/Purvesh/frontend

# Install dependencies
npm install

# Build production bundle
npm run build

# Start Vite dev server
npm run dev
```

Frontend application will be live at: **`http://127.0.0.1:5173/`**

---

## 6. Functional Demonstration: The Project Orion Scenario

### The User Prompt
> *"Prepare an analysis of Project Orion. Its original budget was ₹10 lakh, the deadline was December 2026, and the project budget was later revised to ₹12 lakh. Explain the current project status using the available information."*

### What ContextCraft Demonstrates:
1. **Fact Extraction on Ingestion**:
   - `Fact 1`: Baseline original budget = ₹10 lakh (Topic: Project Orion Budget, version: v1.0).
   - `Fact 2`: Revised budget = ₹12 lakh (Topic: Project Orion Budget, version: v2.0 revision).
   - `Fact 3`: Timeline deadline = December 2026 (Topic: Project Orion Timeline).
2. **Write-Path Conflict Resolution**:
   - ContextCraft's `DeterministicConflictJudge` compares Fact 2 against Fact 1 on matching topic `Project Orion Budget`.
   - The newer revision amendment supersedes the initial baseline (`confidence 0.98 >= 0.95`).
   - The ₹10 lakh fact is marked **`superseded`** (with `superseded_by` set to Fact 2 ID). It is **never deleted**.
   - The ₹12 lakh fact is marked **`current`**.
   - An immutable conflict audit event is recorded in SQLite.
3. **Role-Specific Read-Path Filtering**:
   - **Supervisor** receives high-level task summaries (role weight 0.35, tokens capped at 200).
   - **Executor** receives confirmed, active quantitative facts (₹12 lakh, Dec 2026) and excludes superseded facts.
   - **Critic** receives draft response paired with citations to verify grounding.
4. **Final Grounded Synthesis**:
   - The agent output confirms that the active project budget is **₹12 lakh**, delivery is **December 2026**, and the original **₹10 lakh** baseline was formally superseded.

---

## 7. Verification & Acceptance Criteria Status

| Requirement / Layer | Acceptance Criteria | Status |
|---|---|:---:|
| **Control State vs Factual Memory** | GraphState carries only control variables; all facts in SQLite | ✅ Verified |
| **LangGraph 5-Agent Workflow** | Supervisor, Planner, Retriever, Executor, Critic + Revision loop | ✅ Verified |
| **Write Path Pipeline** | Fact extraction, metadata, confidence, token heuristics, persistence | ✅ Verified |
| **Deterministic Conflict Handling** | Contradictions superseded without data loss; audit events stored | ✅ Verified |
| **Read Path Pipeline** | Multi-factor role scoring (Rel + Rec + Imp + RoleNeed) & deduplication | ✅ Verified |
| **Token Budget Assembler** | Greedy selection within role budget; logs accepted & excluded units | ✅ Verified |
| **Persistence (Layer 3)** | SQLite with Repository Pattern (models, repositories, transactions) | ✅ Verified |
| **External Providers (Layer 4)** | Deterministic MockLLMProvider + Configurable LLM via env | ✅ Verified |
| **Observability (Layer 5)** | Step durations, token counts, memory IDs, scoring breakdowns logged | ✅ Verified |
| **Frontend Screen 1 (Dashboard)** | Real SQLite telemetry, charts, live status badges | ✅ Verified |
| **Frontend Screen 2 (Workflow)** | Interactive React Flow canvas, node telemetry inspection | ✅ Verified |
| **Frontend Screen 3 (Memory)** | Filterable table (Current, Superseded, Conflicting) + Audit log | ✅ Verified |
| **Frontend Screen 4 (Playground)** | Interactive query submitter, Orion prefill, step progress | ✅ Verified |
| **Frontend Screen 5 (Inspector)** | Explains why each memory was chosen, score breakdown, exclusions | ✅ Verified |
| **Automated Test Suite** | 13/13 Pytest unit & integration tests passing | ✅ Verified |

---

## 8. Current Limitations & Roadmap

### Known MVP Limitations
- **Natural Language Inference (NLI)**: Conflict detection uses deterministic topic semantics and version precedence rather than a heavy transformer cross-encoder.
- **Storage**: SQLite file-based storage (production will use PostgreSQL + pgvector).
- **Retrieval**: Lexical BM25 keyword matching (production will incorporate hybrid dense embeddings).
- **Document Ingestion**: Fact extraction operates on text prompts; full PDF table parsing is planned for Phase 2.

### Phase 2 Roadmap
- [ ] DeBERTa-v3 cross-encoder NLI model integration for semantic contradiction classification.
- [ ] PostgreSQL + pgvector migration with zero changes to repository interfaces.
- [ ] PDF document parser with page-level bounding box citations.
- [ ] Automated baseline benchmarking harness (ContextCraft vs Full-History Baseline token cost & hallucination reduction).
