"""
schemas.py — Pydantic schemas for request/response validation
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


# ─── Session ──────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    topic: str = Field(..., min_length=2, description="Chủ đề của video bài giảng")
    learning_goal: str = Field(..., min_length=5, description="Mục tiêu bài học")
    audience: str = Field(..., min_length=2, description="Người học là ai")
    duration_minutes: int = Field(..., ge=1, le=10, description="Thời lượng video (1–10 phút, chuẩn Studio là 3–5 phút)")

class SessionResponse(BaseModel):
    id: str
    topic: str
    learning_goal: str
    audience: str
    duration_minutes: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

# ─── Source ───────────────────────────────────────────────────────────────────

class SourceResponse(BaseModel):
    code: str
    url: str
    title: Optional[str]
    author: Optional[str]
    published_date: Optional[str]
    domain: Optional[str]
    excerpt: Optional[str]
    trust_score: Optional[float]
    trust_reason: Optional[str]
    conflict_note: Optional[str]
    is_active: bool
    added_by: str

    model_config = {"from_attributes": True}


class SourceToggle(BaseModel):
    is_active: bool


class SourceAdd(BaseModel):
    url: str = Field(..., description="URL do người dùng thêm vào")


# ─── Script ───────────────────────────────────────────────────────────────────

class ScriptResponse(BaseModel):
    id: int
    session_id: str
    version: int
    json_content: dict  # Parsed JSON of the script
    sources_used: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class RewriteRequest(BaseModel):
    removed_source_codes: list[str] = Field(
        ..., description="Danh sách mã nguồn bị loại — chỉ câu phụ thuộc vào nguồn này sẽ được viết lại"
    )


# ─── Citation ─────────────────────────────────────────────────────────────────

class CitationResponse(BaseModel):
    sentence_n: int
    loi: str  # Lời đọc của câu đó
    citations: list[dict]  # [{code, url, title, excerpt, verified}]


# ─── Export ───────────────────────────────────────────────────────────────────

class ExportResponse(BaseModel):
    session_id: str
    format: str
    content: str  # JSON string or Markdown string
