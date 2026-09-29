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

> 📌 **Mốc 22h đã bỏ trên CẢ HAI MÁY từ 28/09/2026.** Lý do: đếm trong `logs/baocao.log` **của máy
> công ty** (14/09 – 28/09) thì mốc 8h có 51 dòng, 12h có 37, 17h có 27, còn **mốc 22h có 0 dòng** —
> trên máy này nó chưa từng báo cáo một lần nào. Khi máy thức dậy buổi sáng, lịch 22h chạy bù và
> tự đoán ra mốc 8h — gây ra báo cáo trùng. Máy nhà trước đây có chạy được mốc 22h (xem ghi chép
> ngày 12/09 ở phần "Ba điều cần biết"), nhưng từ 28/09 Đại chốt dùng chung ba mốc 8h, 12h, 17h
> cho cả hai máy. Muốn lấy lại thì xem mục "Người trực là gì" bên dưới.

### 🆕 Mục `🔵 NHẬN ĐỊNH` nay do AI viết (từ 28/09/2026)

Mỗi báo cáo giờ có thêm **3–5 câu nhận xét** do AI viết, nằm ngay dưới dòng `🔵 NHẬN ĐỊNH`.

**Ba điều cần biết về phần này:**

1. **AI chỉ viết chữ, không tính số.** Toàn bộ con số — kể cả cột chênh lệch so với kỳ trước —
   đều do code tính sẵn rồi đưa cho AI. AI chỉ được chép lại, không được tự tính.
2. **AI lỗi thì báo cáo VẪN GỬI đầy đủ.** Mất mạng, sai chìa khoá, hết hạn mức… thì mục
   NHẬN ĐỊNH hiện một dòng ghi chú, còn số liệu và hai bảng xếp hạng vẫn nguyên vẹn.
   **Không bao giờ mất báo cáo vì AI.**
3. **Khoảng 7 ngày đầu chưa so sánh được.** Sổ lịch sử chỉ mới bắt đầu ghi từ 12h ngày
   28/09/2026. Khi chưa đủ số kỳ trước, AI chỉ **mô tả** số hôm nay chứ không so sánh —
   đó là làm đúng, không phải lỗi. Đủ 7 ngày là mốc 8h tự có so sánh.

> 📌 **Chỉ mốc 8h mới so sánh với kỳ trước.** Mốc 8h là báo cáo **trọn ngày hôm qua** nên so
> được. Mốc 12h và 17h là báo cáo **một phần** của ngày hôm nay — đem nửa ngày so với ngày
> đầy đủ là sai, nên hệ thống chủ động **không** cho AI so ở hai mốc này.

Chìa khoá AI lấy ở đâu: xem **`HUONG-DAN-LAY-CHIA-KHOA-AI.md`**.

> 💰 **Trần miễn phí: 20 lượt/ngày** (đo thật 28/09/2026). Dùng thật chỉ 3 lượt/ngày.
> Nhưng **chạy thử `report.py` cũng tốn lượt** — muốn thử code thì bấm đúp **`chay-kiem-thu.bat`**
> (không gọi mạng, không tốn lượt). Hết trần thì báo cáo vẫn gửi, chỉ thiếu phần nhận định,
> hôm sau tự có lại.

---

## Cách cài đặt (chỉ làm 1 lần)

### Bước 1: Kiểm tra file `.env` đã điền token chưa

**Mở file `.env`:** bấm đúp vào **`mo-file-env.bat`** — Notepad mở đúng file cần sửa.
(Khỏi phải đi tìm: trong thư mục có 4 file tên gần giống nhau, dễ sửa nhầm.)

> ⚠️ File cần sửa tên đúng là **`.env`**. Ba file còn lại **không phải** file thật:
> `.env.example` (bản mẫu) · `.env.bak` và `.env.bak-truoc-gd2` (bản sao lưu cũ).
> Sửa xong bấm **Ctrl + S**. Đừng đổi tên, đừng lưu thành `.env.txt`.

Đảm bảo 4 dòng này đã có giá trị:

```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
META_ADS_ACCESS_TOKEN=...
META_AD_ACCOUNT_ID=...
```

### Bước 2: Bấm đúp `cai-dat-nguoi-truc.bat`

File này làm **bốn** việc, chỉ cần bấm một lần:

1. Tạo **một** lịch Windows duy nhất tên `NguoiTruc`, với **hai** cơ chế kích hoạt:
   - **Khi đăng nhập Windows** — để Người trực luôn sống sau mỗi lần khởi động máy.
   - **Lặp lại mỗi 5 phút** — nếu tiến trình chết giữa ngày, Windows tự bật lại trong vòng
     5 phút. Khi tiến trình đang chạy thì lần lặp này **bị bỏ qua**, không tạo bản thứ hai.
2. **Xoá ba lịch cũ** (`BaoCaoMetaAds_08/12/17`) — để hai lịch cùng sống là có hai nguồn
   gửi báo cáo, sẽ bị trùng.
3. **Khởi động Người trực ngay**, không đợi lần đăng nhập sau. Lịch chỉ kích hoạt khi đăng
   nhập, nên nếu chỉ tạo lịch thì từ lúc bấm file đến lần đăng nhập sau sẽ **không có gì
   gửi báo cáo**.
4. Đọc lại lịch vừa tạo và in ra để kiểm tra.

Nếu báo lỗi quyền: chuột phải vào file → **Run as administrator** → bấm lại.
(Chạy lại lên lịch **đã có** bắt buộc cần quyền Administrator.)

**Bấm từ đúng thư mục dự án** (`D:\Buddy Work AI\2026-09-14-07-50-57`). File này tự lấy
đường dẫn `nguoi_truc.py` từ chỗ nó đứng — bấm từ bản sao ở nơi khác là trỏ sai chỗ.

Kết quả mong đợi:

```
  [XOA] Da xoa lich cu BaoCaoMetaAds_08
  [XOA] Da xoa lich cu BaoCaoMetaAds_12
  [XOA] Da xoa lich cu BaoCaoMetaAds_17
  [--]  Lich cu BaoCaoMetaAds_22 khong ton tai
  [OK]  Da tao lich NguoiTruc
  [OK]  Da khoi dong Nguoi truc

  Ten lich    : NguoiTruc
  Trang thai  : Running
  Chuong trinh: C:\...\python.exe
  Tham so     : "D:\Buddy Work AI\2026-09-14-07-50-57\nguoi_truc.py"
  So trigger  : 2
  Chay khi dung pin: True
  Chay bu khi lo gio: True
  Gioi han thoi gian: PT0S
  Tien trinh   : dang chay (PID ...)
```

**Ba dòng phải đúng:**
- **`Tham so`** phải **kết thúc bằng `nguoi_truc.py"`** — có dấu nháy đóng ở cuối. Thiếu dấu
  nháy đó thì đường dẫn có khoảng trắng bị Windows cắt làm hai và lịch không chạy được.
- **`So trigger`** phải là **`2`**.
- **`Trang thai`** phải là **`Running`** và có dòng **`Tien trinh: dang chay`**.

> ⚠️ **Đừng tin dòng `[OK]`.** Nó chỉ nói Windows không báo lỗi, không nói tham số đã đúng.

### Bước 3: Nhắn thử bot

Mở Telegram, nhắn cho bot câu:

```
còn sống không?
```

Bot trả lời kèm tình trạng: đã chạy bao lâu, mốc giờ của máy này, hôm nay đã gửi mốc nào.
Đây là cách kiểm tra nhanh nhất khi nghi ngờ hệ thống có vấn đề.

> ⚠️ **Phải nhắn SAU khi Người trực đã chạy.** Lúc vừa khởi động, Người trực **bỏ qua toàn bộ
> tin nhắn đến trước đó** — đây là chủ ý, để nó không trả lời một loạt tin cũ. Nếu Đại nhắn
> trước khi bấm file, hoặc nhắn đúng lúc nó đang khởi động, thì tin đó bị bỏ qua và **không có
> phản hồi**. Không phải lỗi — **nhắn lại là được**.

---

## Cách tắt

Bấm đúp vào file **`go-nguoi-truc.bat`** → lịch `NguoiTruc` bị xoá và tiến trình đang chạy
bị dừng, hệ thống ngừng gửi báo cáo hoàn toàn.

Muốn quay lại cách cũ (ba lịch rời rạc, không có Người trực): bấm **`cai-dat-lich.bat`**.
Cách cũ vẫn chạy được, nhưng vẫn còn chuyện gửi gần trùng vào các buổi sáng máy bật lại
sau khi tắt qua nhiều mốc — xem mục "Người trực là gì" bên dưới.

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
  **Một camp chỉ xuất hiện ở MỘT trong hai bảng** (sửa 28/09/2026). Nên nếu tài khoản ít camp,
  bảng "kém hiệu quả" sẽ **ngắn hơn 5 dòng hoặc trống** — đó là đúng, không phải lỗi: khi mọi
  camp đều ra đơn thì thật sự không có camp nào kém.

**Tiêu chí xếp hạng (đổi ngày 29/09/2026):**

| Bảng | Xếp theo | Ghi chú |
|---|---|---|
| 🟢 **Camp hiệu quả** | **Chi phí mỗi đơn, rẻ nhất trước** | Camp chỉ có **1 đơn** bị xếp xuống sau những camp đã có từ 2 đơn trở lên — một đơn may mắn chưa nói lên điều gì |
| 🔴 **Camp kém hiệu quả** | Trước hết là camp **chi tiền mà 0 đơn** (chi nhiều nhất trước) | Nếu chưa đủ 5 dòng thì lấy thêm camp ít đơn nhất, **nhưng loại những camp đã nằm ở bảng trên** |

> 📌 **Trước 29/09/2026, bảng "hiệu quả" xếp theo SỐ ĐƠN.** Đó là đo quy mô, không phải đo hiệu
> quả — trái với chính tên bảng. Đo trên 7 ngày thật: **6/7 ngày hai cách chọn ra hai danh sách
> camp KHÁC NHAU**, không chỉ khác thứ tự. Ví dụ ngày 28/09, cách cũ đưa vào bảng một camp
> **775.150 đ/đơn** trong khi bỏ sót một camp chỉ **405.671 đ/đơn**. Muốn quay lại cách cũ: sửa
> hàm `khoa_xep_hang` trong `report.py`.
>
> ⚠️ **Điều chưa biết:** báo cáo chỉ có **số đơn**, không có **giá trị mỗi đơn**. Nên "chi phí mỗi
> đơn" chưa phải "hiệu quả" đầy đủ — một đơn 5 triệu khác một đơn 200 nghìn. Nếu biên lợi nhuận
> mỗi đơn của Đại cao thì camp đắt vẫn đáng chạy.
- Cột **CPR** tự đổi màu: 🟢 xanh = rẻ hơn mức trung bình, 🔴 đỏ = đắt hơn.

**Lưu ý:** Số liệu được **ghi sẵn** vào file lúc tạo — file này là **ảnh chụp (snapshot)**, không tự cập nhật. Muốn số mới, chạy lại script.

---

## 🧍 Người trực là gì

Trước 28/09/2026, hệ thống dùng **ba lịch Windows rời rạc**: 8h, 12h, 17h. Mỗi lịch chạy
`report.py` và script tự đoán xem mình là mốc mấy giờ. Cách đó có hai bệnh:

- **Gửi trùng.** Khi máy ngủ qua nhiều mốc, Windows cho **cả ba lịch chạy bù cùng lúc**;
  cả ba cùng đoán ra một mốc và gửi ra nhiều báo cáo giống hệt nhau.
- **Không nghe được tin nhắn.** Lịch chỉ biết *chạy*, không biết *nghe*, nên không thể
  trả lời khi Đại nhắn hỏi.

Từ Giai đoạn 2, cả ba lịch được thay bằng **một tiến trình chạy suốt** tên `NguoiTruc`,
do `nguoi_truc.py` đảm nhiệm. Nó:

| Việc | Cách làm |
|---|---|
| Canh mốc giờ | Kiểm tra đồng hồ mỗi 30 giây. Tới mốc và mốc đó chưa gửi hôm nay → gọi `report.py` kèm `--slot` |
| Gửi bù khi lỡ | Lúc khởi động, đối chiếu sổ đã gửi. Chỉ gửi **MỘT** báo cáo cho mốc gần nhất bị lỡ; các mốc cũ hơn ghi nhật ký là bỏ qua |
| Nghe Telegram | Chỉ trả lời tin từ `TELEGRAM_CHAT_ID` của Đại. Tin từ người lạ bị bỏ qua và ghi nhật ký |
| Bỏ qua tin cũ | Lúc vừa khởi động, **bỏ qua toàn bộ tin nhắn đến trước đó** (chủ ý — để không trả lời một loạt tin cũ). Nhắn trước khi nó chạy thì tin đó mất, phải nhắn lại |
| Nhịp tim | Ghi một dòng nhật ký mỗi 30 phút để biết còn sống |
| Tự bật lại nếu chết | Lịch có trigger **lặp mỗi 5 phút**; tiến trình đang chạy thì lần lặp bị bỏ qua, tiến trình đã chết thì được bật lại |
| Viết nhận định | Mỗi báo cáo gọi AI **một lần** để viết 3–5 câu nhận xét. AI lỗi thì bỏ qua phần đó, **báo cáo vẫn gửi đầy đủ** |

**Mốc giờ là cấu hình của từng máy**, đọc từ khoá `REPORT_SLOTS` trong `.env`:

```
REPORT_SLOTS=8,12,17
```

**Cả hai máy đều dùng `8,12,17`** — mốc 22h đã bỏ từ 28/09/2026 (xem lý do ở đầu file).
Đây là **cấu hình của từng máy**, không copy y nguyên `.env` giữa hai máy mà quên kiểm dòng này.

Muốn lấy lại mốc 22h ở một máy nào đó: sửa dòng đó thành `REPORT_SLOTS=8,12,17,22` rồi khởi
động lại Người trực. Nếu thiếu khoá này, hệ thống dùng mặc định `8,12,17,22` — nghĩa là **mốc
22h quay trở lại**, nên đừng để thiếu.

**Giới hạn phải biết:** Người trực chỉ sống khi máy **đang bật và đang đăng nhập Windows**.
Máy tắt thì không có báo cáo — nhưng khi bật lại, nó gửi bù đúng một báo cáo cho mốc gần
nhất bị lỡ, không gửi một loạt báo cáo cũ.

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

**Chỉ ghi khi chạy THẬT** (từ 28/09/2026). Chạy thử `--dry` hoặc `--mock` **không** ghi nữa.
Lý do: hai chế độ đó không gửi báo cáo nào, mà `--dry` lại không truyền mốc giờ nên script
tự đoán mốc — dẫn tới sổ ghi **sai mốc**. Đã xảy ra thật: một lần chạy lúc 14h07 bị ghi thành
mốc 12h. Phần nhận định của AI lấy sổ này làm số kỳ trước, nên ghi bẩn là AI nhận định sai.

**File này không lên GitHub** — nó nằm trong `logs/`, đã bị `.gitignore` chặn.

---

## ⚠️ Ba điều cần biết

### 1. Máy phải đang bật VÀ đang đăng nhập Windows

Hệ thống chạy trên máy này. **Người trực chỉ sống khi máy đang bật VÀ đã đăng nhập Windows.**
Máy tắt thì không có báo cáo — nhưng khi bật lại, nó tự gửi bù **đúng một** báo cáo cho mốc
gần nhất bị lỡ, không gửi một loạt báo cáo cũ.

**Không cần bật "tự thức máy" nữa.** Trước đây ba lịch rời rạc cần Windows đánh thức máy để
chạy bù; Người trực chạy suốt nên chuyện đó không còn. File `bat-danh-thuc-may.bat` vẫn nằm
đó nhưng **không cần bấm** khi dùng Người trực.

**Để báo cáo đến đúng giờ:**
- **Cắm sạc** máy thường xuyên (đừng để pin cạn).
- **Đừng tắt máy, đừng đăng xuất Windows** — chỉ để máy ngủ là đủ.

> 📌 **Thực tế đã gặp (trước 28/09/2026, khi còn dùng ba lịch rời rạc):**
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
├── 📄 ai.py                     ← Lớp AI: viết 3-5 câu nhận định (không tính số, không gửi tin)
├── 📄 dashboard.py              ← Bộ tạo file dashboard.html
├── 📄 dashboard.html            ← Dashboard xem báo cáo (tự tạo lại mỗi lần chạy)
├── 📄 doi-token-60-ngay.py      ← Công cụ gia hạn token Meta lên 60 ngày
├── 📄 kiem-tra-token.py         ← Kiểm tra CẢ 2 nhóm token + token Meta còn sống bao lâu
├── 📄 cai-dat-nguoi-truc.bat     ← Bấm để BẬT (tạo Người trực, xoá 3 lịch cũ)
├── 📄 go-nguoi-truc.bat          ← Bấm để TẮT (xoá lịch, dừng tiến trình)
├── 📄 mo-file-env.bat            ← Bấm để mở file bí mật .env bằng Notepad (khỏi phải tìm)
├── 📄 chay-kiem-thu.bat          ← Bấm để tự kiểm tra code còn đúng không (không tốn lượt AI)
├── 📄 cai-dat-lich.bat           ← Cách cũ (3 lịch rời rạc) — đường lùi nếu Người trực có sự cố
├── 📄 go-lich.bat                ← Xoá 3 lịch cũ
├── 📄 bat-chay-bu.bat            ← Chỉ còn dùng cho cách cũ (cần Admin)
├── 📄 nguoi_truc.py              ← Tiến trình chạy suốt: canh mốc giờ + nghe Telegram
├── 📄 bat-danh-thuc-may.bat     ← Bấm để cho phép Windows tự thức máy chạy báo cáo (cần Admin)
├── 📄 logs/baocao.log           ← Nhật ký chạy (xem khi cần chẩn đoán)
│
├── 📄 test_telegram.py          ← Test token Telegram
├── 📄 test_meta.py              ← Test kết nối Meta
├── 📄 test_gemini.py            ← Test chìa khoá AI (chạy sau mỗi lần đổi chìa khoá)
├── 📄 list_actions.py           ← Công cụ dò tên chỉ số
├── 📄 find_payment.py           ← Công cụ dò chỉ số thanh toán
├── 📄 tests/                    ← Kiểm thử tự động (không gọi mạng, không tốn hạn mức)
│
├── 📄 HUONG-DAN-DIEN-TOKEN.md   ← Hướng dẫn lấy token
├── 📄 HUONG-DAN-LAY-CHIA-KHOA-AI.md ← Hướng dẫn lấy chìa khoá AI (Gemini)
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
| `logs/baocao.log` trống hoàn toàn | Chưa cài gì → bấm `cai-dat-nguoi-truc.bat` |
| Không thấy báo cáo nhưng nhật ký vẫn có dòng nhịp tim | Người trực sống, nhưng việc gửi thất bại → tìm dòng `NGUOI TRUC: gui moc ... THAT BAI` và đọc lý do |
| Nhật ký ghi `UnicodeEncodeError` + `charmap` + `cp1252` | **Lỗi bảng mã tiếng Việt** — báo cáo KHÔNG gửi được (đã gặp thật 28/09/2026). Xem `HANDOFF.md`, mục "BÁO CÁO NGỪNG GỬI VÌ LỖI BẢNG MÃ TIẾNG VIỆT" |
| Nhắn bot không trả lời **ngay sau khi vừa cài** | Bình thường — Người trực bỏ qua tin đến trước lúc nó khởi động. **Nhắn lại.** |
| Nhắn bot không trả lời, nhắn lại vẫn im | Mở Task Manager (Ctrl+Shift+Esc), tìm `python.exe` chạy `nguoi_truc.py`. Không có → bấm `cai-dat-nguoi-truc.bat` lại (file này khởi động Người trực ngay), hoặc đăng xuất rồi đăng nhập lại Windows |
| Telegram báo "Token Meta đã HẾT HẠN" | Làm theo `HUONG-DAN-DIEN-TOKEN.md` → mục `META_ADS_ACCESS_TOKEN` |
| Báo cáo ghi "LOI lay du lieu Meta" | Token Meta hết hạn → lấy token mới |
| Báo cáo ghi "LOI GUI TELEGRAM" | Kiểm tra token Telegram và Chat ID |
| Số liệu ra 0 hết | Kiểm tra bộ lọc `dainq` có khớp campaign nào không |
| `dashboard.html` mở ra trắng/trống | Chạy lại `python report.py --dry` để tạo lại file |
| Mục NHẬN ĐỊNH ghi "Phần nhận định do AI viết tạm không có" | **Đọc lý do trong ngoặc** ngay sau đó — hệ thống ghi rõ bằng tiếng Việt (hết hạn mức / tên model sai / chìa khoá sai / mất mạng). **Báo cáo vẫn đầy đủ số liệu.** Chạy `python test_gemini.py` để kiểm chìa khoá |
| Phần nhận định chỉ mô tả, không so sánh | Bình thường trong ~7 ngày đầu: sổ lịch sử chưa đủ số kỳ trước. Xem mục "NHẬN ĐỊNH nay do AI viết" ở đầu file |
| Ghi chú AI báo `het han muc goi AI` | Bản miễn phí cho **20 lượt/ngày**; chạy thử `report.py` nhiều lần cũng tốn lượt. Hôm sau tự có lại. Muốn thử code thì bấm đúp **`chay-kiem-thu.bat`** (không tốn lượt) |

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
- **Task Scheduler**: **một** task tên `NguoiTruc`, **hai** trigger — kích hoạt khi đăng nhập,
  và lặp mỗi 5 phút để tự bật lại nếu tiến trình chết. Có "Restart on failure".
  Cách cũ dùng 3 task `BaoCaoMetaAds_08/12/17` — `cai-dat-lich.bat` vẫn tạo được nếu cần.
- **Tiến trình thường trú**: `nguoi_truc.py`, kiểm tra đồng hồ mỗi 30 giây. Gọi `report.py`
  ở **tiến trình riêng** kèm `--slot N`.
- **Mốc giờ**: khoá `REPORT_SLOTS` trong `.env`. Không có khoá thì mặc định `8,12,17,22`.
- **Dashboard**: `dashboard.py` sinh HTML tĩnh, không dùng thư viện ngoài, không cần server. `report.py` gọi `compute_stats()` **một lần duy nhất** rồi dùng chung cho cả text lẫn HTML (tránh gọi API 2 lần).

### ⚠️ Lưu ý quan trọng khi sửa script

Meta trả về **nhiều tên action cho cùng một hành động** (`omni_purchase`, `onsite_web_purchase`, `onsite_app_purchase`, `onsite_conversion.purchase`...). **Cộng hết sẽ bị đếm gấp đôi.** Chỉ dùng một tên duy nhất cho mỗi chỉ số.

### Tham số `--slot` — chống gửi trùng báo cáo

Mỗi lần gửi đều truyền **đúng mốc giờ** vào `report.py`, không để script tự đoán:

```
python report.py --slot 08
python report.py --slot 12
python report.py --slot 17
```

Người trực (`nguoi_truc.py`) gọi `report.py` theo cách này, kèm `--slot N` của mốc nó vừa tới.

**Vì sao cần:** trước 28/09/2026, lịch Windows không truyền mốc giờ, nên `report.py` phải tự
đoán mốc gần nhất với giờ hiện tại. Khi máy ngủ qua nhiều mốc, Windows cho nhiều lịch chạy bù
**cùng lúc** — tất cả cùng đoán ra một mốc và gửi ra nhiều báo cáo giống hệt nhau.
Đã xảy ra thật: sáng 28/09/2026 lúc 08:26 gửi 4 tin trùng + 4 file HTML.

**Cơ chế chống trùng cũ (`logs/da_gui.json`) vẫn còn, nhưng chỉ là lưới an toàn** — nó kiểm
tra rồi mới ghi, nên khi nhiều tiến trình chạy đồng thời thì cả loạt đều lọt qua. Thứ chặn
được gửi trùng thật là **Người trực biết rõ lịch của chính nó**: mỗi mốc chỉ gửi một lần,
và khi khởi động lại chỉ gửi bù **một** báo cáo cho mốc gần nhất bị lỡ.

**Không có `--slot`** (chạy tay): script vẫn đoán mốc gần nhất như cũ, để tương thích ngược.

### Kiểm chứng mốc giờ đã vào lịch chưa

Dòng `[OK]` khi tạo lịch **không** chứng minh tham số đã đúng — nó chỉ nói lệnh không báo lỗi.
Kiểm riêng bằng PowerShell (`schtasks.exe` có thể bị chính sách công ty chặn):

```powershell
$t = Get-ScheduledTask -TaskName 'NguoiTruc' -ErrorAction SilentlyContinue
if (-not $t) { Write-Host "KHONG TIM THAY lich NguoiTruc" } else {
  foreach ($a in $t.Actions) {
    Write-Host ("Execute  = " + $a.Execute)
    Write-Host ("Args     = " + $a.Arguments)
    Write-Host ("WorkDir  = " + $a.WorkingDirectory)
  }
}
```

**Điều kiện đạt:**
- `Execute` trỏ tới `python.exe`
- `Args` **kết thúc bằng `nguoi_truc.py"`** — có dấu nháy đóng ở cuối. Thiếu dấu nháy đó thì
  đường dẫn có khoảng trắng bị Windows cắt làm hai và lịch không chạy được.
- `WorkDir` là thư mục dự án (`D:\Buddy Work AI\2026-09-14-07-50-57\`)

> Muốn kiểm lịch của **cách cũ** (ba lịch `BaoCaoMetaAds_*`), thay `'NguoiTruc'` bằng
> `'BaoCaoMetaAds_08'` — khi đó `Args` phải chứa `--slot 08`.
