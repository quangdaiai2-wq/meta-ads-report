# HANDOFF — SỔ BÀN GIAO CÔNG VIỆC

**Cập nhật lần cuối:** 29/09/2026 — **Giai đoạn 4 xong**: Đại nhắn bot hỏi số liệu và được trả lời
(4 công cụ đọc sổ lịch sử). `270/270` kiểm thử đạt. Trước đó cùng ngày: hai bảng xếp hạng đổi tiêu
chí sang **chi phí mỗi đơn**, và chữa lỗi nặng **bảng mã cp1252** làm báo cáo ngừng gửi.

> ⏭️ **Việc tiếp theo nằm ở MÁY NHÀ:** `git pull` để nhận GĐ3 + GĐ4, rồi thêm `GEMINI_API_KEY`
> vào `.env` (`.env` không đi theo `git pull`). Xem `HUONG-DAN-MAY-NHA.md` và
> `HUONG-DAN-LAY-CHIA-KHOA-AI.md`.

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
| 5 | Đẩy code lên GitHub | Nhánh `main`, kho riêng tư. **Mốc mới nhất 28/09/2026: `37d927a`** (gồm cả GĐ3) |
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

- ⏳ **Máy nhà chưa cập nhật code mới** — cần `git pull` để nhận **GĐ3 (phần nhận định AI)** và
  **GĐ4 (trả lời câu hỏi)**, rồi thêm `GEMINI_API_KEY` vào `.env` (`.env` không đi theo `git pull`).
  👉 **Hướng dẫn từng bước: xem file `HUONG-DAN-MAY-NHA.md`**
- ⏳ **Giai đoạn 5 chưa làm:** tự xử lý lỗi (tự chờ và thử lại khi Meta chặn tạm, cảnh báo khi số
  liệu bất thường) + **tự gia hạn token Meta**. Phần tự gia hạn **chưa thử lần nào** — cần thử
  trước khi hứa bất cứ điều gì.

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
| `ai.py` | **Lớp AI** — viết 3–5 câu nhận định (GĐ3) **và** trả lời câu hỏi có vòng lặp công cụ (GĐ4). Không tính số, không gọi Meta, không gửi tin |
| `cong_cu.py` | **Bốn công cụ cho AI** — `lay_mot_ngay` · `lay_khoang` · `xep_hang_camp` · `so_sanh`. Thuần đọc `logs/lich-su.json`, **không chạm mạng**. Kèm `moc_thoi_gian()` tính phạm vi ngày |
| `tests/` | Kiểm thử tự động (270 bài). **Không gọi mạng**, không tốn hạn mức Meta/Gemini |
| `chay-kiem-thu.bat` | Bấm đúp là chạy 270 bài kiểm thử — **không tốn lượt AI** |
| `HUONG-DAN-LAY-CHIA-KHOA-AI.md` | Hướng dẫn lấy chìa khoá Gemini + giải thích **hai model, hai trần riêng** |
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
- **Gemini — hai model, hai trần riêng (20 lượt/ngày MỖI model):**
  - `GEMINI_MODEL` = `gemini-3.6-flash` → viết phần nhận định trong báo cáo
  - `GEMINI_MODEL_HOI_DAP` = `gemini-3.8-flash` → trả lời câu hỏi của Đại
  - `GEMINI_MODEL_HOI_DAP_DU_PHONG` = `gemini-3.5-flash` → dùng khi model trên trả 503/404
  - `gemini-2.5-flash` **không dùng được nữa** (`404: no longer available to new users`)

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

### BẢN SỬA NGÀY 28/09/2026 (tiếp) — GIAI ĐOẠN 3: PHẦN NHẬN ĐỊNH DO AI VIẾT

**Thêm gì:** file mới `ai.py`. Mục `🔵 NHẬN ĐỊNH` trong báo cáo Telegram nay có **3–5 câu tiếng
Việt do AI viết**, thay vì chỉ hai bảng xếp hạng camp như trước.

**Sáu điều bắt buộc nhớ:**

1. **Số liệu và phép so sánh vẫn do CODE làm, không giao cho AI.** Đây là điểm khác lớn nhất so
   với bản thiết kế mục 6.1. Lý do: khi để AI tự đối chiếu hai dòng số, nó dễ đọc sai mà câu văn
   vẫn trôi chảy. `ai.bang_so_sanh()` tính sẵn **cột `chenh lech`**, AI chỉ chép lại.
   Quyết định này ra từ việc **gọi Gemini thật** ngày 28/09/2026, không phải suy đoán.
2. **`soan_prompt()` KHÔNG nhận tham số `env`** ⇒ về mặt cấu trúc nó **không thể** làm lộ token
   cho AI. Chỉ `goi_gemini(env, ...)` mới chạm `env`, và chỉ để lấy chìa khoá + tên model.
3. **Suy giảm êm — đã kiểm chứng thật.** AI lỗi (mất mạng / sai chìa khoá / hết hạn mức) thì
   báo cáo **vẫn gửi đầy đủ**: mục NHẬN ĐỊNH hiện một dòng ghi chú, hai bảng xếp hạng vẫn nguyên.
   Cách kiểm: chạy `report.py --slot 8 --dry` trong một thư mục tạm với `.env` **đã xoá dòng**
   `GEMINI_API_KEY` → in ra `⚠️ Phần nhận định do AI viết tạm không có (lý do: thieu
   GEMINI_API_KEY trong .env)` và `grep -c "Camp hiệu quả|Camp kém hiệu quả"` = 2.
4. **Chỉ mốc 8h mới so sánh với kỳ trước.** Mốc 8h là báo cáo **trọn ngày hôm qua**. Mốc 12h/17h
   là báo cáo **một phần** của ngày hôm nay; lịch sử không lưu số theo từng giờ nên **không thể**
   so "0h–17h hôm nay" với "0h–17h hôm qua". Hàm quyết định: `report.la_bao_cao_tron_ngay(slot,
   danh_sach_moc)` — so với `moc_sang()`, không viết cứng số 8.
5. **Giới hạn ~7 ngày đầu:** `logs/lich-su.json` chỉ mới có **1 bản ghi** (từ 12h ngày 28/09)
   ⇒ mốc 8h chưa có kỳ trước để so. Lúc đó AI **chỉ mô tả**, bảng ghi `(khong so sanh)`.
   **Không phải lỗi.** Đừng "sửa" bằng cách bắt AI so bừa.
6. **Tên model không viết cứng trong code.** `ai.py` đọc khoá `GEMINI_MODEL` trong `.env`, thiếu
   thì dùng `MODEL_MAC_DINH = "gemini-3.6-flash"`. Lỗi **HTTP 404** nghĩa là **tên model sai**,
   không phải chìa khoá sai. Cách dò danh sách model: xem `HUONG-DAN-LAY-CHIA-KHOA-AI.md`.

**NĂM thay đổi so với kế hoạch đã duyệt — đọc kỹ:**

| # | Kế hoạch ghi | Thực tế thi công | Vì sao |
|---|---|---|---|
| 1 | `SO_LAN_THU_LAI = 1`, `CHO_GIUA_HAI_LAN = 3` | **`SO_LAN_THU_LAI = 2`**, `CHO_GIUA_HAI_LAN = 5` | Lần gọi Gemini **đầu tiên** khi kiểm chứng trả **503 hai lần liên tiếp** — thử lại 1 lần vẫn hỏng, phải chạy lại cả tiến trình. Chi phí: chậm nhất ~190 giây thay vì ~125. Đổi lại tỉ lệ có được phần nhận định cao hơn hẳn |
| 2 | Task 4 "cần Đại duyệt riêng" | **Đã làm** | Đại giao toàn quyền quyết định. Và bằng chứng đã có sẵn trong chính buổi thi công: **3 lần `--dry`** đã ghi hẳn một bản ghi `2026-09-27 / moc=8 / day_du=True` vào lịch sử. GĐ3 lấy lịch sử làm số kỳ trước nên ghi bẩn là AI nhận định sai. **Muốn bỏ thì nói — chỉ cần xoá hàm `co_nen_ghi_lich_su` và trả lại điều kiện `args.mock is None`** |
| 3 | `test_gap_503_hai_lan_thi_bo_cuoc_chu_khong_lap_vo_han` | đổi tên thành `test_gap_503_lien_tuc_thi_bo_cuoc_chu_khong_lap_vo_han`, **thêm** phép kiểm số lần thử | Tên cũ nói "hai lần" nhưng với `SO_LAN_THU_LAI = 2` thì là ba lần. Thêm `assertEqual(dem["n"], ai.SO_LAN_THU_LAI + 1)` để không bị hụt lần thử về sau mà không ai biết |
| 4 | `HUONG_DAN` viết **không dấu** như mọi chuỗi kỹ thuật khác | `HUONG_DAN` **viết có dấu**, thêm quy tắc "Viết tiếng Việt CÓ DẤU đầy đủ" | **Lỗi thật, bản kiểm chứng một lần của kế hoạch đã bỏ sót.** Gemini **bắt chước giọng văn của chính câu lệnh**: câu lệnh không dấu thì nó trả về không dấu (`Trong ngay 27/09/2026, tai khoan quang cao ghi nhan...`), đọc rất mệt. Gặp khoảng **50% số lần**. Đã kiểm chứng lại **3/3 lần ra có dấu đầy đủ**. Có bài kiểm `test_prompt_bat_buoc_viet_co_dau` để không ai xoá mất quy tắc này |
| 5 | Lỗi AI chỉ trả về `HTTP <mã>` | Dịch sẵn sang tiếng Việt + kèm `error.status` | Dòng ghi chú cũ ghi `HTTP 429` — Đại đọc **không biết là hết hạn mức hay sai chìa khoá**. Nay ghi: `HTTP 429 - het han muc goi AI, thu lai sau [RESOURCE_EXHAUSTED]`. Bảng dịch ở `ai.Y_NGHIA_LOI` |

**Trần miễn phí của Gemini — đo được thật:** **20 lượt/ngày** cho `gemini-3.6-flash`
(`quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier`). Dùng thật chỉ 3 lượt/ngày nên
thoải mái, **nhưng chạy thử `report.py` cũng tốn lượt** — thi công hôm nay đã chạm trần vì chạy
kiểm chứng nhiều lần. Hệ quả đã kiểm chứng: báo cáo **vẫn gửi đầy đủ**, chỉ thiếu phần nhận định.
Đã ghi cảnh báo này vào `README.md` và `HUONG-DAN-LAY-CHIA-KHOA-AI.md`.

**Bằng chứng kiểm chứng mạnh nhất của giai đoạn** (chạy thật, có chìa khoá, trong thư mục tạm):
tiêm một bản ghi kỳ trước vào lịch sử rồi chạy `report.py --slot 8 --dry`. AI viết 4 câu, dùng
**20 con số**, và phép đối chiếu tự động báo:

```
So AI viet ma KHONG co trong du lieu: KHONG CO (dat)
```

Nghĩa là **không một con số nào bị bịa** — kể cả cột chênh lệch và phần trăm.

**Kiểm thử:** `155/155` đạt (trước GĐ3 là 105). Thêm `tests/test_ai.py` (32 bài) và 18 bài mới
trong `tests/test_report.py`. Kiểm thử **không gọi mạng** — mọi lời gọi Gemini đều đi qua hàm
giả tiêm vào bằng `goi_mang_fn=`.

**ĐÃ SỬA ngày 28/09/2026 (sau khi GĐ3 thi công xong) — hai bảng xếp hạng không còn trùng nhau.**

Lỗi cũ: `compute_stats()` **không loại `good` khỏi `bad`**. Bảng "hiệu quả" lấy từ **trên xuống**
theo số lượt mua, bảng "kém hiệu quả" lấy từ **dưới lên**; tài khoản ít camp thì hai đầu gặp nhau.
Đã đo được thật: tài khoản **5 camp đều có đơn ⇒ CẢ 5 nằm ở cả hai bảng**, kể cả camp tốt nhất
(9 lượt mua bị xếp vào "kém hiệu quả"). Tài khoản 13 camp trở lên thì **không** bị — nên lỗi này
ẩn rất lâu.

Cách sửa: `bad` **loại trừ mọi camp đã nằm trong `good`** theo `campaign_id`.

**Hệ quả phải biết (cố ý):** tài khoản ít camp thì bảng "kém hiệu quả" **ngắn lại, hoặc trống** —
báo cáo sẽ ghi *"Không có camp nào kém hiệu quả."* Đó là **đúng**, vì khi mọi camp đều ra đơn thì
thật sự không có camp nào kém. **Đừng "sửa" lại cho đủ 5 dòng** — làm thế là quay lại lỗi cũ.

Kiểm thử: `161/161` đạt. Thêm 7 bài trong `tests/test_report.py` (class `TestKhongLapGiuaHaiBang`),
trong đó có một bài quét **mọi cỡ tài khoản** 1/2/3/5/6/8/13/30 camp. Kiểm chứng trên dữ liệu
thật 28/09: 13 camp vẫn ra đủ 5+5 dòng, không trùng.

> 📌 **Một bài kiểm thử CŨ đã phải sửa:** `test_good_va_bad_van_nhu_cu` khẳng định `len(bad) == 5`
> cho bộ dữ liệu 6 camp — con số đó **khoá lại chính lỗi này**. Đã đổi tên thành
> `test_bang_kem_khong_lap_bang_hieu_qua` và khẳng định đúng hành vi mới. Nếu thấy bài cũ ở đâu
> khác thì đừng khôi phục.

### BẢN SỬA NGÀY 29/09/2026 — HAI BẢNG XẾP HẠNG ĐỔI TIÊU CHÍ + HIỆN CHI PHÍ MỖI ĐƠN

**1. Tin nhắn Telegram nay hiện "Mỗi đơn: X VND"** cho từng camp ở cả hai bảng.
Trước đây con số này **chỉ có trong `dashboard.html`** (cột `CPR`) — tin nhắn Telegram không có,
nên muốn biết camp nào đắt/rẻ thì phải tự chia nhẩm.
Thêm `report.chi_phi_moi_don(r)` và `report.mo_ta_moi_don(r)`. Camp 0 đơn **không** in "Mỗi đơn"
(chia cho 0 là vô nghĩa; in "0 đồng mỗi đơn" sẽ khiến camp tệ nhất trông như rẻ nhất).
Prompt gửi AI cũng có thêm cột `chi phi moi don` — AI **đã dùng ngay** ở lần chạy đầu
("chi phí mỗi đơn là 274.537 d").

**2. Bảng "Camp hiệu quả" đổi từ xếp theo SỐ ĐƠN sang xếp theo CHI PHÍ MỖI ĐƠN.**
Lý do: xếp theo số đơn là đo **quy mô**, không phải **hiệu quả** — trái với chính tên bảng.

**Bằng chứng đo được (đây là lý do thay đổi, không phải cảm tính):** lấy 7 ngày thật
22–28/09/2026, so hai cách xếp:

| | Số ngày |
|---|---|
| Hai cách chọn ra **danh sách camp KHÁC NHAU** | **6/7 ngày** |
| Hai cách chỉ khác **thứ tự** | 1/7 ngày |

Ví dụ ngày 28/09: cách cũ đưa vào bảng một camp **775.150 đ/đơn** và bỏ sót một camp
**405.671 đ/đơn**. Cách mới đưa đúng camp rẻ hơn vào.

**Quy tắc xếp hạng mới** (`report.khoa_xep_hang`): sắp theo chi phí mỗi đơn tăng dần, **nhưng camp
chỉ có 1 đơn bị đẩy xuống sau** những camp đã có từ 2 đơn trở lên.
Lý do có cái chốt 1 đơn: nếu xếp thuần theo chi phí mỗi đơn thì ngày 28/09 một camp
**1 đơn, 63.451 đ/đơn** nhảy lên **đứng đầu bảng** — rẻ nhất ngày, nhưng chỉ là **một đơn may mắn**.

**Hai điều phải nhớ:**

- **Bảng nay có thể xếp một camp 3 đơn LÊN TRÊN một camp 10 đơn** (vì đơn của nó rẻ hơn). Đây là
  **chủ ý**, không phải lỗi. Báo cáo đã in rõ tiêu chí ngay dưới dòng tiêu đề bảng:
  *"(xếp theo chi phí mỗi đơn, rẻ nhất trước — không phải theo số đơn)"*.
  **Đừng xoá dòng đó** — thiếu nó thì Đại sẽ tưởng báo cáo sai.
- **Muốn quay lại cách cũ:** sửa `khoa_xep_hang` thành `key=purchase_count, reverse=True` và bỏ
  `chỉ 1 đơn`. Chỉ một chỗ trong `report.py`.

**Điều chưa biết, đã ghi cả vào `README.md`:** báo cáo chỉ có **số đơn**, không có **giá trị mỗi
đơn**. Nên "chi phí mỗi đơn" chưa phải "hiệu quả" đầy đủ — nếu biên lợi nhuận mỗi đơn của Đại cao
thì camp đắt vẫn đáng chạy. **Việc còn lại cho Giai đoạn 4:** hỏi Đại lợi nhuận mỗi đơn bao nhiêu,
rồi mới nói được camp nào thật sự có lãi.

Kiểm thử: `175/175` đạt (thêm 10 bài). Kiểm chứng trên dữ liệu thật 28/09: camp 775.150 đ/đơn
không còn trong bảng "hiệu quả"; hai camp 3 đơn rẻ hơn (405.671 và 408.493) được đưa vào.

### 🚨 BẢN SỬA NGÀY 29/09/2026 — BÁO CÁO NGỪNG GỬI VÌ LỖI BẢNG MÃ TIẾNG VIỆT

**Đây là lỗi nặng nhất từ trước tới nay: báo cáo NGỪNG GỬI hoàn toàn.**

**Triệu chứng trong `logs/baocao.log`:**

```
NGUOI TRUC: report.py moc 17h thoat voi ma 1: 3.12\Lib\encodings\cp1252.py", line 19, in encode
UnicodeEncodeError: 'charmap' codec can't encode character '\u1ed1' in position 1
```

`\u1ed1` là chữ **ố** trong "**Số** tiền đã chi tiêu". `report.py` thoát với mã 1 ⇒ **không gửi
Telegram**. Vì `print(report)` nằm **TRƯỚC** `send_telegram()` nên chết là chết trước khi gửi.

**Thiệt hại thật:** báo cáo ngừng gửi từ **17h ngày 28/09/2026**. Cụ thể:

| Mốc | Kết quả |
|---|---|
| 28/09 8h, 12h | Đã gửi (trước khi lỗi xuất hiện) |
| **28/09 17h** | ❌ **KHÔNG BAO GIỜ GỬI** — thử 6 lần, cả 6 thất bại |
| 29/09 8h | ❌ thất bại 2 lần đầu, ✅ **gửi được sau khi sửa** (08:10:36) |

**Nguyên nhân gốc:** `nguoi_truc.py` gọi `report.py` bằng `subprocess.run(capture_output=True)`.
Từ Giai đoạn 2, tiến trình con **không còn console** và stdout là **đường ống**, nên Python lấy
bảng mã theo **locale của Windows** — máy này là **cp1252** (bảng mã Tây Âu, không có chữ có dấu
tiếng Việt). `print()` báo cáo ⇒ nổ.

**Vì sao trước đây không bị:** ba lịch cũ chạy `report.py` trực tiếp, **không có console và không
có đường ống** ⇒ `sys.stdout` là `None` ⇒ `print()` **im lặng không làm gì** ⇒ không lỗi.
Chính `capture_output=True` của Giai đoạn 2 đã **đưa bảng mã vào cuộc**. Đây là lỗi **do GĐ2 gây
ra nhưng chỉ lộ ra khi Người trực gửi báo cáo thật lần đầu** (17h ngày 28/09).

**Đã sửa hai lớp (cố ý làm cả hai, để một lớp hỏng thì lớp kia vẫn cứu):**

1. `report.py` — thêm `_ep_stdout_utf8()`, **tự chạy ngay khi nạp mô-đun**: đổi `stdout`/`stderr`
   sang UTF-8 với `errors="replace"`. Lớp này đủ để cứu, và **cứu được cả tiến trình Người trực
   cũ đang chạy** vì `report.py` được nạp mới ở mỗi lần gọi.
2. `nguoi_truc.py` — `gui_bao_cao()` nay truyền `encoding="utf-8"`, `errors="replace"` và
   `env` có `PYTHONIOENCODING=utf-8`. Lớp này để nhật ký đọc được, không bị chữ rác.

**Kiểm chứng (tái hiện được):** đặt `PYTHONIOENCODING=cp1252` rồi chạy `report.py --slot 8 --dry`
trong tiến trình con có `capture_output=True`:

| | Mã thoát |
|---|---|
| Trước khi sửa | **1** — `UnicodeEncodeError`, đúng ký tự `\u1ed1`, đúng vị trí 1 |
| Sau khi sửa | **0** — báo cáo in ra đủ, tiếng Việt có dấu còn nguyên |

Kiểm thử: `185/185` đạt (thêm 10 bài, gồm 5 bài cho `_ep_stdout_utf8` và 5 bài khoá việc truyền
`encoding="utf-8"` trong `nguoi_truc.py`).

> ⚠️ **BÀI HỌC PHẢI NHỚ:** mọi chỗ **in chữ có dấu ra ngoài** trong tiến trình chạy qua
> `subprocess`/Task Scheduler **phải ép UTF-8 tường minh**. Đừng bao giờ tin vào bảng mã mặc định
> của Windows — nó là cp1252, không có chữ Việt có dấu.
>
> 🔎 **Cách nhận ra nhanh lỗi này về sau:** nhật ký có `UnicodeEncodeError` + `charmap` + `cp1252`,
> và `report.py ... thoat voi ma 1`. Khi đó **báo cáo không gửi được**, không phải lỗi Meta/Telegram.

### BẢN SỬA NGÀY 29/09/2026 (tiếp) — GIAI ĐOẠN 4: NGƯỜI TRỰC TRẢ LỜI CÂU HỎI

**Thêm gì:** file mới `cong_cu.py`. Đại nhắn bot một câu hỏi về số liệu và **nhận được câu trả lời
có số thật**, lấy từ sổ lịch sử. Kế hoạch đầy đủ:
`docs/superpowers/plans/2026-09-29-giai-doan-4-tra-loi-cau-hoi.md`.

**Kiến trúc:** AI **xin** hệ thống lấy số (gọi công cụ), chứ không tự bịa. Bốn công cụ:
`lay_mot_ngay` · `lay_khoang` · `xep_hang_camp` · `so_sanh`.

**Bảy điều bắt buộc nhớ:**

1. **Hai model, hai trần riêng.** Trần miễn phí Gemini tính **riêng cho từng model**
   (`quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier`, 20 lượt/ngày). Nên:
   báo cáo dùng `GEMINI_MODEL` (`gemini-3.6-flash`), hỏi đáp dùng `GEMINI_MODEL_HOI_DAP`
   (`gemini-3.8-flash`), dự phòng `GEMINI_MODEL_HOI_DAP_DU_PHONG` (`gemini-3.5-flash`).
   **Đừng gộp lại một model** — hỏi đáp sẽ ăn hết lượt của báo cáo.
2. **`TOI_DA_LUOT_CONG_CU = 3`, không phải 5.** Phép thử thật cho thấy AI cần **đúng 3 lượt công cụ**
   rồi trả lời ở lượt 4. Để 5 thì một câu hỏi tốn 6 lượt AI ⇒ chỉ 3 câu là hết trần trong ngày.
   Lượt cuối cùng **gọi KHÔNG kèm công cụ** để buộc AI trả lời bằng chữ.
3. **`thoughtSignature` phải giữ nguyên.** Response của Gemini 3.x có trường này trong part.
   `ai.tra_loi()` gửi lại **nguyên `content` của model**, không bóc ra ghép lại. Đã kiểm chứng thật.
4. **Số tiền do CODE định dạng, không để AI tự thêm dấu.** Lần gọi AI đầu tiên trả về
   `20319895 đồng` — đọc rất mệt. Sửa bằng cách công cụ trả thêm trường `*_hien_thi` là **chuỗi đã
   định dạng sẵn** (`"20.319.895"`), câu lệnh bắt AI chép từ đó. **Đừng "sửa" bằng cách bảo AI tự
   thêm dấu** — làm vậy là để AI *sửa số*, đúng rủi ro đã tránh ở GĐ3.
5. **Phạm vi ngày do CODE tính.** `cong_cu.moc_thoi_gian()` chèn vào câu lệnh một mục MỐC THỜI GIAN.
   Lý do: trong phép thử, AI tự hiểu *"tuần này"* thành **28/09→29/09 (hai ngày)**. Phạm vi thời
   gian là một phép tính.
6. **Câu lệnh CẤM markdown.** AI viết `**...**` và gạch đầu dòng, Telegram hiện rất rối. Có quy tắc
   "tối đa 8 câu, văn xuôi liền mạch, không dấu sao / dấu thăng / gạch đầu dòng".
7. **`NguoiTruc` có thêm `tra_loi_ai_fn`.** Đây là **lỗi thật do bước dựng thử bắt được**: thiếu
   đường tiêm này thì **bộ kiểm thử gọi AI thật** — tốn lượt AI và phụ thuộc mạng. Khi viết kiểm
   thử đi qua `NguoiTruc`, **luôn tiêm hàm giả**.

**BA thay đổi so với kế hoạch đã duyệt — cả ba đều do dựng thử / kiểm chứng thật bắt được:**

| # | Kế hoạch ghi | Thực tế | Vì sao |
|---|---|---|---|
| 1 | Không nhắc gì tới `NguoiTruc` | Thêm `tra_loi_ai_fn` vào `NguoiTruc.__init__` và `xu_ly_tin` | Thiếu thì `TestXuLyTin` **gọi AI thật**. Lỗi hiện ra khi chạy kiểm thử trong thư mục tạm **không có `GEMINI_API_KEY`** |
| 2 | Không nhắc gì tới định dạng số tiền | Công cụ trả thêm `tong_hien_thi`, `chi_tieu_hien_thi`, `chi_phi_moi_don_hien_thi`, `chenh_lech_hien_thi` | Lần gọi Gemini thật đầu tiên ra `20319895 đồng`. Xem điều 4 ở trên |
| 3 | Chỉ nói sửa `test_hoi_cau_khac_thi_noi_ro_chua_co_AI` | Phải sửa **HAI** bài cũ: thêm `test_cau_hoi_rong_cung_tra_loi_chua_co_AI` | Bài thứ hai nằm ở cuối lớp, kế hoạch bỏ sót; cả hai đều khẳng định có chữ `"giai đoạn sau"` |

**Bằng chứng mạnh nhất của giai đoạn** (gọi Gemini thật, dùng `logs/lich-su.json` thật):

```
Trong ngày 28/09/2026, tổng chi tiêu quảng cáo của shop là 20.319.895 đồng. Chiến dịch
tốn kém nhất trong ngày là 2026-09-04-dainq-Online-Scale KHTN với chi tiêu 2.745.452 đồng.
Chiến dịch này đã mang về 10 lượt mua và 39 tin nhắn mới, với chi phí mỗi đơn là 274.545 d.
```

Đối chiếu `lich-su.json`: chi tiêu ngày 28/09 = **20.319.895** ✅, camp đắt nhất = **2.745.452** ✅,
**10 lượt mua** ✅. Phép kiểm tự động soi từng số AI viết và báo
**`So KHONG khop du lieu: KHONG CO (dat)`**.

**Một hạn chế đã biết, KHÔNG sửa được bằng code:** model chèn khoảng trắng quanh dấu gạch nối
trong tên chiến dịch (`2026-09-04-dainq` → `2026 - 09 - 04 - dainq`). Câu lệnh đã ghi rõ mà model
vẫn làm. **Không sai số, vẫn nhận ra đúng chiến dịch.** Đừng mất công "sửa" lần nữa.

**Kiểm thử:** `270/270` đạt (trước GĐ4 là 185). Thêm `tests/test_cong_cu.py` (66 bài) và 19 bài
mới trong `tests/test_ai.py`, cùng các bài thay thế trong `tests/test_nguoi_truc.py`.
Kiểm thử **không gọi mạng** — mọi lời gọi Gemini đều đi qua hàm giả tiêm vào bằng `goi_mang_fn=`.

**Tài liệu đã cập nhật:** `README.md` (mục "Nhắn tin hỏi bot"), `HUONG-DAN-LAY-CHIA-KHOA-AI.md`
(mục "Hai model, hai trần riêng"), `chay-kiem-thu.bat` (155 → 270 bài), `.env` và `.env.example`.

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
