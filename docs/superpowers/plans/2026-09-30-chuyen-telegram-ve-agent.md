# Kế hoạch — Chuyển Telegram về cho agent, bỏ báo cáo theo khung giờ

**Ngày:** 30/09/2026 · **Trạng thái:** Đại đã chốt hướng, CHƯA thi công
**Đại chốt (30/09/2026):** *"Sau này tạo ra agent hỏi đáp và lấy thông tin được, thì bỏ hẳn cái báo cáo
theo khung giờ đi. Vì tôi thấy nó không cần thiết nữa."*

---

## 1. VÌ SAO PHẢI CHUYỂN — không phải chuyện thẩm mỹ, mà là chuyện kỹ thuật

Telegram chỉ cho **MỘT** nơi đọc tin của một bot, và **`offset` xoá vĩnh viễn** mọi update có mã nhỏ
hơn. Đã kiểm chứng bằng tài liệu Bot API (30/09/2026):

| Cơ chế | Tác dụng |
|---|---|
| `offset` trong `getUpdates` | **Xác nhận và xoá** mọi update có `update_id` nhỏ hơn — kể cả loại mình không xin nhận |
| `allowed_updates` | Chỉ là **bộ lọc giao hàng** — loại bị lọc vẫn nằm chờ, nhưng sẽ bị `offset` xoá nếu nơi khác đọc trước |

⇒ **Hai tiến trình cùng đọc = tin của nhau bị nuốt mất, im lặng, không báo lỗi.** Đây chính là lỗi 6
đã gặp ở nấc 2. Cách chữa tạm hiện nay là cho `nguoi_truc.py` chuyển tiếp lệnh qua
`logs/agent-lenh.json`. **Cách đó chạy được, nhưng là hàng rào tạm** — và Đại muốn bỏ hẳn.

---

## 2. HIỆN TẠI (sau nấc 2, 30/09/2026)

```
nguoi_truc.py  ──►  SỞ HỮU Telegram (getUpdates: message + callback_query)
   │                 · gửi báo cáo theo mốc 8h / 12h / 17h
   │                 · nhận tin Đại gửi
   │                 · gặp lệnh "tắt <mã>" hoặc nút bấm  →  ghi logs/agent-lenh.json
   └──►  agent.py  ──►  đọc hàng đợi đó, rào an toàn, gửi lệnh lên Meta
```

## 3. ĐÍCH ĐẾN (Đại chốt)

```
agent.py  ──►  SỞ HỮU Telegram (getUpdates: message + callback_query)
   │            · tự phát hiện nhóm chạm ngưỡng → gửi tin có 2 nút bấm
   │            · nhận nút bấm + lệnh gõ tay
   │            · TRẢ LỜI CÂU HỎI của Đại (hỏi đáp chuyển từ người trực sang)
   │            · rào an toàn → gửi lệnh lên Meta (khi hết tập sự)
   └──►  KHÔNG CÒN báo cáo theo khung giờ
```

`nguoi_truc.py` **biến mất**. `logs/agent-lenh.json` (hàng đợi tạm) **biến mất**.

---

## 4. ⚠️ MỘT PHỤ THUỘC PHẢI GỠ TRƯỚC KHI BỎ BÁO CÁO

**Đây là chỗ dễ làm hỏng nhất, phải làm trước khi xoá gì.**

`logs/lich-su.json` — sổ số liệu 180 ngày — **do `report.py` ghi, mỗi mốc báo cáo một lần**. Bỏ báo
cáo theo khung giờ nghĩa là **không còn ai ghi sổ đó nữa**.

Nhưng **ba thứ đang đọc nó**:

| Ai đọc | Dùng để làm gì |
|---|---|
| `cong_cu.py` (4 công cụ của phần hỏi đáp) | `lay_mot_ngay`, `lay_khoang`, `xep_hang_camp`, `so_sanh` |
| `ai.py::tra_loi()` | Trả lời câu hỏi của Đại |
| `dashboard.py` | File HTML |

⇒ **Nếu bỏ báo cáo mà không ai ghi `lich-su.json`, phần hỏi đáp sẽ trả lời sai hoặc rỗng** — mà Đại
vừa nói hỏi đáp chính là thứ giữ lại. **Thứ tự bắt buộc:**

1. Cho **agent tự ghi `lich-su.json`** (một lần mỗi ngày, sau nửa đêm, ghi ngày trọn vẹn hôm trước).
2. Chạy song song vài ngày, đối chiếu sổ do agent ghi với sổ do báo cáo ghi — phải khớp.
3. **Rồi mới** tắt báo cáo theo khung giờ.

---

## 5. CÁC BƯỚC THI CÔNG

| # | Việc | Ghi chú |
|---|---|---|
| 1 | Agent tự ghi `logs/lich-su.json` mỗi ngày | Xem mục 4. **Làm trước tiên.** |
| 2 | Chuyển phần **hỏi đáp** vào agent | Dùng lại `nguoi_truc.tra_loi_tin_nhan` — **hàm thuần, đã có kiểm thử**, không viết lại |
| 3 | Agent tự gọi `getUpdates` (message + callback_query) | Bỏ hẳn `logs/agent-lenh.json` và phần chuyển tiếp trong người trực |
| 4 | Chạy song song 1 tuần: agent sở hữu Telegram, người trực **chỉ gửi báo cáo**, không đọc tin | Người trực phải bỏ hẳn `getUpdates` |
| 5 | Tắt báo cáo theo khung giờ | Sửa `REPORT_SLOTS` hoặc bỏ hẳn `nguoi_truc.py` |
| 6 | Gỡ lịch Windows / task của người trực | `go-nguoi-truc.bat` đã có sẵn |

---

## 6. RỦI RO

| Rủi ro | Mức | Xử lý |
|---|---|---|
| Bỏ báo cáo trước khi agent ghi được `lich-su.json` ⇒ **hỏi đáp trả lời sai** | **Cao** | Làm theo đúng thứ tự mục 4: ghi sổ trước, chạy song song, đối chiếu, rồi mới tắt |
| Agent tắt máy thì Đại mất cả báo cáo lẫn hỏi đáp | **Cao** | Phải để agent chạy như một tiến trình thường trú, tự bật khi máy khởi động — giống người trực hiện nay |
| Mất các mốc báo cáo quen thuộc | Trung bình | Đại đã cân nhắc và chấp nhận. Nên giữ lại khả năng bật lại bằng một khoá `.env` |
| Sửa nhiều thứ cùng lúc rồi hỏng khó tìm | Trung bình | Làm từng bước, mỗi bước chạy đủ bộ kiểm thử (**hiện 564 bài**) |

---

## 7. GHI CHÚ VỀ BẢN THIẾT KẾ

Bản thiết kế 29/09 (mục 2.3) nói **agent phải tách riêng, không nhét vào `nguoi_truc.py`**. Kế hoạch
này **không đi ngược** điều đó — nó đi theo hướng ngược lại: **giữ agent là tiến trình riêng, và cho
nó sở hữu Telegram**, còn tiến trình báo cáo thì bỏ hẳn.

Nhưng có **hai điều trong bản thiết kế nay khác thực tế**, phải ghi lại chứ không được lặng lẽ làm:

1. **Trần AI.** Bản thiết kế lo agent chạy nền sẽ ăn hết 20 lượt/ngày của báo cáo. Nhưng nấc 2 **chạy
   bằng luật code, không dùng AI**, nên lo ngại đó không còn. Khi hỏi đáp chuyển sang agent thì **phần
   hỏi đáp vẫn dùng AI** — lúc đó phải tính lại trần, và nên để **model riêng** cho agent.
2. **Xung đột mục tiêu.** Bản thiết kế nói báo cáo cần số cố định, agent cần tự do. Nay **báo cáo bị
   bỏ hẳn**, nên xung đột này tự hết.

⇒ Khi thi công bước 1, phải **sửa `2026-09-28-nguoi-truc-ai-agent-design.md` mục §3** cho khớp thực
tế, kèm ghi chú ngày và lý do — theo đúng luật của chính bản thiết kế.
