from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionBase(BaseModel):
    title: str | None = None
    board: str | None = None
    level: str | None = None
    subject: str | None = None


class SessionCreate(SessionBase):
    pass


class SessionRead(SessionBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
