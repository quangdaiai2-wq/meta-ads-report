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
