"""Test questions router and service."""

from uuid import uuid4
from datetime import datetime, UTC
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.models.question import Question


def test_list_questions_empty(client: TestClient):
    """Test listing questions when session has no questions."""
    session_id = uuid4()
    
    with patch("app.routers.questions.questions_service.list_questions") as mock_service:
        mock_service.return_value = []
        response = client.get(f"/sessions/{session_id}/questions/")
        assert response.status_code == 200
        assert response.json() == []


def test_list_questions_returns_all(client: TestClient):
    """Test listing all questions for a session."""
    session_id = uuid4()
    mock_questions = [
        Question(
            id=uuid4(),
            session_id=session_id,
            question_number=1,
            question_text="What is photosynthesis?",
            created_at=datetime.now(UTC)
        ),
        Question(
            id=uuid4(),
            session_id=session_id,
            question_number=2,
            question_text="How does mitochondria work?",
            created_at=datetime.now(UTC)
        ),
        Question(
            id=uuid4(),
            session_id=session_id,
            question_number=3,
            question_text="What are proteins?",
            created_at=datetime.now(UTC)
        ),
    ]
    
    with patch("app.routers.questions.questions_service.list_questions") as mock_service:
        mock_service.return_value = mock_questions
        response = client.get(f"/sessions/{session_id}/questions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["number"] == 1
        assert data[0]["text"] == "What is photosynthesis?"
        assert data[1]["number"] == 2
        assert data[2]["number"] == 3


def test_list_questions_format(client: TestClient):
    """Test that list_questions returns correct field format."""
    session_id = uuid4()
    question_id = uuid4()
    mock_questions = [
        Question(
            id=question_id,
            session_id=session_id,
            question_number=1,
            question_text="Sample question?",
            created_at=datetime.now(UTC)
        ),
    ]
    
    with patch("app.routers.questions.questions_service.list_questions") as mock_service:
        mock_service.return_value = mock_questions
        response = client.get(f"/sessions/{session_id}/questions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        item = data[0]
        # Verify response has id, text, and number fields
        assert "id" in item
        assert "text" in item
        assert "number" in item
        assert item["id"] == str(question_id)
        assert item["text"] == "Sample question?"
        assert item["number"] == 1


def test_list_questions_filters_by_session_id(client: TestClient):
    """Test that list_questions filters questions by session."""
    session_id = uuid4()
    other_session_id = uuid4()
    
    # Service should only return questions for the given session_id
    mock_questions = [
        Question(
            id=uuid4(),
            session_id=session_id,
            question_number=1,
            question_text="Question for session 1",
            created_at=datetime.now(UTC)
        ),
    ]
    
    with patch("app.routers.questions.questions_service.list_questions") as mock_service:
        mock_service.return_value = mock_questions
        response = client.get(f"/sessions/{session_id}/questions/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Verify service was called with correct session_id
        mock_service.assert_called_once()
        call_args = mock_service.call_args
        assert call_args[0][0] == session_id
