# HƯỚNG DẪN MÁY NHÀ — BẢN 02/10/2026

**Dành cho:** Đại (không cần biết code).

> **Nếu bạn là trợ lý AI trên máy nhà đang đọc file này:**
> đọc hết file rồi làm theo đúng thứ tự ở **PHẦN B**. Không bỏ bước nào.

Máy công ty đã đẩy tới mốc **`16aa0ff`** (02/10/2026). Đây là bản mới nhất.
**Kho GitHub:** `meta-ads-report`, nhánh `main`.

---

## PHẦN A — HIỂU ĐÚNG MỘT ĐIỀU TRƯỚC KHI LÀM

### ⚠️ GitHub KHÔNG chứa cấu hình

> **File `.env` KHÔNG BAO GIỜ lên GitHub** — nó chứa token Telegram, token Meta, chìa khoá AI.
> `.gitignore` chặn lại để không lộ bí mật. Trên GitHub chỉ có **`.env.example`** — file MẪU,
> **không phải công tắc thật**.

| | Máy công ty | Máy nhà |
|---|---|---|
| Code | `git pull` từ GitHub | `git pull` từ GitHub |
| `.env` | **riêng của máy này** | **riêng của máy này** |

⇒ **`git pull` KHÔNG BAO GIỜ làm đổi chế độ chạy.** Muốn đổi thì phải sửa `.env` **của chính máy đó**.
Hai máy ở hai chế độ khác nhau là **đúng thiết kế**, không phải lỗi.

### ⚠️ Sau khi `git pull` xong, BẮT BUỘC khởi động lại agent

Đây là **bài học đắt nhất ngày 02/10/2026**, đã gây lỗi thật:

> Python nạp code vào bộ nhớ **MỘT LẦN** lúc khởi động. Sửa file trên ổ đĩa xong, tiến trình đang chạy
> **vẫn giữ bản cũ trong RAM** và tiếp tục làm theo code cũ.
>
> Máy công ty đã dính đúng lỗi này: agent khởi động 13:39, code sửa lúc 15:37, nhưng đến 16:30
> agent **vẫn ghi tên nhóm sai** — vì chưa ai khởi động lại.

⚠️ **KHÁC với `.env`:** từ 01/10, `.env` được đọc lại **mỗi 15 giây** nên sửa `.env` là **ăn ngay**,
không cần khởi động lại. Nhưng **code thì khác** — **sửa code ⇒ phải khởi động lại agent. Không ngoại lệ.**

---

## PHẦN B — MÁY NHÀ CẦN LÀM (5 BƯỚC, ĐÚNG THỨ TỰ)

### Bước 1 — Kéo code mới

Mở cửa sổ lệnh **tại đúng thư mục dự án** rồi gõ:

```
git pull
```

**Kiểm tra:** gõ tiếp dòng này, phải thấy mốc `16aa0ff`:

```
git log --oneline -1
```

### Bước 2 — Sửa mốc giờ báo cáo trong `.env`

Trong 5 mục cần sửa, còn thiếu dòng này:

```
REPORT_SLOTS=8,17
```

Nếu máy nhà đang là `8,12,17` thì đổi còn `8,17`. **Mốc 12h đã bỏ từ 02/10/2026** trên cả hai máy.

**Cách làm:** bấm đúp file **`mo-file-env.bat`** — nó tự mở Notepad đúng file `.env`.
Tìm dòng `REPORT_SLOTS`, sửa thành `REPORT_SLOTS=8,17`, bấm **Ctrl + S**, đóng Notepad.

⚠️ `.env` **không** đi theo `git pull` (xem PHẦN A). Phải tự sửa tay.

### Bước 3 — Sửa nhịp quét

Cũng trong `.env`, tìm dòng `AGENT_NHIP_PHUT`:

```
AGENT_NHIP_PHUT=15
```

Trước đây là `30`. **Nhịp 30 phút quá thưa** — Đại đã từng tự tay tắt 12 nhóm trong một buổi sáng
trước khi agent kịp quét. Nay đổi còn **15 phút**.

⚠️ Nếu `.env` máy nhà **chưa có** dòng này thì thêm vào cuối file.

### Bước 4 — Sửa phạm vi lọc

Kiểm tra dòng này trong `.env`:

```
FILTER_INCLUDE=dainq
```

⚠️ Nếu máy nhà đang là `` (mã tài khoản) thì đổi thành **`dainq`**.
Phạm vi đúng là **tên đối tượng chứa `dainq`**, lọc ở **cấp chiến dịch/nhóm**, **KHÔNG** lọc theo tên quảng cáo.

### Bước 5 — Chọn chế độ chạy, rồi khởi động lại agent

Có **2 lựa chọn**. Bấm đúp **đúng một** file:

| Muốn gì | Bấm file | Có hỏi lại không |
|---|---|---|
| Agent **TẮT NHÓM THẬT** trên Meta | `chuyen-sang-lam-that.bat` | **Có** — phải gõ đúng chữ `co` |
| Agent **chỉ nói**, không gửi lệnh nào | `chuyen-sang-tap-su.bat` | Không (đây là chiều an toàn) |

Hai file này chỉ sửa **đúng một dòng** `AGENT_TAP_SU` trong `.env`, **sao lưu** `.env` thành
`.env.bak-truoc-doi-che-do`, và in ra chế độ đang có trước khi đổi.

**Rồi BẮT BUỘC bấm `khoi-dong-lai-agent.bat`** (lý do ở PHẦN A — bước này không được bỏ).

### Bước 6 — Kiểm chứng

Mở file `logs\baocao.log`, tìm dòng mới nhất có dạng:

```
AGENT: khoi dong — muc 2 — LAM THAT
AGENT: N nhom cham nguong — hoi X, bo qua Y (dang cho Dai tra loi), chan Z (rao an toan)
```

- Dòng `khoi dong` có **giờ mới** ⇒ agent đã nạp code mới. ✅
- Dòng `N nhom cham nguong` **mới có từ 01/10** ⇒ code mới đã chạy.

⚠️ **Đừng nhầm file `logs\agent-dang-chay.lock` với giờ khởi động.** File đó ghi **nhịp quét gần nhất**,
không phải giờ khởi động. Muốn biết giờ khởi động thật thì tìm dòng `AGENT: khoi dong` trong `baocao.log`.

---

## PHẦN C — LUẬT TẮT NHÓM HIỆN HÀNH (xét theo thứ tự TH3 → TH2 → TH1)

| TH | Điều kiện | Ngưỡng | Tên mới |
|---|---|---|---|
| **TH3** | Có lượt mua tháng | giá/lượt mua **tháng** ≥ **390.000đ** | `<x>/450 X<tháng>-<năm>` |
| **TH2** | Có tin nhắn ≥1, chưa ra lượt mua | chi tiêu **hôm nay** ≥ **290.000đ** | `0/350 X<tháng>-<năm> TN` |
| **TH1** | Không có tin nhắn nào | chi tiêu **hôm nay** ≥ **70.000đ** | `0/<2×chi tiêu> X<tháng>-<năm>` |

**Những điểm đã đổi so với bản cũ ở máy nhà:**

1. **CẢ BA trường hợp đều ghi NĂM** vào tên nhóm. Ví dụ: `0/350 X10-26 TN` (X10 = tháng 10, 26 = năm 2026).
   Luật cũ *"TH1/TH3 không ghi năm"* **đã bỏ**.
2. **Xét ngưỡng theo TỪNG QUẢNG CÁO** (mới từ 02/10):
   - Nhóm có **≥2 quảng cáo** và có quảng cáo chạm ngưỡng ⇒ **tắt LẺ quảng cáo đó**, giữ nhóm.
   - **Tắt lẻ quảng cáo = CHỈ tắt + đổi tên. KHÔNG hạ ngân sách** (hạ ngân sách là việc của cả nhóm).
   - Nhóm **0 hoặc 1 quảng cáo** ⇒ tắt **CẢ NHÓM** như cũ.
3. **Ngưỡng CỐ ĐỊNH** cho mọi nhóm — không đọc từ số `y` trong tên nữa.
4. **Thứ tự khi tắt: tắt NHÓM trước, xong mới tắt QUẢNG CÁO.** Đừng làm ngược.
5. **"Tin nhắn" đếm CẢ HAI** chỉ số: `messaging_first_reply` **hoặc** `messaging_conversation_started_7d`.

**Phạm vi được đụng tới:** tên đối tượng chứa `dainq` HOẶC bắt đầu bằng mã content viết hoa
HOẶC có `new - dainq`. Lọc cấp **chiến dịch/nhóm**, **KHÔNG** theo tên quảng cáo.

---

## PHẦN D — NÚT BẤM TRÊN TELEGRAM

Tin xin phép có **2 kiểu tắt**, **mỗi nút một hàng**:

```
⏸ TẮT NHÓM (giữ ngân sách)        → tắt nhóm + tắt quảng cáo + đổi tên, GIỮ ngân sách
💰 TẮT NHÓM + HẠ NGÂN SÁCH         → như trên + hạ ngân sách 27.000đ
⏭ Bỏ qua
```

⚠️ **Hai nút trả HAI kết quả khác nhau — đừng gộp lại.**

**Meta TỪ CHỐI thì KHÔNG tắt gì cả.** Tin báo lỗi gồm **lỗi Meta nguyên văn** + **đoán nguyên nhân**,
kèm 2 nút `quét lại` / `bỏ qua 24h`. Không bấm gì ⇒ 15 phút sau agent hỏi lại.

⚠️ **Telegram KHÔNG cho đổi màu nút.** Đừng tìm cách đổi màu — chỉ làm rõ bằng **chữ và bố cục**.

**Lệnh nhắn cho bot:** *"báo cáo"* → gửi tin + **file HTML**; *"báo cáo 20/09/2026"* → lấy thẳng từ Meta.
⚠️ **Chỉ nhận ngày ĐỦ năm.** *"báo cáo hôm qua"* = xin FILE; *"báo cáo hôm qua thế nào?"* = câu hỏi.

---

## PHẦN E — ⚠️ ĐỌC TRƯỚC KHI CHO MÁY NHÀ CHẠY THẬT

### ⚠️ Hai máy cùng chạy thật trên MỘT tài khoản Meta

Cả hai máy cùng trỏ vào **một tài khoản Meta**. Nếu cả hai cùng chạy THẬT thì:

- Bot Telegram **riêng** ⇒ không nuốt tin của nhau ✅
- Meta thì **chung** ⇒ **hai agent có thể cùng tác động vào một nhóm** ⚠️

Ngày 02/10/2026 đã thấy dấu hiệu này thật: một nhóm bị tắt tự động, nhưng sau đó **được bật lại thủ công**
và **ngân sách trở về 400.000đ** — nhiều khả năng do máy kia làm.

⇒ **Đại nên chọn: MỘT máy chạy thật, máy kia chỉ nói.** Hoặc chấp nhận hai máy cùng chạy và tự theo dõi.

### Token máy nhà hết hạn ngày nào

| Máy | Token hết hạn |
|---|---|
| **Máy nhà** | **10/11/2026** |
| Máy công ty |  |

Kiểm tra bất cứ lúc nào: **nhắn bot chữ `token`**.

⛔ **Hệ thống KHÔNG tự gia hạn token được. Meta không cho.** Máy công ty đã thử thật 29/09/2026:
Meta trả token mới nhưng **giữ nguyên ngày hết hạn cũ** (lệch **+0 giây**). Vẫn phải làm tay mỗi 60 ngày.
Hệ thống nhắc hai mức: còn dưới **30 ngày** → nhắc mỗi ngày; còn dưới **7 ngày** → nhắc mọi báo cáo.

### Thứ tự khởi động lại BẮT BUỘC

⚠️ **Từ 01/10, AGENT là nơi DUY NHẤT đọc Telegram.** Vì vậy khi khởi động lại:

```
1. Dừng CẢ HAI  (người trực + agent)
2. Bật NGƯỜI TRỰC trước
3. Rồi mới bật AGENT
```

Làm ngược lại ⇒ **hai bên nuốt tin của nhau**.

---

## TÓM TẮT NHANH — DÁN VÀO CỬA SỔ LỆNH

```
MÁY NHÀ — BẢN 02/10/2026

1. git pull                                    ← phải thấy mốc 16aa0ff
2. mo-file-env.bat  →  sửa REPORT_SLOTS=8,17        ← mốc 12h đã bỏ
3.                    sửa AGENT_NHIP_PHUT=15        ← trước là 30
4.                    kiểm FILTER_INCLUDE=dainq      ← không phải tên tài khoản
5. chuyen-sang-lam-that.bat  (hoặc tap-su)     ← chọn chế độ
6. khoi-dong-lai-agent.bat                     ← BẮT BUỘC, sửa code phải khởi động lại
7. mở logs\baocao.log → thấy dòng "AGENT: khoi dong" giờ MỚI là xong
```

**Công cụ kiểm tra (chỉ đọc, không gửi lệnh nào lên Meta):**

```
kiem-tra-ten-nhom.bat     → quét tên nhóm thiếu năm
chay-kiem-thu.bat         → chạy toàn bộ bài kiểm thử
```

**Xong.**
