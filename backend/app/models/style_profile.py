from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class StyleProfile(SQLModel, table=True):
    """Analyzed style/pattern profile from questions in a session"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="session.id", unique=True, index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    topic_distribution: dict = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )  # {"Algebra": 0.3, "Geometry": 0.25, ...}
    question_type_mix: dict = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )  # {"mcq": 0.4, "structured": 0.6}
    difficulty_distribution: dict = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )  # {"easy": 0.2, "medium": 0.5, "hard": 0.3}
    stylistic_traits: list[str] = Field(
        default_factory=list
    )  # Specific patterns observed
    preferred_phrasings: list[str] = Field(default_factory=list)  # Common phrases
    topic_pairing_patterns: list[str] = Field(default_factory=list)
    marks_distribution: dict = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )  # {"avg": 5.2, "max": 15}
    total_questions_analyzed: int = 0
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)
