from __future__ import annotations

from dataclasses import dataclass, field
from typing import Annotated, Any, Dict, List

from pydantic import BaseModel, ConfigDict, StringConstraints


@dataclass
class Task:
    id: str
    title: str
    description: str
    dependencies: List[str] = field(default_factory=list)
    output: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "dependencies": self.dependencies,
            "output": self.output,
        }


@dataclass
class Architecture:
    summary: str
    components: List[str]
    data_flow: List[str]
    apis: List[str]
    risks: List[str]
    design_decisions: List[str]
    open_questions: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "components": self.components,
            "data_flow": self.data_flow,
            "apis": self.apis,
            "risks": self.risks,
            "design_decisions": self.design_decisions,
            "open_questions": self.open_questions,
        }


NonEmptyString = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ArchitectureGeneration(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: NonEmptyString
    components: List[NonEmptyString]
    data_flow: List[NonEmptyString]
    apis: List[NonEmptyString]
    risks: List[NonEmptyString]
    design_decisions: List[NonEmptyString]
    open_questions: List[NonEmptyString]
