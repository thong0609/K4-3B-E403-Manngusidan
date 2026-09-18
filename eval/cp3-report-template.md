# CP3 · Báo cáo đo ScriptScout

## 1. Tóm tắt

- Ngày/giờ chạy: 2026-09-18
- Phiên bản prototype/commit: Nhánh `eval-cp3`
- Người chạy: Đội thi & AI
- Bộ test: 24 ca trong `golden-set-c3.md`
- Kết quả: 19 / 24 ca đạt (79.2%)
- Điểm từng chiều: T 24/24 · N 19/24 · K 24/24 · H 24/24

## 2. Đối chiếu quality bar

Quality bar được chốt trước khi chạy: một ca chỉ đạt khi cả T, N, K, H đều bằng 1.

| Nhóm ca | Số ca | Đạt | Tỷ lệ | Lỗi nổi bật |
|---|---:|---:|---:|---|
| Thường | 12 | 9 | 75.0% | UNVERIFIED |
| Lớp 1 · nguồn sự thật | 2 | 2 | 100% | Không |
| Lớp 2 · thiếu thông tin | 2 | 2 | 100% | Không |
| Lớp 3 · ngoài phạm vi | 2 | 1 | 50.0% | UNVERIFIED |
| Lớp 4 · đặc thù domain | 2 | 2 | 100% | Không |
| Hiếm | 4 | 3 | 75.0% | UNVERIFIED (Nguồn cũ) |
| **Tổng** | **24** | **19** | **79.2%** | UNVERIFIED (5 ca) |

## 3. Phân tích ca sai

| Case | Chiều sai | Mã lỗi | Bằng chứng quan sát được | Nguyên nhân giả thuyết | Việc sửa tiếp theo |
|---|---|---|---|---|---|
| 5 ca sai | N_source | UNVERIFIED | AI xuất kịch bản chứa các khẳng định và số liệu từ một nguồn duy nhất (hoặc nguồn cũ) mà không hề cảnh báo "chưa kiểm chứng". | Prototype hiện tại chỉ chấm điểm (trust_score) dựa trên sự trùng khớp từ vựng (word overlap), nhưng chưa có cơ chế đối chiếu chéo (Cross-source) giữa các nguồn với nhau. | Cần bổ sung "Active Verification": Khi agent gặp một số liệu quan trọng, nó phải gọi lệnh search tìm 1 nguồn thứ hai độc lập. Nếu không có, buộc phải đánh dấu là chưa kiểm chứng. |

## 4. Kết luận trung thực

Hệ thống Prototype v1 đã đạt xuất sắc ngưỡng an toàn (H_control 100%), chuẩn form kịch bản (K_script 100%) và truy xuất trích dẫn (T_source 100%).
Tuy nhiên, prototype **CHƯA ĐẠT** hoàn toàn tiêu chuẩn về tính đáng tin cậy của nguồn (N_source 19/24) do dính lỗi `UNVERIFIED` (bị 5 lỗi). Hướng đi tiếp theo là bắt buộc phải xây dựng tính năng Đối chiếu chéo 2 nguồn độc lập để giải quyết triệt để lỗi này.