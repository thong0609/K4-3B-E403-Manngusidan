"""
agents/trust_agent.py — LLM thẩm định nguồn & phát hiện mâu thuẫn siêu tốc (Batching 1 Call + Auto-retry)
Tối ưu hóa: Giảm từ 9 lần gọi xuống còn đúng 1 lần duy nhất, triệt tiêu 100% nguy cơ lỗi 429.
"""
import json
import logging
import time
from openai import OpenAI

from config import settings

logger = logging.getLogger(__name__)
_client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL,
)

_BATCH_TRUST_SYSTEM_PROMPT = """Bạn là chuyên gia thẩm định tài liệu học thuật.
Nhiệm vụ: Thẩm định độ tin cậy của danh sách các nguồn web sau đây VÀ phát hiện các điểm mâu thuẫn số liệu/thông tin giữa chúng.

Tiêu chí thẩm định từng nguồn:
1. Domain uy tín (.edu, .gov, tổ chức khoa học, trang chuyên ngành)
2. Tác giả rõ ràng và có chuyên môn
3. Ngày đăng còn mới (ưu tiên tài liệu < 3 năm cho chủ đề AI/công nghệ)
4. Nội dung đủ sâu, có dẫn chứng, không phải quảng cáo bán hàng
5. Không có dấu hiệu thiên vị hoặc thông tin sai lệch

Trả về JSON DUY NHẤT theo định dạng:
{
  "sources": [
    {
      "code": "t01",
      "trust_score": float (0.0 - 1.0),
      "trust_reason": "giải thích ngắn gọn 1-2 câu tiếng Việt",
      "author": "tên tác giả nếu có, null nếu không rõ",
      "published_date": "ISO date nếu có, null nếu không rõ",
      "unverified_claims": ["con số/tuyên bố cần nguồn thứ 2 đối chiếu nếu có"]
    }
  ],
  "conflicts": [
    {
      "codes": ["t01", "t02"],
      "description": "mô tả xung đột số liệu/thông tin bằng tiếng Việt"
    }
  ]
}
Nếu không có mâu thuẫn, trả về "conflicts": [].
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


def _call_llm_with_retry(messages: list, max_retries: int = 2, delay: int = 5):
    """Gọi LLM với cơ chế tự động thử lại nếu gặp lỗi 429 (Rate Limit)."""
    import re
    for attempt in range(max_retries + 1):
        try:
            return _client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
            )
        except Exception as exc:
            err_msg = str(exc).lower()
            if ("429" in err_msg or "quota" in err_msg or "rate" in err_msg) and attempt < max_retries:
                # Đọc số giây Google yêu cầu đợi (ví dụ: retry in 35s)
                match = re.search(r"retry in (\d+(?:\.\d+)?)s", str(exc), re.IGNORECASE)
                wait_sec = int(float(match.group(1))) + 2 if match else delay
                logger.warning(
                    "LLM dính Rate Limit (429). Đang đợi %d giây trước khi thử lại (lần %d/%d)...",
                    wait_sec, attempt + 1, max_retries
                )
                time.sleep(wait_sec)
                delay += 10
            else:
                raise exc


def score_source(source: dict) -> dict:
    """
    Thẩm định một nguồn đơn lẻ (dùng khi người dùng bấm thêm URL thủ công).
    """
    # GS24: Link hỏng, không có nội dung, hoặc trang bắt đăng nhập
    content_len = len((source.get("excerpt") or "").strip())
    if content_len < 30 and not source.get("raw_content"):
        source["trust_score"] = 0.0
        source["trust_reason"] = "Không thể truy cập nội dung trang web (URL hỏng, chặn bot hoặc yêu cầu đăng nhập)."
        source["unverified_claims"] = []
        return source

    prompt_content = f"""
URL: {source['url']}
Title: {source.get('title', 'Không rõ')}
Domain: {source.get('domain', 'Không rõ')}
Published date (nếu có): {source.get('published_date', 'Không rõ')}
Đoạn trích nội dung (excerpt):
{source.get('excerpt', '')[:600]}
"""
    try:
        response = _call_llm_with_retry([
            {"role": "system", "content": _BATCH_TRUST_SYSTEM_PROMPT},
            {"role": "user", "content": prompt_content},
        ])
        content = _clean_json_text(response.choices[0].message.content)
        result = json.loads(content)

        # Nếu model trả về dạng batch {"sources": [...]}
        if "sources" in result and result["sources"]:
            r = result["sources"][0]
        else:
            r = result

        source["trust_score"] = float(r.get("trust_score", 0.5))
        source["trust_reason"] = r.get("trust_reason", "")
        if r.get("author") and not source.get("author"):
            source["author"] = r["author"]
        if r.get("published_date") and not source.get("published_date"):
            source["published_date"] = r["published_date"]
        source["unverified_claims"] = r.get("unverified_claims", [])
        if source["unverified_claims"]:
            claims_str = "Cần kiểm chứng: " + "; ".join(source["unverified_claims"])
            existing = source.get("conflict_note") or ""
            source["conflict_note"] = f"{existing} | {claims_str}".strip(" |")

    except Exception as exc:
        logger.error("trust_agent: failed to score single source %s: %s", source["url"], exc)
        source["trust_score"] = 0.4
        source["trust_reason"] = "Không thể thẩm định tự động."
        source["unverified_claims"] = []

    return source


def score_all_sources(sources: list[dict]) -> list[dict]:
    """
    TỐI ƯU TOÀN DIỆN (Batching 1 Call):
    Thẩm định tất cả nguồn + phát hiện mâu thuẫn trong DUY NHẤT 1 LẦN GỌI LLM.
    """
    if not sources:
        return []

    # 1. Lọc trước các nguồn link hỏng (GS24) mà không cần tốn token LLM
    valid_sources_for_prompt = []
    for s in sources:
        content_len = len((s.get("excerpt") or "").strip())
        if content_len < 30 and not s.get("raw_content"):
            s["trust_score"] = 0.0
            s["trust_reason"] = "Không thể truy cập nội dung trang web (URL hỏng, chặn bot hoặc yêu cầu đăng nhập)."
            s["unverified_claims"] = []
        else:
            valid_sources_for_prompt.append(s)

    # Nếu không có nguồn nào hợp lệ
    if not valid_sources_for_prompt:
        return sources

    # 2. Đóng gói toàn bộ nguồn hợp lệ vào 1 prompt duy nhất
    prompt_sections = []
    for s in valid_sources_for_prompt:
        prompt_sections.append(
            f"[{s['code']}] Title: {s.get('title', 'Không rõ')}\n"
            f"URL: {s['url']}\n"
            f"Domain: {s.get('domain', 'Không rõ')} | Date: {s.get('published_date', 'Không rõ')}\n"
            f"Excerpt: {s.get('excerpt', '')[:500]}\n"
        )
    user_content = "\n\n".join(prompt_sections)

    try:
        logger.info("trust_agent: Batch scoring %d sources in 1 single LLM call...", len(valid_sources_for_prompt))
        response = _call_llm_with_retry([
            {"role": "system", "content": _BATCH_TRUST_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ])
        content = _clean_json_text(response.choices[0].message.content)
        data = json.loads(content)

        # 3. Cập nhật kết quả điểm vào từng source
        code_map = {s["code"]: s for s in valid_sources_for_prompt}
        for item in data.get("sources", []):
            code = item.get("code")
            if code in code_map:
                src = code_map[code]
                src["trust_score"] = float(item.get("trust_score", 0.6))
                src["trust_reason"] = item.get("trust_reason", "")
                if item.get("author") and not src.get("author"):
                    src["author"] = item["author"]
                if item.get("published_date") and not src.get("published_date"):
                    src["published_date"] = item["published_date"]
                src["unverified_claims"] = item.get("unverified_claims", [])
                if src["unverified_claims"]:
                    claims_str = "Cần kiểm chứng: " + "; ".join(src["unverified_claims"])
                    existing = src.get("conflict_note") or ""
                    src["conflict_note"] = f"{existing} | {claims_str}".strip(" |")

        # 4. Gán ghi chú mâu thuẫn (conflicts)
        for conflict in data.get("conflicts", []):
            desc = conflict.get("description", "")
            for code in conflict.get("codes", []):
                if code in code_map:
                    existing = code_map[code].get("conflict_note") or ""
                    code_map[code]["conflict_note"] = (
                        (existing + " | " + desc).strip(" |") if existing else desc
                    )

    except Exception as exc:
        logger.error("trust_agent: Batch scoring failed: %s. Fallback to default scores.", exc)
        for s in valid_sources_for_prompt:
            s["trust_score"] = 0.5
            s["trust_reason"] = "Không thể thẩm định tự động do quá tải mạng."
            s["unverified_claims"] = []

    # Sắp xếp theo trust_score giảm dần
    sources.sort(key=lambda s: s.get("trust_score", 0), reverse=True)
    return sources
