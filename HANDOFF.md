# HANDOFF — SỔ BÀN GIAO CÔNG VIỆC

**Cập nhật lần cuối:** 28/09/2026 — Giai đoạn 2 (Người trực) đã thi công xong, **chờ Đại bấm
`cai-dat-nguoi-truc.bat`** để chữa hai lỗi đang chạy trên máy thật.

---

## 📌 CÁCH DÙNG FILE NÀY

**Nếu bạn là trợ lý AI đang đọc file này:** Người dùng (Đại) vừa chuyển sang một máy tính khác. Đây là bối cảnh đầy đủ của dự án. Hãy đọc hết file trước khi làm bất cứ điều gì.

**Nếu bạn là Đại:** Khi sang máy khác, chỉ cần nói với trợ lý ở đó:

> **"Đọc file HANDOFF.md trong thư mục dự án và giúp tôi làm tiếp."**

---

## 🎯 DỰ ÁN LÀ GÌ

Hệ thống tự động lấy số liệu **Meta Ads** và gửi báo cáo vào **Telegram**, chạy theo lịch **3 mốc mỗi ngày**: 8h, 12h, 17h.

Chủ dự án: **Đại** — người không biết lập trình, cần hướng dẫn từng bước.

---

## ✅ TRẠNG THÁI HIỆN TẠI

### Đã hoàn thành (trên máy nhà)

| # | Hạng mục | Chi tiết |
|---|---|---|
| 1 | Token Meta 60 ngày | Hết hạn **10/11/2026** |
| 2 | Người trực (từ 28/09/2026) | Một lịch `NguoiTruc` chạy `nguoi_truc.py` khi đăng nhập. Ba lịch `BaoCaoMetaAds_08/12/17` đã bị bỏ |
| 3 | Chạy bù khi lỡ giờ | Đã bật `StartWhenAvailable` cho cả 3 lịch |
| 4 | Dashboard HTML | Tự tạo lại mỗi lần chạy |
| 5 | Đẩy code lên GitHub | 4 bản ghi, nhánh `main`, kho riêng tư |
| 6 | Cảnh báo lỗi qua Telegram | Tự gửi tin khi có sự cố |

### Đã hoàn thành (trên máy công ty — ngày 14/09/2026)

| # | Hạng mục | Chi tiết |
|---|---|---|
| 1 | Kéo code từ GitHub | Về `D:\Buddy Work AI\2026-09-14-07-50-57` |
| 2 | Token Meta 60 ngày | Hết hạn **** (xem mục 2 bên dưới — KHÁC máy nhà) |
| 3 | Bot Telegram riêng | `@boongbonbap_QuangDai_bot` ("Bot Báo Cáo Company👍") |
| 4 | 3 lịch tự động | Đã xác minh độc lập bằng cách đọc lịch trong Windows |
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
   → nhớ sửa dòng REPORT_SLOTS trong .env cho đúng máy này
5. Bấm cai-dat-nguoi-truc.bat (chuột phải → Run as administrator nếu bị chặn quyền)
6. Chạy python report.py để kiểm tra
7. Nhắn "còn sống không?" cho bot Telegram để kiểm tra Người trực
```

> ⏳ **Lưu ý:** từ 28/09/2026 quy trình cài đổi — không còn bước `bat-chay-bu.bat`.
> File `HUONG-DAN-MAY-CONG-TY.md` đã được cập nhật theo.

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

File `cai-dat-nguoi-truc.bat` **tự dò Python**. Nếu không tìm thấy, nó sẽ báo lỗi và hướng dẫn cách cài.
(File `cai-dat-lich.bat` cũ cũng tự dò, nhưng chỉ dùng khi quay lại cách cũ.)

---

## 📁 CẤU TRÚC FILE QUAN TRỌNG

| File | Vai trò |
|---|---|
| `report.py` | **Script chính** — lấy số liệu Meta, gửi Telegram |
| `dashboard.py` | Tạo file `dashboard.html` xem báo cáo |
| `doi-token-60-ngay.py` | Gia hạn token Meta lên 60 ngày |
| `kiem-tra-token.py` | 🔍 **Kiểm tra token** — cả Telegram lẫn Meta, và token Meta **còn sống bao lâu**. Chạy sau MỖI lần lấy token mới. Không gửi tin nhắn, không in token đầy đủ. |
| `nguoi_truc.py` | **Tiến trình thường trú** — canh mốc giờ, gọi `report.py`, nghe Telegram |
| `cai-dat-nguoi-truc.bat` | Bật Người trực (tạo lịch `NguoiTruc`, xoá 3 lịch cũ) |
| `go-nguoi-truc.bat` | Tắt Người trực |
| `cai-dat-lich.bat` | Cách cũ: bật 3 lịch rời rạc — đường lùi |
| `go-lich.bat` | Tắt 3 lịch cũ |
| `bat-chay-bu.bat` | Bật chạy bù khi lỡ giờ (cần quyền Admin) — chỉ dùng cho cách cũ |
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
- Lịch Windows: `NguoiTruc` (một lịch duy nhất, chạy khi đăng nhập). Cách cũ: `BaoCaoMetaAds_08`, `_12`, `_17`

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

> ✅ **Máy nhà đã `git pull` ngày 14/09/2026 (19:28)** — nay chạy bản mới (1 lần gọi API).

### BẢN SỬA NGÀY 14/09/2026 (tối) — CHỐNG GỬI TRÙNG BÁO CÁO

**Vấn đề:** khi máy ngủ/tắt qua nhiều mốc giờ, Windows cho **cả ba lịch chạy bù CÙNG LÚC**.
Mỗi lịch chạy `python report.py` (không truyền mốc giờ) nên đều tự chọn **mốc gần nhất**
⇒ gửi ra nhiều báo cáo **giống hệt nhau**. Đã gặp thật ngày 14/09: máy nhà ngủ cả ngày,
tới 19:30 gửi **3 báo cáo 17h trùng nhau** (kèm 3 file HTML).

**Đã sửa:** thêm cơ chế chống trùng — mỗi mốc chỉ gửi **1 lần trong ngày**. Trạng thái ghi
vào `logs/da_gui.json` (nằm trong `logs/` nên KHÔNG lên GitHub), và **chỉ ghi sau khi
Telegram báo gửi thành công** (gửi lỗi thì lần sau vẫn thử lại được). Thêm cờ `--force`
để chủ động gửi lại: `python report.py --force`.

**Đã kiểm chứng:** chạy lại cùng mốc trong ngày → in `[BO QUA] Moc 17h da duoc gui trong ngay hom nay`.

> 🔎 **Ghi chú còn tồn:** ngày hết hạn token trong tài liệu (mục 2) có thể đã cũ. Xác nhận
> bằng `python kiem-tra-token.py` — đó mới là con số đúng.

### BẢN SỬA NGÀY 28/09/2026 — TRUYỀN MỐC GIỜ VÀO LỊCH

**Vấn đề gốc:** `cai-dat-lich.bat` tạo lịch mà **không truyền mốc giờ**, nên `report.py`
phải tự đoán mốc gần nhất. Hai hậu quả, đều đã kiểm chứng bằng `logs/baocao.log`:

1. **Mốc 22h chưa từng chạy trên máy công ty.** Đếm trong `logs/baocao.log` của máy công ty
   (14/09 – 28/09): mốc 8h có 51 dòng, 12h có 37, 17h có 27, **22h có 0**. Trên máy này báo cáo
   "tổng kết cả ngày" chưa bao giờ tồn tại. (Máy nhà thì khác — mốc 22h có chạy; xem ghi chép
   ngày 12/09 trong `README.md`, mục "Ba điều cần biết".)
2. **Vẫn gửi trùng.** Đếm số lần gửi thành công theo ngày: 14/09 = 5, 15/09 = 4, 18/09 = 4,
   24/09 = 4, 28/09 = 4 (bình thường chỉ nên 3). Sáng 28/09 lúc 08:26 gửi 4 tin trùng.

**Đã sửa:** thêm tham số `--slot` cho `report.py`; `cai-dat-lich.bat` truyền mốc giờ vào
từng lịch; bỏ mốc 22h. Thêm `lich_su.py` lưu số liệu 180 ngày vào `logs/lich-su.json`.

> ⚠️ **Bài học về cách kiểm chứng:** `HANDOFF.md` trước đây ghi cơ chế chống trùng
> "đã kiểm chứng" — nhưng cách kiểm chỉ là **chạy lại tuần tự**, trong khi lỗi chỉ xuất hiện
> khi chạy **đồng thời**. Từ nay, mọi thay đổi liên quan tới lịch chạy phải được thử bằng
> **nhiều tiến trình song song**, không chỉ chạy lại một mình.

### BẢN SỬA NGÀY 28/09/2026 (tiếp) — `cai-dat-lich.bat` tự đặt thiết lập lịch

**Vấn đề, phát hiện khi cài thật:** `cai-dat-lich.bat` **xoá** lịch cũ rồi tạo lại bằng
`schtasks /Create`, mà lệnh đó **không** đặt `StartWhenAvailable`, `WakeToRun` và
`AllowStartIfOnBatteries`. Ba thiết lập này chỉ được đặt bởi `bat-chay-bu.bat`.

⇒ Mỗi lần chạy lại `cai-dat-lich.bat` là **một lần mất** tính năng chạy bù và tự thức máy.
Đã xảy ra thật ngày 28/09/2026: sau khi cài lại, `StartWhenAvailable` và `WakeToRun` chuyển từ
`True` sang `False`, còn `DisallowStartIfOnBatteries` từ `False` sang `True` — nghĩa là máy ngủ
đúng giờ sẽ **không** có báo cáo bù, đúng cái tính năng cần nhất.

**Đã sửa:** `cai-dat-lich.bat` giờ tự đặt luôn 3 thiết lập đó sau khi tạo lịch, dùng đúng đoạn
PowerShell của `bat-chay-bu.bat`, và in ra phần kiểm tra để thấy ngay `chay bu=True tu thuc=True`.
Nếu chạy mà không có quyền Admin, nó in cảnh báo rõ ràng thay vì im lặng làm mất thiết lập.

**Ba điều phải nhớ khi bàn giao:**
- `cai-dat-lich.bat` **phải chạy bằng quyền Administrator**. Không có quyền Admin thì `schtasks`
  có thể vẫn tạo được lịch, nhưng `Set-ScheduledTask` (phần đặt 3 thiết lập) sẽ báo `Access is denied`.
- `bat-danh-thuc-may.bat` **không** đụng tới lịch — nó chỉ gọi `powercfg` để bật "Allow wake timers"
  ở mức Windows. Việc chạy lại `cai-dat-lich.bat` **không** làm mất thiết lập này. Tài liệu cũ ghi
  sai rằng file đó cũng gọi `Set-ScheduledTask`.
- Kiểm chứng nhanh bằng `Get-ScheduledTask` (đọc `StartWhenAvailable`, `WakeToRun`,
  `DisallowStartIfOnBatteries`, và `Args` phải chứa `--slot`).

### BẢN SỬA NGÀY 28/09/2026 (tiếp) — NGƯỜI TRỰC THAY BA LỊCH

**Vấn đề gốc còn lại:** ba lịch Windows rời rạc không biết gì về nhau. `--slot` (Giai đoạn 1)
đã chữa được phần lớn, nhưng khi máy thức dậy buổi sáng, cả ba lịch vẫn chạy bù cùng lúc và
`determine_period()` ánh xạ mốc 12, 17, 22 đều thành "hôm nay" ⇒ hai tin có **số giống hệt
nhau**, chỉ khác dòng tiêu đề. Đếm trong nhật ký: 4 tin trùng giảm còn 3, chưa hết.

**Đã sửa:** thay ba lịch bằng **một** tiến trình thường trú `nguoi_truc.py`, chạy qua lịch
Windows duy nhất `NguoiTruc`. Nó biết rõ lịch của chính nó nên **không đoán mốc**, và khi
khởi động chỉ gửi **một** báo cáo bù cho mốc gần nhất bị lỡ.

**Bốn quyết định kỹ thuật, kèm lý do:**

1. **`nguoi_truc.py` gọi `report.py` bằng tiến trình riêng** (`subprocess`), kèm `--slot N`.
   Không tách phần gửi của `report.py` thành hàm như bản thiết kế mục 5.4 nói. Lý do: lỗi
   trong `report.py` không giết Người trực; và không phải đụng vào phần tính tiền.
2. **Lịch `NguoiTruc` tạo bằng PowerShell `Register-ScheduledTask`**, không dùng
   `schtasks /Create`. Lý do: `schtasks` không đặt được "Restart on failure" và "không giới
   hạn thời gian chạy"; thêm nữa đường dẫn truyền qua **biến môi trường** nên tránh hẳn bẫy
   dấu nháy của `/TR` đã tốn một vòng sửa ngày 28/09.
3. **Mốc giờ chuyển vào `.env`** (khoá `REPORT_SLOTS`). `determine_period()` không còn viết
   cứng `if slot_hour == 8`; nó nhận `moc_sang_bao_cao` với mặc định 8, và `main()` truyền
   `moc_sang(danh_sach_moc)` = mốc nhỏ nhất.
   **Giá trị đang dùng: cả hai máy đều `REPORT_SLOTS=8,12,17`** (Đại chốt 28/09/2026, bỏ mốc
   22h ở cả hai máy). Không có khoá thì mặc định là `8,12,17,22` — tức mốc 22h quay trở lại.
4. **`cai-dat-nguoi-truc.bat` tự xoá ba lịch cũ.** Bản thiết kế mục 10 ghi hai bước riêng,
   nhưng để hai lịch cùng sống là hai nguồn gửi báo cáo, mà cơ chế chống trùng cũ đọc-rồi-ghi
   **không có khoá** nên hai tiến trình chạy sát nhau vẫn lọt.

**Nhịp tim ghi mỗi 30 phút, không phải mỗi vòng.** Bản thiết kế mục 5.1 nói "mỗi vòng"; mỗi
vòng là 30 giây ⇒ ~2.880 dòng/ngày, làm ngập `logs/baocao.log` — chính file mở đầu tiên khi
có sự cố. Phép thử sức khoẻ thật là lệnh "còn sống không?" qua Telegram.

**Đã kiểm chứng (bằng kiểm thử tự động, không phải chạy tay):** thực dậy lúc 12h05 khi chưa
gửi gì ⇒ gửi **đúng một** báo cáo mốc 12h, mốc 8h ghi nhật ký bỏ qua. Đây là bài kiểm thử
quan trọng nhất của giai đoạn.

**Giới hạn đã biết, cố ý không sửa ở giai đoạn này:**

- **Mốc 8h bị bỏ qua khi khởi động muộn.** Máy bật lúc 13h mà chưa gửi gì thì chỉ gửi báo cáo
  mốc 12h; mốc 8h (báo cáo đầy đủ cả ngày hôm trước) bị bỏ. Hệ quả: `logs/lich-su.json` có
  thể thiếu bản ghi **đầy đủ** của ngày hôm trước, chỉ còn bản **một phần** (mốc 17h của ngày
  đó). Giai đoạn 3 cần biết điều này khi so sánh với kỳ trước.
- **Một mốc chỉ được thử tối đa 3 lần trong ngày, cách nhau 5 phút.** Token Meta chết hẳn thì
  Đại nhận tối đa 3 tin cảnh báo cho mỗi mốc. Đây là chủ ý: bản thiết kế mục 7 (tự xử lý lỗi,
  tự gia hạn token) thuộc Giai đoạn 5.
- **`report.py --dry` vẫn ghi vào `logs/lich-su.json`** — hành vi có từ Giai đoạn 1, không đổi.

**Lỗ hổng phát hiện khi cài thật (28/09, ~14:26): `cai-dat-nguoi-truc.bat` phải khởi động luôn.**
Lịch `NguoiTruc` kích hoạt **khi đăng nhập**, nên sau khi bấm file, hệ thống KHÔNG chạy ngay.
Mà file đó lại **xoá ba lịch cũ** ⇒ từ lúc bấm đến lần đăng nhập sau là **khoảng trống không có
gì gửi báo cáo**. Đã xảy ra thật: Đại bấm file lúc ~14:20, lịch `State=Ready` nhưng
`LastRunTime=11/30/1999` (chưa từng chạy), không có tiến trình nào ⇒ nhắn bot lúc 14:25 không
ai trả lời. **Đã sửa:** `.bat` giờ gọi `Start-ScheduledTask` ngay sau khi tạo lịch, và phần
kiểm tra in thêm `Trang thai` + dòng `Tien trinh: dang chay (PID ...)`.

**Lỗ hổng thứ hai (phát hiện 14:39 cùng ngày): lịch không tự bật lại khi tiến trình chết.**
Tiến trình chạy từ 14:26:29, trả lời được một tin lúc 14:31:07, rồi **chết** —
`LastTaskResult = 3221225786` = `0xC000013A` (`STATUS_CONTROL_C_EXIT`) ⇒ **bị kết thúc cưỡng
bức từ bên ngoài**, không phải lỗi chương trình (nhật ký không có dòng lỗi nào). Nhiều khả năng
do phiên làm việc của trợ lý AI dọn dẹp tiến trình khi kết thúc. **Vấn đề thật:** lịch chỉ có
`-AtLogOn`, nên tiến trình chết giữa ngày thì **nằm chết tới lần đăng nhập sau**;
`-RestartInterval/-RestartCount` không cứu được vì đó là "restart on **failure**", còn đây là
bị giết. **Đã sửa:** `.bat` tạo **HAI trigger** — `-AtLogOn` + `-Once -RepetitionInterval 5 phút`
(không đặt duration = lặp vô hạn). Kết hợp `MultipleInstances=IgnoreNew` ⇒ đang chạy thì lần lặp
bị bỏ qua, đã chết thì được bật lại trong 5 phút. Đây là cơ chế tự chữa bệnh.

> ⚠️ **`Register-ScheduledTask -Force` lên lịch ĐÃ CÓ cần quyền Administrator** (`Access is
> denied` nếu không). Vì vậy nâng cấp lịch đang tồn tại **bắt buộc Đại tự bấm `.bat`** — trợ lý
> AI không làm hộ được. Tạo lịch mới thì không cần quyền Admin.

> Ghi chú kèm: Người trực **bỏ qua mọi tin nhắn đến trước lúc nó khởi động** (xả tồn đọng bằng
> `offset=-1`). Nên nhắn thử bot phải làm **sau** khi nó chạy; nhắn trước là mất tin, không phải lỗi.
> Hệ quả: **mỗi lần khởi động lại đều nuốt tin đang chờ** — nhắn lại là được.

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
2. **File trống hoàn toàn** → chưa cài gì → bấm `cai-dat-nguoi-truc.bat`
3. **Có dòng nhịp tim `NGUOI TRUC: nhip tim` nhưng không có báo cáo** → Người trực sống,
   nhưng việc gửi thất bại → tìm dòng `NGUOI TRUC: gui moc ... THAT BAI`
4. **Có dòng "THAT BAI"** → đọc lý do; nếu ghi `Session has expired` → token Meta hết hạn
5. Telegram không nhận được → kiểm tra token Telegram + đã bấm Start với bot chưa
6. **Nhắn bot không trả lời** → mở Task Manager, tìm `python.exe` chạy `nguoi_truc.py`.
   Không có → bấm `cai-dat-nguoi-truc.bat` lại

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
| **14/09/2026 12:00** | Ba mốc tự chạy đầu tiên của máy công ty (12h, 17h, 22h) — ⚠️ **đã sửa:** nhật ký máy công ty chỉ có 12h và 17h, **mốc 22h có 0 dòng** (xem mục "BẢN SỬA NGÀY 28/09/2026" ở trên) |
| **18/09/2026** | Token GitHub cũ `buddy-web-sync` hết hạn (không ảnh hưởng dự án này) |
| **10/11/2026** | ⚠️ Token Meta **máy nhà** hết hạn |
| **** | ⚠️ Token Meta **máy công ty** hết hạn |

---

*File này được cập nhật mỗi khi có thay đổi quan trọng. Nếu thấy thông tin lỗi thời, hãy kiểm tra `git log` để biết bản mới nhất.*
