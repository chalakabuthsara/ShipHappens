from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.services import papers as papers_service

router = APIRouter(prefix="/papers", tags=["papers"])


@router.post("/sessions/{session_id}/blueprint", response_model=dict, summary="Upsert blueprint JSON for a session", description="Persists blueprint JSON for the session using `papers.upsert_blueprint` service. This stores the AI-extracted blueprint which is later used to generate papers.")
def upsert_blueprint(session_id: UUID, payload: dict, session: Session = Depends(get_session)):
    p = papers_service.upsert_blueprint(session_id, payload, session)
    return {"id": str(p.id), "updated_at": p.updated_at.isoformat()}


@router.get("/sessions/{session_id}", response_model=dict)
def get_paper(session_id: UUID, session: Session = Depends(get_session)):
    p = papers_service.get_paper(session_id, session)
    if not p:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {"id": str(p.id), "paper": p.paper_json or {}, "blueprint": p.blueprint_json or {}}
