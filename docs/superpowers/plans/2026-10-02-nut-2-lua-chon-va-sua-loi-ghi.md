# Kế hoạch — Nút 2 lựa chọn + ID chiến dịch + sửa lỗi ghi Meta

**Ngày:** 02/10/2026 · **Đại duyệt:** "Hãy làm theo ý của bạn"
**Bằng chứng gốc:** điều tra 11:00–11:40 ngày 02/10 (xem `logs/baocao.log` dòng 713–744,
và lịch sử thao tác tài khoản `act_`).

---

## 1. Vì sao có kế hoạch này

Hôm nay Đại **tự tay tắt 12 nhóm** (08:22 · 08:37 · 09:16 · 09:19 · 09:21 · 09:23 ·
10:15 · 10:15 · 10:17 · 10:46 · 10:52 · 11:26) trong khi **agent chỉ hỏi 4 lần**.
Một trong 12 nhóm đó, agent gửi lệnh nhưng **Meta từ chối** — Đại phải làm tay 38 giây sau.

Đã đổi `AGENT_NHIP_PHUT` 30 → 15 phút (xong, không thuộc kế hoạch này).

Kế hoạch này giải quyết **ba việc còn lại**, do Đại yêu cầu trực tiếp.

---

## 2. VIỆC A — Nút Telegram cho Đại chọn 2 kiểu tắt

**Hiện tại:** một nút `✅ Tắt nhóm` → luôn làm cả 4 việc (tắt adset · tắt ad · hạ ngân sách
27.000đ · đổi tên).

**Đại yêu cầu:** cho 2 lựa chọn — *tắt nhóm* hoặc *tắt nhóm + hạ ngân sách*.

**Thiết kế bàn phím mới** (`agent_xin_phep.nut_bam`):

```
[ ⏸ Tắt nhóm ]  [ ⏸💰 Tắt + hạ ngân sách ]
[ ⏭ Bỏ qua ]
```

| Nút | `callback_data` | Làm gì |
|---|---|---|
| ⏸ Tắt nhóm | `tat:<ma>` | tắt adset + tắt ad + đổi tên — **GIỮ ngân sách** |
| ⏸💰 Tắt + hạ ngân sách | `tathns:<ma>` | như trên **+ hạ ngân sách 27.000đ** |
| ⏭ Bỏ qua | `boqua:<ma>` | không làm gì |

**Đọc lệnh** (`lenh_telegram.py`): thêm `tathns` vào danh sách đồng ý, trả về mã kết quả mới
`"dong_y_ha_ngan_sach"` (giữ nguyên `"dong_y"` cho nút tắt thường).

⚠️ **Bẫy đã kiểm tra:** `doc_tra_loi` so khớp **cả từ** (`phan[:len(bx)] == bx`), nên `"tathns"`
KHÔNG bị khớp nhầm thành `"tat"`. Nhưng vẫn phải đặt `tathns` **trước** `tat` trong danh sách
để chắc chắn.

**Xử lý** (`agent.py::_lam_theo_dong_y`): nhánh theo `kq["ket_qua"]`.
- `dong_y` → `tam_dung_va_ha_ngan_sach(..., ngan_sach=None)`
- `dong_y_ha_ngan_sach` → như hiện nay (27.000đ)

⇒ `agent_cong_cu_ghi.tam_dung_va_ha_ngan_sach` phải nhận `ngan_sach=None` = **không đụng ngân sách**.

---

## 3. VIỆC B — Hiện ID CHIẾN DỊCH thay cho ID nhóm

**Đại yêu cầu:** trong tin Telegram, thay ID nhóm bằng ID chiến dịch để dễ tra trên Meta.

**Cách làm:** thêm `campaign_id` vào danh sách trường khi đọc nhóm
(`agent_doc_meta.doc_nhom_dang_chay`), rồi đưa vào `doi_tuong`.

**Tin nhắn mới** (`agent_xin_phep.soan_tin` và `agent.py::_lam_theo_dong_y`):

```
✅ ĐÃ TẮT NHÓM
Chiến dịch: 120250370603560509        <-- ID CHIẾN DỊCH (Đại tra cái này)
Nhóm: 2026 - 09 - 12 - dainq - Scale - Offline A4
Kết quả: ...
Tên mới: ...
Quảng cáo bên trong: đã tắt
```

⚠️ **ID NHÓM vẫn phải giữ trong `callback_data` và trong sổ** — nút bấm cần nó để gửi lệnh
lên Meta. Chỉ **đổi phần hiển thị**, không đổi phần dữ liệu.

---

## 4. VIỆC C — Sửa lỗi ghi Meta

### C1. Ghi log lỗi ĐẦY ĐỦ
Hiện chỉ ghi `loi.get('message')` = *"Invalid parameter"* — vô nghĩa.
Meta còn trả `code`, `error_subcode`, `error_user_msg`, `error_data`.

Thêm hàm `agent_cong_cu_ghi.mo_ta_loi(err)` gom hết thành một chuỗi.

### C2. TÁCH LỆNH khi gộp thất bại — quan trọng nhất
**Bằng chứng:** nhóm `120250277820620509` sáng nay. Lệnh gộp 3 trường bị từ chối.
Nhưng **38 giây sau Đại tắt được nhóm đó bằng tay**, và lúc 11:35 agent thử lại thì
**cả 3 cách đều thành công**. ⇒ Thủ phạm là **một trường trong lệnh gộp**, không phải cả lệnh.

**Thiết kế:** khi gộp thất bại, **thử lại từng phần theo thứ tự ưu tiên**:

1. `status` (+ `name` nếu có) — **việc CHÍNH, phải xong trước**
2. `daily_budget` — việc phụ

Kết quả trả về phải nói rõ **đã tắt được chưa** và **đã hạ được ngân sách chưa**, tách
thành hai thông tin. Không được để "không hạ được ngân sách" làm báo là "tắt thất bại".

⇒ Sửa chữ ký trả về: thêm `chi_tiet["da_tat"]` và `chi_tiet["da_ha_ngan_sach"]`.

### C3. Thử lại khi lỗi tạm thời
Đã có trong `api_post` cho mã lỗi tạm thời. Giữ nguyên, chỉ mở rộng: nếu lỗi **không** nằm
trong danh sách tạm thời thì **không thử lại** (tránh đập vào tường) — nhưng ghi log đầy đủ.

⚠️ **KHÔNG làm hàng chờ thử lại qua nhiều vòng quét.** Lý do: C2 đã giải quyết đúng ca hôm nay
(tắt được ngay), mà hàng chờ lại thêm một đường trạng thái nữa để hỏng. Nếu sau này gặp ca
`status` cũng bị chặn, sẽ làm riêng.

---

## 5. VIỆC D — Trả lời câu hỏi "5 phút quét 1 lần có tốn API không?"

**Đã đo thật 02/10/2026** (đọc header `x-business-use-case-usage` của Meta):

| | |
|---|---|
| Một vòng quét gọi | **3 lần** API (đều là ĐỌC) |
| 21 lần gọi liên tiếp tốn | **1%** hạn mức `call_count` |
| `total_cputime`, `total_time` | **không đổi** |
| Tier token | `development_access` |

⇒ Nếu 1% ≈ 21 lần gọi thì 100% ≈ 2.100 lần/giờ.

| Nhịp | Vòng/ngày | Lần gọi/ngày | Ước tính % hạn mức/giờ |
|---|---|---|---|
| 30 phút | 48 | 144 | ~0,7% |
| 15 phút | 96 | 288 | ~1,4% |
| 10 phút | 144 | 432 | ~2,1% |
| **5 phút** | **288** | **864** | **~4,3%** |

⇒ **5 phút hoàn toàn không tốn API.** Meta chỉ giới hạn **GHI** (mã 613), không giới hạn đọc
ở mức này.

⚠️ **Phát hiện kèm theo:** Meta báo *"v21.0 has been deprecated"* và **tự nâng lên v26.0**.
Code đang ghi cứng `v21.0` (`report.py`, `agent_cong_cu_ghi.py`). Nên sửa cho khớp — nhưng
đây là thay đổi có rủi ro (hành vi API khác), nên **tách riêng, không gộp vào lượt này**.

---

## 6. Kiểm thử phải có

| Việc | Bài kiểm thử |
|---|---|
| A | `nut_bam` trả 3 nút, đúng `callback_data` · `doc_tra_loi` đọc `tathns:<ma>` ra `dong_y_ha_ngan_sach` · **`tathns` KHÔNG bị đọc nhầm thành `tat`** · `tat:<ma>` vẫn ra `dong_y` |
| A | `ngan_sach=None` ⇒ KHÔNG gọi đặt ngân sách (dùng mạng giả, đếm số lần POST) |
| B | Tin nhắn có dòng `Chiến dịch: <id>` · `callback_data` vẫn là **ID nhóm** |
| C1 | `mo_ta_loi` gom đủ `code`, `error_subcode`, `error_user_msg` |
| C2 | Gộp lỗi → tách lệnh → **vẫn tắt được nhóm** · hạ ngân sách lỗi ⇒ báo "đã tắt, chưa hạ ngân sách" chứ KHÔNG báo "thất bại" |
| C2 | Cả hai đều lỗi ⇒ báo thất bại thật |

**Dựng thử trước khi sửa code thật** — theo quy trình đã chốt với Đại.

---

## 7. Rủi ro

| Rủi ro | Mức | Xử lý |
|---|---|---|
| Nút "chỉ tắt" giữ ngân sách ⇒ nhóm tắt mà vẫn giữ 400.000đ | Thấp | Đó đúng là ý Đại; tên nút ghi rõ |
| `tathns` bị đọc nhầm thành `tat` | Trung bình | Có bài kiểm thử riêng cho đúng ca này |
| Đổi chữ ký trả về của `tam_dung_va_ha_ngan_sach` làm vỡ chỗ gọi cũ | Trung bình | Chạy TOÀN BỘ bộ kiểm thử (662 bài) sau khi sửa |
| Tách lệnh làm tăng số lần GHI ⇒ chạm mã 613 | Trung bình | Chỉ tách **khi gộp đã thất bại**; giữ `CHO_GIUA_HAI_LAN_GHI` giữa mọi lần ghi |
