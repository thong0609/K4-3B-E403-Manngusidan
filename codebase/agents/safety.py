"""
agents/safety.py — Lớp kiểm duyệt an toàn đầu vào toàn diện (Input Guardrails & Semantic Coherence)
Tuân thủ chuẩn Google AI Safety Guidelines, Luật An ninh mạng & Chuẩn Studio Giáo dục.
Hỗ trợ cả Tiếng Việt có dấu, KHÔNG DẤU và Tiếng Anh.
"""
import re
import unicodedata

# ==============================================================================
# 1. DANH SÁCH TỪ KHÓA NGUY HẠI NGHIÊM TRỌNG (HARD REJECT - 400 BAD REQUEST)
# So khớp trên chuỗi văn bản ĐÃ BỎ DẤU + Tiếng Anh
# ==============================================================================
_DANGEROUS_UNACCENTED_PATTERNS = [
    # 1. Bạo lực, Giết người, Hành hung, Đánh đập & Gây thương tích
    r"\b(giet\s+nguoi|sat\s+hai|am\s+sat|tra\s+tan)\b",
    r"\b(danh\s+nguoi|danh\s+nhau|danh\s+dap|hanh\s+hung|hanh\s+ha|nguoc\s+dai)\b",
    r"\b(dam\s+chem|chem\s+nguoi|dam\s+nguoi|gay\s+thuong\s+tich|thue\s+giang\s+ho)\b",
    r"\b(kill|murder|assassinate|manslaughter|assault|beat\s+up|physical\s+abuse|stab(bing)?)\b",

    # 2. Tự tử & Tự hại (Self-harm & Suicide)
    r"\b(tu\s+tu|tu\s+sat|cat\s+tay|nhay\s+lau|that\s+co)\b",
    r"\b(suicide|self[- ]harm|hang\s+oneself)\b",

    # 3. Tội phạm tình dục, Xâm hại, Ấu dâm, Mại dâm & Khiêu dâm
    r"\b(hiep\s+dam|cuong\s+hiep|cuong\s+buc|xam\s+hai\s+tinh\s+duc|quay\s+roi\s+tinh\s+duc|au\s+dam)\b",
    r"\b(mai\s+dam|ban\s+dam|mua\s+dam|khieu\s+dam|phim\s+sex|truy\s+lac|dong\s+phim\s+sex)\b",
    r"\b(rape|sexual\s+assault|sexual\s+harassment|pedophil(ia|e)|molest|prostitution|porn|nsfw|brothel)\b",

    # 4. Vũ khí, Bom mìn, Chất độc, Khủng bố & Bạo loạn
    r"\bche\s+tao\s+(bom|vu\s+khi|thuoc\s+no|chat\s+doc|sung)\b",
    r"\b(make\s+a?\s*bomb|build\s+weapon|poison|make\s+explosive)\b",
    r"\b(khung\s+bo|bao\s+loan|phan\s+dong|chong\s+pha\s+nha\s+nuoc|lat\s+do\s+chinh\s+quyen)\b",
    r"\b(terrorism|terrorist|insurrection|sedition)\b",

    # 5. Ma túy, Chất cấm, Tiền giả, Trộm cướp & Cờ bạc (Bắt cả ma túy đứng 1 mình & tiếng lóng)
    r"\b(ma\s+tuy|mai\s+thuy|ma\s+thuy|thuoc\s+phien|can\s+sa|thuoc\s+lac|heroin|meth|cocaine|bong\s+cuoi|narcotics)\b",
    r"\b(chat\s+cam|buon\s+nguoi|buon\s+lau|drug\s+trafficking|human\s+trafficking)\b",
    r"\b(co\s+bac|danh\s+bac|ca\s+do|lo\s+de|song\s+bac|gambling|casino)\b",
    r"\b(tien\s+gia|in\s+tien\s+gia|counterfeit\s+money)\b",
    r"\b(trom\s+cap|cuop\s+giat|moc\s+tui|robbery|theft|burglary)\b",

    # 6. Tấn công phá hoại mạng, Mã độc, Lừa đảo & Tống tiền
    r"\b(tan\s+cong\s+ddos|hack\s+tai\s+khoan|chiem\s+doat\s+tai\s+san|lua\s+dao)\b",
    r"\b(tong\s+tien|tong\s+tinh|blackmail|extortion)\b",
    r"\b(ddos\s+attack|phishing|ransomware|malware\s+creation|scam)\b",

    # 7. Thù ghét, Vu khống, Xúc phạm nhân phẩm & Mê tín dị đoan
    r"\b(vu\s+khong|boi\s+nho|xuc\s+pham\s+danh\s+du|lam\s+nhuc)\b",
    r"\b(me\s+tin\s+di\s+doan|bua\s+ngai|ta\s+dao|thay\s+boi|tru\s+ta)\b",
    r"\b(hate\s+speech|defamation|slander)\b",
]

# ==============================================================================
# 2. DANH SÁCH CHỦ ĐỀ NHẠY CẢM HỢP LỆ (CẦN RÀO ĐÓN THEO RULE 14)
# ==============================================================================
_SENSITIVE_UNACCENTED_PATTERNS = [
    r"\b(ban\s+quyen|copyright)\b",
    r"\b(du\s+lieu\s+ca\s+nhan|privacy|personal\s+data)\b",
    r"\b(luat|phap\s+ly|legal|law)\b",
    r"\b(chinh\s+tri|politics)\b",
    r"\b(chua\s+benh|ke\s+don|thuoc|medical|prescription)\b",
]


def _strip_accents(text: str) -> str:
    """Chuyển văn bản tiếng Việt có dấu thành không dấu chữ thường."""
    if not text:
        return ""
    text = text.replace("đ", "d").replace("Đ", "d")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return text.lower()


def check_content_safety(topic: str, learning_goal: str = "") -> dict:
    """
    Kiểm tra mức độ an toàn của chủ đề và mục tiêu bài học.
    Trả về:
      - is_safe: False nếu là chủ đề nguy hại (chặn ngay ở cổng vào 400)
      - is_sensitive: True nếu liên quan pháp luật/y tế (cho phép nhưng rào đón)
      - reason: Lý do từ chối rõ ràng và lịch sự
    """
    raw_text = f"{topic or ''} {learning_goal or ''}".strip()
    normalized_text = _strip_accents(raw_text)

    # 1. Kiểm tra vi phạm nguy hại (Hard Reject)
    for pattern in _DANGEROUS_UNACCENTED_PATTERNS:
        if re.search(pattern, normalized_text):
            return {
                "is_safe": False,
                "is_sensitive": False,
                "reason": "Chủ đề vi phạm tiêu chuẩn an toàn nội dung (nội dung nguy hại/bạo lực/chất cấm/ngoài phạm vi giáo dục). ScriptScout từ chối xử lý theo quy định an toàn.",
            }

    # 2. Kiểm tra chủ đề nhạy cảm (Cần disclaimer theo Rule 14)
    is_sensitive = any(
        re.search(pattern, normalized_text) for pattern in _SENSITIVE_UNACCENTED_PATTERNS
    )

    return {
        "is_safe": True,
        "is_sensitive": is_sensitive,
        "reason": None,
    }


def check_input_coherence(topic: str, learning_goal: str, audience: str, duration_minutes: int) -> dict:
    """
    Kiểm tra 4 tham số có liên quan logic với nhau không (GS15, GS16).
    Ngăn chặn spam/troll ("haha", "test") và phát hiện độ lệch ngữ nghĩa rõ rệt.
    """
    # 1. Kiểm tra đối tượng người học có hợp lệ không (chống spam/troll như "haha", "test", "abc")
    aud_clean = _strip_accents((audience or "").strip())
    if len(aud_clean) < 3 or re.match(r"^(ha|he|hi|ho|ka|ki|a|b|c|x|y|z|1|2|3|test|asdf|haha|hehe|hihi|abc|xyz)+$", aud_clean):
        return {
            "is_coherent": False,
            "reason": f"Đối tượng người học không hợp lệ ('{audience}'). Vui lòng nhập đối tượng cụ thể (Ví dụ: 'Sinh viên năm nhất', 'Người mới bắt đầu', 'Giảng viên')."
        }

    # 2. Kiểm tra chủ đề có bị spam không
    topic_clean = _strip_accents((topic or "").strip())
    if len(topic_clean) < 3 or re.match(r"^(ha|he|hi|ho|ka|ki|a|b|c|x|y|z|1|2|3|test|asdf)+$", topic_clean):
        return {
            "is_coherent": False,
            "reason": f"Chủ đề bài giảng không hợp lệ ('{topic}'). Vui lòng nhập chủ đề rõ ràng."
        }

    # 3. Kiểm tra thời lượng chuẩn Studio (3–5 phút, tối đa 10 phút)
    if duration_minutes > 10 or duration_minutes < 1:
        return {
            "is_coherent": False,
            "reason": f"Thời lượng {duration_minutes} phút không hợp lệ. Studio chỉ hỗ trợ video ngắn từ 1 đến 10 phút (chuẩn là 3–5 phút)."
        }

    # 4. Kiểm tra độ lệch tông rõ rệt giữa Chủ đề và Mục tiêu (Deterministic Fast Check)
    goal_clean = _strip_accents((learning_goal or "").strip())
    tech_keywords = ["ai", "hoc may", "hoc sau", "machine learning", "deep learning", "ngon ngu lon", "llm", "prompt", "token", "chatgpt"]
    has_tech_in_goal = any(re.search(r"\b" + k + r"\b", goal_clean) for k in tech_keywords)
    has_tech_in_topic = any(re.search(r"\b" + k + r"\b", topic_clean) for k in tech_keywords)

    # Nếu mục tiêu nói rõ là AI/học máy nhưng chủ đề hoàn toàn không liên quan đến công nghệ/AI
    if has_tech_in_goal and not has_tech_in_topic:
        common_words = set(topic_clean.split()) & set(goal_clean.split())
        stopwords = {"la", "gi", "va", "cua", "cac", "nhung", "cho", "trong", "qua", "duoc", "mot", "hai", "ba", "bon", "nam"}
        meaningful_common = common_words - stopwords
        if not meaningful_common:
            return {
                "is_coherent": False,
                "reason": f"Chủ đề ('{topic}') và Mục tiêu bài học ('{learning_goal}') hoàn toàn không cùng lĩnh vực. Vui lòng điều chỉnh để hệ thống tìm đúng tài liệu."
            }

    # 5. Thẩm định qua LLM cho các ca ngữ nghĩa phức tạp khác
    from config import settings
    from openai import OpenAI
    import json

    client = OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
    prompt = f"""Bạn là chuyên gia thẩm định chương trình đào tạo.
Hãy đánh giá xem Chủ đề và Mục tiêu bài học sau có liên quan hợp lý với nhau không:
- Chủ đề: "{topic}"
- Mục tiêu: "{learning_goal}"

Trả về JSON duy nhất:
{{
  "is_coherent": true/false,
  "reason": "Giải thích ngắn gọn nếu không liên quan (tiếng Việt)"
}}
Lưu ý: Chỉ đánh dấu false khi HAI THỨ HOÀN TOÀN KHÔNG LIÊN QUAN (Ví dụ: Chủ đề một đằng, mục tiêu một nẻo). Nếu có thể liên quan hoặc áp dụng được, hãy chọn true."""

    try:
        resp = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"}
        )
        res = json.loads(resp.choices[0].message.content)
        return {
            "is_coherent": res.get("is_coherent", True),
            "reason": res.get("reason")
        }
    except Exception:
        # Nếu mất mạng hoặc lỗi model -> cho qua vì các bước kiểm tra cứng ở trên đã chặn spam/lệch tông
        return {"is_coherent": True, "reason": None}
