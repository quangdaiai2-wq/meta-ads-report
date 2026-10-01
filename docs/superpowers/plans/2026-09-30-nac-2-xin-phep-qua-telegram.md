# Kế hoạch thi công — Nấc 2: Agent xin phép Đại qua Telegram rồi mới tắt nhóm

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or
> executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Một tiến trình mới, chạy nền theo nhịp riêng, tự phát hiện nhóm quảng cáo của Đại đã chạm
ngưỡng → **gửi Telegram xin phép** → Đại trả lời `tắt <mã>` thì agent **thật sự tắt nhóm + hạ ngân
sách về 27.000đ** → ghi sổ → báo lại Telegram.

**Nấc 2 KHÁC nấc 1 ở đúng một chỗ:** nấc 1 chỉ nói. Nấc 2 **có ghi lên Meta**. Người bấm cò là Đại.

**Architecture:** Tiến trình riêng, model AI riêng, trần riêng. Dùng lại hạ tầng Telegram đã có sẵn
trong `nguoi_truc.py`. Không sửa `report.py` / `ai.py` / `dashboard.py`.

**Tech Stack:** Python 3.13 thuần, chỉ thư viện chuẩn (`json`, `urllib`, `unittest`).
Kiểm thử **không gọi mạng**.

**Spec:** `docs/superpowers/specs/2026-09-29-dinh-nghia-ai-agent-facebook-design.md`
(mục 1.4 nấc 2, mục 3.1 cái trần, mục 3.2 chế độ tập sự, mục 4 kiến trúc, mục 5 việc #3)

---

## Kế hoạch này ĐÃ ĐƯỢC KIỂM CHỨNG trước khi thi công (30/09/2026)

Dựng thử trong thư mục tạm **ngoài repo**: viết `agent_rao.py`, `agent_muc_tieu.py`,
`agent_xin_phep.py` + `test_agent.py`, rồi **chạy thật bằng dữ liệu Meta của Đại** (chỉ đọc,
không gửi lệnh nào).

| Phép kiểm | Kết quả |
|---|---|
| Bộ kiểm thử của bản dựng thử | **30/30 đạt** (sau khi sửa 3 lỗi dưới đây) |
| Chạy thật lần 1 — đúng như kế hoạch viết | **298 đề xuất** ⇒ **SAI**, xem lỗi 1–3 |
| Chạy thật lần 2 — sau khi sửa | **1 đề xuất** ⇒ hợp lý, khớp `DE_XUAT_TOI_DA=3` |
| Lọc phạm vi + loại nhóm thương hiệu | Đúng |

### BA CHỖ KẾ HOẠCH SAI, do bước dựng thử bắt được

**Lỗi 1 — Meta trả số dạng CHUỖI, không phải số. Lỗi IM LẶNG, nguy hiểm nhất.**
Kế hoạch ngầm định `spend` và `value` là số. Thực tế Meta trả `"70000"` (chuỗi). Hàm đọc số chỉ nhận
`int/float` ⇒ **mọi dòng bị bỏ qua** ⇒ agent **không bao giờ đề xuất gì** — mà **không hề ném lỗi**,
nên không ai phát hiện. Hệ thống im lặng làm sai.
⇒ `_so()` phải nhận cả chuỗi số.

**Lỗi 2 — lấy số CẢ THÁNG cho một ngưỡng TRONG NGÀY. Nặng nhất.**
Kế hoạch viết *"chi tiêu ≥ 70.000đ"* nhưng **không nói lấy chi tiêu khoảng nào**. Bản dựng thử lấy
cả tháng ⇒ **298 đề xuất**, gồm cả nhóm đã tắt từ ba tuần trước và cả **nhóm thương hiệu**.
⇒ Ngưỡng 70k/80k là ngưỡng **TRONG NGÀY** (Đại nói *"chi tiêu trong ngày"*) ⇒ phải đọc
`date_preset=today`. Còn mốc **400.000đ/lượt mua mới là chỉ số CẢ THÁNG**.

**Lỗi 3 — không lọc nhóm ĐANG CHẠY, không áp `FILTER_EXCLUDE`. Nặng.**
⇒ Chỉ xét nhóm có `effective_status = ACTIVE`. Và phải áp `FILTER_EXCLUDE` giống báo cáo đang làm,
nếu không agent sẽ đề xuất tắt **nhóm thương hiệu** — việc Đại chưa bao giờ làm.

### Hai chỗ khác kế hoạch (nhỏ hơn, cùng họ với lỗi cũ của nấc 1)

`de_xuat_tu_so(123)` ném `TypeError` (`for row in rows or []` không lặp được số nguyên), dù kế hoạch
ghi *"không bao giờ ném lỗi"*. ⇒ Kiểm `isinstance(rows, (list, tuple))` **trước** khi lặp.

Và một chỗ phân biệt tinh tế cũng do dựng thử lộ ra: **"nhóm chưa có lượt mua" (hợp lệ) KHÁC
"trường `luot_mua` có mặt nhưng đọc không ra" (dữ liệu hỏng)**. Trường hợp thứ hai phải **chặn**,
không được coi như 0.

### Một phát hiện về dữ liệu — không phải lỗi kế hoạch

`logs/lich-su.json` **chỉ có cấp CHIẾN DỊCH** (`id`, `name`, `spend`, `purchase`, `payment`, `msg`,
`cpr`) — **không có cấp nhóm quảng cáo**. Nhưng ngân sách và ngưỡng của Đại nằm ở **cấp nhóm**.
⇒ `agent_muc_tieu.py` **không dùng `lich-su.json`**, mà gọi thẳng Meta (`level=adset`).
Đúng như bản thiết kế 28/09 đã cảnh báo: *"Báo cáo hiện tại chỉ nhìn tới cấp chiến dịch, nên có thể
phải mở rộng xuống một cấp nữa."*

Và một giới hạn kỹ thuật đã chạm thật: tài khoản có **hơn 3.000 nhóm**. ⇒ Phải dùng tham số
`filtering` của Meta để chỉ lấy nhóm `ACTIVE`, **không** đọc hết rồi mới lọc.

---

## THI CÔNG XONG (30/09/2026, 14h30) — và HAI lỗi nữa do chạy thật bắt được

Đã viết code thật vào repo: `agent_rao.py`, `agent_muc_tieu.py`, `agent_xin_phep.py`,
`agent_ky_uc.py`, `agent_cong_cu_ghi.py`, `agent_doc_meta.py`, `agent.py`, `tests/test_agent.py`,
`bat-chay-agent.bat`, khoá mới trong `.env` / `.env.example` (sao lưu cũ: `.env.bak-truoc-nac2`).

| Phép kiểm | Kết quả |
|---|---|
| Bộ kiểm thử TOÀN BỘ repo | **546/546 đạt** (trước nấc 2: 487) |
| `agent.py --thu` chạy thật bằng dữ liệu Meta | **1 đề xuất**, đúng như bản dựng thử |
| `agent.py --mot-lan` | Chạy được, ghi sổ, gửi Telegram |

**Lỗi 4 — ghép URL sai làm hỏng token. Nặng, và cũng là lỗi IM LẶNG.**
`agent_doc_meta` gọi `report.api_get(f"{path}?{urlencode(params)}", {})`. Nhưng `api_get` **tự thêm
`?`** vào cuối ⇒ URL thành `...&access_token=TOKEN?` ⇒ Meta trả *"Malformed access token …FO?"* ⇒
agent đọc về **0 nhóm** và **không đề xuất gì cả**, im lặng, không ai biết vì sao.
⇒ Phải truyền `path` và `params` RIÊNG cho `api_get`, không tự ghép chuỗi truy vấn.

**Lỗi 5 — chuỗi hiện cho Đại viết không dấu (vi phạm quy ước dự án).**
Lý do chặn và lý do đề xuất được **gửi thẳng vào Telegram cho Đại đọc**, nhưng bản đầu viết
*"Hom nay chi 83.991d, co 1 tin nhan nhung 0 luot mua"*. Quy ước repo: **chú thích code không dấu,
chuỗi hiện cho người dùng CÓ DẤU**.
⇒ Đã thêm hàm `tien()` định dạng `1.234.567đ` và viết lại toàn bộ chuỗi hiện cho Đại. Có bài kiểm
thử riêng bắt lỗi này: `test_ly_do_hien_cho_dai_phai_CO_DAU`.

**Lỗi 6 — HAI tiến trình dùng CHUNG một bot Telegram, mà `getUpdates` chỉ giao mỗi tin cho MỘT nơi.**
Đây là lỗi **thiết kế**, không phải lỗi cú pháp, và là lỗi nặng nhất về mặt "tính năng có chạy được
không": `nguoi_truc.py` đang chạy nền và cũng gọi `getUpdates`. Ai xác nhận trước thì người kia
**không bao giờ thấy tin đó nữa**. Nghĩa là Đại trả lời `tắt <mã>` thì rất có thể **tin bị tiến trình
báo cáo lấy mất**, đem đi hỏi AI, còn agent **không bao giờ nhận được lệnh** — và **không có gì báo
lỗi**. Tệ hơn: Đại tưởng đã ra lệnh, mà không có gì xảy ra.
⇒ **Cách chữa:** `nguoi_truc.py` nhận ra cú pháp lệnh (`lenh_telegram.la_lenh`) thì **ghi tin vào
`logs/agent-lenh.json`** và trả lời *"đã ghi nhận, agent xử lý ở vòng kế tiếp"*, **không đem hỏi AI**.
Agent đọc file đó, xử lý xong thì xoá. Phần đọc lệnh tách ra `lenh_telegram.py` (hàm thuần) để cả
hai bên dùng chung mà **không tạo vòng lặp nhập** (`agent_xin_phep` đã nhập `nguoi_truc`).

**Lỗi 7 — rào an toàn đọc không ra thời điểm, nên TỪ CHỐI MỌI lệnh Đại đã duyệt.**
`agent.py` đọc lại bản ghi từ `logs/nhat-ky-agent.json`, nơi thời điểm lưu dạng **chuỗi ISO**. Nhưng
`agent_rao._gio()` chỉ nhận `datetime` ⇒ trả `None` ⇒ rào kết luận *"Thời điểm tạo đề xuất không đọc
được"* ⇒ **mọi lệnh đã được Đại đồng ý đều bị chặn**. Tính năng sẽ **không bao giờ tắt được nhóm
nào**, mà log chỉ ghi một dòng "bị chặn" trông như bình thường.
⇒ `_gio()` phải nhận **cả chuỗi ISO**. Bài `test_tap_su_chi_ghi_so_khong_gui_meta` bắt được lỗi này.

**Một chỗ nữa, không phải lỗi sản phẩm mà là lỗi của bộ kiểm thử:** các bài kiểm thử gọi `report.log`
nên **ghi vào `logs/baocao.log` thật** — trong đó có dòng *"AGENT: Dai bo qua nhom …"*, tức **ghi sai
sự thật** (Đại không hề bỏ qua nhóm nào). `logs/baocao.log` là file Đại mở đầu tiên khi có sự cố.
⇒ Thêm lớp `_KhongGhiLog` chặn `report.log` trong kiểm thử. Sổ `nhat-ky-agent.json` vốn đã sạch vì
kiểm thử dùng file tạm.

**Một điều đã kiểm chứng và ghi lại:** nấc 2 **hiện CHƯA dùng AI**. Vòng lặp chạy bằng **luật code** —
đúng khuyến nghị số 1 ở mục 4.4 của bản thiết kế. Nhờ vậy **không tốn lượt AI miễn phí** nào của báo
cáo. Vì thế khoá `AGENT_MODEL` **chưa cần**, và đã ghi chú lý do ngay trong `.env`.

**Đã chạy thật một vòng (30/09/2026, 14h30)** ở chế độ tập sự: đọc 82 nhóm đang chạy → **1 đề xuất**
→ ghi sổ → gửi Telegram. Bộ kiểm thử: **554/554 đạt**.

---

## 0. ĐIỀU ĐÃ ĐỔI SO VỚI BẢN THIẾT KẾ — ĐỌC TRƯỚC

Bản thiết kế 29/09 viết ba điều. Nay **hai điều đã khác**, phải ghi lại đây chứ không được lặng lẽ
làm theo hướng mới:

| # | Bản thiết kế nói | Thực tế 30/09/2026 | Xử lý |
|---|---|---|---|
| 1 | *"Nấc 1 và nấc 2 KHÔNG cần token mới"* (mục 3.3) | **Sai.** Nấc 2 gửi lệnh lên Meta ⇒ cần `ads_management`. Và Đại **đã lấy được token đó** (hạn ) | Không chặn nữa |
| 2 | *"Chưa biết lãi mỗi đơn thì không định nghĩa được camp kém"* (Rào cản 2) | **Không còn đúng.** Đại đã tự mã hoá ngưỡng vào **tên nhóm** — phần `y`. Hệ thống **đọc `y` từ tên**, không cần biết lãi | Bỏ rào cản 2 |
| 3 | *"Agent phải là thư mục riêng"* (mục 2.3) | Repo hiện **không có thư mục code nào** — mọi file `.py` nằm ở gốc. Thư mục con sẽ phải hack `sys.path` để nhập `nguoi_truc` | **Đề nghị giữ ở gốc**, đặt tiền tố `agent_`. Điều bản thiết kế thật sự cần — **tiến trình riêng, model riêng, trần riêng** — vẫn đủ |

**Quyền ghi ĐÃ ĐƯỢC THỬ THẬT, KHÔNG PHẢI PHỎNG ĐOÁN.** `logs/nhat-ky-agent.json` có hai bản ghi ngày
30/09/2026: tạm dừng ad set `120250506886650509` lúc 09:53 và bật lại lúc 09:58, cả hai **HTTP 200,
`success=true`, đọc lại thấy đúng trạng thái**. Đây là bằng chứng quyền ghi hoạt động.

---

## 1. QUY TẮC NGHIỆP VỤ — TẤT CẢ ĐÃ KIỂM CHỨNG BẰNG DỮ LIỆU THẬT

Nguồn: `TONG-HOP-CACH-CHAY-QUANG-CAO.md` (30/09/2026). Không có quy tắc nào ở đây là phỏng đoán.

### 1.1. Phạm vi — chỉ đụng phần của Đại

```
GIỮ  nếu:  người thao tác = ""
     VÀ   tên đối tượng: chứa "dainq" HOẶC bắt đầu bằng mã content viết hoa
                         (kiểu THC295THM295) HOẶC có "new - dainq"
LOẠI:  mọi thao tác của "Vũ Quang Trường"; đối tượng tên mặc định của Meta
```
Lọc ở cấp **chiến dịch / nhóm quảng cáo**, **không** lọc theo tên quảng cáo (Meta tự sinh tên
quảng cáo không có `dainq`).

### 1.2. Hai ngưỡng đề xuất tắt — khác nhau vì có/không có lượt mua

| Tình huống nhóm | Ngưỡng đề xuất tắt | Nguồn |
|---|---|---|
| **Đã có ≥1 lượt mua trong tháng** | **chi phí trung bình mỗi lượt mua ≥ 400.000đ** | C6 (Đại nói thẳng) + phân bố 108 nhóm: 44 nhóm dồn đúng dải 400–450k, trung vị 418.668đ |
| **Có tin nhắn nhưng 0 lượt mua** | **chi tiêu ≥ 70.000đ** | C3 (Đại nói "70.000") — khớp `y=120` = 70.000 + 50.000, gặp **27 lần** |
| **Không có tin nhắn nào** | **chi tiêu ≥ 80.000đ** | C3 (Đại nói "80.000") — khớp `y=160` = 2 × 80.000, gặp **14 lần** |

⚠️ **400.000đ là mốc CỐ ĐỊNH, không phải trần riêng từng nhóm.** Đại xác nhận 30/09: các nhóm có chi
phí/lượt mua trên 400k là do **chưa kịp tắt nên vượt**, không phải Đại nới trần. Giá trị `y` cao
(`550`, `600`, `650`, `750`) là **hậu quả của việc vượt ngưỡng** — Đại đặt lại theo công thức
`y` = chi tiêu mới + 50.000.

### 1.3. Động tác khi tắt — PHẢI LÀ HAI VIỆC, KHÔNG PHẢI MỘT

Đo trên **75 lần** Đại tự tắt:
- **72/75 lần** hạ ngân sách về 27.000đ **đi kèm TẮT nhóm**, lệch nhau **trung vị 6 giây**.
- **75/75 lần** giá trị ngân sách trước đó là **400.000đ**.
- 27.000đ là **giá trị dưới 100.000 duy nhất** Đại từng dùng.
- Đại giải thích: làm cả hai *"để hạn chế nhiều nhất mức chi tiêu tiếp có thể"*.

⇒ Agent phải làm **đúng hai bước**: `status=PAUSED` **và** `daily_budget=27000`.

### 1.4. Nấc thang tăng ngân sách — dùng làm RÀO, không phải để tự tăng

```
ngân sách = 400.000 + 100.000 × (số lượt mua TRONG THÁNG // 5)
```
Kiểm chứng: **23/34 mức khớp đúng dải**, phần còn lại lệch đúng ±1 bậc (sai số của dữ liệu theo ngày).
Đơn vị đếm là **lượt mua trong tháng**, KHÔNG phải cả đời (thử cả đời: 0/34 khớp).

### 1.5. Hai điều bắt buộc phải nhớ về dữ liệu Meta

1. **Meta báo đơn TRỄ.** Nhiều nhóm tên ghi `0/...` sau đó Meta báo có 1 lượt mua (04/09, 09/09,
   12/09, 14/09, 15/09). ⇒ **Chỉ phán xét NGÀY TRỌN VẸN**, không phán xét phần ngày đang chạy.
2. **Meta trả về 5 tên hành động cho CÙNG một lượt mua** (`omni_purchase`,
   `onsite_conversion.purchase`, `onsite_web_purchase`, `onsite_app_purchase`,
   `onsite_web_app_purchase`) với **giá trị y hệt nhau**. Cộng cả 5 là **đếm trùng gấp 5 lần**.
   `report.py` đã đúng sẵn — agent phải dùng **đúng một tên**.

---

## 2. CÁI TRẦN — `agent_rao.py` LÀ FILE QUAN TRỌNG NHẤT

**Hàm thuần.** Nhận một đề xuất, trả `(cho_phep: bool, ly_do: str)`. **Không gọi mạng, không đọc
file, không có AI trong đó.** Nhờ vậy kiểm thử được từng trường hợp, và **không thể bị AI thuyết phục**.

| # | Cái trần | Nội dung | Mặc định |
|---|---|---|---|
| 1 | **Danh sách trắng** | Tên nhóm phải chứa `dainq` (hoặc mã content viết hoa). Không khớp: **chặn tuyệt đối** | bật |
| 2 | **Chỉ tắt, chưa tăng ngân sách** | Nấc 2 **chỉ được `tam_dung`**. Mọi hành động khác (tăng/giảm ngân sách, bật lại) đều chặn | bật |
| 3 | **Cấm tắt nhóm đang hiệu quả** | Nhóm có **≥ 1 lượt mua** và **chi phí/lượt mua < 400.000đ** ⇒ **cấm tắt**, dù AI nói gì | bật |
| 4 | **Ngân sách hạ về đúng 27.000đ** | Không cho giá trị nào khác. Chặn nếu đề xuất hạ về số khác | bật |
| 5 | **Hạn mức hành động** | Tối đa **3 hành động/ngày** (khớp `DE_XUAT_TOI_DA=3`) và **1 hành động/giờ**. Vượt: dừng, báo Đại | `AGENT_TOI_DA_NGAY=3` |
| 6 | **Đề xuất hết hiệu lực sau 24 giờ** | Đại trả lời muộn hơn 24h ⇒ **không làm gì**. Im lặng là mặc định an toàn | bật |
| 7 | **Ghi sổ TRƯỚC khi gửi lên Meta** | Cứng, không tắt được | bật |
| 8 | **Không hỏi lại nhóm đã có câu trả lời** | Nhóm Đại đã nói `bỏ qua` (hoặc đã `tắt`) thì **không đề xuất lại trong 24 giờ**. Không có rào này, nhóm chưa bị tắt sẽ bị hỏi lại **mỗi 30 phút** | bật |

---

## 3. CÁC KHỐI — mỗi khối một việc

Đặt ở gốc repo, tiền tố `agent_` (xem mục 0 điều #3):

| File | Việc duy nhất | Phụ thuộc |
|---|---|---|
| `agent.py` | Vòng lặp + điểm vào. Không chứa logic nghiệp vụ | tất cả dưới |
| `agent_muc_tieu.py` | Đọc `logs/lich-su.json` + Meta, tính ra danh sách nhóm **đáng đề xuất tắt** | `lich_su.py` |
| `agent_rao.py` | **Cái trần.** Hàm thuần, kiểm được bằng unit test | không |
| `agent_ky_uc.py` | Nhật ký hành động + hàng đợi đề xuất đang chờ Đại trả lời | `logs/nhat-ky-agent.json` |
| `agent_xin_phep.py` | Soạn tin Telegram, đọc trả lời của Đại, phân tích cú pháp lệnh | `nguoi_truc.py` (dùng lại) |
| `agent_cong_cu_ghi.py` | Gửi lệnh lên Meta: tắt nhóm + hạ ngân sách | Meta API |

**Dùng lại, KHÔNG viết lại:** `nguoi_truc.py::gui_tin_nhan`, `lay_tin_moi`, `tin_tu_dai`
(hàng rào chỉ nhận tin từ `TELEGRAM_CHAT_ID` của Đại), `lich_su.py::doc`.

### 3.1. Định dạng tin xin phép

```
⚠️ XIN PHÉP TẮT NHÓM

Nhóm: 2026 - 09 - 30 - dainq - Scale - Online 0/160 X9
Chi tháng: 480.000đ · 1 lượt mua · 480.000đ/lượt  (mốc: 400.000đ)
Đề xuất: TẮT nhóm + hạ ngân sách về 27.000đ

Trả lời:
  tắt 120250506886650509
  bỏ qua 120250506886650509
```

Đại trả lời đúng cú pháp thì agent mới gửi lệnh. **Không trả lời, hoặc trả lời khác ⇒ không làm gì.**

### 3.2. Sổ `logs/nhat-ky-agent.json`

**Giữ nguyên định dạng hai bản ghi đã có** (30/09/2026) — thêm hai trường cho nấc 2:

```json
{
  "luc": "2026-10-02T14:30:00+07:00",
  "che_do": "xin_phep",
  "hanh_dong": "tam_dung",
  "doi_tuong": {"cap": "ad_set", "id": "120250506886650509",
                "ten": "…", "ngan_sach_ngay_vnd": 400000},
  "trang_thai_truoc": "ACTIVE",
  "trang_thai_sau": "PAUSED",
  "ly_do": "Chi 480.000d cho 1 luot mua, cham moc 400.000d",
  "rao_an_toan": "cho phep",
  "da_gui_len_meta": true,
  "dai_phan_hoi": "tat 120250506886650509",
  "ket_qua": "thanh cong (HTTP 200, doc lai thay PAUSED)",
  "co_the_hoan_tac": true,
  "hoan_tac_bang": "POST /<id> voi status=ACTIVE",
  "ket_qua_sau_24h": null
}
```

`dai_phan_hoi` và `ket_qua_sau_24h` để trống, điền sau. **Đây là chỗ học** — đối chiếu số lần Đại
bấm "ừ" với số lần Đại "bỏ qua" là biết agent đoán đúng bao nhiêu phần trăm, trước khi cho nó tự bấm.

---

## 4. LUỒNG CHẠY

```
mỗi 30 phút (AGENT_NHIP_PHUT, mặc định 30):

  1. QUAN SÁT   đọc số liệu (chỉ ngày TRỌN VẸN)
  2. PHÁN XÉT   agent_muc_tieu.py: nhóm nào chạm ngưỡng?
  3. RÀO CHẶN   agent_rao.py kiểm. Chặn thì thôi, ghi sổ, không gửi
  4. XIN PHÉP   gửi Telegram, ghi hàng đợi "đang chờ Đại"
  5. ĐỌC TRẢ LỜI  lần chạy sau: có tin `tắt <mã>` chưa?
  6. HÀNH ĐỘNG  ghi sổ TRƯỚC → gửi Meta (PAUSED + 27000) → đọc lại kiểm
  7. BÁO ĐẠI    gửi Telegram kết quả
  8. THEO DÕI   lần chạy sau, đo hậu quả
```

**Chế độ tập sự:** `AGENT_MUC=2` mặc định. Thêm `AGENT_TAP_SU=true` (mặc định **bật**) thì bước 6
**không gửi lên Meta** — chỉ ghi sổ và báo Đại *"tôi SẼ tắt nhóm X"*. Đại đọc vài ngày, đối chiếu,
rồi mới tắt tập sự.

---

## 5. CẤU HÌNH `.env` — khoá mới, đều có mặc định trong code

```
AGENT_MUC=2                # 2 = xin phép (mặc định) · 3 = tự làm (chưa mở)
AGENT_TAP_SU=true          # true = chỉ nói, không gửi lệnh lên Meta
AGENT_NHIP_PHUT=30         # nhịp vòng lặp
AGENT_TOI_DA_NGAY=3        # trần số lệnh gửi lên Meta mỗi ngày
```

Ngưỡng và số tiền (`AGENT_NGUONG_CPR`, `AGENT_NGUONG_TIN_NHAN`, `AGENT_NGUONG_KHONG_TIN`,
`AGENT_NGAN_SACH_HA`) **cố ý để trong code, không đưa ra `.env`** — chúng là quy tắc đã kiểm chứng
bằng dữ liệu thật, không phải thứ để chỉnh tuỳ hứng. Muốn đổi thì sửa code, và có kiểm thử chặn.

**`AGENT_MODEL` KHÔNG có, vì nấc 2 chưa dùng AI.** Vòng lặp chạy bằng luật code — đúng khuyến nghị
số 1 ở mục 4.4 của bản thiết kế. Khi nào cần AI diễn giải tình huống lạ thì mới thêm khoá đó, và
**phải là model khác `GEMINI_MODEL`** — Gemini miễn phí cho **20 lượt/ngày/model**.

---

## 6. KIỂM THỬ — không gọi mạng

File mới `tests/test_agent.py`. Bám theo bộ kiểm thử đang có (435 → 487 bài ở nấc 1).

**Nhóm A — `agent_rao.py` (hàm thuần, phải phủ hết):**
- [ ] Tên không có `dainq` ⇒ chặn
- [ ] Tên có mã content `THC295THM295` ⇒ cho phép
- [ ] Hành động `tang_ngan_sach` ⇒ chặn (nấc 2 chỉ được tắt)
- [ ] Nhóm có 1 lượt mua, chi phí 300.000đ/lượt ⇒ **chặn** (đang hiệu quả)
- [ ] Nhóm có 1 lượt mua, chi phí 480.000đ/lượt ⇒ cho phép
- [ ] Hạ ngân sách về 30.000đ ⇒ chặn (phải đúng 27.000đ)
- [ ] Đã 3 hành động hôm nay ⇒ chặn hành động thứ 4
- [ ] Đề xuất đã quá 24 giờ ⇒ chặn
- [ ] Đầu vào dị dạng (`None`, chuỗi, dict thiếu khoá) ⇒ **không ném lỗi**, trả "chặn"

**Nhóm B — `agent_xin_phep.py` phân tích cú pháp:**
- [ ] `tắt 123` ⇒ hiểu đúng
- [ ] `TẮT 123` / `tat 123` (có dấu / không dấu) ⇒ hiểu đúng
- [ ] `bỏ qua 123` ⇒ hiểu là từ chối, không làm gì
- [ ] `tắt 456` khi đang chờ 123 ⇒ không khớp, không làm gì
- [ ] Tin rác, tin rỗng, tin từ người khác ⇒ không làm gì

**Nhóm C — `agent_muc_tieu.py` (dữ liệu giả, không gọi mạng):**
- [ ] Nhóm 0 lượt mua, chi 65.000đ ⇒ chưa đề xuất
- [ ] Nhóm 0 lượt mua, chi 70.000đ ⇒ đề xuất
- [ ] Nhóm 0 lượt mua, không tin nhắn, chi 75.000đ ⇒ chưa; chi 80.000đ ⇒ đề xuất
- [ ] Nhóm 1 lượt mua, chi 500.000đ ⇒ 500.000đ/lượt ⇒ đề xuất
- [ ] Nhóm 2 lượt mua, chi 700.000đ ⇒ 350.000đ/lượt ⇒ **không** đề xuất
- [ ] Ngày đang chạy (chưa trọn) ⇒ **không** xét
- [ ] Tổng lượt mua bị đếm trùng 5 lần ⇒ phải phát hiện và chỉ tính một lần
- [ ] **Meta trả số dạng CHUỖI** (`"70000"`) ⇒ vẫn phải đọc ra số (lỗi 1 của bản dựng thử)
- [ ] Nhóm **không** `ACTIVE` ⇒ không xét (lỗi 3)
- [ ] Tên chứa `Brand` / `thương hiệu` ⇒ không xét (lỗi 3)
- [ ] Ngưỡng 70k/80k dùng **chi tiêu HÔM NAY**, mốc 400k dùng **chi tiêu CẢ THÁNG** (lỗi 2)
- [ ] `de_xuat_tu_so(123)` ⇒ trả `[]`, **không ném lỗi**
- [ ] Trường `luot_mua` có mặt nhưng đọc không ra ⇒ **chặn** (khác với "chưa có lượt mua")
- [ ] Nhóm đã được Đại trả lời trong 24 giờ ⇒ **không đề xuất lại** (rào 8)

---

## 7. RỦI RO

| Rủi ro | Mức | Xử lý |
|---|---|---|
| Tắt rồi bật lại làm nhóm **mất giai đoạn học** của Meta | **Cao** | Chế độ tập sự + rào #3 (cấm tắt nhóm đang hiệu quả) |
| Meta báo đơn trễ ⇒ tắt oan | **Cao** | Chỉ xét ngày trọn vẹn; rào #3 chặn nhóm có lượt mua rẻ |
| Đại không đọc được code nên không biết agent sai lúc nào | **Cao** | Mọi hành động báo Telegram ngay; sổ ghi **tiếng Việt có dấu**, không phải log kỹ thuật |
| Agent chạy nền ăn hết trần AI của báo cáo | Trung bình | `AGENT_MODEL` riêng; vòng lặp nền bằng **luật code**, AI chỉ gọi khi cần diễn giải |
| Token 60 ngày chết | Trung bình | Nhắc trước 30 ngày như hệ thống đang có |
| Mất điện / tắt máy giữa lúc chờ Đại trả lời | Thấp | Hàng đợi nằm trong `nhat-ky-agent.json`, khởi động lại vẫn còn |

---

## 8. THỨ TỰ THI CÔNG

1. `agent_rao.py` + `tests/test_agent.py` nhóm A — **làm trước tiên**, vì đây là cái trần.
2. `agent_muc_tieu.py` + nhóm C.
3. `agent_xin_phep.py` + nhóm B.
4. `agent_ky_uc.py`, `agent_cong_cu_ghi.py`.
5. `agent.py` — vòng lặp, ghép lại.
6. `.env` / `.env.example` — thêm khoá mới, sao lưu `.env` cũ thành `.env.bak-truoc-nac2`.
7. Cập nhật `HANDOFF.md`.

**Dựng thử trước khi sửa code thật** — theo đúng quy trình đã chốt với Đại. Bước dựng thử ở nấc 1 đã
bắt được **2 lỗi thật của kế hoạch**; đừng bỏ bước này.
