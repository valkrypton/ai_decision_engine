from typing import Any
from pydantic import BaseModel, Field


class DecisionState(BaseModel):
    input: str = ""
    intent: str = ""
    entities: dict[str, Any] = Field(default_factory=dict)
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    enriched: list[dict[str, Any]] = Field(default_factory=list)
    ranked: list[dict[str, Any]] = Field(default_factory=list)
    final_response: str = ""
    domain: str = ""
    error: str = ""
