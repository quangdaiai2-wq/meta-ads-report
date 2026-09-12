# HƯỚNG DẪN CÀI ĐẶT MÁY THỨ HAI (MÁY CÔNG TY)

Dành cho Đại — người không cần biết code. Làm theo đúng thứ tự.

**Nguyên tắc quan trọng:** Code giống nhau, nhưng mỗi máy có file `.env` **riêng**. Đó là lý do dùng bot Telegram khác được mà không cần sửa code.

---

# PHẦN 1 — LÀM TẠI MÁY NHÀ (hôm nay)

## Bước 1: Tạo kho chứa trên GitHub

1. Mở trình duyệt, vào **github.com**
2. Đăng nhập tài khoản **quangdaiai2-wq**
3. Bấm dấu **+** ở góc trên bên phải → chọn **New repository**
4. Điền như sau:

| Ô | Điền gì |
|---|---|
| Repository name | `meta-ads-report` |
| Description | (để trống cũng được) |
| **Private / Public** | ⚠️ **Chọn PRIVATE** |
| Add a README file | ❌ **KHÔNG tick** |
| Add .gitignore | ❌ **KHÔNG chọn** |
| Choose a license | ❌ **KHÔNG chọn** |

5. Bấm nút xanh **Create repository**

> ⚠️ **Vì sao phải chọn Private?**
> Trong file `.env.example` có tên tài khoản quảng cáo công ty và từ khóa lọc nội bộ. Không phải token, nhưng vẫn là thông tin nội bộ — không nên công khai.

---

## Bước 2: Đẩy code lên GitHub

Mở **Command Prompt** hoặc **PowerShell** tại thư mục dự án, chạy 2 lệnh sau (copy nguyên dòng):

```bash
git remote add origin https://github.com/quangdaiai2-wq/meta-ads-report.git
git push -u origin main
```

**Kết quả mong đợi:**

```
Enumerating objects: 20, done.
...
To https://github.com/quangdaiai2-wq/meta-ads-report.git
 * [new branch]      main -> main
```

Lần đầu GitHub sẽ hỏi đăng nhập → bấm **Sign in with your browser** và đăng nhập.

✅ Xong Phần 1. Code đã nằm trên GitHub.

---

# PHẦN 2 — LÀM TẠI MÁY CÔNG TY (thứ 2)

## Bước 3: Kiểm tra máy công ty có Python chưa

1. Bấm phím **Windows**, gõ `cmd`, mở **Command Prompt**
2. Gõ lệnh:

```bash
python --version
```

| Kết quả | Nghĩa là | Làm gì |
|---|---|---|
| Hiện `Python 3.13.x` hoặc `3.12.x` | ✅ Đã có | Sang Bước 4 |
| Hiện `Python 3.11` trở xuống | ⚠️ Cũ | Cài bản mới (xem dưới) |
| Báo lỗi "not recognized" | ❌ Chưa có | Cài Python (xem dưới) |

**Nếu cần cài Python:**
1. Vào **python.org/downloads**
2. Tải bản **3.13** cho Windows
3. Chạy file cài → ⚠️ **TICK vào ô "Add python.exe to PATH"** ở màn hình đầu tiên
4. Bấm **Install Now**

---

## Bước 4: Tải code về máy công ty

1. Mở **Command Prompt**
2. Di chuyển tới thư mục muốn để dự án, ví dụ ổ D:

```bash
d:
cd \
```

3. Tải code về:

```bash
git clone https://github.com/quangdaiai2-wq/meta-ads-report.git
```

4. Vào thư mục vừa tải:

```bash
cd meta-ads-report
```

> 💡 **Thư mục không cần giống máy nhà.** Git tự hiểu đường dẫn, đặt ở đâu cũng được.

---

## Bước 5: Tạo file `.env` cho máy công ty

Đây là bước **duy nhất khác biệt** giữa hai máy.

### 5a. Tạo file từ bản mẫu

```bash
copy .env.example .env
```

### 5b. Mở file `.env` bằng Notepad

```bash
notepad .env
```

### 5c. Điền thông tin

Điền **3 nhóm** sau:

**① Telegram — DÙNG BOT MỚI**

```
TELEGRAM_BOT_TOKEN=<token bot mới của công ty>
TELEGRAM_CHAT_ID=<chat ID>
```

⚠️ **Trước khi điền, làm 2 việc này:**
1. Mở Telegram, tìm bot mới, bấm **Start** (nếu không bot không gửi được tin)
2. Nếu bot mới gửi cho **cùng tài khoản Telegram của Đại** → `TELEGRAM_CHAT_ID` giữ nguyên giá trị cũ. Nếu gửi cho nhóm khác → lấy ID mới từ **@userinfobot**

**② Meta Ads — COPY TỪ MÁY NHÀ**

Mở file `.env` trên máy nhà, copy 4 dòng này sang:

```
META_ADS_ACCESS_TOKEN=<copy nguyên giá trị>
META_APP_ID=<copy nguyên giá trị>
META_APP_SECRET=<copy nguyên giá trị>
META_AD_ACCOUNT_ID=<copy nguyên giá trị>
```

> 💡 Cùng một tài khoản quảng cáo → dùng chung token được. Token 60 ngày dùng cho nhiều máy không bị giới hạn.

**③ Cấu hình báo cáo — COPY TỪ MÁY NHÀ**

```
REPORT_ACCOUNT_NAME=...
FILTER_INCLUDE=...
FILTER_EXCLUDE=...
TOP_CAMPAIGN_COUNT=5
```

### 5d. Lưu file

Bấm **Ctrl + S**, rồi đóng Notepad.

---

## Bước 6: Bật lịch tự động

1. Trong thư mục `meta-ads-report`, tìm file **`cai-dat-lich.bat`**
2. **Bấm đúp** vào nó
3. Nếu báo lỗi quyền → **chuột phải** → **Run as administrator**

**Kết quả mong đợi:**

```
Python : C:\Users\...\python.exe
Script : D:\meta-ads-report\report.py

Dang tao 4 lich...

  [OK]  Moc 08:00 - da tao
  [OK]  Moc 12:00 - da tao
  [OK]  Moc 17:00 - da tao
  [OK]  Moc 22:00 - da tao

[OK] Da tao lich thanh cong.
```

✅ Xong. Máy công ty sẽ tự gửi báo cáo.

---

## Bước 7 (khuyến nghị): Bật chạy bù khi lỡ giờ

**Chuột phải** vào file **`bat-chay-bu.bat`** → **Run as administrator**.

Việc này giúp: nếu máy tắt đúng lúc 12h, khi bật lại Windows sẽ tự gửi bù.

---

# PHẦN 3 — KIỂM TRA

## Chạy thử ngay (không cần chờ đến giờ)

Mở Command Prompt tại thư mục dự án:

```bash
python report.py
```

**Kết quả mong đợi:** `DA GUI BAO CAO VAO TELEGRAM`

→ Mở Telegram kiểm tra. Nếu có tin nhắn từ **bot mới** là thành công.

## Kiểm tra nhật ký

Mở file **`logs\baocao.log`**:

```
[2026-09-15 14:30:12] BAT DAU - moc 12h, khoang 2026-09-15 -> 2026-09-15
[2026-09-15 14:30:20] THANH CONG - moc 12h, da gui Telegram
```

---

# ⚠️ NHỮNG ĐIỀU CẦN NHỚ

## 1. Hai máy chạy song song → nhận 2 bộ báo cáo

Đại đã chọn cả hai máy cùng chạy. Nghĩa là mỗi ngày Đại sẽ nhận:
- 1 bộ báo cáo ở **chat Telegram máy nhà** (bot A)
- 1 bộ báo cáo ở **chat Telegram máy công ty** (bot B)

**Ưu điểm:** máy này tắt thì máy kia vẫn gửi.
**Nhược điểm:** nội dung trùng nhau.

**Nếu muốn chỉ nhận 1 bộ:** bấm `go-lich.bat` ở máy không muốn chạy.

## 2. File `.env` KHÔNG BAO GIỜ đưa lên GitHub

File `.gitignore` đã chặn sẵn. Nhưng đừng tự ý bỏ chặn.

Khi copy `.env` sang máy công ty: dùng **USB** hoặc **gõ lại**.
❌ Đừng gửi qua Telegram / Zalo / email — đó là gửi mật khẩu qua mạng.

## 3. Sửa code ở máy nào thì phải đồng bộ

Ví dụ Đại sửa `report.py` ở máy nhà:

```bash
git add .
git commit -m "sửa cách tính chỉ số"
git push
```

Sang máy công ty:

```bash
git pull
```

## 4. Token Meta dùng chung — hết hạn cùng lúc

Token Meta hết hạn ngày **10/11/2026**. Khi đó **cả hai máy cùng ngừng hoạt động**.

Cần lấy token mới ở **một máy**, rồi copy sang máy kia.

---

# TÓM TẮT NHANH

```
MÁY NHÀ (hôm nay)
├── Tạo repo Private trên GitHub tên meta-ads-report
├── git remote add origin ...
└── git push -u origin main

MÁY CÔNG TY (thứ 2)
├── Kiểm tra Python (cài nếu chưa có)
├── git clone ...
├── copy .env.example .env
├── Điền token bot MỚI + copy token Meta từ máy nhà
├── Bấm cai-dat-lich.bat
└── Bấm bat-chay-bu.bat (Run as administrator)
```

**Chỉ khác nhau 1 dòng:** `TELEGRAM_BOT_TOKEN`
