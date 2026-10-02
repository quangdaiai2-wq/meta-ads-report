"""Doc lenh cua Dai tren Telegram — HAM THUAN, khong phu thuoc gi.

Vi sao tach rieng file nay: ca `agent_xin_phep.py` (agent nac 2) va
`nguoi_truc.py` (tien trinh bao cao) deu can doc cung mot cu phap lenh. Neu de
chung trong `agent_xin_phep.py` thi `nguoi_truc` nhap vao no se thanh vong lap
nhap (agent_xin_phep da nhap nguoi_truc).

VI SAO `nguoi_truc` PHAI BIET CU PHAP NAY: hai tien trinh dung CHUNG mot bot
Telegram, ma `getUpdates` cua Telegram chi giao moi tin cho MOT nguoi goi —
ai xac nhan truoc thi nguoi kia khong bao gio thay tin do nua. Nen neu tien
trinh bao cao nhan duoc "tat <ma>" ma tra loi bang AI, thi agent se KHONG BAO
GIO nhan duoc lenh cua Dai, va tinh nang coi nhu hong trong im lang.
"""
import re
import unicodedata

DONG_Y = ("tat", "tat di", "dong y")
# Nut "Tat + ha ngan sach". Phai kiem TRUOC DONG_Y de chac chan khong bi lot
# vao "tat". (Thuc te `phan[:len(bx)] == bx` so khop CA TU, nen "tathns" khong
# khop "tat"; nhung cu de truoc cho an toan ve sau.)
DONG_Y_HA_NGAN_SACH = ("tathns",)
TU_CHOI = ("bo qua", "boqua", "thoi", "de sau", "khong")

# Hai nut tren TIN BAO LOI (Dai chot 02/10/2026):
#   quetlai:<ma>  -> xoa lenh bo qua, quay ve mac dinh (quet lai roi hoi lai)
#   boqua24:<ma>  -> khong xet nhom nay trong 24 gio
QUET_LAI = ("quetlai", "quet lai")
BO_QUA_24 = ("boqua24", "bo qua 24")

HOAN_TAC = ("batlai", "bat lai", "hoan tac", "undo")

# Lenh phai co dang: <dong tu> <cum so dai>  — vd "tắt 120250506886650509"
RE_LENH = re.compile(
    r"^(tat|tathns|quetlai|boqua24|bo qua|boqua|thoi|batlai|bat lai|hoan tac)\s+\d{6,}",
    re.IGNORECASE)


def bo_dau(s):
    """'TẮT' -> 'tat'. An toan voi moi dau tieng Viet."""
    if not isinstance(s, str):
        return ""
    s = s.replace("\u0111", "d").replace("\u0110", "D")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.lower().strip()


def la_lenh(text):
    """Tin nhan nay co trong nhu mot LENH cho agent khong.

    Dung de tien trinh bao cao biet ma chuyen tiep, KHONG tra loi bang AI.
    """
    if not isinstance(text, str):
        return False
    return bool(RE_LENH.match(bo_dau(text)))


def _tim_ma(phan):
    """Ma nhom = cum so dai cuoi cung trong tin. Khong co -> None."""
    for p in reversed(phan):
        if p.isdigit() and len(p) >= 6:
            return p
    return None


def la_hoan_tac(text):
    """Tin nay co phai lenh HOAN TAC (bat lai nhom da tat) khong."""
    if not isinstance(text, str):
        return False
    chu = bo_dau(text).replace("-", " ").replace("_", " ").replace(":", " ")
    phan = [p for p in chu.split() if p]
    for x in HOAN_TAC:
        bx = bo_dau(x).split()
        if bx and phan[:len(bx)] == bx:
            return True
    return False


def ma_trong_lenh(text):
    """Ma nhom nam trong tin. Khong co -> None."""
    if not isinstance(text, str):
        return None
    chu = bo_dau(text).replace("-", " ").replace("_", " ").replace(":", " ")
    return _tim_ma([p for p in chu.split() if p])


def doc_tra_loi(text, dang_cho):
    """Tra ve (ket_qua, ma).

    ket_qua:
      "dong_y"               — Dai dong y TAT nhom (giu nguyen ngan sach)
      "dong_y_ha_ngan_sach"  — Dai dong y TAT nhom + HA NGAN SACH
      "quet_lai"             — (nut tren tin bao loi) xoa lenh bo qua, quet lai
      "bo_qua_24h"           — (nut tren tin bao loi) khong xet nhom nay 24 gio
      "tu_choi"              — Dai noi bo qua
      "khong_khop"           — dung cu phap nhung ma nhom khac
      "khong_hieu"           — khong doc duoc
    """
    if not isinstance(text, str) or not isinstance(dang_cho, (list, tuple, set)):
        return "khong_hieu", None
    # Doi ca dau ":" vi du lieu cua NUT BAM co dang "tat:120250506886650509".
    # Nho vay mot ham doc duoc ca lenh go tay lan nut bam, khong phai viet hai bo.
    chu = bo_dau(text).replace("-", " ").replace("_", " ").replace(":", " ")
    phan = [p for p in chu.split() if p]
    if not phan:
        return "khong_hieu", None

    ma = _tim_ma(phan)

    # HOAN TAC phai kiem TRUOC "dong y", vi "bat lai" khac han "tat".
    for x in HOAN_TAC:
        bx = bo_dau(x).split()
        if bx and phan[:len(bx)] == bx:
            if ma is None:
                return "khong_hieu", None
            return ("hoan_tac", ma) if ma in dang_cho else ("khong_khop", ma)

    for x in TU_CHOI:
        bx = bo_dau(x).split()
        if bx and phan[:len(bx)] == bx:
            if ma is None:
                return "tu_choi", None
            return ("tu_choi", ma) if ma in dang_cho else ("khong_khop", ma)

    # KIEM TRUOC DONG_Y: nut "tat + ha ngan sach" tra ve ket qua rieng, de
    # agent biet co ha ngan sach hay khong.
    for x in DONG_Y_HA_NGAN_SACH:
        bx = bo_dau(x).split()
        if bx and phan[:len(bx)] == bx:
            if ma is None:
                return "khong_hieu", None
            return ("dong_y_ha_ngan_sach", ma) if ma in dang_cho else ("khong_khop", ma)

    # Hai nut tren TIN BAO LOI (Dai chot 02/10/2026).
    for x in QUET_LAI:
        bx = bo_dau(x).split()
        if bx and phan[:len(bx)] == bx:
            if ma is None:
                return "khong_hieu", None
            return ("quet_lai", ma) if ma in dang_cho else ("khong_khop", ma)

    for x in BO_QUA_24:
        bx = bo_dau(x).split()
        if bx and phan[:len(bx)] == bx:
            if ma is None:
                return "khong_hieu", None
            return ("bo_qua_24h", ma) if ma in dang_cho else ("khong_khop", ma)

    for x in DONG_Y:
        bx = bo_dau(x).split()
        if bx and phan[:len(bx)] == bx:
            if ma is None:
                return "khong_hieu", None
            return ("dong_y", ma) if ma in dang_cho else ("khong_khop", ma)

    return "khong_hieu", ma
