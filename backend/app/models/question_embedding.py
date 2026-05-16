from datetime import datetime, UTC
from uuid import UUID, uuid4

from sqlalchemy import Column
from pgvector.sqlalchemy import Vector
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


class QuestionEmbedding(SQLModel, table=True):
    """pgvector embeddings for semantic search of questions"""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    question_id: UUID = Field(foreign_key="question.id", unique=True, index=True)
    embedding: list[float] = Field(
        sa_column=Column(Vector(768))
    )  # 768-dim Gemini text-embedding-004
    embedded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
