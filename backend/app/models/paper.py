from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Paper(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    session_id: UUID = Field(foreign_key="session.id", unique=True, index=True)
    blueprint_json: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    paper_json: dict = Field(default_factory=dict, sa_column=Column(JSONB))
    updated_at: datetime = Field(default_factory=datetime.utcnow)
