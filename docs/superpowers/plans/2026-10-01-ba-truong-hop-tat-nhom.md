# Kế hoạch: Ba trường hợp tắt nhóm + sửa phép so sánh

**Ngày:** 01/10/2026 · **Người chốt:** Đại · **Trạng thái:** LUẬT ĐÃ DỰNG THỬ XONG, CHỜ ÁP DỤNG

## Phần A — Sửa phép so sánh của báo cáo (Lỗi 1)

Báo cáo mốc 8h đang so **1 ngày** (hôm qua) với **7 ngày** (`ai.SO_NGAY_KY_TRUOC = 7`).
Vì mẫu số luôn gấp 7 lần tử số nên cột chênh lệch luôn ra khoảng −80%.

**Đại chốt:** so **ngày hôm qua với ngày hôm trước**. Sáng 01/10 nhận báo cáo 30/09 so với 29/09.

Sửa: `report.py` dòng ~1130 truyền `1` thay vì `ai.SO_NGAY_KY_TRUOC`.

## Phần B — Ba trường hợp tắt nhóm (Lỗi 2)

### Luật Đại chốt

Xét theo **thứ tự TH3 → TH2 → TH1**. Nhóm có lượt mua **luôn** rơi vào TH3.

| TH | Điều kiện | Ngưỡng | Tên mới khi tắt |
|---|---|---|---|
| **TH3** | Đã có lượt mua tháng (dù có tin nhắn hay không) | giá mỗi lượt mua **tháng** ≥ **390.000đ** | `<x>/450 X<tháng>` |
| **TH2** | Có tin nhắn (≥1), chưa ra lượt mua | chi tiêu **hôm nay** ≥ **290.000đ** | `0/350 X<tháng> TN` |
| **TH1** | Không có tin nhắn nào | chi tiêu **hôm nay** ≥ **70.000đ** | `0/<2× chi tiêu> X<tháng>` |

- "Tin nhắn" = **cả hai** chỉ số: *Người liên hệ nhắn tin mới* (`onsite_conversion.messaging_first_reply`)
  **hoặc** *Lượt bắt đầu cuộc trò chuyện* (`onsite_conversion.messaging_conversation_started_7d`).
- TH1 ghi **gấp đôi số tiền đang chi tiêu** — **động**, không phải luôn 140. Chạm ngưỡng ở
  70.000đ → `0/140`; phát hiện muộn ở 85.000đ → `0/170`.
- TH2/TH3 ghi **cột mốc chẵn cố định** 350 và 450.

### Khi tắt thì làm 4 việc

1. Tắt nhóm quảng cáo (adset) — **đã có**
2. **Tắt luôn quảng cáo (ad) bên trong** — ⚠️ **CHƯA CÓ, phải viết mới**
3. Hạ ngân sách về 27.000đ — **đã có**
4. **Đổi tên nhóm** — ⚠️ **CHƯA CÓ, phải viết mới**

### So với code đang chạy

| | Đang chạy | Luật mới |
|---|---|---|
| Không tin nhắn | 80.000đ | **70.000đ** |
| Có tin nhắn, 0 đơn | 70.000đ | **290.000đ** ⬅ đổi lớn |
| Có đơn | CPR tháng ≥ 400.000đ | CPR tháng ≥ **390.000đ** |
| Đếm tin nhắn | chỉ 1 chỉ số | **cả 2 chỉ số** |
| Tắt quảng cáo | không | **có** |
| Đổi tên | không | **có** |

## Đã dựng thử và kiểm chứng (ngoài repo, `.workbuddy-ai/dung-thu/`)

### 1. Đặt tên nhóm — dùng 5 tên THẬT trong tài khoản
Cắt hậu tố cũ đúng cả 5 trường hợp, kể cả `0/300 X8-26 TN` và `12/495 X2`.
**Tắt lần hai không chồng tên** — kiểm chứng riêng.

| Trường hợp | Kết quả |
|---|---|
| TH1, chi 70.000đ | `... Online 0/140 X10` |
| TH1, chi 85.000đ | `... Online 0/170 X10` |
| TH2 | `... Online 0/350 X10 TN` |
| TH3, 1 đơn | `... Online 1/450 X10` |
| TH3, 2 đơn | `... Online 2/450 X10` |

### 2. Ba trường hợp — 9 ca biên
Đúng ở cả 9: dưới ngưỡng không báo · đúng ngưỡng thì báo · TH2 tính **cả** "Người liên hệ nhắn
tin mới" · TH3 **không cần** tin nhắn · nhóm đang tốt (40.000đ/đơn) **không** bị báo ·
nhóm PAUSED không được xét.

### 3. Chạy trên 88 nhóm THẬT (14h35 ngày 01/10)

**Luật mới báo: 0 nhóm.** Đã đối chiếu để chắc không phải lỗi — nhóm gần ngưỡng nhất:

| Nhóm | Số hiện tại | Ngưỡng | Còn thiếu |
|---|---|---|---|
| `2026 - 09 - 07 - dainq - Scale - Online WEB+VIDEO` | 144.129đ hôm nay | TH2 · 290.000đ | 145.871đ |
| `2026 - 09 - 04 - dainq - Scale - Online A4` | 320.996đ/đơn | TH3 · 390.000đ | 69.004đ |
| `2026 - 09 - 05 - dainq - Scale - Online A4` | 201.071đ/đơn | TH3 · 390.000đ | 188.929đ |

⇒ **0 nhóm là đúng.** Đáng chú ý: nhóm `... WEB+VIDEO` lúc 13:58 **có** bị agent báo theo luật cũ
(134.384đ ≥ 70.000đ). Luật mới đòi 290.000đ nên **sẽ không báo nữa** — đúng ý Đại.

**Kết quả: 21/21 phép kiểm đạt.**

## Việc còn phải làm

1. Sửa `ai.py` / `report.py` — phép so sánh (Phần A).
2. Viết `agent_cong_cu_ghi.py`: tắt quảng cáo (ad) + đổi tên nhóm.
   ⚠️ **Phải thử thật xem chìa khoá Meta có đủ quyền tắt ad không** — chưa kiểm chứng được
   nếu không đụng vào tài khoản thật.
3. Nối vào `agent.py::_lam_theo_dong_y` — gọi 2 việc mới, và truyền `ten_moi`.
4. Sửa `agent_rao.py`: `MOC_CPR` 400.000 → 390.000 (đã sửa ở bản dựng thử).
5. Cập nhật `tests/test_agent.py` cho luật mới.
6. Cập nhật `TONG-HOP-CACH-CHAY-QUANG-CAO.md` và `CAU-HOI-CACH-CARE-QUANG-CAO.md`.

## Điều KHÔNG sửa được bằng code

80/88 nhóm đang chạy **không có** `x/y` trong tên. Nhưng luật mới dùng **ngưỡng cố định**, nên
báo cáo vẫn phán đúng cho mọi nhóm — không còn phụ thuộc vào tên nhóm nữa.
