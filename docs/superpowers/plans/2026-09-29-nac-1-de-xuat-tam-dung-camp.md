# Kế hoạch thi công — Nấc 1: AI đề xuất tạm dừng camp

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Phần NHẬN ĐỊNH trong báo cáo thoát khỏi tình trạng "kể lại số", và có thêm một mục
**ĐỀ XUẤT** chỉ đích danh chiến dịch nên tạm dừng, kèm số chống lưng. **AI chỉ nói, không làm gì.**

**Architecture:** Năm thay đổi, không đổi kiến trúc. Điểm cốt lõi là một nguyên tắc:

> **AI chọn chiến dịch và viết lý do. CODE điền tên và con số.**
> AI chỉ được trả về `id` + câu lý do. Mọi con số hiển thị ra đều do code lấy từ `stats`.
> Nhờ vậy AI **không thể bịa số** — kể cả khi nó muốn.

1. `de_xuat.py` (MỚI) — rào kiểm đề xuất, **hàm thuần**, không gọi mạng, không đọc file.
2. `ai.py` — sửa `HUONG_DAN` (cho AI thật sự **nhận xét**) + thêm `viet_nhan_dinh_va_de_xuat()`
   trả về JSON, có **bóc JSON chịu lỗi**.
3. `dashboard.py` — thêm khối **Đề xuất** trong file HTML + CSS `.analysis.suggest`.
4. `report.py` — `build_report` nhận thêm `de_xuat`, thêm **đúng một dòng** vào tin nhắn Telegram.
5. `.env` / `.env.example` — hai khoá cấu hình mới, có mặc định trong code nên thiếu vẫn chạy.

**Tech Stack:** Python 3.13 thuần, chỉ thư viện chuẩn (`json`, `unittest`). Kiểm thử **không gọi mạng**.

**Spec:** `docs/superpowers/specs/2026-09-29-dinh-nghia-ai-agent-facebook-design.md`
(mục 1.4 nấc 1, mục 3.3 Rào cản 2, mục 5 việc #2, mục 7)

**Quyết định Đại đã chốt (29/09/2026, 17:2x):**

| Câu hỏi | Đại chọn |
|---|---|
| Loại việc được đề xuất | **Chỉ `tam_dung`** (tạm dừng camp). Không đụng ngân sách |
| Hiển thị ở đâu | **Trong file HTML + đúng một dòng nhắc trong tin nhắn Telegram** |

---

## Kế hoạch này ĐÃ ĐƯỢC KIỂM CHỨNG trước khi thi công (30/09/2026)

Dựng thử trong thư mục tạm **ngoài repo**, chép code thật vào, viết code mới, chạy kiểm thử, rồi
**gọi AI thật 4 lần** với dữ liệu thật. Kết quả:

| Phép kiểm | Kết quả |
|---|---|
| Bộ kiểm thử trong thư mục tạm | **487/487 đạt** (trước khi làm: 435) |
| Bộ kiểm thử trong repo thật sau khi chép code | **487/487 đạt** |
| `boc_json` với 6 dạng đầu vào thật của Gemini | Đúng như thiết kế |
| Gọi AI thật 4 lần (`gemini-3.6-flash`, dữ liệu thật 29/09) | JSON đọc được **4/4** · có dấu **4/4** · có đề xuất hợp lệ **4/4** · **0 số nghi bịa** |
| `report.py --mock 12` (Meta + AI **THẬT**) | Tin nhắn **12 dòng**, mã thoát 0 |
| File `dashboard.html` sinh ra | Có khối Đề xuất, **không lộ JSON**, dấu ngoặc cân |
| `nguoi_truc.py --gui-ngay 12 --thu` | `DA GUI`, mã thoát 0 |

### Hai chỗ KẾ HOẠCH SAI, do bước dựng thử bắt được

**Lỗi 1 — thêm tham số vào `build_report` là NỚI LỎNG một hàng rào đã có (nặng).**
Kế hoạch viết `build_report(env, stats, period_text, de_xuat=None)`. Nhưng repo đã có bài kiểm thử
`test_khong_nhan_them_tham_so` **cố ý** khoá chữ ký ở đúng ba tham số. Bài đó tồn tại để bảo vệ một
bài học thật: lần rút tin nhắn từ ~60 dòng còn 11 dòng đã suýt làm mất hai cảnh báo. Cách chữa đúng
là đặt cảnh báo ở **tầng gọi** (`main()`) để hàm soạn nội dung không thể làm mất chúng.
⇒ **Không sửa test. Sửa kế hoạch.** Thêm hàm thuần `dong_nhac_de_xuat(ds_de_xuat)` vào `report.py`;
`main()` nối dòng đó vào cuối tin nhắn — giống hệt cách các cảnh báo đang được gắn.
`build_report` giữ nguyên ba tham số.

**Lỗi 2 — `money(None)` ném lỗi, một đề xuất dị dạng làm hỏng CẢ file báo cáo (nặng).**
Kế hoạch viết `money(d.get("spend", 0))`. Nhưng `d.get("spend", 0)` trả `None` khi khoá **tồn tại
với giá trị None** — và `money(None)` ném `TypeError`. Hệ quả: một đề xuất thiếu trường là **mất luôn
cả báo cáo HTML**, kể cả phần số liệu. Bài `test_thieu_truong_khong_nem_loi` bắt được.
⇒ Thêm `_so(v)` đọc số an toàn, và bọc khối đề xuất trong `try` — hỏng thì bỏ khối, số liệu vẫn còn.

### Một chỗ khác kế hoạch (nhỏ hơn, cùng họ với lỗi cũ)

`dong_nhac_de_xuat` ban đầu viết `len(ds_de_xuat or [])` trong `try/except TypeError`. Với đầu vào là
chuỗi `"chuoi"` thì `len()` = 5 ⇒ in ra *"Có 5 đề xuất"* — **sai mà không hề ném lỗi**. Đây đúng là
họ lỗi "đọc dữ liệu SAI KIỂU thành hợp lệ" mà skill kiểm chứng kế hoạch đã cảnh báo. Đã sửa: kiểm
`isinstance(ds_de_xuat, (list, tuple))` **trước** khi đếm.

### Một phát hiện về hạn mức AI — không phải lỗi kế hoạch, nhưng phải nhớ

Chiều 29/09/2026, `gemini-3.6-flash` trả **HTTP 429 (hết hạn mức)** — trần **20 lượt/ngày/model**
đã chạm vì các lần chạy thử trong ngày. Model dự phòng `3.5-flash` lúc đó cũng quá tải, và
`3.5-flash` sống với câu lệnh ngắn nhưng **429 với câu lệnh dài 4.240 ký tự** ⇒ nghi có thêm trần
theo lượng token. Việc kiểm chứng câu lệnh phải hoãn sang sáng 30/09.

⇒ **Bài học: chạy thử cũng tiêu lượt AI thật.** Đừng dồn nhiều lần chạy thử vào một ngày gần mốc
báo cáo — nếu chạm trần thì báo cáo thật mất phần nhận định.

---

## Bối cảnh — số đo THẬT, không phỏng đoán

Đo trên `logs/lich-su.json` thật ngày 29/09/2026:

| Ngày | Số camp | Camp 0 đơn | Chi ≥ 200k | Chi ≥ 500k | Chi ≥ 1M |
|---|---|---|---|---|---|
| 28/09 | 19 | 8 | **4** | 3 | 1 |
| 29/09 (17h, chưa đủ ngày) | 16 | 4 | **3** | 1 | 0 |

⇒ **Ngưỡng mặc định 200.000đ cho ra 3–4 đề xuất/ngày** — vừa đủ, không ngập.
Ngưỡng 500k chỉ ra 1–3, hơi chặt. Chọn **200.000đ**, để trong `.env` cho Đại chỉnh.

**Ví dụ thật dùng làm dữ liệu kiểm thử** — camp `120250350059260509`,
tên `2026 - 09 - 11 - dainq - Scale - Online MESS - LTT`:
chi **858.562đ** ngày 28/09, **0 đơn**; ngày 29/09 chi tiếp **39.532đ**, vẫn 0 đơn.
Đây đúng là loại camp mà nấc 1 phải chỉ ra.

**Cấu trúc `logs/lich-su.json` (đã đọc thật):** dict theo ngày → mỗi ngày một bản ghi gồm
`moc`, `thoi_diem`, `day_du`, `so_camp`, `tong`, `camp[]`. Mỗi phần tử `camp` có:
`id`, `name`, `spend`, `purchase`, `payment`, `msg`, `cpr`.

**Cấu trúc `stats` mà `compute_stats()` trả về (đã đọc thật):** `stats["all"]` là danh sách
**toàn bộ** camp đủ điều kiện, mỗi phần tử có `rank`, `id`, `name`, `spend`, `purchase`,
`payment`, `msg`, `cpr`. `stats["good"]` và `stats["bad"]` là hai bảng xếp hạng (tối đa
`TOP_CAMPAIGN_COUNT`, mặc định 5).

---

## Điểm yếu đang có, phải sửa (phát hiện 29/09/2026 lúc 16:05)

`ai.HUONG_DAN` hiện đang bắt AI **kể lại số**, không cho nó **nhận xét**:

```
"- Mọi con số bạn viết ra PHẢI chép nguyên từ BẢNG. Không tự tính..."
"- Cột 'chenh lech' trong bảng đã được tính sẵn. Chép nguyên, đừng tự tính lại."
```

Prompt **có gửi kèm** bảng từng camp nhưng **không yêu cầu dùng bảng đó để phán đoán**.
Hệ quả: mục NHẬN ĐỊNH đọc như một bảng số được viết thành câu, không chỉ ra camp nào đang
đốt tiền vô ích.

⇒ **Thêm mục ĐỀ XUẤT mà không sửa chỗ này thì mục mới cũng rỗng.** Đây là lý do Task 2 tồn tại.

---

## Task 1 — `de_xuat.py` (MỚI): rào kiểm đề xuất

**Files:**
- Create: `de_xuat.py`
- Create: `tests/test_de_xuat.py`

**Vì sao tách file riêng:** đây là **tiền thân của `rao_an_toan.py`** ở nấc 3. Cùng một ý tưởng:
AI đề xuất, code quyết định. Viết tách ra ngay từ bây giờ để nấc 3 dùng lại được, và để nó
kiểm thử được mà không cần AI, không cần mạng.

- [ ] **1.1** Viết `de_xuat.py` với các hằng số và hai hàm:

```python
"""Rao kiem de xuat cua AI (nac 1).

Nguyen tac: AI DE XUAT, CODE QUYET DINH. Giong tinh than "phep so sanh do code lam"
trong ai.py - khi giao cho AI mot viec ma no de lam sai, hay lay lai.

Dac biet: AI chi duoc tra ve `id` va cau ly do. TEN va SO TIEN do CODE dien tu `stats`.
Nho vay AI khong the bia so, ke ca khi no muon.

Ham thuan: khong goi mang, khong doc file -> kiem thu duoc tung truong hop.
"""
import os

# Chi cho phep MOT viec o nac 1. Nac 3 se mo rong danh sach nay.
VIEC_CHO_PHEP = ("tam_dung",)

NGUONG_CHI_MAC_DINH = 200000
TOI_DA_MAC_DINH = 3


def doc_cau_hinh(env):
    """Doc nguong chi va so de xuat toi da tu .env. Thieu thi dung mac dinh.

    Khong bao gio nem loi: .env sai dinh dang thi quay ve mac dinh.
    """
    env = env or {}
    try:
        nguong = int(str(env.get("DE_XUAT_NGUONG_CHI", "")).strip() or NGUONG_CHI_MAC_DINH)
    except (ValueError, TypeError):
        nguong = NGUONG_CHI_MAC_DINH
    try:
        toi_da = int(str(env.get("DE_XUAT_TOI_DA", "")).strip() or TOI_DA_MAC_DINH)
    except (ValueError, TypeError):
        toi_da = TOI_DA_MAC_DINH
    return max(0, nguong), max(0, toi_da)


def kiem(ds_tho, stats, env=None):
    """Loc danh sach de xuat AI tra ve. Tra ve (hop_le, bi_loai).

    hop_le: danh sach dict da lam sach, moi phan tu gom
            {"id", "ten", "spend", "viec", "ly_do"} - ten va spend lay TU CODE.
    bi_loai: danh sach (de_xuat_tho, ly_do_bi_loai) de ghi nhat ky.

    KHONG BAO GIO nem loi.
    """
```

Các điều kiện loại, theo thứ tự kiểm:

| # | Điều kiện | Lý do ghi vào nhật ký |
|---|---|---|
| 1 | `de_xuat` không phải dict | `"khong phai kieu dict"` |
| 2 | `id` rỗng hoặc không phải chuỗi | `"thieu id"` |
| 3 | `viec` không nằm trong `VIEC_CHO_PHEP` | `"viec khong duoc phep: {viec}"` |
| 4 | `id` không khớp camp nào trong `stats["all"]` | `"id khong co trong du lieu: {id}"` |
| 5 | Camp đó có `purchase > 0` | `"camp da co {n} don"` |
| 6 | Camp đó có `spend < nguong` | `"chi {x} < nguong {n}"` |
| 7 | `id` đã xuất hiện rồi | `"trung id"` |
| 8 | Đã đủ `toi_da` đề xuất | `"vuot qua so de xuat toi da ({n})"` |

- [ ] **1.2** Viết `tests/test_de_xuat.py`, tối thiểu **12 bài**, không gọi mạng:

| Bài kiểm | Nội dung |
|---|---|
| `test_id_dung_thi_nhan` | Đề xuất hợp lệ → nằm trong `hop_le`, **tên và spend lấy từ stats chứ không lấy từ AI** |
| `test_AI_bia_so_thi_so_cua_code_thang` | AI trả về `"ten": "BỊA"`, `"spend": 999999999` → kết quả vẫn là tên và số thật của code |
| `test_id_la_thi_loai` | `id` không có trong `stats` → vào `bi_loai`, không vào `hop_le` |
| `test_camp_co_don_thi_loai` | Camp có `purchase=1` → bị loại (đây là rào quan trọng nhất) |
| `test_duoi_nguong_thi_loai` | `spend=50000`, ngưỡng 200000 → bị loại |
| `test_dung_bang_nguong_thi_nhan` | `spend=200000`, ngưỡng 200000 → **được nhận** (ngưỡng là "từ mức này trở lên") |
| `test_viec_khac_tam_dung_thi_loai` | `viec="tang_ngan_sach"` → bị loại |
| `test_trung_id_thi_loai` | Hai đề xuất cùng `id` → chỉ một cái được nhận |
| `test_vuot_toi_da_thi_cat` | 5 đề xuất hợp lệ, tối đa 3 → nhận 3, loại 2 |
| `test_danh_sach_rong` | AI trả `[]` → `( [], [] )`, không lỗi |
| `test_dau_vao_rac_khong_nem_loi` | `None`, `"chuoi"`, `[1,2,3]`, `[{}]` → không ném lỗi |
| `test_cau_hinh_sai_dinh_dang_dung_mac_dinh` | `DE_XUAT_NGUONG_CHI="abc"` → quay về 200000 |

- [ ] **1.3** Chạy `python -m unittest tests.test_de_xuat -v` → phải đạt hết.

---

## Task 2 — `ai.py`: cho AI thật sự nhận xét, và trả về JSON

**Files:**
- Modify: `ai.py`
- Modify: `tests/test_ai.py`

- [ ] **2.1** Sửa `HUONG_DAN`. Bỏ cách diễn đạt chỉ nói "chép số", thêm yêu cầu **phán đoán**.
  Câu lệnh **phải viết CÓ DẤU** (lý do đã ghi trong file: Gemini bắt chước giọng văn của câu lệnh).

Nội dung mới, giữ nguyên tinh thần "số do code tính, AI chỉ chép":

```
Bạn là người phân tích báo cáo quảng cáo cho một chủ shop Việt Nam.

Hãy trả về ĐÚNG MỘT khối JSON, không thêm chữ nào khác ngoài JSON, theo đúng mẫu:
{"nhan_dinh": "...", "de_xuat": [{"id": "...", "viec": "tam_dung", "ly_do": "..."}]}

PHẦN "nhan_dinh" - 3 đến 5 câu tiếng Việt CÓ DẤU:
- Đây là phần NHẬN XÉT, KHÔNG phải kể lại số. Đừng liệt kê lại các con số trong bảng.
- Phải chỉ ra được: chiến dịch nào đang đốt tiền mà không ra đơn, chi phí mỗi đơn đang
  tăng hay giảm, và điều gì đáng lo nhất trong kỳ này.
- Người đọc là chủ shop không biết kỹ thuật. Câu ngắn, tránh từ chuyên môn.

PHẦN "de_xuat" - danh sách việc nên làm. Mỗi việc gồm đúng ba trường:
- "id": chép NGUYÊN mã chiến dịch trong bảng. TUYỆT ĐỐI không tự bịa mã.
- "viec": chỉ được dùng đúng chuỗi "tam_dung". Không dùng giá trị nào khác.
- "ly_do": một câu ngắn, số lấy nguyên từ bảng.

Quy tắc bắt buộc:
- MỌI con số viết ra phải chép nguyên từ BẢNG. Không tự tính, không ước lượng, không làm tròn.
- Chỉ đề xuất "tam_dung" cho chiến dịch có chi tiêu LỚN HƠN 0 và số đơn BẰNG 0.
- Tối đa 3 đề xuất. Không có chiến dịch nào như vậy thì để danh sách rỗng: "de_xuat": [].
- Chỉ trả về JSON. Không chào hỏi, không giải thích, không bọc trong dấu ```.
```

- [ ] **2.2** Thêm `id` vào bảng campaign trong `soan_prompt()`. Hiện dòng đó là:

```python
lines.append(
    f"- {c.get('name', '?')} | {fmt_tien(c.get('spend', 0))} d "
    f"| {c.get('purchase', 0)} don | chi phi moi don: {gia}"
)
```

Đổi thành có mã chiến dịch ở đầu, và **sắp xếp camp 0 đơn lên trước** để AI chắc chắn nhìn thấy
chúng kể cả khi danh sách bị cắt:

```python
# Camp 0 don len TRUOC. Ly do: neu tai khoan co nhieu camp hon muc bi cat, camp
# can chu y nhat phai nam trong phan duoc gui - khong the de no bi cat mat.
sap_xep = sorted(camps, key=lambda c: (
    0 if (c.get("purchase") or 0) == 0 else 1,   # 0 don truoc
    -(c.get("spend") or 0),                      # chi nhieu truoc
))
for c in sap_xep[:TOI_DA_CAMP_GUI_AI]:
    ...
    lines.append(
        f"- ma {c.get('id', '?')} | {c.get('name', '?')} "
        f"| chi {fmt_tien(c.get('spend', 0))} d "
        f"| {c.get('purchase', 0)} don | chi phi moi don: {gia}"
    )
```

Thêm hằng số `TOI_DA_CAMP_GUI_AI = 30` (thay cho số 20 viết cứng). Tài khoản thật đang có
16–19 camp nên không bị cắt; con số 30 là để phòng khi tài khoản lớn lên.

- [ ] **2.3** Thêm `boc_json(text)` — bóc JSON **chịu lỗi**, thử ba cách theo thứ tự:

```python
def boc_json(text):
    """Boc khoi JSON tu cau tra loi cua AI. Hong gi -> tra ve None.

    Ba cach thu, theo thu tu:
      1. json.loads truc tiep
      2. boc khoi ```json ... ``` hoac ``` ... ```
      3. lay tu dau { dau tien den } cuoi cung

    Tra ve dict, hoac None neu hong het. KHONG BAO GIO nem loi.
    """
```

Lý do phải có ba cách: Gemini hay bọc JSON trong ```json, và hay thêm câu dẫn phía trước.
**Đã gặp thật ở dự án này** với `doc_cau_tra_loi()` — cấu trúc JSON của Gemini đổi giữa các lần.

- [ ] **2.4** Thêm `viet_nhan_dinh_va_de_xuat(stats, ky_truoc=None, boi_canh="", env=None, goi_mang_fn=None)`:

Trả về `(nhan_dinh, de_xuat_tho, loi)`.

Hành vi suy giảm êm — **đây là phần quan trọng nhất của Task 2**:

| Tình huống | Hành vi |
|---|---|
| AI trả JSON hợp lệ | `(nhan_dinh, de_xuat, None)` |
| AI trả JSON hợp lệ nhưng `de_xuat` rỗng | `(nhan_dinh, [], None)` — bình thường, không phải lỗi |
| AI trả chữ thường, không phải JSON | `(nguyên đoạn chữ, [], None)` — **vẫn giữ được nhận định** |
| AI trả JSON hỏng, bắt đầu bằng `{` | `(None, [], "AI tra ve JSON hong")` — **không hiển thị JSON dở ra báo cáo** |
| AI lỗi mạng / hết hạn mức | `(None, [], lý do)` — như hành vi hiện nay |

Điểm thứ tư là chỗ dễ làm sai nhất: nếu JSON hỏng mà vẫn đem chuỗi `{"nhan_dinh": "Chi phí...`
hiển thị lên báo cáo thì Đại sẽ đọc một đống dấu ngoặc. Phải chặn.

- [ ] **2.5** Giữ nguyên `viet_nhan_dinh()` cũ, **không xoá** — `report.py` sẽ gọi hàm mới, nhưng
  các bài kiểm thử cũ và đường lui vẫn cần hàm cũ. Hàm mới gọi lại phần gọi mạng của hàm cũ.

- [ ] **2.6** Thêm vào `tests/test_ai.py`, tối thiểu **10 bài**:

| Bài kiểm | Nội dung |
|---|---|
| `test_boc_json_truc_tiep` | `'{"a":1}'` → dict |
| `test_boc_json_trong_khoi_ma` | `'```json\n{"a":1}\n```'` → dict |
| `test_boc_json_co_cau_dan_truoc` | `'Đây là kết quả: {"a":1} cảm ơn'` → dict |
| `test_boc_json_hong_tra_ve_none` | `'{abc'`, `'khong phai json'`, `''`, `None` → `None` |
| `test_json_hop_le_tach_duoc_hai_phan` | Nhận định và đề xuất tách đúng |
| `test_AI_tra_chu_thuong_van_giu_nhan_dinh` | Không phải JSON → dùng nguyên làm nhận định, đề xuất rỗng |
| `test_AI_tra_JSON_hong_thi_KHONG_hien_JSON_do` | Bắt đầu bằng `{` mà hỏng → `nhan_dinh is None`, có lỗi |
| `test_AI_loi_thi_tra_ve_loi` | Hàm gọi mạng giả ném lỗi → `(None, [], lý do)`, **không ném ra ngoài** |
| `test_bang_camp_co_ma_chien_dich` | `soan_prompt` chứa `ma 120250350059260509` |
| `test_camp_0_don_len_truoc` | Trong prompt, dòng camp 0 đơn đứng trước dòng camp có đơn |

- [ ] **2.7** Chạy `python -m unittest tests.test_ai -v` → đạt hết. Các bài cũ **không được vỡ**.

---

## Task 3 — `dashboard.py`: khối Đề xuất trong file HTML

**Files:**
- Modify: `dashboard.py`
- Modify: `tests/test_dashboard.py` (hoặc file kiểm thử dashboard hiện có)

- [ ] **3.1** Thêm CSS vào `_CSS`, cạnh `.analysis.warn` (dòng ~205):

```css
.analysis.suggest { border-left-color: var(--bad); }
.analysis.suggest .analysis-label { color: var(--bad); }
.suggest-item { font-size: 15.5px; margin-bottom: 10px; }
.suggest-item:last-child { margin-bottom: 0; }
.suggest-item .camp { font-weight: 500; }
.suggest-item .meta { font-size: 13px; color: var(--muted); display: block; margin-top: 2px; }
.suggest-hint { font-size: 13px; color: var(--faint); margin-top: 12px; }
```

⚠️ **Phải kiểm tên biến màu thật trong `_CSS`** (`--bad`, `--muted`, `--faint` có tồn tại không).
Nếu tên khác thì dùng tên đúng — **không được bịa tên biến**, CSS sẽ im lặng bỏ qua và khối
này mất màu mà không ai biết.

- [ ] **3.2** ⚠️ **SỬA SO VỚI KẾ HOẠCH BAN ĐẦU** (xem mục "Lỗi 2" ở trên). Thêm hàm đọc số an toàn
  cạnh `money()`, rồi mới dựng khối:

```python
def _so(v):
    """Doc mot so an toan: None hoac chuoi rac -> 0.0."""
    try:
        return float(v or 0)
    except (ValueError, TypeError):
        return 0.0
```

  `build_html(...)` nhận thêm tham số `de_xuat=None`, và chèn khối ngay **sau** khối nhận định,
  **trước** phần `.stats`:

```python
    if de_xuat:
        try:
            items = "".join(
                '<div class="suggest-item">'
                f'<span class="camp">{esc(d.get("ten", ""))}</span>'
                f'<span class="meta">Mã {esc(d.get("id", ""))} · chi '
                f'{money(_so(d.get("spend")))} VND · '
                f'{int(_so(d.get("purchase")))} đơn — đề xuất tạm dừng</span>'
                f'<span class="meta">{esc(d.get("ly_do", ""))}</span>'
                "</div>"
                for d in de_xuat
                if isinstance(d, dict)
            )
            phan_de_xuat = (
                '<div class="analysis suggest">'
                '<div class="analysis-label">Đề xuất</div>'
                + items
                + '<div class="suggest-hint">Đây là đề xuất của AI dựa trên số liệu kỳ này. '
                "Chưa có gì được thực hiện — Đại tự quyết định.</div>"
                "</div>"
            )
        except Exception:
            phan_de_xuat = ""
    else:
        phan_de_xuat = ""
```

  ⚠️ Bọc trong `try` là **bắt buộc**: một đề xuất dị dạng không được làm mất cả file báo cáo.

Lưu ý `d["purchase"]` — trường này phải có trong dict mà `de_xuat.kiem()` trả về. **Bổ sung
`purchase` vào Task 1.1** (đã ghi ở trên: mỗi phần tử có `id`, `ten`, `spend`, `purchase`,
`viec`, `ly_do`).

- [ ] **3.3** `save_dashboard(...)` nhận thêm `de_xuat=None` và truyền xuống `build_html`.

- [ ] **3.4** Thêm bài kiểm thử:
  - `test_html_co_khoi_de_xuat_khi_co` — chuỗi HTML chứa `Đề xuất`, tên camp, mã camp
  - `test_html_khong_co_khoi_de_xuat_khi_rong` — `de_xuat=[]` → không có chữ `analysis suggest`
  - `test_ten_camp_duoc_escape` — tên camp chứa `<script>` → phải thành `&lt;script&gt;`

---

## Task 4 — `report.py`: một dòng nhắc trong tin nhắn Telegram

**Files:**
- Modify: `report.py`
- Modify: `tests/test_report.py`

- [ ] **4.1** ⚠️ **SỬA SO VỚI KẾ HOẠCH BAN ĐẦU** (xem mục "Lỗi 1" ở trên):
  **KHÔNG** thêm tham số `de_xuat` vào `build_report`. Thay vào đó thêm hàm thuần riêng:

```python
def dong_nhac_de_xuat(ds_de_xuat):
    """Dong nhac o CUOI tin nhan khi AI co de xuat. Khong co -> tra ve chuoi rong."""
    if not isinstance(ds_de_xuat, (list, tuple)):
        return ""
    if len(ds_de_xuat) <= 0:
        return ""
    return f"💡 Có {len(ds_de_xuat)} đề xuất — xem file HTML."
```

  rồi `main()` nối vào cuối, **ở tầng gọi** — giống hệt cách hai cảnh báo đang được gắn:

```python
    report = build_report(env, stats, period_text)
    dong_de_xuat = dong_nhac_de_xuat(ds_de_xuat)
    if dong_de_xuat:
        report = report + "\n" + dong_de_xuat
```

⚠️ **Khi `ds_de_xuat` rỗng thì KHÔNG thêm dòng nào.** Mẫu tin nhắn 11 dòng Đại chốt ngày 29/09/2026
phải giữ nguyên trong trường hợp bình thường. Đây là ràng buộc cứng, có bài kiểm thử riêng.
⚠️ `build_report` phải giữ **đúng ba tham số** — bài `test_khong_nhan_them_tham_so` khoá lại.

- [ ] **4.2** Trong `main()`, đổi chỗ gọi AI (dòng ~1083):

```python
nhan_dinh, de_xuat_tho, loi_ai = ai.viet_nhan_dinh_va_de_xuat(
    stats, ky_truoc, tao_boi_canh(env, period_text, tron_ngay), env=env
)
```

rồi gọi rào kiểm ngay sau đó:

```python
# --- RAO KIEM DE XUAT: AI de xuat, CODE quyet dinh ---
de_xuat, de_xuat_bi_loai = [], []
if de_xuat_tho:
    try:
        de_xuat, de_xuat_bi_loai = de_xuat_mod.kiem(de_xuat_tho, stats, env)
    except Exception as e:
        log(f"Rao kiem de xuat loi (bo qua de xuat): {e}")
for d, ly_do in de_xuat_bi_loai:
    log(f"DE XUAT BI LOAI: {ly_do}")
if de_xuat:
    log(f"Co {len(de_xuat)} de xuat hop le")
```

Đặt trong `try` giống phần nhận định: **rào kiểm lỗi cũng không được làm mất báo cáo.**

- [ ] **4.3** Truyền `ds_de_xuat` xuống `dashboard.save_dashboard(..., de_xuat=ds_de_xuat)`.
  **Không** truyền vào `build_report`.

- [ ] **4.4** Thêm bài kiểm thử (lớp `TestDongNhacDeXuat`):
  - `test_co_de_xuat_thi_them_dung_1_dong` — có đề xuất → đúng một dòng, chứa số lượng
  - `test_khong_co_de_xuat_thi_tra_ve_rong` — `[]` và `None` đều cho chuỗi rỗng
  - `test_dau_vao_rac_khong_nem_loi` — chuỗi, số, dict đều cho chuỗi rỗng (KHÔNG được đếm `len` của chúng)
  - `test_build_report_giu_nguyen_11_dong_khi_khong_co_de_xuat` — **đúng 11 dòng, không hơn không kém**
  - `test_ghep_vao_tin_nhan_cho_ra_12_dong` — 11 + 1 = 12, và dòng nhắc nằm ở **cuối**

---

## Task 5 — Cấu hình và tài liệu

**Files:**
- Modify: `.env.example`
- Modify: `.env` (**sao lưu trước thành `.env.bak-truoc-nac1`**)
- Modify: `chay-kiem-thu.bat` (cập nhật số bài — **phải giữ kiểu xuống dòng CRLF**)

- [ ] **5.1** Thêm vào `.env.example`, kèm chú thích giải thích bằng lời thường:

```
# --- MUC DE XUAT (nac 1) ---
# Chi de xuat tam dung nhung chien dich da chi tu muc nay tro len ma CHUA RA DON NAO.
# De 200000 = 200 nghin dong. Dat 0 neu muon thay het moi chien dich 0 don.
DE_XUAT_NGUONG_CHI=200000

# So de xuat toi da hien ra moi bao cao. De 3.
DE_XUAT_TOI_DA=3
```

- [ ] **5.2** Thêm hai khoá đó vào `.env` thật (sao lưu trước). Code **có mặc định** nên thiếu
  vẫn chạy — nhưng để sẵn thì Đại chỉnh được mà không cần nhờ ai.

- [ ] **5.3** Cập nhật số bài trong `chay-kiem-thu.bat` (hiện ghi 435).

- [ ] **5.4** Cập nhật `README.md`: mục "Ba điều cần biết" hoặc mục báo cáo — nói rõ báo cáo nay
  có thêm mục **Đề xuất**, và **AI chỉ đề xuất, chưa thực hiện gì**.

---

## Kiểm chứng — bắt buộc chạy hết trước khi báo Đại

### Bước A: dựng thử trong thư mục tạm (TRƯỚC khi sửa code thật)

Theo quy trình đã chốt với Đại. Chép repo sang thư mục tạm, áp toàn bộ thay đổi, rồi chạy:

| # | Phép kiểm | Kết quả mong đợi |
|---|---|---|
| 1 | Toàn bộ bộ kiểm thử | Đạt hết, **không bài cũ nào vỡ** |
| 2 | `boc_json` với 6 dạng đầu vào thật của Gemini | Đúng như bảng ở Task 2.4 |
| 3 | `de_xuat.kiem` với **dữ liệu thật** của camp `120250350059260509` | Nhận, và tên/số là của code |
| 4 | `de_xuat.kiem` khi AI bịa `id` | Loại, ghi rõ lý do |
| 5 | `build_report` với đề xuất rỗng | **Đúng 11 dòng** |
| 6 | `build_html` có đề xuất | Có khối Đề xuất, tên camp đã escape |

### Bước B: chạy thật, có gọi AI

| # | Phép kiểm | Kết quả mong đợi |
|---|---|---|
| 7 | `python report.py --mock 17` (AI + Meta **THẬT**) | Báo cáo ra đủ, có mục Đề xuất hoặc rỗng — cả hai đều chấp nhận |
| 8 | Đọc file `dashboard.html` sinh ra | Khối Đề xuất hiển thị đúng, không có dấu ngoặc JSON lộ ra |
| 9 | Đếm số lượt AI đã dùng | **Vẫn 1 lượt** như trước, không tăng |
| 10 | So sánh phần NHẬN ĐỊNH trước/sau khi sửa | Phải **nhận xét** nhiều hơn, **kể lại số** ít hơn |

> ⚠️ Phép kiểm 10 là phép kiểm **quan trọng nhất và dễ bị bỏ qua nhất**. Sửa prompt có thể làm
> phần nhận định **tệ đi** thay vì tốt lên. Phải in ra cả hai bản và đọc bằng mắt.

### Bước C: kiểm chứng thật trên máy, sau khi thi công

- [ ] `python -m unittest discover -s tests -t .` trong repo thật → đạt hết
- [ ] `chay-kiem-thu.bat` → chạy được, đúng số bài
- [ ] Người trực vẫn chạy bình thường (`bat-chay-bu.bat` hoặc chờ mốc giờ)

---

## Rủi ro và cách xử lý

| Rủi ro | Mức | Cách xử lý |
|---|---|---|
| AI trả JSON hỏng → mất cả phần nhận định | **Cao** | Suy giảm êm 5 nhánh ở Task 2.4; nếu hỏng JSON thì báo rõ lý do thay vì hiện JSON dở |
| Sửa prompt làm nhận định **tệ đi** | **Cao** | Phép kiểm 10 — in cả hai bản ra đọc bằng mắt |
| AI bịa mã chiến dịch | Trung bình | Rào kiểm Task 1 loại; **số và tên do code điền** nên không thể bịa số |
| Prompt dài hơn → tốn token hơn | Thấp | Vẫn **1 lượt gọi**. Tài khoản 16–19 camp, prompt ~2500 ký tự |
| Tin nhắn Telegram bị phá mẫu 11 dòng | Trung bình | Ràng buộc cứng ở Task 4.1 + 2 bài kiểm thử |
| Khối Đề xuất dùng sai tên biến màu CSS | Thấp | Task 3.1 yêu cầu đọc tên biến thật trước khi viết |
| Đề xuất tắt oan camp mới tạo (chưa đủ thời gian ra đơn) | Trung bình | Nấc 1 **không thực hiện gì**, chỉ nói. Nhưng câu lệnh cho AI nên nhắc: nếu tên camp cho thấy nó mới tạo trong 1–2 ngày thì **không** đề xuất tắt |

---

## Điều KHÔNG làm trong kế hoạch này

| Không làm | Vì sao |
|---|---|
| Để AI đề xuất đổi ngân sách | Đại đã chốt chỉ `tam_dung`. Và chưa biết lãi mỗi đơn |
| Để AI tự gửi lệnh lên Meta | Đó là nấc 3. Nấc 1 **chỉ nói** |
| Đổi mẫu tin nhắn Telegram | Đại vừa chốt mẫu 11 dòng hôm nay. Chỉ thêm 1 dòng khi có đề xuất |
| Thêm nút "tắt camp" vào file HTML | Không có đường nào từ file HTML tới Meta. Nếu sau này muốn, đó là nấc 2 — việc riêng |
| Dùng `responseMimeType: application/json` của Gemini | **Chưa kiểm chứng** với model đang dùng, và tốn lượt AI để thử. Cách bóc JSON chịu lỗi là đủ và không phụ thuộc tính năng |
| So sánh với kỳ trước để phát hiện camp tệ nhiều ngày | Lịch sử mới có 2 ngày. Đợi đủ 7 ngày — đã ghi ở Rào cản 3 |

---

## Việc Đại phải làm

**Không có việc nào bắt buộc.** Nấc 1 không cần token mới, không cần biết lãi mỗi đơn.

Chỉ khi muốn đổi ngưỡng hoặc số đề xuất: mở `.env` bằng `mo-file-env.bat` và sửa hai dòng
`DE_XUAT_NGUONG_CHI`, `DE_XUAT_TOI_DA`.

Phần code, kiểm thử, tài liệu — AI làm.
