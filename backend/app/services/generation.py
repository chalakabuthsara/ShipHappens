from uuid import UUID

from sqlmodel import Session as DBSession

from app.models.generation_request import GenerationRequest


def create_generation_request(session_id: UUID, payload: dict, db: DBSession) -> GenerationRequest:
    gr = GenerationRequest(session_id=session_id, **payload)
    db.add(gr)
    db.commit()
    db.refresh(gr)
    return gr
