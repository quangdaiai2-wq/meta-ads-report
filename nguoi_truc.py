"""
NGUOI TRUC - tien trinh thuong tru cua bao cao Meta Ads
=======================================================
Thay ba lich Windows roi rac bang MOT tien trinh chay suot khi may bat.

Hai viec:
  1. Canh moc gio, goi report.py o TIEN TRINH RIENG de gui bao cao dung moc.
  2. Nghe tin nhan Telegram, chi tra loi tin tu chat_id cua Dai.

Ly do thay lich Windows: lich khong biet gi ve nhau. Khi may ngu qua nhieu
moc, Windows cho ca ba lich chay bu CUNG LUC va moi lich tu doan moc gan nhat
-> gui ra nhieu bao cao trung nhau. Nguoi truc biet ro lich cua chinh no, nen
chi gui DUNG MOT bao cao bu, cho moc gan nhat bi lo.

Cach dung:
    python nguoi_truc.py                 # chay that
    python nguoi_truc.py --thu           # chay toan bo luong, KHONG gui gi
    python nguoi_truc.py --gui-ngay 17   # gui ngay moc 17h roi thoat
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

import ai
import cong_cu
import report

GOC = Path(__file__).parent

# Vong lap kiem tra dong ho moi 30 giay (theo thiet ke muc 5.1).
NHIP_GIAC = 30

# Ghi mot dong nhip tim moi 60 vong (~30 phut).
# Thiet ke muc 5.1 noi "moi vong", nhung 30 giay mot dong thi mot ngay co
# ~2.880 dong, lam ngap logs/baocao.log - chinh file Dai mo dau tien khi co
# su co. Lenh "con song khong?" moi la phep thu suc khoe chinh.
NHIP_TIM_MOI_VONG = 60

# Mot moc duoc thu toi da 3 lan trong ngay, cach nhau it nhat 5 phut.
# Muc dich: loi mang thoang qua thi van kip gui, nhung token chet han thi
# khong ban tin canh bao moi 30 giay.
MAX_LAN_THU_MOI_MOC = 3
KHOANG_NGHI_GIUA_HAI_LAN_THU = 300

# Thoi gian toi da cho report.py chay xong (giay).
CHO_REPORT_TOI_DA = 600

# Danh sach moc mac dinh khi .env khong ghi gi.
MOC_MAC_DINH = [8, 12, 17, 22]

# Cau tra loi khi lop AI khong tra loi duoc. Phai noi RO LY DO, khong im lang:
# Dai khong biet ky thuat, mot tin nhan im lang se lam Dai tuong bot hong.
TRA_LOI_AI_LOI = (
    "Tôi chưa trả lời được câu hỏi này.\n"
    "\n"
    "Lý do: {ly_do}\n"
    "\n"
    "Đại thử lại sau vài phút. Nếu vẫn không được thì xem file "
    "logs\\baocao.log để biết chi tiết."
)


TOKEN_HET_HAN = (
    "🔴 TOKEN META ĐÃ HẾT HẠN\n"
    "Hệ thống không lấy được số liệu nữa.\n"
    "→ Lấy token mới theo file HUONG-DAN-DIEN-TOKEN.md (Bước A → E).\n"
    "→ Hệ thống KHÔNG tự gia hạn được — Meta không cho (đã thử 29/09/2026)."
)


def moc_da_toi(now, danh_sach_moc):
    """Cac moc gio da di qua tinh den thoi diem `now`, trong NGAY HOM NAY."""
    return [m for m in danh_sach_moc if now.hour >= m]


class TrangThaiThu:
    """Nho so lan thu va lan thu cuoi cho tung moc, TRONG NGAY hom nay.

    Sang ngay moi thi dem lai tu dau. Khong can luu ra file: tien trinh
    thuong tru chay lien tuc, va khi no khoi dong lai thi thu lai la dung.
    """

    def __init__(self):
        self.ngay = None
        self.so_lan = {}
        self.lan_cuoi = {}

    def _kiem_tra_ngay(self, now):
        ngay = now.strftime("%Y-%m-%d")
        if ngay != self.ngay:
            self.ngay = ngay
            self.so_lan = {}
            self.lan_cuoi = {}

    def duoc_thu(self, moc, now):
        """True neu moc nay con luot thu va da qua khoang nghi."""
        self._kiem_tra_ngay(now)
        if self.so_lan.get(moc, 0) >= MAX_LAN_THU_MOI_MOC:
            return False
        cuoi = self.lan_cuoi.get(moc)
        if cuoi is not None:
            if (now - cuoi).total_seconds() < KHOANG_NGHI_GIUA_HAI_LAN_THU:
                return False
        return True

    def ghi_lan_thu(self, moc, now):
        self._kiem_tra_ngay(now)
        self.so_lan[moc] = self.so_lan.get(moc, 0) + 1
        self.lan_cuoi[moc] = now


def chon_moc_can_gui(now, danh_sach_moc, da_gui, trang_thai):
    """Chon moc gio can gui bao cao trong vong nay.

    Tra ve (moc_can_gui, danh_sach_moc_bo_qua).
    moc_can_gui la None nghia la khong gui gi.

    QUY TAC: chi gui MOT bao cao cho moc GAN NHAT da di qua ma chua gui.
    Cac moc cu hon bi bo qua va ghi nhat ky.

    Day chinh la cho chua loi gui trung: truoc day ba lich Windows chay bu
    cung luc, moi lich tu doan moc, nen gui ra ba bao cao trung nhau.
    """
    chua_gui = [m for m in moc_da_toi(now, danh_sach_moc) if m not in da_gui]
    if not chua_gui:
        return None, []

    can_gui = max(chua_gui)
    bo_qua = [m for m in chua_gui if m != can_gui]

    if not trang_thai.duoc_thu(can_gui, now):
        # Het luot thu cho moc gan nhat thi KHONG lui ve moc cu hon: bao cao
        # cua moc cu hon la bao cao cu, gui di se gay hieu nham.
        return None, bo_qua

    return can_gui, bo_qua


def gui_bao_cao(moc, che_do_thu=False):
    """Goi report.py o TIEN TRINH RIENG de gui bao cao moc `moc`.

    Tra ve MA THOAT cua report.py:
        report.MA_THOAT_OK (0)         = thanh cong
        report.MA_THOAT_TAM_THOI (1)   = loi TAM THOI  -> nen thu lai
        report.MA_THOAT_VINH_VIEN (2)  = loi VINH VIEN -> KHONG thu lai
                                         (vi du token Meta da chet)

    Chay o tien trinh rieng vi: report.py co loi thi Nguoi truc van song, va
    phan tinh tien trong report.py khong bi dung toi.
    """
    lenh = [sys.executable, str(GOC / "report.py"), "--slot", str(moc)]
    if che_do_thu:
        lenh.append("--dry")

    # BAT BUOC chi dinh UTF-8. Khong co bon thiet lap nay thi tien trinh con
    # khong co console se lay bang ma theo locale cua Windows (cp1252), va bao
    # cao co dau tieng Viet lam no CHET voi UnicodeEncodeError => bao cao
    # khong duoc gui. Da xay ra that tu 17h ngay 28/09/2026.
    moi_truong = dict(os.environ)
    moi_truong["PYTHONIOENCODING"] = "utf-8"
    try:
        kq = subprocess.run(
            lenh,
            cwd=str(GOC),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=moi_truong,
            timeout=CHO_REPORT_TOI_DA,
        )
    except subprocess.TimeoutExpired:
        report.log(
            f"NGUOI TRUC: report.py moc {moc}h qua thoi gian cho {CHO_REPORT_TOI_DA} giay"
        )
        return report.MA_THOAT_TAM_THOI
    except Exception as e:
        report.log(f"NGUOI TRUC: khong chay duoc report.py moc {moc}h: {e}")
        return report.MA_THOAT_TAM_THOI

    if kq.returncode == report.MA_THOAT_OK:
        return report.MA_THOAT_OK
    # So sanh DUNG BANG 2, khong dung "khac 0". Rat nhieu duong khac trong
    # report.py thoat voi ma 1 ma KHONG phai loi Meta vinh vien (khong doc duoc
    # .env, khong gui duoc Telegram, --slot sai). Coi chung la vinh vien thi
    # bao cao se im lang khong bao gio gui lai.
    if kq.returncode == report.MA_THOAT_VINH_VIEN:
        report.log(
            f"NGUOI TRUC: report.py moc {moc}h loi VINH VIEN (ma 2) - khong thu lai"
        )
        return report.MA_THOAT_VINH_VIEN

    duoi = (kq.stderr or "")[-300:]
    report.log(f"NGUOI TRUC: report.py moc {moc}h thoat voi ma {kq.returncode}: {duoi}")
    return report.MA_THOAT_TAM_THOI


def goi_telegram(env, method, params):
    """Goi mot API cua Telegram. Tra ve (ket_qua, loi)."""
    token = (env or {}).get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        return None, "thieu TELEGRAM_BOT_TOKEN trong .env"
    url = f"https://api.telegram.org/bot{token}/{method}"
    try:
        data = urllib.parse.urlencode(params).encode("utf-8")
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=30) as resp:
            j = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return None, f"HTTP {e.code}"
    except Exception as e:
        return None, str(e)

    if not j.get("ok"):
        return None, j.get("description", "loi khong ro")
    return j.get("result"), None


def tham_so_lay_tin(offset):
    """Tham so cho getUpdates. offset=None nghia la lay moi tin chua xac nhan."""
    params = {"timeout": 0, "allowed_updates": json.dumps(["message"])}
    if offset is not None:
        params["offset"] = offset
    return params


def offset_moi_tu_ket_qua(ds):
    """Offset cho lan goi tiep theo. Khong co tin nao thi tra ve None."""
    if not ds:
        return None
    return max(u["update_id"] for u in ds) + 1


def lay_tin_moi(env, offset):
    """Lay cac tin nhan moi chua xu ly. Tra ve (danh_sach, loi)."""
    return goi_telegram(env, "getUpdates", tham_so_lay_tin(offset))


def xa_tin_ton_dong(env):
    """Bo qua het tin nhan cu con ton dong. Tra ve (offset_moi, loi).

    Dung offset=-1: Telegram tra ve tin CUOI CUNG va danh dau moi tin cu hon
    la da nhan. Khong lam buoc nay thi lan chay dau tien bot se tra loi mot
    loat tin nhan cu cua Dai.

    Khong co tin nao ton dong thi offset_moi la None - dieu do dung, vi lan
    goi tiep theo khong truyen offset se chi nhan tin moi.
    """
    ket_qua, loi = goi_telegram(env, "getUpdates", {"offset": -1, "timeout": 0})
    if loi:
        return None, loi
    return offset_moi_tu_ket_qua(ket_qua or []), None


def tin_tu_dai(tin, chat_id_dai):
    """True neu tin nhan nay do chinh Dai gui.

    Hang rao bao mat quan trong nhat: nguoi la tim ra bot co the hoi duoc so
    lieu quang cao neu thieu phep kiem tra nay.
    """
    try:
        chat_id = tin["message"]["chat"]["id"]
    except (KeyError, TypeError):
        return False
    return str(chat_id) == str(chat_id_dai).strip()


def noi_dung_tin(tin):
    """Lay phan chu cua tin nhan. Tin hong hoac tin khong phai chu -> ''."""
    try:
        return (tin["message"].get("text") or "").strip()
    except (KeyError, TypeError, AttributeError):
        return ""


def gui_tin_nhan(env, text):
    """Gui mot tin nhan ve Telegram cho Dai. Tra ve True/False."""
    chat_id = (env or {}).get("TELEGRAM_CHAT_ID", "").strip()
    if not chat_id:
        report.log("NGUOI TRUC: thieu TELEGRAM_CHAT_ID, khong gui duoc tin tra loi")
        return False
    _, loi = goi_telegram(env, "sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": True,
    })
    if loi:
        report.log(f"NGUOI TRUC: khong gui duoc tin tra loi: {loi}")
        return False
    return True


def _thoi_gian_da_chay(giay):
    """Doi so giay thanh chu de doc: '3 giờ 2 phút', '1 ngày 2 giờ'."""
    giay = int(giay)
    ngay, du = divmod(giay, 86400)
    gio, du = divmod(du, 3600)
    phut = du // 60
    if ngay:
        return f"{ngay} ngày {gio} giờ"
    if gio:
        return f"{gio} giờ {phut} phút"
    return f"{phut} phút"


def _moc_ke_tiep(now, danh_sach_moc, da_gui):
    """Chu mo ta moc gio ke tiep chua gui."""
    con_lai = [m for m in danh_sach_moc if m > now.hour and m not in da_gui]
    if con_lai:
        return f"{min(con_lai)}h hôm nay"
    return "ngày mai"


def _lay_so_hom_nay(env, ngay):
    """Goi Meta lay so lieu MOT ngay. Tra dict stats hoac None.

    Chi dung cho cau hoi can so HOM NAY, khi lich su chua kip ghi. Moi cau hoi
    toi da mot lan goi, vi goi Meta mat 15-30 giay (do duoc trong log).
    """
    try:
        stats, err = report.compute_stats(env, ngay, ngay)
        if err:
            report.log(f"NGUOI TRUC: khong lay duoc so hom nay tu Meta: {err}")
            return None
        return stats
    except Exception as e:
        report.log(f"NGUOI TRUC: loi khi lay so hom nay tu Meta: {e}")
        return None


def _tra_loi_bang_ai(cau_hoi, env, now):
    """Goi lop AI de tra loi cau hoi ve so lieu. Tra ve (chu, loi)."""
    duong_dan_ls = report.LOG_DIR / "lich-su.json"
    bo = cong_cu.BoCongCu(
        duong_dan=duong_dan_ls,
        lay_so_hom_nay_fn=lambda ngay: _lay_so_hom_nay(env, ngay),
        hom_nay=now.date(),
    )
    moc_tg = cong_cu.moc_thoi_gian(duong_dan_ls, hom_nay=now.date())
    return ai.tra_loi(cau_hoi, bo, env=env, moc_tg=moc_tg)


def tra_loi_han_token(env, now=None, doc_han_fn=None):
    """Cau tra loi cho lenh nhanh `token`. KHONG ton luot AI.

    Day la thay the cho tinh nang "tu gia han token" - da chung minh ngay
    29/09/2026 la Meta KHONG cho. Thay vi mot tinh nang khong ton tai, cho Dai
    mot lenh de TU KIEM TRA bat cu luc nao.

    `doc_han_fn` phai tiem duoc: neu khong thi kiem thu se goi mang that toi Meta.
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
            "→ Thử lại sau vài phút. Nếu vẫn vậy thì xem file logs\\baocao.log."
        )

    may = (env or {}).get("REPORT_ACCOUNT_NAME", "?")

    if so_ngay is None:
        return f"🔑 TOKEN META\n- Máy: {may}\n- Token không bao giờ hết hạn."

    if so_ngay <= 0:
        return TOKEN_HET_HAN

    # Duoi 1 ngay thi hien thi theo GIO, vi "con 0 ngay" doc rat kho hieu.
    # Lam TRON XUONG: con 44,7 ngay ma ghi "45 ngày" la noi THUA thoi gian con
    # lai - voi mot han chot thi phai noi thieu, khong duoc noi thua.
    if so_ngay < 1:
        con_lai_txt = f"{so_ngay * 24:.0f} giờ"
    else:
        con_lai_txt = f"{int(so_ngay)} ngày"

    dong = ["🔑 TOKEN META", f"- Máy: {may}", f"- Còn sống: {con_lai_txt}"]
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


def tra_loi_tin_nhan(cau_hoi, env, danh_sach_moc, bat_dau, lan_gui_cuoi, da_gui,
                     now=None, tra_loi_ai_fn=None, doc_han_fn=None):
    """Soan cau tra loi cho mot tin nhan tu Dai.

    Giai doan 2 tra loi cau hoi suc khoe. Giai doan 4 tra loi them cau hoi ve
    so lieu, bang cach goi lop AI (ai.tra_loi). Giai doan 5 tra loi them cau hoi
    ve han token.

    `tra_loi_ai_fn` va `doc_han_fn` phai tiem duoc: neu khong thi kiem thu se
    goi AI that / goi Meta that, vua hong phep kiem vua ton luot.
    """
    now = now or datetime.now()
    chuan = (cau_hoi or "").lower().strip()

    if any(tu in chuan for tu in (
        "còn sống", "con song", "sống không", "song khong",
        "còn chạy", "con chay", "alive",
    )):
        moc_txt = ", ".join(f"{m}h" for m in danh_sach_moc)
        da_gui_txt = ", ".join(f"{m}h" for m in sorted(da_gui)) or "chưa gửi mốc nào"
        lan_cuoi_txt = (
            lan_gui_cuoi.strftime("%H:%M ngày %d/%m")
            if lan_gui_cuoi else "chưa có trong phiên này"
        )
        return "\n".join([
            "✅ Người trực đang chạy.",
            f"- Máy: {env.get('REPORT_ACCOUNT_NAME', '?')}",
            f"- Đã chạy liên tục: {_thoi_gian_da_chay((now - bat_dau).total_seconds())}",
            f"- Mốc giờ của máy này: {moc_txt}",
            f"- Hôm nay đã gửi: {da_gui_txt}",
            f"- Lần gửi gần nhất: {lan_cuoi_txt}",
            f"- Mốc kế tiếp: {_moc_ke_tiep(now, danh_sach_moc, da_gui)}",
        ])

    # Cau hoi ve han token -> tra loi bang so da co, KHONG ton luot AI.
    # Dat truoc nhanh AI vi day la cau hoi ve suc khoe he thong, khong phai ve
    # so lieu quang cao.
    if "token" in chuan:
        return tra_loi_han_token(env, now=now, doc_han_fn=doc_han_fn)

    if not chuan:
        return "Tôi chưa thấy nội dung trong tin nhắn của Đại."

    # Cau hoi ve so lieu -> lop AI (Giai doan 4).
    if tra_loi_ai_fn is None:
        tra_loi_ai_fn = lambda c: _tra_loi_bang_ai(c, env, now)

    try:
        chu, loi = tra_loi_ai_fn(cau_hoi)
    except Exception as e:
        chu, loi = None, f"loi khong luong truoc: {e}"

    if chu:
        return chu
    return TRA_LOI_AI_LOI.format(ly_do=loi or "khong ro")


class NguoiTruc:
    """Tien trinh thuong tru.

    Cac tham so `*_fn` va `dong_ho` de kiem thu thay duoc phan that (dong ho,
    gui bao cao, gui tin, doc so da gui, goi Telegram). Khi chay that thi de
    trong.

    `xa_tin_fn` va `lay_tin_fn` bat buoc phai thay duoc: neu khong thi kiem thu
    `mot_vong()` se goi mang that toi Telegram.
    """

    def __init__(self, env, danh_sach_moc, che_do_thu=False,
                 gui_bao_cao_fn=None, gui_tin_fn=None,
                 doc_da_gui_fn=None, dong_ho=None,
                 xa_tin_fn=None, lay_tin_fn=None, tra_loi_ai_fn=None,
                 doc_han_fn=None):
        self.env = env or {}
        self.danh_sach_moc = list(danh_sach_moc) or list(MOC_MAC_DINH)
        self.che_do_thu = che_do_thu
        # Ham tra loi bang AI. Phai tiem duoc: neu khong thi kiem thu se goi AI
        # that (ton luot AI va phu thuoc mang).
        self.tra_loi_ai_fn = tra_loi_ai_fn
        # Ham doc han token Meta. Cung phai tiem duoc, cung ly do.
        self.doc_han_fn = doc_han_fn

        if gui_bao_cao_fn is None:
            def gui_bao_cao_fn(moc):
                return gui_bao_cao(moc, che_do_thu)
        if gui_tin_fn is None:
            def gui_tin_fn(text):
                return gui_tin_nhan(self.env, text)
        if doc_da_gui_fn is None:
            doc_da_gui_fn = report.ds_moc_da_gui
        if xa_tin_fn is None:
            def xa_tin_fn(env):
                return xa_tin_ton_dong(env)
        if lay_tin_fn is None:
            def lay_tin_fn(env, offset):
                return lay_tin_moi(env, offset)

        self.gui_bao_cao = gui_bao_cao_fn
        self.gui_tin = gui_tin_fn
        self.doc_da_gui = doc_da_gui_fn
        self.xa_tin = xa_tin_fn
        self.lay_tin = lay_tin_fn
        self.dong_ho = dong_ho or datetime.now

        self.trang_thai = TrangThaiThu()
        self.bat_dau = self.dong_ho()
        self.lan_gui_cuoi = None
        self.so_vong = 0
        # Cac moc da xu ly trong PHIEN nay. Can thiet vi che do --thu khong ghi
        # so gui ra file, va vi mot lan ghi so that bai khong duoc gay gui lap.
        self.da_xu_ly = set()
        # Cac moc hong VINH VIEN trong phien nay (token chet, thieu quyen...).
        # Thu lai chi ton thoi gian va ban them tin canh bao cho Dai.
        self.moc_hong_vinh_vien = set()
        # Cac moc da bao "bo qua" roi, de khong ghi nhat ky lap moi 30 giay.
        self.da_bao_bo_qua = set()
        self.da_xa_tin_ton_dong = False
        self.offset = None

    def _da_gui_hom_nay(self, now):
        """Tap hop cac moc da gui thanh cong hom nay, theo so tren dia."""
        try:
            return set(self.doc_da_gui(now.strftime("%Y-%m-%d"))) | self.da_xu_ly
        except Exception as e:
            report.log(f"NGUOI TRUC: khong doc duoc so da gui: {e}")
            return set(self.da_xu_ly)

    def canh_moc(self, now):
        """Kiem tra xem co moc nao can gui khong, va gui neu can.

        Ba ket cuc:
          - Ma 0: da gui xong.
          - Ma 2 (loi VINH VIEN, vi du token chet): KHONG thu lai moc nay. Moc
            sau se gui binh thuong sau khi Dai sua xong.
          - Ma 1 (loi tam thoi): giu nguyen hanh vi cu - thu lai toi da
            MAX_LAN_THU_MOI_MOC lan, cach nhau KHOANG_NGHI_GIUA_HAI_LAN_THU.

        LUU Y ve moc hong vinh vien: KHONG duoc coi no nhu "da gui". Neu coi nhu
        da gui thi chon_moc_can_gui() se lui ve moc CU HON va gui bao cao cu -
        dung thu ma giai doan 2 da co cong tranh. Da bi buoc dung thu bat duoc
        ngay 29/09/2026: moc 12h hong vinh vien lam he thong lui ve gui moc 8h.
        """
        moc, bo_qua = chon_moc_can_gui(
            now, self.danh_sach_moc, self._da_gui_hom_nay(now), self.trang_thai
        )
        # Chi bao "bo qua" MOT lan cho moi moc. Vong lap 30 giay mot lan, neu
        # bao moi vong thi mot ngay sinh ~2.880 dong nhat ky vo ich.
        for m in bo_qua:
            if m not in self.da_bao_bo_qua:
                self.da_bao_bo_qua.add(m)
                report.log(
                    f"NGUOI TRUC: bo qua moc {m}h - da co bao cao moi hon chua gui"
                )
        if moc is None:
            return

        if moc in self.moc_hong_vinh_vien:
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
                "- KHONG thu lai. Sua xong thi moc sau gui binh thuong."
            )
        else:
            so_lan = self.trang_thai.so_lan.get(moc, 0)
            report.log(
                f"NGUOI TRUC: gui moc {moc}h THAT BAI (lan thu {so_lan}/{MAX_LAN_THU_MOI_MOC})"
            )

    def nghe_telegram(self):
        """Doc tin nhan Telegram moi va xu ly.

        Vong dau tien chi XA TIN TON DONG, khong tra loi - neu khong bot se
        tra loi mot loat tin nhan cu.

        Goi qua self.xa_tin / self.lay_tin (khong goi thang ham) de kiem thu
        thay duoc, khong phai goi mang that.
        """
        if not self.da_xa_tin_ton_dong:
            self.offset, loi = self.xa_tin(self.env)
            if loi:
                report.log(f"NGUOI TRUC: chua xa duoc tin ton dong: {loi}")
                return
            self.da_xa_tin_ton_dong = True
            report.log("NGUOI TRUC: da xa het tin nhan ton dong")
            return

        ds, loi = self.lay_tin(self.env, self.offset)
        if loi:
            report.log(f"NGUOI TRUC: khong lay duoc tin nhan Telegram: {loi}")
            return
        if not ds:
            return

        self.offset = offset_moi_tu_ket_qua(ds)
        for tin in ds:
            try:
                self.xu_ly_tin(tin)
            except Exception as e:
                report.log(f"NGUOI TRUC: loi khi xu ly mot tin nhan: {e}")

    def xu_ly_tin(self, tin):
        """Xu ly mot tin nhan. Tin tu nguoi la bi bo qua va ghi nhat ky."""
        chat_id_dai = self.env.get("TELEGRAM_CHAT_ID", "")
        if not tin_tu_dai(tin, chat_id_dai):
            try:
                chat_id_la = tin["message"]["chat"]["id"]
            except (KeyError, TypeError):
                chat_id_la = "?"
            report.log(f"NGUOI TRUC: bo qua tin tu chat_id la ({chat_id_la})")
            return

        cau_hoi = noi_dung_tin(tin)
        now = self.dong_ho()
        tra_loi = tra_loi_tin_nhan(
            cau_hoi=cau_hoi,
            env=self.env,
            danh_sach_moc=self.danh_sach_moc,
            bat_dau=self.bat_dau,
            lan_gui_cuoi=self.lan_gui_cuoi,
            da_gui=self._da_gui_hom_nay(now),
            now=now,
            tra_loi_ai_fn=self.tra_loi_ai_fn,
            doc_han_fn=self.doc_han_fn,
        )
        if self.che_do_thu:
            report.log(f"NGUOI TRUC [THU]: se tra loi: {tra_loi.splitlines()[0]}")
            return
        if self.gui_tin(tra_loi):
            report.log("NGUOI TRUC: da tra loi mot tin nhan")

    def mot_vong(self):
        """Mot vong lap: canh moc gio, nghe Telegram, ghi nhip tim."""
        now = self.dong_ho()
        self.canh_moc(now)
        self.nghe_telegram()
        self.so_vong += 1
        if self.so_vong % NHIP_TIM_MOI_VONG == 0:
            report.log(f"NGUOI TRUC: nhip tim - dang song, vong {self.so_vong}")


def main():
    parser = argparse.ArgumentParser(
        description="Người trực — tiến trình chạy suốt của báo cáo Meta Ads"
    )
    parser.add_argument("--thu", action="store_true",
                        help="Chạy toàn bộ luồng nhưng KHÔNG gửi gì (để kiểm chứng)")
    parser.add_argument("--gui-ngay", type=int, default=None, metavar="MOC",
                        help="Gửi ngay mốc này rồi thoát (bỏ qua canh giờ)")
    args = parser.parse_args()

    duong_dan_env = GOC / ".env"
    try:
        env = report.load_env(duong_dan_env)
    except Exception:
        print(f"LOI: Khong doc duoc file .env tai {duong_dan_env}")
        print("Cach xu ly: copy .env.example thanh .env roi dien token vao.")
        report.log("NGUOI TRUC: khong doc duoc .env - dung")
        return 1

    danh_sach_moc = report.doc_moc_tu_env(env)

    if args.gui_ngay is not None:
        if args.gui_ngay not in danh_sach_moc:
            print(
                f"LOI: Moc {args.gui_ngay}h khong nam trong danh sach moc cua may nay: "
                f"{danh_sach_moc}"
            )
            return 1
        ma = gui_bao_cao(args.gui_ngay, che_do_thu=args.thu)
        if ma == report.MA_THOAT_OK:
            print("DA GUI")
        elif ma == report.MA_THOAT_VINH_VIEN:
            print("GUI THAT BAI - LOI VINH VIEN (token chet / thieu quyen)")
        else:
            print("GUI THAT BAI - LOI TAM THOI")
        return ma

    truc = NguoiTruc(env, danh_sach_moc, che_do_thu=args.thu)
    print(f"NGUOI TRUC dang chay. Moc gio: {danh_sach_moc}. Che do thu: {args.thu}")
    report.log(
        f"NGUOI TRUC: bat dau - moc gio {danh_sach_moc}, che do thu {args.thu}"
    )

    while True:
        try:
            truc.mot_vong()
        except KeyboardInterrupt:
            report.log("NGUOI TRUC: dung theo yeu cau (Ctrl+C)")
            return 0
        except Exception as e:
            report.log(f"NGUOI TRUC: loi trong vong lap: {e}")
        try:
            time.sleep(NHIP_GIAC)
        except KeyboardInterrupt:
            report.log("NGUOI TRUC: dung theo yeu cau (Ctrl+C)")
            return 0


if __name__ == "__main__":
    sys.exit(main())
