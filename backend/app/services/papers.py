from uuid import UUID

from sqlmodel import Session as DBSession, select

from app.models.paper import Paper


def upsert_blueprint(session_id: UUID, payload: dict, db: DBSession) -> Paper:
    q = db.exec(select(Paper).where(Paper.session_id == session_id)).first()
    if q:
        q.blueprint_json = payload
        db.add(q)
        db.commit()
        db.refresh(q)
        return q

    p = Paper(session_id=session_id, blueprint_json=payload)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def get_paper(session_id: UUID, db: DBSession) -> Paper | None:
    return db.exec(select(Paper).where(Paper.session_id == session_id)).first()
