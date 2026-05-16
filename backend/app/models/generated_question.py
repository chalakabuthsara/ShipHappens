from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import Field, SQLModel


class GeneratedQuestion(SQLModel, table=True):
    """Individual question in a generated paper"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    paper_id: UUID = Field(foreign_key="paper.id", index=True)
    generation_request_id: UUID = Field(
        foreign_key="generationrequest.id", index=True
    )
    question_number: str  # "1", "2", "3", etc.
    question_text: str
    question_type: str  # "mcq", "structured", "calculation"
    topic: str
    subtopics: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    difficulty: str
    marks: int
    solution: str
    mark_scheme: str | None = None
    has_diagram: bool = False
    generation_metadata: dict = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )  # Generation params used
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
