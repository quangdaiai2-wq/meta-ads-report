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
import os
import tempfile
import time
from datetime import date, datetime, timedelta
from pathlib import Path

# So ngay giu lai. Cu hon thi xoa cho gon.
SO_NGAY_GIU = 180

# Tham so cho khoa ghi file. Ba tien trinh chay bu co the ghi cung luc, nen
# phai co khoa. Cho toi da SO_LAN_THU_KHOA * KHOANG_CHO_KHOA ~ 2 giay.
KHOANG_CHO_KHOA = 0.05
SO_LAN_THU_KHOA = 40

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

    Chi giu lai cac ban ghi CO GIA TRI LA DICT. Mot gia tri kieu so
    (vi du {"2026-09-28": 5}) se lam ghi() nem AttributeError, va khi do
    lich su im lang khong bao gio duoc cap nhat nua.
    """
    try:
        path = Path(path)
        if not path.exists():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return {}
        return {k: v for k, v in data.items() if isinstance(v, dict)}
    except Exception:
        return {}


def _khoa(path):
    """Tao file khoa canh file lich su de ngan ghi chong nhau.

    Dung os.open voi O_CREAT | O_EXCL: chi MOT tien trinh tao duoc file khoa,
    cac tien trinh khac gap FileExistsError va phai cho roi thu lai.

    Neu cho mai van khong duoc (kha nang cao la lan chay truoc bi tat giua luc
    dang giu khoa, nen file khoa con sot lai), tra ve None va VAN GHI TIEP.
    Ghi duoc lich su quan trong hon la khoa cho that hoan hao: bo qua ghi moi
    la mat so lieu that su.
    """
    lock = path.with_name(path.name + ".lock")
    for _ in range(SO_LAN_THU_KHOA):
        try:
            fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return lock
        except FileExistsError:
            time.sleep(KHOANG_CHO_KHOA)
        except OSError:
            # Thu muc chua ton tai (hoac khong tao duoc khoa): bo qua khoa,
            # _ghi_nguyen_tu se tu tao thu muc.
            return None
    return None


def _mo_khoa(lock):
    """Xoa file khoa. Khong bao gio nem loi; lock la None thi khong lam gi."""
    if lock is None:
        return
    try:
        os.unlink(str(lock))
    except OSError:
        pass


def _ghi_nguyen_tu(path, data):
    """Ghi file theo kieu nguyen tu: ghi ra file tam roi doi ten.

    Neu tien trinh bi tat giua luc ghi, file chinh van nguyen ven (khong bi
    cat cut thanh file nua voi). os.replace la thao tac doi ten nen rat nhanh.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=str(path.parent), prefix=".lich-su-", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=1))
        os.replace(tmp, str(path))
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _tong_rong():
    return {k: (0.0 if k == "spend" else 0) for k in CAC_CHI_SO}


def _don_dep(data, hom_nay=None):
    """Xoa cac ban ghi cu hon SO_NGAY_GIU ngay.

    Dung <= de giu dung SO_NGAY_GIU ngay (tinh ca hom nay).
    """
    hom_nay = hom_nay or date.today()
    moc_cu = (hom_nay - timedelta(days=SO_NGAY_GIU)).strftime("%Y-%m-%d")
    for k in [k for k in data if k <= moc_cu]:
        del data[k]
    return data


def ghi(path, ngay, moc, stats):
    """Ghi so lieu mot lan chay vao lich su.

    ngay: ngay KET THUC cua ky bao cao (date hoac 'YYYY-MM-DD')
    moc:  moc gio bao cao, vi du 8
    stats: dict do compute_stats() tra ve

    Quy tac ghi de: ban day du luon thang ban khong day du.
    Neu da co ban day du ma ban moi chi mot phan thi BO QUA (tra ve False).

    Ca doc lan ghi deu nam trong mot khoa file, va ghi theo kieu nguyen tu,
    de nhieu tien trinh chay bu cung luc khong lam mat du lieu.
    """
    path = Path(path)
    ngay = _chuan_hoa_ngay(ngay)
    lock = _khoa(path)
    try:
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

        _ghi_nguyen_tu(path, data)
        return True
    finally:
        _mo_khoa(lock)


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
    """Tra ve tong hop `so_ngay` ngay NGAY TRUOC `ngay` (khong tinh chinh ngay do).

    Ngay sai dinh dang thi tra ve tong rong, khong nem loi — giong cac ham
    khac trong module nay.
    """
    ngay = _chuan_hoa_ngay(ngay)
    try:
        d = datetime.strptime(ngay, "%Y-%m-%d").date()
    except ValueError:
        return {"tong": _tong_rong(), "so_ngay": 0}
    den = (d - timedelta(days=1)).strftime("%Y-%m-%d")
    tu = (d - timedelta(days=so_ngay)).strftime("%Y-%m-%d")
    return lay_khoang(path, tu, den)
