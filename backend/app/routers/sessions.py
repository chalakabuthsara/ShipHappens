from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.services import sessions as sessions_service
from app.schemas import SessionCreate, SessionRead

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/", response_model=SessionRead, summary="Create a new session", description="Creates a session row grouping uploaded source files and generated papers. Underlying service `sessions.create_session` inserts a `Session` SQLModel record.")
def create_session(payload: SessionCreate, session: Session = Depends(get_session)):
    s = sessions_service.create_session(payload.model_dump(), session)
    return s


@router.get("/", response_model=list[SessionRead], summary="List sessions", description="Lists sessions. Calls `sessions.list_sessions` service which queries `Session` table.")
def list_sessions(session: Session = Depends(get_session)):
    rows = sessions_service.list_sessions(session)
    return rows


@router.get("/{session_id}", response_model=SessionRead, summary="Get session", description="Retrieves a session by id. Uses `sessions.get_session_by_id` service.")
def get_session_by_id(session_id: UUID, session: Session = Depends(get_session)):
    row = sessions_service.get_session_by_id(session_id, session)
    if not row:
        raise HTTPException(status_code=404, detail="Session not found")
    return row
