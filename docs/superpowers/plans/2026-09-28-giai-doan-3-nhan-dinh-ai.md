# Kế hoạch thi công — Giai đoạn 3: Phần nhận định có AI

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mục `🔵 NHẬN ĐỊNH` trong báo cáo Telegram có **nội dung thật** — 3–5 câu tiếng Việt do AI viết, dựa trên số liệu **đã tính sẵn**. AI lỗi vì bất kỳ lý do gì thì báo cáo **vẫn gửi bình thường**, chỉ thiếu phần nhận định và có một dòng ghi chú.

**Architecture:** Thêm `ai.py` — một mô-đun nhỏ, hai việc: (1) `soan_prompt()` ghép số liệu thành câu lệnh cho AI; (2) `goi_gemini()` gọi API và trả về chữ. `report.py` **không** tự gọi AI: `main()` lấy số kỳ trước từ `lich_su.lay_ky_truoc()`, gọi `ai.viet_nhan_dinh()`, rồi **truyền văn bản** vào `build_report()`. Toàn bộ lời gọi AI bọc trong `try`. Không đụng vào bất kỳ phép tính nào.

**Tech Stack:** Python 3.13 thuần, chỉ thư viện chuẩn (`json`, `urllib`, `unittest`). Nhà cung cấp: **Gemini** qua `generativelanguage.googleapis.com`. Kiểm thử **không gọi mạng** — tiêm hàm gọi mạng giả.

**Spec:** `docs/superpowers/specs/2026-09-28-nguoi-truc-ai-agent-design.md` (mục 1.4, 5.3, 5.4, 6.1, 7.2, 8, 9.2 điều 5, 11, 13)

---

## Kế hoạch này đã được kiểm chứng trước khi giao

Trước khi giao, tôi đã **dựng thử toàn bộ code của kế hoạch trong một thư mục tạm**: sao chép
`report.py`, `lich_su.py`, `dashboard.py`, `nguoi_truc.py` và cả bốn file kiểm thử ra ngoài, áp
đúng **tám sửa đổi** của kế hoạch vào `report.py`, viết `ai.py` và `tests/test_ai.py` theo đúng
văn bản dưới đây, rồi chạy. Kết quả:

| Phép kiểm | Kết quả |
|---|---|
| Tám sửa đổi áp vào `report.py` thật | Khớp **cả tám** vị trí, không chỗ nào lệch |
| Toàn bộ kiểm thử | **144/144 đạt** |
| `report.py --help` khi **chưa có** `.env` | Vẫn chạy, in usage bình thường |
| Gọi `build_report(env, stats, period_text)` **3 tham số như cũ** | Chạy được, **không** có dòng ghi chú AI (tương thích ngược tuyệt đối) |
| Đường AI lỗi: `build_report(..., None, "thieu GEMINI_API_KEY trong .env")` | Mục NHẬN ĐỊNH hiện dòng ghi chú, **và** hai bảng `Camp hiệu quả` / `Camp kém hiệu quả` vẫn còn |
| `build_report` có đúng 5 tham số, hai tham số cuối có giá trị mặc định | Đúng |

**Một lỗi của kế hoạch đã bị phép kiểm này bắt được và đã sửa:** bài
`test_khi_co_ky_truoc_thi_cho_phep_so_sanh` ban đầu kiểm `assertNotIn("KHONG co so ky truoc")` —
nhưng **chính câu đó có sẵn trong phần HUONG_DAN gửi cho AI** ("Neu KHONG co so ky truoc thi chi
mo ta…"), nên phép kiểm **luôn thất bại** dù code đúng. Đã đổi dấu kiểm thành
`CHUA CO SO KY TRUOC` (chữ in hoa, khác hẳn câu trong hướng dẫn) và ghi chú lý do ngay trong
`ai.py` để người sau không vô tình đổi lại. Ghi lại đây để người thi công biết chỗ đó là **cố ý**.

**Số bài kiểm thử đã đếm thật, không phải đoán:** `test_ai` 21 bài · `test_report` 52 bài ·
`test_lich_su` 20 bài · `test_nguoi_truc` 51 bài · **tổng 144**.

Thư mục tạm đã được xoá sau khi kiểm chứng. Việc dựng thử **không** thay đổi gì trong repo thật.

---

## ⚠️ ĐỌC TRƯỚC KHI DUYỆT — ba sự thật về dữ liệu hiện có

Ba điều dưới đây quyết định kế hoạch này trông thế nào. Đại cần biết trước khi duyệt, để
không kỳ vọng sai.

### 1. Chưa có số kỳ trước để so sánh — và sẽ mất khoảng 7 ngày mới có

Đọc thẳng `logs/lich-su.json` hôm nay (28/09):

```
So ngay: 1
  2026-09-28  moc=12  day_du=False  so_camp=19  chi_tieu=7034942.0  luot_mua=15
```

`lich_su.lay_ky_truoc('logs/lich-su.json', '2026-09-28', 7)` → `so_ngay_co_du_lieu = 0`.

**Lý do:** file lịch sử mới bắt đầu ghi từ **12h hôm nay** (Giai đoạn 1 được gộp vào `main`
lúc ~11:45; báo cáo 8h hôm nay chạy lúc 8:00 bằng code cũ nên không ghi gì).

⇒ **Khoảng 7 ngày đầu, phần nhận định chỉ MÔ TẢ số hôm nay, chưa SO SÁNH được.** Đây không
phải lỗi — đây là dữ liệu chưa tích đủ. Kế hoạch này làm đúng theo thực tế đó: AI **không được
bịa** chuyện so sánh khi không có số.

### 2. Báo cáo mốc 12h và 17h là báo cáo MỘT PHẦN ngày

| Mốc | Nội dung | Có so sánh được không |
|---|---|---|
| **8h** | Trọn ngày hôm trước | **Có** — so với 7 ngày trước đó |
| 12h | Hôm nay, 0h–12h | **Không** — so nửa ngày với ngày đầy đủ là sai |
| 17h | Hôm nay, 0h–17h | **Không** — như trên |

Lịch sử **không lưu số theo từng giờ**, nên không thể so "0h–17h hôm nay" với "0h–17h hôm
qua". Vì vậy: **chỉ mốc 8h có so sánh.** Hai mốc kia AI chỉ mô tả và nêu con số, không so.

### 3. `--dry` đang ghi bẩn lịch sử — cần Đại quyết

Hôm nay lúc 14:07, một lần chạy `report.py --dry` đã ghi đè bản ghi `2026-09-28` thành
`moc=12` với số liệu **lúc 14:07** — tức lịch sử ghi **sai mốc** (14h mà ghi là mốc 12h).

Nguyên nhân: `main()` gọi `luu_lich_su()` khi `args.mock is None`, tức **cả khi `--dry`**.
Giai đoạn 1 cố ý giữ hành vi này. Nhưng Giai đoạn 3 làm phần nhận định **phụ thuộc vào chất
lượng lịch sử**, nên chỗ này trở thành đáng sửa.

**Đề nghị (Task 4 trong kế hoạch này): chỉ ghi lịch sử khi chạy THẬT.**
`--dry` và `--mock` không ghi nữa. Rủi ro thấp: bản ghi lịch sử chỉ có giá trị khi nó tương ứng
với một báo cáo thật đã gửi. **Nếu Đại không đồng ý thì bỏ Task 4**, phần còn lại vẫn chạy được.

---

## Khác với bản thiết kế — đọc trước khi duyệt

| # | Bản thiết kế nói | Kế hoạch này làm | Vì sao |
|---|---|---|---|
| 1 | Mục 5.4: "`build_report()` gọi `ai.viet_nhan_dinh()`" | `main()` gọi AI, rồi **truyền văn bản** vào `build_report(env, stats, period_text, nhan_dinh=...)` | Giữ `build_report` **thuần** (không mạng) nên kiểm thử được không cần chìa khoá; và đúng bài học Giai đoạn 1: "tính một lần rồi truyền vào", không để hai chỗ tự gọi |
| 2 | Mục 5.3: `viet_nhan_dinh(stats_hom_nay, stats_ky_truoc)` — hai tham số | Thêm tham số thứ ba `boi_canh` (chuỗi mô tả kỳ báo cáo + có/không có kỳ trước) | Mốc 12h/17h là báo cáo **một phần** ngày. Không nói cho AI biết thì AI sẽ so nửa ngày với ngày đầy đủ và **nói sai** |
| 3 | Mục 6.1: luôn so với "số kỳ trước" | Chỉ so khi có **bản ghi đầy đủ thật**; không có thì chỉ mô tả | Xem mục "ĐỌC TRƯỚC KHI DUYỆT" — hiện có 0 ngày dữ liệu kỳ trước |
| 4 | Mục 5.3: dùng Gemini, không nói tên model | **Không viết cứng tên model.** Đọc khoá `GEMINI_MODEL` trong `.env`, thiếu thì dùng mặc định | Tên model Gemini thay đổi theo thời gian; lỗi 404 vì tên model là lỗi đã gặp thật. Kèm cách **dò danh sách model** bằng chính chìa khoá của Đại |
| 5 | Mục 5.4: "tách phần gửi thành hàm gọi được từ cả hai chỗ" | **Vẫn không làm** — giống quyết định của Giai đoạn 2 | `nguoi_truc.py` gọi `report.py` bằng tiến trình riêng; đã chạy đúng, không cần đụng lại |

---

## Danh sách kiểm chứng của bản thiết kế (mục 9.2) — Giai đoạn 3 làm được gì

| # | Tình huống (thiết kế 9.2) | Giai đoạn 3 | Ở đâu |
|---|---|---|---|
| 5 | Giả lập AI lỗi → báo cáo vẫn gửi, thiếu nhận định, có ghi chú | ✅ | Task 2 + Task 3 |
| 9 | Nhắn một câu hỏi cần số liệu → trả lời đúng số | ⏳ | Giai đoạn 4 (cần `ai.tra_loi` + 4 công cụ) |
| — | 8 tình huống còn lại | ➖ | Đã làm ở Giai đoạn 1–2 |

**Giai đoạn 3 chỉ nhắm đúng một tình huống trong danh sách: số 5.** Đó là tình huống mà bản
thiết kế gọi là "điều kiện bắt buộc": *Đại không bao giờ mất báo cáo vì AI.*

---

## Global Constraints

- **Không thư viện ngoài.** Chỉ thư viện chuẩn. Kiểm thử bằng `unittest`. Không `requirements.txt`.
- **Kiểm thử KHÔNG được gọi mạng.** Mọi lời gọi Gemini trong kiểm thử phải đi qua hàm giả được tiêm vào.
- **Không đụng vào phép tính.** Giữ nguyên tuyệt đối: `fetch_insights`, `apply_filter`,
  `get_action_value`, `fmt_money`, `compute_stats`, `determine_period`, `doc_moc_tu_env`,
  `moc_sang`, `ds_moc_da_gui`, `send_telegram`, `send_telegram_document`, `api_get`, `load_env`.
  Trong `report.py`, Giai đoạn 3 chỉ được sửa **`build_report`** (thêm tham số có giá trị mặc
  định) và **`main()`** (thêm vài dòng).
- **AI không bao giờ được chặn báo cáo.** Mọi lời gọi AI bọc `try`, có `timeout` 60 giây. AI
  chậm/lỗi/hết hạn mức ⇒ bỏ qua phần nhận định, báo cáo vẫn đi.
- **AI không được bịa số.** Số gửi cho AI là **số đã tính sẵn**. Prompt phải ghi rõ: chỉ dùng
  số được cung cấp, không tự suy ra số khác.
- **`soan_prompt()` KHÔNG nhận `env`.** Nhờ vậy về mặt cấu trúc nó **không thể** làm lộ token.
  Chỉ `goi_gemini(env, ...)` mới chạm `env`, và chỉ để lấy chìa khoá + tên model.
- **Chú thích code tiếng Việt KHÔNG dấu. Chuỗi hiện cho người dùng tiếng Việt CÓ dấu.**
- **Không commit `.env`.** `.gitignore` đã chặn. Không sửa `.gitignore`.
- **Python để chạy:** `C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe`
- **Chạy kiểm thử từ thư mục gốc repo:**
  `"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v`
- **Điều kiện tiên quyết của Đại:** có `GEMINI_API_KEY` trong `.env`. Xem mục dưới.

---

## Việc Đại phải làm — và làm được NGAY, không cần chờ code xong

Đại lấy chìa khoá trước, song song với lúc tôi viết code. Bốn bước:

**Bước 1.** Mở trình duyệt, vào **aistudio.google.com/apikey** (đăng nhập bằng tài khoản Google).
**Bước 2.** Bấm **Create API key** → chọn project có sẵn hoặc tạo project mới → **copy chìa khoá**.
**Bước 3.** Mở file `.env` bằng Notepad, tìm dòng `GEMINI_API_KEY=`, dán chìa khoá vào **sau dấu `=`**, lưu lại.
**Bước 4.** Kiểm tra — mở cửa sổ lệnh tại thư mục dự án, dán dòng này:

```powershell
python test_gemini.py
```

Kết quả phải ghi **`GEMINI API KEY HOAT DONG TOT`**.

> ⚠️ **Nếu báo `LOI HTTP 404`** — nghĩa là **tên model** trong `test_gemini.py` không còn đúng,
> không phải chìa khoá sai. Cách dò tên model đúng, dán nguyên dòng này (chìa khoá đọc từ `.env`,
> không in ra màn hình):
>
> ```powershell
> python -c "import json,urllib.request,report; k=report.load_env('.env')['GEMINI_API_KEY']; d=json.loads(urllib.request.urlopen('https://generativelanguage.googleapis.com/v1beta/models?key='+k,timeout=30).read()); [print('  ', m['name'], '|', m.get('supportedGenerationMethods')) for m in d.get('models',[])]"
> ```
>
> Tìm dòng có `generateContent` và có chữ `flash` trong tên → đó là tên model cần dùng. Gửi kết quả cho tôi.

Hướng dẫn đầy đủ hơn (kèm ảnh chụp từng màn hình nếu cần) sẽ được viết thành file
`HUONG-DAN-LAY-CHIA-KHOA-AI.md` ở Task 5.

---

## Cấu trúc file

| File | Trạng thái | Trách nhiệm |
|---|---|---|
| `ai.py` | **Tạo mới** | `soan_prompt()`, `goi_gemini()`, `viet_nhan_dinh()`, `doc_cau_tra_loi()`. **Không** tính số, **không** gửi Telegram |
| `tests/test_ai.py` | **Tạo mới** | Kiểm thử `ai.py`, không gọi mạng |
| `report.py` | **Sửa** | `build_report()` nhận thêm `nhan_dinh`; `main()` lấy kỳ trước, gọi AI, truyền vào |
| `tests/test_report.py` | **Sửa** | Kiểm thử `build_report()` có/không có nhận định |
| `HUONG-DAN-LAY-CHIA-KHOA-AI.md` | **Tạo mới** | Hướng dẫn Đại lấy chìa khoá, từng bước |
| `.env.example` | **Sửa** | Ghi lại hai khoá `GEMINI_API_KEY` và `GEMINI_MODEL` |
| `.env` (trên máy, KHÔNG lên GitHub) | **Sửa** | Đại dán chìa khoá thật |
| `README.md` | **Sửa** | Mục nhận định, xử lý sự cố khi AI lỗi |
| `HANDOFF.md` | **Sửa** | Bản sửa Giai đoạn 3 |
| `lich_su.py`, `nguoi_truc.py`, `dashboard.py`, các `.bat` | **Giữ nguyên** | Không đụng tới |

---

## Task 1: `ai.py` — gọi Gemini và soạn phần nhận định

**Files:**
- Create: `ai.py`
- Test: `tests/test_ai.py`

**Interfaces:**
- Consumes: không (chỉ thư viện chuẩn)
- Produces:
  - `MODEL_MAC_DINH` (str), `TIMEOUT` (int = 60), `SO_NGAY_KY_TRUOC` (int = 7)
  - `soan_prompt(stats, ky_truoc, boi_canh) -> str`
  - `goi_gemini(env, prompt, timeout=None, goi_mang_fn=None) -> (str|None, str|None)`
  - `doc_cau_tra_loi(du_lieu_tra_ve) -> str` — bóc chữ ra khỏi JSON của Gemini; hỏng thì trả `""`
  - `viet_nhan_dinh(stats, ky_truoc=None, boi_canh="", env=None, goi_mang_fn=None) -> (str|None, str|None)`

**Vì sao tách `doc_cau_tra_loi` ra riêng:** cấu trúc JSON của Gemini có thể đổi. Tách ra thì
kiểm thử được cả trường hợp JSON lạ mà không cần mạng.

- [ ] **Step 1: Viết kiểm thử thất bại**

Tạo `tests/test_ai.py`:

```python
"""Kiem thu ai.py - lop AI cua bao cao Meta Ads. KHONG goi mang."""
import unittest

import ai


STATS = {
    "total_campaigns": 19,
    "totals": {
        "spend": 7034942.0,
        "msg": 120,
        "contact": 40,
        "order": 9,
        "purchase": 15,
        "payment": 11,
        "comment": 3,
    },
    "all": [
        {"id": "111", "name": "dainq - camp A", "spend": 3000000.0, "purchase": 9},
        {"id": "222", "name": "dainq - camp B", "spend": 4034942.0, "purchase": 6},
    ],
    "good": [{"id": "111", "name": "dainq - camp A", "spend": 3000000.0, "purchase": 9}],
    "bad": [{"id": "222", "name": "dainq - camp B", "spend": 4034942.0, "purchase": 6}],
}

KY_TRUOC_CO_SO = {
    "tong": {"spend": 6000000.0, "msg": 100, "contact": 30, "order": 8,
             "purchase": 10, "payment": 8, "comment": 2},
    "so_ngay": 7,
}

KY_TRUOC_RONG = {
    "tong": {"spend": 0.0, "msg": 0, "contact": 0, "order": 0,
             "purchase": 0, "payment": 0, "comment": 0},
    "so_ngay": 0,
}


class TestSoanPrompt(unittest.TestCase):
    def test_co_so_tong(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "bao cao ngay 27/09/2026")
        self.assertIn("7.034.942", p)
        self.assertIn("15", p)

    def test_co_ten_camp(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("dainq - camp A", p)

    def test_co_boi_canh(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "bao cao ngay 27/09/2026")
        self.assertIn("bao cao ngay 27/09/2026", p)

    def test_khi_khong_co_ky_truoc_thi_noi_ro_dung_so_sanh(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_RONG, "x")
        self.assertIn("CHUA CO SO KY TRUOC", p)

    def test_khi_ky_truoc_None_cung_noi_ro(self):
        p = ai.soan_prompt(STATS, None, "x")
        self.assertIn("CHUA CO SO KY TRUOC", p)

    def test_khi_co_ky_truoc_thi_cho_phep_so_sanh(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertNotIn("CHUA CO SO KY TRUOC", p)
        self.assertIn("6.000.000", p)

    def test_prompt_cam_bia_so(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("khong duoc tu suy ra", p)

    def test_stats_rong_khong_no(self):
        p = ai.soan_prompt({}, None, "x")
        self.assertIsInstance(p, str)
        self.assertTrue(p)

    def test_khong_nhan_env_nen_khong_the_lo_token(self):
        # soan_prompt KHONG co tham so env -> ve cau truc khong the lo token.
        import inspect
        self.assertNotIn("env", inspect.signature(ai.soan_prompt).parameters)


class TestDocCauTraLoi(unittest.TestCase):
    def _goi(self, text):
        return {"candidates": [{"content": {"parts": [{"text": text}]}}]}

    def test_boc_duoc_chu(self):
        self.assertEqual(ai.doc_cau_tra_loi(self._goi("  Nam camp tot.  ")), "Nam camp tot.")

    def test_json_hong_tra_ve_rong(self):
        self.assertEqual(ai.doc_cau_tra_loi({"candidates": []}), "")

    def test_thieu_truong_tra_ve_rong(self):
        self.assertEqual(ai.doc_cau_tra_loi({}), "")

    def test_khong_phai_dict_tra_ve_rong(self):
        self.assertEqual(ai.doc_cau_tra_loi(None), "")


class TestGoiGemini(unittest.TestCase):
    def test_thieu_chia_khoa_thi_bao_loi_ro(self):
        text, loi = ai.goi_gemini({}, "hoi gi do")
        self.assertIsNone(text)
        self.assertIn("GEMINI_API_KEY", loi)

    def test_goi_thanh_cong(self):
        def gia(url, payload, timeout):
            return {"candidates": [{"content": {"parts": [{"text": "Nhan dinh thu."}]}}]}

        text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertEqual(text, "Nhan dinh thu.")
        self.assertIsNone(loi)

    def test_mang_loi_thi_tra_ve_loi_chu_khong_nem(self):
        def gia(url, payload, timeout):
            raise OSError("mat mang")

        text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertIn("mat mang", loi)

    def test_ai_tra_rong_thi_coi_nhu_loi(self):
        def gia(url, payload, timeout):
            return {"candidates": []}

        text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertTrue(loi)

    def test_dung_model_trong_env(self):
        da_goi = []

        def gia(url, payload, timeout):
            da_goi.append(url)
            return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

        ai.goi_gemini({"GEMINI_API_KEY": "k", "GEMINI_MODEL": "model-rieng"},
                      "x", goi_mang_fn=gia)
        self.assertIn("model-rieng", da_goi[0])


class TestVietNhanDinh(unittest.TestCase):
    def test_thanh_cong(self):
        def gia(url, payload, timeout):
            return {"candidates": [{"content": {"parts": [{"text": "Ba cau nhan dinh."}]}}]}

        text, loi = ai.viet_nhan_dinh(STATS, KY_TRUOC_CO_SO, "x",
                                      env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertEqual(text, "Ba cau nhan dinh.")
        self.assertIsNone(loi)

    def test_loi_thi_tra_ve_loi_chu_khong_nem(self):
        def gia(url, payload, timeout):
            raise OSError("het han muc")

        text, loi = ai.viet_nhan_dinh(STATS, None, "x",
                                      env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertIn("het han muc", loi)

    def test_stats_rong_van_khong_no(self):
        def gia(url, payload, timeout):
            return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

        text, loi = ai.viet_nhan_dinh({}, None, "x",
                                      env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertEqual(text, "ok")
        self.assertIsNone(loi)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . 2>&1 | tail -5
```

Kết quả mong đợi: `ModuleNotFoundError: No module named 'ai'`.

- [ ] **Step 3: Viết `ai.py`**

```python
"""
LOP AI CUA BAO CAO META ADS
============================
Mot viec duy nhat: bien SO LIEU DA TINH SAN thanh 3-5 cau nhan dinh tieng Viet.

Nguyen tac bat buoc:
  - KHONG tu goi Meta. So lieu do report.py tinh roi truyen vao.
  - KHONG bao gio nem loi ra ngoai. AI loi thi bao cao van phai gui duoc.
  - KHONG gui token hay thong tin dang nhap cho AI. Ham soan_prompt() khong
    nhan tham so env, nen ve cau truc no khong the lam lo token.

Nha cung cap: Gemini. Chia khoa doc tu khoa GEMINI_API_KEY trong .env.
"""
import json
import urllib.error
import urllib.parse
import urllib.request

# Ten model mac dinh. Doi duoc bang khoa GEMINI_MODEL trong .env.
# Ten model Gemini thay doi theo thoi gian, nen KHONG viet cung trong code.
MODEL_MAC_DINH = "gemini-2.5-flash"

BASE = "https://generativelanguage.googleapis.com/v1beta/models"

# Thoi gian toi da cho mot lan goi AI (giay). Bao cao khong duoc tre vi AI.
TIMEOUT = 60

# So ngay lay lam ky so sanh (chi dung cho bao cao TRON ngay).
SO_NGAY_KY_TRUOC = 7

# Cau khoa khi chua co so ky truoc. Phai la chuoi CO DAU vi day la cau gui
# cho AI doc, khong phai chuoi hien cho nguoi dung.
#
# LUU Y: chuoi nay phai KHAC voi cau trong HUONG_DAN ben duoi. Neu trung nhau
# thi khong the kiem bang assertNotIn duoc (da bi bat boi buoc dung thu).
CHUA_CO_KY_TRUOC = "CHUA CO SO KY TRUOC"

HUONG_DAN = (
    "Ban la nguoi viet bao cao quang cao cho mot chu shop Viet Nam.\n"
    "Hay viet 3 den 5 cau tieng Viet nhan xet ve so lieu duoi day.\n"
    "\n"
    "Quy tac bat buoc:\n"
    "- CHI dung nhung con so duoc cung cap. khong duoc tu suy ra, khong duoc "
    "uoc luong, khong duoc bia them so nao khac.\n"
    "- Neu thieu so de ket luan thi noi thang la thieu, dung doan.\n"
    "- Neu co so ky truoc thi so sanh va noi ro tang hay giam.\n"
    "- Neu KHONG co so ky truoc thi chi mo ta, TUYET DOI khong so sanh.\n"
    "- Cau ngan, de hieu, tranh tu chuyen mon. Nguoi doc khong biet ky thuat.\n"
    "- Chi tra ve phan nhan xet, khong chao hoi, khong giai thich ban la ai.\n"
)


def _fmt_tien(v):
    """Dinh dang tien kieu Viet Nam: 7034942.0 -> '7.034.942'."""
    try:
        return f"{int(round(float(v))):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def _dong_chi_so(tong):
    """Mot dong tom tat cac chi so, dung chung cho ca hai ky."""
    tong = tong or {}
    return (
        f"chi tieu {_fmt_tien(tong.get('spend', 0))} d; "
        f"tin nhan moi {tong.get('msg', 0)}; "
        f"lien he moi {tong.get('contact', 0)}; "
        f"don hang {tong.get('order', 0)}; "
        f"luot mua {tong.get('purchase', 0)}; "
        f"luot thanh toan {tong.get('payment', 0)}; "
        f"binh luan {tong.get('comment', 0)}"
    )


def soan_prompt(stats, ky_truoc, boi_canh):
    """Ghep so lieu thanh cau lenh cho AI.

    KHONG nhan env -> khong the lam lo token.
    """
    stats = stats or {}
    lines = [HUONG_DAN, "", "--- BOI CANH ---", str(boi_canh or "")]
    lines.append("")
    lines.append("--- SO KY BAO CAO NAY ---")
    lines.append(f"so campaign: {stats.get('total_campaigns', 0)}")
    lines.append(_dong_chi_so(stats.get("totals")))

    camps = stats.get("all") or []
    if camps:
        lines.append("")
        lines.append("Tung campaign (ten | chi tieu | luot mua):")
        for c in camps[:20]:
            lines.append(
                f"- {c.get('name', '?')} | {_fmt_tien(c.get('spend', 0))} d "
                f"| {c.get('purchase', 0)}"
            )

    so_ngay = (ky_truoc or {}).get("so_ngay", 0)
    lines.append("")
    if so_ngay:
        lines.append(f"--- SO KY TRUOC ({so_ngay} ngay) ---")
        lines.append(_dong_chi_so((ky_truoc or {}).get("tong")))
    else:
        lines.append(f"--- {CHUA_CO_KY_TRUOC} ---")
        lines.append("Chi mo ta so o tren. TUYET DOI khong so sanh voi ky nao.")

    return "\n".join(lines)


def doc_cau_tra_loi(du_lieu_tra_ve):
    """Boc phan chu ra khoi JSON Gemini tra ve. Hong gi -> tra ve chuoi rong.

    Tach rieng vi cau truc JSON cua Gemini co the doi, va vi kiem thu phai
    kiem duoc truong hop JSON la ma khong can goi mang.
    """
    try:
        return du_lieu_tra_ve["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError, AttributeError):
        return ""


def _goi_mang_that(url, payload, timeout):
    """Goi Gemini that. Tach rieng de kiem thu thay duoc bang ham gia."""
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def goi_gemini(env, prompt, timeout=None, goi_mang_fn=None):
    """Goi Gemini mot lan. Tra ve (chu, loi).

    KHONG BAO GIO nem loi ra ngoai: moi loi deu tra ve qua kenh `loi`.
    """
    env = env or {}
    key = str(env.get("GEMINI_API_KEY", "")).strip()
    if not key:
        return None, "thieu GEMINI_API_KEY trong .env"
    model = str(env.get("GEMINI_MODEL", "")).strip() or MODEL_MAC_DINH
    url = f"{BASE}/{model}:generateContent?key=" + urllib.parse.quote(key)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    goi = goi_mang_fn or _goi_mang_that

    try:
        du_lieu = goi(url, payload, timeout or TIMEOUT)
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)

    text = doc_cau_tra_loi(du_lieu)
    if not text:
        return None, "AI tra ve rong hoac sai cau truc"
    return text, None


def viet_nhan_dinh(stats, ky_truoc=None, boi_canh="", env=None, goi_mang_fn=None):
    """Viet 3-5 cau nhan dinh. Tra ve (chu, loi). Khong bao gio nem loi."""
    try:
        prompt = soan_prompt(stats, ky_truoc, boi_canh)
    except Exception as e:
        return None, f"khong soan duoc cau lenh cho AI: {e}"
    return goi_gemini(env, prompt, goi_mang_fn=goi_mang_fn)
```

- [ ] **Step 4: Chạy kiểm thử để chắc chắn Task 1 đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . 2>&1 | tail -5
```

Kết quả mong đợi: `OK`, **126 bài** đạt (105 bài hiện có + 21 bài mới của Task 1).

- [ ] **Step 5: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add ai.py tests/test_ai.py
git commit -m "Them ai.py: lop AI viet phan nhan dinh (chua ghep vao bao cao)"
```

---

## Task 2: `report.py` — chèn phần nhận định vào mục NHẬN ĐỊNH

**Files:**
- Modify: `report.py` (`build_report` — thêm hai tham số có giá trị mặc định)
- Modify: `tests/test_report.py`

**Interfaces:**
- Consumes: không
- Produces: `build_report(env, stats, period_text, nhan_dinh=None, loi_ai=None) -> str`
  - `nhan_dinh` là chuỗi AI viết → in ra ngay dưới dòng `🔵 NHẬN ĐỊNH`, **trước** hai bảng xếp hạng.
  - `loi_ai` là chuỗi lý do lỗi → in một dòng ghi chú thay cho phần nhận định.
  - Cả hai `None` → **giữ nguyên hành vi cũ** (tương thích ngược tuyệt đối).

- [ ] **Step 1: Viết kiểm thử thất bại**

Thêm vào **cuối** `tests/test_report.py`, trước khối `if __name__ == "__main__":`:

```python
class TestBuildReportCoNhanDinhAI(unittest.TestCase):
    """Kiem thu phan nhan dinh do AI viet, chen vao bao cao."""

    def setUp(self):
        self.env = {
            "FILTER_INCLUDE": "dainq",
            "FILTER_EXCLUDE": "thuonghieu",
            "REPORT_ACCOUNT_NAME": "Test",
        }
        self.stats = {
            "total_campaigns": 2,
            "totals": {"spend": 1000.0, "msg": 1, "contact": 1, "order": 1,
                       "purchase": 2, "payment": 1, "comment": 0},
            "good": [{"rank": 1, "id": "1", "name": "a", "spend": 500.0,
                      "purchase": 2, "payment": 1, "msg": 1, "cpr": 250.0}],
            "bad": [{"rank": 1, "id": "2", "name": "b", "spend": 500.0,
                     "purchase": 0, "payment": 0, "msg": 0, "cpr": None}],
            "all": [],
            "include_kw": "dainq",
            "exclude_kw": "thuonghieu",
            "account_name": "Test",
        }

    def test_khong_co_nhan_dinh_thi_giu_nguyen_hanh_vi_cu(self):
        text = report.build_report(self.env, self.stats, "27/09/2026")
        self.assertIn("🔵 NHẬN ĐỊNH", text)
        self.assertNotIn("AI", text.split("🔵 NHẬN ĐỊNH")[1][:200])

    def test_co_nhan_dinh_thi_chen_vao(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   nhan_dinh="Hom nay chi tieu tang 20 phan tram.")
        self.assertIn("Hom nay chi tieu tang 20 phan tram.", text)

    def test_nhan_dinh_nam_TRONG_muc_nhan_dinh(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   nhan_dinh="CAU_KIEM_THU")
        phan = text.split("🔵 NHẬN ĐỊNH")[1]
        self.assertIn("CAU_KIEM_THU", phan)

    def test_co_loi_ai_thi_ghi_chu_ro_va_bao_cao_van_day_du(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   loi_ai="HTTP 429")
        self.assertIn("HTTP 429", text)
        self.assertIn("Camp hiệu quả", text)
        self.assertIn("Camp kém hiệu quả", text)

    def test_co_loi_ai_thi_noi_ro_bao_cao_van_day_du(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   loi_ai="het han muc")
        self.assertIn("vẫn đầy đủ", text)

    def test_co_ca_nhan_dinh_lan_loi_thi_uutien_nhan_dinh(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   nhan_dinh="CAU_KIEM_THU", loi_ai="HTTP 429")
        self.assertIn("CAU_KIEM_THU", text)
        self.assertNotIn("HTTP 429", text)
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . 2>&1 | tail -5
```

Kết quả mong đợi: `TypeError: build_report() got an unexpected keyword argument 'nhan_dinh'`.

- [ ] **Step 3: Sửa `build_report`**

Đổi chữ ký hàm (khoảng dòng 520):

```python
def build_report(env, stats, period_text, nhan_dinh=None, loi_ai=None):
```

Rồi tìm đoạn `lines.append("🔵 NHẬN ĐỊNH")` và chèn ngay **sau** nó, **trước** dòng
`lines.append(f"Camp hiệu quả (top {len(good)}):")`:

```python
    if nhan_dinh:
        lines.append(nhan_dinh.strip())
        lines.append("")
    elif loi_ai:
        lines.append(
            "⚠️ Phần nhận định do AI viết tạm không có "
            f"(lý do: {loi_ai})."
        )
        lines.append(
            "Số liệu ở trên vẫn đầy đủ — báo cáo không bị ảnh hưởng."
        )
        lines.append("")
```

- [ ] **Step 4: Chạy kiểm thử để chắc chắn Task 2 đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . 2>&1 | tail -5
```

Kết quả mong đợi: `OK`, **132 bài** đạt (126 + 6 bài mới).

- [ ] **Step 5: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add report.py tests/test_report.py
git commit -m "report.py: build_report nhan them phan nhan dinh do AI viet (co gia tri mac dinh, tuong thich nguoc)"
```

---

## Task 3: `main()` — lấy số kỳ trước, gọi AI, truyền vào báo cáo

**Files:**
- Modify: `report.py` (`main()` — thêm khoảng 15 dòng)

**Interfaces:**
- Consumes: `ai.viet_nhan_dinh()`, `lich_su.lay_ky_truoc()`, `moc_sang()`
- Produces: không (hàm cuối luồng)

**Quy tắc quyết định — đây là phần dễ làm sai nhất:**

| Mốc đang chạy | Kỳ so sánh | Vì sao |
|---|---|---|
| Bằng `moc_sang(danh_sach_moc)` (thường là 8) | **Có** — `lay_ky_truoc(path, until, 7)` | Báo cáo trọn ngày hôm trước |
| Mốc khác (12, 17) | **Không** — truyền `None` | Báo cáo một phần ngày, so với ngày đầy đủ là sai |

- [ ] **Step 1: Viết kiểm thử thất bại**

Thêm vào **cuối** `tests/test_report.py`, trước `if __name__ == "__main__":`:

```python
class TestQuyetDinhKySoSanh(unittest.TestCase):
    """Kiem thu ham quyet dinh co lay so ky truoc hay khong."""

    def test_moc_sang_thi_CO_so_sanh(self):
        self.assertTrue(report.la_bao_cao_tron_ngay(8, [8, 12, 17]))

    def test_moc_12_thi_KHONG_so_sanh(self):
        self.assertFalse(report.la_bao_cao_tron_ngay(12, [8, 12, 17]))

    def test_moc_17_thi_KHONG_so_sanh(self):
        self.assertFalse(report.la_bao_cao_tron_ngay(17, [8, 12, 17]))

    def test_may_khong_co_moc_8_thi_moc_nho_nhat_la_tron_ngay(self):
        self.assertTrue(report.la_bao_cao_tron_ngay(7, [7, 13, 20]))

    def test_danh_sach_rong_thi_khong_so_sanh(self):
        self.assertFalse(report.la_bao_cao_tron_ngay(8, []))


class TestBoiCanh(unittest.TestCase):
    def test_mo_ta_co_ten_tai_khoan_va_ky(self):
        bc = report.tao_boi_canh({"REPORT_ACCOUNT_NAME": "HBR"}, "27/09/2026", True)
        self.assertIn("HBR", bc)
        self.assertIn("27/09/2026", bc)

    def test_moc_tron_ngay_thi_noi_ro(self):
        bc = report.tao_boi_canh({"REPORT_ACCOUNT_NAME": "HBR"}, "27/09/2026", True)
        self.assertIn("TRON ngay", bc)

    def test_moc_mot_phan_thi_noi_ro_va_khong_so_sanh(self):
        bc = report.tao_boi_canh({"REPORT_ACCOUNT_NAME": "HBR"}, "28/09/2026", False)
        self.assertIn("MOT PHAN", bc)
        self.assertIn("khong so sanh", bc)
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . 2>&1 | tail -5
```

Kết quả mong đợi: `AttributeError: module 'report' has no attribute 'la_bao_cao_tron_ngay'`.

- [ ] **Step 3: Thêm hai hàm nhỏ vào `report.py`**

Chèn ngay **sau** hàm `moc_sang()`:

```python
def la_bao_cao_tron_ngay(slot, danh_sach_moc):
    """True neu moc nay bao cao TRON mot ngay (thuong la moc sang).

    Chi bao cao tron ngay moi so sanh duoc voi ky truoc. Bao cao moc 12h,
    17h chi la MOT PHAN cua ngay, so voi ngay day du la sai.
    """
    if not danh_sach_moc:
        return False
    return slot == moc_sang(danh_sach_moc)


def tao_boi_canh(env, period_text, tron_ngay):
    """Cau mo ta ky bao cao, gui kem cho AI de AI khong hieu sai pham vi."""
    ten = (env or {}).get("REPORT_ACCOUNT_NAME", "?")
    if tron_ngay:
        return (
            f"Tai khoan {ten}. Day la bao cao TRON ngay {period_text}. "
            "Co the so sanh voi so ky truoc."
        )
    return (
        f"Tai khoan {ten}. Day la bao cao MOT PHAN cua ngay {period_text} "
        "(so lieu tich luy tu 0h den gio bao cao). "
        "khong so sanh voi ngay day du nao."
    )
```

- [ ] **Step 4: Sửa `main()` để gọi AI**

Thêm `import ai` vào đầu `report.py` (cạnh `import lich_su`).

Trong `main()`, ngay **sau** dòng `luu_lich_su(stats, until, slot)` (khoảng dòng 759), chèn:

```python
    # --- PHAN NHAN DINH DO AI VIET ---
    # Dat trong try: AI loi vi bat ky ly do gi cung KHONG duoc lam mat bao cao.
    # Chi bao cao TRON ngay moi co so ky truoc de so sanh.
    nhan_dinh = None
    loi_ai = None
    tron_ngay = la_bao_cao_tron_ngay(slot, danh_sach_moc)
    try:
        ky_truoc = None
        if tron_ngay:
            ky_truoc = lich_su.lay_ky_truoc(
                LOG_DIR / "lich-su.json", until, ai.SO_NGAY_KY_TRUOC
            )
        nhan_dinh, loi_ai = ai.viet_nhan_dinh(
            stats, ky_truoc, tao_boi_canh(env, period_text, tron_ngay), env=env
        )
        if loi_ai:
            log(f"AI viet nhan dinh that bai: {loi_ai}")
        else:
            log("AI da viet xong phan nhan dinh")
    except Exception as e:
        nhan_dinh = None
        loi_ai = str(e)
        log(f"AI viet nhan dinh that bai (ngoai du kien): {e}")
```

Rồi thay dòng gọi `build_report`:

```python
    report = build_report(env, stats, period_text)
```

bằng:

```python
    report = build_report(env, stats, period_text, nhan_dinh, loi_ai)
```

- [ ] **Step 5: Chạy kiểm thử để chắc chắn nó đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . 2>&1 | tail -5
```

Kết quả mong đợi: `OK`, **140 bài** đạt (132 + 8 bài mới).

- [ ] **Step 6: Kiểm chứng suy giảm êm — CHẠY THẬT, chưa có chìa khoá AI**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --slot 8 --dry
```

Kết quả mong đợi: **báo cáo vẫn ra đầy đủ**, mục `🔵 NHẬN ĐỊNH` có dòng
`⚠️ Phần nhận định do AI viết tạm không có (lý do: thieu GEMINI_API_KEY trong .env)`,
và hai bảng `Camp hiệu quả` / `Camp kém hiệu quả` vẫn còn nguyên. Nhật ký có dòng
`AI viet nhan dinh that bai`.

- [ ] **Step 7: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add report.py tests/test_report.py
git commit -m "report.py: main() lay so ky truoc va goi AI viet nhan dinh, AI loi thi bao cao van gui"
```

---

## Task 4: Chỉ ghi lịch sử khi chạy thật — **cần Đại duyệt riêng**

> ⚠️ **Task này thay đổi hành vi có từ Giai đoạn 1.** Nếu Đại không đồng ý thì **bỏ Task 4**,
> phần còn lại của kế hoạch vẫn chạy được nguyên vẹn.

**Files:**
- Modify: `report.py` (`main()` — sửa điều kiện gọi `luu_lich_su`)
- Modify: `tests/test_report.py`

**Vì sao:** `--dry` và `--mock` hiện vẫn ghi vào `logs/lich-su.json` với mốc do script **tự
đoán**. Hôm nay 14:07 một lần `--dry` đã ghi bản ghi `2026-09-28` thành `moc=12` trong khi
số liệu là lúc 14:07. Giai đoạn 3 làm phần nhận định phụ thuộc chất lượng lịch sử ⇒ ghi bẩn
làm AI nhận định sai.

- [ ] **Step 1: Viết kiểm thử thất bại**

```python
class TestCoNenGhiLichSu(unittest.TestCase):
    def test_chay_that_thi_ghi(self):
        self.assertTrue(report.co_nen_ghi_lich_su(mock=None, dry=False))

    def test_dry_thi_KHONG_ghi(self):
        self.assertFalse(report.co_nen_ghi_lich_su(mock=None, dry=True))

    def test_mock_thi_KHONG_ghi(self):
        self.assertFalse(report.co_nen_ghi_lich_su(mock=12, dry=False))

    def test_mock_va_dry_deu_khong_ghi(self):
        self.assertFalse(report.co_nen_ghi_lich_su(mock=12, dry=True))
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

Kết quả mong đợi: `AttributeError: module 'report' has no attribute 'co_nen_ghi_lich_su'`.

- [ ] **Step 3: Thêm hàm và sửa `main()`**

Chèn ngay **trước** hàm `luu_lich_su()`:

```python
def co_nen_ghi_lich_su(mock, dry):
    """Chi ghi lich su khi day la mot lan chay THAT.

    --mock va --dry khong gui bao cao, nen ban ghi cua chung khong tuong ung
    voi bao cao nao. Te hon: --dry khong truyen moc gio nen report.py tu doan
    moc, dan den lich su ghi SAI MOC (da xay ra that ngay 28/09/2026: mot lan
    chay luc 14h07 ghi thanh moc 12h).
    """
    return mock is None and not dry
```

Rồi trong `main()`, thay:

```python
    if args.mock is None:
        luu_lich_su(stats, until, slot)
```

bằng:

```python
    if co_nen_ghi_lich_su(args.mock, args.dry):
        luu_lich_su(stats, until, slot)
```

- [ ] **Step 4: Chạy kiểm thử + kiểm chứng lịch sử không bị ghi khi `--dry`**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
SO_NGAY_TRUOC=$("C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -c "import lich_su; print(len(lich_su.doc('logs/lich-su.json')))")
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --slot 8 --dry > /dev/null
SO_NGAY_SAU=$("C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -c "import lich_su; print(len(lich_su.doc('logs/lich-su.json')))")
echo "Truoc: $SO_NGAY_TRUOC  Sau: $SO_NGAY_SAU"
```

Kết quả mong đợi: hai số **bằng nhau** (lịch sử không bị ghi thêm).

- [ ] **Step 5: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add report.py tests/test_report.py
git commit -m "report.py: chi ghi lich su khi chay that, khong ghi khi --dry/--mock (tranh ghi sai moc)"
```

---

## Task 5: Cập nhật tài liệu

**Files:**
- Create: `HUONG-DAN-LAY-CHIA-KHOA-AI.md`
- Modify: `README.md`, `HANDOFF.md`, `.env.example`

> **Phương pháp:** đừng dùng số dòng — dùng `grep` tìm **đúng chuỗi** rồi sửa. Sửa xong chạy
> lại chính lệnh `grep` đó; không còn dòng nào khớp là xong.

- [ ] **Step 1: Quét xem tài liệu đang nói gì về phần NHẬN ĐỊNH**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
grep -n "NHẬN ĐỊNH\|nhận định\|GEMINI\|Gemini\|AI" README.md HANDOFF.md QUY-TRINH-HANG-NGAY.md
```

Mỗi dòng rơi vào một trong ba nhóm: **nói về trạng thái hiện tại** (phải sửa), **ghi chép lịch
sử ngày cụ thể** (giữ nguyên), **file không còn dùng** (giữ nguyên).

- [ ] **Step 2: Viết `HUONG-DAN-LAY-CHIA-KHOA-AI.md`**

Nội dung bắt buộc có, viết cho người **không biết lập trình**:

1. Lấy chìa khoá: vào `aistudio.google.com/apikey`, đăng nhập Google, **Create API key**,
   copy. (Kèm ghi chú: bản miễn phí đủ dùng — hệ thống chỉ gọi 3 lần/ngày.)
2. Dán vào `.env`: mở Notepad, tìm `GEMINI_API_KEY=`, dán sau dấu `=`, **Ctrl+S**.
3. Kiểm tra: `python test_gemini.py` → phải hiện `HOAT DONG TOT`.
4. **Nếu báo 404** — tên model sai, không phải chìa khoá sai. Kèm lệnh dò danh sách model
   (chép từ mục "Việc Đại phải làm" của kế hoạch này).
5. **Chìa khoá là mật khẩu.** Không gửi qua Zalo/Telegram/email. `.env` không lên GitHub.
6. Chi phí: ước tính dưới 1 USD/tháng. Nếu hết hạn mức, báo cáo **vẫn gửi**, chỉ thiếu phần nhận định.

- [ ] **Step 3: Sửa `.env.example`**

Đổi mục `4. KHONG DUNG NUA - de trong` (đã lỗi thời) thành mục dùng thật:

```
# ------------------------------------------------------------
#  4. AI VIET PHAN NHAN DINH   [CAN DIEN - xem HUONG-DAN-LAY-CHIA-KHOA-AI.md]
# ------------------------------------------------------------
#  Lay chia khoa mien phi tai: aistudio.google.com/apikey
GEMINI_API_KEY=

#  Ten model Gemini. De trong thi dung mac dinh trong ai.py.
#  Neu bao loi HTTP 404 thi doi ten model o day (xem huong dan cach do).
GEMINI_MODEL=
```

- [ ] **Step 4: Sửa `README.md`**

- Mục "Những chỉ số được báo cáo" hoặc mục "Hệ thống này làm gì": ghi rõ mục **NHẬN ĐỊNH** giờ
  do **AI viết**, dựa trên số đã tính; **AI lỗi thì báo cáo vẫn đầy đủ**, chỉ thiếu phần nhận định.
- Mục "Người trực là gì": thêm một dòng vào bảng — `Viết nhận định | Gọi Gemini 1 lần mỗi báo cáo; lỗi thì bỏ qua`.
- Mục "Xử lý sự cố": thêm hai dòng:

```markdown
| Mục NHẬN ĐỊNH ghi "Phần nhận định do AI viết tạm không có" | Chìa khoá Gemini sai/hết hạn mức/mất mạng. **Báo cáo vẫn đầy đủ số liệu.** Chạy `python test_gemini.py` để kiểm chìa khoá |
| Phần nhận định chỉ mô tả, không so sánh | Bình thường trong ~7 ngày đầu: lịch sử chưa đủ số kỳ trước. Xem mục "Người trực là gì" |
```

- Mục "Cấu trúc file": thêm `ai.py`, `tests/test_ai.py`, `HUONG-DAN-LAY-CHIA-KHOA-AI.md`.

- [ ] **Step 5: Sửa `HANDOFF.md`**

Chèn một mục mới vào **cuối** phần "🔧 GHI CHÚ KỸ THUẬT CHO TRỢ LÝ AI", ngay **trước**
`### ⚠️ BẪY QUAN TRỌNG NHẤT`, ghi rõ:

- Phần NHẬN ĐỊNH nay do AI viết; số liệu vẫn do code tính, AI **không** tự gọi Meta.
- **Suy giảm êm:** AI lỗi ⇒ báo cáo vẫn gửi. Đã kiểm chứng bằng cách chạy khi **chưa có**
  chìa khoá (`Task 3 Step 6`).
- **`soan_prompt()` không nhận `env`** ⇒ về cấu trúc không thể lộ token cho AI.
- **Chỉ mốc 8h có so sánh kỳ trước.** Mốc 12h/17h là báo cáo một phần ngày; lịch sử không lưu
  số theo giờ nên không so được.
- **Giới hạn ~7 ngày đầu:** lịch sử chỉ mới có 1 bản ghi (từ 12h ngày 28/09) ⇒ chưa so sánh
  được. Không phải lỗi.
- **Tên model không viết cứng** — đọc khoá `GEMINI_MODEL` trong `.env`.

- [ ] **Step 6: Kiểm chứng không còn câu nói sai**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
grep -n "NHẬN ĐỊNH\|nhận định\|GEMINI\|Gemini" README.md HANDOFF.md HUONG-DAN-LAY-CHIA-KHOA-AI.md .env.example
```

Đọc từng dòng: dòng nào mô tả **trạng thái hiện tại** phải nói đúng rằng phần nhận định do AI
viết và AI lỗi thì báo cáo vẫn đi.

- [ ] **Step 7: Chạy lại toàn bộ kiểm thử**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . 2>&1 | tail -5
```

Kết quả mong đợi: `OK`, 144 bài đạt (hoặc 140 nếu bỏ Task 4).

- [ ] **Step 8: Commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git add README.md HANDOFF.md .env.example HUONG-DAN-LAY-CHIA-KHOA-AI.md
git commit -m "Cap nhat tai lieu cho Giai doan 3: phan nhan dinh do AI viet"
```

---

## Kiểm chứng cuối cùng

- [ ] **Toàn bộ kiểm thử đạt**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . 2>&1 | tail -3
```

- [ ] **Kiểm thử KHÔNG gọi mạng** — chứng minh bằng cách chạy khi tạm đổi tên biến môi trường
      không có tác dụng; thay vào đó kiểm bằng cách đọc: mọi hàm trong `tests/test_ai.py` gọi
      `goi_gemini`/`viet_nhan_dinh` đều truyền `goi_mang_fn=`, trừ hai bài kiểm "thiếu chìa khoá"
      (không chạm mạng vì thoát sớm).

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
grep -n "goi_mang_fn" tests/test_ai.py | wc -l
```

- [ ] **AI lỗi ⇒ báo cáo vẫn đầy đủ** (chạy thật, chưa có chìa khoá)

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --slot 8 --dry 2>&1 | grep -A3 "NHẬN ĐỊNH"
```

Mong đợi: có dòng ghi chú AI tạm lỗi, và ngay sau đó vẫn có `Camp hiệu quả`.

- [ ] **Có chìa khoá ⇒ phần nhận định có nội dung thật** *(làm sau khi Đại dán chìa khoá)*

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --slot 8 --dry 2>&1 | grep -A8 "NHẬN ĐỊNH"
```

Mong đợi: 3–5 câu tiếng Việt, **không** có chữ "KHONG co so ky truoc" lọt ra ngoài,
**không** bịa ra con số nào không có trong báo cáo.

- [ ] **`report.py --dry` không còn ghi lịch sử** *(nếu làm Task 4)*

- [ ] **`.env` không lọt lên GitHub**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git check-ignore -v .env
git status --short
```

- [ ] **`ai.py` đã được commit**

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
git ls-files | grep -E "^ai.py|test_ai.py|HUONG-DAN-LAY-CHIA-KHOA-AI"
```

---

## Ghi chú chuyển sang Giai đoạn 4

- **`ai.py` đã có sẵn chỗ để gắn tiếp.** Giai đoạn 4 thêm `ai.tra_loi(câu_hỏi)` với vòng lặp
  công cụ (`lay_mot_ngay`, `lay_khoang`, `xep_hang_camp`, `so_sanh`), tối đa 5 lượt gọi công cụ.
- **Chỗ nối đã dựng sẵn từ Giai đoạn 2:** `nguoi_truc.tra_loi_tin_nhan()` hiện trả về
  `TRA_LOI_CHUA_CO_AI` cho mọi câu hỏi không phải câu hỏi sức khoẻ. Giai đoạn 4 thay nhánh đó
  bằng `ai.tra_loi()`.
- **Rủi ro mang sang:** câu trả lời cho Đại sẽ dựa trên `logs/lich-su.json`. Nếu lịch sử còn
  mỏng (xem mục "ĐỌC TRƯỚC KHI DUYỆT" số 1) thì AI **phải nói thật là chưa có số**, không được
  đoán. Prompt của Giai đoạn 4 phải có cùng ràng buộc "không được tự suy ra số".
- **Còn tồn đọng từ Giai đoạn 1, chưa xử lý:** `compute_stats()` không loại trừ `good` khỏi
  `bad`, nên tài khoản ít campaign có thể thấy cùng một camp ở cả hai mục. Đến Giai đoạn 3 việc
  này còn đáng sửa hơn, vì AI đọc cả hai bảng đó để viết nhận định — thấy cùng một camp ở cả
  "hiệu quả" lẫn "kém hiệu quả" thì nhận định sẽ mâu thuẫn. **Cần Đại quyết trước khi làm Giai đoạn 4.**
