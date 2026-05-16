from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.services import style as style_service

router = APIRouter(prefix="/sessions/{session_id}/style", tags=["style"])


@router.get("/", response_model=dict, summary="Get style profile", description="Retrieves the computed style profile for a session. Uses `style.get_style_profile` service which returns persisted analysis results.")
def get_style(session_id: UUID, session: Session = Depends(get_session)):
    sp = style_service.get_style_profile(session_id, session)
    if not sp:
        raise HTTPException(status_code=404, detail="Style profile not found")
    return {"id": str(sp.id), "profile": sp.topic_distribution or {}}


@router.post("/analyze", response_model=dict, summary="Analyze teaching style from session questions", description="Runs style analysis over session questions and persists a StyleProfile record. Implementation lives in `style.analyze_style` service.")
def analyze_style(session_id: UUID, payload: dict | None = None, session: Session = Depends(get_session)):
    sp = style_service.analyze_style(session_id, payload, session)
    return {"id": str(sp.id), "profile": sp.topic_distribution}
