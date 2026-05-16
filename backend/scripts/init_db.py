"""
Script to initialize the database and create all tables.

Usage:
    uv run python -m scripts.init_db
"""

from sqlmodel import SQLModel, Session

from app.database import engine
from app.models import (
    ApiUsageLog,
    GeneratedQuestion,
    GenerationRequest,
    Paper,
    Question,
    QuestionEmbedding,
    Session as SessionModel,
    SourceFile,
    StyleProfile,
    User,
)


def init_db():
    """Create all tables in the database"""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("✓ Database initialized successfully!")


if __name__ == "__main__":
    init_db()
