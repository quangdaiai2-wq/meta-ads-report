# Đổi mẫu tin nhắn Telegram + làm lại giao diện file HTML

**Ngày:** 29/09/2026
**Người yêu cầu:** Đại
**Trạng thái:** Đã thi công xong, đã kiểm chứng

---

## 1. Đại yêu cầu gì

> *"tôi muốn đổi mẫu báo cáo thông qua telegram như bình thường vẫn gửi. Không cần nhiều tin nhắn nữa.
> Chỉ cần gửi theo mẫu ví dụ sau:*
> ```
> 🔴 BÁO CÁO META ADS — 29/09/2026 (00:00 - 12:00)
> Tài khoản: 
> 🔵 TÓM TẮT
> Có 16 campaign đủ điều kiện.
> - Số tiền đã chi tiêu: 8.198.223 VND
> - Lượt bắt đầu cuộc trò chuyện qua tin nhắn: 59
> - Người liên hệ nhắn tin mới: 55
> - Đơn đặt hàng đã tạo: 19
> - Lượt mua: 19
> - Lượt thanh toán: 21
> - Bình luận về bài viết: 1
> ```
> *Sau đó đến file html. Trong file html hãy thay đổi giao diện kiểu khác và có phần nhận định như
> đã thống nhất"*

Ba việc, đọc theo đúng thứ tự Đại viết:

1. **Tin nhắn Telegram rút gọn** còn đúng 11 dòng như ví dụ.
2. **File HTML giao diện khác** — khác hẳn bản đang dùng.
3. **Phần NHẬN ĐỊNH chuyển vào file HTML** (trước đây nằm trong tin nhắn).

---

## 2. Quyết định đã chốt (và lý do)

### 2.1. Ba thứ chuyển từ tin nhắn sang file HTML

| Chuyển đi đâu | Nội dung | Lý do |
|---|---|---|
| ➡️ Vào file HTML | Mục **BỘ LỌC** | Không đổi giữa các ngày, chỉ cần xem khi nghi ngờ |
| ➡️ Vào file HTML | Phần **NHẬN ĐỊNH** của AI | Đại yêu cầu trực tiếp |
| ➡️ Vào file HTML | Hai **bảng xếp hạng camp** | Dài nhất, và Đại đọc trên điện thoại |

**Hai thứ CỐ Ý GIỮ LẠI trong tin nhắn Telegram** — Đại không nhắc tới, nhưng bỏ đi là bỏ tính an toàn:

- 🟡 **Cảnh báo token Meta sắp hết hạn** — Đại phải thấy để đi lấy token mới. Nếu chỉ nằm trong file
  HTML thì phải mở file mới biết.
- ⚠️ **Cảnh báo số liệu trông bất thường** — cùng lý do: đây là lời cảnh báo, không phải dữ liệu.

Cả hai đều **thỉnh thoảng mới xuất hiện**, không làm tin nhắn dài thêm trong ngày bình thường.

### 2.2. Giao diện mới: nền tối + nút đổi sang nền sáng

Yêu cầu "giao diện kiểu khác" là mở. Chọn **nền tối làm mặc định** vì:
- Đó là kiểu **khác hẳn** bản cũ (bản cũ nền sáng xám).
- Đại mở file này trên điện thoại, thường buổi tối — nền tối dễ chịu hơn.

**Nhưng kèm một nút đổi sang nền sáng** ở góc phải trên, vì "Đại có thích nền tối không" là chuyện
chưa biết. Nút này **nhớ lựa chọn** (localStorage) nên bấm một lần là lần sau vẫn vậy.
⇒ Không phải chọn thay Đại, và không phải làm lại nếu Đại thích nền sáng hơn.

### 2.3. Thứ tự nội dung trong file HTML

Đọc từ trên xuống theo mức quan trọng:

```
1. Ba số lớn:  Chi tiêu  ·  Lượt mua  ·  Chi phí mỗi đơn
2. Khung NHẬN ĐỊNH (AI viết)          ← đưa lên cao vì đây là phần "đọc hiểu"
3. Năm chỉ số phụ
4. Bảng Camp hiệu quả      (kèm dòng ghi rõ tiêu chí xếp hạng)
5. Bảng Camp kém hiệu quả  (kèm dòng ghi rõ vì sao bảng có thể trống)
6. Chân trang: bộ lọc + cách tính + giờ tạo file
```

> ⚠️ **Giữ nguyên hai dòng ghi chú tiêu chí xếp hạng.** Bản cũ đã có, và `README.md` ghi rõ "đừng xoá
> dòng đó": nếu không có, Đại sẽ tưởng bảng xếp sai khi thấy camp 3 đơn đứng trên camp 10 đơn.

---

## 3. Việc phát sinh khi thi công — **thêm model dự phòng cho phần nhận định**

**Đây là việc Đại KHÔNG yêu cầu, nhưng không làm thì yêu cầu của Đại không thành.**

Đại muốn phần nhận định nằm trong file HTML. Khi thi công, kiểm tra thật thì phát hiện:

| Model | Kết quả thử lúc 15:50 ngày 29/09/2026 |
|---|---|
| `gemini-3.6-flash` (model báo cáo) | ❌ **HTTP 503** — quá tải |
| `gemini-3.8-flash` (model hỏi đáp) | ❌ **HTTP 503** — quá tải |
| `gemini-3.5-flash` | ✅ chạy tốt |

Và trong `logs/baocao.log` cùng buổi chiều, model báo cáo đã hỏng **ba lần liên tiếp**:
`12:00:39`, `15:48:21`, `15:49:17` — mỗi lần code đã tự thử lại 3 lượt theo `SO_LAN_THU_LAI` mà
vẫn hỏng.

⇒ Không có dự phòng thì **phần nhận định mà Đại vừa yêu cầu sẽ thiếu suốt nhiều giờ**, và Đại không
biết vì sao.

**Cách sửa:** `ai.viet_nhan_dinh()` thử **lần lượt** model chính rồi model dự phòng
(`GEMINI_MODEL_BAO_CAO_DU_PHONG`, mặc định `gemini-3.5-flash`). Trần miễn phí tính riêng cho từng
model (20 lượt/ngày/model) nên dùng dự phòng **không ăn vào lượt của model chính**.

**Kết quả thật sau khi sửa:** chạy lại `report.py --mock 12` → nhật ký ghi
**`AI da viet xong phan nhan dinh`** (trước đó 3/3 lần hỏng). Phần nhận định trong file HTML là chữ
thật của AI, có dấu đầy đủ.

> ⚠️ **Dự phòng đặt ở `viet_nhan_dinh()`, KHÔNG đặt trong `goi_gemini()`.** `goi_gemini()` là hàm
> dùng chung; nhét vòng lặp model vào đó sẽ làm **mọi** lỗi gọi tốn gấp đôi số lần thử và làm hỏng
> các bài kiểm thử đếm số lần gọi. Đã kiểm: 8 bài kiểm thử cũ gọi `goi_gemini()` trực tiếp vẫn
> nguyên vẹn.

---

## 4. Thay đổi trong code

| File | Thay đổi |
|---|---|
| `dashboard.py` | **Viết lại phần giao diện.** Thêm `doan_van()` (đổi chữ AI thành các đoạn HTML, **có escape**), `the_so()`. `build_html` và `save_dashboard` nhận thêm `nhan_dinh`, `loi_ai`. Tách CSS và JS ra **chuỗi riêng** thay vì nhét vào f-string (bản cũ phải viết `{{ }}` cho mọi dấu ngoặc — khó đọc, dễ sai) |
| `report.py` | `build_report(env, stats, period_text)` — **bỏ** tham số `nhan_dinh`/`loi_ai`, còn 11 dòng. `main()` truyền nhận định vào `save_dashboard`. Rút ngắn caption file HTML. **Xoá `mo_ta_moi_don()`** (không còn ai dùng) |
| `ai.py` | Thêm `MODEL_BAO_CAO_DU_PHONG_MAC_DINH`, `chon_model_bao_cao()`. `viet_nhan_dinh()` thử lần lượt các model |
| `.env.example` | Thêm khoá `GEMINI_MODEL_BAO_CAO_DU_PHONG` (để trống thì dùng mặc định trong code) |
| `tests/test_dashboard.py` | **File mới** — trước 29/09/2026 file `dashboard.py` **không có bài kiểm thử nào**, dù đây là thứ Đại mở ra đọc |
| `tests/test_report.py` | Thay lớp `TestBuildReportCoNhanDinhAI` bằng `TestBuildReportMauNgan` (13 bài) |
| `tests/test_ai.py` | Thêm lớp `TestModelDuPhongChoNhanDinh` (9 bài) |
| `chay-kiem-thu.bat` | 392 → 435 bài |

**Không đụng tới:** `fetch_insights`, `apply_filter`, `compute_stats`, `get_action_value`,
`fmt_money`, `determine_period`, `chi_phi_moi_don`, `cong_cu.py`, `nguoi_truc.py`, `lich_su.py`,
`bat_thuong.py`. Toàn bộ phép tính tiền giữ nguyên.

---

## 5. Kiểm chứng

Dựng thử trong thư mục tạm trước, rồi mới áp vào repo thật.

| # | Phép kiểm | Kết quả |
|---|---|---|
| 1 | Bộ kiểm thử trong thư mục tạm | **435/435 đạt** (trước khi đổi: 392) |
| 2 | Bộ kiểm thử trong repo thật | **435/435 đạt**, không gọi mạng |
| 3 | Tin nhắn so với ví dụ của Đại | **Khớp từng ký tự** — có bài `test_khop_CHINH_XAC_vi_du_cua_Dai` khoá nguyên văn |
| 4 | Tin nhắn còn mục BỘ LỌC / NHẬN ĐỊNH / hai bảng camp không | **Không** — 4 bài kiểm thử khẳng định điều đó |
| 5 | Tin nhắn có dòng trống nào không | **Không** — 11 dòng liền mạch |
| 6 | `report.py --mock 12` trên dữ liệu **THẬT** | Tin nhắn đúng mẫu với số thật (12.549.830 VND · 16 campaign · 26 lượt mua) |
| 7 | File HTML thật sinh ra từ dữ liệu **THẬT** | 14.803 ký tự, có nút đổi nền, cả hai bộ màu, media query cho điện thoại |
| 8 | Phần nhận định trong file HTML thật | **Có chữ thật của AI**, dấu tiếng Việt đầy đủ |
| 9 | Chữ do AI viết có được escape không | **Có** — bài kiểm thử nhét `<script>alert(1)</script>` và khẳng định nó **không** chạy được |
| 10 | Tên camp có ký tự HTML có được escape không | **Có** |
| 11 | AI lỗi thì file HTML ghi gì | Khung Nhận định ghi rõ **lý do** + "số liệu vẫn đầy đủ" (đã thấy thật lúc Gemini 503) |
| 12 | Model dự phòng có được gọi khi model chính chạy được không | **Không** — không tốn thêm lượt |
| 13 | Model dự phòng trùng model chính | **Bị bỏ qua**, không gọi hai lần cùng model |
| 14 | Cả hai model đều hỏng thì thông báo ghi gì | Ghi **cả hai** model, không chỉ model cuối |
| 15 | `goi_gemini()` có bị đổi hành vi không | **Không** — có bài kiểm thử riêng khẳng định điều này |
| 16 | `mo_ta_moi_don()` còn ai gọi không | **Không** — đã xoá, và có bài kiểm tra chữ ký hàm |

---

## 6. Việc Đại cần làm

**Không có.** Không phải sửa `.env`, không phải bấm file `.bat` nào.

Muốn xem giao diện mới trước khi chờ tới mốc giờ: mở file `dashboard.html` trong thư mục dự án
(file này tự tạo lại mỗi lần chạy).

**Nếu Đại không thích nền tối:** bấm nút ở góc phải trên để đổi sang nền sáng — lựa chọn được nhớ
lại. Muốn đổi mặc định thành nền sáng thì nói, sửa một dòng.

**Nếu Đại thấy tin nhắn vẫn còn gì chưa đúng ý:** nói rõ dòng nào, mẫu tin nhắn có bài kiểm thử khoá
nguyên văn nên sửa rất nhanh.

---

## 7. Rủi ro đã biết

| Rủi ro | Mức | Cách xử lý |
|---|---|---|
| Đại không thích nền tối | Thấp | Có nút đổi sang nền sáng, có nhớ lựa chọn |
| Bỏ hai bảng camp khỏi tin nhắn làm Đại không thấy số quan trọng | Thấp | File HTML nằm **ngay dưới** tin nhắn trong cùng khung chat |
| Mất cảnh báo khi rút gọn tin nhắn | **Đã xử lý** | Hai cảnh báo (token, số bất thường) **cố ý giữ lại**, và `build_report` không nhận chúng — `main()` gắn lên đầu nên không thể mất khi đổi mẫu |
| Nhận định thiếu vì model quá tải | **Đã xử lý** | Thêm model dự phòng, có bằng chứng thật |
| Model dự phòng ăn hết lượt miễn phí | Thấp | Trần tính riêng từng model; dự phòng chỉ chạy khi model chính hỏng |
