import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client():
    return TestClient(main.app)


def test_root(client):
    assert client.get("/").json() == {"status": "Backend is running"}


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "ok"
    assert set(body["tools"]) == {"blender", "rhubarb"}


def test_cors_allows_vite_dev_origin(client):
    res = client.options(
        "/api/plan",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
    )
    assert res.status_code == 200
    assert res.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_cors_rejects_unknown_origin(client):
    res = client.options(
        "/api/plan",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert "access-control-allow-origin" not in res.headers


def test_compile_success(client, sample_plan):
    res = client.post("/api/compile", json=sample_plan)
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "success"
    assert body["compiled_script"].startswith("import bpy")


def test_compile_invalid_plan_returns_422(client):
    res = client.post("/api/compile", json={"character": "Aiko"})
    assert res.status_code == 422
    assert "duration_seconds" in res.json()["detail"]


def test_plan_uses_planner(client, monkeypatch):
    monkeypatch.setattr(main, "generate_plan", lambda c, r, s: {"character": c, "duration_seconds": 1})
    res = client.post("/api/plan", json={"character": "Aiko", "request_text": "wave"})
    assert res.status_code == 200
    assert res.json()["plan"]["character"] == "Aiko"


@pytest.mark.parametrize("payload", [
    {"character": "", "request_text": "wave"},
    {"character": "Aiko", "request_text": "   "},
    {"character": "Aiko"},
])
def test_plan_request_validation(client, payload):
    assert client.post("/api/plan", json=payload).status_code == 422


def test_knowledge_query_bounds(client):
    assert client.post("/api/knowledge/query", json={"query": "x", "n_results": 0}).status_code == 422
    assert client.post("/api/knowledge/query", json={"query": ""}).status_code == 422


def test_dataset_generate_requires_non_blank_prompt(client):
    res = client.post("/api/dataset/generate", json={"character": "Aiko", "prompts": ["", "  "]})
    assert res.status_code == 422


def test_dataset_list_empty(client):
    res = client.get("/api/dataset/list")
    assert res.status_code == 200
    assert res.json() == {"status": "success", "datasets": []}


def test_finetune_status_without_output(client):
    data = client.get("/api/finetune/status").json()["data"]
    assert data == {"lora_output_exists": False, "gguf_exists": False, "gguf_file": None}


def test_plan_reports_mock_fallback_as_valid(client):
    # OLLAMA_URL points at an unroutable port in conftest, so the mock plan is used.
    body = client.post("/api/plan", json={"character": "Aiko", "request_text": "wave"}).json()
    assert body["mock"] is True
    assert body["valid"] is True
    assert body["validation_error"] is None


def test_plan_flags_invalid_llm_output(client, monkeypatch):
    monkeypatch.setattr(main, "generate_plan", lambda c, r, s: {"character": "Aiko", "duration_seconds": -1})
    body = client.post("/api/plan", json={"character": "Aiko", "request_text": "wave"}).json()
    assert body["status"] == "success"
    assert body["valid"] is False
    assert "duration_seconds" in body["validation_error"]
    assert body["mock"] is False


@pytest.mark.parametrize("metadata", [{"tags": ["a", "b"]}, {"nested": {"x": 1}}, {"none": None}])
def test_knowledge_rejects_non_scalar_metadata(client, metadata):
    res = client.post("/api/knowledge/add", json={"content": "rig notes", "metadata": metadata})
    assert res.status_code == 422


def test_dataset_rejects_oversized_prompt(client):
    res = client.post("/api/dataset/generate", json={"character": "Aiko", "prompts": ["x" * 4001]})
    assert res.status_code == 422


def test_query_rejects_oversized_text(client):
    res = client.post("/api/knowledge/query", json={"query": "x" * 4001})
    assert res.status_code == 422


def test_internal_errors_do_not_leak_details(client, monkeypatch):
    def boom(*a):
        raise RuntimeError("secret path /home/me/.env")

    monkeypatch.setattr(main, "generate_plan", boom)
    res = client.post("/api/plan", json={"character": "Aiko", "request_text": "wave"})
    assert res.status_code == 500
    assert "secret" not in res.text
