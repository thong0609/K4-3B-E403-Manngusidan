"""
models.py — SQLAlchemy ORM models
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class Session(Base):
    """One ScriptScout run = one session."""

    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    topic: Mapped[str] = mapped_column(String, nullable=False)
    learning_goal: Mapped[str] = mapped_column(Text, nullable=False)
    audience: Mapped[str] = mapped_column(String, nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, default="created")
    # Status values: created | searching | sources_ready | scripting | done | error
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    sources: Mapped[list["Source"]] = relationship(
        "Source", back_populates="session", cascade="all, delete-orphan"
    )
    scripts: Mapped[list["Script"]] = relationship(
        "Script", back_populates="session", cascade="all, delete-orphan"
    )


class Source(Base):
    """Hồ sơ tài liệu — một nguồn tìm được hoặc người dùng thêm vào."""

    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)

    # Mã nguồn ngắn, ví dụ "t01", "t02" — dùng trong trường nguon[] của kịch bản
    code: Mapped[str] = mapped_column(String, nullable=False)

    url: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=True)
    author: Mapped[str] = mapped_column(String, nullable=True)
    published_date: Mapped[str] = mapped_column(String, nullable=True)  # ISO date string
    domain: Mapped[str] = mapped_column(String, nullable=True)

    # Nội dung thô đã tải về — dùng để soát trích dẫn
    raw_content: Mapped[str] = mapped_column(Text, nullable=True)

    # Đoạn trích đại diện dùng làm bằng chứng
    excerpt: Mapped[str] = mapped_column(Text, nullable=True)

    # Kết quả chấm tin cậy
    trust_score: Mapped[float] = mapped_column(Float, nullable=True)
    trust_reason: Mapped[str] = mapped_column(Text, nullable=True)

    # Nếu mâu thuẫn với nguồn khác — mô tả xung đột
    conflict_note: Mapped[str] = mapped_column(Text, nullable=True)

    # True = dùng để sinh kịch bản, False = người duyệt đã loại
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Nguồn do người dùng thêm tay hay do agent tìm
    added_by: Mapped[str] = mapped_column(String, default="agent")  # "agent" | "user"

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="sources")


class Script(Base):
    """Kịch bản đã được sinh ra, lưu dạng JSON text."""

    __tablename__ = "scripts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id"), nullable=False)

    # JSON string theo mẫu BTC
    json_content: Mapped[str] = mapped_column(Text, nullable=False)

    # Snapshot danh sách source codes đã dùng khi sinh kịch bản này
    sources_used: Mapped[str] = mapped_column(Text, nullable=True)  # JSON array of codes

    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    session: Mapped["Session"] = relationship("Session", back_populates="scripts")
