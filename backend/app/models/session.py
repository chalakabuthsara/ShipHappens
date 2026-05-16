from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Session(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    title: str | None = None
    board: str | None = None  # e.g. "Cambridge", "AQA", "Edexcel"
    level: str | None = None  # e.g. "A Level", "AS Level"
    subject: str | None = None  # e.g. "English Literature"
