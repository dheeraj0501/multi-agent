from fastapi.testclient import TestClient

from agentic_system.api import app
from agentic_system.models import ArchitectureGeneration
from agentic_system.workflow import llm_client


def test_llm_client_requests_schema_constrained_architecture(monkeypatch):
    expected = ArchitectureGeneration(
        summary="A service architecture.",
        components=[],
        data_flow=[],
        apis=[],
        risks=[],
        design_decisions=[],
        open_questions=[],
    )

    class StructuredClient:
        def invoke(self, prompt):
            return expected

    class FakeClient:
        def with_structured_output(self, schema, method):
            assert schema is ArchitectureGeneration
            assert method == "json_schema"
            return StructuredClient()

    monkeypatch.setattr(llm_client, "enabled", True)
    monkeypatch.setattr(llm_client, "client", FakeClient())

    assert llm_client.generate_structured("Design an architecture") is expected


def test_analyze_requirement_returns_generated_architecture(monkeypatch):
    requirement = "Build a library catalog with search and item checkout."
    generated_architecture = {
        "summary": "A library catalog with searchable inventory and checkout workflows.",
        "components": ["Catalog API", "Inventory database", "Search index"],
        "data_flow": ["Search the catalog", "Reserve an available item", "Record checkout"],
        "apis": ["GET /api/v1/items", "POST /api/v1/items/{item_id}/checkout"],
        "risks": ["Search results may be stale after an item is checked out."],
        "design_decisions": ["Index searchable catalog fields."],
        "open_questions": ["Should reservations expire automatically?"],
    }
    prompts = []

    def generate_architecture(prompt):
        prompts.append(prompt)
        return ArchitectureGeneration.model_validate(generated_architecture)

    monkeypatch.setattr(llm_client, "generate_structured", generate_architecture)
    monkeypatch.setattr(llm_client, "generate", lambda prompt: "Plan generated.")

    response = TestClient(app).post(
        "/api/v1/requirements/analyze",
        json={"requirement": requirement},
    )

    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "validated"
    assert result["architecture"] == generated_architecture
    assert requirement in prompts[0]
    assert "Derive every field from this requirement" in prompts[0]


def test_swagger_exposes_only_workflow_endpoints():
    schema = TestClient(app).get("/openapi.json").json()

    assert set(schema["paths"]) == {"/health", "/api/v1/requirements/analyze"}
    assert set(schema["components"]["schemas"]) == {
        "HTTPValidationError",
        "RequirementRequest",
        "ValidationError",
        "WorkflowResponse",
    }
