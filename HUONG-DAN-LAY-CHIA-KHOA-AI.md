# HƯỚNG DẪN LẤY CHÌA KHOÁ AI

Dành cho Đại — người không cần biết code.

**Để làm gì:** báo cáo Telegram có mục `🔵 NHẬN ĐỊNH`. Không có chìa khoá này thì mục đó chỉ
hiện một dòng ghi chú, không có 3–5 câu nhận xét do AI viết.

> ✅ **Tin tốt:** chìa khoá này **miễn phí** và lấy mất khoảng **5 phút**.
> Hệ thống chỉ gọi AI **3 lần mỗi ngày** (mỗi báo cáo một lần). Chi phí thực tế: **0 đồng**.
>
> 📌 **Trần miễn phí đã đo được thật (28/09/2026): 20 lượt/ngày** cho model `gemini-3.6-flash`.
> Dùng thật chỉ 3 lượt/ngày nên **thoải mái**. Nhưng chạy thử nhiều lần trong ngày có thể hết
> trần — xem mục "Hết hạn mức cũng không sao" bên dưới.

---

## Bước 1: Lấy chìa khoá

1. Mở trình duyệt (Chrome / Edge), vào địa chỉ: **aistudio.google.com/apikey**
2. Đăng nhập bằng **tài khoản Google** của bạn.
3. Bấm nút **Create API key** (Tạo khoá API).
4. Nếu được hỏi chọn project → chọn project có sẵn, hoặc bấm tạo project mới. Chọn sao cũng được.
5. Một dãy ký tự dài hiện ra. Bấm **Copy** để chép nó.

> ⚠️ **Đừng đóng trang đó vội** nếu chưa dán xong. Tuy nhiên chìa khoá **xem lại được bất cứ lúc
> nào** ở đúng địa chỉ trên, nên lỡ mất cũng không sao.

---

## Bước 2: Dán chìa khoá vào file `.env`

1. Trong thư mục dự án, bấm đúp vào **`mo-file-env.bat`**.
   Notepad mở ra **đúng file cần sửa**. (Khỏi phải đi tìm: trong thư mục có 4 file tên gần
   giống nhau, rất dễ sửa nhầm.)
2. Bấm **Ctrl + F**, gõ `GEMINI_API_KEY`, bấm Enter để nhảy tới dòng đó.
3. Dán chìa khoá vào **ngay sau dấu `=`**, **không có dấu cách**.

❌ **SAI:**

```
GEMINI_API_KEY= AIzaSy...
```

✅ **ĐÚNG:**

```
GEMINI_API_KEY=AIzaSy...
```

4. Bấm **Ctrl + S** để lưu. Đóng Notepad.
5. **Đừng đổi tên file.** Đừng lưu thành `.env.txt`.

---

## Bước 3: Kiểm tra

Mở cửa sổ lệnh tại thư mục dự án (xem cách mở ở `README.md`, mục "Cách chạy thử ngay"),
rồi dán nguyên dòng này và bấm Enter:

```powershell
python test_gemini.py
```

Kết quả đúng phải là dòng cuối ghi:

```
KET QUA: GEMINI API KEY HOAT DONG TOT
```

---

## Nếu báo lỗi thì sao?

### 🔴 `LOI HTTP 404` — **tên model sai, KHÔNG phải chìa khoá sai**

Tên model Gemini thay đổi theo thời gian. Cách dò tên đúng, dán nguyên dòng này
(chìa khoá đọc từ file, **không** in ra màn hình):

```powershell
python -c "import json,urllib.request,report; k=report.load_env('.env')['GEMINI_API_KEY']; d=json.loads(urllib.request.urlopen('https://generativelanguage.googleapis.com/v1beta/models?key='+k,timeout=30).read()); [print('  ', m['name'], '|', m.get('supportedGenerationMethods')) for m in d.get('models',[])]"
```

Nó in ra danh sách model. Tìm dòng có chữ **`generateContent`** và có chữ **`flash`** trong tên.
Chép phần tên đó (bỏ chữ `models/` ở đầu) rồi dán vào `.env` ở dòng `GEMINI_MODEL=`.
Ví dụ: nếu thấy `models/gemini-3.6-flash` thì ghi `GEMINI_MODEL=gemini-3.6-flash`.

### 🔴 `LOI HTTP 400` hoặc `403`

Chìa khoá dán sai hoặc đã bị xoá. Làm lại **Bước 1** để lấy chìa khoá mới.

### 🔴 Báo lỗi mạng / `503`

Gemini đang quá tải. Hệ thống **tự thử lại**, không cần Đại làm gì.
Nếu vẫn không được thì báo cáo vẫn gửi, chỉ thiếu phần nhận định.

### 🟡 Mục NHẬN ĐỊNH ghi *"Phần nhận định do AI viết tạm không có"*

Chìa khoá sai, hết hạn mức, hoặc máy mất mạng.

> ✅ **Báo cáo VẪN ĐẦY ĐỦ SỐ LIỆU.** Chỉ thiếu phần nhận xét. Không có gì hỏng.
> Chạy `python test_gemini.py` để biết lý do cụ thể.

---

## Ba điều phải nhớ

### 1. 🔐 Chìa khoá này là mật khẩu

- **KHÔNG** gửi qua Zalo / Telegram / email.
- **KHÔNG** đưa lên GitHub. File `.gitignore` đã chặn sẵn — **đừng tự ý bỏ chặn**.
- Chuyển sang máy khác thì chép file `.env` bằng **USB**, giống như token Meta.

### 2. 💰 Hết hạn mức cũng không sao

Bản miễn phí cho **20 lượt gọi mỗi ngày** (đo thật ngày 28/09/2026). Dùng thật chỉ **3 lượt/ngày**
nên rất khó chạm trần.

⚠️ **Nhưng coi chừng: chạy thử cũng tốn lượt.** Mỗi lần chạy `python report.py` hoặc
`python report.py --dry` là **một lượt**. Chạy thử 20 lần trong một ngày là hết trần — và lúc đó
báo cáo vẫn gửi nhưng **thiếu phần nhận định** cho tới hôm sau.

👉 **Muốn thử code thì bấm đúp `chay-kiem-thu.bat`** — không cần chìa khoá, **không tốn lượt nào**,
không gửi tin nhắn nào, không đụng tới số liệu.

**Nếu có chạm trần thật:** báo cáo **vẫn gửi bình thường**, chỉ thiếu phần nhận định. Dòng ghi
chú sẽ ghi rõ `het han muc goi AI`. Hôm sau tự có lại, không cần làm gì.

### 3. 🖥️ Mỗi máy một chìa khoá

Máy nhà và máy công ty **dùng chung một chìa khoá cũng được** — không giới hạn số máy.
Nhưng nếu muốn tách riêng cho dễ theo dõi thì cứ lấy hai chìa khoá khác nhau.

---

## Máy nhà cần làm gì?

Khi ở nhà, sau khi `git pull` xong thì:

1. Mở `.env` (bằng `mo-file-env.bat`) và kiểm xem dòng `GEMINI_API_KEY=` đã có chìa khoá chưa.
2. Chưa có thì làm **Bước 1 → Bước 3** ở trên.
3. Chạy `python test_gemini.py` để chắc chắn.

> 📌 `.env` **không** đi theo `git pull` (đã bị chặn, vì là file bí mật). Nên mỗi máy phải tự
> dán chìa khoá một lần.
