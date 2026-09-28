# BÁO CÁO META ADS TỰ ĐỘNG → TELEGRAM

Hướng dẫn dành cho Đại (người không cần biết code).

---

## 🚀 Mới sang máy khác? Đọc file này trước

👉 **`HANDOFF.md`** — sổ bàn giao, chứa toàn bộ bối cảnh dự án.

Khi làm việc trên máy mới, chỉ cần nói với trợ lý:

> **"Đọc file HANDOFF.md trong thư mục dự án và giúp tôi làm tiếp."**

File đó có đủ: dự án là gì, đã làm được gì, còn việc gì, và những điều bắt buộc phải nhớ.

---

## Hệ thống này làm gì

Mỗi ngày, tự động lấy số liệu quảng cáo Meta Ads và gửi báo cáo vào Telegram của bạn — **3 lần mỗi ngày**:

| Giờ | Nội dung báo cáo |
|---|---|
| 🌅 **8:00** | Tổng kết ngày hôm qua |
| ☀️ **12:00** | Kết quả từ 0h đến 12h hôm nay |
| 🌤️ **17:00** | Kết quả từ 0h đến 17h hôm nay |

> 📌 **Mốc 22h đã bỏ trên máy công ty từ 28/09/2026.** Lý do: đếm trong `logs/baocao.log` **của máy
> công ty** (14/09 – 28/09) thì mốc 8h có 51 dòng, 12h có 37, 17h có 27, còn **mốc 22h có 0 dòng** —
> trên máy này nó chưa từng báo cáo một lần nào. Khi máy thức dậy buổi sáng, lịch 22h chạy bù và
> tự đoán ra mốc 8h — gây ra báo cáo trùng.
> (Máy nhà trước đây vẫn chạy được mốc 22h — xem ghi chép ngày 12/09 ở phần "Ba điều cần biết".)

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

### Bước 2: Chuột phải `cai-dat-lich.bat` → **Run as administrator**

> ⚠️ **Phải chạy bằng quyền Administrator.** File này làm **hai** việc: tạo 3 lịch, và đặt luôn
> 3 thiết lập quan trọng (chạy bù khi lỡ giờ, tự thức máy để chạy đúng giờ, cho phép chạy khi
> dùng pin). Nếu chạy mà không có quyền Admin, lịch vẫn được tạo nhưng **thiếu 3 thiết lập đó**,
> và file sẽ in cảnh báo rõ ràng.

File này sẽ tự tạo 3 lịch trong Windows.

Bạn sẽ thấy thông báo:

```
[OK]  Moc 8:00 - da tao
[OK]  Moc 12:00 - da tao
[OK]  Moc 17:00 - da tao
```

Ngay sau đó là phần kiểm tra thiết lập — **cả ba dòng đều phải ghi `True`**:

```
BaoCaoMetaAds_08 : chay bu=True  tu thuc=True
BaoCaoMetaAds_12 : chay bu=True  tu thuc=True
BaoCaoMetaAds_17 : chay bu=True  tu thuc=True
```

Nếu thấy `False` ở bất kỳ dòng nào, nghĩa là file chưa được chạy bằng quyền Admin — chạy lại.

> ⚠️ **Chạy file này từ đúng thư mục dự án.** `cai-dat-lich.bat` tự lấy đường dẫn `report.py`
> từ chính thư mục chứa nó, nên phải bấm nó ở thư mục có `.env` và `logs/`. Nếu bấm từ một bản
> code khác, lịch đang chạy thật sẽ bị trỏ sang bản code đó.
>
> ⚠️ **Dòng `[OK]` của `schtasks` chỉ chứng tỏ lệnh tạo lịch không báo lỗi**, chứ không chứng
> minh tham số truyền vào đã đúng. Phải kiểm riêng phần tham số — cách kiểm `--slot` nằm ở mục
> "Kiểm chứng `--slot` đã vào lịch chưa" trong phần Ghi chú kỹ thuật.

**Xong.** Từ nay hệ thống tự chạy.

---

## Cách tắt

Bấm đúp vào file **`go-lich.bat`** → 3 lịch bị xóa, hệ thống ngừng gửi báo cáo.

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

Mỗi lần script chạy, nó **tự tạo thêm 1 file `dashboard.html`** và **gửi kèm vào Telegram** dưới dạng file đính kèm (tên dạng `baocao_12h_13-09-2026.html`).

**Cách xem — 2 cách:**

**Cách A — Trên Telegram (mới):**
1. Mở Telegram, vào chat với bot báo cáo.
2. Thấy tin nhắn chữ (số liệu) → ngay dưới là **file HTML đính kèm**.
3. Bấm vào file → tải về → mở bằng trình duyệt (Chrome, Edge...).

**Cách B — Trên máy (cũ):**
1. Mở thư mục dự án.
2. Bấm đúp vào file **`dashboard.html`** → nó mở bằng trình duyệt.
3. Xem bảng số liệu đẹp, có màu — không cần cài gì thêm.

**Có gì trong đó:**

- 8 ô số liệu lớn: Chi tiêu, Lượt mua, CPR, Lượt thanh toán, Trò chuyện, Liên hệ mới, Đơn hàng, Bình luận.
- Khung bộ lọc đang áp dụng.
- 2 bảng xếp hạng: 🟢 Camp hiệu quả (top 5) và 🔴 Camp kém hiệu quả (top 5).
- Cột **CPR** tự đổi màu: 🟢 xanh = rẻ hơn mức trung bình, 🔴 đỏ = đắt hơn.

**Lưu ý:** Số liệu được **ghi sẵn** vào file lúc tạo — file này là **ảnh chụp (snapshot)**, không tự cập nhật. Muốn số mới, chạy lại script.

---

## 🗂️ Lịch sử số liệu (file `logs/lich-su.json`)

Mỗi lần chạy, hệ thống ghi lại số liệu vào `logs/lich-su.json`, giữ **180 ngày**.

**Để làm gì:** trước đây `dashboard.html` bị ghi đè mỗi lần chạy nên không giữ lại số cũ.
Không có số cũ thì không thể trả lời những câu như *"tuần này so với tuần trước thế nào"*.
File này là nền cho các tính năng so sánh sẽ làm sau.

**Có gì trong đó:** mỗi ngày một bản ghi, gồm tổng 7 chỉ số và danh sách toàn bộ campaign.
Bản ghi của báo cáo 8h — và của báo cáo 22h, **nếu máy đó có bật mốc này** — là bản **đầy đủ cả ngày**;
bản của 12h và 17h là bản **một phần**.
Khi cả hai loại cùng có, bản đầy đủ luôn thắng.

**File này không lên GitHub** — nó nằm trong `logs/`, đã bị `.gitignore` chặn.

---

## ⚠️ Ba điều cần biết

### 1. Máy phải đang bật (hoặc đang ngủ)

Hệ thống chạy trên máy này. Nếu máy **tắt** hoặc **ngủ** đúng lúc 8h, báo cáo 8h có thể bị trễ.

**Cách khắc phục:**

1. **Đã tự động.** Từ 28/09/2026, `cai-dat-lich.bat` đặt luôn 3 thiết lập này khi tạo lịch — miễn
   là chạy bằng quyền Admin. Nếu vì lý do nào đó chúng bị mất, bấm **`bat-chay-bu.bat`**
   (chuột phải → Run as administrator) để đặt lại. File đó bật:
   - **Tự chạy bù** báo cáo đã lỡ ngay khi máy được bật lại.
   - **Tự thức máy** để chạy báo cáo đúng giờ.
   - **Cho phép chạy khi dùng pin.**
2. Bấm file **`bat-danh-thuc-may.bat`** (chuột phải → Run as administrator) — **một lần duy nhất**.
   File này bật "Allow wake timers" ở mức Windows, khác với cờ `WakeToRun` của từng lịch.
   Cần cả hai thì Windows mới thức được máy.

**Ngoài ra, để báo cáo đến đúng giờ:**
- **Cắm sạc** máy thường xuyên (đừng để pin cạn).
- **Đừng tắt máy** — chỉ để máy ngủ là đủ.
- Trong khung **8h–17h**, hạn chế để máy ngủ quá sâu.

> 📌 **Thực tế đã gặp:**
> - **12/09:** Máy ngủ lúc 12h → báo cáo 12h trễ; khi máy "thức" lúc 14:27, tính năng chạy bù **tự gửi bù**. Mốc 17h, 22h chạy **đúng giờ**.
> - **13/09:** Máy ngủ/ngủ đông suốt sáng → lỡ mốc 8h và 12h; máy thức lúc 14:05. Nguyên nhân: **"Allow wake timers" bị tắt** → cần chạy `bat-danh-thuc-may.bat`.

> ⚠️ **Giới hạn:** Nếu lỡ NHIỀU mốc, khi máy bật lại hệ thống chỉ gửi bù **mốc gần nhất** (ví dụ bật lúc 14h chỉ gửi mốc 12h). Mốc 8h có thể không được gửi bù.

> 🛡️ **Chống trùng (từ 14/09/2026):** Mỗi mốc giờ chỉ gửi **1 lần trong ngày**. Nhưng cơ chế này chỉ là **lưới an toàn**: nó kiểm tra sổ rồi mới ghi, nên khi nhiều lịch chạy bù **cùng lúc** thì cả loạt đều lọt qua — đã xảy ra thật, sáng 28/09/2026 gửi 4 tin trùng. Tham số `--slot` (xem mục "Tham số `--slot`" ở phần Ghi chú kỹ thuật) chặn được những tin **giống hệt nhau** — loại do mọi lịch đều đoán ra cùng một mốc. Nhưng buổi sáng chạy bù, lịch 12h và lịch 17h vẫn có thể báo **cùng một khoảng** và trông như trùng nhau — chuyện này chỉ chữa dứt điểm ở Giai đoạn 2 (tiến trình thường trú). Muốn gửi lại chủ động: `python report.py --force`.

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
├── 📄 kiem-tra-token.py         ← Kiểm tra CẢ 2 nhóm token + token Meta còn sống bao lâu
├── 📄 cai-dat-lich.bat          ← Bấm để BẬT tự động
├── 📄 go-lich.bat               ← Bấm để TẮT tự động
├── 📄 bat-chay-bu.bat           ← Bấm để bật "chạy bù khi lỡ giờ" (cần Admin)
├── 📄 bat-danh-thuc-may.bat     ← Bấm để cho phép Windows tự thức máy chạy báo cáo (cần Admin)
├── 📄 logs/baocao.log           ← Nhật ký chạy (xem khi cần chẩn đoán)
│
├── 📄 test_telegram.py          ← Test token Telegram
├── 📄 test_meta.py              ← Test kết nối Meta
├── 📄 test_gemini.py            ← Test key AI (chưa dùng)
├── 📄 list_actions.py           ← Công cụ dò tên chỉ số
├── 📄 find_payment.py           ← Công cụ dò chỉ số thanh toán
│
├── 📄 HUONG-DAN-DIEN-TOKEN.md   ← Hướng dẫn lấy token
├── 📄 HUONG-DAN-MAY-NHA.md      ← Hướng dẫn cập nhật MÁY NHÀ (đọc khi ở nhà)
├── 📄 HUONG-DAN-MAY-CONG-TY.md  ← Hướng dẫn cài lên máy thứ hai
└── 📄 HANDOFF.md                ← Sổ bàn giao cho máy khác (đọc file này trước khi sang máy mới)
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
- **Task Scheduler**: 3 task tên `BaoCaoMetaAds_08/12/17`, chạy DAILY.
- **Dashboard**: `dashboard.py` sinh HTML tĩnh, không dùng thư viện ngoài, không cần server. `report.py` gọi `compute_stats()` **một lần duy nhất** rồi dùng chung cho cả text lẫn HTML (tránh gọi API 2 lần).

### ⚠️ Lưu ý quan trọng khi sửa script

Meta trả về **nhiều tên action cho cùng một hành động** (`omni_purchase`, `onsite_web_purchase`, `onsite_app_purchase`, `onsite_conversion.purchase`...). **Cộng hết sẽ bị đếm gấp đôi.** Chỉ dùng một tên duy nhất cho mỗi chỉ số.

### Tham số `--slot` — chống gửi trùng báo cáo

Mỗi lịch Windows gọi `report.py` kèm mốc giờ của chính nó:

```
python report.py --slot 08
python report.py --slot 12
python report.py --slot 17
```

**Vì sao cần:** trước 28/09/2026, lịch không truyền mốc giờ, nên `report.py` phải tự đoán
mốc gần nhất với giờ hiện tại. Khi máy ngủ qua nhiều mốc, Windows cho nhiều lịch chạy bù
**cùng lúc** — tất cả cùng đoán ra một mốc và gửi ra nhiều báo cáo giống hệt nhau.
Đã xảy ra thật: sáng 28/09/2026 lúc 08:26 gửi 4 tin trùng + 4 file HTML.

**Lưu ý:** cơ chế chống trùng cũ (`logs/da_gui.json`) vẫn còn, nhưng chỉ là lưới an toàn —
nó kiểm tra rồi mới ghi, nên khi nhiều tiến trình chạy đồng thời thì cả loạt đều lọt qua.
`--slot` chặn được những tin **giống hệt nhau** (do mọi lịch đoán ra cùng một mốc).

**Còn sót lại:** vào buổi sáng chạy bù, `determine_period()` cho mốc 12h và 17h cùng ra
`(hôm nay, hôm nay)`, nên hai lịch này có thể báo **cùng một khoảng** và trông như trùng
nhau — số tin trùng giảm từ 4 xuống 3, chứ không về 0. Việc này được chữa dứt điểm ở
Giai đoạn 2 (tiến trình thường trú).

**Không có `--slot`** (chạy tay): script vẫn đoán mốc gần nhất như cũ, để tương thích ngược.

### Kiểm chứng `--slot` đã vào lịch chưa

Dòng `[OK]` khi tạo lịch **không** chứng minh tham số đã đúng — nó chỉ nói `schtasks` không
báo lỗi. Kiểm riêng bằng PowerShell (`schtasks.exe` có thể bị chính sách công ty chặn):

```powershell
foreach ($n in @('BaoCaoMetaAds_08','BaoCaoMetaAds_12','BaoCaoMetaAds_17')) {
  $t = Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue
  if (-not $t) { Write-Host "$n : KHONG TIM THAY"; continue }
  foreach ($a in $t.Actions) { Write-Host ($n + " Args=" + $a.Arguments) }
}
```

**Điều kiện đạt:** `Args` của `BaoCaoMetaAds_08` phải chứa `--slot 08`, của `BaoCaoMetaAds_12`
phải chứa `--slot 12`, của `BaoCaoMetaAds_17` phải chứa `--slot 17`.
