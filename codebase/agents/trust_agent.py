"""
agents/trust_agent.py — LLM chấm điểm tin cậy từng nguồn và phát hiện mâu thuẫn
"""
import json
import logging
from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)
_client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)

_TRUST_SYSTEM_PROMPT = """Bạn là chuyên gia thẩm định tài liệu học thuật.
Nhiệm vụ: đánh giá mức độ tin cậy của một nguồn tài liệu web dựa trên các tiêu chí sau:
1. Domain uy tín (edu, gov, tổ chức khoa học, trang chuyên ngành)
2. Tác giả rõ ràng và có chuyên môn
3. Ngày đăng còn mới (ưu tiên tài liệu < 3 năm cho chủ đề AI/công nghệ)
4. Nội dung đủ sâu, có dẫn chứng, không phải quảng cáo
5. Không có dấu hiệu thiên vị hoặc thông tin sai lệch

Trả về JSON với cấu trúc:
{
  "trust_score": float (0.0 - 1.0),
  "trust_reason": "giải thích ngắn gọn bằng tiếng Việt, tối đa 2 câu",
  "author": "tên tác giả nếu đoán được từ URL/nội dung, null nếu không rõ",
  "published_date": "ISO date nếu tìm được, null nếu không rõ",
  "unverified_claims": ["các con số/tuyên bố quan trọng cần nguồn thứ 2 xác nhận"]
}
"""


def _clean_json_text(text: str) -> str:
    text = (text or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def score_source(source: dict) -> dict:
    """
    Chấm tin cậy một nguồn. Trả về source dict đã bổ sung trust_score, trust_reason, v.v.
    """
    prompt_content = f"""
URL: {source['url']}
Title: {source.get('title', 'Không rõ')}
Domain: {source.get('domain', 'Không rõ')}
Published date (nếu có): {source.get('published_date', 'Không rõ')}
Đoạn trích nội dung (excerpt):
{source.get('excerpt', '')[:600]}
"""

    try:
        response = _client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": _TRUST_SYSTEM_PROMPT},
                {"role": "user", "content": prompt_content},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        content = _clean_json_text(response.choices[0].message.content)
        result = json.loads(content)

        source["trust_score"] = float(result.get("trust_score", 0.5))
        source["trust_reason"] = result.get("trust_reason", "")
        # Update author/date if LLM found them
        if result.get("author") and not source.get("author"):
            source["author"] = result["author"]
        if result.get("published_date") and not source.get("published_date"):
            source["published_date"] = result["published_date"]
        source["unverified_claims"] = result.get("unverified_claims", [])

    except Exception as exc:
        logger.error("trust_agent: failed to score %s: %s", source["url"], exc)
        source["trust_score"] = 0.4
        source["trust_reason"] = "Không thể thẩm định tự động."
        source["unverified_claims"] = []

    return source


def detect_conflicts(sources: list[dict]) -> list[dict]:
    """
    Phát hiện mâu thuẫn giữa các nguồn về cùng một số liệu/tuyên bố.
    Cập nhật conflict_note cho những nguồn có xung đột.
    """
    if len(sources) < 2:
        return sources

    excerpts_for_prompt = "\n\n".join(
        f"[{s['code']}] {s.get('title','')}\n{s.get('excerpt','')[:400]}"
        for s in sources
    )

    prompt = f"""Phân tích các đoạn trích sau từ nhiều nguồn khác nhau về cùng một chủ đề.
Xác định những điểm mâu thuẫn (số liệu khác nhau, tuyên bố trái ngược).

{excerpts_for_prompt}

Trả về JSON:
{{
  "conflicts": [
    {{
      "codes": ["t01", "t02"],
      "description": "mô tả xung đột bằng tiếng Việt"
    }}
  ]
}}
Nếu không có mâu thuẫn: {{"conflicts": []}}
"""

    try:
        response = _client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        content = _clean_json_text(response.choices[0].message.content)
        result = json.loads(content)

        # Gán conflict_note vào từng source liên quan
        code_to_source = {s["code"]: s for s in sources}
        for conflict in result.get("conflicts", []):
            desc = conflict.get("description", "")
            for code in conflict.get("codes", []):
                if code in code_to_source:
                    existing = code_to_source[code].get("conflict_note") or ""
                    code_to_source[code]["conflict_note"] = (
                        (existing + " | " + desc).strip(" |") if existing else desc
                    )

    except Exception as exc:
        logger.warning("detect_conflicts failed: %s", exc)

    return sources


def score_all_sources(sources: list[dict]) -> list[dict]:
    """Score tất cả sources và phát hiện mâu thuẫn."""
    scored = [score_source(s) for s in sources]
    scored = detect_conflicts(scored)
    # Sắp xếp theo trust_score giảm dần
    scored.sort(key=lambda s: s.get("trust_score", 0), reverse=True)
    return scored
