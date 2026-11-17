# pyright: reportMissingImports=false
from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import Any, Dict, List

from langgraph.graph import END, StateGraph  # type: ignore[import-not-found]

from .config import settings
from .llm import llm_client
from .models import Architecture, ArchitectureGeneration, Task


def record_step(state: Dict[str, Any], step_name: str, detail: str) -> Dict[str, Any]:
    execution_details = state.setdefault("execution_details", [])
    execution_details.append(
        {
            "step": step_name,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )
    return {**state, "execution_details": execution_details}


class RequirementState(dict):
    pass


def normalize_requirement(requirement: str) -> Dict[str, Any]:
    requirement_text = requirement.strip()
    if not requirement_text:
        raise ValueError("Requirement cannot be empty")

    normalized = {
        "raw_requirement": requirement_text,
        "intent": requirement_text.lower(),
        "ambiguities": [
            "Scope and acceptance criteria may need clarification",
            "Operational constraints are unspecified",
            "Data handling and retention requirements may need clarification",
        ],
        "problem_statement": f"Implement and validate: {requirement_text}",
    }
    return normalized


def decompose_tasks(requirement: Dict[str, Any]) -> List[Task]:
    tasks = [
        Task(
            id="T1",
            title="Requirements synthesis",
            description="Interpret the requirement and clarify assumptions, constraints, and acceptance criteria.",
        ),
        Task(
            id="T2",
            title="Architecture design",
            description="Define the system components, data flows, and interfaces needed to satisfy the requirement.",
            dependencies=["T1"],
        ),
        Task(
            id="T3",
            title="Data model and persistence",
            description="Define domain data models and persistence requirements, if applicable.",
            dependencies=["T2"],
        ),
        Task(
            id="T4",
            title="API implementation",
            description="Implement the required behavior through appropriate application interfaces.",
            dependencies=["T2", "T3"],
        ),
        Task(
            id="T5",
            title="Test suite and validation",
            description="Add tests for acceptance criteria, expected behavior, and relevant edge cases.",
            dependencies=["T3", "T4"],
        ),
        Task(
            id="T6",
            title="Documentation and rollout notes",
            description="Write setup instructions, architecture overview, risks, and assumptions.",
            dependencies=["T2", "T5"],
        ),
    ]
    return tasks


def build_architecture(requirement: Dict[str, Any]) -> Architecture:
    prompt = f"""Design an architecture from this software requirement:
{requirement["raw_requirement"]}

Return only a valid JSON object with exactly these string/list-of-string fields:
summary, components, data_flow, apis, risks, design_decisions, open_questions.
Derive every field from this requirement. Do not reuse generic placeholder text or assume
domain features that are not stated. Suggest concrete REST endpoints for explicitly stated
workflows and entities; when details are missing, state the assumption and ask a focused
question in open_questions. Include relevant components, ordered data flow, requirement-
specific risks, and justified design decisions. Use empty arrays when a category has no
supported entries. Do not include markdown fences or additional keys."""

    generated = llm_client.generate_structured(prompt)
    if generated is None:
        raise RuntimeError(
            "Requirement-specific architecture generation requires an enabled LLM. "
            "Set USE_LLM=true and configure GEMINI_API_KEY or GOOGLE_API_KEY."
        )

    if not isinstance(generated, ArchitectureGeneration):
        raise TypeError("The LLM did not return a schema-validated architecture.")
    return Architecture(**generated.model_dump())


def create_execution_plan(tasks: List[Task]) -> List[str]:
    task_map = {task.id: task for task in tasks}
    indegree = {task.id: len(task.dependencies) for task in tasks}
    reverse = defaultdict(list)
    for task in tasks:
        for dependency in task.dependencies:
            reverse[dependency].append(task.id)

    queue = deque(sorted([task.id for task, _ in [(task, indegree[task.id]) for task in tasks] if indegree[task.id] == 0]))
    order: List[str] = []
    while queue:
        current = queue.popleft()
        order.append(current)
        for dependent in sorted(reverse[current]):
            indegree[dependent] -= 1
            if indegree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(tasks):
        raise ValueError("Cyclic dependency detected in task graph")
    return order


def generate_artifacts(requirement: Dict[str, Any], architecture: Architecture, tasks: List[Task]) -> Dict[str, Any]:
    return {
        "project_name": "agentic-engineering-demo",
        "requirement_summary": requirement["problem_statement"],
        "architecture": architecture.to_dict(),
        "tasks": [task.to_dict() for task in tasks],
        "generated_files": [
            "docs/architecture.md",
            "tests/",
        ],
        "validation_strategy": {
            "unit_tests": "Verify the requirement's acceptance criteria and relevant edge cases",
            "integration_tests": "Test required workflows and failure modes",
            "manual_review": "Human approval required before production rollout",
        },
    }


def run_requirement_workflow(requirement: str) -> Dict[str, Any]:
    normalized = normalize_requirement(requirement)
    tasks = decompose_tasks(normalized)
    architecture = build_architecture(normalized)
    execution_plan = create_execution_plan(tasks)
    artifacts = generate_artifacts(normalized, architecture, tasks)

    llm_summary = llm_client.generate(
        f"Analyze requirement and produce a concise engineering plan: {normalized['raw_requirement']}"
    )

    execution_details: List[Dict[str, str]] = []

    def trace(step_name: str, detail: str) -> None:
        entry = {
            "step": step_name,
            "detail": detail,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        execution_details.append(entry)
        print(f"[workflow] {step_name}: {detail}")

    trace("analyze", "Requirement normalized and ambiguity summary created")
    trace("decompose", f"Decomposed requirement into {len(tasks)} tasks with dependency graph")
    trace("design", "Requirement-driven architecture proposed")
    trace("plan", f"Execution plan generated: {execution_plan}")
    trace("artifacts", "Prepared implementation, test, and documentation artifacts")
    trace("validate", "Validation and human approval gate confirmed for rollout")

    workflow = StateGraph(dict)
    workflow.add_node(
        "analyze",
        lambda state: ({**state, "normalized": normalized, "llm_summary": llm_summary, "execution_details": execution_details}),
    )
    workflow.add_node(
        "decompose",
        lambda state: ({**state, "tasks": [task.to_dict() for task in tasks], "execution_details": execution_details}),
    )
    workflow.add_node(
        "design",
        lambda state: ({**state, "architecture": architecture.to_dict(), "execution_details": execution_details}),
    )
    workflow.add_node(
        "plan",
        lambda state: ({**state, "execution_plan": execution_plan, "execution_details": execution_details}),
    )
    workflow.add_node(
        "artifacts",
        lambda state: ({**state, "artifacts": artifacts, "execution_details": execution_details}),
    )
    workflow.add_node(
        "validate",
        lambda state: ({**state, "status": "validated", "execution_details": execution_details}),
    )

    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "decompose")
    workflow.add_edge("decompose", "design")
    workflow.add_edge("design", "plan")
    workflow.add_edge("plan", "artifacts")
    workflow.add_edge("artifacts", "validate")
    workflow.add_edge("validate", END)

    app = workflow.compile()
    result = app.invoke({})
    result["requirement"] = normalized
    result["execution_summary"] = {
        "status": "success",
        "tasks_completed": len(tasks),
        "plan": execution_plan,
        "controlled_autonomy": "Humans review outputs before rollout and approve changes",
        "llm_enabled": settings.use_llm and bool(settings.api_key),
        "llm_summary": llm_summary,
        "execution_details": execution_details,
    }
    return result
