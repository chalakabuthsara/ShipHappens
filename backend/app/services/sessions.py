from typing import List
from uuid import UUID

from sqlmodel import Session as DBSession, select

from app.models.session import Session as SessionModel


def create_session(payload: dict, db: DBSession) -> SessionModel:
    s = SessionModel(**payload)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def list_sessions(db: DBSession) -> List[SessionModel]:
    return db.exec(select(SessionModel)).all()


def get_session_by_id(session_id: UUID, db: DBSession) -> SessionModel | None:
    return db.get(SessionModel, session_id)
