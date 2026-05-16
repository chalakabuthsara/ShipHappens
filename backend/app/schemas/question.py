from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

QuestionType = Literal["mcq", "structured", "calculation"]
Difficulty = Literal["easy", "medium", "hard"]


class QuestionBase(BaseModel):
    paper_id: UUID
    teacher_id: UUID
    question_number: str
    question_text: str
    question_type: QuestionType
    topic: str
    subtopics: list[str] = Field(default_factory=list)
    difficulty: Difficulty
    marks: int
    solution: str | None = None
    mark_scheme: str | None = None
    has_diagram: bool = False
    embedding: list[float] | None = None
    source_page: int | None = None


class QuestionCreate(QuestionBase):
    pass


class QuestionRead(QuestionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
