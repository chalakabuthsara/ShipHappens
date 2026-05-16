from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.services import sourcefiles as sourcefiles_service
from app.schemas import SourceFileRead

router = APIRouter(prefix="/sessions/{session_id}/uploads", tags=["uploads"])


@router.post("/", response_model=SourceFileRead, summary="Upload a PDF for a session", description="Saves uploaded file to local storage (dev) and creates a `SourceFile` row via `sourcefiles.save_source_file` service. In production this should use Supabase Storage.")
def upload_file(session_id: UUID, file: UploadFile = File(...), session: Session = Depends(get_session)):
    try:
        content = file.file.read()
        sf = sourcefiles_service.save_source_file(session_id, file.filename, content, session)
        return sf
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
