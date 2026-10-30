# ContextCraft REST API Specification

Base URL: `/api/v1`

## Endpoints

### 1. Health Check
- **`GET /health`**
  - **Description**: Returns API and database connectivity status.
  - **Response 200**:
    ```json
    {
      "status": "healthy",
      "version": "1.0.0",
      "database": "connected",
      "mock_mode": true
    }
    ```

### 2. Executions
- **`POST /executions`**
  - **Description**: Initiates a new multi-agent workflow execution.
  - **Request Body**:
    ```json
    {
      "query": "Prepare an analysis of Project Orion...",
      "max_iterations": 2,
      "mock_mode": true
    }
    ```
  - **Response 201**:
    ```json
    {
      "id": "exec-abc12345",
      "user_query": "Prepare an analysis of Project Orion...",
      "status": "completed",
      "iteration_count": 1,
      "final_answer": "...",
      "total_duration_ms": 340,
      "total_tokens_estimated": 1280,
      "created_at": "2026-10-30T07:30:00Z"
    }
    ```

- **`GET /executions`**
  - **Description**: Lists past workflow executions with pagination.
  - **Parameters**: `limit` (default 20), `offset` (default 0)
  - **Response 200**: `List[ExecutionSummary]`

- **`GET /executions/{execution_id}`**
  - **Description**: Retrieves full details of a specific execution.
  - **Response 200**: `ExecutionDetail`

- **`GET /executions/{execution_id}/traces`**
  - **Description**: Returns chronologically ordered agent execution traces for the execution.
  - **Response 200**: `List[AgentExecutionTrace]`

- **`GET /executions/{execution_id}/memory-views`**
  - **Description**: Returns all role-specific memory views provided to each agent, including candidate score breakdowns and excluded units.
  - **Response 200**: `List[RoleMemoryViewInspection]`

### 3. Memory Units
- **`GET /memories`**
  - **Description**: Queries persistent memory units with filtering.
  - **Parameters**:
    - `status`: "current" | "superseded" | "conflicting" (optional)
    - `topic`: string filter (optional)
    - `author_agent`: string filter (optional)
    - `limit`: int (default 50)
    - `offset`: int (default 0)
  - **Response 200**:
    ```json
    {
      "total": 3,
      "items": [
        {
          "id": "mem-1",
          "fact_text": "Project Orion revised budget is 12 lakh INR",
          "topic": "Project Orion Budget",
          "value": "12",
          "unit": "lakh INR",
          "status": "current",
          "confidence": 0.95,
          "importance": 0.9,
          "token_count": 18,
          "version_date": "2026-10-30",
          "author_agent": "executor",
          "created_at": "2026-10-30T07:30:00Z"
        }
      ]
    }
    ```

- **`GET /memories/{memory_id}`**
  - **Description**: Returns full record and audit trail of a specific memory unit.
  - **Response 200**: `MemoryUnitDetail`

### 4. Dashboard Metrics
- **`GET /dashboard/metrics`**
  - **Description**: Aggregated real-time metrics computed directly from database tables.
  - **Response 200**:
    ```json
    {
      "total_executions": 12,
      "successful_executions": 12,
      "failed_executions": 0,
      "total_memory_units": 45,
      "current_memory_units": 38,
      "superseded_memory_units": 7,
      "conflicting_memory_units": 0,
      "average_duration_ms": 420.5,
      "total_estimated_tokens": 15420,
      "agent_distribution": {
        "supervisor": 12,
        "planner": 12,
        "retriever": 12,
        "executor": 12,
        "critic": 12
      }
    }
    ```
