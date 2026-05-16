from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TeacherBase(BaseModel):
    name: str
    subject: str


class TeacherCreate(TeacherBase):
    pass


class TeacherRead(TeacherBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
