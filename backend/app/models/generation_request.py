from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlmodel import Field, SQLModel


class GenerationRequest(SQLModel, table=True):
    """User request to generate a new exam paper"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="session.id", index=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    topics: list[str] = Field(
        default_factory=list, sa_column=Column(ARRAY(String))
    )  # Topics to include in paper
    total_questions: int  # How many questions to generate
    mcq_percentage: int = 0  # 0-100
    difficulty_mix: dict = Field(
        default_factory=dict, sa_column=Column(JSONB)
    )  # {"easy": 20, "medium": 50, "hard": 30}
    duration_minutes: int = 60
    status: str = "pending"  # "pending", "processing", "completed", "failed"
    error_message: str | None = None
    generated_paper_id: UUID | None = Field(
        foreign_key="paper.id", nullable=True
    )  # Link to generated Paper
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
