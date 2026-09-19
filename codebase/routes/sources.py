"""
routes/sources.py — Tìm nguồn, duyệt nguồn, thêm nguồn
"""
import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models import Session, Source
from schemas import SourceAdd, SourceResponse, SourceToggle
from agents.search_agent import search_sources, _scrape_content, _domain_of
from agents.trust_agent import score_all_sources, score_source
from agents.safety import check_content_safety

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sessions", tags=["Sources"])


def _get_session_or_404(session_id: str, db: DBSession) -> Session:
    session = db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def _run_search_pipeline(session_id: str):
    """Background task: tìm nguồn → chấm tin cậy → lưu DB."""
    from database import SessionLocal

    db = SessionLocal()
    try:
        def is_cancelled() -> bool:
            check_db = SessionLocal()
            try:
                s = check_db.get(Session, session_id)
                return s is not None and s.status == "cancelled"
            finally:
                check_db.close()

        session = db.get(Session, session_id)
        if not session or is_cancelled():
            logger.info("Search pipeline aborted before start: session %s cancelled.", session_id)
            return

        session.status = "searching"
        db.commit()

        # Bước 1: Tìm nguồn (có truyền is_cancelled để ngắt ngay)
        raw_sources = search_sources(session.topic, session.learning_goal, max_sources=8, is_cancelled=is_cancelled)

        if is_cancelled():
            logger.info("Search pipeline aborted after search: session %s cancelled.", session_id)
            return

        # Bước 2: Chấm tin cậy + phát hiện mâu thuẫn
        scored = score_all_sources(raw_sources)

        if is_cancelled():
            logger.info("Search pipeline aborted after scoring: session %s cancelled.", session_id)
            return

        if is_cancelled():
            logger.info("Search pipeline aborted before DB save: session %s cancelled.", session_id)
            return

        # Bước 3: Lưu vào DB
        for s in scored:
            source = Source(
                session_id=session_id,
                code=s["code"],
                url=s["url"],
                title=s.get("title"),
                author=s.get("author"),
                published_date=s.get("published_date"),
                domain=s.get("domain"),
                raw_content=s.get("raw_content"),
                excerpt=s.get("excerpt"),
                trust_score=s.get("trust_score"),
                trust_reason=s.get("trust_reason"),
                conflict_note=s.get("conflict_note"),
                is_active=True,
                added_by="agent",
            )
            db.add(source)

        if is_cancelled():
            db.rollback()
            logger.info("Search pipeline rolled back: session %s cancelled.", session_id)
            return

        session = db.get(Session, session_id)
        if session and session.status != "cancelled":
            session.status = "sources_ready"
            db.commit()
            logger.info("Search pipeline done for session %s: %d sources", session_id, len(scored))

    except Exception as exc:
        logger.error("Search pipeline failed for session %s: %s", session_id, exc)
        session = db.get(Session, session_id)
        if session and session.status != "cancelled":
            session.status = "error"
            db.commit()
    finally:
        db.close()


@router.post("/{session_id}/search", status_code=202)
def trigger_search(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db),
):
    """
    Kích hoạt agent đi tìm tài liệu. Trả về ngay (202 Accepted).
    Dùng GET /sources để lấy kết quả khi status = sources_ready.
    """
    session = _get_session_or_404(session_id, db)
    
    safety_result = check_content_safety(session.topic, session.learning_goal)
    if not safety_result["is_safe"]:
        raise HTTPException(status_code=400, detail=safety_result["reason"])

    if session.status not in ("created", "error"):
        raise HTTPException(
            status_code=409,
            detail=f"Search already triggered (status={session.status}). Use GET /sources.",
        )
    background_tasks.add_task(_run_search_pipeline, session_id)
    return {"message": "Search started in background", "session_id": session_id, "status": "searching"}


@router.get("/{session_id}/sources", response_model=list[SourceResponse])
def list_sources(session_id: str, db: DBSession = Depends(get_db)):
    """Lấy danh sách nguồn (kể cả những nguồn đã bị loại)."""
    _get_session_or_404(session_id, db)
    sources = (
        db.query(Source)
        .filter(Source.session_id == session_id)
        .order_by(Source.trust_score.desc())
        .all()
    )
    return sources


@router.patch("/{session_id}/sources/{code}", response_model=SourceResponse)
def toggle_source(
    session_id: str,
    code: str,
    body: SourceToggle,
    db: DBSession = Depends(get_db),
):
    """Bật/tắt một nguồn. is_active=false = người duyệt đã loại nguồn này."""
    _get_session_or_404(session_id, db)
    source = (
        db.query(Source)
        .filter(Source.session_id == session_id, Source.code == code)
        .first()
    )
    if not source:
        raise HTTPException(status_code=404, detail=f"Source {code} not found")
    source.is_active = body.is_active
    db.commit()
    db.refresh(source)
    return source


@router.post("/{session_id}/sources", response_model=SourceResponse, status_code=201)
def add_source(
    session_id: str,
    body: SourceAdd,
    db: DBSession = Depends(get_db),
):
    """Người dùng tự thêm nguồn bằng URL."""
    session = _get_session_or_404(session_id, db)

    # Kiểm tra URL chưa có trong DB
    existing = db.query(Source).filter(Source.session_id == session_id, Source.url == body.url).first()
    if existing:
        raise HTTPException(status_code=409, detail="URL already exists in this session")

    # Đếm source hiện tại để tạo code tiếp theo
    count = db.query(Source).filter(Source.session_id == session_id).count()
    new_code = f"t{count + 1:02d}"

    # Scrape + score
    raw_content = _scrape_content(body.url)
    raw_source = {
        "code": new_code,
        "url": body.url,
        "title": None,
        "author": None,
        "published_date": None,
        "domain": _domain_of(body.url),
        "excerpt": (raw_content or "")[:800] if raw_content else "",
        "raw_content": raw_content,
    }
    scored = score_source(raw_source)

    source = Source(
        session_id=session_id,
        code=new_code,
        url=body.url,
        title=scored.get("title"),
        author=scored.get("author"),
        published_date=scored.get("published_date"),
        domain=scored.get("domain"),
        raw_content=raw_content,
        excerpt=scored.get("excerpt"),
        trust_score=scored.get("trust_score"),
        trust_reason=scored.get("trust_reason"),
        is_active=True,
        added_by="user",
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source
