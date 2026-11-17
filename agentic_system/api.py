from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agentic_system.workflow import run_requirement_workflow


class RequirementRequest(BaseModel):
    requirement: str = Field(..., min_length=10, description="Software requirement text")


class WorkflowResponse(BaseModel):
    requirement: Dict[str, Any]
    status: str
    execution_summary: Dict[str, Any]
    architecture: Dict[str, Any] | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="Agentic Engineering Workflow API", version="1.0.0")

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/v1/requirements/analyze", response_model=WorkflowResponse)
    def analyze_requirement(payload: RequirementRequest) -> Dict[str, Any]:
        workflow_result = run_requirement_workflow(payload.requirement)
        return {
            "requirement": workflow_result["requirement"],
            "status": workflow_result["status"],
            "execution_summary": workflow_result["execution_summary"],
            "architecture": workflow_result.get("architecture"),
        }

    return app


app = create_app()
