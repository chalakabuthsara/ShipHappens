from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

IngestionStatus = Literal["pending", "processing", "done", "failed"]


class PaperBase(BaseModel):
    teacher_id: UUID
    filename: str
    raw_pdf_url: str | None = None
    markdown_content: str | None = None
    ingestion_status: IngestionStatus = "pending"


class PaperCreate(PaperBase):
    pass


class PaperRead(PaperBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
