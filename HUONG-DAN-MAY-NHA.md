# HƯỚNG DẪN MÁY NHÀ — BẢN 02/10/2026

> ## 🤖 NẾU BẠN LÀ TRỢ LÝ AI TRÊN MÁY NHÀ — ĐỌC MỤC NÀY TRƯỚC
>
> File này viết **cho bạn**, không phải cho Đại. Nhiệm vụ của bạn là **tự tay cài đặt giúp Đại**
> để máy nhà chạy giống hệt máy công ty (đã cập nhật lúc 16:48 ngày 02/10/2026).
>
> **Đại không biết lập trình.** Đừng đưa Đại đoạn code rồi bảo "anh chạy đi". Bạn là người chạy.
> Chỉ nhờ Đại đúng 2 việc mà bạn không làm được: **(a)** sửa file `.env` nếu bạn không có quyền ghi,
> **(b)** bấm nút xác nhận khi được hỏi.
>
> **Đọc hết mục 🤖 và mục "BẪY" trước khi làm bất cứ gì.** Có những cái bẫy đã gây lỗi THẬT
> trên máy công ty — đừng để máy nhà lặp lại.

---

# 🤖 PHẦN DÀNH RIÊNG CHO AI

## Bối cảnh bạn cần biết

Đây là **hệ thống báo cáo Meta Ads → Telegram** ("Người trực") của Đại. Chạy trên **2 máy**:
- **Máy công ty** — đã cập nhật xong bản `19f05ce`, đang chạy thật.
- **Máy nhà** — là máy bạn đang ngồi. Đang cũ hơn, cần cập nhật cho khớp.

**Hai máy dùng CHUNG một tài khoản Meta** nhưng **bot Telegram riêng**. Đây là điểm quan trọng
nhất về mặt vận hành (xem PHẦN E).

**Thư mục dự án:** tìm thư mục có file `nguoi_truc.py`, `agent.py`, `report.py`, `.env`.
Thường nằm ở `D:\Buddy Work AI\<ngày>\`.

**Python để chạy:** thử theo thứ tự — `python`, rồi `py`, rồi đường dẫn đầy đủ
`C:\Users\<tên>\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe`.
Các file `.bat` trong dự án **tự dò Python** rồi, cứ bấm là được.

**Kho GitHub:** `meta-ads-report`, nhánh `main`, repo riêng tư của `quangdaiai2-wq`.

## Việc bạn phải làm — 6 bước, đúng thứ tự

### Bước 1 — Kéo code mới

```
git pull
```

**Kiểm chứng — BẮT BUỘC, đừng bỏ:**
```
git log --oneline -1
```
Phải in ra **`19f05ce`** (hoặc mới hơn). Nếu chưa tới `19f05ce` thì **DỪNG LẠI**:
kiểm tra nhánh (`git branch`), thử `git fetch && git pull origin main`.
**Không làm tiếp khi chưa có mốc này** — code cũ ghi tên nhóm thiếu năm.

### Bước 2 → 4 — Sửa `.env` (BẮT BUỘC, `git pull` KHÔNG mang theo)

⚠️ **Hiểu đúng chỗ này trước khi làm.** File `.env` **không bao giờ lên GitHub** — nó chứa token
Telegram, token Meta, chìa khoá AI, nên `.gitignore` chặn lại. Trên GitHub chỉ có `.env.example`
là file **MẪU**, không phải cấu hình thật.

⇒ **`git pull` không bao giờ làm đổi chế độ chạy.** Mọi thay đổi `.env` phải sửa **tay trên máy nhà**.
⇒ **Hai máy ở hai chế độ khác nhau là ĐÚNG THIẾT KẾ**, không phải lỗi.

Mở file `.env` ở gốc thư mục dự án (có sẵn `mo-file-env.bat` để mở bằng Notepad).
Sửa **3 dòng sau** (dòng nào chưa có thì thêm vào cuối file):

| Dòng | Giá trị đúng | Máy công ty đang dùng | Ghi chú |
|---|---|---|---|
| `REPORT_SLOTS` | `8,17` | `8,17` | Mốc 12h **đã bỏ** từ 02/10/2026 |
| `AGENT_NHIP_PHUT` | `15` | `15` | Trước là `30` — quá thưa |
| `FILTER_INCLUDE` | `dainq` | `dainq` | ⚠️ **KHÔNG** phải tên tài khoản |

**Kiểm chứng 2 trong 3 dòng bằng lệnh (dán vào cửa sổ lệnh tại thư mục dự án):**

```
python -c "import report; e=report.load_env('.env'); print('SLOTS =', report.doc_moc_tu_env(e)); print('NHIP  =', e.get('AGENT_NHIP_PHUT')); print('LOC   =', e.get('FILTER_INCLUDE'))"
```

Kết quả đúng phải là:
```
SLOTS = [8, 17]
NHIP  = 15
LOC   = dainq
```

Nếu `SLOTS` ra `[8, 12, 17, 22]` ⇒ dòng `REPORT_SLOTS` **sai chính tả hoặc thiếu**
(phải đúng chữ in hoa, không dấu cách quanh dấu `=`).
Nếu `NHIP` ra `None` ⇒ chưa thêm dòng, hoặc thêm sai tên khoá.
Nếu `LOC` ra tên tài khoản ⇒ phải đổi thành `dainq`.

### Bước 5 — Chọn chế độ chạy

Có **2 chế độ**, bấm đúp **đúng một** file:

| Muốn gì | File bấm | Có hỏi lại không |
|---|---|---|
| Agent **TẮT NHÓM THẬT** trên Meta | `chuyen-sang-lam-that.bat` | **Có** — phải gõ đúng chữ `co` |
| Agent **chỉ nói**, không gửi lệnh nào | `chuyen-sang-tap-su.bat` | Không (đây là chiều an toàn) |

Cả hai file chỉ sửa **đúng một dòng** `AGENT_TAP_SU` trong `.env`, **sao lưu** `.env` thành
`.env.bak-truoc-doi-che-do`, và **in ra chế độ đang có** trước khi đổi.

**Kiểm chứng:**
```
python -c "import report; e=report.load_env('.env'); print('TAP_SU =', e.get('AGENT_TAP_SU'))"
```
- `false` ⇒ chạy THẬT (agent tắt nhóm thật).
- `true` ⇒ tập sự (chỉ nói).

⚠️ **Đây là quyết định của Đại, không phải của bạn.** Hỏi Đại trước khi chọn.
⚠️ **Đọc PHẦN E trước khi chọn chạy thật.**

### Bước 6 — KHỞI ĐỘNG LẠI AGENT (bắt buộc)

Bấm đúp **`khoi-dong-lai-agent.bat`**.

## 🔴🔴 BẪY LỚN NHẤT — đã gây lỗi THẬT trên máy công ty

**Sửa code mà không khởi động lại agent ⇒ agent vẫn chạy code CŨ trong bộ nhớ.**

> Python nạp code vào RAM **MỘT LẦN** lúc khởi động. Sửa file trên ổ đĩa xong, tiến trình đang chạy
> **vẫn giữ bản cũ** và tiếp tục làm theo code cũ. Không có cảnh báo nào.

**Chuyện đã xảy ra thật ngày 02/10/2026 trên máy công ty:**
```
13:39:18   Agent khởi động
15:37:25   Sửa code (thêm năm vào tên nhóm)
16:30:50   Agent VẪN ghi tên sai   ← vì chưa khởi động lại
```
Mất gần 3 tiếng chạy sai. Đã kiểm chứng: chạy đúng code mới thì ra `X10-26`, code cũ ra `X10`.

⚠️ **Điều này KHÁC hẳn với `.env`.** Từ 01/10, `.env` được đọc lại **mỗi 15 giây** nên sửa `.env`
là **ăn ngay, không cần khởi động lại**. Nhưng **code thì khác**:

> **Sửa code ⇒ PHẢI khởi động lại agent. Không ngoại lệ.**

**Vì `git pull` là sửa code** ⇒ sau `git pull` **luôn phải** bấm `khoi-dong-lai-agent.bat`.

### Kiểm chứng bước 6 — dùng ĐÚNG cách này

Mở `logs\baocao.log`, tìm dòng **cuối cùng** có chữ `khoi dong`:

```
AGENT: khoi dong — muc 2 — LAM THAT — ...
```

**Giờ của dòng đó phải là giờ bạn vừa bấm** (trong vòng 1–2 phút).

⚠️ **ĐỪNG dùng `logs\agent-dang-chay.lock` để đoán giờ khởi động.** File đó ghi **nhịp quét gần nhất**
(mỗi 15 phút nó ghi lại), **không phải giờ khởi động**. Máy công ty đã từng đọc nhầm file này và
kết luận sai, làm mất thời gian truy tìm. Muốn biết giờ khởi động thật thì **chỉ có `baocao.log`**.

Ngoài ra, đợi 1–2 phút rồi tìm dòng này (có từ 01/10):
```
AGENT: N nhom cham nguong — hoi X, bo qua Y (dang cho Dai tra loi), chan Z (rao an toan)
```
Thấy nó ⇒ agent đang làm việc bình thường.

---

# CÁC BẪY KHÁC ĐÃ GẶP THẬT

**Log không ghi số tiền ở mọi chỗ.** Dòng `xin phep tat '...' (tin nhan 204)` — `204` là
**SỐ TIN NHẮN**, không phải **204.000đ**. Máy công ty từng đọc nhầm và báo sai số tiền cho Đại.
⇒ **Muốn số tiền thật thì đọc từ Meta, đừng đọc từ log.** Log chỉ cho biết agent ĐÃ LÀM gì.

**Meta trả `spend`/`value` dạng CHUỖI** (`"70000"` chứ không phải `70000`). Hàm đọc số chỉ nhận
`int/float` sẽ **bỏ qua cả dòng mà không ném lỗi** — lỗi im lặng, rất khó tìm. Nếu thấy số ra 0
một cách vô lý, nghi chỗ này trước.

**Meta giới hạn GHI ~1 lần/30 giây** (`#613 rate limit`). Chờ 5–15 giây **KHÔNG đủ — phải 35 giây**.
Đọc thì không bị giới hạn. Mẹo: **gộp nhiều trường vào MỘT lần gọi** (`name` + `status` +
`daily_budget` cùng lúc) thay vì gọi 3 lần.

**Meta có 2 loại hạn mức đọc.** Loại rộng rãi (`x-business-use-case-usage`) rất thoáng — nhịp 5 phút
cũng chỉ ăn ~4% hạn mức/giờ. NHƯNG giới hạn **số lệnh gọi mỗi giây/phút theo tài khoản** chặt hơn
nhiều: gọi dồn dập (1 lệnh/nhóm × 50 nhóm trong vài giây) bị chặn ngay bằng
`code=17 · error_subcode=2446079 · "User request limit reached"`. Gặp mã 17 thì **chờ ~2 phút**, đừng chờ 15 giây.

**File `.bat` PHẢI là ASCII thuần VÀ xuống dòng CRLF.** Ký tự nhiều byte (dấu `—`, `·`) làm
`cmd.exe` đọc lệch dòng ⇒ `The syntax of the command is incorrect.` **Kể cả dòng `REM`.**
Nếu bạn tạo file `.bat` mới, phải tự kiểm 2 điều này trước khi lưu.

**Python chỉ nạp module một lần** — đã nói ở trên, nhưng nhắc lại vì đây là bẫy tốn kém nhất.

---

# PHẦN E — ⚠️ ĐỌC TRƯỚC KHI CHO MÁY NHÀ CHẠY THẬT

## Hai máy cùng chạy thật trên MỘT tài khoản Meta

| | Riêng hay chung | Hậu quả |
|---|---|---|
| Bot Telegram | **Riêng** mỗi máy | Không nuốt tin của nhau ✅ |
| Tài khoản Meta | **CHUNG** | Hai agent có thể cùng tác động vào một nhóm ⚠️ |

**Đã thấy dấu hiệu thật ngày 02/10/2026:** một nhóm bị agent máy công ty tắt tự động, nhưng sau đó
**được bật lại thủ công** và **ngân sách trở về 400.000đ** — nhiều khả năng do máy kia làm.

⇒ **Khuyến nghị: MỘT máy chạy thật, máy kia để tập sự.** Hoặc chấp nhận hai máy cùng chạy và
tự theo dõi. **Hỏi Đại quyết định — đây không phải việc kỹ thuật.**

## Token

| Máy | Token Meta hết hạn |
|---|---|
| **Máy nhà** | **10/11/2026** |
| Máy công ty |  |

Kiểm tra bất cứ lúc nào: **nhắn bot Telegram chữ `token`**.

⛔ **Hệ thống KHÔNG tự gia hạn token được. Meta không cho.** Máy công ty đã thử thật 29/09/2026:
Meta trả token mới nhưng **giữ nguyên ngày hết hạn cũ** (lệch **+0 giây**, thử 2 lần đều vậy).
⇒ Vẫn phải làm tay mỗi 60 ngày. Hệ thống nhắc 2 mức: còn dưới **30 ngày** → nhắc mỗi ngày;
còn dưới **7 ngày** → nhắc ở mọi báo cáo.

⚠️ **Token máy nhà hết hạn TRƯỚC máy công ty 19 ngày.** Đừng quên.

## Trước khi chạy THẬT — đọc bảng luật tắt nhóm

**Xét theo thứ tự TH3 → TH2 → TH1** (dừng ở trường hợp đầu tiên khớp):

| TH | Điều kiện | Ngưỡng | Tên mới |
|---|---|---|---|
| **TH3** | Có lượt mua tháng | giá/lượt mua **tháng** ≥ **390.000đ** | `<x>/450 X<tháng>-<năm>` |
| **TH2** | Có tin nhắn ≥1, chưa ra lượt mua | chi tiêu **hôm nay** ≥ **290.000đ** | `0/350 X<tháng>-<năm> TN` |
| **TH1** | Không có tin nhắn nào | chi tiêu **hôm nay** ≥ **70.000đ** | `0/<2×chi tiêu> X<tháng>-<năm>` |

**5 điểm đã đổi so với bản cũ:**
1. **CẢ BA trường hợp đều ghi NĂM** vào tên. Vd `0/350 X10-26 TN` (X10 = tháng 10, 26 = năm 2026).
2. **Xét theo TỪNG QUẢNG CÁO** (mới từ 02/10): nhóm có **≥2 quảng cáo** mà có quảng cáo chạm ngưỡng
   ⇒ **tắt LẺ quảng cáo đó**, giữ nhóm. Nhóm **0 hoặc 1 quảng cáo** ⇒ tắt **CẢ NHÓM**.
3. **Tắt lẻ quảng cáo = CHỈ tắt + đổi tên. KHÔNG hạ ngân sách.**
4. **Ngưỡng CỐ ĐỊNH** mọi nhóm — không đọc từ số `y` trong tên nữa.
5. **Thứ tự khi tắt: tắt NHÓM trước, xong mới tắt QUẢNG CÁO.**

⚠️ **"Tin nhắn" đếm CẢ HAI chỉ số:** `messaging_first_reply` **hoặc** `messaging_conversation_started_7d`.

**Phạm vi được đụng tới:** tên đối tượng chứa `dainq` HOẶC bắt đầu bằng mã content viết hoa
HOẶC có `new - dainq`. Lọc cấp **chiến dịch/nhóm**, **KHÔNG** theo tên quảng cáo.

## Nút bấm Telegram

```
⏸ TẮT NHÓM (giữ ngân sách)    → tắt nhóm + tắt quảng cáo + đổi tên, GIỮ ngân sách
💰 TẮT NHÓM + HẠ NGÂN SÁCH     → như trên + hạ ngân sách 27.000đ
⏭ Bỏ qua
```
⚠️ **Hai nút trả HAI kết quả khác nhau — đừng gộp lại.** Mỗi nút một hàng.
⚠️ **Telegram KHÔNG cho đổi màu nút.** Đừng tìm cách đổi màu nữa.

**Meta TỪ CHỐI thì KHÔNG tắt gì cả.** Tin báo lỗi gồm **lỗi Meta nguyên văn** + **đoán nguyên nhân**,
kèm 2 nút `quét lại` / `bỏ qua 24h`. Không bấm gì ⇒ 15 phút sau hỏi lại.

**Lệnh nhắn cho bot:** `báo cáo` → gửi tin + file HTML. `báo cáo 20/09/2026` → lấy thẳng từ Meta.
⚠️ **Chỉ nhận ngày ĐỦ năm.** `báo cáo hôm qua` = xin FILE; `báo cáo hôm qua thế nào?` = câu hỏi.

## Thứ tự khởi động lại — BẮT BUỘC

⚠️ **Từ 01/10, AGENT là nơi DUY NHẤT đọc Telegram.** Làm ngược thứ tự là mất tin:

```
1. Dừng CẢ HAI  (người trực + agent)
2. Bật NGƯỜI TRỰC trước
3. Rồi mới bật AGENT
```

---

# TÓM TẮT CHO AI — chạy tuần tự, kiểm chứng từng bước

```
BƯỚC 1  git pull                       → git log --oneline -1 phải ra 19f05ce
BƯỚC 2  sửa .env: REPORT_SLOTS=8,17    → kiểm: python -c "... doc_moc_tu_env ..."  ra [8, 17]
BƯỚC 3  sửa .env: AGENT_NHIP_PHUT=15   → kiểm: e.get('AGENT_NHIP_PHUT')  ra 15
BƯỚC 4  sửa .env: FILTER_INCLUDE=dainq → kiểm: e.get('FILTER_INCLUDE')  ra dainq
BƯỚC 5  HỎI ĐẠI chọn chế độ → bấm chuyen-sang-lam-that.bat HOẶC chuyen-sang-tap-su.bat
BƯỚC 6  khoi-dong-lai-agent.bat        → kiểm: logs\baocao.log có "AGENT: khoi dong" giờ MỚI
```

**Ba điều không được quên:**
1. `.env` **không** đi theo `git pull` — phải sửa tay.
2. `git pull` là **sửa code** ⇒ **bắt buộc** khởi động lại agent.
3. Đo giờ khởi động bằng `logs\baocao.log`, **KHÔNG** bằng `logs\agent-dang-chay.lock`.

**Công cụ có sẵn (chỉ đọc, không gửi lệnh nào lên Meta):**
```
kiem-tra-ten-nhom.bat   → quét tên nhóm thiếu năm
chay-kiem-thu.bat       → chạy toàn bộ bài kiểm thử (phải đạt hết mới yên tâm)
```

**Báo cáo lại cho Đại bằng tiếng Việt**, nói rõ: đã tới mốc nào, 3 dòng `.env` ra sao,
chọn chế độ gì, agent khởi động lúc mấy giờ. **Đừng nói "đã xong" mà không kèm bằng chứng.**

**Xong.**
