"""
routes/sessions.py — Session management endpoints
"""
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models import Session
from schemas import SessionCreate, SessionResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(body: SessionCreate, db: DBSession = Depends(get_db)):
    """Tạo một session mới — bước đầu tiên của một lần chạy ScriptScout."""
    session = Session(
        topic=body.topic,
        learning_goal=body.learning_goal,
        audience=body.audience,
        duration_minutes=body.duration_minutes,
        status="created",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    logger.info("Created session %s — topic: %r", session.id, session.topic)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    session = db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
