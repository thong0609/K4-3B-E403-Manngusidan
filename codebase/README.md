# ScriptScout Backend — Track C3

## Cách chạy

### 1. Cài đặt
```bash
cd codebase
pip install -r requirements.txt
```

### 2. Tạo file .env
```bash
cp .env.example .env
# Điền OPENAI_API_KEY và TAVILY_API_KEY vào .env
```

### 3. Khởi động server
```bash
uvicorn main:app --reload
```

Server chạy tại: http://localhost:8000
Swagger UI: http://localhost:8000/docs

### 4. Test nhanh (cần server đang chạy)
```bash
python test_api.py
```

---

## Luồng sử dụng API

```
POST /api/sessions
  → Tạo session mới (trả về session_id)

POST /api/sessions/{id}/search
  → Agent tìm tài liệu (chạy nền, trả về 202)
  → Gọi GET /api/sessions/{id} để kiểm tra status

GET /api/sessions/{id}/sources
  → Xem danh sách nguồn + điểm tin cậy

PATCH /api/sessions/{id}/sources/{code}
  Body: {"is_active": false}
  → Loại một nguồn khỏi danh sách dùng để viết

POST /api/sessions/{id}/sources
  Body: {"url": "https://..."}
  → Thêm nguồn tự chọn

POST /api/sessions/{id}/script
  → Sinh kịch bản từ các nguồn active

PATCH /api/sessions/{id}/script/rewrite
  Body: {"removed_source_codes": ["t02"]}
  → Chỉ viết lại câu phụ thuộc vào nguồn đó

GET /api/sessions/{id}/cite/5
  → Xem bằng chứng cho câu số 5

GET /api/sessions/{id}/export?format=json
GET /api/sessions/{id}/export?format=markdown
  → Xuất file kịch bản hoàn chỉnh
```

---

## Chi phí ước tính mỗi lần chạy (gpt-4o-mini)

| Bước | Token ước tính | Chi phí |
|---|---|---|
| Trust scoring (8 nguồn × 600 token) | ~5,000 tokens | ~$0.003 |
| Detect conflicts | ~3,000 tokens | ~$0.002 |
| Generate script (3 phút) | ~4,000 tokens | ~$0.003 |
| **Tổng** | ~12,000 tokens | **~$0.01** |

---

## Những gì hệ thống chưa làm được

- Trang web yêu cầu JavaScript để render (SPA) → scrape không lấy được nội dung
- Trang bắt đăng nhập → bỏ qua
- Tác giả không được trích xuất tự động từ tất cả trang
- Verify trích dẫn dùng word overlap đơn giản, có thể bỏ sót paraphrase
- Chưa có hệ thống theo dõi nguồn đã cũ/có bản mới
