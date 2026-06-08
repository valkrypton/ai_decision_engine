from typing import Any
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    domain: str = Field(
        description="Domain to query. Use 'auto' to detect automatically.",
        examples=["carddeals", "hirestream", "leadfinder", "travelplanner", "auto"],
    )
    input: str = Field(description="Natural language query from the user.")
    modality: str = Field(default="text", description="Input modality: 'text' or 'audio'.")
    audio_path: str | None = Field(
        default=None,
        description="Path to audio file. Required when modality='audio'.",
    )


class QueryResponse(BaseModel):
    domain: str
    intent: str
    entities: dict[str, Any]
    candidates_count: int
    ranked: list[dict[str, Any]]
    final_response: str
    latency_seconds: float
