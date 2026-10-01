# Kế hoạch thi công — Agent tự ghi `logs/lich-su.json`

**Ngày:** 01/10/2026 · **Trạng thái:** viết xong, **CHỜ ĐẠI DUYỆT**
**Là BƯỚC 1 của:** `2026-09-30-chuyen-telegram-ve-agent.md` (chuyển Telegram về cho agent)

> **For agentic workers:** REQUIRED SUB-SKILL: dùng `executing-plans` để thi công từng bước.

**Mục tiêu:** mỗi ngày một lần, agent tự lấy số liệu **một ngày trọn vẹn** rồi ghi vào
`logs/lich-su.json` — **chỉ khi ngày đó còn thiếu**. Nhờ vậy phần **hỏi đáp** không chết khi báo cáo
theo khung giờ bị tắt.

**Tech Stack:** Python 3.13 thuần, chỉ thư viện chuẩn (`json`, `datetime`, `unittest`, `unittest.mock`).
Kiểm thử **không gọi mạng**.

---

## 1. VÌ SAO PHẢI LÀM BƯỚC NÀY TRƯỚC KHI BỎ BÁO CÁO

`logs/lich-su.json` là **sổ số liệu 180 ngày**. Hiện **chỉ `report.py` ghi**, mỗi mốc báo cáo một lần.
Ba thứ đang **đọc** nó:

| Ai đọc | Dùng để làm gì |
|---|---|
| `cong_cu.py` (4 công cụ của phần hỏi đáp) | `lay_mot_ngay`, `lay_khoang`, `xep_hang_camp`, `so_sanh` |
| `ai.py::tra_loi()` | trả lời câu hỏi của Đại |
| `dashboard.py` | tạo file HTML |

⇒ Bỏ báo cáo theo khung giờ mà **không cho ai ghi sổ** ⇒ **hỏi đáp trả lời sai hoặc rỗng** — đúng
thứ Đại muốn giữ lại. Thứ tự bắt buộc: **agent ghi sổ → chạy song song đối chiếu → rồi mới tắt báo cáo.**

---

## 2. THIẾT KẾ

### 2.1. Ba nguyên tắc

1. **Không viết lại hàm nào của `report.py`.** Dùng đúng `report.compute_stats` và
   `report.luu_lich_su` ⇒ số liệu agent ghi **giống hệt** số liệu báo cáo ghi, kể cả bộ lọc
   `FILTER_INCLUDE` / `FILTER_EXCLUDE` và cách đếm lượt mua.
2. **Chỉ ghi khi THIẾU.** Ngày đó đã có bản ghi **trọn ngày** thì **không làm gì**. Nhờ vậy chạy
   song song với báo cáo **không giẫm chân nhau**: báo cáo ghi trước thì agent thôi.
3. **Việc phụ, không được làm chết agent.** Mọi lỗi đều bị nuốt và trả về `(False, lý do)`.

### 2.2. Vì sao phải **sau 09:00** mới ghi

`report.py` ghi bản ghi **trọn ngày cho hôm trước** vào **mốc 8h** (sáng hôm sau). Và Meta
**báo đơn TRỄ**. Nếu agent chạy lúc 00:05 thì: (a) tranh nhau với mốc 8h, (b) lấy số khi Meta chưa
chốt xong. ⇒ Agent chỉ **thử từ 09:00 trở đi**, và thử lại **mỗi giờ** cho tới khi ghi được.

### 2.3. Vì sao mốc ghi là `8`

`lich_su.MOC_DAY_DU = (8, 22)` — **chỉ hai mốc này** được coi là "trọn ngày".
Mốc 8 nghĩa là *"báo cáo về NGÀY HÔM TRƯỚC"* ⇒ cặp đúng là `moc=8` + `ngay=hôm qua`.
Dùng mốc khác thì bản ghi bị coi là **không trọn ngày** và sẽ bị mốc 8 ghi đè sau.

### 2.4. Điểm gắn vào `agent.py`

Thêm **nhịp thứ ba, thưa** (1 giờ một lần) chạy **trước** phần quét Meta.
**Không đụng** vào hai nhịp sẵn có: nghe nút bấm 15 giây · quét Meta `AGENT_NHIP_PHUT` phút.

```
vòng lặp agent (15 giây một vòng)
 ├── 1. nghe nút bấm / lệnh gõ tay          (mỗi vòng)
 ├── 2. GHI LỊCH SỬ nếu cần                 (1 giờ một lần)  ← MỚI
 └── 3. quét Meta, xin phép tắt nhóm        (AGENT_NHIP_PHUT phút)
```

---

## 3. CODE

### 3.1. File mới `agent_lich_su.py`

```python
"""AGENT TU GHI logs/lich-su.json — de phan hoi dap khong chet khi bo bao cao.

VI SAO CAN: logs/lich-su.json do report.py ghi moi moc bao cao. Neu bo bao cao
theo khung gio thi KHONG CON AI GHI SO DO, ma phan hoi dap (cong_cu.py, ai.py)
doc chinh so do => tra loi sai hoac rong.

CACH LAM: moi ngay mot lan (sau 09:00), agent kiem tra xem ngay HOM QUA da co
ban ghi TRON NGAY chua. Chua co thi lay so tu Meta roi ghi.

KHONG viet lai ham nao cua report.py: dung dung report.compute_stats va
report.luu_lich_su, nen so lieu agent ghi GIONG HET so lieu bao cao ghi.
"""
from datetime import datetime, timedelta, timezone

import lich_su
import report

GIO_VN = timezone(timedelta(hours=7))

# Chi ghi sau gio nay. Ly do: report.py ghi ban ghi TRON NGAY cho hom truoc vao
# moc 8h, va Meta bao don TRE. Chay luc 00:05 se tranh nhau voi moc 8h va lay
# so khi Meta chua chot.
GIO_BAT_DAU = 9

# Moc ghi vao lich su. Phai nam trong lich_su.MOC_DAY_DU = (8, 22) thi ban ghi
# moi duoc coi la TRON NGAY. Moc 8 = "bao cao ve NGAY HOM TRUOC".
MOC_TRON_NGAY = 8


def duong_dan_lich_su():
    return report.LOG_DIR / "lich-su.json"


def ngay_hom_qua(bay_gio=None):
    """Ngay HOM QUA theo gio Viet Nam."""
    goc = bay_gio or datetime.now(GIO_VN)
    return goc.date() - timedelta(days=1)


def da_co_ban_ghi_tron_ngay(path, ngay):
    """Lich su da co ban ghi TRON NGAY cho ngay do chua. Hong -> coi nhu CHUA."""
    try:
        ban = lich_su.lay_mot_ngay(path, ngay)
    except Exception:
        return False
    return bool(ban) and bool(ban.get("day_du"))


def ghi_neu_can(env, bay_gio=None, path=None):
    """Ghi lich su cho ngay hom qua neu thieu. Tra ve (da_ghi: bool, ly_do: str).

    KHONG BAO GIO nem loi ra ngoai — day la viec phu, khong duoc lam chet agent.
    """
    try:
        goc = bay_gio or datetime.now(GIO_VN)
        if goc.hour < GIO_BAT_DAU:
            return False, f"chua toi {GIO_BAT_DAU}h"
        ngay = ngay_hom_qua(goc)
        path = path or duong_dan_lich_su()
        if da_co_ban_ghi_tron_ngay(path, ngay):
            return False, f"{ngay} da co ban ghi tron ngay"
        stats, loi = report.compute_stats(env, ngay, ngay)
        if loi or not isinstance(stats, dict):
            return False, f"khong lay duoc so ngay {ngay}: {loi}"
        report.luu_lich_su(stats, ngay, MOC_TRON_NGAY, path)
        if da_co_ban_ghi_tron_ngay(path, ngay):
            return True, f"da ghi so ngay {ngay}"
        return False, f"ghi so ngay {ngay} khong thanh cong"
    except Exception as e:
        return False, f"loi khi ghi so: {type(e).__name__}: {e}"
```

### 3.2. Sửa `agent.py` — thêm nhịp thứ ba

**Thêm import** (cạnh các import `agent_*` sẵn có):

```python
import agent_lich_su
```

**Thêm hằng** (cạnh `NHIP_NHANH_GIAY`):

```python
# Ghi lich su: thu moi 1 gio mot lan. Viec nhe (chi doc file), va chi goi Meta
# khi THIEU ban ghi — nen khong ton gi.
KHOANG_THU_LICH_SU = 60 * 60
```

**Trong `main()`, trước `while True:`** (cạnh `lan_quet_ke = 0.0`):

```python
    lan_thu_lich_su_ke = 0.0
```

**Trong vòng lặp**, đặt **giữa** bước nghe nút bấm và bước quét Meta:

```python
                # 2. GHI LICH SU cho ngay hom qua — 1 gio mot lan.
                #    Chi goi Meta khi ngay do THIEU ban ghi tron ngay, nen chay
                #    song song voi bao cao khong giẫm chan nhau.
                if time.time() >= lan_thu_lich_su_ke:
                    lan_thu_lich_su_ke = time.time() + KHOANG_THU_LICH_SU
                    da_ghi, ly = agent_lich_su.ghi_neu_can(env, bay_gio)
                    if da_ghi:
                        report.log(f"AGENT: tu ghi lich su — {ly}")
                    elif ly.startswith("khong lay duoc") or ly.startswith("loi"):
                        report.log(f"AGENT: ghi lich su that bai — {ly}")
```

### 3.3. Kiểm thử — lớp mới `L_AgentTuGhiLichSu` trong `tests/test_agent.py`

Dùng `unittest.mock` để **không gọi mạng**:

| # | Bài kiểm thử | Điều phải đúng |
|---|---|---|
| 1 | `test_truoc_9h_thi_khong_lam_gi` | `ghi_neu_can` lúc 08:59 trả `(False, "chua toi 9h")`, **không** gọi `compute_stats` |
| 2 | `test_da_co_ban_ghi_tron_ngay_thi_thoi` | Có bản ghi `day_du=True` ⇒ trả `(False, ...)`, **không** gọi `compute_stats` |
| 3 | `test_ban_ghi_khong_day_du_thi_van_ghi` | Có bản ghi `day_du=False` ⇒ **có** gọi `compute_stats` |
| 4 | `test_thieu_thi_lay_so_va_ghi` | Gọi `compute_stats(env, ngay, ngay)` rồi `luu_lich_su(stats, ngay, 8, path)` |
| 5 | `test_moc_ghi_phai_nam_trong_MOC_DAY_DU` | `MOC_TRON_NGAY in lich_su.MOC_DAY_DU` — chống đổi mốc làm hỏng "trọn ngày" |
| 6 | `test_meta_loi_thi_KHONG_nem_ra` | `compute_stats` trả lỗi ⇒ `(False, ...)`, không ném |
| 7 | `test_compute_stats_nem_exception_cung_khong_sao` | `compute_stats` ném `RuntimeError` ⇒ `(False, "loi khi ghi so: ...")` |
| 8 | `test_ngay_hom_qua_dung_mui_gio_VN` | 01/10 08:00 VN ⇒ 30/09; 01/10 00:30 VN ⇒ 30/09 |
| 9 | `test_ly_do_hien_cho_Dai_phai_CO_DAU` | Chuỗi trả về có dấu tiếng Việt (quy ước repo) — nếu có hiện cho Đại |

---

## 4. RỦI RO

| Rủi ro | Mức | Xử lý |
|---|---|---|
| Agent ghi đè bản ghi báo cáo bằng số **thiếu** (Meta chưa chốt) | Trung bình | Chỉ ghi khi **thiếu hẳn** bản ghi trọn ngày; và chỉ **sau 09:00**. Báo cáo ghi trước thì agent thôi |
| Hai tiến trình cùng ghi `lich-su.json` | Thấp | `lich_su.ghi` đã có **khoá file + ghi nguyên tử** sẵn |
| Meta lỗi kéo dài ⇒ mất sổ nhiều ngày | Trung bình | Thử lại **mỗi giờ**; lỗi được ghi vào `logs/baocao.log` |
| Ghi sổ làm chậm/chết vòng lặp agent | Thấp | `ghi_neu_can` **nuốt mọi lỗi**; nằm trong `try` chung của vòng lặp |
| Đổi `MOC_TRON_NGAY` sau này làm hỏng "trọn ngày" | Thấp | Có bài kiểm thử #5 chặn |

---

## 5. KẾT QUẢ DỰNG THỬ (01/10/2026, 10h43)

Dựng `agent_lich_su.py` **ngoài repo** (`%TEMP%\dung-thu-lich-su\`), chạy thật bằng **dữ liệu Meta
của Đại** (chỉ đọc), ghi vào **file lịch sử tạm** — không đụng gì trong repo.

| # | Phép kiểm | Kết quả |
|---|---|---|
| 1 | `MOC_TRON_NGAY=8` có nằm trong `lich_su.MOC_DAY_DU=(8,22)` | ✅ `True` |
| 2 | `ngay_hom_qua()` theo giờ VN (00h30 · 08h30 · 09h30 · 23h30 ngày 01/10) | ✅ đều ra `2026-09-30` |
| 3 | Trước 09:00 thì không làm gì | ✅ `(False, 'chua toi 9h')` |
| 4 | Chạy THẬT cho ngày hôm qua | ✅ `(True, 'da ghi so ngay 2026-09-30')` |
| 5 | Bản ghi ghi ra | ✅ `moc=8`, `day_du=True`, `so_camp=6` |
| 6 | Chạy lần hai | ✅ `(False, '2026-09-30 da co ban ghi tron ngay')` — **không giẫm chân báo cáo** |
| 7 | Đã có bản ghi KHÔNG trọn ngày (mốc 17) | ✅ vẫn ghi, nâng lên `moc=8`, `day_du=True` |
| 8 | `compute_stats` ném lỗi | ✅ `(False, 'loi khi ghi so: RuntimeError: ...')` — **không làm chết agent** |
| 9 | `lich_su.lay_mot_ngay(path, ngay)` nhận `date` | ✅ nhận trực tiếp, không cần đổi thành chuỗi |

### Đối chiếu với sổ THẬT trong repo (ngày 30/09/2026)

| Chỉ số | Sổ repo (ghi lúc 08:00) | Agent ghi (10:43) | |
|---|---|---|---|
| `msg` | 62 | 62 | **KHỚP** |
| `purchase` | 25 | 25 | **KHỚP** |
| `payment` | 25 | 25 | **KHỚP** |
| `spend` | 6.719.831 | 6.746.301 | lệch **+26.470đ (0,4%)** |

### Không phát hiện lỗi trong kế hoạch — nhưng phát hiện một điều PHẢI ghi lại

**Meta vẫn "chốt số" thêm sau khi báo cáo 8h đã ghi.** Cùng một ngày 30/09: lúc 08:00 chi tiêu là
6.719.831đ, tới 10:43 thành 6.746.301đ — **tăng 26.470đ**. Số lượt mua **không đổi**.

⇒ Hai hệ quả:

1. **Chạy song song vẫn an toàn:** agent **chỉ ghi khi thiếu**, nên **không bao giờ ghi đè** bản của
   báo cáo ⇒ không có chuyện hai sổ đá nhau.
2. **Sau này khi tắt báo cáo**, sổ do agent ghi sẽ **sát thực tế hơn** (lấy muộn hơn, Meta đã chốt
   xong). Đây là điều **tốt**, nhưng phải nói trước để Đại không bất ngờ khi thấy số lệch nhẹ so với
   trí nhớ.

### Kết luận dựng thử

**Kế hoạch đứng vững, không phải sửa gì.** Đã sẵn sàng thi công khi Đại duyệt.

