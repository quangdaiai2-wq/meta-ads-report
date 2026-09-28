# QUY TRÌNH — 2 MÁY: NHÀ + CÔNG TY

📌 Dành cho Đại (không cần biết code). Đọc file này để tự làm ở công ty mà không cần nhờ AI.

---

## 🎯 TÓM TẮT QUAN TRỌNG

✅ **Sau khi setup 1 lần, hệ thống TỰ ĐỘNG. Đại KHÔNG cần làm gì hàng ngày.**

- Báo cáo tự chạy lúc **8h, 12h, 17h** mỗi ngày.
- `git pull` **KHÔNG bắt buộc mỗi ngày** — chỉ cần khi có cập nhật code (AI sẽ báo trước).

---

## 🔑 NGUYÊN TẮC

1. 2 máy chạy **SONG SONG**, mỗi máy 1 bot Telegram riêng.
2. Code đồng bộ qua GitHub.
3. `.env` (chứa token) **KHÔNG lên GitHub** → chuyển giữa 2 máy bằng **USB**.
4. Nếu máy tắt đúng giờ báo cáo, Windows sẽ **tự chạy bù** khi bật lại (đã bật sẵn).

---

## 🏢 LẦN ĐẦU Ở CÔNG TY (Thứ 2) — LÀM 1 LẦN DUY NHẤT

**Bước 1 — Mở cửa sổ lệnh tại thư mục sẽ chứa dự án** (xem MẸO cuối file).

**Bước 2 — Tải code về (lần đầu dùng `clone`, không dùng `pull`):**

```powershell
git clone https://github.com/quangdaiai2-wq/meta-ads-report.git
cd meta-ads-report
```

**Bước 3 — Tạo file `.env` từ mẫu + điền token:**

```powershell
copy .env.example .env
```

Mở `.env` bằng Notepad, điền:
- `TELEGRAM_BOT_TOKEN` = token bot **MỚI** của công ty
- `TELEGRAM_CHAT_ID` = chat id của bạn
- `META_ADS_ACCESS_TOKEN` = **copy từ máy nhà** (mang qua USB)

**Bước 4 — Tạo lịch tự động:** bấm đúp file `cai-dat-lich.bat`.

**Bước 5 — Bật chạy bù:** chuột phải `bat-chay-bu.bat` → **Run as administrator**.

**Bước 6 — Thử chạy:** `python report.py`

→ **Xong. Từ đây hệ thống tự chạy, Đại đi uống cà phê ☕.**

---

## 🔄 HÀNG NGÀY SAU KHI ĐÃ SETUP

**Không cần làm gì.** Máy bật là báo cáo tự chạy.

Chỉ `git pull` KHI:
- AI báo *"có bản cập nhật, chạy git pull"*, hoặc
- Đại muốn chắc chắn có code mới (tuỳ chọn, ví dụ 1 lần/tuần):

```powershell
git pull
```

---

## 📤 KHI NÀO CẦN `git push`?

Chỉ khi **AI hoặc bạn sửa code**. Bảo AI: *"đẩy code lên GitHub giúp tôi."*
Hoặc tự chạy (copy-paste):

```powershell
git add -A
git commit -m "cap nhat"
git push
```

> 💡 Bình thường Đại không cần bước này — để AI làm sau khi sửa xong.

---

## 🔄 GIA HẠN TOKEN META (máy nhà: sau 10/11/2026 — máy công ty: sau )

1. Trên máy đang dùng, chạy: `python doi-token-60-ngay.py`
2. **Copy file `.env` sang máy kia bằng USB** (vì `.env` không lên GitHub).
3. Bảo AI đẩy code nếu có đổi script.

> ⚠️ Hệ thống sẽ **tự nhắn cảnh báo** vào Telegram khi token hết hạn — Đại không cần tự nhớ ngày.

---

## 🔍 KIỂM TRA BÁO CÁO CÓ CHẠY KHÔNG

Chạy thử ngay:

```powershell
python report.py
```

Xem nhật ký:

```powershell
type logs\baocao.log
```

> 📄 Hoặc mở `logs/baocao.log` bằng Notepad. Thấy dòng `THANH CONG` là ok.

---

## 💡 MẸO: MỞ CỬA SỔ LỆNH TẠI ĐÚNG THƯ MỤC

**Cách 1 (nhanh nhất):** File Explorer → vào thư mục dự án → bấm thanh địa chỉ → xóa hết, gõ `powershell` → Enter.

**Cách 2:** `cd "đường dẫn thư mục dự án"` (tại công ty thay bằng đường dẫn thực tế nơi bạn clone).

---

## 🆘 NẾU GẶP LỖI

| Triệu chứng | Xử lý |
|---|---|
| `git clone` / `git pull` báo lỗi | Nhờ AI xử lý, **đừng tự sửa** |
| Không nhận được báo cáo | Máy có bật không? Mở `logs/baocao.log` xem |
| Telegram báo token Meta hết hạn | Làm mục "GIA HẠN TOKEN META" ở trên |

---

*File này nằm trong thư mục dự án (`QUY-TRINH-HANG-NGAY.md`) và đã gửi vào Telegram. Sau setup 1 lần, mọi thứ tự động — không cần làm hàng ngày.*
