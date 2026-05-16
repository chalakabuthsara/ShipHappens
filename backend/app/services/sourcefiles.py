from pathlib import Path
from uuid import UUID

from sqlmodel import Session as DBSession

from app.models.source_file import SourceFile

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_source_file(session_id: UUID, filename: str, content: bytes, db: DBSession) -> SourceFile:
    dest = UPLOAD_DIR / f"{session_id}_{filename}"
    with dest.open("wb") as f:
        f.write(content)

    sf = SourceFile(session_id=session_id, filename=filename, storage_path=str(dest))
    db.add(sf)
    db.commit()
    db.refresh(sf)
    return sf
