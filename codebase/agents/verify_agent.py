"""
agents/verify_agent.py — Soát trích dẫn: đoạn trích phải thật trong nội dung trang đã tải về
"""
import logging
import re

logger = logging.getLogger(__name__)

_MIN_OVERLAP_RATIO = 0.6  # 60% từ trong excerpt phải xuất hiện trong raw_content


def _normalize(text: str) -> str:
    """Chuẩn hoá text để so sánh: bỏ dấu câu thừa, lowercase."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def _word_overlap_ratio(query: str, document: str) -> float:
    """Tính tỉ lệ từ trong query xuất hiện trong document."""
    q_words = set(_normalize(query).split())
    d_words = set(_normalize(document).split())
    if not q_words:
        return 0.0
    overlap = q_words & d_words
    return len(overlap) / len(q_words)


def verify_citations(script: dict, code_to_source: dict) -> dict:
    """
    Soát trích dẫn cho toàn bộ kịch bản.

    Với mỗi câu có trường "nguon":
    - Lấy raw_content của nguồn đó
    - Kiểm tra lời câu đó có "chứng minh được" bởi nội dung trang không
    - Thêm trường "citation_verified": bool và "citation_details" vào câu

    Trả về script đã bổ sung thông tin xác minh.
    """
    verified_count = 0
    total_with_source = 0

    for sentence in script.get("cau", []):
        nguon_list: list[str] = sentence.get("nguon", [])
        if not nguon_list:
            continue

        total_with_source += 1
        loi = sentence.get("loi", "")
        details = []
        all_verified = True

        for code in nguon_list:
            source = code_to_source.get(code)
            if not source:
                details.append({"code": code, "verified": False, "reason": "Nguồn không tồn tại"})
                all_verified = False
                continue

            raw = source.get("raw_content") or ""
            if not raw:
                details.append({"code": code, "verified": False, "reason": "Không tải được nội dung trang"})
                all_verified = False
                continue

            ratio = _word_overlap_ratio(loi, raw)
            verified = ratio >= _MIN_OVERLAP_RATIO

            if not verified:
                all_verified = False

            details.append(
                {
                    "code": code,
                    "url": source.get("url", ""),
                    "title": source.get("title", ""),
                    "excerpt": source.get("excerpt", ""),
                    "verified": verified,
                    "overlap_ratio": round(ratio, 2),
                    "reason": (
                        f"Tìm thấy {ratio:.0%} từ trong nội dung trang"
                        if verified
                        else f"Chỉ tìm thấy {ratio:.0%} từ — có thể AI tự thêm thông tin"
                    ),
                }
            )

        sentence["citation_verified"] = all_verified
        sentence["citation_details"] = details
        if all_verified:
            verified_count += 1

    # Ghi tổng hợp vào metadata
    script["_verification_summary"] = {
        "total_sentences_with_source": total_with_source,
        "verified_count": verified_count,
        "unverified_count": total_with_source - verified_count,
        "accuracy_rate": (
            round(verified_count / total_with_source, 2) if total_with_source > 0 else 0.0
        ),
    }

    logger.info(
        "verify_agent: %d/%d sentences verified (%.0f%%)",
        verified_count,
        total_with_source,
        (verified_count / total_with_source * 100) if total_with_source else 0,
    )
    return script
