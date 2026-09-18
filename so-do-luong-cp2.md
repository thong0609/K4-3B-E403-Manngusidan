# Sơ đồ luồng hoạt động (CP2) - ScriptScout (Track C3)

Dưới đây là sơ đồ luồng các bước thao tác từ đầu đến cuối của tính năng ScriptScout. Nhóm có thể nộp file này (chứa sơ đồ Mermaid tự động vẽ trên GitHub) cho yêu cầu của Checkpoint 2.

```mermaid
flowchart TD
    %% Định nghĩa Style
    classDef user fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef ai fill:#6366f1,stroke:#4338ca,stroke-width:2px,color:#fff;
    classDef ui fill:#334155,stroke:#1e293b,stroke-width:2px,color:#fff;
    classDef decision fill:#f59e0b,stroke:#b45309,stroke-width:2px,color:#fff;

    A([Người viết kịch bản]):::user -->|Nhập Chủ đề & Thời lượng| B(Màn hình Nhập liệu):::ui
    
    B --> C{Agent AI Xử lý ngầm}:::ai
    C -->|Tìm kiếm & Thu thập| D[(Trích xuất tài liệu web)]:::ai
    C -->|Chấm điểm tin cậy| E[Lập Hồ sơ nguồn]:::ai
    D --> E
    
    E --> F(Màn hình Duyệt Nguồn):::ui
    F --> G{Người duyệt quyết định}:::decision
    
    G -->|Giữ nguyên nguồn| H[AI Viết Kịch Bản]:::ai
    G -->|Bỏ/Thêm nguồn| I[Cập nhật tập nguồn]:::user
    I --> H
    
    H --> J(Màn hình Kịch bản hoàn thiện):::ui
    J -->|Click vào số liệu/ví dụ| K[Hiện trích đoạn nguồn gốc]:::ui
    J -->|Xác nhận toàn bộ| L([Xuất file Markdown/JSON]):::user
```

### Chú thích luồng thao tác:
1. **Bắt đầu:** Người viết kịch bản vào màn hình nhập liệu, nhập các thông số (Chủ đề, Thời lượng, Đối tượng).
2. **AI xử lý:** Agent tự động lên mạng tìm kiếm, đọc hiểu tài liệu, lập danh sách nguồn và tự chấm điểm độ tin cậy.
3. **Duyệt nguồn:** Màn hình hiển thị danh sách các nguồn. Người dùng đọc và quyết định loại bỏ những nguồn không uy tín.
4. **Sinh kịch bản:** AI chỉ dựa trên các nguồn đã duyệt để viết ra kịch bản. Nếu có nguồn bị loại, AI chỉ viết lại đúng câu liên quan.
5. **Kết thúc:** Người dùng xem kịch bản. Các thông tin quan trọng đều bấm vào được để đối chiếu với tài liệu gốc. Sau đó bấm nút xuất file.
