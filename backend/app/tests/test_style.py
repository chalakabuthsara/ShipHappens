"""Test style router and service."""

from uuid import uuid4
from datetime import datetime, UTC
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.models.style_profile import StyleProfile


def test_get_style_profile_found(client: TestClient):
    """Test retrieving a style profile."""
    session_id = uuid4()
    profile_id = uuid4()
    profile_data = {"topics": {"math": 0.5, "science": 0.3, "writing": 0.2}}
    
    mock_profile = StyleProfile(
        id=profile_id,
        session_id=session_id,
        topic_distribution=profile_data,
        updated_at=datetime.now(UTC)
    )
    
    with patch("app.routers.style.style_service.get_style_profile") as mock_service:
        mock_service.return_value = mock_profile
        response = client.get(f"/sessions/{session_id}/style/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(profile_id)
        assert data["profile"] == profile_data


def test_get_style_profile_not_found(client: TestClient):
    """Test retrieving non-existent style profile returns 404."""
    session_id = uuid4()
    
    with patch("app.routers.style.style_service.get_style_profile") as mock_service:
        mock_service.return_value = None
        response = client.get(f"/sessions/{session_id}/style/")
        assert response.status_code == 404


def test_get_style_profile_empty_distribution(client: TestClient):
    """Test retrieving style profile with empty distribution."""
    session_id = uuid4()
    profile_id = uuid4()
    
    mock_profile = StyleProfile(
        id=profile_id,
        session_id=session_id,
        topic_distribution=None,
        updated_at=datetime.now(UTC)
    )
    
    with patch("app.routers.style.style_service.get_style_profile") as mock_service:
        mock_service.return_value = mock_profile
        response = client.get(f"/sessions/{session_id}/style/")
        assert response.status_code == 200
        data = response.json()
        assert data["profile"] == {}


def test_analyze_style_create_new(client: TestClient):
    """Test creating a new style analysis."""
    session_id = uuid4()
    profile_id = uuid4()
    analysis_data = {"topics": {"math": 0.6, "science": 0.4}}
    
    mock_profile = StyleProfile(
        id=profile_id,
        session_id=session_id,
        topic_distribution=analysis_data,
        updated_at=datetime.now(UTC)
    )
    
    with patch("app.routers.style.style_service.analyze_style") as mock_service:
        mock_service.return_value = mock_profile
        response = client.post(
            f"/sessions/{session_id}/style/analyze",
            json={"analysis_type": "comprehensive"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(profile_id)
        assert data["profile"] == analysis_data


def test_analyze_style_update_existing(client: TestClient):
    """Test updating an existing style analysis."""
    session_id = uuid4()
    profile_id = uuid4()
    new_analysis = {"topics": {"math": 0.7, "science": 0.3}}
    
    mock_profile = StyleProfile(
        id=profile_id,
        session_id=session_id,
        topic_distribution=new_analysis,
        updated_at=datetime.now(UTC)
    )
    
    with patch("app.routers.style.style_service.analyze_style") as mock_service:
        mock_service.return_value = mock_profile
        response = client.post(
            f"/sessions/{session_id}/style/analyze",
            json={"topics": {"math": 0.7, "science": 0.3}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["profile"] == new_analysis


def test_analyze_style_with_no_payload(client: TestClient):
    """Test analyze style with empty payload uses default."""
    session_id = uuid4()
    profile_id = uuid4()
    
    mock_profile = StyleProfile(
        id=profile_id,
        session_id=session_id,
        topic_distribution={"note": "analysis placeholder"},
        updated_at=datetime.now(UTC)
    )
    
    with patch("app.routers.style.style_service.analyze_style") as mock_service:
        mock_service.return_value = mock_profile
        response = client.post(f"/sessions/{session_id}/style/analyze")
        assert response.status_code == 200
        data = response.json()
        assert data["profile"]["note"] == "analysis placeholder"
