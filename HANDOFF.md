# HANDOFF — SỔ BÀN GIAO CÔNG VIỆC

**Cập nhật lần cuối:** 14/09/2026, 08:30 (giờ Việt Nam)

---

## 📌 CÁCH DÙNG FILE NÀY

**Nếu bạn là trợ lý AI đang đọc file này:** Người dùng (Đại) vừa chuyển sang một máy tính khác. Đây là bối cảnh đầy đủ của dự án. Hãy đọc hết file trước khi làm bất cứ điều gì.

**Nếu bạn là Đại:** Khi sang máy khác, chỉ cần nói với trợ lý ở đó:

> **"Đọc file HANDOFF.md trong thư mục dự án và giúp tôi làm tiếp."**

---

## 🎯 DỰ ÁN LÀ GÌ

Hệ thống tự động lấy số liệu **Meta Ads** và gửi báo cáo vào **Telegram**, chạy theo lịch **4 mốc mỗi ngày**: 8h, 12h, 17h, 22h.

Chủ dự án: **Đại** — người không biết lập trình, cần hướng dẫn từng bước.

---

## ✅ TRẠNG THÁI HIỆN TẠI

### Đã hoàn thành (trên máy nhà)

| # | Hạng mục | Chi tiết |
|---|---|---|
| 1 | Token Meta 60 ngày | Hết hạn **10/11/2026** |
| 2 | 4 lịch tự động | Tên `BaoCaoMetaAds_08/12/17/22` |
| 3 | Chạy bù khi lỡ giờ | Đã bật `StartWhenAvailable` cho cả 4 lịch |
| 4 | Dashboard HTML | Tự tạo lại mỗi lần chạy |
| 5 | Đẩy code lên GitHub | 4 bản ghi, nhánh `main`, kho riêng tư |
| 6 | Cảnh báo lỗi qua Telegram | Tự gửi tin khi có sự cố |

### Đã hoàn thành (trên máy công ty — ngày 14/09/2026)

| # | Hạng mục | Chi tiết |
|---|---|---|
| 1 | Kéo code từ GitHub | Về `D:\Buddy Work AI\2026-09-14-07-50-57` |
| 2 | Token Meta 60 ngày | Hết hạn **** (xem mục 2 bên dưới — KHÁC máy nhà) |
| 3 | Bot Telegram riêng | `@boongbonbap_QuangDai_bot` ("Bot Báo Cáo Company👍") |
| 4 | 4 lịch tự động | Đã xác minh độc lập bằng cách đọc lịch trong Windows |
| 5 | Chạy bù + đánh thức máy | Đã bật, và "Allow wake timers" đã chuyển sang Enable |
| 6 | Chạy thử thật | Đã gửi báo cáo ngày 13/09 vào Telegram thành công |

### Chưa làm

- ⏳ **Máy nhà chưa cập nhật code mới** — cần `git pull` để nhận 3 bản cập nhật ngày 14/09.
  👉 **Hướng dẫn từng bước: xem file `HUONG-DAN-MAY-NHA.md`**

---

## 🖥️ VIỆC CẦN LÀM TRÊN MÁY CÔNG TY

👉 **Hướng dẫn đầy đủ 7 bước: xem file `HUONG-DAN-MAY-CONG-TY.md`**

Tóm tắt nhanh:

```
1. Kiểm tra máy có Python chưa (cài nếu chưa có)
2. git clone https://github.com/quangdaiai2-wq/meta-ads-report.git
3. copy .env.example .env
4. Điền token bot Telegram MỚI + copy token Meta từ máy nhà
5. Bấm cai-dat-lich.bat
6. Bấm bat-chay-bu.bat (chuột phải → Run as administrator)
7. Chạy python report.py để kiểm tra
```

---

## 🔒 QUYẾT ĐỊNH ĐÃ CHỐT

| Vấn đề | Quyết định |
|---|---|
| Số máy chạy | **Cả 2 máy chạy song song** (máy nhà + máy công ty) — để dự phòng |
| Bot Telegram | **Mỗi máy dùng bot riêng** — máy công ty dùng bot mới |
| Cách đồng bộ code | GitHub, kho riêng tư `meta-ads-report` |
| File bí mật | `.env` **không** đẩy lên GitHub; chuyển giữa các máy bằng **USB** |
| Token Meta | Dùng chung cho cả 2 máy (không giới hạn số máy) |
| Bộ lọc báo cáo | Tên campaign chứa `dainq`; loại trừ `thuonghieu`, `thương hiệu`, `Brand` |

---

## ⚠️ NHỮNG ĐIỀU BẮT BUỘC NHỚ

### 1. Bot Telegram mới phải được bấm Start trước

Mở Telegram → tìm bot mới → bấm **Start**.
Nếu không, bot không gửi được tin → lỗi **403**.

### 2. Token Meta — HAI MÁY HẾT HẠN KHÁC NGÀY NHAU

Từ 14/09/2026, hai máy dùng **hai token khác nhau** (vì máy công ty phải đổi token
ngắn hạn sang token 60 ngày):

| Máy | Token hết hạn |
|---|---|
| Máy nhà | **10/11/2026** |
| Máy công ty | **** |

⇒ **Không còn chuyện "cả hai máy cùng ngừng hoạt động"** như tài liệu cũ ghi.
Máy nhà sẽ hết hạn trước 3 ngày. Thực ra điều này tốt hơn: khi máy nhà báo lỗi, bạn còn
3 ngày để xử lý trước khi máy công ty cũng tới hạn.

Cần lấy token mới thì làm theo `HUONG-DAN-DIEN-TOKEN.md`, rồi copy sang máy kia.

### Cảnh báo token đi đâu?

Mỗi máy gửi qua **bot Telegram riêng của máy đó** — `report.py` đọc `TELEGRAM_BOT_TOKEN`
trong `.env` của chính nó. Nên máy nhà → khung chat **bot Home**, máy công ty → **bot Company**.
Hai máy không lẫn vào nhau.

Có **2 loại** cảnh báo:

| Loại | Khi nào | Nội dung |
|---|---|---|
| 🟡 Cảnh báo sớm | Token còn dưới **7 ngày** | Nằm ở **đầu** mỗi báo cáo (thêm ngày 14/09/2026) |
| 🔴 Báo lỗi | Token **đã chết**, lần chạy thất bại | Tin nhắn riêng, nội dung tuỳ lỗi Meta trả về |

⚠️ **Giới hạn:** cả hai loại đều chỉ gửi được khi **có một lần chạy báo cáo**. Máy tắt hoặc
đăng xuất Windows đúng lúc đó ⇒ **không có cảnh báo nào**. Đừng phụ thuộc hoàn toàn vào cảnh báo.

Ngưỡng cảnh báo sớm đổi được ở dòng `NGUONG_CANH_BAO_NGAY = 7` trong `report.py`.

> ⚠️ **BẮT BUỘC: sau khi lấy token mới, phải kiểm HẠN của nó.**
> Token lấy trực tiếp từ Graph API Explorer chỉ sống **1–2 giờ**. Đã gặp thật ngày
> 14/09/2026: token chỉ còn sống **1 giờ 44 phút** mà `test_meta.py` vẫn báo ĐẠT và lấy
> được dữ liệu bình thường — vì bài test đó chỉ kiểm "token còn sống không", chứ không
> kiểm "còn sống bao lâu".
>
> Phải: chạy `python doi-token-60-ngay.py` để đổi sang 60 ngày, rồi hỏi thẳng Meta bằng
> `debug_token` (trường `expires_at`) để xác nhận.

### 3. Chuyển file `.env` giữa các máy bằng USB

❌ **KHÔNG** gửi qua Telegram / Zalo / email — đó là gửi mật khẩu qua mạng.

### 4. Không đẩy `.env` lên GitHub

File `.gitignore` đã chặn sẵn. **Đừng tự ý bỏ chặn.**

### 5. Máy công ty cần Python

File `cai-dat-lich.bat` **tự dò Python**. Nếu không tìm thấy, nó sẽ báo lỗi và hướng dẫn cách cài.

---

## 📁 CẤU TRÚC FILE QUAN TRỌNG

| File | Vai trò |
|---|---|
| `report.py` | **Script chính** — lấy số liệu Meta, gửi Telegram |
| `dashboard.py` | Tạo file `dashboard.html` xem báo cáo |
| `doi-token-60-ngay.py` | Gia hạn token Meta lên 60 ngày |
| `kiem-tra-token.py` | 🔍 **Kiểm tra token** — cả Telegram lẫn Meta, và token Meta **còn sống bao lâu**. Chạy sau MỖI lần lấy token mới. Không gửi tin nhắn, không in token đầy đủ. |
| `cai-dat-lich.bat` | Bật 4 lịch tự động |
| `go-lich.bat` | Tắt 4 lịch |
| `bat-chay-bu.bat` | Bật chạy bù khi lỡ giờ (cần quyền Admin) |
| `.env` | 🔐 **BÍ MẬT** — chứa token. Không đẩy lên GitHub |
| `.env.example` | File mẫu (an toàn để đẩy lên) |
| `logs/baocao.log` | **Nhật ký chạy** — xem đầu tiên khi có sự cố |
| `HUONG-DAN-MAY-CONG-TY.md` | Hướng dẫn cài máy thứ hai |
| `HUONG-DAN-MAY-NHA.md` | Hướng dẫn **cập nhật máy nhà** — đọc khi về nhà (git pull + kiểm token) |
| `HUONG-DAN-DIEN-TOKEN.md` | Hướng dẫn lấy token từng bước |
| `README.md` | Hướng dẫn sử dụng chung |

---

## 🔧 GHI CHÚ KỸ THUẬT CHO TRỢ LÝ AI

### Cách chạy
```bash
python report.py            # chạy thật, gửi Telegram
python report.py --dry      # chạy thật, không gửi
python report.py --mock 12  # giả lập mốc 12h, không gửi
```

### Thông số
- **Python thuần** — không cần thư viện ngoài (`urllib`, `json`, `argparse`)
- **Meta Graph API v21.0**
- Lịch Windows: `BaoCaoMetaAds_08`, `_12`, `_17`, `_22`

### BẢN SỬA NGÀY 14/09/2026 — `report.py` gọi Meta API 1 lần thay vì 2

**Vấn đề cũ:** `report.py` gọi `compute_stats()` **hai lần** cho mỗi lần chạy — một lần để
dựng báo cáo chữ, một lần nữa để dựng dashboard HTML. Trong khi `README.md` và chú thích
trong code đều ghi "chỉ gọi một lần". Hệ quả thật:

- Tốn **gấp đôi hạn mức gọi Meta API** mỗi lần chạy (vượt hạn mức là bị Meta chặn tạm).
- Hai lần gọi cách nhau vài giây, mà số liệu quảng cáo thay đổi liên tục ⇒ **tin nhắn
  Telegram và file HTML đính kèm có thể ghi hai con số khác nhau** cho cùng một chỉ số.

**Đã sửa:** hàm dựng báo cáo giờ nhận `stats` từ ngoài vào —
`build_report(env, stats, period_text)` — thay vì tự gọi lại Meta. `main()` tính **một lần
duy nhất** rồi dùng chung cho cả hai đầu ra. Dọn luôn 3 tham số thừa và 1 biến chết (`top_n`).

**Đã kiểm chứng:** cú pháp sạch · chỉ còn 1 chỗ gọi API · chạy thử với số liệu giả cho ra
đúng định dạng tiền Việt và số liệu khớp giữa tin nhắn với HTML · chạy thật thành công,
thời gian giảm từ 12 giây xuống 5 giây.

> ⚠️ **Máy nhà vẫn đang chạy bản CŨ** (2 lần gọi API) cho tới khi `git pull`.

### ⚠️ BẪY QUAN TRỌNG NHẤT — đừng để mất

Meta trả về **NHIỀU TÊN cho CÙNG một hành động**: `omni_purchase`, `onsite_web_purchase`, `onsite_app_purchase`, `onsite_conversion.purchase` đều phản ánh **cùng một số**.

**Cộng hết sẽ bị ĐẾM GẤP ĐÔI.** Chỉ dùng **một tên duy nhất** cho mỗi chỉ số.

Tên đã kiểm chứng (nằm trong `report.py`):

| Chỉ số | Tên action |
|---|---|
| Lượt mua | `onsite_conversion.purchase` |
| Lượt thanh toán | `onsite_conversion.initiate_checkout` |
| Đơn đặt hàng | `onsite_conversion.messaging_order_created_v2` |
| Bắt đầu trò chuyện | `onsite_conversion.messaging_conversation_started_7d` |
| Liên hệ mới | `onsite_conversion.messaging_first_reply` |
| Bình luận | `onsite_conversion.post_net_comment` |

### Chẩn đoán lỗi — thứ tự ưu tiên

1. Mở `logs/baocao.log` xem có dòng nào không
2. **File trống hoàn toàn** → lịch chưa được cài → bấm `cai-dat-lich.bat`
3. **Có dòng "THAT BAI"** → đọc lý do; nếu ghi `Session has expired` → token Meta hết hạn
4. Telegram không nhận được → kiểm tra token Telegram + đã bấm Start với bot chưa

---

## 🤝 QUY ƯỚC LÀM VIỆC VỚI ĐẠI

Đại **không biết lập trình**. Khi giải thích kỹ thuật, bắt buộc:

1. **Không dùng thuật ngữ dev** trần trụi. Nếu buộc phải dùng, giải thích ngay bằng ngôn ngữ đời thường.
2. **Đánh số từng bước**: "Bước 1... Bước 2..." — mỗi bước một hành động.
3. **Chỉ rõ bấm vào đâu** trên giao diện.
4. **Đưa sẵn đoạn văn bản copy-paste được** — đừng bắt Đại tự viết lệnh.
5. **Dùng sơ đồ cây và mũi tên** để minh họa luồng.
6. **Dùng icon** để đánh dấu phần quan trọng.
7. **Trấn an** rằng Đại không cần hiểu code bên trong.
8. **Nói rõ việc nào Đại làm, việc nào AI làm hộ.**

---

## 📅 MỐC THỜI GIAN CẦN THEO DÕI

| Thời điểm | Việc |
|---|---|
| ~~12/09/2026 12:00~~ | Đã qua — lần đầu hệ thống tự chạy trên máy nhà |
| ~~Thứ 2 (15/09)~~ | **Đã xong sớm** — cài đặt lên máy công ty ngày **14/09/2026** |
| **14/09/2026 12:00** | Ba mốc tự chạy đầu tiên của máy công ty (12h, 17h, 22h) |
| **18/09/2026** | Token GitHub cũ `buddy-web-sync` hết hạn (không ảnh hưởng dự án này) |
| **10/11/2026** | ⚠️ Token Meta **máy nhà** hết hạn |
| **** | ⚠️ Token Meta **máy công ty** hết hạn |

---

*File này được cập nhật mỗi khi có thay đổi quan trọng. Nếu thấy thông tin lỗi thời, hãy kiểm tra `git log` để biết bản mới nhất.*
