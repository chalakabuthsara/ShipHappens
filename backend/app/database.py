from typing import Generator

from sqlmodel import Session, create_engine, select
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Create SQLModel engine pointing to Supabase PostgreSQL
engine = create_engine(
    settings.database_url,
    echo=False,  # Set to True for SQL query logging
    pool_size=10,
    max_overflow=20,
)

SessionLocal = sessionmaker(
    engine, class_=Session, expire_on_commit=False
)


def get_session() -> Generator[Session, None, None]:
    """Dependency for FastAPI to get a database session"""
    with SessionLocal() as session:
        yield session
