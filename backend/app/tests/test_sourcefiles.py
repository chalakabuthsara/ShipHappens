"""Test sourcefiles router and service."""

from uuid import uuid4
from datetime import datetime, UTC
from io import BytesIO
from unittest.mock import patch, MagicMock, mock_open

from fastapi.testclient import TestClient

from app.models.source_file import SourceFile


def test_upload_file_success(client: TestClient):
    """Test successful file upload."""
    session_id = uuid4()
    sf_id = uuid4()
    filename = "test_document.pdf"
    
    mock_sourcefile = SourceFile(
        id=sf_id,
        session_id=session_id,
        filename=filename,
        storage_path=f"data/uploads/{session_id}_{filename}",
        uploaded_at=datetime.now(UTC)
    )
    
    with patch("app.routers.sourcefiles.sourcefiles_service.save_source_file") as mock_service:
        mock_service.return_value = mock_sourcefile
        
        # Create a mock file upload
        file_content = b"PDF file content here"
        files = {"file": (filename, BytesIO(file_content), "application/pdf")}
        
        response = client.post(
            f"/sessions/{session_id}/uploads/",
            files=files
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(sf_id)
        assert data["filename"] == filename
        assert data["storage_path"] == f"data/uploads/{session_id}_{filename}"


def test_upload_file_multiple(client: TestClient):
    """Test uploading multiple files to same session."""
    session_id = uuid4()
    
    mock_files = [
        SourceFile(
            id=uuid4(),
            session_id=session_id,
            filename="file1.pdf",
            storage_path=f"data/uploads/{session_id}_file1.pdf",
            uploaded_at=datetime.now(UTC)
        ),
        SourceFile(
            id=uuid4(),
            session_id=session_id,
            filename="file2.pdf",
            storage_path=f"data/uploads/{session_id}_file2.pdf",
            uploaded_at=datetime.now(UTC)
        ),
    ]
    
    for mock_file in mock_files:
        with patch("app.routers.sourcefiles.sourcefiles_service.save_source_file") as mock_service:
            mock_service.return_value = mock_file
            
            files = {"file": (mock_file.filename, BytesIO(b"content"), "application/pdf")}
            response = client.post(
                f"/sessions/{session_id}/uploads/",
                files=files
            )
            assert response.status_code == 200
            data = response.json()
            assert data["filename"] == mock_file.filename


def test_upload_file_error(client: TestClient):
    """Test file upload error handling."""
    session_id = uuid4()
    
    with patch("app.routers.sourcefiles.sourcefiles_service.save_source_file") as mock_service:
        mock_service.side_effect = Exception("Disk full")
        
        files = {"file": ("test.pdf", BytesIO(b"content"), "application/pdf")}
        response = client.post(
            f"/sessions/{session_id}/uploads/",
            files=files
        )
        assert response.status_code == 500
        assert "Failed to save file" in response.json()["detail"]


def test_upload_preserves_session_id(client: TestClient):
    """Test that uploaded file is associated with correct session."""
    session_id = uuid4()
    sf_id = uuid4()
    filename = "document.pdf"
    
    mock_sourcefile = SourceFile(
        id=sf_id,
        session_id=session_id,
        filename=filename,
        storage_path=f"data/uploads/{session_id}_{filename}",
        uploaded_at=datetime.now(UTC)
    )
    
    with patch("app.routers.sourcefiles.sourcefiles_service.save_source_file") as mock_service:
        mock_service.return_value = mock_sourcefile
        
        files = {"file": (filename, BytesIO(b"pdf content"), "application/pdf")}
        response = client.post(
            f"/sessions/{session_id}/uploads/",
            files=files
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == filename
        
        # Verify service was called with correct session_id
        mock_service.assert_called_once()
        call_args = mock_service.call_args
        assert call_args[0][0] == session_id


def test_upload_filename_preserved(client: TestClient):
    """Test that original filename is preserved."""
    session_id = uuid4()
    sf_id = uuid4()
    filename = "my_research_paper_2024.pdf"
    
    mock_sourcefile = SourceFile(
        id=sf_id,
        session_id=session_id,
        filename=filename,
        storage_path=f"data/uploads/{session_id}_{filename}",
        uploaded_at=datetime.now(UTC)
    )
    
    with patch("app.routers.sourcefiles.sourcefiles_service.save_source_file") as mock_service:
        mock_service.return_value = mock_sourcefile
        
        files = {"file": (filename, BytesIO(b"pdf content"), "application/pdf")}
        response = client.post(
            f"/sessions/{session_id}/uploads/",
            files=files
        )
        assert response.status_code == 200
        data = response.json()
        assert data["filename"] == filename
