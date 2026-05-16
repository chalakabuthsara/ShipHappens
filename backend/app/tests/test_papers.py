"""Test papers router and service."""

from uuid import UUID, uuid4
from datetime import datetime, UTC
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.models.paper import Paper


def test_upsert_blueprint_create_new(client: TestClient):
    """Test creating a new blueprint."""
    session_id = uuid4()
    blueprint_data = {"key": "value", "sections": ["intro", "body"]}
    
    mock_paper = Paper(
        id=uuid4(),
        session_id=session_id,
        blueprint_json=blueprint_data,
        paper_json={},
        updated_at=datetime.now(UTC)
    )
    
    with patch("app.routers.papers.papers_service.upsert_blueprint") as mock_service:
        mock_service.return_value = mock_paper
        response = client.post(
            f"/papers/sessions/{session_id}/blueprint",
            json=blueprint_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(mock_paper.id)
        assert "updated_at" in data


def test_upsert_blueprint_update_existing(client: TestClient):
    """Test updating an existing blueprint."""
    session_id = uuid4()
    paper_id = uuid4()
    new_blueprint = {"key": "updated_value", "sections": ["intro", "body", "conclusion"]}
    
    mock_paper = Paper(
        id=paper_id,
        session_id=session_id,
        blueprint_json=new_blueprint,
        paper_json={},
        updated_at=datetime.now(UTC)
    )
    
    with patch("app.routers.papers.papers_service.upsert_blueprint") as mock_service:
        mock_service.return_value = mock_paper
        response = client.post(
            f"/papers/sessions/{session_id}/blueprint",
            json=new_blueprint
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(paper_id)


def test_get_paper_found(client: TestClient):
    """Test retrieving paper with blueprint and paper JSON."""
    session_id = uuid4()
    paper_id = uuid4()
    blueprint = {"sections": ["intro", "body"]}
    paper_content = {"title": "My Paper", "content": "..."}
    
    mock_paper = Paper(
        id=paper_id,
        session_id=session_id,
        blueprint_json=blueprint,
        paper_json=paper_content,
        updated_at=datetime.now(UTC)
    )
    
    with patch("app.routers.papers.papers_service.get_paper") as mock_service:
        mock_service.return_value = mock_paper
        response = client.get(f"/papers/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(paper_id)
        assert data["blueprint"] == blueprint
        assert data["paper"] == paper_content


def test_get_paper_not_found(client: TestClient):
    """Test retrieving non-existent paper returns 404."""
    session_id = uuid4()
    
    with patch("app.routers.papers.papers_service.get_paper") as mock_service:
        mock_service.return_value = None
        response = client.get(f"/papers/sessions/{session_id}")
        assert response.status_code == 404


def test_get_paper_empty_json_fields(client: TestClient):
    """Test retrieving paper with empty JSON fields."""
    session_id = uuid4()
    paper_id = uuid4()
    
    mock_paper = Paper(
        id=paper_id,
        session_id=session_id,
        blueprint_json=None,
        paper_json=None,
        updated_at=datetime.now(UTC)
    )
    
    with patch("app.routers.papers.papers_service.get_paper") as mock_service:
        mock_service.return_value = mock_paper
        response = client.get(f"/papers/sessions/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["blueprint"] == {}
        assert data["paper"] == {}
