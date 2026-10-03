# Xử lý CBO: chuyển NS chiến dịch sang NS nhóm (không bỏ qua)

**Ngày:** 03/10/2026
**Đại chốt (09:22 03/10):** Thao tác thủ công thực tế của Đại:

## Thao tác thật của Đại (TH1 — nhóm chạm ngưỡng trong chiến dịch có ≥2 nhóm)

1. Vào **nhóm chạm ngưỡng** → tắt adset + đổi hậu tố theo quy định
2. Vào **quảng cáo bên trong nhóm đó** → tắt ad + đổi hậu tố theo quy định
3. Chuyển đổi NS từ chiến dịch sang nhóm: đặt `daily_budget=400.000` lên **nhóm ĐANG CHẠY**
   (Meta tự động chuyển từ NS chiến dịch sang NS nhóm). Nhóm đã tắt giữ ở mức tối thiểu của Meta (~26.123đ) hoặc 27.000đ.

## Thao tác thật của Đại (TH2 — cả 2 nhóm đều chạm ngưỡng)

1. Tắt HẾT nhóm trong chiến dịch + đổi hậu tố
2. Tắt HẾT ad trong chiến dịch + đổi hậu tố  
3. Hạ ngân sách CHIẾN DỊCH về 27.000đ

## Dữ liệu thật (đọc 03/10, ID 120250500099510509)

- Chiến dịch `2026 - 10 - 03 - dainq - Online - Scale MUA - LTT`, CBO
- Nhóm 1 PAUSED: `... Scale A1 0/140 X10`, daily=26.135 (mặc định Meta sau khi tách NS)
- Nhóm 2 ACTIVE: `... Scale A1`, daily=400.000 (được cấp riêng sau khi nhóm 1 tụt)
- Mỗi nhóm có đúng 1 ad. Sau khi tụt: nhóm 1 giữ ~27k, nhóm 2 được cấp 400k riêng.

## Thiết kế code

### Hàm mới: `_doc_nhom_trong_chien_dich(env, ma_chien_dich)`
- Đọc TẤT CẢ nhóm (khác với `agent_doc_meta.doc_nhom_dang_chay` chỉ lọc ACTIVE)
- Trả về danh sách {id, name, status, effective_status, daily_budget}
- Dùng `/account/adsets` với filtering `campaign_id` + `effective_status IN [ACTIVE, PAUSED]`

### Hàm mới: `_xu_ly_cbo_tang_ns_ve_nhom(env, ma_chien_dich, ma_nhom_cham_nguong, ngan_sach_moi=NGAN_SACH_CHIEN_DICH_MAC_DINH=400000)`
- Tìm các nhóm còn ACTIVE trong chiến dịch (trừ nhóm chạm ngưỡng)
- Nếu tìm thấy nhóm sống → đặt `daily_budget=400.000` lên nhóm sống → thành công
- Nếu không có nhóm sống → TH2: hạ NS chiến dịch về 27.000đ
- Trả về (success, message)

### Tích hợp vào `_doi_trang_thai_va_ngan_sach` / `tam_dung_va_ha_ngan_sach`:
1. Đọc nhóm trước khi thao tác → phát hiện CBO (`daily_budget` là `None`)
2. Tắt nhóm + đổi tên (như cũ)
3. Gọi `_xu_ly_cbo_tang_ns_ve_nhom(...)` để chuyển NS cho nhóm sống
4. Báo rõ kết quả trong tin Telegram

### Tích hợp vào `doan_nguyen_nhan`:
Nhận diện CBO lỗi 1885621 → giải thích "nhóm thuộc chiến dịch Advantage+, đặt daily_budget cấp nhóm bị từ chối. Cần chuyển NS chiến dịch sang NS nhóm."

## Kiểm chứng (dựng thử ngoài repo)

Tạo stub mô phỏng: nhóm CBO (daily_budget=None, campaign_id=C), 2 nhóm trong chiến dịch.
Kiểm thử: tắt nhóm 1 → chuyển NS cho nhóm 2. Và: tắt hết → hạ NS chiến dịch.

## Ghi chú

Bản `68e5f59` đã push sớm (Đại nhắc cứ ~3 lần sửa mới push). Từ giờ GIỮ Ở MÁY, không push thêm cho tới khi đủ ~3 lần sửa.
