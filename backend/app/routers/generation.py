from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.services import generation as generation_service
from app.schemas import GenerationRequestCreate, GenerationRequestRead

router = APIRouter(prefix="/sessions/{session_id}/generation", tags=["generation"])


@router.post("/", response_model=GenerationRequestRead, summary="Create a generation request", description="Creates a GenerationRequest record and enqueues the paper generation job. Uses `generation.create_generation_request` service. The service is responsible for persisting the request and returning status metadata.")
def create_generation_request(session_id: UUID, payload: GenerationRequestCreate, session: Session = Depends(get_session)):
    gr = generation_service.create_generation_request(session_id, payload.model_dump(), session)
    return gr
