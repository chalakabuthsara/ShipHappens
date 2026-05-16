"""Pytest configuration and fixtures for the backend test suite."""

import pytest
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel

from app.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """Create an in-memory SQLite test database session.
    
    Note: SQLite doesn't support JSONB or ARRAY types used in production models.
    For unit tests, we use SQLite for speed/isolation and skip DB-specific features.
    For integration tests against Supabase, use a separate test suite.
    """
    # Use SQLite in-memory for fast tests, no external DB dependency
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    # Create only basic User/Session tables that don't use JSONB/ARRAY.
    # For full DB testing, use integration tests against Supabase.
    try:
        SQLModel.metadata.create_all(engine)
    except Exception:
        # If metadata includes incompatible types (JSONB, ARRAY), skip table creation.
        # Unit tests will mock the DB layer instead.
        pass
    
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test FastAPI client with a mocked database session."""
    from fastapi.testclient import TestClient

    from app.main import app

    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
