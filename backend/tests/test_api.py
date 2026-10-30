import pytest
from fastapi.testclient import TestClient
from backend.app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "ContextCraft"


def test_dashboard_metrics_endpoint(client):
    response = client.get("/api/v1/dashboard/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_executions" in data
    assert "total_memory_units" in data
    assert "mock_mode" in data


def test_execution_creation_and_retrieval(client):
    payload = {
        "query": (
            "Prepare an analysis of Project Orion. Its original budget was ₹10 lakh, "
            "the deadline was December 2026, and the project budget was later revised to ₹12 lakh."
        ),
        "max_iterations": 2,
        "mock_mode": True,
    }
    create_res = client.post("/api/v1/executions", json=payload)
    assert create_res.status_code == 201
    exec_data = create_res.json()
    execution_id = exec_data["id"]
    assert exec_data["status"] == "completed"
    assert exec_data["final_answer"] is not None

    # Retrieve execution details
    get_res = client.get(f"/api/v1/executions/{execution_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == execution_id

    # Retrieve execution traces
    traces_res = client.get(f"/api/v1/executions/{execution_id}/traces")
    assert traces_res.status_code == 200
    traces = traces_res.json()
    assert len(traces) >= 5

    # Retrieve memory views
    views_res = client.get(f"/api/v1/executions/{execution_id}/memory-views")
    assert views_res.status_code == 200
    views = views_res.json()
    assert len(views) >= 5

    # Retrieve memories list
    mems_res = client.get("/api/v1/memories")
    assert mems_res.status_code == 200
    mems = mems_res.json()
    assert mems["total"] >= 3

    # Check superseded filter
    superseded_res = client.get("/api/v1/memories?status=superseded")
    assert superseded_res.status_code == 200
    assert superseded_res.json()["total"] >= 1
