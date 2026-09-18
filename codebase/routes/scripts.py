"""
routes/scripts.py — Sinh kịch bản, rewrite một phần, export, tra cứu trích dẫn
"""
import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session as DBSession

from database import get_db
from models import Session, Source, Script
from schemas import ScriptResponse, RewriteRequest, CitationResponse
from agents.script_agent import generate_script
from agents.verify_agent import verify_citations

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sessions", tags=["Scripts"])


def _get_session_or_404(session_id: str, db: DBSession) -> Session:
    session = db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


def _active_sources(session_id: str, db: DBSession) -> list[Source]:
    return (
        db.query(Source)
        .filter(Source.session_id == session_id, Source.is_active == True)  # noqa: E712
        .order_by(Source.trust_score.desc())
        .all()
    )


def _latest_script(session_id: str, db: DBSession) -> Script | None:
    return (
        db.query(Script)
        .filter(Script.session_id == session_id)
        .order_by(Script.version.desc())
        .first()
    )


def _source_dicts(sources: list[Source]) -> list[dict]:
    return [
        {
            "code": s.code,
            "url": s.url,
            "title": s.title,
            "author": s.author,
            "published_date": s.published_date,
            "trust_score": s.trust_score,
            "trust_reason": s.trust_reason,
            "excerpt": s.excerpt,
            "raw_content": s.raw_content,
            "conflict_note": s.conflict_note,
        }
        for s in sources
    ]


def _script_to_response(script_obj: Script) -> dict:
    return {
        "id": script_obj.id,
        "session_id": script_obj.session_id,
        "version": script_obj.version,
        "json_content": json.loads(script_obj.json_content),
        "sources_used": json.loads(script_obj.sources_used or "[]"),
        "created_at": script_obj.created_at,
    }


@router.post("/{session_id}/script")
def create_script(session_id: str, db: DBSession = Depends(get_db)):
    """
    Sinh kịch bản mới dựa trên các nguồn đang active.
    Kịch bản được lưu vào DB và trả về kèm kết quả soát trích dẫn.
    """
    session = _get_session_or_404(session_id, db)
    active = _active_sources(session_id, db)

    if not active:
        raise HTTPException(
            status_code=422,
            detail="Không có nguồn nào đang active. Hãy chạy /search trước hoặc thêm nguồn.",
        )

    session.status = "scripting"
    db.commit()

    try:
        source_dicts = _source_dicts(active)
        script_json = generate_script(
            session_id=session_id,
            topic=session.topic,
            learning_goal=session.learning_goal,
            audience=session.audience,
            duration_minutes=session.duration_minutes,
            sources=source_dicts,
        )

        # Soát trích dẫn
        code_to_source = {s["code"]: s for s in source_dicts}
        script_json = verify_citations(script_json, code_to_source)

        # Tính version
        last = _latest_script(session_id, db)
        version = (last.version + 1) if last else 1

        script_obj = Script(
            session_id=session_id,
            json_content=json.dumps(script_json, ensure_ascii=False),
            sources_used=json.dumps([s["code"] for s in source_dicts]),
            version=version,
        )
        db.add(script_obj)
        session.status = "done"
        db.commit()
        db.refresh(script_obj)

        logger.info("Script v%d created for session %s", version, session_id)
        return _script_to_response(script_obj)

    except Exception as exc:
        session.status = "error"
        db.commit()
        raise HTTPException(status_code=500, detail=str(exc))


@router.patch("/{session_id}/script/rewrite")
def rewrite_script(
    session_id: str,
    body: RewriteRequest,
    db: DBSession = Depends(get_db),
):
    """
    Người duyệt loại một số nguồn → chỉ viết lại câu phụ thuộc vào nguồn đó.
    Các câu khác giữ nguyên.
    """
    session = _get_session_or_404(session_id, db)
    last = _latest_script(session_id, db)
    if not last:
        raise HTTPException(status_code=404, detail="Chưa có kịch bản. Hãy chạy POST /script trước.")

    existing_script = json.loads(last.json_content)

    # Xác định câu nào cần viết lại
    removed_codes = set(body.removed_source_codes)
    sentences_to_rewrite = [
        s["n"]
        for s in existing_script.get("cau", [])
        if set(s.get("nguon", [])) & removed_codes
    ]

    if not sentences_to_rewrite:
        return {
            "message": "Không có câu nào phụ thuộc vào nguồn đã loại. Kịch bản không thay đổi.",
            "rewritten_sentences": [],
        }

    # Tắt những nguồn bị loại trong DB
    for code in removed_codes:
        source = (
            db.query(Source)
            .filter(Source.session_id == session_id, Source.code == code)
            .first()
        )
        if source:
            source.is_active = False
    db.commit()

    active = _active_sources(session_id, db)
    source_dicts = _source_dicts(active)

    try:
        rewritten = generate_script(
            session_id=session_id,
            topic=session.topic,
            learning_goal=session.learning_goal,
            audience=session.audience,
            duration_minutes=session.duration_minutes,
            sources=source_dicts,
            sentences_to_rewrite=sentences_to_rewrite,
            existing_script=existing_script,
        )

        code_to_source = {s["code"]: s for s in source_dicts}
        rewritten = verify_citations(rewritten, code_to_source)

        script_obj = Script(
            session_id=session_id,
            json_content=json.dumps(rewritten, ensure_ascii=False),
            sources_used=json.dumps([s["code"] for s in source_dicts]),
            version=last.version + 1,
        )
        db.add(script_obj)
        db.commit()
        db.refresh(script_obj)

        return {
            "message": f"Đã viết lại {len(sentences_to_rewrite)} câu",
            "rewritten_sentences": sentences_to_rewrite,
            "script": _script_to_response(script_obj),
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{session_id}/cite/{sentence_n}", response_model=CitationResponse)
def get_citation(
    session_id: str,
    sentence_n: int,
    db: DBSession = Depends(get_db),
):
    """
    Bấm vào câu n → xem đoạn tài liệu gốc chứng minh cho câu đó.
    Đây là API phục vụ tính năng "bấm vào câu, thấy nguồn" khi demo.
    """
    _get_session_or_404(session_id, db)
    last = _latest_script(session_id, db)
    if not last:
        raise HTTPException(status_code=404, detail="Chưa có kịch bản.")

    script_json = json.loads(last.json_content)
    sentence = next((s for s in script_json.get("cau", []) if s["n"] == sentence_n), None)
    if not sentence:
        raise HTTPException(status_code=404, detail=f"Câu số {sentence_n} không tồn tại.")

    citations = sentence.get("citation_details", [])
    # Bổ sung excerpt thật từ DB nếu citation_details chưa có
    if not citations:
        for code in sentence.get("nguon", []):
            source = db.query(Source).filter(
                Source.session_id == session_id, Source.code == code
            ).first()
            if source:
                citations.append({
                    "code": code,
                    "url": source.url,
                    "title": source.title,
                    "excerpt": source.excerpt,
                    "verified": None,
                })

    return {
        "sentence_n": sentence_n,
        "loi": sentence.get("loi", ""),
        "citations": citations,
    }


@router.get("/{session_id}/export")
def export_script(
    session_id: str,
    format: str = Query("json", pattern="^(json|markdown)$"),
    db: DBSession = Depends(get_db),
):
    """
    Xuất kịch bản và hồ sơ tài liệu ra file.
    format=json → JSON đầy đủ kèm hồ sơ tài liệu
    format=markdown → Markdown đúng mẫu BTC
    """
    session = _get_session_or_404(session_id, db)
    last = _latest_script(session_id, db)
    if not last:
        raise HTTPException(status_code=404, detail="Chưa có kịch bản.")

    script_json = json.loads(last.json_content)
    all_sources = db.query(Source).filter(Source.session_id == session_id).all()

    if format == "json":
        export_data = {
            "script": script_json,
            "ho_so_tai_lieu": [
                {
                    "code": s.code,
                    "url": s.url,
                    "title": s.title,
                    "author": s.author,
                    "published_date": s.published_date,
                    "trust_score": s.trust_score,
                    "trust_reason": s.trust_reason,
                    "excerpt": s.excerpt,
                    "is_active": s.is_active,
                    "conflict_note": s.conflict_note,
                }
                for s in all_sources
            ],
            "verification_summary": script_json.get("_verification_summary", {}),
        }
        return export_data

    else:  # markdown
        md = _script_to_markdown(script_json, session)
        return PlainTextResponse(content=md, media_type="text/markdown")


def _script_to_markdown(script: dict, session) -> str:
    """Chuyển script JSON sang Markdown đúng mẫu BTC."""
    lines = [
        f"# {script.get('tieuDe', session.topic)}\n",
        f"- **Mục tiêu:** {session.learning_goal}",
        f"- **Thời lượng dự kiến:** khoảng {session.duration_minutes} phút.",
        f"- **Đối tượng:** {session.audience}",
        "",
    ]

    phan_map = {p["so"]: p["ten"] for p in script.get("phan", [])}
    current_phan = None

    for cau in script.get("cau", []):
        phan_so = cau.get("phan", 1)
        if phan_so != current_phan:
            current_phan = phan_so
            phan_name = phan_map.get(phan_so, f"Phần {phan_so}")
            lines.append(f"\n## {phan_so} · {phan_name}\n")

        n = cau.get("n")
        if cau.get("dungGiay"):
            lines.append(f"### Câu {n}")
            lines.append(f"- **Dừng:** {cau['dungGiay']} giây")
            lines.append(f"- **Trên màn hình:** {cau.get('chuTrenManHinh', '')}")
        else:
            lines.append(f"### Câu {n}")
            if cau.get("kieu"):
                lines.append(f"- **Kiểu:** {cau['kieu']}")
            lines.append(f"- **Lời:** {cau.get('loi', '')}")
            lines.append(f"- **Trên màn hình:** {cau.get('chuTrenManHinh', '')}")
            lines.append(f"- **Ý đồ hình:** {cau.get('yDoHinh', '')}")
            if cau.get("nguon"):
                lines.append(f"- **Nguồn:** {', '.join(cau['nguon'])}")
        lines.append("")

    return "\n".join(lines)
