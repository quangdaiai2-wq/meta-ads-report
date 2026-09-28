# HƯỚNG DẪN MÁY NHÀ — CẬP NHẬT NGÀY 14/09/2026

**Dành cho:** Đại (người không cần biết code) **và** trợ lý AI trên máy nhà.

> **Nếu bạn là trợ lý AI đang đọc file này:** máy công ty vừa đẩy 3 bản cập nhật lên GitHub.
> File này nói rõ có gì mới, máy nhà cần làm gì, và những điểm cần biết về token.
> Đọc hết trước khi làm.

**Ngày máy công ty cài đặt:** 14/09/2026. Kho GitHub: `meta-ads-report`, nhánh `main`.

---

## ⚠️ CẬP NHẬT NGÀY 28/09/2026 — ĐỌC PHẦN NÀY TRƯỚC

Bản 28/09 sửa hai lỗi đang chạy thật. **Lần này máy nhà PHẢI chạy lại `cai-dat-lich.bat`** —
khác hẳn bản 14/09. Lý do: bản này đổi cả cách lịch Windows gọi script, không chỉ đổi code.

**Ba bước, theo đúng thứ tự:**

1. **`git pull`** tại thư mục dự án → nhận code mới.
2. **Chuột phải `cai-dat-lich.bat` → Run as administrator.** Bắt buộc có quyền Admin.
   Phải chạy bước này, vì lịch trên máy nhà **chưa truyền `--slot`** — không chạy thì máy nhà
   vẫn giữ nguyên hai lỗi cũ (báo cáo trùng, và mốc 8h chạy bù sai).
3. **Kiểm tra kết quả.** File in ra ba dòng, cả ba phải ghi `True`:

   ```
   BaoCaoMetaAds_08 : chay bu=True  tu thuc=True
   BaoCaoMetaAds_12 : chay bu=True  tu thuc=True
   BaoCaoMetaAds_17 : chay bu=True  tu thuc=True
   ```

**Hai điều cần biết trước khi bấm bước 2:**

- **Mốc 22h trên máy nhà sẽ bị bỏ.** `cai-dat-lich.bat` hiện tạo đúng ba mốc 08/12/17 và xoá mốc 22h.
  Nếu Đại muốn **giữ** mốc 22h ở máy nhà thì **đừng chạy bước 2**, và nhắn cho trợ lý AI biết —
  cần chỉnh riêng cho máy nhà.
- **Không mất tính năng chạy bù.** Bản mới của `cai-dat-lich.bat` tự đặt lại cả ba thiết lập
  (chạy bù khi lỡ giờ, tự thức máy, cho phép chạy khi dùng pin) ngay sau khi tạo lịch.
  Đây là lý do dòng kiểm tra ở bước 3 phải hiện `True`.

---

## PHẦN 1 — VIỆC MÁY NHÀ CẦN LÀM (bản 14/09 — nay đã cũ)

### Bước 1: Cập nhật code

Mở cửa sổ lệnh **tại đúng thư mục dự án** rồi chạy:

```powershell
git pull
```

**Kết quả mong đợi:** thấy danh sách file thay đổi, trong đó có `report.py` và `kiem-tra-token.py`.

> ⚠️ **Câu dưới đây đúng cho bản 14/09, KHÔNG đúng cho bản 28/09.**
> Bản 28/09 đổi cách lịch gọi script, nên máy nhà **phải** chạy lại `cai-dat-lich.bat` —
> xem mục "CẬP NHẬT NGÀY 28/09/2026" ở đầu file.
>
> ~~Không cần chạy lại `cai-dat-lich.bat`. 4 lịch trên máy nhà vẫn còn nguyên, không bị ảnh hưởng.~~
> ~~`git pull` chỉ thay file code, không đụng tới lịch Windows.~~

### Bước 2: Kiểm tra token của máy nhà

```powershell
python kiem-tra-token.py
```

Lệnh này cho biết token máy nhà **còn sống bao lâu** — điều mà `test_meta.py` không làm được.

> ⚠️ **Quan trọng:** nếu nó báo token chỉ còn **vài giờ**, nghĩa là token máy nhà cũng đang là
> loại ngắn hạn. Phải chạy ngay `python doi-token-60-ngay.py` rồi kiểm lại.
>
> Ngày 14/09, token máy công ty đã suýt chết vì đúng lý do này: nó chỉ còn sống 1 giờ 44 phút
> mà mọi bài kiểm tra đều báo ĐẠT.

---

## PHẦN 2 — CÓ GÌ MỚI TRONG 3 BẢN CẬP NHẬT

| # | Thay đổi | Vì sao |
|---|---|---|
| 1 | `report.py` chỉ gọi Meta API **1 lần** thay vì 2 | Trước đây mỗi lần chạy tốn gấp đôi hạn mức gọi Meta, và số liệu trên tin nhắn Telegram có thể **lệch** với file HTML đính kèm. Nay hai đầu ra luôn khớp nhau. |
| 2 | Thêm file **`kiem-tra-token.py`** | Kiểm cả 2 nhóm token và cho biết token Meta còn sống bao lâu. Chạy sau mỗi lần lấy token mới. |
| 3 | **Cảnh báo trước khi token hết hạn** | Trước đây hệ thống chỉ báo **sau khi** token đã chết. Nay nếu token còn dưới **7 ngày**, mỗi báo cáo sẽ kèm một dòng cảnh báo vàng ở đầu tin nhắn. |

Xem chi tiết từng bản: `git log --oneline -5`

---

## PHẦN 3 — TOKEN CỦA MÁY NHÀ

### Ngày hết hạn: 10/11/2026

Từ 14/09/2026, **hai máy dùng hai token khác nhau và hết hạn khác ngày**:

| Máy | Token hết hạn |
|---|---|
| **Máy nhà** | **10/11/2026** |
| Máy công ty |  |

⇒ **Không còn chuyện "cả hai máy cùng ngừng hoạt động"** như tài liệu cũ ghi. Máy nhà sẽ
hết hạn trước 3 ngày — thực ra tốt hơn, vì bạn còn thời gian xử lý trước khi máy kia cũng tới hạn.

---

## PHẦN 4 — THÔNG BÁO TOKEN HẾT HẠN ĐI ĐÂU?

### Mỗi máy gửi qua bot Telegram riêng của máy đó

`report.py` đọc `TELEGRAM_BOT_TOKEN` trong file `.env` **của chính máy đang chạy**. Nên:

- Máy **nhà** → cảnh báo nằm trong khung chat với **bot Home**
- Máy **công ty** → cảnh báo nằm trong khung chat với **bot Company**

Hai máy không lẫn vào nhau. Mở đúng khung chat của bot là thấy.

### Có 2 loại cảnh báo

| Loại | Khi nào | Nội dung |
|---|---|---|
| 🟡 **Cảnh báo sớm** | Token còn dưới **7 ngày** | Nằm ở **đầu** mỗi báo cáo, kèm hướng dẫn lấy token mới |
| 🔴 **Báo lỗi** | Token **đã chết**, lần chạy thất bại | Tin nhắn riêng, nội dung tuỳ lỗi Meta trả về |

### ⚠️ Giới hạn phải biết

**Cả hai loại cảnh báo đều chỉ gửi được khi có một lần chạy báo cáo.** Nghĩa là:

- Máy **tắt** hoặc **đăng xuất Windows** đúng lúc đó ⇒ **không có cảnh báo nào**.
- Nếu máy tắt nhiều ngày, bạn chỉ biết khi tự để ý là báo cáo không về.

⇒ **Đừng phụ thuộc hoàn toàn vào cảnh báo.** Thỉnh thoảng mở Telegram xem báo cáo có về đều không.

---

## PHẦN 5 — KHI CẦN LẤY TOKEN META MỚI

1. Làm theo `HUONG-DAN-DIEN-TOKEN.md` — **chỉ làm ở MỘT máy**
2. Chạy `python kiem-tra-token.py` để xác nhận token mới sống được 60 ngày
3. **Copy file `.env` sang máy kia bằng USB**

> ❌ **Đừng** gửi file `.env` qua Telegram / Zalo / email / chat AI.
> Đó là gửi mật khẩu tài khoản quảng cáo qua mạng.
>
> ✅ Sau khi copy sang máy kia, chạy `python kiem-tra-token.py` ở máy đó để chắc chắn.

---

## PHẦN 6 — MỐC THỜI GIAN

| Thời điểm | Việc |
|---|---|
| **Tối 14/09/2026** | Chạy `git pull` + `python kiem-tra-token.py` ở máy nhà |
| **10/11/2026** | ⚠️ Token Meta **máy nhà** hết hạn |
| **** | ⚠️ Token Meta **máy công ty** hết hạn |

Hệ thống sẽ **tự nhắn cảnh báo trước 7 ngày** — bạn không cần tự nhớ ngày.

---

## TÓM TẮT NHANH

```
MÁY NHÀ — BẢN 28/09 (mới nhất, làm theo mục đầu file)
├── git pull                                  ← nhận code mới
├── cai-dat-lich.bat (Run as administrator)   ← PHẢI chạy: tạo lại lịch có --slot
└── nhìn dòng kiểm tra: cả ba phải là True

LƯU Ý: bước 2 sẽ bỏ mốc 22h trên máy nhà.
KHÔNG cần: sửa file .env (token máy nhà không đổi)
KHÔNG cần: bat-danh-thuc-may.bat (thiết lập nguồn điện vẫn còn nguyên)
```

**Chỉ 2 lệnh. Xong.**
