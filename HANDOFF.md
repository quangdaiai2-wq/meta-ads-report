# HANDOFF — SỔ BÀN GIAO CÔNG VIỆC

**Cập nhật lần cuối:** 12/09/2026, 10:00 (giờ Việt Nam)

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

### Chưa làm

- ⏳ **Cài đặt lên máy công ty** ← việc đang làm

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

### 2. Token Meta hết hạn ngày 10/11/2026

Khi đó **cả hai máy cùng ngừng hoạt động**. Cần lấy token mới, làm theo `HUONG-DAN-DIEN-TOKEN.md`, rồi copy sang máy kia.

Hệ thống sẽ **tự nhắn Telegram cảnh báo** khi token hết hạn — không cần tự nhớ.

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
| `cai-dat-lich.bat` | Bật 4 lịch tự động |
| `go-lich.bat` | Tắt 4 lịch |
| `bat-chay-bu.bat` | Bật chạy bù khi lỡ giờ (cần quyền Admin) |
| `.env` | 🔐 **BÍ MẬT** — chứa token. Không đẩy lên GitHub |
| `.env.example` | File mẫu (an toàn để đẩy lên) |
| `logs/baocao.log` | **Nhật ký chạy** — xem đầu tiên khi có sự cố |
| `HUONG-DAN-MAY-CONG-TY.md` | Hướng dẫn cài máy thứ hai |
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
| **12/09/2026 12:00** | Lần đầu hệ thống tự chạy — kiểm tra `logs/baocao.log` |
| **Thứ 2 (15/09)** | Cài đặt lên máy công ty |
| **18/09/2026** | Token GitHub cũ `buddy-web-sync` hết hạn (không ảnh hưởng dự án này) |
| **10/11/2026** | ⚠️ **Token Meta hết hạn** — cần gia hạn cho cả 2 máy |

---

*File này được cập nhật mỗi khi có thay đổi quan trọng. Nếu thấy thông tin lỗi thời, hãy kiểm tra `git log` để biết bản mới nhất.*
