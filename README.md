# BÁO CÁO META ADS TỰ ĐỘNG → TELEGRAM

Hướng dẫn dành cho Đại (người không cần biết code).

---

## Hệ thống này làm gì

Mỗi ngày, tự động lấy số liệu quảng cáo Meta Ads và gửi báo cáo vào Telegram của bạn — **4 lần mỗi ngày**:

| Giờ | Nội dung báo cáo |
|---|---|
| 🌅 **8:00** | Tổng kết ngày hôm qua |
| ☀️ **12:00** | Kết quả từ 0h đến 12h hôm nay |
| 🌤️ **17:00** | Kết quả từ 0h đến 17h hôm nay |
| 🌙 **22:00** | Tổng kết cả ngày hôm nay |

---

## Cách cài đặt (chỉ làm 1 lần)

### Bước 1: Kiểm tra file `.env` đã điền token chưa

Mở file `.env`, đảm bảo 4 dòng này đã có giá trị:

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
META_ADS_ACCESS_TOKEN=...
META_AD_ACCOUNT_ID=...
```

### Bước 2: Bấm đúp vào file `cai-dat-lich.bat`

File này sẽ tự tạo 4 lịch trong Windows.

Bạn sẽ thấy thông báo:

```
[OK]  Moc 8:00 - da tao
[OK]  Moc 12:00 - da tao
[OK]  Moc 17:00 - da tao
[OK]  Moc 22:00 - da tao
```

**Xong.** Từ nay hệ thống tự chạy.

---

## Cách tắt

Bấm đúp vào file **`go-lich.bat`** → 4 lịch bị xóa, hệ thống ngừng gửi báo cáo.

---

## Cách chạy thử ngay (không cần chờ đến giờ)

**Bước 1 — Mở cửa sổ lệnh tại đúng thư mục dự án.**

PowerShell mặc định mở ở `C:\WINDOWS\System32` — **không phải** thư mục dự án. Cách nhanh nhất:

1. Mở **File Explorer**, vào thư mục dự án
2. Bấm vào **thanh địa chỉ** phía trên (chỗ ghi đường dẫn)
3. Xóa nội dung, gõ `powershell` rồi bấm **Enter**

→ Cửa sổ PowerShell mở ra đã ở đúng thư mục.

**Cách khác — dùng lệnh `cd`:**

```powershell
cd "D:\Workbuddy\2026-09-11-21-17-48"
```

Kiểm tra đầu dòng lệnh đã hiện đường dẫn dự án chưa:

```
PS D:\Workbuddy\2026-09-11-21-17-48>   ← đúng
```

**Bước 2 — Chạy báo cáo:**

```powershell
python report.py
```

Nếu báo lỗi `python is not recognized`, dùng đường dẫn đầy đủ:

```powershell
& "C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe" report.py
```

Kết quả sẽ được gửi vào Telegram ngay lập tức.

**Các tùy chọn khác:**

| Lệnh | Ý nghĩa |
|---|---|
| `python report.py` | Gửi báo cáo thật vào Telegram |
| `python report.py --dry` | Chạy thật nhưng KHÔNG gửi |
| `python report.py --mock 8` | Giả lập mốc 8h, không gửi |

---

## 📊 Dashboard xem báo cáo (file HTML)

Mỗi lần script chạy, nó **tự tạo thêm 1 file `dashboard.html`** bên cạnh báo cáo Telegram.

**Cách xem:**

1. Mở thư mục dự án.
2. Bấm đúp vào file **`dashboard.html`** → nó mở bằng trình duyệt (Chrome, Edge...).
3. Xem bảng số liệu đẹp, có màu — không cần cài gì thêm.

**Có gì trong đó:**

- 8 ô số liệu lớn: Chi tiêu, Lượt mua, CPR, Lượt thanh toán, Trò chuyện, Liên hệ mới, Đơn hàng, Bình luận.
- Khung bộ lọc đang áp dụng.
- 2 bảng xếp hạng: 🟢 Camp hiệu quả (top 5) và 🔴 Camp kém hiệu quả (top 5).
- Cột **CPR** tự đổi màu: 🟢 xanh = rẻ hơn mức trung bình, 🔴 đỏ = đắt hơn.

**Lưu ý:** Số liệu được **ghi sẵn** vào file lúc tạo — file này là **ảnh chụp (snapshot)**, không tự cập nhật. Muốn số mới, chạy lại script.

---

## ⚠️ Ba điều cần biết

### 1. Máy phải đang bật

Hệ thống chạy trên máy này. Nếu máy tắt đúng lúc 8h, báo cáo 8h sẽ không gửi.

**Cách khắc phục:**
- Bật máy trước các mốc giờ, hoặc để máy chạy thường xuyên.
- **Hoặc** bấm file **`bat-chay-bu.bat`** (chuột phải → Run as administrator) — sau đó Windows sẽ **tự chạy bù** báo cáo đã lỡ ngay khi máy được bật lại.

### 2. Token Meta Ads có thể hết hạn

Token Meta thường hết hạn sau một thời gian. Khi đó báo cáo sẽ báo lỗi.

**Dấu hiệu:** Telegram không thấy báo cáo, hoặc có tin nhắn lỗi.

**Cách sửa:** lấy token mới, dán lại vào `.env`.

### 3. File `.env` không được đưa lên GitHub

File này chứa token. Nó đã được `.gitignore` chặn rồi — nhưng đừng tự ý bỏ chặn.

---

## Cấu trúc file trong dự án

```
📁 D:\Workbuddy\2026-09-11-21-17-48\
│
├── 📄 .env                      ← Token của bạn (BÍ MẬT, không đưa lên mạng)
├── 📄 .env.example              ← Bản mẫu cho máy khác
├── 📄 .gitignore                ← Danh sách file cấm đưa lên GitHub
│
├── 📄 report.py                 ← Script chính (chạy báo cáo)
├── 📄 dashboard.py              ← Bộ tạo file dashboard.html
├── 📄 dashboard.html            ← Dashboard xem báo cáo (tự tạo lại mỗi lần chạy)
├── 📄 doi-token-60-ngay.py      ← Công cụ gia hạn token Meta lên 60 ngày
├── 📄 cai-dat-lich.bat          ← Bấm để BẬT tự động
├── 📄 go-lich.bat               ← Bấm để TẮT tự động
├── 📄 bat-chay-bu.bat           ← Bấm để bật "chạy bù khi lỡ giờ" (cần Admin)
├── 📄 logs/baocao.log           ← Nhật ký chạy (xem khi cần chẩn đoán)
│
├── 📄 test_telegram.py          ← Test token Telegram
├── 📄 test_meta.py              ← Test kết nối Meta
├── 📄 test_gemini.py            ← Test key AI (chưa dùng)
├── 📄 list_actions.py           ← Công cụ dò tên chỉ số
├── 📄 find_payment.py           ← Công cụ dò chỉ số thanh toán
│
└── 📄 HUONG-DAN-DIEN-TOKEN.md   ← Hướng dẫn lấy token
└── 📄 HUONG-DAN-MAY-CONG-TY.md  ← Hướng dẫn cài lên máy thứ hai
```

---

## Những chỉ số được báo cáo

| Chỉ số trong báo cáo | Lấy từ Meta |
|---|---|
| Số tiền đã chi tiêu | `spend` |
| Lượt bắt đầu cuộc trò chuyện | `messaging_conversation_started_7d` |
| Người liên hệ nhắn tin mới | `messaging_first_reply` |
| Đơn đặt hàng đã tạo | `messaging_order_created_v2` |
| Lượt mua | `onsite_conversion.purchase` |
| Lượt thanh toán | `initiate_checkout` |
| Bình luận về bài viết | `post_net_comment` |

---

## Xử lý sự cố

| Vấn đề | Cách xử lý |
|---|---|
| Không nhận được báo cáo | Kiểm tra máy có bật không; mở `logs/baocao.log` xem có dòng nào không |
| `logs/baocao.log` trống hoàn toàn | Lịch chưa được cài → bấm `cai-dat-lich.bat` |
| Telegram báo "Token Meta đã HẾT HẠN" | Làm theo `HUONG-DAN-DIEN-TOKEN.md` → mục `META_ADS_ACCESS_TOKEN` |
| Báo cáo ghi "LOI lay du lieu Meta" | Token Meta hết hạn → lấy token mới |
| Báo cáo ghi "LOI GUI TELEGRAM" | Kiểm tra token Telegram và Chat ID |
| Số liệu ra 0 hết | Kiểm tra bộ lọc `dainq` có khớp campaign nào không |
| `dashboard.html` mở ra trắng/trống | Chạy lại `python report.py --dry` để tạo lại file |

---

## 🔔 Hệ thống tự báo khi có lỗi

Từ nay nếu có lỗi, bạn sẽ **nhận được tin nhắn Telegram cảnh báo** — không còn im lặng nữa.

Ví dụ khi token hết hạn:

```
⚠️ BÁO CÁO META ADS GẶP LỖI

Hệ thống không lấy được số liệu.
Lý do Meta trả về:
Error validating access token: Session has expired...

Cách xử lý:
→ Token Meta đã HẾT HẠN.
→ Cần lấy token mới rồi dán lại vào file .env.
```

**Nhật ký:** Mọi lần chạy đều được ghi vào `logs/baocao.log`.

```
[2026-09-12 08:08:49] BAT DAU - moc 8h, khoang 2026-09-11 -> 2026-09-11
[2026-09-12 08:08:50] Da gui canh bao loi vao Telegram
```

File này là **cách nhanh nhất để biết** lịch có chạy hay không. Nếu nó trống → lịch chưa được cài.

---

## ⏰ Token Meta sống bao lâu?

| Loại token | Thời hạn | Ghi chú |
|---|---|---|
| Token lấy trực tiếp từ Graph API Explorer | **1–2 giờ** | ❌ Không dùng được cho hệ thống |
| Token đã đổi bằng `doi-token-60-ngay.py` | **60 ngày** | ✅ Dùng cái này |

**Cách gia hạn:** làm theo `HUONG-DAN-DIEN-TOKEN.md` → mục `META_ADS_ACCESS_TOKEN`.

Hệ thống sẽ **nhắn tin cảnh báo** khi token hết hạn, nên bạn không cần tự nhớ ngày.

---

## Ghi chú kỹ thuật (cho người biết code)

- **Python**: `C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe`
- **Không cần thư viện ngoài** — script dùng `urllib` có sẵn của Python.
- **Meta Graph API**: `v21.0`
- **Task Scheduler**: 4 task tên `BaoCaoMetaAds_8/12/17/22`, chạy DAILY.
- **Dashboard**: `dashboard.py` sinh HTML tĩnh, không dùng thư viện ngoài, không cần server. `report.py` gọi `compute_stats()` **một lần duy nhất** rồi dùng chung cho cả text lẫn HTML (tránh gọi API 2 lần).

### ⚠️ Lưu ý quan trọng khi sửa script

Meta trả về **nhiều tên action cho cùng một hành động** (`omni_purchase`, `onsite_web_purchase`, `onsite_app_purchase`, `onsite_conversion.purchase`...). **Cộng hết sẽ bị đếm gấp đôi.** Chỉ dùng một tên duy nhất cho mỗi chỉ số.
