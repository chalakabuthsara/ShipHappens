from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GenerationRequestBase(BaseModel):
    topics: list[str] = Field(default_factory=list)
    total_questions: int = 0
    mcq_percentage: int | None = None
    difficulty_mix: dict[str, Any] = Field(default_factory=dict)
    duration_minutes: int | None = None


class GenerationRequestCreate(GenerationRequestBase):
    pass


class GenerationRequestRead(GenerationRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    status: str
    created_at: datetime
    completed_at: datetime | None = None
