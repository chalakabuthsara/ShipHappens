from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .question import Difficulty, QuestionType

GeneratedPaperStatus = Literal["draft", "finalized"]


class GeneratedQuestion(BaseModel):
    question_text: str
    question_type: QuestionType
    topic: str
    subtopics: list[str] = Field(default_factory=list)
    difficulty: Difficulty
    marks: int
    solution: str | None = None
    mark_scheme: str | None = None
    has_diagram: bool = False


class GeneratedPaperBase(BaseModel):
    teacher_id: UUID
    request_params: dict[str, Any] = Field(default_factory=dict)
    questions: list[dict[str, Any]] = Field(default_factory=list)
    status: GeneratedPaperStatus = "draft"


class GeneratedPaperCreate(GeneratedPaperBase):
    pass


class GeneratedPaperRead(GeneratedPaperBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
