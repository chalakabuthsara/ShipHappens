from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class SourceFile(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="session.id", index=True)
    filename: str
    storage_path: str  # uploads/{session_id}/{file_uuid}.pdf
    gemini_file_uri: str | None = None  # cached Gemini Files API URI
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
