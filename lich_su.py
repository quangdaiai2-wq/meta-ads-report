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
