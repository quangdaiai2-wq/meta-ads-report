# Kế hoạch thi công — Giai đoạn 4: Người trực trả lời câu hỏi

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Đại nhắn một câu hỏi về số liệu cho bot Telegram (ví dụ *"camp nào tệ nhất tuần này?"*) và **nhận được câu trả lời có số thật**, lấy từ lịch sử đã lưu. AI chỉ được **đọc số do công cụ trả về** — không tự tính, không tự chọn khoảng ngày, không bịa. AI lỗi thì Đại nhận một tin nhắn nói rõ lý do, không im lặng.

**Architecture:** Thêm `cong_cu.py` — bốn công cụ **thuần đọc dữ liệu**, không chạm mạng, không biết Gemini là gì. `ai.py` được thêm khả năng **gọi công cụ** (function calling) và một hàm `tra_loi()` chạy vòng lặp *AI xin công cụ → code chạy → trả kết quả → AI viết câu trả lời*, có **giới hạn cứng số lượt**. `nguoi_truc.py` nối phần nghe Telegram vào lớp AI. Không đụng tới `report.py`.

**Tech Stack:** Python 3.13 thuần, chỉ thư viện chuẩn (`json`, `urllib`, `unittest`). Nhà cung cấp: **Gemini function calling** qua `generativelanguage.googleapis.com`. Kiểm thử **không gọi mạng** — tiêm hàm gọi mạng giả.

**Spec:** `docs/superpowers/specs/2026-09-28-nguoi-truc-ai-agent-design.md` (mục 5.3, 6.2, 8, 9.2 điều 7–9, 11)

---

## Kết quả kiểm chứng trước khi viết kế hoạch (29/09/2026)

Đây là **việc thử nghiệm đầu tiên** của giai đoạn, làm bằng **chìa khoá thật của Đại**, trước khi viết một dòng kế hoạch nào. Kết quả quyết định hình dạng cả kế hoạch.

### 1. Gemini CÓ hỗ trợ gọi công cụ — đã chạy được thật

| Phép thử | Kết quả |
|---|---|
| Gửi kèm khai báo công cụ, hỏi *"tuần này chiến dịch nào tệ nhất?"* | Model trả về `functionCall: {name: "xep_hang_camp", args: {tu: "2026-09-28", den: "2026-09-29", sap_theo: "cpr", tang_dan: false}}` |
| Trả kết quả công cụ về cho model | Model **gọi công cụ lần thứ hai** với tham số khác (`tang_dan: true, sap_theo: purchase`) |
| Chạy vòng lặp đầy đủ tới khi model tự dừng | Lượt 1 `xep_hang_camp` → lượt 2 `lay_khoang(21/09→27/09)` → lượt 3 `lay_khoang(28/09→29/09)` → **lượt 4 model dừng và viết câu trả lời tiếng Việt có dấu đầy đủ** |

**Ba model đã thử:** `gemini-3.8-flash` ✅ chạy được · `gemini-3.5-flash` ✅ chạy được · `gemini-2.5-flash` ❌ bị khoá cho tài khoản mới (`404: no longer available to new users`, khuyên dùng `gemini-3.8-flash`).

**Chi tiết kỹ thuật bắt buộc nhớ khi thi công:**

- Gửi: `{"contents": [...], "tools": [{"functionDeclarations": [...]}]}`
- Nhận: `candidates[0].content.parts[i].functionCall = {name, args, id}`
- Response còn có `thoughtSignature` trong part. **Phải gửi lại nguyên `content` của model** (không bóc ra rồi ghép lại) — đây là yêu cầu của Gemini 3.x, đã làm đúng trong phép thử và chạy được.
- Trả kết quả: `{"role": "user", "parts": [{"functionResponse": {"name": ..., "response": {...}}}]}`

### 2. Phép thử lộ ra BA vấn đề thật, kế hoạch phải xử lý

**Vấn đề A — AI tự chọn khoảng thời gian sai.** Trong phép thử, tôi nói *"Hôm nay là 29/09/2026"* và hỏi *"tuần này"*. AI hiểu "tuần này" = **28/09 → 29/09 (hai ngày)** và tự chọn "tuần trước" = 21/09 → 27/09. Cả hai đều không đúng ý người hỏi, và **lịch sử lúc đó chỉ có số tới 28/09**.

⇒ **Phạm vi thời gian là một phép tính. Code phải làm, không giao cho AI.** Đây đúng bài học của Giai đoạn 3 (phép so sánh do code làm), lặp lại ở một chỗ khác. Giải pháp: `cong_cu.moc_thoi_gian()` tính sẵn và chèn vào câu lệnh một mục **MỐC THỜI GIAN** do hệ thống cấp.

**Vấn đề B — AI gọi công cụ mãi không dừng.** Ở phép thử thứ hai, model nhận kết quả rồi **gọi công cụ tiếp**, không tự dừng. Nếu không có giới hạn cứng, một câu hỏi có thể ngốn hàng chục lượt gọi AI.

⇒ Phải có `TOI_DA_LUOT_CONG_CU` và **lượt cuối gọi KHÔNG kèm công cụ** để buộc AI trả lời bằng chữ.

**Vấn đề C — AI viết markdown, câu trả lời dài.** Kết quả thật của phép thử:
```
- **Chiến dịch tệ nhất tuần này (2026-09-28 đến 2026-09-29):** Chiến dịch `dainq_he_03`...
```
Dấu `**`, dấu `` ` ``, gạch đầu dòng. Telegram hiện những ký hiệu này **rất rối**.

⇒ Câu lệnh phải **cấm markdown** và giới hạn độ dài, nói rõ "đây là tin nhắn Telegram".

---

## Kế hoạch này đã được kiểm chứng trước khi giao

Trước khi giao, tôi đã **dựng thử toàn bộ code của kế hoạch trong một thư mục tạm**: chép
`report.py`, `lich_su.py`, `ai.py`, `nguoi_truc.py`, `dashboard.py` và cả thư mục `tests/` sang
thư mục tạm, viết `cong_cu.py` + `tests/test_cong_cu.py` theo đúng kế hoạch, áp các sửa đổi vào
`ai.py` và `nguoi_truc.py`, rồi chạy. Kết quả:

| Phép kiểm | Kết quả |
|---|---|
| Toàn bộ kiểm thử trong thư mục tạm | **270/270 đạt** (trước GĐ4 là 185) |
| Bốn công cụ chạy trên **`logs/lich-su.json` THẬT của Đại** | Chạy đúng, số khớp bản ghi 28/09 |
| `moc_thoi_gian` trên lịch sử thật (1 ngày) | Ghi đúng `7 ngày liền trước đó: CHƯA CÓ số liệu, không so sánh được` |
| `so_sanh` khi kỳ trước rỗng | Trả `ky_truoc: None`, **không bịa** |
| Các trường hợp lỗi (ngày sai định dạng, chỉ số sai, khoảng rỗng) | Đều trả `{"loi": ...}` rõ ràng, **không ném lỗi** |
| **Gọi Gemini THẬT** một câu hỏi, dùng lịch sử thật | AI gọi 2 công cụ, viết câu trả lời đúng số |
| Đối chiếu từng con số AI viết với dữ liệu công cụ | **`So KHONG khop du lieu: KHONG CO (dat)`** |
| Câu trả lời có markdown không | **Không** (`Dinh dang: khong co markdown (dat)`) |

Câu trả lời thật của AI trên dữ liệu thật của Đại (đây là bằng chứng mạnh nhất của giai đoạn):

```
Trong ngày 28/09/2026, tổng chi tiêu quảng cáo của shop là 20.319.895 đồng. Chiến dịch
tốn kém nhất trong ngày là 2026-09-04-dainq-Online-Scale KHTN với chi tiêu 2.745.452 đồng.
Chiến dịch này đã mang về 10 lượt mua và 39 tin nhắn mới, với chi phí mỗi đơn là 274.545 d.
```

Đối chiếu `logs/lich-su.json`: chi tiêu ngày 28/09 = **20.319.895** ✅, camp đắt nhất
= **2.745.452** ✅, **10 lượt mua** ✅. Không một con số nào bịa.

### Ba lỗi của kế hoạch đã bị chính bước dựng thử bắt được

**Lỗi 1 — `NguoiTruc` thiếu đường tiêm hàm AI (nặng nhất).** Kế hoạch chỉ sửa
`tra_loi_tin_nhan` mà quên rằng `NguoiTruc.xu_ly_tin()` gọi hàm đó. Hệ quả: **bài kiểm thử
`TestXuLyTin` gọi AI THẬT** — chạy `270` bài kiểm thử sẽ tốn lượt AI và phụ thuộc mạng. Bắt được
vì trong thư mục tạm không có `GEMINI_API_KEY`, nên lỗi hiện ra thành
`Lý do: gemini-3.5-flash: thieu GEMINI_API_KEY trong .env` nằm giữa nội dung tin nhắn mà bài kiểm
thử mong đợi. **Đã sửa:** `NguoiTruc.__init__` nhận thêm `tra_loi_ai_fn=None`, `xu_ly_tin` truyền
xuống, và `TrucGia` trong kiểm thử cũng nhận tham số này.

**Lỗi 2 — số tiền mất dấu phân cách (lỗi thật của sản phẩm, không phải của kiểm thử).** Lần gọi
Gemini thật **đầu tiên** cho ra: *"tổng chi tiêu quảng cáo là **20319895** đồng"*. Nguyên nhân:
công cụ trả JSON số nguyên thô, AI chép nguyên xi. Báo cáo Telegram của Đại vẫn ghi `20.319.895`,
nên cách viết này đọc rất mệt. **Không thể sửa bằng cách bảo AI tự thêm dấu phân cách** — làm vậy
là để AI *sửa số*, đúng rủi ro đã tránh ở Giai đoạn 3. **Đã sửa:** công cụ trả thêm các trường
`*_hien_thi` là **chuỗi đã định dạng sẵn** (`"20.319.895"`), câu lệnh bắt AI chép từ trường đó.
Gọi lại Gemini thật: số ra đúng `20.319.895` ✅.

**Lỗi 3 — hai bài kiểm thử cũ của GĐ2 sẽ hỏng.** `test_cau_hoi_rong_cung_tra_loi_chua_co_AI` và
`test_tin_tu_dai_hoi_so_lieu_thi_bao_chua_co` đều khẳng định có chữ `"giai đoạn sau"` — câu đó
không còn tồn tại sau GĐ4. Kế hoạch đã liệt kê việc sửa nhưng **thiếu bài thứ nhất** (nó nằm ở
một lớp khác của file, không phải lớp `TestTraLoiTinNhan`). Đã sửa cả hai.

### Một hạn chế đã biết, KHÔNG sửa được bằng code

Model chèn khoảng trắng quanh dấu gạch nối trong tên chiến dịch: `2026-09-04-dainq-Online-Scale KHTN`
thành `2026 - 09 - 04 - dainq - Online - Scale KHTN`. Câu lệnh đã ghi rõ *"Tên chiến dịch phải chép
y nguyên từng ký tự, không thêm khoảng trắng quanh dấu gạch nối"* nhưng model vẫn làm. Đây là hành
vi của model, không phải lỗi logic: **không sai số, vẫn đọc được, vẫn nhận ra đúng chiến dịch nào**.
Ghi lại đây để sau này không ai mất công "sửa" nó lần nữa.

### Ghi chú nhỏ: kiểu xuống dòng của repo KHÔNG nhất quán

Đo thật ngày 29/09/2026:

| File | Kiểu xuống dòng |
|---|---|
| `ai.py`, `nguoi_truc.py`, `tests/test_ai.py` (các file mới) | **LF** |
| `report.py`, `lich_su.py`, `dashboard.py`, các file `.bat` (các file cũ) | **CRLF** |

Repo **không có** `.gitattributes`, nên Git không tự chuyển. Vì vậy:

- `cong_cu.py` và `tests/test_cong_cu.py` viết bằng **LF** là đúng — khớp với `ai.py` cùng giai đoạn.
- **File `.bat` mới (nếu có) phải ghi bằng CRLF** — đây là quy tắc cũ vẫn đúng, vì batch trên Windows
  cần CRLF. Giai đoạn này không tạo file `.bat` nào.
- Ghi chú trong `HANDOFF.md` nói "cả repo đang CRLF" nay **không còn đúng** với các file mới.

---

## ⚠️ ĐỌC TRƯỚC KHI DUYỆT — ba sự thật về hệ thống hiện tại

### 1. Trần miễn phí của Gemini là 20 lượt/ngày **cho mỗi model** — và sáng nay đã chạm trần

Bằng chứng từ `logs/baocao.log` ngày 29/09/2026:

```
[08:05:23] AI viet nhan dinh that bai: HTTP 429 - het han muc goi AI, thu lai sau [RESOURCE_EXHAUSTED]
[08:10:35] AI viet nhan dinh that bai: HTTP 429 - het han muc goi AI, thu lai sau [RESOURCE_EXHAUSTED]
[08:10:36] THANH CONG - moc 8h, da gui Telegram      ← báo cáo VẪN gửi, chỉ thiếu phần nhận định
```

Thông báo gốc của Google: `limit: 20, model: gemini-3.6-flash`,
`quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier`.

Điểm mấu chốt: **`PerDayPerProjectPerModel` — trần tính RIÊNG cho từng model.** Đây là chỗ kế hoạch này lợi dụng:

> **Báo cáo và hỏi đáp dùng HAI MODEL KHÁC NHAU** ⇒ hai trần riêng, không tranh nhau.
> Báo cáo: `gemini-3.6-flash` (đang chạy, đã kiểm chứng) · Hỏi đáp: `gemini-3.8-flash` (đã kiểm chứng gọi được công cụ).

Nếu không tách, mỗi câu hỏi của Đại (2–4 lượt AI) sẽ **ăn vào trần của báo cáo** và báo cáo mất phần nhận định.

### 2. Lịch sử mới có **1 ngày** — khoảng 7 ngày đầu chưa so sánh được

Đọc thẳng `logs/lich-su.json` hôm nay (29/09):

```
So ngay: 1
  2026-09-28  moc=8  day_du=True  chi_tieu=20.319.895  luot_mua=40  so_camp=19
```

⇒ Câu hỏi kiểu *"tuần này so với tuần trước"* **chưa trả lời được** — không phải lỗi, mà là dữ liệu chưa tích đủ. Kế hoạch làm đúng theo thực tế đó: công cụ trả về `"loi": "không có ngày nào có số liệu trong khoảng ..."`, và AI **phải nói thật là không có**, tuyệt đối không bịa.

### 3. Lịch sử chỉ lưu **một bản ghi cho mỗi ngày**, không lưu theo giờ

`lich_su.ghi()` ghi đè theo ngày (bản đầy đủ thắng bản một phần). Hệ quả:

- Câu hỏi *"hôm nay chi bao nhiêu?"* lúc 9h sáng → lịch sử chưa có ngày 29/09.
- Kế hoạch này **cho phép** công cụ `lay_mot_ngay` gọi Meta trực tiếp **khi và chỉ khi** ngày được hỏi là hôm nay và lịch sử chưa có. Giới hạn **một lần gọi Meta cho mỗi câu hỏi** (mỗi lần gọi Meta mất 15–30 giây, đã đo được trong log: `08:00:05 → 08:00:37`).

---

## Khác với bản thiết kế — đọc trước khi duyệt

| # | Bản thiết kế nói | Kế hoạch này làm | Vì sao |
|---|---|---|---|
| 1 | Bốn công cụ nằm trong `ai.py` | **Tách ra `cong_cu.py`** | Công cụ là *đọc dữ liệu*, không phải *gọi AI*. Tách ra thì `cong_cu.py` **không chạm mạng** ⇒ kiểm thử được toàn bộ mà không cần giả lập mạng, và sau này đổi nhà cung cấp AI không phải sửa file này |
| 2 | "Tối đa 5 lượt gọi công cụ rồi buộc trả lời" | **`TOI_DA_LUOT_CONG_CU = 3`** | Trần miễn phí chỉ 20 lượt/ngày/model. 5 lượt công cụ + 1 lượt trả lời = 6 lượt cho **một** câu hỏi ⇒ chỉ 3 câu hỏi là hết ngày. Phép thử thật cho thấy AI cần **3 lượt công cụ rồi trả lời ở lượt 4** ⇒ 3 là vừa đủ và khớp bằng chứng |
| 3 | "Nhà cung cấp: Gemini" (một model) | **Hai model: `GEMINI_MODEL` cho báo cáo, `GEMINI_MODEL_HOI_DAP` cho hỏi đáp** | Trần tính riêng theo model (bằng chứng ở mục 1 phía trên). Không tách thì hỏi đáp ăn hết trần của báo cáo |
| 4 | Không nói gì về mốc thời gian | **Thêm `cong_cu.moc_thoi_gian()`** | Phép thử thật cho thấy AI tự hiểu "tuần này" thành 28/09→29/09. Phạm vi thời gian phải do code tính |
| 5 | Không nói gì về định dạng câu trả lời | **Câu lệnh cấm markdown, giới hạn 8 câu** | Phép thử thật cho ra câu trả lời đầy `**`, `` ` `` và gạch đầu dòng — Telegram hiện rất rối |
| 6 | Không nói gì về `thoughtSignature` | **Gửi lại nguyên `content` của model** | Gemini 3.x trả về `thoughtSignature` trong part; bóc ra ghép lại có thể hỏng vòng lặp. Cách an toàn nhất là giữ nguyên object |
| 7 | Không nói gì về `maxOutputTokens` | **Đặt `maxOutputTokens = 2000`** | Câu trả lời trong phép thử **bị cắt giữa dòng**. Model 3.x tính cả token suy nghĩ vào phần output nên dễ chạm trần mặc định |
| 8 | Không nói gì về định dạng số tiền | **Công cụ trả thêm trường `*_hien_thi` là chuỗi đã định dạng** (`"20.319.895"`), câu lệnh bắt AI chép từ đó | **Lỗi thật, phép kiểm chứng bắt được:** lần gọi Gemini thật đầu tiên cho ra `20319895 đồng` — mất dấu phân cách, đọc rất mệt. Không thể bảo AI tự thêm dấu vì như vậy là để AI *sửa số* |
| 9 | Không nói gì về đường tiêm hàm AI trong `NguoiTruc` | **`NguoiTruc.__init__` nhận thêm `tra_loi_ai_fn`** | **Lỗi thật, dựng thử bắt được:** thiếu đường tiêm thì bộ kiểm thử **gọi AI thật** — tốn lượt AI và phụ thuộc mạng |

---

## Kiến trúc sau khi làm

```
Đại nhắn Telegram: "camp nào tệ nhất tuần này?"
   │
   ▼
nguoi_truc.nghe_telegram()          ← đã có từ GĐ2
   │  chỉ nhận tin từ TELEGRAM_CHAT_ID của Đại
   ▼
nguoi_truc.tra_loi_tin_nhan()       ← SỬA ở kế hoạch này
   │  câu hỏi sức khoẻ  → trả lời ngay (giữ nguyên GĐ2)
   │  câu hỏi số liệu   → đi tiếp
   ▼
cong_cu.moc_thoi_gian()             ← MỚI: code tính phạm vi ngày
   │
   ▼
ai.tra_loi(câu hỏi, bộ công cụ)     ← MỚI: vòng lặp công cụ
   │
   ├─► gọi Gemini kèm khai báo 4 công cụ
   │        │
   │        ├── AI trả về CHỮ          → xong, gửi Đại
   │        └── AI xin GỌI CÔNG CỤ
   │                 │
   │                 ▼
   │            cong_cu.BoCongCu.thuc_thi(tên, tham số)
   │                 │  đọc logs/lich-su.json  (hoặc gọi Meta nếu là hôm nay)
   │                 │  CODE tính sẵn: chênh lệch, phần trăm, chi phí mỗi đơn, thứ hạng
   │                 ▼
   │            trả kết quả về cho Gemini, lặp lại (tối đa 3 lượt công cụ)
   │
   ▼
gui_tin_nhan(câu trả lời)            ← đã có từ GĐ2
```

**Ranh giới bất biến (giống GĐ3):** mọi lời gọi AI đều bọc trong `try`. AI lỗi vì bất kỳ lý do gì → Đại nhận tin nhắn nói rõ lý do. Người trực **không bao giờ chết** vì AI.

---

## Task 1 — `cong_cu.py` (file mới): bốn công cụ + mốc thời gian

**Files:**
- Create: `cong_cu.py`
- Test: `tests/test_cong_cu.py`

- [ ] **Bước 1: viết `cong_cu.py`**

```python
"""
CONG CU TRA LOI CAU HOI
========================
Bon cong cu ma AI duoc phep goi de lay so lieu. CODE chay cong cu, AI chi doc
ket qua tra ve.

Nguyen tac quan trong nhat (bai hoc tu Giai doan 3, lap lai o day):
  PHEP TINH DO CODE LAM. Cong cu tra ve so DA TINH SAN (chenh lech, phan tram,
  chi phi moi don, thu hang). AI khong tu tinh, chi chep lai.

Vi sao tach rieng khoi ai.py: file nay KHONG cham mang, KHONG biet Gemini la gi.
Nho vay kiem thu duoc toan bo ma khong can gia lap mang, va doi nha cung cap AI
sau nay khong phai sua file nay.
"""
from datetime import date, datetime
from pathlib import Path

import lich_su

DUONG_DAN_MAC_DINH = Path(__file__).parent / "logs" / "lich-su.json"

# So camp toi da tra ve trong mot lan xep hang. Nhieu hon thi cau lenh gui cho
# AI dai vo ich, va AI cung khong doc het.
TOI_DA_CAMP = 15

# Cac chi so dung khi so sanh hai ky. Ten viet CO DAU vi day la chu gui cho AI
# doc va AI se chep lai -> phai co dau ngay tu day.
#
# KHAC voi ai.TEN_CHI_SO (viet khong dau): bang do la bang nam trong bao cao
# Telegram, da kiem chung va da chot, khong dung vao.
CHI_SO_SO_SANH = [
    ("spend", "chi tieu", "tien"),
    ("msg", "tin nhan moi", "so"),
    ("contact", "lien he moi", "so"),
    ("order", "don hang", "so"),
    ("purchase", "luot mua", "so"),
    ("payment", "luot thanh toan", "so"),
    ("comment", "binh luan", "so"),
]

# Chi so duoc phep dung khi xep hang chien dich.
CHI_SO_XEP_HANG = ("spend", "purchase", "payment", "msg", "cpr")

THU_TRONG_TUAN = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu",
                  "Thứ Bảy", "Chủ Nhật"]


def _thanh_ngay(s):
    """'2026-09-28' -> date. Sai dinh dang -> None (khong nem loi)."""
    try:
        return datetime.strptime(str(s), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def _hien_thi_ngay(s):
    """'2026-09-28' -> '28/09/2026'. Sai dinh dang -> nguyen chuoi cu."""
    d = _thanh_ngay(s)
    return d.strftime("%d/%m/%Y") if d else str(s)


def _lam_tron(v, kieu):
    """Lam tron theo kieu chi so. 'tien' thi ve so nguyen dong."""
    try:
        return int(round(float(v or 0)))
    except (ValueError, TypeError):
        return 0


def _tien(v):
    """20319895 -> '20.319.895'. Kieu Viet Nam (dau cham ngan nghin)."""
    return f"{_lam_tron(v, 'tien'):,}".replace(",", ".")


def _chuoi_so(v):
    """Moi chi so thanh CHUOI da dinh dang san.

    Vi sao tra ve CHUOI chu khong phai so: da thu that ngay 29/09/2026, AI chep
    so tho tu JSON nen viet ra '20319895 dong' - thieu dau phan cach, doc rat
    met (bao cao cua Dai van ghi '20.319.895'). Neu de AI tu them dau phan cach
    thi tuc la de AI SUA SO, dung rai ro da tranh o Giai doan 3.
    Cach dung: CODE dinh dang san, AI chep nguyen chuoi.
    """
    ra = {}
    for khoa, ten, kieu in CHI_SO_SO_SANH:
        ra[ten] = _tien(v.get(khoa, 0)) if kieu == "tien" else str(int(v.get(khoa, 0) or 0))
    return ra


def moc_thoi_gian(duong_dan=None, hom_nay=None):
    """Chu mo ta MOC THOI GIAN, do CODE tinh. Dua vao cau lenh cho AI.

    Ly do phai co: khi thu nghiem ngay 29/09/2026, AI tu hieu "tuan nay" thanh
    28/09 -> 29/09 (hai ngay) va tu chon "tuan truoc" la 21/09 -> 27/09. Ca hai
    deu khong dung y nguoi hoi, va luc do lich su chi co so toi 28/09.

    Pham vi thoi gian la mot PHEP TINH. Phai do code lam.
    """
    duong_dan = Path(duong_dan or DUONG_DAN_MAC_DINH)
    hom_nay = hom_nay or date.today()

    dong = [f"Hôm nay: {hom_nay.strftime('%d/%m/%Y')} "
            f"({THU_TRONG_TUAN[hom_nay.weekday()]})"]

    try:
        data = lich_su.doc(duong_dan)
        ds_ngay = sorted(k for k in data if data[k].get("tong"))
    except Exception:
        ds_ngay = []

    if not ds_ngay:
        dong.append("Lịch sử CHƯA CÓ ngày nào. Không trả lời được câu hỏi "
                    "cần số liệu. Nếu được hỏi, hãy nói thật là chưa có số.")
        return "\n".join(dong)

    dong.append(f"Ngày cuối cùng CÓ số liệu: {_hien_thi_ngay(ds_ngay[-1])}")
    dong.append(f"Số liệu có từ ngày: {_hien_thi_ngay(ds_ngay[0])} "
                f"(tổng cộng {len(ds_ngay)} ngày)")

    bay_ngay = ds_ngay[-7:]
    dong.append(f"7 ngày có số gần nhất: {_hien_thi_ngay(bay_ngay[0])} "
                f"đến {_hien_thi_ngay(bay_ngay[-1])}")

    truoc_do = ds_ngay[-14:-7]
    if truoc_do:
        dong.append(f"7 ngày liền trước đó: {_hien_thi_ngay(truoc_do[0])} "
                    f"đến {_hien_thi_ngay(truoc_do[-1])}")
    else:
        dong.append("7 ngày liền trước đó: CHƯA CÓ số liệu, không so sánh được.")

    dong.append("Khi trả lời, phải nói rõ bạn dùng khoảng ngày nào. "
                "Không tự chọn khoảng khác ngoài các khoảng ở trên.")
    return "\n".join(dong)


class BoCongCu:
    """Bon cong cu AI duoc phep goi. Mot doi tuong song trong MOT cau hoi.

    lay_so_hom_nay_fn(ngay) -> dict stats hoac None.
        None (mac dinh) nghia la KHONG goi Meta. Day la che do an toan, dung
        trong kiem thu va trong truong hop chua cau hinh token.
    """

    def __init__(self, duong_dan=None, lay_so_hom_nay_fn=None, hom_nay=None):
        self.duong_dan = Path(duong_dan or DUONG_DAN_MAC_DINH)
        self.lay_so_hom_nay_fn = lay_so_hom_nay_fn
        self.hom_nay = hom_nay or date.today()
        # Moi cau hoi toi da MOT lan goi Meta: goi Meta mat 15-30 giay, ma AI
        # co the xin goi cong cu nhieu lan lien tiep.
        self.da_goi_meta = False
        self.cache_meta = None

    # ---------- khai bao cho AI ----------

    def khai_bao(self):
        """Danh sach khai bao cong cu, dung lam truong `tools` gui cho Gemini."""
        return [{"functionDeclarations": [
            {
                "name": "lay_mot_ngay",
                "description": ("Lay so lieu tong hop cua MOT ngay. Dung khi cau hoi "
                                "chi ve mot ngay cu the. Neu ngay do chua co trong "
                                "lich su va la hom nay thi he thong tu lay tu Meta."),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "ngay": {"type": "STRING",
                                 "description": "Ngay can lay, dang YYYY-MM-DD"},
                    },
                    "required": ["ngay"],
                },
            },
            {
                "name": "lay_khoang",
                "description": ("Cong don so lieu trong mot khoang ngay, bao gom ca hai "
                                "dau mut. Dung khi cau hoi noi ve nhieu ngay."),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "tu": {"type": "STRING", "description": "Tu ngay, YYYY-MM-DD"},
                        "den": {"type": "STRING", "description": "Den ngay, YYYY-MM-DD"},
                    },
                    "required": ["tu", "den"],
                },
            },
            {
                "name": "xep_hang_camp",
                "description": ("Xep hang cac chien dich theo mot chi so trong mot khoang "
                                "ngay. Ket qua da duoc sap san. Chi so hop le: "
                                "spend (chi tieu), purchase (luot mua), payment (luot "
                                "thanh toan), msg (tin nhan moi), cpr (chi phi moi don)."),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "tu": {"type": "STRING", "description": "Tu ngay, YYYY-MM-DD"},
                        "den": {"type": "STRING", "description": "Den ngay, YYYY-MM-DD"},
                        "sap_theo": {"type": "STRING",
                                     "description": "Chi so de sap xep"},
                        "tang_dan": {"type": "BOOLEAN",
                                     "description": ("true = nho nhat len dau "
                                                     "(muon tim cai te nhat thi dung true)")},
                    },
                    "required": ["tu", "den", "sap_theo"],
                },
            },
            {
                "name": "so_sanh",
                "description": ("So sanh hai khoang ngay voi nhau. He thong da tinh san "
                                "chenh lech va phan tram. Dung khi cau hoi co y so sanh."),
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "ky_nay_tu": {"type": "STRING", "description": "Ky nay, tu ngay"},
                        "ky_nay_den": {"type": "STRING", "description": "Ky nay, den ngay"},
                        "ky_truoc_tu": {"type": "STRING", "description": "Ky truoc, tu ngay"},
                        "ky_truoc_den": {"type": "STRING", "description": "Ky truoc, den ngay"},
                    },
                    "required": ["ky_nay_tu", "ky_nay_den", "ky_truoc_tu", "ky_truoc_den"],
                },
            },
        ]}]

    # ---------- phan phoi ----------

    def thuc_thi(self, ten, args):
        """Chay mot cong cu theo ten. KHONG BAO GIO nem loi ra ngoai.

        Moi loi deu tra ve qua khoa "loi", de AI doc duoc va noi that voi Dai
        thay vi im lang.
        """
        args = args or {}
        try:
            if ten == "lay_mot_ngay":
                return self.lay_mot_ngay(args.get("ngay"))
            if ten == "lay_khoang":
                return self.lay_khoang(args.get("tu"), args.get("den"))
            if ten == "xep_hang_camp":
                return self.xep_hang_camp(
                    args.get("tu"), args.get("den"),
                    args.get("sap_theo"), args.get("tang_dan"))
            if ten == "so_sanh":
                return self.so_sanh(
                    args.get("ky_nay_tu"), args.get("ky_nay_den"),
                    args.get("ky_truoc_tu"), args.get("ky_truoc_den"))
        except Exception as e:
            return {"loi": f"Cong cu '{ten}' bi loi khi chay: {e}"}
        return {"loi": f"Khong co cong cu nao ten '{ten}'. "
                       f"Chi dung: lay_mot_ngay, lay_khoang, xep_hang_camp, so_sanh."}

    # ---------- bon cong cu ----------

    def lay_mot_ngay(self, ngay):
        if _thanh_ngay(ngay) is None:
            return {"loi": f"Ngay '{ngay}' sai dinh dang. Phai la YYYY-MM-DD."}

        ban_ghi = lich_su.lay_mot_ngay(self.duong_dan, ngay)
        if ban_ghi:
            tong = ban_ghi.get("tong") or {}
            return {
                "ngay": str(ngay),
                "nguon": "so da luu trong lich su",
                "moc_gio_bao_cao": ban_ghi.get("moc"),
                "day_du_ca_ngay": bool(ban_ghi.get("day_du")),
                "ghi_chu": ("day_du_ca_ngay = false nghia la so nay moi tich luy "
                            "den mot moc gio trong ngay, chua phai ca ngay."),
                "tong": tong,
                "tong_hien_thi": _chuoi_so(tong),
                "so_camp": ban_ghi.get("so_camp", 0),
            }

        # Chua co trong lich su. Chi goi Meta khi la HOM NAY va duoc phep.
        d = _thanh_ngay(ngay)
        if d == self.hom_nay and self.lay_so_hom_nay_fn is not None:
            stats = self._lay_meta_mot_lan()
            if stats:
                tong = stats.get("totals") or {}
                return {
                    "ngay": str(ngay),
                    "nguon": "vua lay truc tiep tu Meta",
                    "day_du_ca_ngay": False,
                    "ghi_chu": ("So tich luy tu 0h den luc nay, CHUA het ngay. "
                                "Phai noi ro dieu nay khi tra loi."),
                    "tong": tong,
                    "tong_hien_thi": _chuoi_so(tong),
                    "so_camp": stats.get("total_campaigns", 0),
                }

        return {"loi": (f"Lich su chua co so ngay {ngay}. "
                        f"Ngay cuoi cung co so la {self._ngay_cuoi() or 'khong co'}.")}

    def lay_khoang(self, tu, den):
        if _thanh_ngay(tu) is None or _thanh_ngay(den) is None:
            return {"loi": "Ngay phai co dinh dang YYYY-MM-DD."}
        r = lich_su.lay_khoang(self.duong_dan, tu, den)
        if not r.get("so_ngay"):
            return {"loi": (f"Khong co ngay nao co so lieu trong khoang "
                            f"{tu} den {den}. Ngay cuoi cung co so la "
                            f"{self._ngay_cuoi() or 'khong co'}.")}
        return {"tu": str(tu), "den": str(den), "so_ngay": r["so_ngay"],
                "tong": r.get("tong") or {},
                "tong_hien_thi": _chuoi_so(r.get("tong") or {})}

    def xep_hang_camp(self, tu, den, sap_theo="spend", tang_dan=False):
        if _thanh_ngay(tu) is None or _thanh_ngay(den) is None:
            return {"loi": "Ngay phai co dinh dang YYYY-MM-DD."}
        sap_theo = str(sap_theo or "spend").strip().lower()
        if sap_theo not in CHI_SO_XEP_HANG:
            return {"loi": f"Chi so '{sap_theo}' khong hop le. "
                           f"Chi dung: {list(CHI_SO_XEP_HANG)}"}

        gop = self._gop_camp(tu, den)
        if not gop:
            return {"loi": (f"Khong co du lieu chien dich nao trong khoang "
                            f"{tu} den {den}.")}

        ds = list(gop.values())
        if sap_theo == "cpr":
            # Camp CHUA CO don thi cpr la None -> day xuong cuoi cung, KHONG
            # coi la 0. So 0 trong nhu re nhat, da biet la sai.
            co_don = [c for c in ds if c.get("cpr")]
            khong_don = [c for c in ds if not c.get("cpr")]
            co_don.sort(key=lambda c: c["cpr"], reverse=not tang_dan)
            ds = co_don + khong_don
        else:
            ds.sort(key=lambda c: float(c.get(sap_theo, 0) or 0),
                    reverse=not tang_dan)

        return {"tu": str(tu), "den": str(den), "so_camp": len(ds),
                "sap_theo": sap_theo, "tang_dan": bool(tang_dan),
                "danh_sach": ds[:TOI_DA_CAMP]}

    def so_sanh(self, ky_nay_tu, ky_nay_den, ky_truoc_tu, ky_truoc_den):
        for v in (ky_nay_tu, ky_nay_den, ky_truoc_tu, ky_truoc_den):
            if _thanh_ngay(v) is None:
                return {"loi": "Ngay phai co dinh dang YYYY-MM-DD."}

        nay = lich_su.lay_khoang(self.duong_dan, ky_nay_tu, ky_nay_den)
        truoc = lich_su.lay_khoang(self.duong_dan, ky_truoc_tu, ky_truoc_den)
        if not nay.get("so_ngay"):
            return {"loi": (f"Ky nay ({ky_nay_tu} den {ky_nay_den}) khong co so lieu, "
                            f"khong so sanh duoc.")}

        co_ky_truoc = bool(truoc.get("so_ngay"))
        bang = []
        for khoa, ten, kieu in CHI_SO_SO_SANH:
            moi = _lam_tron((nay.get("tong") or {}).get(khoa, 0), kieu)
            moi_chu = _tien(moi) if kieu == "tien" else str(moi)
            if not co_ky_truoc:
                bang.append({"ten": ten, "ky_nay": moi, "ky_truoc": None,
                             "chenh_lech": None, "phan_tram": None,
                             "ky_nay_hien_thi": moi_chu,
                             "ky_truoc_hien_thi": None,
                             "chenh_lech_hien_thi": None})
                continue
            cu = _lam_tron((truoc.get("tong") or {}).get(khoa, 0), kieu)
            chenh = moi - cu
            cu_chu = _tien(cu) if kieu == "tien" else str(cu)
            chenh_chu = ("+" if chenh >= 0 else "-") + (
                _tien(abs(chenh)) if kieu == "tien" else str(abs(chenh)))
            bang.append({
                "ten": ten, "ky_nay": moi, "ky_truoc": cu, "chenh_lech": chenh,
                "phan_tram": (round(chenh / cu * 100) if cu else None),
                "ky_nay_hien_thi": moi_chu, "ky_truoc_hien_thi": cu_chu,
                "chenh_lech_hien_thi": chenh_chu,
            })

        return {
            "ky_nay": f"{ky_nay_tu} den {ky_nay_den}",
            "so_ngay_ky_nay": nay.get("so_ngay", 0),
            "ky_truoc": (f"{ky_truoc_tu} den {ky_truoc_den}" if co_ky_truoc else None),
            "so_ngay_ky_truoc": truoc.get("so_ngay", 0),
            "bang": bang,
            "ghi_chu": ("Cot 'chenh_lech' va 'phan_tram' do he thong tinh san. "
                        "Chep nguyen, khong tu tinh lai. Neu 'ky_truoc' la null thi "
                        "noi ro la khong co so ky truoc, dung so sanh."),
        }

    # ---------- phu tro ----------

    def _gop_camp(self, tu, den):
        """Cong don tung chien dich qua cac ngay trong khoang.

        Khoa la id; id rong thi dung ten. Id khong doi khi camp doi ten.
        """
        data = lich_su.doc(self.duong_dan)
        gop = {}
        for ngay in sorted(data):
            if not (tu <= ngay <= den):
                continue
            for c in (data[ngay].get("camp") or []):
                khoa = str(c.get("id") or "").strip() or str(c.get("name") or "").strip()
                if not khoa:
                    continue
                if khoa not in gop:
                    gop[khoa] = {"id": str(c.get("id") or ""),
                                 "name": c.get("name") or "",
                                 "spend": 0.0, "purchase": 0, "payment": 0, "msg": 0,
                                 "so_ngay_xuat_hien": 0}
                g = gop[khoa]
                g["spend"] += float(c.get("spend", 0) or 0)
                for k in ("purchase", "payment", "msg"):
                    g[k] += int(c.get(k, 0) or 0)
                g["so_ngay_xuat_hien"] += 1
                if not g["name"] and c.get("name"):
                    g["name"] = c["name"]

        for g in gop.values():
            g["spend"] = int(round(g["spend"]))
            g["cpr"] = (int(round(g["spend"] / g["purchase"]))
                        if g["purchase"] > 0 else None)
            # Ten thu hai cho cung mot so, de AI khong phai doan 'cpr' la gi.
            g["chi_phi_moi_don"] = g["cpr"]
            # Cac truong CHUOI da dinh dang san. AI phai chep tu day, khong
            # chep tu truong so tho (xem _chuoi_so de biet ly do).
            g["chi_tieu_hien_thi"] = _tien(g["spend"])
            g["chi_phi_moi_don_hien_thi"] = (
                f"{_tien(g['cpr'])} d" if g["cpr"] else "chua co don")
            g["tin_nhan_moi"] = str(g["msg"])
            g["luot_mua"] = str(g["purchase"])
        return gop

    def _lay_meta_mot_lan(self):
        """Goi Meta lay so hom nay. Toi da MOT lan cho moi cau hoi."""
        if self.da_goi_meta:
            return self.cache_meta
        self.da_goi_meta = True
        try:
            self.cache_meta = self.lay_so_hom_nay_fn(self.hom_nay)
        except Exception:
            self.cache_meta = None
        return self.cache_meta

    def _ngay_cuoi(self):
        try:
            data = lich_su.doc(self.duong_dan)
        except Exception:
            return None
        ds = sorted(k for k in data if data[k].get("tong"))
        return ds[-1] if ds else None
```

- [ ] **Bước 2: viết `tests/test_cong_cu.py`**

```python
"""Kiem thu cong_cu.py - bon cong cu tra loi cau hoi. KHONG goi mang."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import cong_cu


def _ghi_lich_su(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


LICH_SU = {
    "2026-09-27": {
        "moc": 8, "day_du": True, "so_camp": 2,
        "tong": {"spend": 5000000, "msg": 60, "contact": 20, "order": 5,
                 "purchase": 20, "payment": 18, "comment": 1},
        "camp": [
            {"id": "A", "name": "dainq A", "spend": 3000000, "purchase": 18,
             "payment": 16, "msg": 40, "cpr": 166666},
            {"id": "B", "name": "dainq B", "spend": 2000000, "purchase": 2,
             "payment": 2, "msg": 20, "cpr": 1000000},
        ],
    },
    "2026-09-28": {
        "moc": 8, "day_du": True, "so_camp": 2,
        "tong": {"spend": 7000000, "msg": 90, "contact": 30, "order": 8,
                 "purchase": 15, "payment": 12, "comment": 3},
        "camp": [
            {"id": "A", "name": "dainq A", "spend": 4000000, "purchase": 12,
             "payment": 10, "msg": 50, "cpr": 333333},
            {"id": "B", "name": "dainq B", "spend": 3000000, "purchase": 3,
             "payment": 2, "msg": 40, "cpr": 1000000},
        ],
    },
}
```

Các bài kiểm thử cần có (tên + điều phải khẳng định):

| Nhóm | Bài kiểm thử |
|---|---|
| `moc_thoi_gian` | `test_ghi_ro_hom_nay_va_thu` (có "29/09/2026" và "Thứ Ba") · `test_chi_ro_ngay_cuoi_co_so` (28/09/2026) · `test_khoang_7_ngay_gan_nhat` (22/09 → 28/09) · `test_chua_du_7_ngay_thi_noi_ro_chua_so_sanh_duoc` · `test_lich_su_rong_thi_noi_that` · `test_file_hong_khong_nem_loi` |
| `khai_bao` | `test_co_du_bon_cong_cu` · `test_moi_cong_cu_co_description_va_parameters` · `test_ten_cong_cu_dung_nhu_thuc_thi_nhan` (khai báo và `thuc_thi` phải khớp tên — nếu lệch thì AI gọi tên không chạy được) |
| `lay_mot_ngay` | `test_lay_dung_so_mot_ngay` · `test_ngay_sai_dinh_dang_tra_loi` · `test_ngay_khong_co_trong_lich_su_tra_loi_kem_ngay_cuoi` · `test_hom_nay_chua_co_thi_goi_meta_mot_lan` · `test_hom_nay_goi_meta_hai_lan_chi_chay_that_mot_lan` (đếm số lần hàm Meta được gọi = 1) · `test_meta_loi_thi_tra_loi_chu_khong_nem` · `test_khong_tiem_ham_meta_thi_khong_goi` |
| `lay_khoang` | `test_cong_don_dung_hai_ngay` (spend = 12.000.000, so_ngay = 2) · `test_khoang_khong_co_du_lieu_tra_loi` · `test_ngay_sai_dinh_dang_tra_loi` |
| `xep_hang_camp` | `test_gop_camp_qua_hai_ngay` (camp A: spend 7.000.000, purchase 30) · `test_sap_theo_chi_tieu_giam_dan_mac_dinh` · `test_tang_dan_true_thi_nho_nhat_len_dau` · `test_camp_chua_co_don_bi_day_xuong_cuoi_khi_sap_theo_cpr` (KHÔNG được coi cpr = 0) · `test_chi_so_sai_tra_loi_kem_danh_sach_hop_le` · `test_khoang_rong_tra_loi` · `test_chi_phi_moi_don_bang_chi_tieu_chia_luot_mua` |
| `so_sanh` | `test_tinh_dung_chenh_lech` (7000000 − 5000000 = 2000000, phan_tram = 40) · `test_ky_truoc_rong_thi_ky_truoc_la_None` · `test_ky_nay_rong_thi_tra_loi` · `test_chia_cho_khong_khi_ky_truoc_bang_0` (phan_tram = None, không chia 0) |
| An toàn | `test_cong_cu_la_tra_loi_chu_khong_nem` · `test_ten_cong_cu_sai_tra_loi` · `test_file_lich_su_khong_ton_tai_khong_lam_chet` · `test_tham_so_rong_khong_lam_chet` · `test_tham_so_None_khong_lam_chet` · `test_file_lich_su_hong_khong_lam_chet` |
| `TestDinhDangTien` (từ lỗi thật) | `test_tien_dinh_dang_kieu_viet_nam` (`20319895` → `"20.319.895"`) · `test_lay_mot_ngay_co_truong_hien_thi` · `test_lay_khoang_co_truong_hien_thi` · `test_xep_hang_camp_co_truong_hien_thi` · `test_camp_chua_co_don_hien_thi_ro_chu` · `test_so_sanh_co_truong_hien_thi` · `test_chenh_lech_am_co_dau_tru` · `test_ky_truoc_rong_thi_truong_hien_thi_la_None` |

---

## Task 2 — `ai.py`: thêm khả năng gọi công cụ và vòng lặp trả lời

**Files:**
- Modify: `ai.py`
- Test: `tests/test_ai.py`

- [ ] **Bước 1: thêm hằng số và câu lệnh**

Thêm ngay sau `SO_NGAY_KY_TRUOC = 7`:

```python
# Model RIENG cho phan hoi dap. Ly do: tran mien phi cua Gemini tinh rieng cho
# tung model (quotaId: GenerateRequestsPerDayPerProjectPerModel-FreeTier, do
# duoc 20 luot/ngay). Neu dung chung model voi bao cao thi moi cau hoi cua Dai
# se an vao tran cua bao cao, lam bao cao mat phan nhan dinh.
#
# gemini-3.8-flash DA DUOC THU THAT ngay 29/09/2026: goi duoc cong cu.
# gemini-2.5-flash KHONG dung duoc nua (404: no longer available to new users).
MODEL_HOI_DAP_MAC_DINH = "gemini-3.8-flash"

# Model du phong, dung khi model chinh bi 503/404/429. De trong thi khong dung.
# gemini-3.5-flash cung DA THU THAT ngay 29/09/2026: goi duoc cong cu.
MODEL_HOI_DAP_DU_PHONG_MAC_DINH = "gemini-3.5-flash"

# So luot AI duoc phep xin goi cong cu truoc khi bi buoc phai tra loi.
#
# Vi sao 3: phep thu that ngay 29/09/2026 cho thay AI can DUNG 3 luot cong cu
# (xep_hang_camp -> lay_khoang ky truoc -> lay_khoang ky nay) roi tra loi o luot
# thu 4. Dat 3 la vua du va khop bang chung. Dat 5 nhu ban thiet ke thi mot cau
# hoi ton 6 luot AI => chi 3 cau hoi la het tran 20 luot/ngay.
TOI_DA_LUOT_CONG_CU = 3

# Thoi gian toi da cho mot luot goi AI khi tra loi cau hoi (giay).
# Ngan hon TIMEOUT cua bao cao: nguoi dang cho tin nhan, khong the doi 60 giay.
TIMEOUT_HOI_DAP = 30

# Tran token cho mot cau tra loi. Phai dat vi model 3.x tinh ca token suy nghi
# vao phan output; trong phep thu that cau tra loi bi CAT giua dong.
TOI_DA_TOKEN_TRA_LOI = 2000
```

Thêm câu lệnh có dấu (đặt ngay sau `HUONG_DAN`):

```python
# Cau lenh cho phan HOI DAP (khac phan viet bao cao o tren).
#
# Viet CO DAU, cung ly do nhu HUONG_DAN: Gemini bat chuoc giong van cua chinh
# cau lenh. Cau lenh khong dau thi no tra ve khong dau.
HUONG_DAN_HOI_DAP = (
    "Bạn là trợ lý trả lời câu hỏi về số liệu quảng cáo cho một chủ shop Việt Nam.\n"
    "\n"
    "Quy tắc bắt buộc:\n"
    "- Viết tiếng Việt CÓ DẤU đầy đủ. Tuyệt đối không viết kiểu không dấu.\n"
    "- MỌI con số bạn viết ra phải lấy nguyên từ kết quả công cụ. Không tự "
    "tính, không ước lượng, không suy diễn, không làm tròn thành số khác.\n"
    "- SỐ TIỀN phải chép từ trường có chữ 'hien_thi' (ví dụ '20.319.895'). "
    "Các trường số thô chỉ để đối chiếu, KHÔNG viết số thô vào câu trả lời.\n"
    "- Tên chiến dịch phải chép y nguyên từng ký tự. Không thêm khoảng trắng "
    "quanh dấu gạch nối, không viết lại tên theo cách của bạn.\n"
    "- Nếu công cụ báo không có dữ liệu thì nói thẳng là không có. Không bịa.\n"
    "- Dùng đúng khoảng ngày ghi ở phần MỐC THỜI GIAN. Không tự chọn khoảng khác.\n"
    "- Khi nói về số của một phần ngày (day_du_ca_ngay = false) thì phải nói rõ "
    "là số mới tích lũy đến lúc đó, chưa phải cả ngày.\n"
    "- Trả lời ngắn gọn: tối đa 8 câu, viết thành đoạn văn liền mạch.\n"
    "- TUYỆT ĐỐI KHÔNG dùng dấu sao, dấu thăng, gạch đầu dòng hay bảng biểu. "
    "Đây là tin nhắn Telegram, các ký hiệu đó hiện ra rất rối.\n"
    "- Đi thẳng vào câu trả lời. Không chào hỏi, không giới thiệu bản thân.\n"
)
```

- [ ] **Bước 2: tách ruột phần gọi mạng (refactor có kiểm soát)**

Thay toàn bộ thân hàm `goi_gemini` hiện có bằng hai hàm dưới đây. **Chữ ký `goi_gemini(env, prompt, timeout=None, goi_mang_fn=None)` giữ nguyên** để 34 bài kiểm thử của GĐ3 vẫn đạt; chỉ thêm tham số `model=None` ở cuối.

```python
def _goi_gemini_than(env, payload_them, model, timeout, goi_mang_fn):
    """Goi Gemini voi phan payload tuy y. Tra ve (du_lieu_json, loi).

    KHONG BAO GIO nem loi ra ngoai: moi loi deu tra ve qua kenh `loi`.

    Tach rieng khoi goi_gemini() vi phan hoi dap can gui kem `tools` va doc
    nguyen `content` cua model, khong chi doc phan chu.
    """
    env = env or {}
    key = str(env.get("GEMINI_API_KEY", "")).strip()
    if not key:
        return None, "thieu GEMINI_API_KEY trong .env"

    model = str(model or "").strip() or MODEL_MAC_DINH
    url = f"{BASE}/{model}:generateContent?key=" + urllib.parse.quote(key)
    goi = goi_mang_fn or _goi_mang_that

    for lan in range(SO_LAN_THU_LAI + 1):
        try:
            return goi(url, payload_them, timeout or TIMEOUT), None
        except urllib.error.HTTPError as e:
            loi = f"HTTP {e.code}"
            y_nghia = Y_NGHIA_LOI.get(e.code)
            if y_nghia:
                loi += f" - {y_nghia}"
            trang_thai = _trang_thai_loi(e)
            if trang_thai:
                loi += f" [{trang_thai}]"
            if e.code in (503, 429) and lan < SO_LAN_THU_LAI:
                time.sleep(CHO_GIUA_HAI_LAN)
                continue
            return None, loi
        except Exception as e:
            return None, str(e)
    return None, "da thu lai nhieu lan nhung van loi"


def goi_gemini(env, prompt, timeout=None, goi_mang_fn=None, model=None):
    """Goi Gemini mot lan (co thu lai khi qua tai). Tra ve (chu, loi).

    KHONG BAO GIO nem loi ra ngoai: moi loi deu tra ve qua kenh `loi`.
    """
    env = env or {}
    model = str(model or env.get("GEMINI_MODEL", "")).strip() or MODEL_MAC_DINH
    du_lieu, loi = _goi_gemini_than(
        env, {"contents": [{"parts": [{"text": prompt}]}]},
        model, timeout, goi_mang_fn,
    )
    if loi:
        return None, loi
    text = doc_cau_tra_loi(du_lieu)
    if not text:
        return None, "AI tra ve rong hoac sai cau truc"
    return text, None
```

- [ ] **Bước 3: thêm phần gọi công cụ và vòng lặp**

Thêm vào cuối `ai.py`:

```python
def soan_prompt_hoi_dap(cau_hoi, moc_tg=""):
    """Ghep cau hoi + moc thoi gian thanh cau lenh cho AI.

    KHONG nhan tham so env -> ve cau truc no khong the lam lo token.
    """
    return (
        HUONG_DAN_HOI_DAP
        + "\n--- MỐC THỜI GIAN (do hệ thống cung cấp, không tự suy diễn) ---\n"
        + str(moc_tg or "(không có)")
        + "\n\n--- CÂU HỎI CỦA CHỦ SHOP ---\n"
        + str(cau_hoi or "")
    )


def boc_content(content):
    """Boc mot `content` cua Gemini -> (chu, function_call).

    Uu tien CHU: model co the vua viet chu vua xin goi cong cu; khi do lay chu.
    Khong bao gio nem loi.
    """
    chu = ""
    xin_goi = None
    try:
        for p in (content or {}).get("parts") or []:
            if p.get("text") and str(p["text"]).strip():
                chu += str(p["text"]).strip() + "\n"
            elif p.get("functionCall") and xin_goi is None:
                xin_goi = p["functionCall"]
    except (AttributeError, TypeError):
        pass
    return chu.strip(), xin_goi


def _chon_model_hoi_dap(env):
    """Danh sach model se thu, theo thu tu. Model chinh truoc, du phong sau."""
    env = env or {}
    chinh = str(env.get("GEMINI_MODEL_HOI_DAP", "")).strip() or MODEL_HOI_DAP_MAC_DINH
    du_phong = (str(env.get("GEMINI_MODEL_HOI_DAP_DU_PHONG", "")).strip()
                or MODEL_HOI_DAP_DU_PHONG_MAC_DINH)
    ds = [chinh]
    if du_phong and du_phong != chinh:
        ds.append(du_phong)
    return ds


def goi_gemini_cong_cu(env, noi_dung, khai_bao_cong_cu=None, timeout=None,
                       goi_mang_fn=None):
    """Goi Gemini kem khai bao cong cu. Tra ve (content_cua_model, loi).

    Tra ve NGUYEN `content` (khong phai chuoi chu) vi vong lap cong cu phai gui
    lai nguyen phan do cho luot sau. Trong do co `thoughtSignature` ma Gemini 3.x
    yeu cau giu - da kiem chung ngay 29/09/2026.

    Thu lan luot cac model trong _chon_model_hoi_dap() khi gap loi 503/404/429.
    """
    payload = {"contents": noi_dung,
               "generationConfig": {"maxOutputTokens": TOI_DA_TOKEN_TRA_LOI}}
    if khai_bao_cong_cu:
        payload["tools"] = khai_bao_cong_cu

    loi_cuoi = "chua goi duoc AI"
    for model in _chon_model_hoi_dap(env):
        du_lieu, loi = _goi_gemini_than(env, payload, model, timeout or TIMEOUT_HOI_DAP,
                                        goi_mang_fn)
        if loi:
            loi_cuoi = f"{model}: {loi}"
            continue
        try:
            return du_lieu["candidates"][0]["content"], None
        except (KeyError, IndexError, TypeError):
            loi_cuoi = f"{model}: AI tra ve sai cau truc"
            continue
    return None, loi_cuoi


def tra_loi(cau_hoi, bo_cong_cu, env=None, moc_tg="", goi_mang_fn=None):
    """Tra loi mot cau hoi cua Dai. Tra ve (chu, loi). KHONG BAO GIO nem loi.

    Vong lap: hoi AI -> AI xin goi cong cu -> CODE chay cong cu -> tra ket qua
    ve -> hoi lai. Toi da TOI_DA_LUOT_CONG_CU luot cong cu, sau do hoi lan cuoi
    KHONG kem cong cu de BUOC AI tra loi bang chu.

    Vi sao phai buoc: da thu that ngay 29/09/2026, AI nhan ket qua roi goi tiep
    cong cu chu khong tu dung. Khong co gioi han cung thi mot cau hoi co the
    ton hang chuc luot goi AI, trong khi tran mien phi chi 20 luot/ngay.
    """
    try:
        prompt = soan_prompt_hoi_dap(cau_hoi, moc_tg)
    except Exception as e:
        return None, f"khong soan duoc cau lenh cho AI: {e}"

    khai_bao = None
    if bo_cong_cu is not None:
        try:
            khai_bao = bo_cong_cu.khai_bao()
        except Exception as e:
            return None, f"khong khai bao duoc cong cu: {e}"

    noi_dung = [{"role": "user", "parts": [{"text": prompt}]}]

    for luot in range(TOI_DA_LUOT_CONG_CU + 1):
        con_cong_cu = khai_bao if luot < TOI_DA_LUOT_CONG_CU else None
        content, loi = goi_gemini_cong_cu(
            env, noi_dung, khai_bao_cong_cu=con_cong_cu, goi_mang_fn=goi_mang_fn)
        if loi:
            return None, loi
        if content is None:
            return None, "AI tra ve rong"

        chu, xin_goi = boc_content(content)
        if chu:
            return chu, None
        if not xin_goi:
            return None, "AI tra ve rong, khong co ca cong cu"
        if bo_cong_cu is None:
            return None, "AI xin goi cong cu nhung khong co cong cu nao"

        noi_dung.append(content)
        try:
            kq = bo_cong_cu.thuc_thi(xin_goi.get("name"), xin_goi.get("args") or {})
        except Exception as e:
            kq = {"loi": f"cong cu bi loi: {e}"}
        noi_dung.append({"role": "user", "parts": [{
            "functionResponse": {"name": xin_goi.get("name"), "response": kq}}]})

    return None, "AI xin goi cong cu qua nhieu luot ma chua tra loi"
```

- [ ] **Bước 4: thêm bài kiểm thử vào `tests/test_ai.py`**

| Nhóm | Bài kiểm thử |
|---|---|
| `boc_content` | `test_boc_duoc_chu` · `test_boc_duoc_function_call` · `test_content_rong_tra_ve_rong` · `test_uu_tien_chu_khi_co_ca_hai` |
| `soan_prompt_hoi_dap` | `test_prompt_co_cau_hoi` · `test_prompt_co_moc_thoi_gian` · `test_prompt_bat_buoc_viet_co_dau` · `test_prompt_cam_markdown` · `test_prompt_khong_nhan_env` (kiểm chữ ký hàm không có tham số `env`) |
| `_chon_model_hoi_dap` | `test_mac_dinh_dung_model_da_kiem_chung` · `test_doc_duoc_tu_env` · `test_model_du_phong_khac_model_chinh_thi_them_vao` · `test_du_phong_trung_chinh_thi_khong_them` |
| `goi_gemini_cong_cu` | `test_gui_kem_tools_khi_co_khai_bao` · `test_khong_gui_tools_khi_khong_khai_bao` · `test_co_maxOutputTokens` · `test_dung_model_hoi_dap_khong_dung_model_bao_cao` · `test_503_thi_thu_model_du_phong` · `test_ca_hai_model_deu_loi_thi_tra_loi` |
| `tra_loi` | `test_ai_tra_loi_ngay_khong_goi_cong_cu` · `test_ai_xin_cong_cu_roi_tra_loi` (kiểm công cụ được chạy với đúng tham số) · `test_ket_qua_cong_cu_duoc_gui_lai_cho_ai` (kiểm `functionResponse` có trong payload lượt sau) · `test_het_luot_thi_luot_cuoi_khong_kem_tools` · `test_het_luot_van_khong_tra_loi_thi_bao_loi` · `test_cong_cu_loi_khong_lam_chet_vong_lap` · `test_ai_loi_mang_tra_ve_loi` · `test_khong_bao_gio_nem_loi` (bo_cong_cu giả ném lỗi) |
| An toàn | `test_khong_gui_token_cho_ai` (prompt không chứa giá trị `GEMINI_API_KEY`) |

---

## Task 3 — `nguoi_truc.py`: nối lớp AI vào phần nghe Telegram

**Files:**
- Modify: `nguoi_truc.py`
- Test: `tests/test_nguoi_truc.py`

- [ ] **Bước 1: thêm import và thay hằng số**

Thêm `import ai` và `import cong_cu` vào khối import đầu file (cùng chỗ với `import report`).

**Xoá** hằng `TRA_LOI_CHUA_CO_AI` (không còn dùng) và thay bằng:

```python
# Cau tra loi khi lop AI khong tra loi duoc. Phai noi RO LY DO, khong im lang:
# Dai khong biet ky thuat, mot tin nhan im lang se lam Dai tuong bot hong.
TRA_LOI_AI_LOI = (
    "Tôi chưa trả lời được câu hỏi này.\n"
    "\n"
    "Lý do: {ly_do}\n"
    "\n"
    "Đại thử lại sau vài phút. Nếu vẫn không được thì xem file "
    "logs\\baocao.log để biết chi tiết."
)
```

- [ ] **Bước 2: thêm hai hàm mới**

Đặt ngay trước `def tra_loi_tin_nhan(...)`:

```python
def _lay_so_hom_nay(env, ngay):
    """Goi Meta lay so lieu MOT ngay. Tra dict stats hoac None.

    Chi dung cho cau hoi can so HOM NAY, khi lich su chua kip ghi. Moi cau hoi
    toi da mot lan goi, vi goi Meta mat 15-30 giay (do duoc trong log).
    """
    try:
        stats, err = report.compute_stats(env, ngay, ngay)
        if err:
            report.log(f"NGUOI TRUC: khong lay duoc so hom nay tu Meta: {err}")
            return None
        return stats
    except Exception as e:
        report.log(f"NGUOI TRUC: loi khi lay so hom nay tu Meta: {e}")
        return None


def _tra_loi_bang_ai(cau_hoi, env, now):
    """Goi lop AI de tra loi cau hoi ve so lieu. Tra ve (chu, loi)."""
    duong_dan_ls = report.LOG_DIR / "lich-su.json"
    bo = cong_cu.BoCongCu(
        duong_dan=duong_dan_ls,
        lay_so_hom_nay_fn=lambda ngay: _lay_so_hom_nay(env, ngay),
        hom_nay=now.date(),
    )
    moc_tg = cong_cu.moc_thoi_gian(duong_dan_ls, hom_nay=now.date())
    return ai.tra_loi(cau_hoi, bo, env=env, moc_tg=moc_tg)
```

- [ ] **Bước 3: sửa `tra_loi_tin_nhan`**

Thêm tham số `tra_loi_ai_fn=None` vào cuối chữ ký. Thay đoạn cuối hàm:

```python
    if not chuan:
        return "Tôi chưa thấy nội dung trong tin nhắn của Đại."

    # Cau hoi ve so lieu -> lop AI (Giai doan 4).
    #
    # `tra_loi_ai_fn` phai tiem duoc: neu khong thi kiem thu se goi AI that,
    # vua hong phep kiem vua ton luot AI.
    if tra_loi_ai_fn is None:
        tra_loi_ai_fn = lambda c: _tra_loi_bang_ai(c, env, now)

    try:
        chu, loi = tra_loi_ai_fn(cau_hoi)
    except Exception as e:
        chu, loi = None, f"loi khong luong truoc: {e}"

    if chu:
        return chu
    return TRA_LOI_AI_LOI.format(ly_do=loi or "khong ro")
```

Cập nhật docstring của hàm: GĐ2 chỉ trả lời được câu hỏi sức khoẻ, GĐ4 trả lời được cả câu hỏi số liệu.

- [ ] **Bước 4: cho `NguoiTruc` tiêm được hàm AI — BẮT BUỘC**

> **Chỗ này kế hoạch ban đầu đã sai, và chính bước dựng thử bắt được.** `NguoiTruc.xu_ly_tin()`
> gọi `tra_loi_tin_nhan()` mà không truyền `tra_loi_ai_fn`, nên mọi bài kiểm thử đi qua `xu_ly_tin`
> sẽ **gọi AI thật**. Khi chạy `270` bài kiểm thử trong thư mục tạm (không có `GEMINI_API_KEY`),
> lỗi hiện ra thành nội dung tin nhắn sai. Nếu thư mục có chìa khoá thì bộ kiểm thử sẽ **tốn lượt
> AI và phụ thuộc mạng** — đúng thứ kiểm thử không được phép làm.

Trong `NguoiTruc.__init__`, thêm tham số cuối và lưu lại:

```python
    def __init__(self, env, danh_sach_moc, che_do_thu=False,
                 gui_bao_cao_fn=None, gui_tin_fn=None,
                 doc_da_gui_fn=None, dong_ho=None,
                 xa_tin_fn=None, lay_tin_fn=None, tra_loi_ai_fn=None):
        self.env = env or {}
        self.danh_sach_moc = list(danh_sach_moc) or list(MOC_MAC_DINH)
        self.che_do_thu = che_do_thu
        # Ham tra loi bang AI. Phai tiem duoc: neu khong thi kiem thu se goi AI
        # that (ton luot AI va phu thuoc mang).
        self.tra_loi_ai_fn = tra_loi_ai_fn
```

Trong `xu_ly_tin()`, truyền xuống:

```python
            da_gui=self._da_gui_hom_nay(now),
            now=now,
            tra_loi_ai_fn=self.tra_loi_ai_fn,
        )
```

Và trong `tests/test_nguoi_truc.py`, `TrucGia.__init__` nhận thêm `tra_loi_ai_fn=None` rồi truyền
vào `nguoi_truc.NguoiTruc(...)`.

- [ ] **Bước 5: sửa `TestTraLoiTinNhan` trong `tests/test_nguoi_truc.py`**

Bài `test_hoi_cau_khac_thi_noi_ro_chua_co_AI` **sẽ hỏng** vì hành vi đã đổi — nó còn kiểm `assertIn("giai đoạn sau", tl)`. Phải thay bằng các bài dưới. **Lưu ý: còn một bài nữa cũng hỏng mà kế hoạch ban đầu bỏ sót** — `test_cau_hoi_rong_cung_tra_loi_chua_co_AI` nằm ở cuối lớp này, cũng kiểm `"giai đoạn sau"`.

```python
    def _tra_loi(self, cau_hoi, tra_loi_ai_fn=None):
        return nguoi_truc.tra_loi_tin_nhan(
            cau_hoi=cau_hoi,
            env={"REPORT_ACCOUNT_NAME": "Test"},
            danh_sach_moc=[8, 12, 17],
            bat_dau=luc(6),
            lan_gui_cuoi=luc(12, 1),
            da_gui={8, 12},
            now=luc(13),
            tra_loi_ai_fn=tra_loi_ai_fn,
        )

    def test_cau_hoi_so_lieu_thi_goi_ai(self):
        da_goi = []

        def ai_gia(cau_hoi):
            da_goi.append(cau_hoi)
            return "Chi tieu hom qua la 7.034.942 dong.", None

        tl = self._tra_loi("camp nào tệ nhất tuần này?", tra_loi_ai_fn=ai_gia)
        self.assertEqual(da_goi, ["camp nào tệ nhất tuần này?"])
        self.assertIn("7.034.942", tl)

    def test_ai_loi_thi_tra_loi_kem_ly_do(self):
        def ai_gia(cau_hoi):
            return None, "HTTP 429 - het han muc goi AI"

        tl = self._tra_loi("doanh thu hôm nay?", tra_loi_ai_fn=ai_gia)
        self.assertIn("chưa trả lời được", tl)
        self.assertIn("HTTP 429", tl)

    def test_ai_nem_loi_cung_khong_lam_chet(self):
        def ai_gia(cau_hoi):
            raise RuntimeError("no ra")

        tl = self._tra_loi("số hôm nay?", tra_loi_ai_fn=ai_gia)
        self.assertIn("chưa trả lời được", tl)

    def test_tin_rong_thi_khong_goi_ai(self):
        da_goi = []
        tl = self._tra_loi("", tra_loi_ai_fn=lambda c: da_goi.append(c) or ("x", None))
        self.assertEqual(da_goi, [])

    def test_cau_hoi_rong_thi_bao_khong_thay_noi_dung(self):
        """Bài CŨ `test_cau_hoi_rong_cung_tra_loi_chua_co_AI` phải đổi thành bài này."""
        self.assertIn("chưa thấy nội dung", self._tra_loi(""))
```

Trong `TestXuLyTin`, bài `test_tin_tu_dai_hoi_so_lieu_thi_bao_chua_co` phải thay bằng hai bài:

```python
    def test_tin_tu_dai_hoi_so_lieu_thi_goi_ai(self):
        tg = TrucGia(luc(13), tra_loi_ai_fn=lambda c: ("Chi tieu 7.034.942 dong.", None))
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "camp nào tệ nhất tuần này?"},
        })
        self.assertEqual(len(tg.tin_da_gui), 1)
        self.assertIn("7.034.942", tg.tin_da_gui[0])

    def test_tin_tu_dai_hoi_so_lieu_ai_loi_thi_noi_ro_ly_do(self):
        tg = TrucGia(luc(13), tra_loi_ai_fn=lambda c: (None, "HTTP 429 - het han muc"))
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "camp nào tệ nhất tuần này?"},
        })
        self.assertEqual(len(tg.tin_da_gui), 1)
        self.assertIn("HTTP 429", tg.tin_da_gui[0])
```

Thêm lớp kiểm thử mới cho phần nối:

| Bài kiểm thử | Điều phải khẳng định |
|---|---|
| `test_tra_loi_bang_ai_truyen_dung_duong_dan_lich_su` | `BoCongCu` được tạo với `report.LOG_DIR / "lich-su.json"` |
| `test_ket_qua_ai_duoc_gui_nguyen_van` | `xu_ly_tin` gửi đúng chuỗi AI trả về |
| `test_che_do_thu_khong_gui_tin` | `che_do_thu=True` → chỉ ghi nhật ký, không gửi |

---

## Task 4 — Cấu hình và tài liệu

**Files:**
- Modify: `.env`, `.env.example`, `README.md`, `HANDOFF.md`, `HUONG-DAN-LAY-CHIA-KHOA-AI.md`

- [ ] **Bước 1: thêm vào `.env` và `.env.example`**

```
# Model dung cho phan TRA LOI CAU HOI (khac model viet bao cao o tren).
# Tach rieng vi tran mien phi cua Gemini tinh theo TUNG MODEL: 20 luot/ngay/model.
# Dung chung mot model thi moi cau hoi cua Dai se an vao tran cua bao cao.
GEMINI_MODEL_HOI_DAP=gemini-3.8-flash

# Model du phong, dung khi model chinh bi qua tai (503) hoac bi khoa (404).
GEMINI_MODEL_HOI_DAP_DU_PHONG=gemini-3.5-flash
```

- [ ] **Bước 2: `HUONG-DAN-LAY-CHIA-KHOA-AI.md`** — thêm mục nói rõ: có **hai** model, trần tính riêng; nếu hỏi đáp báo `HTTP 404` thì đổi tên model trong `.env` (404 = tên model sai, **không phải** chìa khoá sai); cách dò danh sách model bằng `liet_ke_model.py`.

- [ ] **Bước 3: `README.md`** — thêm mục "Hỏi bot bằng tin nhắn": những câu hỏi bot trả lời được, những câu chưa trả lời được (so sánh tuần trong ~7 ngày đầu), và giới hạn số câu hỏi mỗi ngày.

- [ ] **Bước 4: `HANDOFF.md`** — thêm mục "GIAI ĐOẠN 4" theo đúng khuôn mục "GIAI ĐOẠN 3": thêm gì, những điều bắt buộc nhớ, bảng khác kế hoạch, số bài kiểm thử.

---

## Danh sách kiểm chứng (mục 9.2 của bản thiết kế)

| # | Tình huống | Cách làm | Kết quả mong đợi |
|---|---|---|---|
| 1 | Toàn bộ kiểm thử | `chay-kiem-thu.bat` | **270/270 đạt**, **không gọi mạng** |
| 2 | Nhắn *"còn sống không?"* | Nhắn thật cho bot | Trả lời tình trạng như GĐ2, **không** tốn lượt AI |
| 3 | Nhắn *"chi tiêu ngày 28/09 là bao nhiêu?"* | Nhắn thật | Trả lời **20.319.895** (có dấu chấm), khớp `lich-su.json` |
| 4 | Nhắn *"camp nào tệ nhất tuần này?"* | Nhắn thật | Trả lời có số, **nói rõ khoảng ngày đã dùng** |
| 5 | Nhắn *"tuần này so với tuần trước thế nào?"* | Nhắn thật | Nói thật là **chưa đủ số để so sánh** (lịch sử mới 1 ngày), **không bịa** |
| 6 | Nhắn *"hôm nay chi bao nhiêu?"* | Nhắn thật | Lấy từ Meta trực tiếp, **nói rõ số chưa hết ngày** |
| 7 | Nhắn *"doanh thu hôm qua?"* (câu không có số liệu) | Nhắn thật | Trả lời được, không lạc đề |
| 8 | Nhắn tin từ một `chat_id` lạ | Gửi từ tài khoản khác | Bị bỏ qua, ghi nhật ký (giữ nguyên GĐ2) |
| 9 | Giả lập AI lỗi (xoá `GEMINI_API_KEY`) | Nhắn thật trong thư mục tạm | Nhận tin "chưa trả lời được" + lý do; **Người trực vẫn sống** |
| 10 | Đọc kết quả AI, soi từng con số | Đối chiếu tay với `lich-su.json` | **Không một con số nào bịa** |
| 11 | **Đọc kết quả AI, xem số tiền có dấu chấm** | Đọc tin nhắn | Số tiền dạng `20.319.895`, **không** phải `20319895` |
| 12 | Mốc giờ vẫn chạy đúng sau khi thêm GĐ4 | Chờ mốc 12h | Báo cáo 12h vẫn gửi, phần nhận định vẫn có |

**Năm tình huống quan trọng nhất: 3, 4, 5, 10, 11** — chúng nhắm thẳng vào rủi ro *"AI trả lời sai
mà câu văn vẫn trôi chảy"*, rủi ro lớn nhất của giai đoạn này.

---

## Việc Đại phải làm

**Không phải làm gì thêm về cấu hình.** Chìa khoá AI đã có, Người trực đã chạy. Sau khi thi công xong:

1. Nhắn thử bot một câu hỏi về số liệu — ví dụ *"chi tiêu ngày 28/09 là bao nhiêu?"*.
2. Đối chiếu con số bot trả lời với con số trong báo cáo Telegram buổi sáng. Phải khớp.
3. Nếu muốn tắt phần hỏi đáp: xoá dòng `GEMINI_MODEL_HOI_DAP` trong `.env` (bấm `mo-file-env.bat`), bot quay về trả lời như GĐ2.

Phần code, kiểm thử, gỡ lỗi, viết tài liệu — AI làm.

---

## Rủi ro đã biết

| Rủi ro | Mức | Cách xử lý |
|---|---|---|
| **AI trả lời sai số mà văn vẫn trôi chảy** | **Cao** | Số do code tính, AI chỉ chép. Câu lệnh cấm tự tính. Kiểm chứng #10 soi từng con số |
| **Số tiền mất dấu phân cách** | **Cao** | **Đã xảy ra thật** ở lần gọi AI đầu tiên (`20319895 đồng`). Công cụ trả sẵn chuỗi `*_hien_thi`, câu lệnh bắt chép từ đó. Kiểm chứng #11 |
| Hết trần 20 lượt/ngày | Trung bình | Tách model cho hỏi đáp. Giới hạn 3 lượt công cụ. Hết trần → nhận tin nói rõ lý do, báo cáo **không** bị ảnh hưởng |
| Model bị quá tải (503) hoặc bị khoá (404) | Trung bình | Có model dự phòng, tự chuyển. Đã gặp thật cả 503 và 404 ngày 29/09 |
| AI chọn sai khoảng ngày | Trung bình | `moc_thoi_gian()` do code tính, chèn vào câu lệnh. Đây là **lỗi đã gặp thật** trong phép thử |
| Model chèn khoảng trắng vào tên chiến dịch | Thấp — **chấp nhận** | **Đã gặp thật**, câu lệnh đã ghi rõ mà model vẫn làm (`2026-09-04-dainq` → `2026 - 09 - 04 - dainq`). Không sai số, vẫn nhận ra đúng chiến dịch. **Đừng mất công "sửa" lần nữa** |
| Hỏi đáp làm trễ mốc giờ | Thấp | `canh_moc` chạy **trước** `nghe_telegram` trong `mot_vong()`. Trễ tối đa vài phút, báo cáo vẫn gửi |
| Trả lời quá dài cho Telegram | Thấp | Câu lệnh giới hạn 8 câu, cấm markdown, `maxOutputTokens = 2000` |
| Gọi Meta trong lúc trả lời làm chậm | Thấp | Tối đa **một** lần gọi Meta cho mỗi câu hỏi, có cache trong `BoCongCu` |
| Bộ kiểm thử gọi AI thật | **Đã chặn** | `NguoiTruc` nhận `tra_loi_ai_fn` để tiêm. **Lỗi này đã xảy ra thật** khi dựng thử — xem "Lỗi 1" ở phần đầu kế hoạch |
