# Kế hoạch thi công — Giai đoạn 1: Lịch sử số liệu và mốc giờ

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Chữa hai lỗi đang hoạt động của hệ thống báo cáo Meta Ads (gửi trùng báo cáo, mốc 22h chưa từng chạy) và bắt đầu lưu lịch sử số liệu để các giai đoạn sau so sánh được.

**Architecture:** Ba thay đổi nhỏ, độc lập với nhau. (1) Thêm một module lưu lịch sử số liệu ra `logs/lich-su.json`. (2) Thêm tham số `--slot` cho `report.py` để mỗi lịch Windows nói rõ nó là mốc mấy giờ, thay vì để script tự đoán mốc gần nhất — đây chính là nguyên nhân gốc của cả hai lỗi. (3) Sửa `cai-dat-lich.bat` để truyền mốc giờ vào từng lịch, và bỏ mốc 22h trên máy công ty. Không có AI trong giai đoạn này.

**Tech Stack:** Python 3.13 thuần, chỉ dùng thư viện chuẩn (`json`, `unittest`, `argparse`, `pathlib`). Repo hiện không có thư viện ngoài nào — giữ nguyên như vậy. Kiểm thử bằng `unittest` của thư viện chuẩn, không cài `pytest`. Windows Task Scheduler cho phần lịch chạy.

**Spec:** `docs/superpowers/specs/2026-09-28-nguoi-truc-ai-agent-design.md`

## Global Constraints

- **Không thư viện ngoài.** Toàn bộ repo dùng `urllib`, `json`, `argparse` có sẵn. Kiểm thử dùng `unittest`. Không thêm `requirements.txt`, không `pip install`.
- **Tên file Python dùng gạch dưới.** `lich_su.py`, không phải `lich-su.py`. Đã kiểm chứng: `import lich-su` báo `SyntaxError`.
- **Không đụng vào phép tính.** Các hàm `fetch_insights`, `apply_filter`, `get_action_value`, `fmt_money`, `determine_period` giữ nguyên tuyệt đối. Ngoại lệ duy nhất được phép: thêm khoá `"all"` vào kết quả `compute_stats()` (thuần thêm, không đổi giá trị nào đang có).
- **Thao tác phụ không được làm hỏng việc chính.** Mọi lời gọi lưu lịch sử phải bọc trong `try`. Nguyên tắc: Đại không bao giờ mất báo cáo vì một tính năng phụ lỗi.
- **Chú thích trong code bằng tiếng Việt KHÔNG dấu** (theo đúng lệ của repo, ví dụ `# Ghi nhat ky moi lan chay`). **Chuỗi hiện cho người dùng bằng tiếng Việt CÓ dấu** (ví dụ `"Đã gửi báo cáo"`).
- **Không commit `.env`.** Đã có `.gitignore` chặn. Không sửa `.gitignore`.
- **Python để chạy:** `C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe`
- **Chạy kiểm thử từ thư mục gốc repo:**
  `"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v`
- **Lịch Windows chạy ở chế độ `Interactive`** — máy phải đang bật **và đang đăng nhập**. Đây là giới hạn có sẵn, không phải điều giai đoạn này sửa.
- **`schtasks.exe` bị chặn trong môi trường agent.** Muốn kiểm chứng lịch, dùng `Get-ScheduledTask` (xem Task 4).

---

## Cấu trúc file

| File | Trạng thái | Trách nhiệm |
|---|---|---|
| `lich_su.py` | **Tạo mới** | Đọc/ghi lịch sử số liệu ra `logs/lich-su.json`. Không biết gì về Meta hay Telegram. |
| `tests/test_lich_su.py` | **Tạo mới** | Kiểm thử `lich_su.py` |
| `tests/test_report.py` | **Tạo mới** | Kiểm thử `chon_moc()` và `luu_lich_su()` |
| `report.py` | **Sửa** | Thêm `chon_moc()`, `luu_lich_su()`, tham số `--slot`; thêm khoá `"all"` vào `compute_stats()` |
| `cai-dat-lich.bat` | **Sửa** | Truyền `--slot` vào từng lịch; bỏ mốc 22h |
| `README.md` | **Sửa** | Ghi lại `--slot`, file lịch sử, mốc giờ mới |

**Phải tạo `tests/__init__.py` (file rỗng).** Ban đầu kế hoạch này ghi "không cần file đó" —
**đó là sai, đã kiểm chứng ngày 28/09/2026**: tạm xoá file rồi chạy
`python -m unittest discover -s tests -t .` sẽ chết với
`ImportError: Start directory is not importable: '...\tests'`.
Lý do: khi `-t .` khác `-s tests`, unittest phải import `tests` như một gói, mà gói thì cần
`__init__.py`. File này rỗng, không chứa gì.

---

## Task 1: Module lưu lịch sử số liệu

**Files:**
- Create: `lich_su.py`
- Create: `tests/__init__.py` (rỗng — bắt buộc để lệnh kiểm thử chạy được)
- Test: `tests/test_lich_su.py`

**Interfaces:**
- Consumes: không (module độc lập)
- Produces:
  - `doc(path) -> dict` — toàn bộ lịch sử, `{}` nếu chưa có hoặc file hỏng
  - `ghi(path, ngay, moc, stats) -> bool` — `True` nếu có ghi, `False` nếu bỏ qua
  - `lay_mot_ngay(path, ngay) -> dict | None`
  - `lay_khoang(path, tu, den) -> {"tong": dict, "so_ngay": int}`
  - `lay_ky_truoc(path, ngay, so_ngay) -> {"tong": dict, "so_ngay": int}`
  - Hằng số `SO_NGAY_GIU = 180`, `MOC_DAY_DU = (8, 22)`
  - Khoá trong một bản ghi: `moc`, `thoi_diem`, `day_du`, `so_camp`, `tong`, `camp`
  - `tong` có 7 khoá: `spend`, `msg`, `contact`, `order`, `purchase`, `payment`, `comment`

- [ ] **Step 1: Viết kiểm thử thất bại**

Tạo `tests/test_lich_su.py`:

```python
"""Kiem thu module lich_su - kho luu lich su so lieu bao cao."""
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import lich_su


def stats_mau(spend=1000.0, purchase=10, ten_camp="Camp A"):
    """Tao mot dict stats gia, giong cau truc compute_stats() tra ve."""
    return {
        "total_campaigns": 1,
        "totals": {
            "spend": spend, "msg": 5, "contact": 4, "order": 3,
            "purchase": purchase, "payment": 2, "comment": 1,
        },
        "all": [
            {
                "id": "1", "name": ten_camp, "spend": spend,
                "purchase": purchase, "payment": 2, "msg": 5,
                "cpr": (spend / purchase) if purchase else None,
            }
        ],
    }


class TestDocVaGhi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "lich-su.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_file_chua_co_thi_doc_tra_ve_rong(self):
        self.assertEqual(lich_su.doc(self.path), {})

    def test_ghi_roi_doc_lai_duoc(self):
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau())
        ban_ghi = lich_su.lay_mot_ngay(self.path, "2026-09-27")
        self.assertIsNotNone(ban_ghi)
        self.assertEqual(ban_ghi["moc"], 8)
        self.assertTrue(ban_ghi["day_du"])
        self.assertEqual(ban_ghi["tong"]["spend"], 1000.0)
        self.assertEqual(ban_ghi["so_camp"], 1)
        self.assertEqual(len(ban_ghi["camp"]), 1)
        self.assertEqual(ban_ghi["camp"][0]["name"], "Camp A")

    def test_moc_12h_khong_phai_ban_day_du(self):
        lich_su.ghi(self.path, "2026-09-28", 12, stats_mau())
        self.assertFalse(lich_su.lay_mot_ngay(self.path, "2026-09-28")["day_du"])

    def test_moc_22h_la_ban_day_du(self):
        lich_su.ghi(self.path, "2026-09-28", 22, stats_mau())
        self.assertTrue(lich_su.lay_mot_ngay(self.path, "2026-09-28")["day_du"])

    def test_ban_day_du_ghi_de_ban_so_khong_day_du(self):
        lich_su.ghi(self.path, "2026-09-28", 17, stats_mau(spend=500.0))
        lich_su.ghi(self.path, "2026-09-28", 8, stats_mau(spend=900.0))
        self.assertEqual(
            lich_su.lay_mot_ngay(self.path, "2026-09-28")["tong"]["spend"], 900.0
        )

    def test_ban_so_khong_day_du_KHONG_ghi_de_ban_day_du(self):
        lich_su.ghi(self.path, "2026-09-28", 8, stats_mau(spend=900.0))
        ket_qua = lich_su.ghi(self.path, "2026-09-28", 17, stats_mau(spend=500.0))
        self.assertFalse(ket_qua)
        self.assertEqual(
            lich_su.lay_mot_ngay(self.path, "2026-09-28")["tong"]["spend"], 900.0
        )

    def test_nhan_doi_tuong_date_chu_khong_chi_chuoi(self):
        lich_su.ghi(self.path, date(2026, 9, 27), 8, stats_mau())
        self.assertIsNotNone(lich_su.lay_mot_ngay(self.path, "2026-09-27"))

    def test_lay_mot_ngay_khong_co_tra_ve_None(self):
        self.assertIsNone(lich_su.lay_mot_ngay(self.path, "2020-01-01"))

    def test_file_hong_thi_doc_tra_ve_rong_khong_no(self):
        self.path.write_text("{ day khong phai json", encoding="utf-8")
        self.assertEqual(lich_su.doc(self.path), {})

    def test_ghi_tu_tao_thu_muc_neu_chua_co(self):
        sau = Path(self.tmp.name) / "logs" / "lich-su.json"
        lich_su.ghi(sau, "2026-09-27", 8, stats_mau())
        self.assertTrue(sau.exists())

    def test_don_dep_ban_ghi_cu_hon_180_ngay(self):
        hom_nay = date.today()
        cu = (hom_nay - timedelta(days=200)).strftime("%Y-%m-%d")
        moi = hom_nay.strftime("%Y-%m-%d")
        lich_su.ghi(self.path, cu, 8, stats_mau())
        lich_su.ghi(self.path, moi, 8, stats_mau())
        self.assertIsNone(lich_su.lay_mot_ngay(self.path, cu))


class TestLayKhoang(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "lich-su.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_cong_dung_cac_ngay_trong_khoang(self):
        lich_su.ghi(self.path, "2026-09-26", 8, stats_mau(spend=100.0, purchase=1))
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=200.0, purchase=2))
        lich_su.ghi(self.path, "2026-09-28", 8, stats_mau(spend=400.0, purchase=4))
        kq = lich_su.lay_khoang(self.path, "2026-09-26", "2026-09-27")
        self.assertEqual(kq["tong"]["spend"], 300.0)
        self.assertEqual(kq["tong"]["purchase"], 3)
        self.assertEqual(kq["so_ngay"], 2)

    def test_bao_gom_ca_hai_dau_mut(self):
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=200.0))
        kq = lich_su.lay_khoang(self.path, "2026-09-27", "2026-09-27")
        self.assertEqual(kq["tong"]["spend"], 200.0)
        self.assertEqual(kq["so_ngay"], 1)

    def test_bo_qua_ngay_chua_co_du_lieu(self):
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=200.0))
        kq = lich_su.lay_khoang(self.path, "2026-09-25", "2026-09-27")
        self.assertEqual(kq["tong"]["spend"], 200.0)
        self.assertEqual(kq["so_ngay"], 1)

    def test_khoang_rong_tra_ve_tong_0(self):
        kq = lich_su.lay_khoang(self.path, "2020-01-01", "2020-12-31")
        self.assertEqual(kq["so_ngay"], 0)
        self.assertEqual(kq["tong"]["spend"], 0.0)

    def test_lay_ky_truoc_lay_dung_so_ngay_ngay_truoc(self):
        lich_su.ghi(self.path, "2026-09-25", 8, stats_mau(spend=100.0))
        lich_su.ghi(self.path, "2026-09-26", 8, stats_mau(spend=200.0))
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=400.0))
        kq = lich_su.lay_ky_truoc(self.path, "2026-09-27", 2)
        self.assertEqual(kq["tong"]["spend"], 300.0)
        self.assertEqual(kq["so_ngay"], 2)

    def test_lay_ky_truoc_khong_bao_gom_chinh_ngay_do(self):
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=400.0))
        kq = lich_su.lay_ky_truoc(self.path, "2026-09-27", 1)
        self.assertEqual(kq["so_ngay"], 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

Chạy từ thư mục gốc repo:

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `ModuleNotFoundError: No module named 'lich_su'`

- [ ] **Step 3: Viết phần code tối thiểu**

Tạo `lich_su.py`:

```python
"""
LICH SU SO LIEU BAO CAO
=======================
Luu so lieu moi lan chay de cac lan sau so sanh duoc.

Ly do co file nay: truoc day dashboard.html bi ghi de moi lan chay, khong giu
ban nao, nen khong the tra loi cau hoi kieu "hom qua so voi hom kia the nao".

Cau truc file logs/lich-su.json:
{
  "2026-09-27": {
      "moc": 8,
      "thoi_diem": "2026-09-28 08:26:34",
      "day_du": true,
      "so_camp": 12,
      "tong": {"spend": 20346476.0, "msg": 120, ...},
      "camp": [{"id": "...", "name": "...", "spend": ..., "purchase": ...}]
  }
}

Khoa cua dict la NGAY KET THUC cua ky bao cao:
  - Bao cao moc 8h ngay 28/09 noi ve ngay 27/09  -> luu vao khoa "2026-09-27"
  - Bao cao moc 17h ngay 28/09 noi ve ngay 28/09 -> luu vao khoa "2026-09-28"
Nho vay mot ngay chi co MOT ban ghi, va ban day du nhat se thang.
"""
import json
from datetime import date, datetime, timedelta
from pathlib import Path

# So ngay giu lai. Cu hon thi xoa cho gon.
SO_NGAY_GIU = 180

# Moc gio bao cao TRON mot ngay: 8h (hom truoc) va 22h (hom nay).
# Cac moc khac chi bao cao mot phan cua ngay.
MOC_DAY_DU = (8, 22)

CAC_CHI_SO = ("spend", "msg", "contact", "order", "purchase", "payment", "comment")


def _chuan_hoa_ngay(ngay):
    """Chap nhan ca doi tuong date lan chuoi 'YYYY-MM-DD'."""
    if hasattr(ngay, "strftime"):
        return ngay.strftime("%Y-%m-%d")
    return str(ngay)


def doc(path):
    """Doc toan bo lich su. Tra ve dict rong neu file chua co hoac bi hong.

    Khong bao gio nem loi: file hong khong duoc lam chet bao cao.
    """
    try:
        path = Path(path)
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _tong_rong():
    return {k: (0.0 if k == "spend" else 0) for k in CAC_CHI_SO}


def _don_dep(data, hom_nay=None):
    """Xoa cac ban ghi cu hon SO_NGAY_GIU ngay."""
    hom_nay = hom_nay or date.today()
    moc_cu = (hom_nay - timedelta(days=SO_NGAY_GIU)).strftime("%Y-%m-%d")
    for k in [k for k in data if k < moc_cu]:
        del data[k]
    return data


def ghi(path, ngay, moc, stats):
    """Ghi so lieu mot lan chay vao lich su.

    ngay: ngay KET THUC cua ky bao cao (date hoac 'YYYY-MM-DD')
    moc:  moc gio bao cao, vi du 8
    stats: dict do compute_stats() tra ve

    Quy tac ghi de: ban day du luon thang ban khong day du.
    Neu da co ban day du ma ban moi chi mot phan thi BO QUA (tra ve False).
    """
    path = Path(path)
    ngay = _chuan_hoa_ngay(ngay)
    data = doc(path)

    cu = data.get(ngay)
    day_du = moc in MOC_DAY_DU
    if cu and cu.get("day_du") and not day_du:
        return False

    data[ngay] = {
        "moc": moc,
        "thoi_diem": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "day_du": day_du,
        "so_camp": stats.get("total_campaigns", 0),
        "tong": dict(stats.get("totals", {})),
        "camp": [
            {
                "id": str(c.get("id", "")),
                "name": c.get("name", ""),
                "spend": c.get("spend", 0),
                "purchase": c.get("purchase", 0),
                "payment": c.get("payment", 0),
                "msg": c.get("msg", 0),
                "cpr": c.get("cpr"),
            }
            for c in stats.get("all", [])
        ],
    }
    _don_dep(data)

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return True


def lay_mot_ngay(path, ngay):
    """Tra ve ban ghi cua mot ngay, hoac None neu chua co."""
    return doc(path).get(_chuan_hoa_ngay(ngay))


def lay_khoang(path, tu, den):
    """Cong don cac chi so trong khoang [tu, den], bao gom ca hai dau mut.

    Tra ve {"tong": {...}, "so_ngay": so_ngay_co_du_lieu}.
    Ngay chua co du lieu bi bo qua (khong tinh vao so_ngay).
    """
    tu = _chuan_hoa_ngay(tu)
    den = _chuan_hoa_ngay(den)
    data = doc(path)
    tong = _tong_rong()
    so_ngay = 0

    for ngay in sorted(data):
        if tu <= ngay <= den:
            so_ngay += 1
            for k, v in (data[ngay].get("tong") or {}).items():
                if k in tong:
                    tong[k] += v

    return {"tong": tong, "so_ngay": so_ngay}


def lay_ky_truoc(path, ngay, so_ngay):
    """Tra ve tong hop `so_ngay` ngay NGAY TRUOC `ngay` (khong tinh chinh ngay do)."""
    ngay = _chuan_hoa_ngay(ngay)
    d = datetime.strptime(ngay, "%Y-%m-%d").date()
    den = (d - timedelta(days=1)).strftime("%Y-%m-%d")
    tu = (d - timedelta(days=so_ngay)).strftime("%Y-%m-%d")
    return lay_khoang(path, tu, den)
```

- [ ] **Step 4: Chạy kiểm thử để chắc chắn nó đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `OK`, 17 bài kiểm thử đạt.

- [ ] **Step 5: Kiểm tra `logs/` vẫn nằm trong `.gitignore`**

```bash
git check-ignore -v logs/lich-su.json
```

Kết quả mong đợi: in ra một dòng có `logs/`, nghĩa là file lịch sử sẽ **không** lên GitHub. Nếu không có kết quả, dừng lại và báo — không được commit file lịch sử lên mạng.

- [ ] **Step 6: Commit**

```bash
git add lich_su.py tests/test_lich_su.py
git commit -m "Them lich_su.py: kho luu lich su so lieu bao cao"
```

---

## Task 2: Thêm mốc giờ tường minh cho `report.py`

**Files:**
- Modify: `report.py` (thêm hàm mới sau hằng số `REPORT_SLOTS`; sửa `main()`)
- Test: `tests/test_report.py`

**Interfaces:**
- Consumes: không
- Produces:
  - `chon_moc(moc_tu_lenh, gio_hien_tai, danh_sach_moc=None) -> int`
    — `moc_tu_lenh` là `int` hoặc `None`; `danh_sach_moc` mặc định là `REPORT_SLOTS`; ném `ValueError` nếu `moc_tu_lenh` không nằm trong danh sách
  - `main()` nhận thêm cờ dòng lệnh `--slot N`

**Vì sao đây là chìa khoá chữa lỗi:** hiện tại `report.py` tự đoán mốc gần nhất
(`slot = min(REPORT_SLOTS, key=lambda s: abs(s - now.hour))`). Khi máy ngủ qua nhiều mốc,
Windows cho cả bốn lịch chạy bù cùng lúc, cả bốn cùng đoán ra một mốc, và gửi ra nhiều báo cáo
giống hệt nhau. Đã xảy ra thật: sáng 28/09/2026 lúc 08:26 gửi **4 tin trùng + 4 file HTML**.
Khi có `--slot`, mỗi lịch nói rõ nó là mốc nào, nên không còn đoán và không còn trùng.

- [ ] **Step 1: Viết kiểm thử thất bại**

Tạo `tests/test_report.py`:

```python
"""Kiem thu phan chon moc gio cua report.py."""
import unittest

import report


class TestChonMoc(unittest.TestCase):
    def test_co_slot_thi_tra_ve_dung_slot(self):
        self.assertEqual(report.chon_moc(22, 8, [8, 12, 17, 22]), 22)

    def test_co_slot_thi_bo_qua_gio_hien_tai(self):
        self.assertEqual(report.chon_moc(8, 23, [8, 12, 17]), 8)

    def test_khong_co_slot_thi_lay_moc_gan_nhat(self):
        self.assertEqual(report.chon_moc(None, 11, [8, 12, 17]), 12)

    def test_khong_co_slot_gio_23_lay_moc_gan_nhat(self):
        self.assertEqual(report.chon_moc(None, 23, [8, 12, 17]), 17)

    def test_khong_co_slot_dung_danh_sach_mac_dinh(self):
        self.assertEqual(report.chon_moc(None, 8), 8)

    def test_slot_khong_nam_trong_danh_sach_thi_bao_loi(self):
        with self.assertRaises(ValueError):
            report.chon_moc(22, 8, [8, 12, 17])

    def test_danh_sach_rong_thi_dung_mac_dinh(self):
        self.assertEqual(report.chon_moc(None, 8, []), 8)

    def test_moc_8h_va_22h_deu_chon_dung(self):
        for moc in (8, 12, 17, 22):
            with self.subTest(moc=moc):
                self.assertEqual(report.chon_moc(moc, 3, [8, 12, 17, 22]), moc)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `AttributeError: module 'report' has no attribute 'chon_moc'`

- [ ] **Step 3: Thêm hàm `chon_moc()` vào `report.py`**

Chèn ngay **sau** dòng khai báo `REPORT_SLOTS = [8, 12, 17, 22]` (khoảng dòng 27), trước phần
khai báo `NGUONG_CANH_BAO_NGAY`:

```python
def chon_moc(moc_tu_lenh, gio_hien_tai, danh_sach_moc=None):
    """Chon moc gio bao cao.

    moc_tu_lenh:  so nguyen do lich Windows truyen vao (co --slot), hoac None.
    gio_hien_tai: gio cua may, 0-23.
    danh_sach_moc: danh sach moc hop le; None thi dung REPORT_SLOTS.

    CO --slot thi tra ve DUNG moc do, khong doan gi ca.
    Day la diem chua loi gui trung: truoc day moi tien trinh deu tu doan moc
    gan nhat, nen nhieu lich chay bu cung luc se cung doan ra mot moc va gui
    ra nhieu bao cao giong het nhau.
    """
    if danh_sach_moc is None:
        danh_sach_moc = REPORT_SLOTS
    if not danh_sach_moc:
        danh_sach_moc = REPORT_SLOTS

    if moc_tu_lenh is not None:
        if moc_tu_lenh not in danh_sach_moc:
            raise ValueError(
                f"Moc {moc_tu_lenh}h khong nam trong danh sach moc {danh_sach_moc}"
            )
        return moc_tu_lenh

    # Khong co --slot: giu cach cu (doan moc gan nhat) de khong pha vo
    # cac lich cu trong luc chuyen doi.
    return min(danh_sach_moc, key=lambda s: abs(s - gio_hien_tai))
```

- [ ] **Step 4: Chạy kiểm thử để chắc chắn nó đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `OK`, 25 bài kiểm thử đạt.

- [ ] **Step 5: Nối `--slot` vào `main()`**

Trong `report.py`, tìm đoạn đầu của `main()` (khoảng dòng 584-603) và thay:

```python
    parser.add_argument("--mock", type=int, choices=REPORT_SLOTS,
                        help="Chay thu voi moc gio nay (khong gui Telegram)")
```

bằng:

```python
    parser.add_argument("--mock", type=int, choices=REPORT_SLOTS,
                        help="Chay thu voi moc gio nay (khong gui Telegram)")
    parser.add_argument("--slot", type=int, choices=REPORT_SLOTS,
                        help="Moc gio do lich Windows truyen vao (dung khi gui that)")
```

Rồi thay khối chọn mốc:

```python
    if args.mock is not None:
        slot = args.mock
        print(f"[CHE DO THU] Moc gio: {slot}h")
    else:
        # Tim moc gio gan nhat
        slot = min(REPORT_SLOTS, key=lambda s: abs(s - now.hour))
        print(f"Moc gio hien tai: {slot}h (gio may: {now.hour}h)")
```

bằng:

```python
    if args.mock is not None:
        slot = args.mock
        print(f"[CHE DO THU] Moc gio: {slot}h")
    else:
        slot = chon_moc(args.slot, now.hour, REPORT_SLOTS)
        if args.slot is not None:
            print(f"Mốc giờ do lịch truyền vào: {slot}h")
        else:
            print(f"Moc gio hien tai: {slot}h (gio may: {now.hour}h)")
```

> **Ghi chú (sửa 28/09):** dòng in khi có `--slot` phải **có dấu** vì nó hiện ra màn hình —
> đúng theo ràng buộc toàn cục. Bản đầu của kế hoạch ghi không dấu, mâu thuẫn với chính ràng buộc.
> Dòng `Moc gio hien tai:` giữ nguyên không dấu vì đó là chuỗi cũ, đổi sẽ phá tính tương thích.

- [ ] **Step 6: Chạy kiểm thử lại**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `OK`.

- [ ] **Step 7: Kiểm tra `--slot` chạy thật, không gửi gì**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --slot 12 --dry
```

Kết quả mong đợi: dòng `Mốc giờ do lịch truyền vào: 12h`, rồi báo cáo in ra màn hình,
kết thúc bằng `[Khong gui Telegram - che do thu]`.

- [ ] **Step 8: Kiểm tra mốc giờ sai bị chặn**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --slot 9 --dry
```

Kết quả mong đợi: thoát với lỗi `invalid choice: 9` — nghĩa là mốc giờ sai bị chặn ngay,
không âm thầm chạy sai.

- [ ] **Step 9: Commit**

```bash
git add report.py tests/test_report.py
git commit -m "report.py: them --slot de lich Windows noi ro moc gio (chua loi gui trung)"
```

---

## Task 3: Lưu số liệu vào lịch sử mỗi lần chạy

**Files:**
- Modify: `report.py` (`compute_stats()`, thêm `luu_lich_su()`, sửa `main()`)
- Test: `tests/test_report.py` (thêm lớp kiểm thử mới)

**Interfaces:**
- Consumes: `lich_su.ghi()` từ Task 1
- Produces:
  - `compute_stats()` trả về thêm khoá `"all"` — danh sách **mọi** campaign đủ điều kiện, cùng dạng dict với `"good"`/`"bad"`
  - `luu_lich_su(stats, ngay, moc, path_lich_su=None) -> None` — không bao giờ ném lỗi

**Ghi chú về một ngoại lệ có chủ ý:** bản thiết kế ghi "không đụng vào `compute_stats`".
Task này thêm **một khoá mới** `"all"` vào kết quả trả về. Đây là thay đổi **thuần thêm**:
không đổi giá trị của bất kỳ khoá nào đang có, không đổi phép tính nào. Cần thiết vì
`"good"` và `"bad"` chỉ chứa top 5 mỗi loại, không đủ để trả lời "camp nào tệ nhất tuần này"
ở giai đoạn sau. Lịch sử không thể ghi bù về quá khứ, nên phải ghi đủ ngay từ đầu.

- [ ] **Step 1: Viết kiểm thử thất bại**

Thêm vào cuối `tests/test_report.py`, **trước** khối `if __name__ == "__main__":`:

```python
import tempfile
from datetime import date
from pathlib import Path

import lich_su


def _hang_camp(cid, ten, spend, purchase):
    """Tao mot dong du lieu giong Meta tra ve."""
    actions = []
    if purchase:
        actions.append(
            {"action_type": "onsite_conversion.purchase", "value": str(purchase)}
        )
    return {
        "campaign_id": cid,
        "campaign_name": ten,
        "spend": str(spend),
        "actions": actions,
    }


class TestComputeStatsCoDanhSachDayDu(unittest.TestCase):
    def setUp(self):
        self.goc = report.fetch_insights
        self.rows = [
            _hang_camp("1", "dainq A", 100, 5),
            _hang_camp("2", "dainq B", 50, 0),
            _hang_camp("3", "thuonghieu X", 999, 9),
        ]
        report.fetch_insights = lambda env, since, until: (self.rows, None)
        self.env = {
            "FILTER_INCLUDE": "dainq",
            "FILTER_EXCLUDE": "thuonghieu,thương hiệu,Brand",
            "TOP_CAMPAIGN_COUNT": "5",
            "REPORT_ACCOUNT_NAME": "Test",
        }

    def tearDown(self):
        report.fetch_insights = self.goc

    def test_co_khoa_all(self):
        stats, err = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        self.assertIsNone(err)
        self.assertIn("all", stats)

    def test_all_chua_moi_camp_du_dieu_kien_khong_chi_top(self):
        stats, _ = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        self.assertEqual(len(stats["all"]), 2)

    def test_all_loai_bo_camp_bi_loc(self):
        stats, _ = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        ten = [c["name"] for c in stats["all"]]
        self.assertNotIn("thuonghieu X", ten)

    def test_all_co_du_cac_truong_can_thiet(self):
        stats, _ = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        self.assertEqual(
            set(stats["all"][0].keys()),
            {"rank", "id", "name", "spend", "purchase", "payment", "msg", "cpr"},
        )

    def test_good_va_bad_van_nhu_cu(self):
        stats, _ = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        self.assertEqual(len(stats["good"]), 1)
        self.assertEqual(len(stats["bad"]), 2)


class TestLuuLichSu(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "lich-su.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_luu_duoc_so_lieu(self):
        stats = {
            "total_campaigns": 2,
            "totals": {"spend": 100.0, "msg": 1, "contact": 1,
                       "order": 1, "purchase": 2, "payment": 1, "comment": 0},
            "all": [],
        }
        report.luu_lich_su(stats, "2026-09-27", 8, path_lich_su=self.path)
        ban_ghi = lich_su.lay_mot_ngay(self.path, "2026-09-27")
        self.assertIsNotNone(ban_ghi)
        self.assertEqual(ban_ghi["tong"]["spend"], 100.0)

    def test_loi_ghi_lich_su_KHONG_lam_no_chuong_trinh(self):
        # Truyen vao mot THU MUC thay vi file -> viec ghi se loi.
        # Ham phai nuot loi, khong duoc nem ra ngoai.
        report.luu_lich_su({"totals": {}, "all": []}, "2026-09-27", 8,
                           path_lich_su=Path(self.tmp.name))

    def test_stats_thieu_khoa_cung_khong_no(self):
        report.luu_lich_su({}, "2026-09-27", 8, path_lich_su=self.path)
        self.assertIsNotNone(lich_su.lay_mot_ngay(self.path, "2026-09-27"))
```

- [ ] **Step 2: Chạy kiểm thử để chắc chắn nó thất bại**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `AttributeError: module 'report' has no attribute 'luu_lich_su'`
và `AssertionError: 'all' not found in {...}`

> **Ghi chú (sửa 28/09):** bản đầu của kế hoạch ghi `len(stats["bad"]) == 1` — **sai, đã kiểm chứng**.
> Chạy thật `compute_stats()` với chính dữ liệu giả trên cho ra `bad` có **2** phần tử
> (`dainq B` rồi `dainq A`).
>
> Lý do: `compute_stats()` xếp `bad` = (camp không có lượt mua, chi tiêu giảm dần) **nối tiếp**
> (camp có lượt mua nhưng thấp, tăng dần), rồi cắt top N. Dữ liệu giả chỉ có 2 camp đủ điều kiện
> nên cả hai đều vào `bad`.
>
> ⚠️ **Hệ quả cần biết, không sửa trong kế hoạch này:** `bad` **không loại trừ** `good`.
> Camp `dainq A` nằm ở **cả hai** danh sách. Đây là hành vi **có sẵn** của `compute_stats()`,
> không phải thứ Task này tạo ra — nhưng nghĩa là khi tài khoản có ít camp, báo cáo Telegram có thể
> liệt kê cùng một camp ở cả mục "Camp hiệu quả" lẫn "Camp kém hiệu quả". Cần Đại quyết ở giai đoạn sau.

- [ ] **Step 3: Thêm khoá `"all"` vào `compute_stats()`**

Trong `report.py`, tìm phần `return` của `compute_stats()` (khoảng dòng 418-426) và thêm một dòng:

```python
    return {
        "total_campaigns": len(filtered),
        "totals": totals,
        "good": [pack(r, i + 1) for i, r in enumerate(good)],
        "bad": [pack(r, i + 1) for i, r in enumerate(bad)],
        "all": [pack(r, i + 1) for i, r in enumerate(filtered)],
        "include_kw": include_kw,
        "exclude_kw": env.get("FILTER_EXCLUDE", ""),
        "account_name": env.get("REPORT_ACCOUNT_NAME", ""),
    }, None
```

- [ ] **Step 4: Thêm hàm `luu_lich_su()` vào `report.py`**

Chèn ngay **trước** hàm `def main():`:

```python
def luu_lich_su(stats, ngay, moc, path_lich_su=None):
    """Luu so lieu vao lich su. KHONG BAO GIO nem loi ra ngoai.

    Muc dich: mot su co khi luu lich su khong duoc phep lam hong viec gui
    bao cao. Moi loi deu bi nuot va chi ghi nhat ky.
    """
    try:
        if path_lich_su is None:
            path_lich_su = LOG_DIR / "lich-su.json"
        lich_su.ghi(path_lich_su, ngay, moc, stats)
    except Exception as e:
        log(f"Khong luu duoc lich su: {e}")
```

- [ ] **Step 5: Thêm dòng import**

Ở đầu `report.py`, cạnh dòng `from dashboard import save_dashboard` (khoảng dòng 21), thêm:

```python
import lich_su
```

- [ ] **Step 6: Nối vào `main()`**

Trong `main()`, tìm khối:

```python
    stats, err = compute_stats(env, since, until)
    if err:
        print(f"LOI: {err}")
        log(f"THAT BAI - moc {slot}h: {err}")
        if args.mock is None and not args.dry:
            send_error_alert(env, err)
        sys.exit(1)

    report = build_report(env, stats, period_text)
```

Thay bằng:

```python
    stats, err = compute_stats(env, since, until)
    if err:
        print(f"LOI: {err}")
        log(f"THAT BAI - moc {slot}h: {err}")
        if args.mock is None and not args.dry:
            send_error_alert(env, err)
        sys.exit(1)

    # Luu lich su TRUOC khi gui: neu gui loi thi so lieu van con.
    # Bo qua o che do --mock vi moc gio trong che do do la gia.
    if args.mock is None:
        luu_lich_su(stats, until, slot)

    report = build_report(env, stats, period_text)
```

- [ ] **Step 7: Chạy kiểm thử để chắc chắn nó đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Kết quả mong đợi: `OK`, 33 bài kiểm thử đạt.

- [ ] **Step 8: Chạy thật ở chế độ không gửi, kiểm tra file lịch sử được tạo**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --slot 12 --dry
```

Rồi kiểm tra:

```bash
ls -la logs/lich-su.json && cat logs/lich-su.json
```

Kết quả mong đợi: file tồn tại, chứa một khoá là ngày hôm nay với `"moc": 12`, `"day_du": false`,
và danh sách `camp` không rỗng.

- [ ] **Step 9: Commit**

```bash
git add report.py tests/test_report.py
git commit -m "report.py: luu so lieu vao lich su moi lan chay"
```

---

## Task 4: Sửa lịch Windows để truyền mốc giờ

**Files:**
- Modify: `cai-dat-lich.bat`

**Interfaces:**
- Consumes: cờ `--slot N` của `report.py` từ Task 2
- Produces: bốn lịch Windows (hoặc ba, nếu bỏ mốc 22h) mà mỗi lịch tự khai mốc của mình

**Bối cảnh:** đây là **bản vá tạm** chữa hai lỗi đang chạy ngay lập tức, trước khi Giai đoạn 2
thay toàn bộ cơ chế lịch bằng một tiến trình thường trú. Phần sửa trong `report.py` (`--slot`)
là lâu dài; phần sửa trong `cai-dat-lich.bat` sẽ bị Giai đoạn 2 gỡ bỏ.

**Quyết định của Đại:** bỏ mốc 22h trên máy công ty. Vì vậy danh sách còn `8,12,17`.

**Trạng thái thật của máy, đọc ngày 28/09/2026 bằng `Get-ScheduledTask`:**

```
BaoCaoMetaAds_08 | State=Ready  Args="D:\Buddy Work AI\2026-09-14-07-50-57\report.py"
BaoCaoMetaAds_12 | State=Ready  Args="D:\Buddy Work AI\2026-09-14-07-50-57\report.py"
BaoCaoMetaAds_17 | State=Ready  Args="D:\Buddy Work AI\2026-09-14-07-50-57\report.py"
BaoCaoMetaAds_22 | State=Ready  Args="D:\Buddy Work AI\2026-09-14-07-50-57\report.py"
   (ca bon deu co StartWhenAvailable=True, WakeToRun=True, LastResult=0)
```

Hai điều rút ra:

1. **`Args` hoàn toàn không có `--slot`** — đúng như chẩn đoán. Đây là bằng chứng trực tiếp,
   không phải suy luận.
2. **Lịch 22h CÓ tồn tại và đang ở trạng thái Ready.** Nghĩa là nó không hỏng vì thiếu lịch.
   Nó không báo cáo vì máy **không bật lúc 22:00** — khi đó lịch 22h chỉ chạy bù vào sáng hôm sau,
   và lúc đó script tự đoán ra mốc 8h. Vậy việc bỏ mốc 22h là hợp lý: Đại không có mặt ở máy lúc 22:00.

- [ ] **Step 1: Sửa hàm `:TaoLich` để truyền `--slot`**

Trong `cai-dat-lich.bat`, tìm dòng 129:

```bat
schtasks /Create /TN "BaoCaoMetaAds_%MOC%" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" /SC DAILY /ST %MOC%:00 /F >nul 2>&1
```

Thay bằng:

```bat
schtasks /Create /TN "BaoCaoMetaAds_%MOC%" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --slot %MOC%" /SC DAILY /ST %MOC%:00 /F >nul 2>&1
```

Và dòng 133 (nhánh in lỗi chi tiết) cũng phải sửa y hệt:

```bat
    schtasks /Create /TN "BaoCaoMetaAds_%MOC%" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --slot %MOC%" /SC DAILY /ST %MOC%:00 /F
```

Dùng luôn `%MOC%` (đang ở dạng hai chữ số `08`, `12`, `17`) chứ không cần biến mới.
`argparse` với `type=int` đọc `"08"` thành `8` bình thường, nên `--slot 08` hợp lệ.
Giữ nguyên dạng hai chữ số còn giúp bước kiểm chứng ở Step 7 rõ ràng, không nhầm `8` với `17`.

> ⚠️ **BẪY DẤU NHÁY — đọc kỹ (sửa 28/09, đã kiểm chứng bằng thực nghiệm).**
> Dòng lệnh phải kết thúc bằng `--slot %MOC%"` với dấu nháy **ĐÓNG THẬT**, **KHÔNG** phải `--slot %MOC%\"`.
>
> Bản đầu của kế hoạch này viết `\"`. Đó là dấu nháy **đã escape**, không phải dấu nháy đóng — nên
> chuỗi của `/TR` không bao giờ được đóng lại và nuốt luôn `/SC DAILY /ST ... /F`.
>
> Đã kiểm chứng bằng cách chạy thật một file `.bat` với chương trình in `sys.argv` thay cho `schtasks`
> (cùng quy tắc tách đối số của Windows):
> - **Sai:** `['"...report.py" --slot 08" /SC DAILY /ST 08:00 /F']` — một đối số duy nhất, mất sạch cờ.
> - **Đúng:** `['"...report.py" --slot 08', '/SC', 'DAILY', '/ST', '08:00', '/F']`.
>
> Hậu quả nếu dùng bản sai: `schtasks` không nhận `/SC` nên **không tạo được lịch nào cả** — bản vá
> còn tệ hơn trước khi sửa. Vì dòng đầu có `>nul 2>&1` che lỗi, dấu hiệu duy nhất là các dòng `[LOI]`
> in ra từ nhánh thứ hai.

- [ ] **Step 2: Bỏ mốc 22h khỏi danh sách tạo lịch**

Tìm khối khoảng dòng 88-91:

```bat
call :TaoLich 08
call :TaoLich 12
call :TaoLich 17
call :TaoLich 22
```

Thay bằng:

```bat
REM Ngay 28/09/2026: bo moc 22h. Ly do: kiem tra logs/baocao.log cho thay moc 22h
REM CHUA TUNG chay mot lan nao (0 lan trong toan bo nhat ky), va khi may thuc day
REM buoi sang thi lich 22h chay bu va tu doan ra moc 8h -> gay bao cao trung.
call :TaoLich 08
call :TaoLich 12
call :TaoLich 17
```

- [ ] **Step 3: Dọn cả lịch cũ đã có tiền tố khác**

Khối xoá lịch cũ ở khoảng dòng 80-83 đang là:

```bat
for %%H in (08 12 17 22) do (
    schtasks /Delete /TN "BaoCaoMetaAds_%%H" /F >nul 2>&1
)
```

Giữ nguyên (nó vẫn xoá đúng lịch `BaoCaoMetaAds_22` cũ), nhưng thêm một dòng ngay sau để
dọn cả dạng tên không có số 0 ở đầu, phòng trường hợp đã từng cài bằng bản khác:

```bat
for %%H in (8 22) do (
    schtasks /Delete /TN "BaoCaoMetaAds_%%H" /F >nul 2>&1
)
```

- [ ] **Step 4: Cập nhật dòng thông báo cuối file**

Tìm dòng 115:

```bat
echo Cac moc gio: 08:00, 12:00, 17:00, 22:00 hang ngay
```

Thay bằng:

```bat
echo Cac moc gio: 08:00, 12:00, 17:00 hang ngay
echo (Moc 22h da bo tu 28/09/2026 - xem ghi chu trong file nay)
```

- [ ] **Step 5: Cài lịch**

**Việc này Đại làm.** Chuột phải `cai-dat-lich.bat` → **Run as administrator**.
Kết quả mong đợi:

```
[OK]  Moc 08:00 - da tao
[OK]  Moc 12:00 - da tao
[OK]  Moc 17:00 - da tao
```

- [ ] **Step 6: Kiểm chứng độc lập rằng lịch đã có `--slot`**

**Không tin dòng `[OK]`** — nó chỉ nói `schtasks` không báo lỗi, không nói tham số đã đúng.
`schtasks.exe` bị chặn trong môi trường agent, nên dùng `Get-ScheduledTask`.
Cách này **đã chạy thử và hoạt động** ngày 28/09/2026.
Ghi ra file tạm rồi đọc, vì công cụ PowerShell không trả về stdout:

```powershell
$out = @()
foreach ($n in @('BaoCaoMetaAds_08','BaoCaoMetaAds_12','BaoCaoMetaAds_17','BaoCaoMetaAds_22')) {
  $t = Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue
  if (-not $t) { $out += "$n : KHONG TIM THAY"; continue }
  $out += "$n | State=" + $t.State
  foreach ($a in $t.Actions) { $out += "   Args=" + $a.Arguments }
  $out += "   StartWhenAvailable=" + $t.Settings.StartWhenAvailable + " WakeToRun=" + $t.Settings.WakeToRun
  $i = Get-ScheduledTaskInfo -TaskName $n -ErrorAction SilentlyContinue
  if ($i) { $out += "   LastResult=" + $i.LastTaskResult }
}
$out | Out-File "$env:TEMP\_tasks.txt" -Encoding UTF8
```

Rồi đọc `C:\Users\nguye\AppData\Local\Temp\_tasks.txt`.

**Điều kiện đạt:**
- `BaoCaoMetaAds_08` → `Args` **phải chứa** `--slot 08`
- `BaoCaoMetaAds_12` → `Args` **phải chứa** `--slot 12`
- `BaoCaoMetaAds_17` → `Args` **phải chứa** `--slot 17`
- `BaoCaoMetaAds_22` → `KHONG TIM THAY` (đã bỏ đúng như chủ ý)
- `State=Ready` cho cả ba lịch còn lại

Nếu `Args` không có `--slot`, dừng lại — bản vá chưa có tác dụng, phải tìm nguyên nhân trước.

- [ ] **Step 7: Kiểm chứng không còn gửi trùng**

Đây là điều quan trọng nhất của cả giai đoạn. `HANDOFF.md` từng kết luận sai ở đúng bước này
vì chỉ thử **chạy lại tuần tự**, trong khi lỗi chỉ hiện khi chạy **đồng thời**.

Mô phỏng đúng tình huống gây lỗi: nhiều lịch chạy bù cùng lúc. Chạy ba tiến trình song song
với ba mốc khác nhau, ở chế độ không gửi:

```bash
cd "D:/Buddy Work AI/2026-09-14-07-50-57"
P="C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
"$P" report.py --slot 08 --dry & "$P" report.py --slot 12 --dry & "$P" report.py --slot 17 --dry & wait
```

**Điều kiện đạt:** cả ba dòng đầu ra phải ghi **mốc khác nhau** (`08h`, `12h`, `17h`).
Nếu cả ba cùng ghi một mốc thì bản vá thất bại.

> ⚠️ **Lưu ý phụ:** vì `--dry` là "chạy thật nhưng không gửi", ba lần chạy này **có ghi vào
> `logs/lich-su.json`** (mốc 8 ghi vào ngày hôm qua, mốc 12 và 17 ghi vào ngày hôm nay).
> Đây là số liệu thật nên không sai, chỉ là bản ghi của ngày hôm nay sẽ là bản **một phần**
> cho tới khi báo cáo 8h sáng mai ghi đè bằng bản đầy đủ. Không cần dọn.
> Chỉ khi muốn xoá sạch để thử lại từ đầu thì xoá `logs/lich-su.json`.

- [ ] **Step 8: Commit**

```bash
git add cai-dat-lich.bat
git commit -m "cai-dat-lich.bat: truyen --slot vao tung lich; bo moc 22h"
```

---

## Task 5: Cập nhật tài liệu

**Files:**
- Modify: `README.md`
- Modify: `HANDOFF.md`

> **Ghi chú (bổ sung 28/09 — bắt buộc làm):** bốn bước dưới đây **chưa đủ**. Khi kiểm lại sau khi
> làm bốn bước đó, tài liệu vẫn còn **13 câu nói sai về hệ thống hiện tại** — chúng vẫn ghi "4 lịch",
> "4 mốc", hoặc liệt kê mốc 22h như đang tồn tại, trong khi bảng mốc giờ đã còn 3.
> Mục tiêu của Task này là "tài liệu khớp với hành vi thật", nên để lại chúng là Task không đạt mục tiêu.
>
> **Phải sửa — mọi câu nói về trạng thái HIỆN TẠI:**
> - `README.md:21` — "**4 lần mỗi ngày**" → 3
> - `README.md:50` — "tự tạo 4 lịch trong Windows" → 3
> - `README.md:58` — dòng `[OK]  Moc 22:00 - da tao` trong khối kết quả mong đợi → xoá
> - `README.md:67` — "4 lịch bị xóa" → 3
> - `README.md:172` — "cả 4 lịch" → 3
> - `README.md:178` — "khung **8h–22h**" → "8h–17h"
> - `README.md:311` — "4 task tên `BaoCaoMetaAds_8/12/17/22`" → "3 task tên `BaoCaoMetaAds_08/12/17`"
> - `HANDOFF.md:19` — "**4 mốc mỗi ngày**: 8h, 12h, 17h, 22h" → 3 mốc, bỏ 22h
> - `HANDOFF.md:32` — "4 lịch tự động | Tên `BaoCaoMetaAds_08/12/17/22`" → 3 lịch, bỏ 22
> - `HANDOFF.md:33` — "cho cả 4 lịch" → 3
> - `HANDOFF.md:45` — "4 lịch tự động" → 3
> - `HANDOFF.md:159` — "Bật 4 lịch tự động" → 3
> - `HANDOFF.md:160` — "Tắt 4 lịch" → 3
> - `HANDOFF.md:208` — "cả 4 lịch chạy bù CÙNG LÚC" → "cả ba lịch"
>
> **KHÔNG sửa — đây là ghi chép lịch sử, đúng với thời điểm được ghi:**
> `README.md:181` (nhật ký ngày 12/09 nói mốc 22h chạy đúng giờ) và `HANDOFF.md:288`
> (dòng mốc thời gian ngày 14/09 liệt kê 22h). Chỉ cần bảo đảm chúng đọc ra là chuyện **đã qua** —
> nếu câu chữ hiện tại khiến người đọc tưởng đó là trạng thái hiện tại thì thêm một chữ như "trước đây".
>
> `README.md:155` ("Bản ghi của báo cáo 8h và 22h là bản đầy đủ cả ngày") **giữ nguyên** — câu này
> mô tả đúng **mã nguồn** (`MOC_DAY_DU = (8, 22)`), và máy nhà vẫn có thể bật mốc 22h.

**Interfaces:**
- Consumes: tất cả thay đổi của Task 1–4
- Produces: tài liệu khớp với hành vi thật của hệ thống

- [ ] **Step 1: Cập nhật bảng mốc giờ trong `README.md`**

Bảng ở khoảng dòng 23-28 đang liệt kê bốn mốc. Xoá dòng mốc 22h và thêm ghi chú:

```markdown
| Giờ | Nội dung báo cáo |
|---|---|
| 🌅 **8:00** | Tổng kết ngày hôm qua |
| ☀️ **12:00** | Kết quả từ 0h đến 12h hôm nay |
| 🌤️ **17:00** | Kết quả từ 0h đến 17h hôm nay |

> 📌 **Mốc 22h đã bỏ từ 28/09/2026.** Lý do: kiểm tra `logs/baocao.log` cho thấy mốc 22h
> **chưa từng chạy một lần nào** kể từ khi lắp hệ thống, và khi máy thức dậy buổi sáng thì
> lịch 22h chạy bù và tự đoán ra mốc 8h — gây ra báo cáo trùng.
```

- [ ] **Step 2: Thêm mục về file lịch sử vào `README.md`**

Chèn sau mục "📊 Dashboard xem báo cáo":

```markdown
---

## 🗂️ Lịch sử số liệu (file `logs/lich-su.json`)

Mỗi lần chạy, hệ thống ghi lại số liệu vào `logs/lich-su.json`, giữ **180 ngày**.

**Để làm gì:** trước đây `dashboard.html` bị ghi đè mỗi lần chạy nên không giữ lại số cũ.
Không có số cũ thì không thể trả lời những câu như *"tuần này so với tuần trước thế nào"*.
File này là nền cho các tính năng so sánh sẽ làm sau.

**Có gì trong đó:** mỗi ngày một bản ghi, gồm tổng 7 chỉ số và danh sách toàn bộ campaign.
Bản ghi của báo cáo 8h và 22h là bản **đầy đủ cả ngày**; bản của 12h và 17h là bản **một phần**.
Khi cả hai loại cùng có, bản đầy đủ luôn thắng.

**File này không lên GitHub** — nó nằm trong `logs/`, đã bị `.gitignore` chặn.
```

- [ ] **Step 3: Thêm mục về `--slot` vào phần "Ghi chú kỹ thuật" của `README.md`**

Chèn vào cuối mục "Ghi chú kỹ thuật (cho người biết code)":

```markdown
### Tham số `--slot` — chống gửi trùng báo cáo

Mỗi lịch Windows gọi `report.py` kèm mốc giờ của chính nó:

```
python report.py --slot 08
python report.py --slot 12
python report.py --slot 17
```

**Vì sao cần:** trước 28/09/2026, lịch không truyền mốc giờ, nên `report.py` phải tự đoán
mốc gần nhất với giờ hiện tại. Khi máy ngủ qua nhiều mốc, Windows cho nhiều lịch chạy bù
**cùng lúc** — tất cả cùng đoán ra một mốc và gửi ra nhiều báo cáo giống hệt nhau.
Đã xảy ra thật: sáng 28/09/2026 lúc 08:26 gửi 4 tin trùng + 4 file HTML.

**Lưu ý:** cơ chế chống trùng cũ (`logs/da_gui.json`) vẫn còn, nhưng chỉ là lưới an toàn —
nó kiểm tra rồi mới ghi, nên khi nhiều tiến trình chạy đồng thời thì cả loạt đều lọt qua.
`--slot` mới là thứ chặn từ gốc.

**Không có `--slot`** (chạy tay): script vẫn đoán mốc gần nhất như cũ, để tương thích ngược.
```

- [ ] **Step 4: Cập nhật `HANDOFF.md`**

Thêm một mục vào phần "GHI CHÚ KỸ THUẬT CHO TRỢ LÝ AI":

```markdown
### BẢN SỬA NGÀY 28/09/2026 — TRUYỀN MỐC GIỜ VÀO LỊCH

**Vấn đề gốc:** `cai-dat-lich.bat` tạo lịch mà **không truyền mốc giờ**, nên `report.py`
phải tự đoán mốc gần nhất. Hai hậu quả, đều đã kiểm chứng bằng `logs/baocao.log`:

1. **Mốc 22h chưa từng chạy.** Đếm trong toàn bộ nhật ký: mốc 8h có 51 dòng, 12h có 37,
   17h có 27, **22h có 0**. Báo cáo "tổng kết cả ngày" chưa bao giờ tồn tại.
2. **Vẫn gửi trùng.** Đếm số lần gửi thành công theo ngày: 14/09 = 5, 15/09 = 4, 18/09 = 4,
   24/09 = 4, 28/09 = 4 (bình thường chỉ nên 3). Sáng 28/09 lúc 08:26 gửi 4 tin trùng.

**Đã sửa:** thêm tham số `--slot` cho `report.py`; `cai-dat-lich.bat` truyền mốc giờ vào
từng lịch; bỏ mốc 22h. Thêm `lich_su.py` lưu số liệu 180 ngày vào `logs/lich-su.json`.

> ⚠️ **Bài học về cách kiểm chứng:** `HANDOFF.md` trước đây ghi cơ chế chống trùng
> "đã kiểm chứng" — nhưng cách kiểm chỉ là **chạy lại tuần tự**, trong khi lỗi chỉ xuất hiện
> khi chạy **đồng thời**. Từ nay, mọi thay đổi liên quan tới lịch chạy phải được thử bằng
> **nhiều tiến trình song song**, không chỉ chạy lại một mình.
```

- [ ] **Step 5: Commit**

```bash
git add README.md HANDOFF.md
git commit -m "Cap nhat README va HANDOFF cho --slot, lich su so lieu, bo moc 22h"
```

---

## Kiểm chứng cuối cùng

Chạy toàn bộ trước khi báo hoàn thành:

- [ ] **Toàn bộ kiểm thử đạt**

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -m unittest discover -s tests -t . -v
```

Mong đợi: `OK`, 33 bài đạt, 0 lỗi.

- [ ] **Ba mốc song song ra ba mốc khác nhau** (bước 7 của Task 4)

- [ ] **Lịch đã có `--slot` và mốc 22h đã mất** (bước 6 của Task 4)

- [ ] **`logs/lich-su.json` được tạo và chứa dữ liệu thật** (bước 8 của Task 3)

- [ ] **File lịch sử không lọt lên GitHub**

```bash
git check-ignore -v logs/lich-su.json
```

- [ ] **Chạy tay vẫn hoạt động như cũ** (tương thích ngược)

```bash
"C:/Users/nguye/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" report.py --dry
```

Mong đợi: vẫn tự đoán mốc gần nhất, không lỗi.

---

## Ghi chú chuyển sang Giai đoạn 2

- Bản vá trong `cai-dat-lich.bat` sẽ bị Giai đoạn 2 gỡ bỏ, khi tiến trình thường trú thay
  toàn bộ cơ chế lịch. Phần `--slot` trong `report.py` thì **giữ lại** — tiến trình thường trú
  cũng sẽ gọi `report.py` kèm mốc giờ.
- Khoá `REPORT_SLOTS` trong `.env` **chưa làm ở giai đoạn này**. Giai đoạn 2 sẽ thêm, để tiến
  trình thường trú biết danh sách mốc của máy mình. Hiện tại danh sách mốc nằm trong
  `cai-dat-lich.bat`.
- **Hạn chế đã biết, cố ý không sửa ở giai đoạn này:** `determine_period()` vẫn viết cứng
  `if slot_hour == 8`. Nếu sau này đổi mốc sáng sang giờ khác (ví dụ 7h), báo cáo sẽ hiểu sai
  thành "trong ngày" thay vì "hôm qua". Đại đang giữ mốc 8h nên chưa ảnh hưởng. Giai đoạn 2
  nên sửa cùng lúc với việc đưa `REPORT_SLOTS` vào `.env`.
