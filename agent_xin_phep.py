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
           "gui_xin_phep", "sua_ket_qua", "quet_tra_loi", "dong_doi_tuong",
           "nut_loi", "soan_tin_loi", "gui_tin_loi"]


def nut_bam(ma):
    """Ban phim cho tin xin phep. Tra ve chuoi JSON.

    HAI lua chon tat (Dai chot 02/10/2026):
      - "Tat nhom"              : tat adset + tat quang cao + doi ten, GIU nguyen sach
      - "Tat + ha ngan sach"    : nhu tren, VA ha ngan sach ve 27.000d

    Vi sao de 2 lua chon: co lan Dai chi muon dung nhom lai de xem tinh hinh roi
    bat lai — ha ngan sach ve san roi bat lai thi phai nang lai tu dau.

    Du lieu nut co dang "tat:<ma>" / "tathns:<ma>" / "boqua:<ma>". Ham doc lenh
    (`lenh_telegram.doc_tra_loi`) da biet doi dau ":" thanh dau cach, nen mot
    ham doc duoc ca lenh go tay lan nut bam.
    """
    return json.dumps({"inline_keyboard": [
        [
            {"text": "\u23f8 Tắt nhóm", "callback_data": f"tat:{ma}"},
            {"text": "\u23f8\U0001f4b0 Tắt + hạ ngân sách", "callback_data": f"tathns:{ma}"},
        ],
        [
            {"text": "\u23ed Bỏ qua", "callback_data": f"boqua:{ma}"},
        ],
    ]}, ensure_ascii=False)


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
        *dong_doi_tuong(de_xuat),
        f"Nhóm: {ten}",
        ly_do,
        "",
        "Chọn một trong hai:",
        "  \u23f8 Tắt nhóm            — giữ nguyên ngân sách",
        "  \u23f8\U0001f4b0 Tắt + hạ ngân sách  — hạ về 27.000đ",
        "",
        "Hoặc gõ tay:",
        f"  tắt {ma}",
        f"  bỏ qua {ma}",
    ]
    if ghi_chu:
        dong += ["", ghi_chu]
    return "\n".join(dong)


def nut_loi(ma):
    """Ban phim cho TIN BAO LOI. Tra ve chuoi JSON.

    Dai chot 02/10/2026: khi Meta tu choi thi KHONG tat gi ca, bao loi roi hoi
    Dai muon lam gi tiep:
      - "Tiep tuc quet lai lan sau" : xoa lenh bo qua, de lan quet sau hoi lai
      - "Bo qua 24h"                : khong xet nhom nay trong 24 gio
    """
    return json.dumps({"inline_keyboard": [[
        {"text": "\U0001f501 Tiếp tục quét lại lần sau", "callback_data": f"quetlai:{ma}"},
        {"text": "\u23f8 Bỏ qua 24h", "callback_data": f"boqua24:{ma}"},
    ]]}, ensure_ascii=False)


def soan_tin_loi(ban_ghi, ket_qua, nguyen_nhan=None, chi_tiet=None):
    """Soan tin bao LOI khi Meta tu choi. Tra ve chuoi.

    Dai yeu cau: "phai bao loi nay la loi do dau". Nen tin nay co ba phan:
      1. Loi Meta tra ve NGUYEN VAN (khong cat bot)
      2. Doan nguyen nhan bang tieng nguoi thuong — CHI khi doan duoc
      3. Noi ro agent KHONG tat gi ca
    """
    dt = (ban_ghi or {}).get("doi_tuong") or {}
    dong = [
        "\u274c KHÔNG TẮT ĐƯỢC NHÓM",
        "",
        *dong_doi_tuong(ban_ghi),
        f"Nhóm: {dt.get('ten')}",
        f"Lỗi Meta trả về: {ket_qua}",
    ]
    if nguyen_nhan:
        dong.append(f"Có thể do: {nguyen_nhan}")
    else:
        dong.append("Chưa rõ nguyên nhân — xem nguyên văn lỗi ở trên.")
    dong += [
        "",
        "Agent KHÔNG tắt gì cả (nhóm và quảng cáo vẫn nguyên).",
        "Đại chọn bên dưới:",
        "  \U0001f501 Tiếp tục quét lại lần sau",
        "  \u23f8 Bỏ qua 24h",
    ]
    return "\n".join(dong)


def gui_tin_loi(env, ban_ghi, ket_qua, nguyen_nhan=None):
    """Gui tin bao loi KEM 2 NUT. Tra ve message_id (None neu loi)."""
    ma = str(((ban_ghi or {}).get("doi_tuong") or {}).get("id") or "")
    if not ma:
        return None
    text = soan_tin_loi(ban_ghi, ket_qua, nguyen_nhan)
    ket_qua_gui, _ = nguoi_truc.gui_tin_nhan_day_du(env, text, nut_loi(ma))
    if not isinstance(ket_qua_gui, dict):
        return None
    return ket_qua_gui.get("message_id")


def dong_doi_tuong(de_xuat):
    """Dong hien ID CHIEN DICH (Dai chot 02/10/2026).

    Dai tra tren Meta bang ID chien dich de hon ID nhom. Neu khong doc duoc
    campaign_id thi tra ve danh sach rong — tin nhan van gui duoc binh thuong.
    """
    cid = ((de_xuat.get("doi_tuong") or {}).get("campaign_id") or "").strip()
    return [f"Chiến dịch: {cid}"] if cid else []


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
