# Kế hoạch thi công — Giai đoạn 5: Tự xử lý lỗi

> **For agentic workers:** REQUIRED SUB-SKILL: Use subagent-driven-development (recommended) or executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Hệ thống tự xử lý được những lỗi có thể tự xử lý (Meta chặn tạm → tự chờ rồi thử lại; số liệu trông sai → cảnh báo thay vì gửi báo cáo gây hiểu lầm), **không làm phiền Đại** bằng những tin nhắn lặp lại vô ích, và **nói thật** về giới hạn không vượt được: token Meta phải do người thật lấy lại.

**Architecture:** Bốn thay đổi nhỏ, không thay đổi kiến trúc:
1. `report.api_get` — lùi dần khi Meta chặn tạm, và **phân loại lỗi tạm thời / vĩnh viễn** để trả về mã thoát khác nhau.
2. `bat_thuong.py` (mới) — ba điều kiện bất thường của bản thiết kế mục 7.3, thuần đọc `logs/lich-su.json`.
3. `report.canh_bao_han_token` — hai mức nhắc thay vì một, cộng **lệnh hỏi hạn token qua bot** (không tốn lượt AI).
4. `nguoi_truc` — đọc mã thoát để **không thử lại lỗi vĩnh viễn**, và không gửi cùng một tin cảnh báo nhiều lần trong 12 giờ.

**Tech Stack:** Python 3.13 thuần, chỉ thư viện chuẩn (`json`, `urllib`, `unittest`). Kiểm thử **không gọi mạng**.

**Spec:** `docs/superpowers/specs/2026-09-28-nguoi-truc-ai-agent-design.md` (mục 7 bảng xử lý lỗi, 7.1, 7.3, 9.2 điều 4 và 6, 11)

---

## Cập nhật khi thi công (29/09/2026) — ĐÃ XONG

**Đã thi công xong 5/5 task. `392/392` kiểm thử đạt** (trước GĐ5 là 285). Bộ kiểm thử chạy
**không gọi mạng**, không tốn lượt AI.

**Hai lỗi thật của kế hoạch, do chính bước dựng thử bắt được:**

**Lỗi 1 — điều kiện (3) báo động sai khi thiếu dữ liệu (nặng).** Điều kiện "mọi chỉ số đều bằng 0"
được viết là `all(_so(tong.get(k)) == 0 ...)`. Với `stats = {}` hoặc `stats = None`, **mọi phép đọc
đều ra 0**, nên hàm kết luận "mọi chỉ số đều bằng 0" và chèn cảnh báo ⚠️ vào một báo cáo hoàn toàn
bình thường. Bài kiểm thử `test_stats_rong_khong_nem_loi` bắt được ngay lần chạy đầu.
**Đã sửa:** chỉ kết luận khi thật sự nhận đủ **cả 7 chỉ số**; thiếu một chỉ số nào thì trả về rỗng.

**Lỗi 2 — chống thử lại làm hệ thống lùi về gửi báo cáo CŨ (nặng).** Kế hoạch viết
`chon_moc_can_gui(..., da_gui | moc_hong_vinh_vien, ...)` — tức coi mốc hỏng vĩnh viễn như "đã gửi".
Hệ quả: mốc 12h hỏng vì token chết thì mốc 12h bị loại khỏi danh sách chờ, và hàm chọn mốc **lùi về
mốc 8h** rồi gửi báo cáo 8h — **đúng cái lỗi mà Giai đoạn 2 đã có công chữa**. Bài kiểm thử
`test_loi_vinh_vien_thi_KHONG_thu_lai` bắt được (`[12, 8] != [12]`).
**Đã sửa:** không gộp vào `da_gui`; thay bằng chặn ngay trong `canh_moc` — nếu mốc được chọn nằm
trong `moc_hong_vinh_vien` thì thoát, **không gửi và cũng không lùi về mốc cũ hơn**.

**Ba chỗ khác kế hoạch (nhỏ hơn, đều là sửa cho đúng):**

1. **`bat_thuong` phải chặn cả trường hợp thiếu chỉ số**, không chỉ `stats` rỗng — thêm điều kiện
   "đủ cả 7 chỉ số" thay vì chỉ kiểm `isinstance(tong, dict)`.
2. **Nhiệt kế nhật ký: bỏ qua mốc bị ghi lại mỗi 30 giây.** `canh_moc` ghi một dòng "bỏ qua mốc Xh"
   **mỗi vòng lặp 30 giây** khi có mốc cũ chưa gửi — một ngày sinh ~2.880 dòng vô ích vào chính file
   Đại mở đầu tiên khi có sự cố. Đã thêm `da_bao_bo_qua`: mỗi mốc chỉ báo một lần.
3. **Làm tròn XUỐNG khi hiện số ngày còn lại.** Token còn 44,75 ngày mà ghi "45 ngày" là **nói thừa**
   thời gian còn lại. Với một hạn chốt thì phải nói thiếu, không được nói thừa.

**Kiểm chứng trên máy thật, sau khi thi công:**

| Phép kiểm | Kết quả |
|---|---|
| `python -m unittest discover -s tests -t .` trong repo thật | **392/392 đạt**, không gọi mạng |
| `chay-kiem-thu.bat` | Đã cập nhật số bài 285 → 392, vẫn đúng kiểu xuống dòng CRLF |
| `bat_thuong.kiem_tra` trên `logs/lich-su.json` **THẬT** (2 ngày) | Trả `[]` — đúng, vì chưa đủ 7 ngày |
| `doc_han_token_chi_tiet` gọi Meta **THẬT** | 44,75 ngày · hết hạn ` 08:15` (giờ máy) |
| `canh_bao_han_token` với token **THẬT** ở cả 3 mốc 8h/12h/17h | Không nhắc gì — đúng, vì còn 44 ngày |
| Lệnh `token` qua `tra_loi_tin_nhan` với dữ liệu **THẬT** | Trả đủ máy, số ngày, mốc hết hạn, việc cần làm |
| Lệnh `token` có gọi AI không | **Không** — 0 lượt AI |
| `phan_loai_loi` với 4 mã thật (190, 17, 80004, 10) | `vinh_vien` · `tam_thoi` · `tam_thoi` · `vinh_vien` |
| Chống lặp cảnh báo qua 4 mốc thời gian | Gửi → bỏ qua → bỏ qua → gửi lại sau 12 giờ |
| `report.py --mock 12` đầu-cuối (Meta + AI THẬT) | Báo cáo ra đủ, dashboard tạo được, **mã thoát 0** |
| `nguoi_truc.py --gui-ngay 12 --thu` (tiến trình con THẬT) | In `DA GUI`, **mã thoát 0** — đường ống mã thoát đúng |

> 📌 Ghi chú: trong lần chạy `--mock` cuối cùng, Gemini đang **quá tải (503 / hết thời gian chờ)** nên
> phần NHẬN ĐỊNH thiếu và báo cáo có ghi chú lý do. **Đó là hành vi đúng** của cơ chế suy giảm êm đã
> làm từ Giai đoạn 3, không phải lỗi của giai đoạn này.

---

## Kết quả kiểm chứng TRƯỚC KHI viết kế hoạch (29/09/2026)

Bản thiết kế mục 7.1 ghi rõ phần **tự gia hạn token** là *"việc thử nghiệm đầu tiên của kế hoạch, làm trước khi hứa bất cứ điều gì"* và *"chưa thử lần nào"*. Đã thử ngay hôm nay, bằng chìa khoá thật của Đại, trước khi viết một dòng kế hoạch.

### Kết quả: **KHÔNG tự gia hạn được**

Gọi `GET /v21.0/oauth/access_token` với `grant_type=fb_exchange_token` (đúng cách Meta mô tả):

| Phép đo | Kết quả |
|---|---|
| Token hiện tại còn sống | 44.76 ngày |
| Meta trả về token mới? | **CÓ** — một chuỗi khác hẳn token cũ |
| Hạn của token mới (lần 1) | `2026-11-13 01:15:07 UTC` |
| Hạn của token mới (lần 2) | `2026-11-13 01:15:07 UTC` |
| Hạn của token cũ | `2026-11-13 01:15:07 UTC` |
| **Chênh lệch** | **+0 giây, cả hai lần** |

Nghĩa là: Meta **đổi chuỗi token** nhưng **giữ nguyên đồng hồ 60 ngày**. Đổi bao nhiêu lần cũng vậy. Đây là hành vi đúng theo tài liệu Meta: `fb_exchange_token` có tác dụng biến token **ngắn hạn (1–2 giờ)** thành token **dài hạn (60 ngày)**; khi đưa vào một token **đã dài hạn** thì Meta trả lại đúng phiên đó, không reset hạn.

> ⚠️ **Hệ quả cho kế hoạch:** hạng mục "tự gia hạn token" trong bản thiết kế **phải bị bỏ**. Không phải vì code khó, mà vì Meta không cho. Hứa tính năng này là hứa sai.
>
> Phep thu nay **khong thu hoi token cu** — token dang dung van con nguyen gia tri (da kiem lai bang `debug_token` sau khi thu).

### Vậy Giai đoạn 5 làm gì cho token?

Thay vì một tính năng không tồn tại, làm hai việc có thật:

1. **Nhắc sớm hơn và đúng mức.** Hiện tại chỉ có một ngưỡng 7 ngày, và nó hiện ở **mọi** báo cáo (3 tin/ngày × 7 ngày = 21 tin giống nhau). Sửa thành hai mức: từ **30 ngày** nhắc nhẹ một lần mỗi ngày ở báo cáo mốc sáng (để Đại còn kịp xếp thời gian), dưới **7 ngày** nhắc ở mọi báo cáo.
2. **Lệnh hỏi hạn token qua bot.** Đại nhắn `token` → bot trả lời còn bao nhiêu ngày, hết hạn ngày nào, cần làm gì. **Không tốn lượt AI.** Đây là thứ biến cảnh báo thụ động thành thứ Đại chủ động kiểm được.

### Một đường khác CHƯA thử, ghi lại để sau này cân nhắc

**Token của "System User" trong Business Manager** — loại token này có tuỳ chọn không hết hạn, và đúng là dùng được cho `ads_read`. Nhưng phải tạo bằng tay trong giao diện Business Manager và gán quyền cho tài khoản quảng cáo; **chưa thử, không hứa**. Ghi lại ở `HUONG-DAN-DIEN-TOKEN.md` như một hướng nghiên cứu sau, kèm câu "chưa kiểm chứng".

---

## Phạm vi: 5 task

| # | Task | Giá trị |
|---|---|---|
| 1 | `api_get` lùi dần + phân loại lỗi + mã thoát | Meta chặn tạm thì tự chờ, không làm phiền Đại |
| 2 | `bat_thuong.py` — ba điều kiện bất thường | Bắt được token chết / bộ lọc hỏng trước khi Đại tin số sai |
| 3 | Cảnh báo hạn token hai mức + lệnh `token` qua bot | Đại chủ động kiểm được, nhắc sớm hơn 3 tuần |
| 4 | Người trực: không thử lại lỗi vĩnh viễn + chống tin cảnh báo trùng | Token chết: 9 tin/ngày → 1 tin/ngày |
| 5 | Cập nhật tài liệu | Người sau không thử lại việc đã chứng minh không được |

---

## Task 1 — `api_get` lùi dần và phân loại lỗi

**Vấn đề thật của code hiện tại (`report.py` dòng 307–327):** khi Meta trả mã 17 hoặc 80004, vòng lặp `continue` **thử lại ngay lập tức, không chờ giây nào**. Ba lần gọi liên tiếp trong vòng vài phần nghìn giây — đúng lúc Meta đang chặn vì quá nhiều yêu cầu. Cách này gần như chắc chắn thất bại cả ba lần.

**File:** `report.py` (sửa)

### 1.1. Thêm hằng số và hàm phân loại

Thêm `import time` vào đầu file (hiện chưa có).

```python
# Ma loi Meta TAM THOI - thu lai duoc, phai CHO roi moi thu.
# 17 va 80004 da gap that; 4, 32, 613 la cac ma chan vi qua nhieu yeu cau
# khac cua Meta (app / page / endpoint).
MA_LOI_META_TAM_THOI = (4, 17, 32, 613, 80004)

# Ma loi Meta VINH VIEN - thu lai chi ton thoi gian, phai bao ngay.
# 190 = token het han / khong hop le (kem ma con 463, 467). Day la ma hay gap
# nhat va la ly do chinh khien giai doan nay phai lam.
# 10, 200, 272 = thieu quyen. 100 = tham so sai. 803 = tai khoan khong ton tai.
MA_LOI_META_VINH_VIEN = (10, 100, 102, 190, 200, 272, 463, 467, 803)

# Thoi gian CHO (giay) truoc lan thu lai thu nhat va thu hai. LUY TIEN:
# Meta chan vi qua nhieu yeu cau thi cho ngan khong co tac dung.
CHO_TRUOC_KHI_THU_LAI = (5, 15)

# Ma thoat cua report.py. Nguoi truc doc ma nay de biet co nen thu lai khong.
MA_THOAT_OK = 0
MA_THOAT_TAM_THOI = 1
MA_THOAT_VINH_VIEN = 2
```

```python
def mo_ta_loi_meta(err):
    """Chuoi loi de doc, KEM MA LOI - de con phan loai duoc tam thoi / vinh vien.

    Truoc day chi tra ve `err['message']`, nen khong co cach nao biet loi do co
    thu lai duoc hay khong.
    """
    err = err or {}
    msg = err.get("message", "loi khong ro")
    ma = err.get("code")
    if ma is None:
        return f"Loi lay du lieu Meta: {msg}"
    return f"Loi lay du lieu Meta (ma {ma}): {msg}"


def doc_ma_loi(chuoi_loi):
    """Boc ma loi Meta ra khoi chuoi loi. Khong doc duoc -> None."""
    import re
    m = re.search(r"\(ma (-?\d+)\)", str(chuoi_loi or ""))
    return int(m.group(1)) if m else None


def phan_loai_loi(chuoi_loi):
    """Tra ve 'tam_thoi' hoac 'vinh_vien'.

    Mac dinh tra ve 'tam_thoi' khi khong ro: thu lai mot lan nua la vo hai,
    con tu bo mot loi that su thi bao cao im lang khong gui - te hon nhieu.
    """
    ma = doc_ma_loi(chuoi_loi)
    if ma in MA_LOI_META_VINH_VIEN:
        return "vinh_vien"
    if ma in MA_LOI_META_TAM_THOI:
        return "tam_thoi"

    low = str(chuoi_loi or "").lower()
    for tu in ("expired", "session has expired", "invalid oauth",
               "khong hop le", "thieu quyen", "permission"):
        if tu in low:
            return "vinh_vien"
    return "tam_thoi"
```

### 1.2. Sửa `api_get`

```python
def api_get(path, params, ngu_fn=None):
    """Goi Meta Graph API. Tra ve (du_lieu, loi).

    Loi TAM THOI (Meta chan vi qua nhieu yeu cau) thi CHO roi thu lai, cho lau
    dan: CHO_TRUOC_KHI_THU_LAI. Truoc day vong lap thu lai NGAY LAP TUC, khong
    cho giay nao - dung luc Meta dang chan vi qua nhieu yeu cau thi thu lai
    ngay chi ton them mot lan goi nua.

    `ngu_fn` tiem duoc de kiem thu khong phai ngu that.
    """
    ngu = ngu_fn or time.sleep
    url = f"{GRAPH}/{path}?" + urllib.parse.urlencode(params)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            try:
                err = json.loads(body).get("error", {})
            except Exception:
                err = {"message": f"HTTP {e.code}"}
            if err.get("code") in MA_LOI_META_TAM_THOI and attempt < 2:
                ngu(CHO_TRUOC_KHI_THU_LAI[attempt])
                continue
            return None, err
        except Exception as e:
            if attempt < 2:
                ngu(CHO_TRUOC_KHI_THU_LAI[attempt])
                continue
            return None, {"message": str(e)}
    return None, {"message": "Khong the ket noi sau 3 lan thu"}
```

> ⚠️ **Bẫy đã biết:** tham số `err` khi vào `MA_LOI_META_TAM_THOI` phải là **số nguyên**. Meta trả `code` dạng số, nhưng `json.loads` có thể cho `"17"` nếu Meta đổi kiểu. So sánh `err.get("code") in (4, 17, ...)` với `"17"` là **False** ⇒ mất tính năng lùi dần mà không ai biết. Phải chuẩn hoá:
> ```python
> def _ma_nguyen(v):
>     """Meta co the tra ma loi dang so hoac chuoi. Chuan hoa ve so nguyen."""
>     try:
>         return int(v)
>     except (ValueError, TypeError):
>         return None
> ```
> rồi dùng `if _ma_nguyen(err.get("code")) in MA_LOI_META_TAM_THOI and attempt < 2:`.

### 1.3. `compute_stats` dùng `mo_ta_loi_meta`

Sửa dòng 553:

```python
    rows, err = fetch_insights(env, since, until)
    if err:
        return None, mo_ta_loi_meta(err)
```

### 1.4. `main()` trả mã thoát theo loại lỗi

Sửa khối dòng 902–908:

```python
    stats, err = compute_stats(env, since, until)
    if err:
        print(f"LOI: {err}")
        log(f"THAT BAI - moc {slot}h: {err}")
        loai = phan_loai_loi(err)
        if args.mock is None and not args.dry:
            send_error_alert(env, err)
        log(f"LOI {loai} - moc {slot}h"
            + (" (Nguoi truc se thu lai)" if loai == "tam_thoi"
               else " (Nguoi truc KHONG thu lai)"))
        sys.exit(MA_THOAT_TAM_THOI if loai == "tam_thoi" else MA_THOAT_VINH_VIEN)
```

---

## Task 2 — `bat_thuong.py`: ba điều kiện bất thường

**File:** `lich_su.py` (thêm một hàm nhỏ) và `bat_thuong.py` (mới)

### 2.1. `lich_su.cua_so_truoc` — tránh chép lại phép tính ngày

`lay_ky_truoc` đang tự tính khoảng ngày. `bat_thuong.py` cũng cần **đúng khoảng đó**. Chép lại phép tính ở hai nơi thì sớm muộn hai nơi lệch nhau.

```python
def cua_so_truoc(ngay, so_ngay):
    """Khoang `so_ngay` ngay NGAY TRUOC `ngay`. Tra (tu, den) dang 'YYYY-MM-DD'.

    Ngay sai dinh dang -> (None, None), khong nem loi.
    """
    try:
        d = datetime.strptime(_chuan_hoa_ngay(ngay), "%Y-%m-%d").date()
    except ValueError:
        return None, None
    return ((d - timedelta(days=so_ngay)).strftime("%Y-%m-%d"),
            (d - timedelta(days=1)).strftime("%Y-%m-%d"))
```

và `lay_ky_truoc` viết lại phần cuối cho gọn:

```python
def lay_ky_truoc(path, ngay, so_ngay):
    """Tra ve tong hop `so_ngay` ngay NGAY TRUOC `ngay` (khong tinh chinh ngay do)."""
    tu, den = cua_so_truoc(ngay, so_ngay)
    if tu is None:
        return {"tong": _tong_rong(), "so_ngay": 0}
    return lay_khoang(path, tu, den)
```

### 2.2. `bat_thuong.py` (mới)

```python
"""
PHAT HIEN SO LIEU BAT THUONG
=============================
Ba dieu kien duy nhat duoc coi la bat thuong (ban thiet ke muc 7.3). Co tinh
KHONG them dieu kien nao khac: mot canh bao sai lam Dai mat long tin vao ca
nhung canh bao dung.

  (1) Chi tieu vot   : chi tieu > 3 lan muc trung binh 7 ngay truoc do.
  (2) Chi ma khong co ket qua: chi tieu > 0, luot mua = 0, trong khi 7 ngay
      truoc do trung binh van co luot mua.
  (3) Tat ca deu bang 0: moi chi so = 0, trong khi 7 ngay truoc do NGAY NAO
      cung co chi tieu -> dau hieu token hoac bo loc hong.

Can it nhat 7 ngay lich su moi bat kiem tra. Chua du thi BO QUA, khong canh
bao - canh bao "bat thuong" khi chua co gi de so sanh la vo nghia.

Hai dieu kien (1) va (2) CHI ap dung cho bao cao TRON mot ngay. Ly do: bao cao
moc 12h, 17h chi la MOT PHAN cua ngay (so tich luy tu 0h), dem so nua ngay so
voi trung binh ngay day du thi luon thay "thap bat thuong" - sai hoan toan.
Dieu kien (3) ap dung cho moi moc: moi chi so bang 0 thi du la moc nao cung la
dau hieu hong.

Khong bao gio tu y chan bao cao. Chi them mot dong canh bao o dau.
"""
from datetime import datetime, timedelta

import lich_su

# So ngay lich su toi thieu moi duoc phep ket luan.
SO_NGAY_LICH_SU_TOI_THIEU = 7

# Chi tieu ky nay lon hon bao nhieu lan muc trung binh thi coi la vot.
HE_SO_CHI_TIEU_VOT = 3.0

CAC_CHI_SO = ("spend", "msg", "contact", "order", "purchase", "payment", "comment")


def _so(v):
    """Doi ve so thuc. Gia tri la khong doi duoc -> 0."""
    try:
        return float(v or 0)
    except (ValueError, TypeError):
        return 0.0


def _tien(v):
    """20319895 -> '20.319.895'."""
    return f"{int(round(_so(v))):,}".replace(",", ".")


def kiem_tra(stats, duong_dan_lich_su, ngay, tron_ngay=False):
    """Tra ve DANH SACH LY DO (chuoi tieng Viet). Rong = binh thuong.

    KHONG BAO GIO nem loi: moi truc trac deu tra ve danh sach rong.
    """
    try:
        tong = (stats or {}).get("totals") or {}
    except AttributeError:
        return []

    tu, den = lich_su.cua_so_truoc(ngay, SO_NGAY_LICH_SU_TOI_THIEU)
    if tu is None:
        return []

    try:
        truoc = lich_su.lay_khoang(duong_dan_lich_su, tu, den)
        data = lich_su.doc(duong_dan_lich_su)
    except Exception:
        return []

    so_ngay = int(truoc.get("so_ngay", 0) or 0)
    if so_ngay < SO_NGAY_LICH_SU_TOI_THIEU:
        return []

    tong_truoc = truoc.get("tong") or {}
    tb_spend = _so(tong_truoc.get("spend")) / so_ngay
    tb_purchase = _so(tong_truoc.get("purchase")) / so_ngay

    spend = _so(tong.get("spend"))
    purchase = _so(tong.get("purchase"))

    ly_do = []

    # (1) Chi tieu vot
    if tron_ngay and tb_spend > 0 and spend > HE_SO_CHI_TIEU_VOT * tb_spend:
        ly_do.append(
            f"chi tiêu {_tien(spend)} đồng, cao hơn {HE_SO_CHI_TIEU_VOT:.0f} lần "
            f"mức trung bình {_tien(tb_spend)} đồng/ngày của {so_ngay} ngày trước đó"
        )

    # (2) Chi ma khong co ket qua
    if tron_ngay and spend > 0 and purchase == 0 and tb_purchase > 0:
        ly_do.append(
            f"có chi tiêu {_tien(spend)} đồng nhưng 0 lượt mua, trong khi "
            f"{so_ngay} ngày trước đó trung bình có {tb_purchase:.1f} lượt mua/ngày"
        )

    # (3) Tat ca deu bang 0
    if spend == 0 and all(_so(tong.get(k)) == 0 for k in CAC_CHI_SO):
        so_ngay_co_chi_tieu = 0
        for k in sorted(data):
            if tu <= k <= den and _so((data[k].get("tong") or {}).get("spend")) > 0:
                so_ngay_co_chi_tieu += 1
        if so_ngay_co_chi_tieu >= so_ngay:
            ly_do.append(
                f"mọi chỉ số đều bằng 0, trong khi {so_ngay} ngày trước đó "
                f"ngày nào cũng có chi tiêu"
            )

    return ly_do


def canh_bao(danh_sach_ly_do):
    """Dong canh bao dat o DAU bao cao. Khong co ly do -> chuoi rong."""
    if not danh_sach_ly_do:
        return ""
    return (
        "⚠️ Số liệu kỳ này trông bất thường: "
        + "; ".join(danh_sach_ly_do)
        + ". Nên kiểm tra lại trước khi tin.\n"
    )
```

### 2.3. Nối vào `report.main()`

Thêm `import bat_thuong` vào đầu `report.py`. Sau khối AI, trước `build_report` (dòng 939):

```python
    # --- Canh bao SO LIEU BAT THUONG (muc 7.3) ---
    # Dat SAU khi da luu lich su: cua so 7 ngay la 7 ngay TRUOC ky bao cao,
    # nen ban ghi vua luu khong lam nhieu ket qua.
    try:
        ly_do_bt = bat_thuong.kiem_tra(
            stats, LOG_DIR / "lich-su.json", until, tron_ngay
        )
    except Exception as e:
        ly_do_bt = []
        log(f"Khong kiem duoc so bat thuong: {e}")
    if ly_do_bt:
        log(f"CANH BAO so bat thuong: {'; '.join(ly_do_bt)}")
```

và sửa khối dòng 941–945 thành:

```python
    # --- Canh bao SOM neu token Meta sap het han ---
    # Dat LEN DAU bao cao de de thay, khong bi lan vao cuoi tin nhan.
    canh_bao_token = canh_bao_han_token(env, slot, danh_sach_moc)
    if canh_bao_token:
        report = canh_bao_token + "\n" + report
    canh_bao_bt = bat_thuong.canh_bao(ly_do_bt)
    if canh_bao_bt:
        report = canh_bao_bt + report
```

**Thứ tự có chủ ý:** cảnh báo token lên trên cùng (nghiêm trọng hơn, và Đại phải làm việc bằng tay), rồi tới cảnh báo số bất thường, rồi mới tới báo cáo.

---

## Task 3 — Cảnh báo hạn token hai mức + lệnh `token` qua bot

### 3.1. `report.doc_han_token_chi_tiet` — lấy cả MỐC hết hạn

Hiện `doc_han_token` chỉ trả về số ngày, không đủ để nói "hết hạn ngày nào".

```python
def doc_han_token_chi_tiet(env):
    """Hoi Meta xem token con song bao lau. Tra ve (so_ngay, het_han, loi).

    so_ngay = None  -> token khong bao gio het han (het_han = None).
    so_ngay = 0.0   -> token da het han / khong hop le.
    het_han         -> datetime theo GIO MAY, hoac None neu khong xac dinh.
    """
    token = env.get("META_ADS_ACCESS_TOKEN", "").strip()
    app_id = env.get("META_APP_ID", "").strip()
    app_secret = env.get("META_APP_SECRET", "").strip()

    if not token or not app_id or not app_secret:
        return None, None, "thieu META_APP_ID hoac META_APP_SECRET trong .env"

    data, err = api_get("debug_token", {
        "input_token": token,
        "access_token": f"{app_id}|{app_secret}",
    })
    if err:
        return None, None, err.get("message", "loi khong ro")

    d = data.get("data", {})
    if not d.get("is_valid"):
        return 0.0, None, None

    expires_at = d.get("expires_at", 0)
    if not expires_at:
        return None, None, None

    het_han = datetime.fromtimestamp(expires_at, tz=timezone.utc).astimezone()
    con_lai = (datetime.fromtimestamp(expires_at, tz=timezone.utc)
               - datetime.now(timezone.utc))
    return con_lai.total_seconds() / 86400, het_han, None


def doc_han_token(env):
    """Nhu doc_han_token_chi_tiet nhung chi tra ve (so_ngay, loi).

    Giu lai de khong pha vo phan da chay duoc.
    """
    so_ngay, _, loi = doc_han_token_chi_tiet(env)
    return so_ngay, loi
```

### 3.2. `canh_bao_han_token` — hai mức

```python
# Nhac nhe tu muc nay: con kip xep thoi gian lam token moi, ma chua gap.
NGUONG_NHAC_NHE_NGAY = 30
```

```python
def canh_bao_han_token(env, slot=None, danh_sach_moc=None):
    """Doan text canh bao neu token Meta sap het han, hoac '' neu khong can.

    HAI MUC:
      - tu NGUONG_NHAC_NHE_NGAY (30) den NGUONG_CANH_BAO_NGAY (7): nhac nhe,
        CHI o bao cao moc sang - mot tin moi ngay, khong lam roi 3 tin/ngay.
      - duoi NGUONG_CANH_BAO_NGAY (7): nhac o MOI bao cao (nhu truoc day).
      - da het han: bao do.

    `slot=None` (cach goi cu) nghia la hien o moi bao cao - giu nguyen hanh vi
    cu cho ai goi ham nay ma khong truyen moc gio.

    Ham nay KHONG BAO GIO lam hong bao cao: moi loi deu bi nuot va ghi nhat ky.
    """
    try:
        so_ngay, het_han, loi = doc_han_token_chi_tiet(env)
    except Exception as e:
        log(f"Khong kiem duoc han token Meta: {e}")
        return ""

    if loi:
        log(f"Khong kiem duoc han token Meta: {loi}")
        return ""

    if so_ngay is None:
        return ""

    if so_ngay <= 0:
        return (
            "🔴 CẢNH BÁO TOKEN META\n"
            "Token đã HẾT HẠN. Số liệu trong báo cáo này có thể không đầy đủ.\n"
            "→ Lấy token mới theo file HUONG-DAN-DIEN-TOKEN.md\n"
            "→ Hệ thống KHÔNG tự gia hạn được (đã thử 29/09/2026).\n"
        )

    het_han_txt = f" (hết hạn {het_han.strftime('%d/%m/%Y')})" if het_han else ""

    if so_ngay >= NGUONG_NHAC_NHE_NGAY:
        return ""

    if so_ngay < 1:
        con_lai_txt = f"{so_ngay * 24:.0f} giờ"
    else:
        con_lai_txt = f"{so_ngay:.0f} ngày"

    if so_ngay < NGUONG_CANH_BAO_NGAY:
        return (
            f"🟡 CẢNH BÁO TOKEN META — chỉ còn sống {con_lai_txt}{het_han_txt}\n"
            "→ Nên lấy token mới sớm, đừng chờ tới lúc nó chết.\n"
            "→ Làm theo HUONG-DAN-DIEN-TOKEN.md (Bước A → E)\n"
            "→ Chỉ lấy token mới ở MỘT máy, rồi copy file .env sang máy kia bằng USB.\n"
            "→ Hệ thống KHÔNG tự gia hạn được (đã thử 29/09/2026).\n"
        )

    # Tu 7 den 30 ngay: nhac nhe, chi o bao cao moc sang.
    if slot is None or danh_sach_moc is None or slot != moc_sang(danh_sach_moc):
        return ""
    return (
        f"🔵 NHẮC TOKEN META — còn sống {con_lai_txt}{het_han_txt}\n"
        "→ Chưa gấp. Đây là nhắc trước để Đại xếp thời gian lấy token mới.\n"
        "→ Khi nào rảnh thì làm theo HUONG-DAN-DIEN-TOKEN.md (Bước A → E).\n"
    )
```

### 3.3. Lệnh `token` qua bot (`nguoi_truc.py`)

```python
TOKEN_HET_HAN = (
    "🔴 TOKEN META ĐÃ HẾT HẠN\n"
    "Hệ thống không lấy được số liệu nữa.\n"
    "→ Lấy token mới theo file HUONG-DAN-DIEN-TOKEN.md (Bước A → E).\n"
    "→ Hệ thống KHÔNG tự gia hạn được — Meta không cho (đã thử 29/09/2026)."
)


def tra_loi_han_token(env, now=None, doc_han_fn=None):
    """Cau tra loi cho lenh nhanh `token`. KHONG ton luot AI.

    `doc_han_fn` tiem duoc: neu khong thi kiem thu se goi mang that toi Meta.
    """
    now = now or datetime.now()
    doc_han_fn = doc_han_fn or report.doc_han_token_chi_tiet
    try:
        so_ngay, het_han, loi = doc_han_fn(env)
    except Exception as e:
        so_ngay, het_han, loi = None, None, f"loi khong luong truoc: {e}"

    if loi:
        return (
            "Chưa kiểm tra được hạn token Meta.\n"
            f"Lý do: {loi}\n"
            "→ Thử lại sau vài phút. Nếu vẫn vậy thì xem logs\\baocao.log."
        )

    may = env.get("REPORT_ACCOUNT_NAME", "?")

    if so_ngay is None:
        return f"🔑 TOKEN META\n- Máy: {may}\n- Token không bao giờ hết hạn."

    if so_ngay <= 0:
        return TOKEN_HET_HAN

    if so_ngay < 1:
        con_lai_txt = f"{so_ngay * 24:.0f} giờ"
    else:
        con_lai_txt = f"{so_ngay:.0f} ngày"

    dong = [f"🔑 TOKEN META", f"- Máy: {may}", f"- Còn sống: {con_lai_txt}"]
    if het_han:
        dong.append(f"- Hết hạn: {het_han.strftime('%d/%m/%Y lúc %H:%M')}")

    if so_ngay < report.NGUONG_CANH_BAO_NGAY:
        dong.append("- Việc cần làm: LẤY TOKEN MỚI NGAY.")
        dong.append("→ Làm theo HUONG-DAN-DIEN-TOKEN.md (Bước A → E).")
        dong.append("→ Chỉ lấy ở MỘT máy, rồi copy .env sang máy kia bằng USB.")
    elif so_ngay < report.NGUONG_NHAC_NHE_NGAY:
        dong.append("- Việc cần làm: chưa gấp, nhưng nên xếp thời gian lấy token mới.")
    else:
        dong.append("- Việc cần làm: chưa cần làm gì.")

    dong.append("- Hệ thống KHÔNG tự gia hạn được — Meta không cho (đã thử 29/09/2026).")
    return "\n".join(dong)
```

Nối vào `tra_loi_tin_nhan`, **sau** nhánh "còn sống không?" và **trước** nhánh AI:

```python
    if "token" in chuan:
        return tra_loi_han_token(env, now=now, doc_han_fn=doc_han_fn)
```

và thêm tham số `doc_han_fn=None` vào chữ ký `tra_loi_tin_nhan` (cạnh `tra_loi_ai_fn=None`), truyền xuống từ `NguoiTruc` qua một tham số `doc_han_fn` mới trong `__init__`.

---

## Task 4 — Người trực: không thử lại lỗi vĩnh viễn, không lặp tin cảnh báo

### 4.1. `gui_bao_cao` trả MÃ THOÁT thay vì True/False

**Vấn đề thật:** token chết thì `report.py` thất bại, Người trực thử lại 3 lần cách nhau 5 phút, mỗi lần `report.py` lại gửi một tin cảnh báo lỗi. Ba mốc × ba lần = **9 tin cảnh báo giống nhau mỗi ngày**, trong khi việc cần làm chỉ có một.

Sửa chữ ký và phần thân (dòng 138–180):

```python
def gui_bao_cao(moc, che_do_thu=False):
    """Goi report.py o TIEN TRINH RIENG de gui bao cao moc `moc`.

    Tra ve MA THOAT cua report.py:
        0 = thanh cong (hoac khong co gi de gui)
        1 = loi TAM THOI  -> Nguoi truc nen thu lai
        2 = loi VINH VIEN -> Nguoi truc KHONG thu lai (vi du token da chet)

    Chay o tien trinh rieng vi: report.py co loi thi Nguoi truc van song, va
    phan tinh tien trong report.py khong bi dung toi.
    """
    lenh = [sys.executable, str(GOC / "report.py"), "--slot", str(moc)]
    if che_do_thu:
        lenh.append("--dry")
    ...
    except subprocess.TimeoutExpired:
        report.log(...)
        return report.MA_THOAT_TAM_THOI
    except Exception as e:
        report.log(...)
        return report.MA_THOAT_TAM_THOI

    if kq.returncode == 0:
        return report.MA_THOAT_OK
    if kq.returncode == report.MA_THOAT_VINH_VIEN:
        report.log(f"NGUOI TRUC: report.py moc {moc}h loi VINH VIEN - khong thu lai")
        return report.MA_THOAT_VINH_VIEN
    duoi = (kq.stderr or "")[-300:]
    report.log(f"NGUOI TRUC: report.py moc {moc}h thoat voi ma {kq.returncode}: {duoi}")
    return report.MA_THOAT_TAM_THOI
```

> ⚠️ **Bẫy đã biết:** mã thoát **1** hiện nay là "lỗi bất kỳ", và có rất nhiều đường trả về 1 mà **không phải** lỗi Meta tạm thời: không đọc được `.env`, không gửi được Telegram, `--slot` không hợp lệ. Những trường hợp đó **không được** coi là vĩnh viễn — chỉ đúng mã 2 mới là vĩnh viễn. Vì vậy `gui_bao_cao` phải kiểm `kq.returncode == report.MA_THOAT_VINH_VIEN` (so sánh đúng bằng 2), **không** dùng `!= 0`.

### 4.2. `canh_moc` xử lý ba mã

```python
    def canh_moc(self, now):
        """Kiem tra xem co moc nao can gui khong, va gui neu can."""
        moc, bo_qua = chon_moc_can_gui(
            now, self.danh_sach_moc,
            self._da_gui_hom_nay(now) | self.moc_hong_vinh_vien,
            self.trang_thai,
        )
        for m in bo_qua:
            report.log(
                f"NGUOI TRUC: bo qua moc {m}h - da co bao cao moi hon chua gui"
            )
        if moc is None:
            return

        report.log(f"NGUOI TRUC: toi moc {moc}h - bat dau gui")
        self.trang_thai.ghi_lan_thu(moc, now)
        ma = self.gui_bao_cao(moc)

        if ma == report.MA_THOAT_OK:
            self.da_xu_ly.add(moc)
            self.lan_gui_cuoi = now
            report.log(f"NGUOI TRUC: da gui xong moc {moc}h")
        elif ma == report.MA_THOAT_VINH_VIEN:
            self.moc_hong_vinh_vien.add(moc)
            report.log(
                f"NGUOI TRUC: moc {moc}h loi VINH VIEN (token chet / thieu quyen) "
                "- KHONG thu lai. Sua xong thi moc sau se gui binh thuong."
            )
        else:
            so_lan = self.trang_thai.so_lan.get(moc, 0)
            report.log(
                f"NGUOI TRUC: gui moc {moc}h THAT BAI (lan thu {so_lan}/{MAX_LAN_THU_MOI_MOC})"
            )
```

thêm vào `__init__`:

```python
        # Cac moc hong VINH VIEN trong phien nay (token chet...). Thu lai chi ton
        # thoi gian va ban them tin canh bao cho Dai.
        self.moc_hong_vinh_vien = set()
```

và thêm `doc_han_fn=None` vào `__init__`, truyền xuống `tra_loi_tin_nhan`.

### 4.3. Chống gửi cùng một tin cảnh báo nhiều lần (`report.py`)

```python
# Nho lan cuoi da gui canh bao cho TUNG LOAI loi, de khong ban lai cung mot
# tin nhieu lan. Truoc day token chet gay 9 tin canh bao giong nhau moi ngay
# (3 moc x 3 lan thu), trong khi viec can lam chi co MOT.
CANH_BAO_FILE = LOG_DIR / "canh_bao.json"
CHO_GIUA_HAI_CANH_BAO = 12 * 3600
```

```python
def _doc_canh_bao():
    try:
        if CANH_BAO_FILE.exists():
            d = json.loads(CANH_BAO_FILE.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                return d
    except Exception:
        pass
    return {}


def _ghi_canh_bao(loai, ts):
    try:
        LOG_DIR.mkdir(exist_ok=True)
        d = _doc_canh_bao()
        d[loai] = ts
        CANH_BAO_FILE.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        log(f"Khong ghi duoc so canh bao: {e}")


def loai_canh_bao(chuoi_loi):
    """Khoa nhan dang loai loi, de biet hai lan loi co PHAI CUNG MOT THU khong."""
    ma = doc_ma_loi(chuoi_loi)
    return f"{phan_loai_loi(chuoi_loi)}:{ma if ma is not None else 'khong-ro'}"


def nen_gui_canh_bao(loai, now=None, doc_fn=None, ghi_fn=None):
    """True neu nen gui canh bao loai nay. Chan lap lai trong CHO_GIUA_HAI_CANH_BAO.

    Loi DAU TIEN cua mot loai luon duoc gui. Chi nhung lan lap lai moi bi chan,
    nen Dai khong bao gio bi bo quen.
    """
    now = now or datetime.now()
    doc_fn = doc_fn or _doc_canh_bao
    ghi_fn = ghi_fn or _ghi_canh_bao
    try:
        cu = (doc_fn() or {}).get(loai)
        if cu:
            truoc = datetime.strptime(str(cu), "%Y-%m-%d %H:%M:%S")
            if (now - truoc).total_seconds() < CHO_GIUA_HAI_CANH_BAO:
                return False
    except Exception:
        pass
    ghi_fn(loai, now.strftime("%Y-%m-%d %H:%M:%S"))
    return True
```

Thêm vào đầu `send_error_alert`:

```python
def send_error_alert(env, err):
    """Gui canh bao loi vao Telegram — de loi khong bao gio xay ra im lang."""
    loai = loai_canh_bao(err)
    if not nen_gui_canh_bao(loai):
        log(f"Bo qua canh bao lap lai ({loai}) - da gui trong 12 gio qua")
        return
    msg = (...)
```

### 4.4. `main()` của `nguoi_truc.py`

Đường `--gui-ngay` giờ nhận mã thoát:

```python
        ma = gui_bao_cao(args.gui_ngay, che_do_thu=args.thu)
        if ma == report.MA_THOAT_OK:
            print("DA GUI")
        elif ma == report.MA_THOAT_VINH_VIEN:
            print("GUI THAT BAI - LOI VINH VIEN (token chet / thieu quyen)")
        else:
            print("GUI THAT BAI - LOI TAM THOI")
        return ma
```

---

## Task 5 — Cập nhật tài liệu

| File | Sửa gì |
|---|---|
| `HANDOFF.md` | Trạng thái GĐ5; mốc push mới; bảng file thêm `bat_thuong.py`, `logs/canh_bao.json`; mục **"Token Meta KHÔNG tự gia hạn được"** kèm bảng bằng chứng; bảng mã thoát 0/1/2 |
| `README.md` | Mục cảnh báo token (hai mức); lệnh `token` cho bot; mục xử lý sự cố thêm "báo cáo có dòng ⚠️ bất thường nghĩa là gì" |
| `HUONG-DAN-DIEN-TOKEN.md` | Thêm mục **"Vì sao hệ thống không tự gia hạn token được"** (bảng 2 lần thử, +0 giây) + hướng **chưa kiểm chứng**: token System User của Business Manager |
| `.env.example` | Không thêm khoá mới (ngưỡng vẫn để trong code như `NGUONG_CANH_BAO_NGAY`) |

---

## Kiểm chứng trước khi giao (bắt buộc)

Trước khi giao kế hoạch này cho Đại, **dựng thử toàn bộ code trong một thư mục tạm**: chép `report.py`, `lich_su.py`, `nguoi_truc.py`, `cong_cu.py`, `ai.py`, `dashboard.py` và thư mục `tests/` sang thư mục tạm, áp đúng các sửa đổi ở trên, viết `bat_thuong.py` + kiểm thử mới, rồi chạy.

| # | Phép kiểm | Kết quả mong đợi |
|---|---|---|
| 1 | Toàn bộ kiểm thử trong thư mục tạm | Đạt hết, **không gọi mạng** |
| 2 | `api_get` khi Meta trả mã 17 ba lần | Chờ 5s rồi 15s, tổng 2 lần chờ — **đo được bằng hàm ngu giả** |
| 3 | `api_get` khi Meta trả mã 190 | Trả lỗi **ngay**, không chờ giây nào |
| 4 | `api_get` khi Meta trả `"code": "17"` (chuỗi) | Vẫn nhận ra là tạm thời (bẫy ở mục 1.2) |
| 5 | `phan_loai_loi` với 9 mã vĩnh viễn và 5 mã tạm thời | Đúng hết |
| 6 | `bat_thuong.kiem_tra` với 6 ngày lịch sử | Trả `[]` — chưa đủ 7 ngày |
| 7 | `bat_thuong.kiem_tra` với 7 ngày, chi tiêu gấp 4 lần trung bình, báo cáo trọn ngày | Trả 1 lý do "chi tiêu vọt" |
| 8 | Cùng dữ liệu nhưng báo cáo **một phần** ngày | Trả `[]` — không so nửa ngày với ngày đầy đủ |
| 9 | Mọi chỉ số = 0, 7 ngày trước ngày nào cũng có chi tiêu | Trả 1 lý do "mọi chỉ số đều bằng 0" |
| 10 | Mọi chỉ số = 0 nhưng 7 ngày trước có 1 ngày chi tiêu = 0 | Trả `[]` |
| 11 | `canh_bao_han_token` với 45 ngày / 20 ngày / 5 ngày / đã hết hạn, ở mốc 8h và mốc 17h | 45 → rỗng; 20 → chỉ ở 8h; 5 → cả 8h và 17h; hết hạn → báo đỏ |
| 12 | `tra_loi_han_token` với hàm đọc hạn giả | Chuỗi có đủ ngày, mốc hết hạn, việc cần làm; **không gọi mạng** |
| 13 | `gui_bao_cao` khi `report.py` thoát mã 2 | Trả 2; `canh_moc` gọi **đúng một lần**, mốc vào `moc_hong_vinh_vien` |
| 14 | `gui_bao_cao` khi `report.py` thoát mã 1 | Trả 1; `canh_moc` vẫn thử lại sau khoảng nghỉ (hành vi cũ giữ nguyên) |
| 15 | `nen_gui_canh_bao` gọi hai lần liền | Lần 1 `True`, lần 2 `False`; sau 12 giờ lại `True` |
| 16 | `nen_gui_canh_bao` với hai loại lỗi khác nhau | Cả hai đều `True` |
| 17 | `report.py --mock` sau khi sửa | Chạy hết, không gửi, không ghi sổ |
| 18 | `bat_thuong.kiem_tra` trên `logs/lich-su.json` THẬT của Đại (2 ngày) | Trả `[]` — đúng, vì chưa đủ 7 ngày |

Bốn phép kiểm quan trọng nhất là **2, 3, 4, 8**: chúng nhắm thẳng vào chỗ dễ làm sai mà lại không nhìn thấy được bằng mắt.

---

## Việc Đại phải làm sau khi giai đoạn này xong

Không có việc gì mới. Không phải bấm file `.bat` nào, không phải điền thêm khoá nào vào `.env`.

Chỉ hai việc nhỏ, khi nào rảnh:

1. **Nhắn thử bot một chữ `token`** để xem hạn token còn bao lâu — đây là phép thử sức khoẻ mới.
2. **Ghi vào lịch:** token máy nhà hết hạn **10/11/2026**, máy công ty ****. Từ 30 ngày trước đó bot sẽ bắt đầu nhắc.

---

## Rủi ro đã biết của giai đoạn này

| Rủi ro | Mức | Cách xử lý |
|---|---|---|
| Cảnh báo "số bất thường" báo sai làm Đại mất lòng tin | **Trung bình** | Chỉ 3 điều kiện của bản thiết kế, không thêm; cần đủ 7 ngày lịch sử; hai điều kiện dễ sai nhất chỉ áp dụng cho báo cáo trọn ngày |
| Chống lặp cảnh báo che mất một lỗi MỚI | Thấp | Khoá theo **loại + mã lỗi**; lỗi đầu tiên của mỗi loại luôn được gửi; mọi lần đều ghi `baocao.log` |
| Lùi dần làm `report.py` chạy lâu hơn | Thấp | Chờ tối đa 20 giây; Người trực cho tối đa 600 giây |
| Token vẫn phải làm tay | **Cao — không tránh được** | Đã chứng minh Meta không cho tự gia hạn. Bù lại bằng nhắc sớm 30 ngày + lệnh `token` để Đại tự kiểm |
