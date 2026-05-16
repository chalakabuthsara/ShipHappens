from datetime import datetime
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlmodel import Field, SQLModel


class QuestionEmbedding(SQLModel, table=True):
    """pgvector embeddings for semantic search of questions"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    question_id: UUID = Field(foreign_key="question.id", unique=True, index=True)
    embedding: Vector = Field(
        sa_column_kwargs={"postgresql_using": "hnsw"}
    )  # 768-dim Gemini text-embedding-004
    embedded_at: datetime = Field(default_factory=datetime.utcnow)
