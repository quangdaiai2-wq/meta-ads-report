# HƯỚNG DẪN CÀI LẠI TRÊN MÁY NHÀ — 29/09/2026

**Dành cho:** Đại. Không cần biết code. Cứ làm theo đúng thứ tự, mỗi bước một việc.

> **File này khác gì `HUONG-DAN-MAY-NHA.md`?**
> File kia giả định máy nhà **đã cài sẵn**. File này dành cho tình huống **dựng lại từ đầu**:
> code đã tải mới về thư mục mới, nhưng `.env` phải mang từ bản cài cũ sang.

---

## PHẦN A — ĐÃ XONG (trợ lý làm, Đại không phải làm gì)

| Việc | Kết quả |
|---|---|
| Tải code mới nhất về thư mục làm việc | ✅ Xong — bản `8845e3c` |
| Mang `.env` từ bản cài cũ sang | ✅ Xong — token còn nguyên |
| Thêm dòng `REPORT_SLOTS=8,12,17` | ✅ Xong — bỏ mốc 22h |
| Kiểm tra token Telegram + Meta | ✅ Còn sống, dùng được |
| Chạy thử toàn bộ luồng (không gửi) | ✅ Xong — ra số thật |

**Thư mục làm việc từ nay:**

```
D:\Workbuddy AI\AI AGENT FB        ← dự án chính, dùng từ nay
D:\Workbuddy\2026-09-11-21-17-48   ← bản cài CŨ, GIỮ LẠI làm bản dự phòng, đừng xoá
```

---

## PHẦN B — KẾT QUẢ KIỂM TRA TOKEN (đọc để yên tâm)

| Mục | Kết quả |
|---|---|
| Bot Telegram | `@BCCTYCT_bot` — tên hiển thị **"Bot Báo Cáo Home❤️"** ✅ đúng bot máy nhà |
| Khung chat | "Quang" ✅ |
| Token Meta | Còn sống **44,5 ngày**, hết hạn **** |
| Tài khoản quảng cáo |  — đang hoạt động, tiền tệ VND ✅ |
| Quyền của token | `ads_read` ✅ — **chưa có** `ads_management` ❌ (xem Phần E) |

**Chạy thử ra số thật:** 16 campaign, chi 15.317.803 VND, 37 lượt mua.

---

## PHẦN C — ĐẠI CÒN **BỐN BƯỚC**

### 🔴 BƯỚC 1 — Lấy chìa khoá AI (khoảng 5 phút, miễn phí)

1. Mở **Chrome** hoặc **Edge**
2. Gõ vào thanh địa chỉ: `aistudio.google.com/apikey` rồi Enter
3. Đăng nhập bằng **tài khoản Google** của Đại
4. Bấm nút **Create API key**
5. Nếu hỏi chọn project → chọn cái nào cũng được
6. Một dãy ký tự dài hiện ra → bấm **Copy**

> ⚠️ Chìa khoá này **xem lại được bất cứ lúc nào** ở đúng địa chỉ trên. Lỡ đóng trang cũng không sao.

**Chưa có chìa khoá này thì:** báo cáo **vẫn gửi đầy đủ số liệu**, chỉ **thiếu mục NHẬN ĐỊNH**,
và bot **không trả lời được** khi Đại nhắn hỏi số liệu.

---

### 🔴 BƯỚC 2 — Dán chìa khoá vào file `.env`

1. Trong thư mục `D:\Workbuddy AI\AI AGENT FB`, **bấm đúp** vào file **`mo-file-env.bat`**
   → Notepad tự mở đúng file cần sửa. (Đừng tự đi tìm — trong thư mục có 4 file tên gần giống nhau.)
2. Trong Notepad bấm **Ctrl + F**, gõ `GEMINI_API_KEY`, bấm Enter
3. Dán chìa khoá vào **ngay sau dấu `=`, không có dấu cách**

   ❌ SAI:
   ```
   GEMINI_API_KEY= AIzaSy...
   ```

   ✅ ĐÚNG:
   ```
   GEMINI_API_KEY=AIzaSy...
   ```

4. Bấm **Ctrl + S** để lưu → đóng Notepad
5. **Đừng đổi tên file.** Đừng lưu thành `.env.txt`

---

### 🔴 BƯỚC 3 — Kiểm tra chìa khoá đã đúng chưa

1. Mở **File Explorer**, vào thư mục `D:\Workbuddy AI\AI AGENT FB`
2. Bấm vào **thanh địa chỉ** phía trên cùng
3. Gõ `powershell` rồi bấm **Enter** → cửa sổ xanh hiện ra, đã đứng sẵn đúng thư mục
4. Dán nguyên dòng này rồi Enter:

```powershell
python test_gemini.py
```

5. Kết quả đúng là dòng cuối ghi:

```
KET QUA: GEMINI API KEY HOAT DONG TOT
```

> 🔴 Nếu báo `HTTP 404` → **không phải chìa khoá sai**, mà là **tên model sai**.
> Mở `HUONG-DAN-LAY-CHIA-KHOA-AI.md`, mục "Nếu báo lỗi thì sao" để dò tên đúng.
>
> 🔴 Nếu báo `400` hoặc `403` → chìa khoá dán sai. Làm lại Bước 1.

---

### 🔴 BƯỚC 4 — Cài "Người trực" (bước cuối, cần quyền Admin)

1. Trong thư mục dự án, **chuột phải** vào file **`cai-dat-nguoi-truc.bat`**
2. Chọn **Run as administrator** → bấm **Yes**
3. Cửa sổ đen chạy một lúc rồi dừng lại. **Đọc phần "KIỂM TRA LẠI"** ở gần cuối:

```
Ten lich    : NguoiTruc
Trang thai  : Running
Tham so     : "D:\Workbuddy AI\AI AGENT FB\nguoi_truc.py"
So trigger  : 2
Tien trinh   : dang chay (PID ...)
```

4. **Ba dòng phải đúng** (sai dòng nào thì chụp màn hình gửi trợ lý):

| Dòng | Phải là |
|---|---|
| `Tham so` | kết thúc bằng `nguoi_truc.py"` — **có dấu nháy đóng** |
| `So trigger` | **`2`** |
| `Trang thai` | `Running` **và** có dòng `Tien trinh: dang chay` |

5. Bấm phím bất kỳ để đóng cửa sổ

> ✅ File này **tự xoá ba lịch cũ** (`BaoCaoMetaAds_08/12/17/22`) và lịch `NguoiTruc` cũ.
> Nhờ vậy bản cài cũ ở `D:\Workbuddy\2026-09-11-21-17-48` **sẽ không gửi báo cáo nữa** —
> không có chuyện hai hệ thống cùng gửi.

---

### 🔴 BƯỚC 5 — Nhắn thử bot

1. Mở **Telegram**, vào khung chat với bot **"Bot Báo Cáo Home❤️"**
2. Nhắn đúng một câu: `còn sống không?`

3. Bot phải trả lời kèm: máy nào, đã chạy bao lâu, hôm nay đã gửi mốc nào.

> ⚠️ **Phải nhắn SAU khi bước 4 chạy xong.** Người trực bỏ qua mọi tin nhắn đến trước lúc
> nó khởi động — nhắn trước là mất tin, **không phải lỗi**.

---

## PHẦN D — HAI CHUYỆN SẼ XẢY RA NGAY SAU KHI CÀI, ĐỪNG HOẢNG

1. **Đại sẽ nhận được MỘT báo cáo bù.** Hôm nay đã qua cả ba mốc 8h/12h/17h, nên Người trực
   gửi bù **một** báo cáo cho mốc gần nhất bị lỡ. Đây là đúng thiết kế, không phải lỗi.
2. **Từ mai trở đi chỉ còn ba báo cáo/ngày** — 8h, 12h, 17h. Mốc 22h đã bỏ.

**Muốn tắt hoàn toàn:** bấm `go-nguoi-truc.bat`.
**Kiểm tra sức khoẻ bất cứ lúc nào:** nhắn bot `còn sống không?` hoặc `token`.

---

## PHẦN E — MỘT VIỆC RIÊNG, KHÔNG THUỘC BƯỚC NÀO Ở TRÊN

Token Meta hiện **chỉ có quyền ĐỌC**, chưa có quyền GHI. Nghĩa là hệ thống hiện tại **chạy tốt
báo cáo**, nhưng sau này muốn làm "AI tự tắt camp" thì **bắt buộc phải xin lại token** có thêm
quyền `ads_management`.

Việc này **chưa gấp** — chỉ cần khi làm việc #3. Nhưng càng thử sớm càng tốt, vì nếu Meta
không cấp thì cả kế hoạch đó phải dừng.

---

## TÓM TẮT NHANH

```
ĐÃ XONG (trợ lý làm)
├── tải code mới nhất                       ✅
├── mang .env từ bản cài cũ sang            ✅
├── thêm REPORT_SLOTS=8,12,17               ✅
├── kiểm tra token Telegram + Meta          ✅
└── chạy thử toàn bộ luồng (không gửi)      ✅

ĐẠI LÀM (5 bước)
├── 1. Lấy chìa khoá AI ở aistudio.google.com/apikey
├── 2. Dán vào .env (bấm mo-file-env.bat) → Ctrl+S
├── 3. python test_gemini.py  → phải ra "HOAT DONG TOT"
├── 4. Chuột phải cai-dat-nguoi-truc.bat → Run as administrator
└── 5. Nhắn bot: còn sống không?

CÒN LẠI, KHÔNG GẤP
└── Xin token Meta có quyền ads_management (chỉ cần cho việc #3)
```

**Xong 5 bước trên là hệ thống chạy đủ: báo cáo tự gửi 3 lần/ngày + bot trả lời câu hỏi.**
