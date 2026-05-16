from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StyleProfileBase(BaseModel):
    teacher_id: UUID
    observed_patterns: dict[str, Any] = Field(default_factory=dict)
    total_questions_analyzed: int = 0


class StyleProfileCreate(StyleProfileBase):
    pass


class StyleProfileRead(StyleProfileBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    last_updated: datetime
