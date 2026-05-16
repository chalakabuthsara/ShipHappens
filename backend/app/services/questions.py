from uuid import UUID
from typing import List

from sqlmodel import Session as DBSession, select

from app.models.question import Question


def list_questions(session_id: UUID, db: DBSession) -> List[Question]:
    return db.exec(select(Question).where(Question.session_id == session_id)).all()


def regenerate_question(session_id: UUID, question_number: str, payload: dict | None, db: DBSession) -> dict:
    # Placeholder: actual regeneration will call AI service and splice paper JSON
    q = db.exec(select(Question).where(Question.session_id == session_id, Question.question_number == question_number)).first()
    if not q:
        return {}
    return {"id": str(q.id), "question_number": q.question_number, "status": "regenerated", "payload": payload or {}}
