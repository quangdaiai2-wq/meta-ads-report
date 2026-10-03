"""So ghi viec agent da lam + hang doi de xuat dang cho Dai tra loi.

Hai loai tri nho, dung lan:
  - Nho SO  : logs/lich-su.json   (so lieu tung ngay)  — da co san
  - Nho VIEC: logs/nhat-ky-agent.json (da lam gi, vi sao, ket qua) — file nay

File nay giu NGUYEN dinh dang hai ban ghi da co (30/09/2026, tam dung + bat lai
ad set 120250506886650509) de doc lai bang mat thuong van hieu.
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

GIO_VN = timezone(timedelta(hours=7))
GOC = Path(__file__).parent
DUONG_DAN = GOC / "logs" / "nhat-ky-agent.json"

# So rieng cho viec "BO QUA 24h" (Dai chot 02/10/2026).
# Vi sao tach file rieng: day la y DINH CUA DAI, khong phai lich su viec da lam.
# Nhet vao nhat-ky-agent.json se lam ban so do.
BO_QUA_PATH = GOC / "logs" / "agent-bo-qua.json"

HAN_CHO_PHUT = 24 * 60
HAN_QUET_LAI_PHUT = 15   # mac dinh sau khi Meta tu choi: cho 1 nhip roi hoi lai


def _gio(t):
    """Chuan hoa thoi diem ve co mui gio. Doc khong duoc -> None."""
    if isinstance(t, str):
        try:
            t = datetime.fromisoformat(t)
        except ValueError:
            return None
    if not isinstance(t, datetime):
        return None
    return t if t.tzinfo else t.replace(tzinfo=GIO_VN)


def doc(duong_dan=None):
    """Doc so. File chua co / hong -> danh sach rong (khong nem loi)."""
    p = Path(duong_dan) if duong_dan else DUONG_DAN
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return d if isinstance(d, list) else []


def ghi(ban_ghi, duong_dan=None):
    """Them mot ban ghi vao so. Ghi kieu nguyen tu: ghi file tam roi doi ten.

    Tra ve True/False. KHONG BAO GIO nem loi — mat so khong duoc lam sap agent.
    """
    p = Path(duong_dan) if duong_dan else DUONG_DAN
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        ds = doc(p)
        ds.append(ban_ghi)
        tam = p.with_suffix(".json.tmp")
        tam.write_text(json.dumps(ds, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tam, p)
        return True
    except OSError:
        return False


def _la_hanh_dong_that(rec):
    """Ban ghi nay co tinh la MOT hanh dong da gui len Meta khong?

    Uu tien truong `da_gui_len_meta`. Hai ban ghi cu (30/09/2026) chua co truong
    do nhung van la hanh dong that => van phai dem, de khong noi long tran.
    """
    if not isinstance(rec, dict):
        return False
    if rec.get("da_gui_len_meta") is True:
        return True
    if "da_gui_len_meta" not in rec and rec.get("hanh_dong") in ("tam_dung", "bat_lai"):
        return True
    return False


def dem_hanh_dong(bay_gio=None, duong_dan=None):
    """Dem so hanh dong da lam HOM NAY va trong GIO nay."""
    goc = _gio(bay_gio) or datetime.now(GIO_VN)
    n_ngay = n_gio = 0
    for rec in doc(duong_dan):
        if not _la_hanh_dong_that(rec):
            continue
        t = _gio(rec.get("luc"))
        if t is None:
            continue
        if t.date() == goc.date():
            n_ngay += 1
            if t.hour == goc.hour:
                n_gio += 1
    return {"so_hanh_dong_hom_nay": n_ngay, "so_hanh_dong_gio_nay": n_gio}


def lan_tat_gan_nhat(ma, bay_gio=None, duong_dan=None):
    """Ban ghi lan TAT THANH CONG gan nhat cua mot nhom. Khong co -> None.

    Dung cho viec HOAN TAC: phai biet truoc khi tat thi nhom do co ngan sach
    bao nhieu, de bat lai dung muc cu.
    """
    goc = _gio(bay_gio) or datetime.now(GIO_VN)
    ra = None
    for rec in doc(duong_dan):
        if not isinstance(rec, dict):
            continue
        if str((rec.get("doi_tuong") or {}).get("id") or "") != str(ma):
            continue
        if rec.get("hanh_dong") != "tam_dung" or not _la_hanh_dong_that(rec):
            continue
        if not str(rec.get("ket_qua") or "").startswith("thanh cong"):
            continue
        t = _gio(rec.get("luc"))
        if t is None or (goc - t) > timedelta(minutes=HAN_CHO_PHUT):
            continue
        if ra is None or t > (_gio(ra.get("luc")) or datetime.min.replace(tzinfo=GIO_VN)):
            ra = rec
    return ra


def nhom_da_tra_loi(bay_gio=None, duong_dan=None):
    """{id_nhom: thoi_diem_tra_loi} — de khong hoi lai nhom vua hoi.

    Tinh ca hai truong hop: Dai da dong y, va Dai da noi bo qua.

    ⚠️ BO QUA cac ban ghi ma buoc GHI LEN META THAT BAI (`ghi_meta_that_bai`).
    Ly do (Dai chot 02/10/2026): khi Meta tu choi, Dai DA bam nut nhung viec
    chua xong. Neu van tinh la "da tra loi" thi nhom bi khoa 24 gio — trong khi
    Dai muon "lan quet sau thu lai". Viec bo qua 24h nay do co che RIENG lo
    (`bo_qua_nhom`), do chinh Dai bam.
    """
    ra = {}
    for rec in doc(duong_dan):
        if not isinstance(rec, dict) or not rec.get("dai_phan_hoi"):
            continue
        if rec.get("ghi_meta_that_bai"):
            continue
        ma = str((rec.get("doi_tuong") or {}).get("id") or "")
        t = _gio(rec.get("luc"))
        if ma and t is not None:
            cu = ra.get(ma)
            if cu is None or t > cu:
                ra[ma] = t
    return ra


def nhom_bat_lai_gan_nhat(bay_gio=None, duong_dan=None):
    """{id_nhom: thoi_diem_bat_lai_gan_nhat} — lan BAT LAI thanh cong moi nhat.

    VI SAO CAN (Dai chot 03/10/2026): Rao 8 trong `agent_rao.py` chan hoi lai
    nhom da co cau tra loi trong 24 gio. Nhung neu nhom da duoc BAT LAI roi chay
    lai phat sinh chi tieu thi cau tra loi cu KHONG con gia tri — phai hoi lai.

    Truong hop that 03/10/2026: Dai tra loi nhom X luc 02/10 11:45, nhom duoc
    bat lai va chay lai, nhung agent im lang suot 24 gio. Dai tuong bot chet.

    ⚠️ Chi tinh lan bat lai THANH CONG:
      - Ban ghi MOI: co `da_gui_len_meta` — chi nhan khi co dung `True`.
      - Ban ghi CU (truoc 03/10/2026) khong co co do => suy tu `ket_qua`
        chua "thanh cong" (giong `_la_hanh_dong_that`).
      - Du co co `True`, neu `ket_qua` bao loi/that bai/tu choi thi VAN KHONG
        tinh. LOI NAY da bi dung thu bat duoc: bo qua no thi Rao 8 mo oan cho
        nhom CHUA he duoc bat lai — dung loai loi nguy hiem nhat.
    """
    ra = {}
    for rec in doc(duong_dan):
        if not isinstance(rec, dict) or rec.get("hanh_dong") != "bat_lai":
            continue
        kq = str(rec.get("ket_qua") or "").lower()
        if "da_gui_len_meta" in rec:
            if rec.get("da_gui_len_meta") is not True:
                continue
        elif "thanh cong" not in kq:
            continue
        if "loi" in kq or "that bai" in kq or "tu choi" in kq:
            continue
        ma = str((rec.get("doi_tuong") or {}).get("id") or "")
        t = _gio(rec.get("luc"))
        if ma and t is not None:
            cu = ra.get(ma)
            if cu is None or t > cu:
                ra[ma] = t
    return ra


def _doc_dict(p):
    """Doc file JSON dang DICT. Chua co / hong / la dang khac -> dict rong."""
    try:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def _ghi_dict(p, d):
    """Ghi file JSON dang DICT theo kieu an toan (ghi file tam roi doi ten)."""
    try:
        Path(p).parent.mkdir(parents=True, exist_ok=True)
        tam = Path(p).with_suffix(".json.tmp")
        tam.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tam, p)
        return True
    except OSError:
        return False


def bo_qua_nhom(ma, den_luc, duong_dan=None):
    """Ghi 'bo qua nhom nay den <den_luc>'. Tra ve True/False.

    Dung khi Dai bam nut "Bo qua 24h" tren tin bao loi.
    """
    p = duong_dan or BO_QUA_PATH
    ds = _doc_dict(p)
    ds[str(ma)] = (den_luc.isoformat(timespec="seconds")
                   if hasattr(den_luc, "isoformat") else str(den_luc))
    return _ghi_dict(p, ds)


def xoa_bo_qua(ma, duong_dan=None):
    """Xoa lenh bo qua cua mot nhom. Dung khi Dai bam 'Tiep tuc quet lai lan sau'."""
    p = duong_dan or BO_QUA_PATH
    ds = _doc_dict(p)
    ds.pop(str(ma), None)
    return _ghi_dict(p, ds)


def nhom_dang_bo_qua(bay_gio=None, duong_dan=None):
    """{id_nhom: thoi_diem_het_bo_qua} — chi gom nhom CON trong han bo qua."""
    goc = _gio(bay_gio) or datetime.now(GIO_VN)
    ra = {}
    for ma, t in (_doc_dict(duong_dan or BO_QUA_PATH) or {}).items():
        den = _gio(t)
        if den is not None and goc < den:
            ra[str(ma)] = den
    return ra


def hang_cho(bay_gio=None, duong_dan=None):
    """Cac de xuat DA GUI cho Dai nhung CHUA co cau tra loi, con trong 24 gio."""
    goc = _gio(bay_gio) or datetime.now(GIO_VN)
    ra = []
    for rec in doc(duong_dan):
        if not isinstance(rec, dict):
            continue
        if rec.get("che_do") != "xin_phep" or rec.get("dai_phan_hoi"):
            continue
        t = _gio(rec.get("luc"))
        if t is None or (goc - t) > timedelta(minutes=HAN_CHO_PHUT):
            continue
        ra.append(rec)
    return ra


def ma_dang_cho(bay_gio=None, duong_dan=None):
    """Danh sach id nhom dang cho Dai tra loi."""
    return [str((r.get("doi_tuong") or {}).get("id") or "")
            for r in hang_cho(bay_gio, duong_dan)
            if (r.get("doi_tuong") or {}).get("id")]


def cap_nhat_phan_hoi(ma_nhom, tra_loi, ket_qua=None, duong_dan=None,
                      ghi_meta_that_bai=False):
    """Ghi cau tra loi cua Dai vao ban ghi dang cho. Tra ve True/False.

    `ghi_meta_that_bai=True`: buoc GUI LEN META da that bai. Danh dau de
    `nhom_da_tra_loi` BO QUA ban ghi nay — Dai da bam nut nhung viec chua xong,
    nen khong duoc khoa nhom 24 gio. Xem chu thich o `nhom_da_tra_loi`.

    🔴 SUA 03/10/2026 — LOI "BAN GHI MO COI" (Dai chot, da do bang so that).
    Vi sao: mot viec sinh HAI ban ghi —
        ban ghi 1: luc HOI Dai        (che_do="xin_phep", da_gui_len_meta=False)
        ban ghi 2: GHI TRUOC KHI GUI META (da_gui_len_meta=True)  <-- quy dinh bat buoc
    Ban cu tim nguoc tu duoi len va dung o dieu kien "chua co dai_phan_hoi". Ban ghi 2
    duoc `_lam_theo_dong_y` gan `dai_phan_hoi` trong BO NHO roi ghi ra file TRUOC khi
    goi ham nay, nen luc khop no DA co `dai_phan_hoi` => bi bo qua. Ket qua bi ghi vao
    ban ghi 1, con ban ghi 2 (ban ghi THUC SU da gui len Meta) mai mai trong ket qua.

    Hau qua that (do tren logs/nhat-ky-agent.json ngay 03/10/2026):
      - 17/40 ban ghi bi mo coi.
      - 0 ban ghi nao vua `da_gui_len_meta=True` vua co `ket_qua` => cong cu doi
        chieu voi Meta KHONG THE khop duoc gi.
      - Nhin vao so thay nhu "tat 2 lan", va khong biet viec nao da xong that.

    Nay: UU TIEN ban ghi `da_gui_len_meta is True` va chua co ket qua. Neu khong co
    (so cu chi 1 ban ghi) thi lui ve hanh vi cu — khong pha du lieu da co.
    """
    p = Path(duong_dan) if duong_dan else DUONG_DAN
    try:
        ds = doc(p)
        dich = _chon_ban_ghi_de_chot(ds, ma_nhom)
        if dich is None:
            return False
        dich["dai_phan_hoi"] = tra_loi
        if ket_qua is not None:
            dich["ket_qua"] = ket_qua
        if ghi_meta_that_bai:
            dich["ghi_meta_that_bai"] = True
        tam = p.with_suffix(".json.tmp")
        tam.write_text(json.dumps(ds, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tam, p)
        return True
    except OSError:
        return False


def _chon_ban_ghi_de_chot(ds, ma_nhom):
    """Chon DUNG ban ghi de ghi ket qua. Tra ve dict hoac None.

    Thu tu uu tien (Dai chot 03/10/2026):
      1. Ban ghi DA GUI LEN META (`da_gui_len_meta is True`) va CHUA co ket qua.
         Day la ban ghi that su mang hanh dong — ket qua phai nam o day.
      2. Ban ghi chua co `dai_phan_hoi` (hanh vi CU, giu de tuong thich so 1 ban ghi).
    """
    ung_vien = [r for r in ds
                if isinstance(r, dict)
                and str((r.get("doi_tuong") or {}).get("id") or "") == str(ma_nhom)
                and r.get("da_gui_len_meta") is True
                and r.get("ket_qua") is None]
    if ung_vien:
        # Moi nhat truoc — neu vi pham quy uoc, ghi vao lan gui gan nhat.
        def _khoa(r):
            return _gio(r.get("luc")) or datetime.min.replace(tzinfo=GIO_VN)
        return max(ung_vien, key=_khoa)

    # Duong lui: hanh vi cu (ban ghi dang cho chua co cau tra loi).
    for rec in reversed(ds):
        if not isinstance(rec, dict):
            continue
        if str((rec.get("doi_tuong") or {}).get("id") or "") != str(ma_nhom):
            continue
        if rec.get("dai_phan_hoi"):
            continue
        return rec
    return None


def tim_ban_ghi_mo_coi(duong_dan=None):
    """Danh sach ban ghi DA GUI LEN META nhung KHONG co ket qua.

    VI SAO CAN (Dai chot 03/10/2026): truoc khi sua `cap_nhat_phan_hoi`, moi lan tat
    deu de lai mot ban ghi mo coi. Ham nay de NHIN THAY chung — khong the sua cai
    minh khong do duoc.
    """
    ra = []
    for rec in doc(duong_dan):
        if not isinstance(rec, dict):
            continue
        if rec.get("da_gui_len_meta") is not True:
            continue
        if rec.get("ket_qua"):
            continue
        ra.append(rec)
    return ra


# Nhan nguon goc — de biet viec do MAY lam hay DAI lam, khong can mo Meta.
# Ly do (Dai chot 03/10/2026): Dai khong phai chu tai khoan doanh nghiep, vai tro
# EMPLOYEE nen khong tao duoc System User. Moi thao tac gui len Meta deu mang ten
# chu token ca nhan ("Nam Duc Pham") => nhat ky Meta KHONG phan biet duoc nguoi va may.
NGUON_GOC_HOP_LE = ("agent_tu_hanh", "dai_bam_nut", "dai_go_tay", "cho_duyet")


def nguon_goc_cua(ban_ghi):
    """Tra ve nguon goc cua mot ban ghi. Ban ghi CU (chua co truong) thi SUY RA.

    Gia tri:
      agent_tu_hanh : may tu quyet, khong ai bam nut (TH2 tat chien dich, chuyen NS)
      dai_bam_nut   : Dai bam nut tren Telegram
      dai_go_tay    : Dai go lenh bang tay
      cho_duyet     : moi la de xuat, chua gui gi len Meta (khong phai hanh dong)
      ""            : ban ghi rac, khong doc duoc
    """
    if not isinstance(ban_ghi, dict):
        return ""
    gt = ban_ghi.get("nguon_goc")
    if isinstance(gt, str) and gt in NGUON_GOC_HOP_LE:
        return gt

    # --- Ban ghi CU: suy tu cac truong da co ---
    if ban_ghi.get("da_gui_len_meta") is True and ban_ghi.get("dai_phan_hoi"):
        # Da gui len Meta VA co cau tra loi cua Dai => Dai da bam nut (hoac go tay).
        return "dai_bam_nut"
    if ban_ghi.get("da_gui_len_meta") is True:
        # Da gui len Meta ma khong co cau tra loi cua Dai => may tu lam.
        return "agent_tu_hanh"
    # 🔴 Ban ghi CU BI LECH (hau qua cua loi "ban ghi mo coi"): `da_gui=False`
    # NHUNG da co `ket_qua` thanh cong. Thuc chat viec DA duoc gui len Meta, chi
    # la ket qua bi ghi nham cho. Xem `doi_chieu_meta._la_ban_ghi_cu_bi_lech`.
    if ban_ghi.get("che_do") == "xin_phep" and ban_ghi.get("ket_qua"):
        return "dai_bam_nut"
    if ban_ghi.get("che_do") == "xin_phep":
        # Chua gui len Meta, chua co ket qua => con dang cho Dai tra loi.
        return "cho_duyet"
    # HAI BAN GHI GOC 30/09/2026: dinh dang CU, KHONG co `che_do` lan
    # `da_gui_len_meta`, nhung CO `ket_qua` thanh cong => la hanh dong that
    # (Dai bam nut HOAN TAC). Xem `_la_hanh_dong_that` — cung suy nhu vay.
    if ban_ghi.get("hanh_dong") in ("tam_dung", "bat_lai") and ban_ghi.get("ket_qua"):
        return "dai_bam_nut"
    return ""


# ---------------------------------------------------------------------------
#  HANG DOI LENH — de tien trinh bao cao chuyen tiep lenh cua Dai cho agent
# ---------------------------------------------------------------------------
#  Vi sao can: hai tien trinh (bao cao va agent) dung CHUNG mot bot Telegram,
#  ma getUpdates cua Telegram chi giao moi tin cho MOT nguoi goi. Ai xac nhan
#  truoc thi nguoi kia khong bao gio thay tin do nua. Nen tien trinh bao cao
#  phai nhan ra lenh "tat <ma>" / "bo qua <ma>" va GHI VAO FILE NAY, thay vi
#  tra loi bang AI. Agent doc file nay o vong chay ke tiep.

LENH_PATH = GOC / "logs" / "agent-lenh.json"


def _doc_ds(p):
    try:
        d = json.loads(Path(p).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return d if isinstance(d, list) else []


def _ghi_ds(p, ds):
    try:
        Path(p).parent.mkdir(parents=True, exist_ok=True)
        tam = Path(p).with_suffix(".json.tmp")
        tam.write_text(json.dumps(ds, ensure_ascii=False, indent=2), encoding="utf-8")
        os.replace(tam, p)
        return True
    except OSError:
        return False


def ghi_lenh(text, tin_nhan_id=None, duong_dan=None):
    """Chuyen tiep mot lenh cua Dai cho agent. Tra ve True/False.

    `tin_nhan_id`: voi lenh bam tu NUT, day la ma tin nhan chua nut — de agent
    sua chinh tin do thanh ket qua, thay vi gui them tin moi.
    """
    if not isinstance(text, str) or not text.strip():
        return False
    p = Path(duong_dan) if duong_dan else LENH_PATH
    ds = _doc_ds(p)
    ds.append({"luc": datetime.now(GIO_VN).isoformat(timespec="seconds"),
               "noi_dung": text.strip(),
               "tin_nhan_id": tin_nhan_id})
    return _ghi_ds(p, ds)


def doc_lenh(duong_dan=None):
    """Danh sach lenh dang cho agent xu ly."""
    return _doc_ds(Path(duong_dan) if duong_dan else LENH_PATH)


def xoa_lenh(duong_dan=None):
    """Xoa hang doi sau khi agent da xu ly xong."""
    return _ghi_ds(Path(duong_dan) if duong_dan else LENH_PATH, [])


# ---------------------------------------------------------------------------
#  KHOA MOT-TIEN-TRINH — chi cho MOT agent chay cung luc
# ---------------------------------------------------------------------------
#  Vi sao can: ngay 30/09/2026, nhat ky ghi AGENT khoi dong HAI LAN cach nhau 15
#  giay (14:52:29 va 14:52:44) — rat co the Dai bam bat-chay-agent.bat hai lan.
#  Hai agent cung chay thi:
#    · moi cai de xuat mot lan  -> Dai nhan tin trung
#    · ca hai doc hang doi      -> cung mot lan bam nut bi xu ly hai lan
#    · ca hai ghi so            -> so loan
#  Cach lam: mot file khoa ghi THOI DIEM cap nhat (dong 1) va PID (dong 2).
#  Tao file theo kieu O_CREAT|O_EXCL nen la nguyen tu — hai tien trinh khoi
#  dong cung luc thi chi mot cai tao duoc.
#  Khoa duoc coi la DA CHET khi:
#    · PID trong khoa KHONG con song  (chac chan — xem _tien_trinh_song), HOAC
#    · thoi diem cap nhat da qua han   (doan, dung khi khoa khong ghi PID)

KHOA_PATH = GOC / "logs" / "agent-dang-chay.lock"


def _doc_khoa(duong_dan=None):
    """Thoi diem trong file khoa (DONG DAU). Khong co / hong -> None."""
    p = Path(duong_dan) if duong_dan else KHOA_PATH
    try:
        dong = p.read_text(encoding="utf-8").strip().splitlines()
    except OSError:
        return None
    if not dong:
        return None
    return _gio(dong[0].strip())


def _doc_khoa_pid(duong_dan=None):
    """PID trong file khoa (DONG THU HAI). Khong co / hong -> None."""
    p = Path(duong_dan) if duong_dan else KHOA_PATH
    try:
        dong = p.read_text(encoding="utf-8").strip().splitlines()
    except OSError:
        return None
    if len(dong) < 2:
        return None
    try:
        return int(dong[1].strip())
    except ValueError:
        return None


def _tien_trinh_song(pid):
    """PID con song khong: True / False / None (khong biet).

    ⚠️ CANH BAO Windows: os.kill(pid, 0) KHONG phai phep thu vo hai — Python
    tren Windows goi TerminateProcess, tuc la GIET tien trinh do. Nen tren
    Windows phai dung ctypes OpenProcess + GetExitCodeProcess.
    """
    if not pid:
        return None
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes

            k32 = ctypes.windll.kernel32
            k32.OpenProcess.restype = wintypes.HANDLE
            k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            k32.GetExitCodeProcess.argtypes = [wintypes.HANDLE,
                                               ctypes.POINTER(wintypes.DWORD)]
            k32.CloseHandle.argtypes = [wintypes.HANDLE]
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            STILL_ACTIVE = 259

            h = k32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
            if not h:
                return False                     # khong mo duoc => khong con song
            try:
                ma = wintypes.DWORD()
                if not k32.GetExitCodeProcess(h, ctypes.byref(ma)):
                    return None
                return ma.value == STILL_ACTIVE
            finally:
                k32.CloseHandle(h)
        except Exception:
            return None
    try:
        os.kill(int(pid), 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return None


def _ghi_khoa(bay_gio=None, duong_dan=None):
    p = Path(duong_dan) if duong_dan else KHOA_PATH
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        # Dong 1: thoi diem cap nhat. Dong 2: PID cua tien trinh giu khoa.
        # Co PID thi biet CHAC tien trinh con song hay da chet, khong phai doi
        # het han (xem _khoa_con_song).
        noi_dung = (_gio(bay_gio) or datetime.now(GIO_VN)).isoformat(timespec="seconds")
        p.write_text(f"{noi_dung}\n{os.getpid()}\n", encoding="utf-8")
        return True
    except OSError:
        return False


def _khoa_con_song(nhip_phut, bay_gio=None, duong_dan=None):
    """True neu khoa con moi (tuc tien trinh giu khoa con dang chay).

    Uu tien PID: neu khoa CO ghi PID ma PID do KHONG con song thi coi nhu chet
    NGAY, khong doi het han.

    Vi sao can: 01/10/2026, khi chuyen sang chay ngam, file .bat dung agent cu
    roi bat lai NGAY. Khoa cu chi duoc lam moi 30 phut mot lan (luc quet Meta),
    nen no trong nhu "con song" toi 60 phut ⇒ agent moi TU CHOI khoi dong gan
    mot gio dong ho. Do la loi that, khong phai loi nguoi dung.
    """
    pid = _doc_khoa_pid(duong_dan)
    if pid is not None and _tien_trinh_song(pid) is False:
        return False
    goc = _gio(bay_gio) or datetime.now(GIO_VN)
    t = _doc_khoa(duong_dan)
    if t is None:
        return False
    return (goc - t) < timedelta(minutes=max(10, int(nhip_phut) * 2))


def co_agent_khac_dang_chay(nhip_phut=30, bay_gio=None, duong_dan=None):
    """Co agent khac dang chay khong. Tra ve (co: bool, ly_do: str)."""
    if _khoa_con_song(nhip_phut, bay_gio, duong_dan):
        t = _doc_khoa(duong_dan)
        return True, f"co agent khac dang chay (cap nhat luc {t.strftime('%H:%M:%S')})"
    return False, "khong co agent nao khac"


def giu_khoa(nhip_phut=30, bay_gio=None, duong_dan=None):
    """Gianh quyen chay. Tra ve (giu_duoc: bool, ly_do: str).

    Tao file theo kieu O_CREAT|O_EXCL => nguyen tu. Neu file da co ma con moi
    thi tra False (dung khoi dong). Neu file cu qua han thi gianh lai.
    """
    p = Path(duong_dan) if duong_dan else KHOA_PATH
    goc = _gio(bay_gio) or datetime.now(GIO_VN)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(f"{goc.isoformat(timespec='seconds')}\n{os.getpid()}\n")
        return True, "vua gianh duoc quyen chay"
    except FileExistsError:
        pass
    except OSError as e:
        # Khong tao duoc khoa (quyen, dia) => KHONG chan agent chay.
        return True, f"khong tao duoc khoa ({e}) — van chay"

    if _khoa_con_song(nhip_phut, goc, duong_dan):
        t = _doc_khoa(duong_dan)
        return False, (f"đã có agent khác đang chạy (cập nhật lúc "
                       f"{t.strftime('%H:%M:%S')}) — không khởi động thêm")
    _ghi_khoa(goc, duong_dan)
    return True, "khoa cu khong con hieu luc (da qua han hoac tien trinh cu da chet) — gianh lai"


def cap_nhat_khoa(bay_gio=None, duong_dan=None):
    """Gia han khoa. Goi moi vong de tien trinh khac biet minh con song."""
    return _ghi_khoa(bay_gio, duong_dan)


def nha_khoa(duong_dan=None):
    """Xoa khoa khi tat han. Khong xoa duoc cung khong sao (khoa se qua han)."""
    p = Path(duong_dan) if duong_dan else KHOA_PATH
    try:
        p.unlink()
        return True
    except OSError:
        return False
