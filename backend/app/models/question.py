from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel


class Question(SQLModel, table=True):
    """Extracted question from a source paper"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    source_file_id: UUID = Field(foreign_key="sourcefile.id", index=True)
    session_id: UUID = Field(foreign_key="session.id", index=True)
    question_number: str  # e.g., "1", "2a", "3(ii)"
    question_text: str  # Full question with LaTeX
    question_type: str  # "mcq", "structured", "calculation", "essay"
    topic: str  # e.g., "Algebra", "Geometry"
    subtopics: list[str] = Field(default_factory=list, sa_column=Column(ARRAY(String)))
    difficulty: str  # "easy", "medium", "hard"
    marks: int
    solution: str | None = None  # Worked solution with LaTeX
    mark_scheme: str | None = None  # Mark breakdown
    has_diagram: bool = False
    source_page: int | None = None
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
