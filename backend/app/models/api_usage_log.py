from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class ApiUsageLog(SQLModel, table=True):
    """Track API calls for cost tracking and rate limiting"""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    session_id: UUID | None = Field(foreign_key="session.id", nullable=True)
    api_provider: str  # "gemini", "supabase", etc.
    operation: str  # "embed", "generate", "transcribe", "upload"
    tokens_used: int | None = None
    cost_usd: float = 0.0
    status: str  # "success", "failed", "rate_limited"
    error_message: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
