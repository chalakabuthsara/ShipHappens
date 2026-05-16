from uuid import UUID

from sqlmodel import Session as DBSession, select

from app.models.style_profile import StyleProfile


def get_style_profile(session_id: UUID, db: DBSession) -> StyleProfile | None:
    return db.exec(select(StyleProfile).where(StyleProfile.session_id == session_id)).first()


def analyze_style(session_id: UUID, payload: dict | None, db: DBSession) -> StyleProfile:
    sp = db.exec(select(StyleProfile).where(StyleProfile.session_id == session_id)).first()
    data = payload or {"note": "analysis placeholder"}
    if sp:
        sp.topic_distribution = data
        db.add(sp)
        db.commit()
        db.refresh(sp)
        return sp

    sp = StyleProfile(session_id=session_id, topic_distribution=data)
    db.add(sp)
    db.commit()
    db.refresh(sp)
    return sp
