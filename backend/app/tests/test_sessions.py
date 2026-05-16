"""Test session router and service."""

from uuid import UUID, uuid4
from datetime import datetime, UTC
from unittest.mock import Mock, patch, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.models.session import Session as SessionModel
from app.services import sessions as sessions_service


def test_list_sessions_empty(client: TestClient):
    """Test listing sessions when empty."""
    with patch("app.services.sessions.select") as mock_select:
        with patch("app.routers.sessions.sessions_service.list_sessions") as mock_service:
            mock_service.return_value = []
            response = client.get("/sessions/")
            assert response.status_code == 200
            assert response.json() == []


def test_list_sessions_returns_all(client: TestClient):
    """Test listing multiple sessions."""
    session1_id = uuid4()
    session2_id = uuid4()
    mock_sessions = [
        SessionModel(id=session1_id, title="Math", created_at=datetime.now(UTC)),
        SessionModel(id=session2_id, title="Science", created_at=datetime.now(UTC)),
    ]
    
    with patch("app.routers.sessions.sessions_service.list_sessions") as mock_service:
        mock_service.return_value = mock_sessions
        response = client.get("/sessions/")
        assert response.status_code == 200
        sessions_data = response.json()
        assert len(sessions_data) == 2
        assert sessions_data[0]["id"] == str(session1_id)
        assert sessions_data[1]["id"] == str(session2_id)


def test_create_session(client: TestClient):
    """Test creating a new session."""
    session_id = uuid4()
    mock_session = SessionModel(
        id=session_id,
        title="Physics 101",
        board="Cambridge",
        level="A Level",
        subject="Physics",
        created_at=datetime.now(UTC)
    )
    
    with patch("app.routers.sessions.sessions_service.create_session") as mock_service:
        mock_service.return_value = mock_session
        
        payload = {"title": "Physics 101", "board": "Cambridge", "level": "A Level", "subject": "Physics"}
        response = client.post("/sessions/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(session_id)
        assert data["title"] == "Physics 101"


def test_get_session_by_id_found(client: TestClient):
    """Test retrieving a session by ID."""
    session_id = uuid4()
    mock_session = SessionModel(
        id=session_id,
        title="History",
        created_at=datetime.now(UTC)
    )
    
    with patch("app.routers.sessions.sessions_service.get_session_by_id") as mock_service:
        mock_service.return_value = mock_session
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(session_id)


def test_get_session_by_id_not_found(client: TestClient):
    """Test retrieving a non-existent session returns 404."""
    session_id = uuid4()
    
    with patch("app.routers.sessions.sessions_service.get_session_by_id") as mock_service:
        mock_service.return_value = None
        response = client.get(f"/sessions/{session_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
