# Kế hoạch triển khai Backend ScriptScout (Track C3) — FastAPI

## Mục tiêu

Xây dựng **backend API** hoàn chỉnh cho ScriptScout theo đúng yêu cầu đề bài C3:
- Agent tự tìm tài liệu web (dùng **Tavily Search API** thật)
- Chấm điểm tin cậy nguồn bằng AI
- Sinh kịch bản JSON đúng mẫu của BTC, mỗi câu có trường `nguon` trỏ về hồ sơ tài liệu
- API cho phép người duyệt bỏ/thêm nguồn và chỉ viết lại đúng câu phụ thuộc

---

## Yêu cầu API Keys (cần chuẩn bị trước)

| Dịch vụ | Dùng để | Free tier |
|---|---|---|
| **Tavily API** | Tìm kiếm web thật, trả về nội dung đã extract | 1,000 req/tháng |
| **OpenAI hoặc Gemini API** | Chấm tin cậy nguồn + sinh kịch bản | Tuỳ plan |

> [!IMPORTANT]
> Trước khi bắt đầu, lấy API key từ [tavily.com](https://tavily.com) (free) và key của model AI bạn muốn dùng. Ghi vào file `.env`.

---

## Cấu trúc Project

```
codebase/
├── main.py               ← FastAPI app, mount routes
├── .env                  ← API keys (không commit!)
├── requirements.txt
├── database.py           ← SQLite setup với SQLAlchemy
├── models.py             ← ORM models: Session, Source, Script
├── schemas.py            ← Pydantic schemas (request/response)
└── agents/
    ├── search_agent.py   ← Gọi Tavily, extract nội dung trang
    ├── trust_agent.py    ← LLM chấm điểm tin cậy từng nguồn
    ├── script_agent.py   ← LLM viết kịch bản JSON đúng mẫu BTC
    └── verify_agent.py   ← Soát trích dẫn: đoạn trích có thật trong trang không?
```

---

## Data Models

### `Session` (mỗi lần người dùng gửi yêu cầu)
```python
id, topic, learning_goal, audience, duration_minutes, status, created_at
```

### `Source` (hồ sơ tài liệu — 1 nguồn)
```python
id, session_id, code,        # e.g. "t01", "t02"
url, title, author, published_date,
trust_score,                  # 0.0–1.0
trust_reason,                 # LLM giải thích vì sao tin/không tin
excerpt,                      # đoạn trích dùng làm bằng chứng
is_active,                    # True = được dùng, False = người duyệt loại
conflict_note                 # nếu mâu thuẫn với nguồn khác
```

### `Script` (kết quả kịch bản)
```python
id, session_id, json_content, created_at, sources_snapshot
```

---

## API Endpoints

### Phase 1 — Tìm & Thẩm định nguồn

```
POST /api/sessions
Body: { topic, learning_goal, audience, duration_minutes }
→ Tạo session mới, trả về session_id
```

```
POST /api/sessions/{id}/search
→ Agent gọi Tavily tìm ~8 kết quả
→ Scrape nội dung từng trang
→ LLM chấm trust_score và trust_reason cho từng nguồn
→ Lưu vào DB, trả về danh sách sources
```

**Response mẫu `GET /api/sessions/{id}/sources`:**
```json
[
  {
    "code": "t01",
    "url": "https://example.com/ai-overview",
    "title": "AI Overview 2024",
    "author": "Jane Doe",
    "published_date": "2024-03-15",
    "trust_score": 0.85,
    "trust_reason": "Tác giả có chuyên môn, bài đăng gần đây, domain uy tín (.edu)",
    "excerpt": "Machine learning is a subset of AI...",
    "is_active": true,
    "conflict_note": null
  }
]
```

---

### Phase 2 — Người duyệt kiểm soát nguồn

```
PATCH /api/sessions/{id}/sources/{code}
Body: { "is_active": false }
→ Đánh dấu nguồn bị loại (không xoá khỏi DB)
```

```
POST /api/sessions/{id}/sources
Body: { url }
→ Scrape URL do người dùng tự thêm
→ Chấm trust_score, thêm vào danh sách
```

---

### Phase 3 — Sinh kịch bản

```
POST /api/sessions/{id}/script
→ Lấy các sources có is_active=True
→ LLM viết kịch bản JSON đúng mẫu BTC
→ Mỗi câu có trường "nguon": ["t01", "t02"] trỏ về code của nguồn
→ Verify Agent kiểm tra đoạn trích có thật trong trang đã lưu không
→ Lưu vào DB, trả về script JSON
```

**Response — JSON đúng mẫu BTC:**
```json
{
  "id": "session-abc123",
  "tieuDe": "Trí tuệ nhân tạo và học máy",
  "phan": [
    { "so": 1, "ten": "Mở đầu" }
  ],
  "cau": [
    {
      "n": 1,
      "phan": 1,
      "kieu": "ke",
      "loi": "Trí tuệ nhân tạo đang thay đổi cách chúng ta làm việc.",
      "chuTrenManHinh": "AI đang thay đổi công việc",
      "yDoHinh": "Icon robot và người làm việc cạnh nhau.",
      "nguon": []
    },
    {
      "n": 2,
      "phan": 1,
      "kieu": "giang",
      "loi": "Học máy là nhánh lớn nhất trong lĩnh vực này, chiếm hơn sáu mươi phần trăm ứng dụng thực tế.",
      "chuTrenManHinh": "Học máy > 60% ứng dụng AI",
      "yDoHinh": "Biểu đồ tròn, phần học máy được tô màu nổi bật.",
      "nguon": ["t01", "t03"]
    }
  ]
}
```

```
PATCH /api/sessions/{id}/script/rewrite
Body: { "removed_source_codes": ["t02"] }
→ Xác định câu nào có "nguon" chứa "t02"
→ Chỉ rewrite những câu đó, giữ nguyên phần còn lại
→ Trả về script đã cập nhật, đánh dấu câu nào được viết lại
```

---

### Phase 4 — Export & Eval

```
GET /api/sessions/{id}/export?format=json
→ Trả về script JSON hoàn chỉnh kèm hồ sơ tài liệu

GET /api/sessions/{id}/export?format=markdown
→ Chuyển JSON sang Markdown đúng mẫu BTC

GET /api/sessions/{id}/cite/{sentence_n}
→ Nhận số câu n, trả về đoạn tài liệu gốc chứng minh cho câu đó
→ Đây là API "bấm vào câu, xem nguồn" phục vụ demo
```

---

## Chi tiết từng Agent

### `search_agent.py`
1. Nhận `topic + learning_goal`
2. Tạo 3 query tìm kiếm (tiếng Việt + tiếng Anh)
3. Gọi `tavily.search()` với `search_depth="advanced"` để lấy content đã extract
4. Lọc bỏ: URL hỏng, trang login-gated, nội dung quá ngắn (< 200 chars)
5. Lưu `raw_content` vào DB để Verify Agent dùng sau

### `trust_agent.py`
1. Với mỗi nguồn, gửi cho LLM: URL, title, author, date, excerpt
2. LLM chấm theo bộ tiêu chí cứng (domain uy tín, tác giả rõ ràng, ngày đăng, độ dài, v.v.)
3. Phát hiện **mâu thuẫn**: nếu 2 nguồn cùng nói về 1 con số nhưng khác nhau → ghi vào `conflict_note`
4. Đánh dấu số liệu chưa có 2 nguồn xác nhận là `"unverified": true`

### `script_agent.py`
1. Nhận: input của user + danh sách sources (chỉ `is_active=True`) + mẫu kịch bản BTC
2. Prompt yêu cầu LLM viết kịch bản dạng **văn nói**, chia cảnh, đúng 5 kiểu đọc
3. Mỗi câu chứa thông tin/số liệu **phải** có trường `nguon` trỏ đúng code nguồn
4. Câu dẫn dắt hoặc chuyển ý thì `nguon: []`

### `verify_agent.py`
1. Với mỗi câu có `nguon`, lấy `raw_content` của nguồn đó từ DB
2. Kiểm tra xem đoạn trích (excerpt) có thật sự tồn tại trong nội dung trang đã tải về không (string matching / semantic similarity)
3. Nếu không tìm thấy → đánh dấu `"citation_verified": false` → cảnh báo trong response

---

## Tech Stack

| Thành phần | Thư viện |
|---|---|
| Web framework | `fastapi`, `uvicorn` |
| Database | `sqlalchemy` + SQLite (file `scriptscout.db`) |
| Search | `tavily-python` |
| LLM | `openai` hoặc `google-generativeai` |
| HTTP scraping | `httpx`, `beautifulsoup4` |
| Validation | `pydantic` (built-in FastAPI) |

---

## Thứ tự thực hiện (Execution Order)

- [ ] **Phase 0** — Setup: tạo `codebase/`, `requirements.txt`, `.env`, `database.py`, `models.py`, `schemas.py`
- [ ] **Phase 1** — Search & Trust: `search_agent.py` + `trust_agent.py` + endpoint `/search`
- [ ] **Phase 2** — Script & Verify: `script_agent.py` + `verify_agent.py` + endpoint `/script`
- [ ] **Phase 3** — Review flow: endpoint `PATCH sources`, `PATCH script/rewrite`
- [ ] **Phase 4** — Export & Cite: endpoint `/export`, `/cite/{n}`
- [ ] **Eval** — Chạy 20 chủ đề, đếm số câu có `citation_verified: true`

---

## Verification Plan

### Automated
```bash
# Khởi động server
uvicorn main:app --reload

# Test end-to-end với chủ đề đơn giản
curl -X POST http://localhost:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"topic":"Học máy là gì","learning_goal":"Phân biệt AI, ML, Deep Learning","audience":"Người mới","duration_minutes":5}'
```

### Manual (cho CP3 eval)
1. Chạy lần lượt **20 chủ đề** từ `data/studio-pack/c3-scriptscout/chu-de-goi-y.md`
2. Với mỗi kịch bản sinh ra, đếm:
   - **Số câu có `nguon` không rỗng**: bao nhiêu câu trỏ được về nguồn?
   - **Số câu có `citation_verified: true`**: bao nhiêu câu trích dẫn thật?
3. Báo cáo dạng: *"Thử 20 chủ đề, sinh tổng cộng X câu có thông tin, Y câu trích dẫn xác minh được (Z%), W câu không tìm thấy bằng chứng trong nội dung trang"*
