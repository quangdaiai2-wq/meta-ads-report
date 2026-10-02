# Kế hoạch — Nhánh LỖI khi Meta từ chối tắt nhóm

**Ngày:** 02/10/2026 · **Đại chốt:** qua 2 câu hỏi ở đầu lượt này.
**Thay thế:** cơ chế "tách lệnh" đã làm buổi chiều cùng ngày (commit `18f4597`) — **bỏ**.

---

## 1. Đại chốt gì

> *"Đường màu vàng thì nếu Meta báo lỗi thì phải báo lỗi này là lỗi do đâu và sau đó thì quét lại
> chứ không tắt gì ở đây cả. Bạn có thể hiện 2 nút: Tiếp tục quét lại lần sau · Bỏ qua 24h
> (đúng 24h sau phải quét lại)."*

Hai câu hỏi đã hỏi và Đại trả lời:

| Câu hỏi | Đại chọn |
|---|---|
| Không bấm nút nào thì sao? | **Tự hỏi lại ở lần quét sau** (15 phút). Nút "Tiếp tục quét lại" dùng để huỷ lệnh "bỏ qua 24h" nếu đổi ý. |
| Thứ tự tắt? | **Đổi: tắt NHÓM trước, rồi mới tắt quảng cáo.** |

---

## 2. Vì sao bỏ "tách lệnh"

Buổi chiều tôi làm: gộp lỗi → tự tách ra gửi `status` riêng → vẫn tắt được nhóm.
**Đại không muốn thế.** Lý do hợp lý: nếu Meta đã từ chối thì có gì đó chưa sẵn sàng; cố tắt sẽ
tạo **trạng thái nửa vời** (tắt được nhóm nhưng không hạ được ngân sách), khó cho Đại kiểm tra sau.

⇒ **Bỏ hẳn tách lệnh.** Meta từ chối ⇒ **KHÔNG tắt gì cả**, báo lỗi, hẹn quét lại.

⚠️ **Hệ quả phải nói rõ với Đại:** ca sáng nay (nhóm mới tạo) sẽ **không tự tắt được nữa** — agent
báo lỗi rồi quét lại lần sau. Nếu Meta vẫn từ chối thì nhóm **vẫn phải tắt tay**. Đổi lại: không
bao giờ có trạng thái nửa vời.

---

## 3. Thứ tự tắt — ĐỔI

**Cũ:** tắt quảng cáo → tắt nhóm. Bước sau lỗi ⇒ quảng cáo đã tắt mất rồi, nhóm vẫn chạy.
**Mới:** **tắt nhóm (+ ngân sách + tên) → nếu THÀNH CÔNG mới tắt quảng cáo.**

⇒ Không còn cảnh "nhóm còn chạy mà quảng cáo đã tắt".

---

## 4. Tin báo lỗi — 2 nút

```
❌ KHÔNG TẮT ĐƯỢC NHÓM

Chiến dịch: 120250277820620509
Nhóm: 2026 - 10 - 02 - dainq - Scale - Online
Lỗi Meta trả về: Invalid parameter | ma=100 | ma phu=1487534
Có thể do: ngân sách đặt không hợp lệ cho nhóm này

Agent KHÔNG tắt gì cả (nhóm và quảng cáo vẫn nguyên).
Lần quét sau agent sẽ thử lại.
```

Nút:
```
[ 🔁 Tiếp tục quét lại lần sau ]  [ ⏸ Bỏ qua 24h ]
```
- `quetlai:<ma>` → **xoá** lệnh bỏ qua, quay về mặc định (hỏi lại ở lần quét sau)
- `boqua24:<ma>` → **chặn 24 giờ**, đúng 24h sau mới xét lại

---

## 5. "Lỗi do đâu" — hàm đoán nguyên nhân

Thêm `agent_cong_cu_ghi.doan_nguyen_nhan(err)`. Dựa vào mã lỗi Meta:

| Mã | Nghĩa dễ hiểu |
|---|---|
| `613` | Ghi quá nhanh, Meta tạm chặn |
| `190` | Token hết hạn hoặc sai |
| `200` / `272` | Token thiếu quyền |
| `17` | Vượt hạn mức của tài khoản |
| `100` + `error_user_msg` có chữ "budget" | Ngân sách không hợp lệ cho nhóm này |
| `100` khác | Meta không nhận tham số — thường do nhóm **vừa tạo trong ngày, Meta chưa duyệt xong** |
| Không rõ | Ghi nguyên văn lời Meta, không đoán bừa |

⚠️ **Không đoán bừa.** Không khớp bảng thì in nguyên văn lỗi Meta kèm ghi chú "chưa rõ nguyên nhân".

---

## 6. Chặn "bỏ qua 24h" — dùng lại cơ chế đã có

Đã có sẵn `agent_rao.kiem` + `agent_ky_uc.nhom_da_tra_loi` + `HAN_HOI_LAI_PHUT` (chặn hỏi lại
trong X phút). Nay thêm **mốc bỏ qua riêng cho từng nhóm**:
- `agent_ky_uc.bo_qua_nhom(ma, den_luc)` — ghi mốc
- `agent_ky_uc.nhom_dang_bo_qua(bay_gio)` — đọc ra
- `agent_rao.kiem` thêm một rào: nhóm còn trong hạn bỏ qua ⇒ **chặn**, lý do ghi rõ

---

## 7. Kiểm thử phải có

| Việc | Bài kiểm thử |
|---|---|
| Bỏ tách lệnh | Gộp lỗi ⇒ **KHÔNG** có lần gọi thứ hai lên Meta · trả về thất bại |
| Thứ tự tắt | Tắt nhóm lỗi ⇒ `tat_quang_cao` **KHÔNG được gọi** |
| Thứ tự tắt | Tắt nhóm OK ⇒ quảng cáo mới được tắt |
| Nút lỗi | `nut_loi` có đúng 2 nút, đúng `callback_data` |
| Đọc lệnh | `quetlai:<ma>` → `dong_y_quet_lai` · `boqua24:<ma>` → `bo_qua_24h` |
| Bỏ qua 24h | Ghi mốc rồi `kiem()` **chặn** · sau 24h thì **không chặn** |
| Quét lại | Bấm "quét lại" ⇒ xoá mốc ⇒ `kiem()` **không chặn** |
| Đoán nguyên nhân | 5–6 mã lỗi mẫu ra đúng câu · mã lạ thì in nguyên văn, không đoán |

**Dựng thử toàn bộ ngoài repo trước khi sửa code thật.**

---

## 8. Rủi ro

| Rủi ro | Xử lý |
|---|---|
| Bỏ tách lệnh ⇒ nhóm không tự tắt được khi Meta từ chối | **Đúng ý Đại.** Nói rõ hệ quả trong báo cáo |
| Đổi thứ tự ⇒ chậm hơn 20 giây mỗi nhóm (chờ giữa hai lần ghi) | Chấp nhận; an toàn hơn |
| Đổi thứ tự ⇒ tắt nhóm OK nhưng tắt quảng cáo lỗi | Báo rõ "đã tắt nhóm, quảng cáo chưa tắt" — vẫn là thành công |
| Sổ cũ không có trường `bo_qua` | Phải chịu được sổ thiếu khoá (đã là quy ước của `agent_ky_uc`) |
