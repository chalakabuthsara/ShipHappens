from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_session
from app.services import questions as questions_service

router = APIRouter(prefix="/sessions/{session_id}/questions", tags=["questions"])


@router.get("/", response_model=list, summary="List extracted questions for a session", description="Returns questions extracted from uploaded source files. Underlying service `questions.list_questions` queries the `Question` table.")
def list_questions(session_id: UUID, session: Session = Depends(get_session)):
    rows = questions_service.list_questions(session_id, session)
    return [{"id": str(r.id), "text": r.question_text, "number": r.question_number} for r in rows]


@router.post("/{question_number}/regenerate", response_model=dict, summary="Regenerate a single question", description="Placeholder endpoint that will call the generation service to regenerate a single question and splice it back into the paper JSON. Currently calls `questions.regenerate_question` which returns a placeholder response.")
def regenerate_question(session_id: UUID, question_number: str, payload: dict | None = None, session: Session = Depends(get_session)):
    result = questions_service.regenerate_question(session_id, question_number, payload, session)
    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result
