# Agentic Engineering System with LangGraph

This workspace contains a working prototype of an agentic software engineering system built around a LangGraph workflow. It demonstrates requirement interpretation, task decomposition, dependency-aware orchestration, generated engineering artifacts, and validation guardrails.

## Example input
The prototype accepts software requirements as input and produces a general engineering plan.

## What the system demonstrates
- Requirement understanding and ambiguity detection
- Structured task decomposition with dependencies
- Architecture planning for a real engineering system
- Multi-step orchestration through a LangGraph state machine
- Generation of artifact sketches and validation strategy
- Human-controlled autonomy and review gates

## Architecture overview
The workflow is implemented in `agentic_system/workflow.py` and includes these phases:

1. Analyze requirement
2. Decompose tasks
3. Design architecture
4. Build execution plan
5. Generate artifacts
6. Validate and mark workflow as complete

Key components:
- `agentic_system/workflow.py` - orchestration logic
- `agentic_system/models.py` - task and architecture data structures
- `agentic_system/api.py` - health and requirement-analysis endpoints
- `tests/test_api.py` - API behavior tests
- `docs/architecture.md` - architecture and risk notes

## Example scenarios
The prototype also includes sample requirement types in `sample_requirements.py`:
- Greenfield: a new software service
- Brownfield: enhancement of current behavior
- Ambiguous: underspecified product requirement

## Execution model
The system uses a dependency graph rather than a simple linear pipeline. Each task has explicit dependencies and sequencing, which allows the workflow to coordinate multiple steps and preserve cross-step execution flow.

## Validation approach
The prototype validates correctness through:
- Tests for requirement analysis and API behavior
- Human approval gate before production rollout

## Setup
From the workspace root:

1. Install dependencies:
   python -m pip install -r requirements.txt
2. Enable requirement-specific architecture generation:
   `$env:USE_LLM = 'true'`
   `$env:GEMINI_API_KEY = '<your Gemini API key>'`
   (`GOOGLE_API_KEY` is also supported.)
3. Run the workflow demo:
   python demo.py
4. Run tests:
   $env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = '1'; python -m pytest -q
5. Run with uvicorn
   uvicorn agentic_system.api:app --host 127.0.0.1 --port 8000

The architecture summary, components, data flow, APIs, risks, design decisions, and open questions are generated from each submitted requirement. If the LLM is not configured or returns an invalid architecture, analysis reports an error instead of returning a generic static architecture.

## Known limitations
This is a prototype intended to demonstrate agentic engineering orchestration rather than a full production deployment. Workflow outputs are illustrative and require review before use in a production system.

# This is a multi agent system

Building this project to run multi agent system for SRE