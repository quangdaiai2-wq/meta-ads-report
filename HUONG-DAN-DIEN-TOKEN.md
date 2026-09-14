# HƯỚNG DẪN ĐIỀN TOKEN

Dành cho Đại — người không cần biết code.

---

## Bước 1: Copy file mẫu thành file thật

Trong thư mục dự án, bạn sẽ thấy 2 file:

```
.env.example    ← file MẪU (có thể đưa lên GitHub)
.env            ← file THẬT (đã có sẵn, chứa token của bạn)
```

File `.env` đã được tạo sẵn cho bạn. Không cần copy gì cả.

**Lưu ý:** File `.env` bắt đầu bằng dấu chấm nên có thể bị ẩn. Nếu không thấy nó, hãy bật chế độ "hiện file ẩn" trong Windows Explorer.

---

## Bước 2: Mở file `.env` bằng Notepad

- Bấm chuột phải vào file `.env`
- Chọn **Open with** → **Notepad**

Bạn sẽ thấy các dòng như thế này:

```
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
META_ADS_ACCESS_TOKEN=
META_AD_ACCOUNT_ID=
```

---

## Bước 3: Điền token

Dán token vào **sau dấu bằng `=`, không có dấu cách**.

❌ **SAI:**
```
TELEGRAM_BOT_TOKEN= 1234567890:ABC...
```

✅ **ĐÚNG:**
```
TELEGRAM_BOT_TOKEN=1234567890:ABC...
```

---

## Bước 4: Lưu file

Bấm **Ctrl + S**.

---

## Token lấy ở đâu?

### 🔐 TELEGRAM_BOT_TOKEN

1. Mở Telegram trên điện thoại
2. Tìm **@BotFather** (có dấu tick xanh)
3. Bấm **Start**
4. Gõ: `/newbot`
5. Đặt tên bot (ví dụ: `Bao cao Ads`)
6. Đặt username, phải kết thúc bằng chữ `bot` (ví dụ: `baocao_ads_bot`)
7. BotFather trả về **token** — copy và dán vào file

### 🔐 TELEGRAM_CHAT_ID

1. Mở Telegram
2. Tìm **@userinfobot**
3. Bấm **Start**
4. Nó trả về **Id:** kèm dãy số — copy dãy số đó

### 🔐 META_ADS_ACCESS_TOKEN

Phần này khó nhất, cần làm trên máy tính.

**⚠️ ĐỌC TRƯỚC:** Token lấy trực tiếp từ Graph API Explorer chỉ **sống 1–2 giờ**. Nếu dán thẳng vào hệ thống, hôm sau báo cáo sẽ lỗi. Vì vậy phải làm thêm **Bước B** để đổi thành token sống **60 ngày**.

---

#### Bước A: Lấy token ngắn hạn

1. Vào **developers.facebook.com**
2. Đăng nhập bằng tài khoản Facebook có quyền quảng cáo
3. Bấm **My Apps** → **Create App**
4. Chọn loại app → **Business**
5. Vào **Tools** → **Graph API Explorer**
6. Ở phần **Permissions**, thêm quyền `ads_read`
7. Bấm **Generate Access Token** → xác nhận
8. **Copy token đó** (dán tạm vào Notepad, sẽ dùng ở Bước B)

---

#### Bước B: Lấy App ID và App Secret

1. Vẫn trong trang **developers.facebook.com**
2. Ở menu bên trái, bấm **Settings** → **Basic**
3. Bạn sẽ thấy 2 dòng:
   - **App ID** — một dãy số
   - **App Secret** — bấm nút **Show** để hiện ra
4. Copy **cả hai** (dán vào Notepad)

---

#### Bước C: Điền vào file `.env`

Mở `.env` bằng Notepad, điền 3 dòng:

```
META_ADS_ACCESS_TOKEN=<dán token ngắn hạn ở Bước A>
META_APP_ID=<dán App ID ở Bước B>
META_APP_SECRET=<dán App Secret ở Bước B>
```

Lưu file (**Ctrl + S**).

---

#### Bước D: Chạy công cụ đổi token

**Mở cửa sổ lệnh tại đúng thư mục dự án trước** — PowerShell mặc định mở ở `C:\WINDOWS\System32`, chạy lệnh ở đó sẽ báo lỗi "không tìm thấy file".

Cách nhanh nhất:
1. Mở **File Explorer**, vào thư mục dự án
2. Bấm vào **thanh địa chỉ** phía trên
3. Gõ `powershell` rồi bấm **Enter**

Hoặc dùng lệnh `cd` trong cửa sổ PowerShell:

```powershell
cd "D:\Workbuddy\2026-09-11-21-17-48"
```

Sau đó chạy:

```powershell
python doi-token-60-ngay.py
```

Nếu báo lỗi `python is not recognized`, dùng đường dẫn đầy đủ:

```powershell
& "C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe" doi-token-60-ngay.py
```

Kết quả mong đợi:

```
THANH CONG - DA DOI TOKEN DAI HAN
Token moi: EAAZ... (198 ky tu)
Song duoc : 60 ngay
Het han   :  08:15
```

> Ngày hết hạn thật = ngày bạn chạy + 60 ngày. Ví dụ trên chỉ là minh hoạ.

✅ Công cụ **tự động ghi token mới vào `.env`** — không cần copy tay.
✅ Nó cũng tự sao lưu file cũ thành `.env.bak` để phòng hờ.

#### Bước E: KIỂM TRA LẠI — bắt buộc, đừng bỏ qua

```powershell
python kiem-tra-token.py
```

Lệnh này kiểm **cả 2 nhóm token**, và quan trọng nhất: **cho biết token Meta còn sống bao lâu**.

> ⚠️ **Vì sao bắt buộc?** Nếu bạn quên chạy Bước D, token vẫn hoạt động bình thường trong
> 1–2 giờ rồi chết — và mọi bài kiểm tra đều báo ĐẠT trong lúc đó. Đã gặp thật ngày
> 14/09/2026: token chỉ còn sống **1 giờ 44 phút** mà `test_meta.py` vẫn báo ĐẠT.
>
> Nhìn dòng `Con lai`. Phải thấy khoảng **60 ngày**. Nếu thấy vài giờ ⇒ Bước D chưa xong.

Script này cũng kiểm luôn:
- Token Telegram có hợp lệ không, **và tên bot có đúng bot của máy này không**
- Chat ID có gửi được không
- Token Meta có quyền `ads_read` không
- Tài khoản quảng cáo có truy cập được không

---

⚠️ **Sau 60 ngày** token hết hạn → lặp lại Bước A → E.
Hệ thống sẽ **nhắn tin cảnh báo vào Telegram** khi token hết hạn, nên bạn sẽ không bị bỏ lỡ.

### 🔐 META_AD_ACCOUNT_ID

1. Vào **Trình quản lý quảng cáo Meta**
2. Xem phần cài đặt tài khoản
3. ID có dạng `act_123456789012345`
4. Copy cả chữ `act_` và dán vào file

---

## ⚠️ Ba điều tuyệt đối không làm

| ❌ Không làm | Lý do |
|---|---|
| Gửi file `.env` cho ai | Chứa token = mật khẩu của bạn |
| Đưa file `.env` lên GitHub | Bot tự động quét và tìm thấy trong vài phút |
| Dán token vào cửa sổ chat | Token sẽ nằm trong log hội thoại |

**File `.gitignore` đã chặn file `.env` rồi** — nên bạn yên tâm, kể cả có push lên GitHub thì `.env` vẫn không đi.

---

## Kiểm tra đã đúng chưa

**Cách 1 — tự kiểm, nhanh nhất.** Mở cửa sổ lệnh tại thư mục dự án rồi chạy:

```powershell
python kiem-tra-token.py
```

Script tự báo còn thiếu gì, sai ở đâu, và cách sửa. Nó **không gửi tin nhắn nào** vào Telegram
và **không in token đầy đủ** ra màn hình.

**Cách 2 — nhờ trợ lý.** Gửi tin nhắn:

> Tôi đã điền xong token. Kiểm tra giúp tôi đã điền đúng chưa.

Trợ lý sẽ kiểm tra **cấu trúc** file (không đọc nội dung token) và báo cho bạn biết còn thiếu gì.
