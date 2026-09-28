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
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

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

# Cau tra loi cho cau hoi chua lam duoc (phan AI thuoc Giai doan 4).
TRA_LOI_CHUA_CO_AI = (
    "Tôi đang trực, nhưng chưa trả lời được câu hỏi về số liệu.\n"
    "\n"
    "Phần hỏi số liệu (ví dụ \"camp nào tệ nhất tuần này?\") sẽ có ở "
    "giai đoạn sau, khi nối phần AI vào.\n"
    "\n"
    "Hiện tôi làm được hai việc:\n"
    "- Gửi báo cáo tự động đúng các mốc giờ mỗi ngày.\n"
    "- Trả lời câu \"còn sống không?\" để Đại biết tôi còn chạy."
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

    Chay o tien trinh rieng vi: report.py co loi thi Nguoi truc van song, va
    phan tinh tien trong report.py khong bi dung toi.

    Tra ve True neu report.py thoat voi ma 0.
    """
    lenh = [sys.executable, str(GOC / "report.py"), "--slot", str(moc)]
    if che_do_thu:
        lenh.append("--dry")
    try:
        kq = subprocess.run(
            lenh,
            cwd=str(GOC),
            capture_output=True,
            text=True,
            timeout=CHO_REPORT_TOI_DA,
        )
    except subprocess.TimeoutExpired:
        report.log(
            f"NGUOI TRUC: report.py moc {moc}h qua thoi gian cho {CHO_REPORT_TOI_DA} giay"
        )
        return False
    except Exception as e:
        report.log(f"NGUOI TRUC: khong chay duoc report.py moc {moc}h: {e}")
        return False

    if kq.returncode == 0:
        return True
    duoi = (kq.stderr or "")[-300:]
    report.log(f"NGUOI TRUC: report.py moc {moc}h thoat voi ma {kq.returncode}: {duoi}")
    return False


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
                 xa_tin_fn=None, lay_tin_fn=None):
        self.env = env or {}
        self.danh_sach_moc = list(danh_sach_moc) or list(MOC_MAC_DINH)
        self.che_do_thu = che_do_thu

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
        """Kiem tra xem co moc nao can gui khong, va gui neu can."""
        moc, bo_qua = chon_moc_can_gui(
            now, self.danh_sach_moc, self._da_gui_hom_nay(now), self.trang_thai
        )
        for m in bo_qua:
            report.log(
                f"NGUOI TRUC: bo qua moc {m}h - da co bao cao moi hon chua gui"
            )
        if moc is None:
            return

        report.log(f"NGUOI TRUC: toi moc {moc}h - bat dau gui")
        self.trang_thai.ghi_lan_thu(moc, now)
        if self.gui_bao_cao(moc):
            self.da_xu_ly.add(moc)
            self.lan_gui_cuoi = now
            report.log(f"NGUOI TRUC: da gui xong moc {moc}h")
        else:
            so_lan = self.trang_thai.so_lan.get(moc, 0)
            report.log(
                f"NGUOI TRUC: gui moc {moc}h THAT BAI (lan thu {so_lan}/{MAX_LAN_THU_MOI_MOC})"
            )
