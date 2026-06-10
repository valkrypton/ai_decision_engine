from typing import Any
from pydantic import BaseModel, Field


class DecisionState(BaseModel):
    input: str = ""
    intent: str = ""
    entities: dict[str, Any] = Field(default_factory=dict)
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    enriched: list[dict[str, Any]] = Field(default_factory=list)
    ranked: list[dict[str, Any]] = Field(default_factory=list)
    evaluation: dict[str, Any] = Field(default_factory=dict)
    final_response: str = ""
    domain: str = ""
    error: str = ""


class PipelineInput(BaseModel):
    input: str
    domain: str


class PipelineOutput(BaseModel):
    domain: str
    intent: str
    entities: dict[str, Any]
    candidates_count: int
    ranked: list[dict[str, Any]]
    final_response: str
