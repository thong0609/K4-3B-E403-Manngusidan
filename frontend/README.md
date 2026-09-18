# Hướng dẫn chạy frontend ScriptScout

Frontend được FastAPI phục vụ tại `/app/`. Chỉ cần chạy backend là sử dụng được cả giao diện và API, không cần `npm install` hoặc chạy server frontend riêng.

## 1. Chuẩn bị

- Mở thư mục gốc project trong VS Code và mở Terminal PowerShell.
- Cần Python 3.10 trở lên nếu phải tạo môi trường mới.
- Cần kết nối Internet để tải React, ReactDOM, Babel từ CDN và sử dụng dịch vụ AI/tìm kiếm.

Nếu project đã có `venv` và đã cài thư viện, chuyển sang bước 2. Nếu chưa có, chạy từ thư mục gốc project:

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r .\codebase\requirements.txt
```

Các lệnh dùng trực tiếp Python trong `venv`, không cần chạy `Activate.ps1`.

## 2. Cấu hình API key

Kiểm tra file `codebase/.env`. Nếu chưa có, chạy từ thư mục gốc project:

```powershell
if (-not (Test-Path .\codebase\.env)) {
    Copy-Item .\codebase\.env.example .\codebase\.env
}
```

Điền API key thật trong `codebase/.env`:

```dotenv
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./scriptscout.db
```

Nếu sử dụng nhà cung cấp API tương thích khác, cấu hình thêm `OPENAI_BASE_URL` và chọn `OPENAI_MODEL` phù hợp với nhà cung cấp. Không đưa API key vào mã frontend hoặc commit file `.env`.

## 3. Khởi chạy

Từ thư mục gốc project, chạy:

```powershell
cd .\codebase
..\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Nếu terminal đang ở thư mục `frontend`, dùng `cd ..\codebase` thay cho `cd .\codebase`.

Phải chạy server trong thư mục `codebase` để ứng dụng đọc đúng file `.env`. Khi terminal báo `Application startup complete`, mở:

- **Giao diện:** <http://127.0.0.1:8000/app/>
- **Kiểm tra server:** <http://127.0.0.1:8000/>
- **Tài liệu và thử API:** <http://127.0.0.1:8000/docs>

Giữ terminal mở trong lúc test. Nhấn **Ctrl+C** để dừng server. Sau khi sửa frontend, tải lại trang trình duyệt để thấy thay đổi.

Nên giữ cổng **8000** vì frontend hiện cấu hình API theo cổng này. Mở giao diện qua URL `/app/`, không mở trực tiếp file `index.html`.

## 4. Test luồng chính

### Bước 1: Thiết lập và tìm kiếm

Nhập dữ liệu thử:

| Trường | Giá trị ví dụ |
| --- | --- |
| Chủ đề bài giảng | Học máy là gì? |
| Mục tiêu người học | Phân biệt AI, Machine Learning và Deep Learning |
| Đối tượng | Người mới bắt đầu |
| Thời lượng | 3 phút |

Bấm **Bắt đầu Tìm kiếm & Thẩm định nguồn**. Chờ xử lý và kiểm tra giao diện chuyển sang danh sách tài liệu, có thông tin nguồn và đánh giá độ tin cậy.

### Bước 2: Duyệt nguồn và sinh kịch bản

1. Xem thông tin các nguồn và thử mở liên kết tài liệu.
2. Thử bật/tắt một nguồn để thay đổi danh sách dùng viết kịch bản.
3. Thử thêm URL một bài viết liên quan, kiểm tra nguồn mới xuất hiện hoặc thông báo lỗi rõ ràng nếu không lấy được nội dung.
4. Giữ ít nhất một nguồn được chọn, bấm **Xác nhận & Sinh kịch bản**.
5. Chờ kịch bản xuất hiện và kiểm tra nội dung phù hợp chủ đề, mục tiêu đã nhập.

### Bước 3: Kiểm tra kết quả và xuất file

1. Bấm từng câu có dẫn nguồn để xem tài liệu và bằng chứng liên quan.
2. Kiểm tra các nhận định trong kịch bản có được nguồn hỗ trợ hay không.
3. Thử xuất Markdown, xuất JSON và sao chép nội dung.
4. Mở file tải về, kiểm tra nội dung và tiếng Việt hiển thị đúng.
5. Thử quay lại chỉnh nguồn và tạo lại kịch bản.

Việc giao diện mở thành công chỉ xác nhận server phục vụ được frontend. Cần chạy hết các bước trên để kiểm tra kết nối dịch vụ, chất lượng kết quả và luồng xuất file. Tìm kiếm và sinh kịch bản dùng API thật, có thể tiêu thụ quota hoặc phát sinh chi phí theo tài khoản.

## 5. Xử lý lỗi thường gặp

| Hiện tượng | Cách kiểm tra |
| --- | --- |
| Không tìm thấy Python trong `venv` | Tạo môi trường và cài thư viện theo bước 1; kiểm tra vị trí hiện tại của terminal. |
| `No module named uvicorn` hoặc thiếu module khác | Từ thư mục gốc, chạy `.\venv\Scripts\python.exe -m pip install -r .\codebase\requirements.txt`. |
| Lỗi cấu hình thiếu API key khi khởi động | Kiểm tra `codebase/.env` và bảo đảm terminal đang ở `codebase` khi chạy Uvicorn. |
| Cổng 8000 đang được sử dụng | Thử mở URL giao diện; nếu là server project đã chạy thì dùng server đó. Nếu cần chạy lại, dừng tiến trình đang dùng cổng mà bạn quản lý trước. |
| Không mở được trang hoặc API không kết nối | Kiểm tra terminal server còn chạy và truy cập `http://127.0.0.1:8000/`. |
| Trang trắng | Nhấn F12, xem Console và Network; kiểm tra kết nối CDN tải React, ReactDOM và Babel. |
| Tìm kiếm hoặc sinh kịch bản thất bại | Xem lỗi trong terminal và tab Network; kiểm tra API key, quota, kết nối mạng, model và base URL nếu có. |
| Tìm kiếm quá thời gian chờ | Kiểm tra log backend và dịch vụ tìm kiếm/AI. Giao diện hiện giới hạn khoảng 5 phút chờ tìm kiếm. |
| Sửa frontend nhưng chưa thấy thay đổi | Thử tải lại bằng Ctrl+F5. |

Khi báo lỗi, ghi lại bước đang thực hiện, thông báo trên giao diện và log tương ứng trong terminal; che API key nếu log có chứa thông tin nhạy cảm.
