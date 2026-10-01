"""NAC 2 — soan tin xin phep, doc cau tra loi cua Dai.

Phan DOC LENH nam o `lenh_telegram.py` (ham thuan, dung chung voi nguoi_truc.py).
File nay chi con phan NOI voi Telegram.

Dung lai ha tang Telegram da co trong nguoi_truc.py (gui_tin_nhan, lay_tin_moi,
tin_tu_dai, noi_dung_tin). Khong xay kenh moi.

Nguyen tac an toan quan trong nhat: IM LANG LA MAC DINH AN TOAN. Dai khong tra
loi, hoac tra loi khac cu phap, hoac tra loi sai ma nhom => KHONG LAM GI.
"""
import json

import nguoi_truc
from lenh_telegram import bo_dau, doc_tra_loi, la_lenh   # noqa: F401 (dung lai)

__all__ = ["bo_dau", "doc_tra_loi", "la_lenh", "soan_tin", "nut_bam",
           "gui_xin_phep", "sua_ket_qua", "quet_tra_loi"]


def nut_bam(ma):
    """Ban phim noi 2 nut cho tin xin phep. Tra ve chuoi JSON.

    Du lieu nut co dang "tat:<ma>" / "boqua:<ma>". Ham doc lenh
    (`lenh_telegram.doc_tra_loi`) da biet doi dau ":" thanh dau cach, nen mot
    ham doc duoc ca lenh go tay lan nut bam.
    """
    return json.dumps({"inline_keyboard": [[
        {"text": "\u2705 Tắt nhóm", "callback_data": f"tat:{ma}"},
        {"text": "\u23ed Bỏ qua", "callback_data": f"boqua:{ma}"},
    ]]}, ensure_ascii=False)


def soan_tin(de_xuat, ghi_chu=None):
    """Soan tin Telegram xin phep. Tra ve chuoi (rong neu de xuat hong).

    `ghi_chu`: them mot dong cuoi. Dung de noi ro dang o CHE DO TAP SU — neu
    khong, Dai tra loi "tat ..." roi khong thay gi xay ra se tuong he thong hong.
    """
    try:
        ten = de_xuat["doi_tuong"]["ten"]
        ma = de_xuat["doi_tuong"]["id"]
        ly_do = de_xuat.get("ly_do", "")
    except (KeyError, TypeError):
        return ""
    dong = [
        "\u26a0\ufe0f XIN PHÉP TẮT NHÓM",
        "",
        f"Nhóm: {ten}",
        ly_do,
        "",
        "Đề xuất: TẮT nhóm + hạ ngân sách về 27.000đ",
        "",
        "Trả lời:",
        f"  tắt {ma}",
        f"  bỏ qua {ma}",
    ]
    if ghi_chu:
        dong += ["", ghi_chu]
    return "\n".join(dong)


def nut_hoan_tac(ma):
    """Nut HOAN TAC gan vao tin bao ket qua. Tra ve chuoi JSON.

    Vi sao can: tat nham thi cai mat khong phai tien, ma la GIAI DOAN HOC cua
    Meta — nhom bi tat roi bat lai se hoc lai tu dau. Nen hoan tac phai la
    MOT LAN BAM, khong phai mo Trinh quan ly quang cao.
    """
    return json.dumps({"inline_keyboard": [[
        {"text": "\u21a9\ufe0f Bật lại nhóm này", "callback_data": f"batlai:{ma}"},
    ]]}, ensure_ascii=False)


def gui_xin_phep(env, de_xuat, ghi_chu=None):
    """Gui tin xin phep KEM 2 NUT BAM. Tra ve message_id (None neu loi).

    Tra ve message_id de sau nay SUA chinh tin do thanh ket qua, thay vi gui
    them tin moi (Dai chon 30/09/2026).
    """
    try:
        ma = de_xuat["doi_tuong"]["id"]
    except (KeyError, TypeError):
        return None
    text = soan_tin(de_xuat, ghi_chu)
    if not text:
        return None
    ket_qua, _ = nguoi_truc.gui_tin_nhan_day_du(env, text, nut_bam(ma))
    if not isinstance(ket_qua, dict):
        return None
    return ket_qua.get("message_id")


def sua_ket_qua(env, message_id, text, reply_markup=None):
    """Doi tin xin phep thanh ket qua. Tra ve True/False.

    Khong truyen `reply_markup` thi xoa nut. Truyen `nut_hoan_tac(ma)` thi de
    lai dung MOT nut hoan tac.
    """
    if message_id is None:
        return False
    return nguoi_truc.sua_tin_nhan(env, message_id, text, bo_nut=True,
                                   reply_markup=reply_markup)


def quet_tra_loi(ds_tin, dang_cho, chat_id_dai):
    """Loc cac tin TRA LOI cua Dai trong danh sach update cua Telegram.

    Tra ve danh sach dict: {ket_qua, ma, noi_dung}
    Chi nhan tin tu chinh chat_id cua Dai — day la hang rao bao mat.
    """
    ra = []
    if not isinstance(ds_tin, (list, tuple)):
        return ra
    for tin in ds_tin:
        if not nguoi_truc.tin_tu_dai(tin, chat_id_dai):
            continue
        noi_dung = nguoi_truc.noi_dung_tin(tin)
        if not noi_dung:
            continue
        ket_qua, ma = doc_tra_loi(noi_dung, dang_cho)
        ra.append({"ket_qua": ket_qua, "ma": ma, "noi_dung": noi_dung})
    return ra
