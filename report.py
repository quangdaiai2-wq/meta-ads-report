"""
BAO CAO META ADS TU DONG -> TELEGRAM
=====================================
Script chay theo lich, lay so lieu Meta Ads, gui bao cao vao Telegram.

Cach dung:
    python report.py            # tu dong nhan biet moc gio hien tai
    python report.py --mock 8   # chay thu voi moc gio 8h (khong gui Telegram)
    python report.py --dry      # chay that nhung khong gui Telegram

Uu tien doc moc gio tu tham so --mock, neu khong co thi lay gio hien tai.
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dashboard import save_dashboard
import ai
import bat_thuong
import lich_su


def _ep_stdout_utf8():
    """Bat buoc stdout/stderr dung UTF-8. Duoc goi ngay khi nap mo-dun.

    VI SAO CAN: khi Windows Task Scheduler khoi dong Nguoi truc, tien trinh
    con (report.py) khong co console nen Python lay bang ma theo locale cua
    Windows - o may nay la cp1252. Bao cao co dau tieng Viet ("So tien...")
    khong ma hoa duoc => print() nem UnicodeEncodeError => report.py thoat
    voi ma 1 => BAO CAO KHONG DUOC GUI.

    Da xay ra THAT: bao cao ngung gui tu 17h ngay 28/09/2026, va ca ba lan
    thu cua moc 8h ngay 29/09/2026 deu that bai. Tai hien duoc bang cach dat
    PYTHONIOENCODING=cp1252.

    errors="replace": ky tu nao khong ma hoa duoc thi thay bang '?', tuyet doi
    khong lam chet ca bao cao.
    """
    for ten in ("stdout", "stderr"):
        luong = getattr(sys, ten, None)
        if luong is None:
            continue
        try:
            luong.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            # Mot so loai luong (bi thay bang doi tuong gia, da bi dong...)
            # khong doi duoc bang ma. Khong duoc phep lam chet chuong trinh.
            pass


_ep_stdout_utf8()

API_VERSION = "v21.0"
GRAPH = f"https://graph.facebook.com/{API_VERSION}"

# Cac moc gio bao cao MAC DINH (gio Viet Nam).
# Doi duoc bang khoa REPORT_SLOTS trong .env, vi du: REPORT_SLOTS=8,12,17
# (may cong ty bo moc 22h ngay 28/09/2026; may nha giu 22h).
REPORT_SLOTS = [8, 12, 17, 22]

# Moc gio bao cao NGAY HOM TRUOC khi khong xac dinh duoc moc nao khac.
MOC_SANG_MAC_DINH = 8


def chon_moc(moc_tu_lenh, gio_hien_tai, danh_sach_moc=None):
    """Chon moc gio bao cao.

    moc_tu_lenh:  so nguyen do lich Windows truyen vao (co --slot), hoac None.
    gio_hien_tai: gio cua may, 0-23.
    danh_sach_moc: danh sach moc hop le; None thi dung REPORT_SLOTS.

    CO --slot thi tra ve DUNG moc do, khong doan gi ca.
    Day la diem chua loi gui trung: truoc day moi tien trinh deu tu doan moc
    gan nhat, nen nhieu lich chay bu cung luc se cung doan ra mot moc va gui
    ra nhieu bao cao giong het nhau.
    """
    if not danh_sach_moc:
        danh_sach_moc = REPORT_SLOTS

    if moc_tu_lenh is not None:
        if moc_tu_lenh not in danh_sach_moc:
            raise ValueError(
                f"Moc {moc_tu_lenh}h khong nam trong danh sach moc {danh_sach_moc}"
            )
        return moc_tu_lenh

    # Khong co --slot: giu cach cu (doan moc gan nhat) de khong pha vo
    # cac lich cu trong luc chuyen doi.
    return min(danh_sach_moc, key=lambda s: abs(s - gio_hien_tai))


def doc_moc_tu_env(env):
    """Doc danh sach moc gio bao cao tu khoa REPORT_SLOTS trong .env.

    Chap nhan: "8,12,17" hoac "8, 12, 17" hoac "17,8,8" hoac "8;12;17".
    Tra ve danh sach da sap xep tang dan, bo trung.

    Phan tu sai (chu, so ngoai 0-23) bi bo qua tung cai mot. Neu khong doc
    duoc moc nao hop le thi tra ve REPORT_SLOTS.

    Khong bao gio nem loi: mot dong cau hinh go sai khong duoc lam chet
    bao cao.
    """
    raw = (env or {}).get("REPORT_SLOTS", "")
    ds = []
    for phan in str(raw).replace(";", ",").split(","):
        phan = phan.strip()
        if not phan:
            continue
        try:
            moc = int(phan)
        except ValueError:
            continue
        if 0 <= moc <= 23 and moc not in ds:
            ds.append(moc)
    return sorted(ds) if ds else list(REPORT_SLOTS)


def moc_sang(danh_sach_moc):
    """Moc gio bao cao NGAY HOM TRUOC = moc NHO NHAT trong danh sach.

    Truoc day determine_period() viet cung `if slot_hour == 8`. Khi danh sach
    moc doi (vi du bo moc 8h), bao cao moc dau tien se bi hieu sai thanh
    "trong ngay" thay vi "hom qua". Lay min() de doi danh sach moc ma khong
    phai sua code.
    """
    return min(danh_sach_moc) if danh_sach_moc else MOC_SANG_MAC_DINH


def la_bao_cao_tron_ngay(slot, danh_sach_moc):
    """True neu moc nay bao cao TRON mot ngay (thuong la moc sang).

    Chi bao cao tron ngay moi so sanh duoc voi ky truoc. Bao cao moc 12h,
    17h chi la MOT PHAN cua ngay, so voi ngay day du la sai.

    Day la cho DE LAM SAI NHAT cua Giai doan 3: neu cho AI so sanh nua ngay
    voi ngay day du thi cau van van troi chay nhung ket luan sai hoan toan.
    """
    if not danh_sach_moc:
        return False
    return slot == moc_sang(danh_sach_moc)


def tao_boi_canh(env, period_text, tron_ngay):
    """Cau mo ta ky bao cao, gui kem cho AI de AI khong hieu sai pham vi."""
    ten = (env or {}).get("REPORT_ACCOUNT_NAME", "?")
    if tron_ngay:
        return (
            f"Tai khoan {ten}. Day la bao cao TRON ngay {period_text}. "
            "Co the so sanh voi so ky truoc."
        )
    return (
        f"Tai khoan {ten}. Day la bao cao MOT PHAN cua ngay {period_text} "
        "(so lieu tich luy tu 0h den gio bao cao). "
        "khong so sanh voi ngay day du nao."
    )


# Canh bao SOM khi token Meta con song it hon nguong nay (ngay).
# Muc dich: bao TRUOC khi token chet, de con kip lay token moi.
# Truoc day he thong chi bao SAU khi token da chet (luc do moi bao cao that bai).
NGUONG_CANH_BAO_NGAY = 7

# Nhac NHE tu muc nay (ngay). Con 3 tuan la con kip xep thoi gian di lay token
# moi, ma chua den muc phai gap. Chi nhac o bao cao MOC SANG - mot tin moi ngay,
# khong lam roi bang 3 tin giong nhau.
NGUONG_NHAC_NHE_NGAY = 30

# Ma loi Meta TAM THOI - thu lai duoc, phai CHO roi moi thu.
# 17 va 80004 da gap that; 4, 32, 613 la cac ma chan vi qua nhieu yeu cau khac
# cua Meta (app / page / endpoint).
MA_LOI_META_TAM_THOI = (4, 17, 32, 613, 80004)

# Ma loi Meta VINH VIEN - thu lai chi ton thoi gian, phai bao ngay.
# 190 = token het han / khong hop le (kem 463, 467) - day la ma hay gap nhat.
# 10, 200, 272 = thieu quyen. 100 = tham so sai. 803 = tai khoan khong ton tai.
MA_LOI_META_VINH_VIEN = (10, 100, 102, 190, 200, 272, 463, 467, 803)

# Thoi gian CHO (giay) truoc lan thu lai thu nhat va thu hai. LUY TIEN:
# Meta chan vi qua nhieu yeu cau thi cho ngan khong co tac dung gi.
CHO_TRUOC_KHI_THU_LAI = (5, 15)

# Ma thoat cua report.py. Nguoi truc (nguoi_truc.py) doc ma nay de biet co nen
# thu lai hay khong.
MA_THOAT_OK = 0
MA_THOAT_TAM_THOI = 1
MA_THOAT_VINH_VIEN = 2

# Ten cac loai action trong Meta API (da kiem chung bang list_actions.py)
# LUU Y: Meta tra ve NHIEU ten cho CUNG mot hanh dong (omni_*, onsite_*, offsite_*).
# Neu cong het se bi dem trung. Chi dung MOT ten duy nhat cho moi chi so.
ACT_PURCHASE = ["onsite_conversion.purchase"]
ACT_PAYMENT = ["onsite_conversion.initiate_checkout"]
ACT_ORDER = ["onsite_conversion.messaging_order_created_v2"]
ACT_MSG = ["onsite_conversion.messaging_conversation_started_7d"]
ACT_CONTACT = ["onsite_conversion.messaging_first_reply"]
ACT_COMMENT = ["onsite_conversion.post_net_comment"]
INSIGHT_FIELDS = [
    "campaign_id",
    "campaign_name",
    "spend",
    "impressions",
    "clicks",
    "actions",
    "cost_per_action_type",
]


def load_env(path):
    env = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


LOG_DIR = Path(__file__).parent / "logs"


def log(message):
    """Ghi nhat ky moi lan chay vao logs/baocao.log (de biet task co chay hay khong)."""
    try:
        LOG_DIR.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_DIR / "baocao.log", "a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {message}\n")
    except Exception:
        pass


# --- CHONG TRUNG BAO CAO ---
# Ly do: khi may ngu/tat qua nhieu moc gio, Windows co the cho NHIEU lich
# chay bu CUNG LUC. Moi lich chay `python report.py` (khong truyen moc gio)
# nen ca bon deu tu chon moc GAN NHAT -> gui ra nhieu bao cao TRUNG NHAU.
# Giai phap: moi moc chi gui 1 lan trong ngay. Ghi lai SAU khi gui thanh cong.
DEDUP_FILE = LOG_DIR / "da_gui.json"


def _doc_da_gui():
    """Doc danh sach moc da gui thanh cong, theo tung ngay."""
    try:
        if DEDUP_FILE.exists():
            data = json.loads(DEDUP_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def ds_moc_da_gui(ngay=None):
    """Danh sach cac moc da gui THANH CONG trong mot ngay (mac dinh hom nay).

    Nguoi truc (nguoi_truc.py) doc ham nay de biet moc nao con thieu.
    File hong hoac gia tri sai kieu thi tra ve danh sach rong.
    """
    data = _doc_da_gui()
    ngay = ngay or datetime.now().strftime("%Y-%m-%d")
    ds = data.get(ngay, [])
    return list(ds) if isinstance(ds, list) else []


def da_gui_hom_nay(slot):
    """True neu moc nay da duoc gui thanh cong trong ngay hom nay."""
    return slot in ds_moc_da_gui()


def ghi_da_gui(slot):
    """Ghi lai moc vua gui THANH CONG (chi goi sau khi Telegram bao OK)."""
    try:
        LOG_DIR.mkdir(exist_ok=True)
        data = _doc_da_gui()
        today = datetime.now().strftime("%Y-%m-%d")
        # Don dep: chi giu 7 ngay gan nhat cho gon
        moc_cu = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        for k in [k for k in list(data.keys()) if k < moc_cu]:
            del data[k]
        data.setdefault(today, [])
        if slot not in data[today]:
            data[today].append(slot)
        DEDUP_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        log(f"Khong ghi duoc trang thai chong trung: {e}")


# --- CHONG LAP TIN CANH BAO LOI ---
# Ly do: khi token Meta chet, CA BA moc gio deu that bai, va moi moc Nguoi truc
# thu lai 3 lan. Ket qua that: 9 tin canh bao GIONG HET NHAU moi ngay, trong khi
# viec can lam chi co MOT (lay token moi). Dai se bo qua het, ke ca tin that.
#
# Cach lam: nho lan cuoi gui canh bao cho tung LOAI loi (loai + ma loi). Loi DAU
# TIEN cua mot loai luon duoc gui. Chi nhung lan LAP LAI moi bi chan.
CANH_BAO_FILE = LOG_DIR / "canh_bao.json"
CHO_GIUA_HAI_CANH_BAO = 12 * 3600


def _doc_canh_bao():
    """Doc so lan cuoi da gui canh bao cho tung loai loi."""
    try:
        if CANH_BAO_FILE.exists():
            d = json.loads(CANH_BAO_FILE.read_text(encoding="utf-8"))
            if isinstance(d, dict):
                return d
    except Exception:
        pass
    return {}


def _ghi_canh_bao(loai, ts):
    """Ghi lai vua gui canh bao loai nay luc nao. Khong bao gio nem loi."""
    try:
        LOG_DIR.mkdir(exist_ok=True)
        d = _doc_canh_bao()
        d[loai] = ts
        CANH_BAO_FILE.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    except Exception as e:
        log(f"Khong ghi duoc so canh bao: {e}")


def loai_canh_bao(chuoi_loi):
    """Khoa nhan dang LOAI loi, de biet hai lan loi co phai cung mot thu khong.

    Ghep ca phan loai (tam thoi / vinh vien) lan ma loi: token het han (190) va
    loi mang la hai chuyen khac nhau, khong duoc chan lan nhau.
    """
    ma = doc_ma_loi(chuoi_loi)
    return f"{phan_loai_loi(chuoi_loi)}:{ma if ma is not None else 'khong-ro'}"


def nen_gui_canh_bao(loai, now=None, doc_fn=None, ghi_fn=None):
    """True neu nen gui canh bao loai nay. Chan lap lai trong CHO_GIUA_HAI_CANH_BAO.

    `doc_fn` / `ghi_fn` tiem duoc de kiem thu khong phai cham vao file that.
    Moi truc trac deu tra ve True (gui) - bo sot mot canh bao loi te hon la
    gui thua mot tin.
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
    # Ghi lai vao file la viec PHU. Ghi khong duoc thi van phai GUI canh bao -
    # bo sot mot canh bao loi te hon la gui thua mot tin.
    try:
        ghi_fn(loai, now.strftime("%Y-%m-%d %H:%M:%S"))
    except Exception:
        pass
    return True


def send_error_alert(env, err):
    """Gui canh bao loi vao Telegram — de loi khong bao gio xay ra im lang.

    Chan lap lai: cung MOT loai loi trong vong CHO_GIUA_HAI_CANH_BAO thi khong
    gui lai. Truoc day token chet gay 9 tin canh bao giong nhau moi ngay
    (3 moc x 3 lan thu), trong khi viec can lam chi co MOT.
    """
    loai = loai_canh_bao(err)
    if not nen_gui_canh_bao(loai):
        log(f"Bo qua canh bao lap lai ({loai}) - da gui trong 12 gio qua")
        return
    msg = (
        "⚠️ BÁO CÁO META ADS GẶP LỖI\n"
        "\n"
        "Hệ thống không lấy được số liệu.\n"
        f"Lý do Meta trả về:\n{err}\n"
        "\n"
        "Cách xử lý:\n"
    )
    low = str(err).lower()
    if "expired" in low or "session has expired" in low:
        msg += (
            "→ Token Meta đã HẾT HẠN.\n"
            "→ Cần lấy token mới rồi dán lại vào file .env.\n"
            "→ Xem hướng dẫn trong file HUONG-DAN-DIEN-TOKEN.md"
        )
    elif "rate limit" in low or "too many" in low:
        msg += (
            "→ Meta tạm thời chặn (quá nhiều yêu cầu).\n"
            "→ Không cần làm gì. Hệ thống tự thử lại ở mốc giờ sau."
        )
    elif "permission" in low or "ads_read" in low:
        msg += (
            "→ Token thiếu quyền đọc quảng cáo.\n"
            "→ Khi lấy token mới, nhớ tick quyền ads_read."
        )
    else:
        msg += "→ Xem file logs/baocao.log để biết chi tiết."
    try:
        ok, err2 = send_telegram(env, msg)
        if ok:
            log("Da gui canh bao loi vao Telegram")
        else:
            log(f"Khong gui duoc canh bao Telegram: {err2}")
    except Exception as e:
        log(f"Khong gui duoc canh bao Telegram: {e}")


def _ma_nguyen(v):
    """Meta co the tra ma loi dang SO hoac dang CHUOI. Chuan hoa ve so nguyen.

    Vi sao can: so sanh `"17" in (4, 17, ...)` la False. Neu Meta doi kieu tra
    ve thi tinh nang lui dan im lang mat tac dung ma khong ai biet.
    """
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


def mo_ta_loi_meta(err):
    """Chuoi loi de doc, KEM MA LOI - de con phan loai duoc tam thoi / vinh vien.

    Truoc day chi tra ve `err['message']`, nen khong co cach nao biet loi do co
    thu lai duoc hay khong.
    """
    err = err or {}
    msg = err.get("message", "loi khong ro")
    ma = _ma_nguyen(err.get("code"))
    if ma is None:
        return f"Loi lay du lieu Meta: {msg}"
    return f"Loi lay du lieu Meta (ma {ma}): {msg}"


def doc_ma_loi(chuoi_loi):
    """Boc ma loi Meta ra khoi chuoi loi. Khong doc duoc -> None."""
    m = re.search(r"\(ma (-?\d+)\)", str(chuoi_loi or ""))
    return int(m.group(1)) if m else None


def phan_loai_loi(chuoi_loi):
    """Tra ve 'tam_thoi' hoac 'vinh_vien'.

    Mac dinh tra ve 'tam_thoi' khi khong ro: thu lai mot lan nua la vo hai, con
    tu bo mot loi that su thi bao cao im lang khong gui - te hon nhieu.
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


def api_get(path, params, ngu_fn=None):
    """Goi Meta Graph API. Tra ve (du_lieu, loi).

    Loi TAM THOI (Meta chan vi qua nhieu yeu cau) thi CHO roi thu lai, cho lau
    dan theo CHO_TRUOC_KHI_THU_LAI. Truoc day vong lap thu lai NGAY LAP TUC,
    khong cho giay nao - dung luc Meta dang chan vi qua nhieu yeu cau thi thu
    lai ngay chi ton them mot lan goi nua.

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
            # Loi rate limit thi thu lai
            if _ma_nguyen(err.get("code")) in MA_LOI_META_TAM_THOI and attempt < 2:
                ngu(CHO_TRUOC_KHI_THU_LAI[attempt])
                continue
            return None, err
        except Exception as e:
            if attempt < 2:
                ngu(CHO_TRUOC_KHI_THU_LAI[attempt])
                continue
            return None, {"message": str(e)}
    return None, {"message": "Khong the ket noi sau 3 lan thu"}


def doc_han_token_chi_tiet(env):
    """Hoi Meta xem token con song bao lau. Tra ve (so_ngay, het_han, loi).

    so_ngay = None  -> token khong bao gio het han (het_han = None).
    so_ngay = 0.0   -> token da het han / khong hop le.
    het_han         -> datetime theo GIO MAY, hoac None neu khong xac dinh duoc.

    Ham nay ra doi vi `doc_han_token` cu chi tra ve SO NGAY, khong du de tra loi
    Dai cau "het han ngay nao".
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
        return None, None, None  # token khong bao gio het han

    het_han_utc = datetime.fromtimestamp(expires_at, tz=timezone.utc)
    con_lai = het_han_utc - datetime.now(timezone.utc)
    return con_lai.total_seconds() / 86400, het_han_utc.astimezone(), None


def doc_han_token(env):
    """Nhu doc_han_token_chi_tiet nhung chi tra ve (so_ngay, loi).

    Giu lai de khong pha vo phan da chay duoc.
    """
    so_ngay, _, loi = doc_han_token_chi_tiet(env)
    return so_ngay, loi


def canh_bao_han_token(env, slot=None, danh_sach_moc=None):
    """Tra ve doan text canh bao neu token Meta sap het han, hoac '' neu khong can.

    Muc dich: bao TRUOC khi token chet, de con kip lay token moi.
    Truoc day he thong chi bao SAU khi token da chet.

    HAI MUC:
      - tu NGUONG_NHAC_NHE_NGAY (30) den NGUONG_CANH_BAO_NGAY (7): nhac nhe,
        CHI o bao cao MOC SANG - mot tin moi ngay thay vi ba tin giong nhau.
      - duoi NGUONG_CANH_BAO_NGAY (7): nhac o MOI bao cao (nhu truoc day).
      - da het han: bao do.

    `slot=None` (cach goi cu) nghia la hien o moi bao cao - giu nguyen hanh vi
    cu cho ai goi ham nay ma khong truyen moc gio.

    Ham nay KHONG BAO GIO lam hong bao cao: moi loi deu bi nuot va chi ghi nhat ky.
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
        return ""  # token khong bao gio het han

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

    # Duoi 1 ngay thi hien thi theo GIO, vi "con 0 ngay" doc rat kho hieu.
    # Lam TRON XUONG (int) chu khong lam tron gan nhat: con 44,7 ngay ma ghi
    # "45 ngày" la noi THUA thoi gian con lai - voi mot han chot thi phai noi
    # thieu, khong duoc noi thua.
    if so_ngay < 1:
        con_lai_txt = f"{so_ngay * 24:.0f} giờ"
    else:
        con_lai_txt = f"{int(so_ngay)} ngày"

    if so_ngay < NGUONG_CANH_BAO_NGAY:
        return (
            f"🟡 CẢNH BÁO TOKEN META — chỉ còn sống {con_lai_txt}{het_han_txt}\n"
            "→ Nên lấy token mới sớm, đừng chờ tới lúc nó chết.\n"
            "→ Làm theo HUONG-DAN-DIEN-TOKEN.md (Bước A → E)\n"
            "→ Chỉ lấy token mới ở MỘT máy, rồi copy file .env sang máy kia bằng USB.\n"
            "→ Hệ thống KHÔNG tự gia hạn được (đã thử 29/09/2026).\n"
        )

    # Tu 7 den 30 ngay: nhac nhe, CHI o bao cao moc sang.
    if slot is None or danh_sach_moc is None or slot != moc_sang(danh_sach_moc):
        return ""
    return (
        f"🔵 NHẮC TOKEN META — còn sống {con_lai_txt}{het_han_txt}\n"
        "→ Chưa gấp. Đây là nhắc trước để Đại xếp thời gian lấy token mới.\n"
        "→ Khi nào rảnh thì làm theo HUONG-DAN-DIEN-TOKEN.md (Bước A → E).\n"
        "→ Hệ thống KHÔNG tự gia hạn được (đã thử 29/09/2026).\n"
    )


def fmt_money(value):
    """Dinh dang tien kieu Viet Nam: 20.346.476"""
    try:
        return f"{int(round(float(value))):,}".replace(",", ".")
    except (ValueError, TypeError):
        return "0"


def chi_phi_moi_don(r):
    """Chi phi cho MOT luot mua. Tra ve None neu camp chua ra don nao.

    Con so nay quyet dinh "hieu qua" theo nghia thuc su: cung mot so tien,
    camp nao ra nhieu don hon thi re hon. Bang xep hang hien tai xep theo SO
    LUOT MUA (quy mo), khong theo chi phi moi don (hieu qua) - nen in them con
    so nay de Dai tu thay ca hai mat.

    Tra ve None chu KHONG tra ve 0 khi chua co don: chia cho 0 la vo nghia, va
    in ra "0 d moi don" se khien camp te nhat trong nhu re nhat.
    """
    try:
        so_don = int(r.get("purchase") or 0)
        if so_don <= 0:
            return None
        return float(r.get("spend", 0) or 0) / so_don
    except (ValueError, TypeError, ZeroDivisionError):
        return None


def mo_ta_moi_don(r):
    """Manh chu de noi vao cuoi dong mo ta camp. Rong neu chua co don nao."""
    cpr = chi_phi_moi_don(r)
    if cpr is None:
        return ""
    return f"; Mỗi đơn: {fmt_money(cpr)} VND"


def get_action_value(actions, action_type):
    """Lay gia tri cua MOT loai action. action_type co the la str hoac list."""
    if not actions:
        return 0
    types = [action_type] if isinstance(action_type, str) else action_type
    total = 0
    for a in actions:
        if a.get("action_type") in types:
            total += int(float(a.get("value", 0)))
    return total


def determine_period(now, slot_hour, moc_sang_bao_cao=None):
    """Tra ve (tu_ngay, den_ngay, mo_ta) theo moc gio.

    moc_sang_bao_cao: moc gio bao cao NGAY HOM TRUOC (thuong la moc nho nhat).
                      None thi dung 8 - giu dung hanh vi cu.
    """
    if moc_sang_bao_cao is None:
        moc_sang_bao_cao = MOC_SANG_MAC_DINH

    today = now.date()

    if slot_hour == moc_sang_bao_cao:
        # Bao cao ngay hom truoc
        target = today - timedelta(days=1)
        return target, target, f"{target.strftime('%d/%m/%Y')}"
    else:
        # Bao cao trong ngay, tu 0h den gio hien tai
        return today, today, (
            f"{today.strftime('%d/%m/%Y')} "
            f"(00:00 - {slot_hour:02d}:00)"
        )


def fetch_insights(env, since, until):
    """Lay insight theo campaign trong khoang thoi gian."""
    token = env["META_ADS_ACCESS_TOKEN"]
    account = env["META_AD_ACCOUNT_ID"]
    acct = account if account.startswith("act_") else f"act_{account}"

    params = {
        "access_token": token,
        "level": "campaign",
        "fields": ",".join(INSIGHT_FIELDS),
        "time_range": json.dumps({
            "since": since.strftime("%Y-%m-%d"),
            "until": until.strftime("%Y-%m-%d"),
        }),
        "limit": "500",
    }

    all_rows = []
    data, err = api_get(f"{acct}/insights", params)
    if err:
        return None, err
    all_rows.extend(data.get("data", []))

    # Lay tiep cac trang sau
    while True:
        paging = data.get("paging", {})
        next_url = paging.get("next")
        if not next_url:
            break
        try:
            with urllib.request.urlopen(next_url, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            all_rows.extend(data.get("data", []))
        except Exception:
            break

    return all_rows, None


def apply_filter(rows, include_kw, exclude_kws):
    """Loc campaign theo tu khoa."""
    include_kw = include_kw.lower().strip()
    exclude_kws = [k.strip().lower() for k in exclude_kws if k.strip()]

    result = []
    for row in rows:
        name = (row.get("campaign_name") or "").lower()

        # Phai chua tu khoa include
        if include_kw and include_kw not in name:
            continue

        # Khong duoc chua tu khoa exclude
        if any(kw in name for kw in exclude_kws):
            continue

        # Chi lay campaign co chi tieu > 0
        try:
            if float(row.get("spend", 0)) <= 0:
                continue
        except (ValueError, TypeError):
            continue

        result.append(row)

    return result


def compute_stats(env, since, until):
    """Tinh toan so lieu, tra ve dict de dung chung cho text va HTML."""
    include_kw = env.get("FILTER_INCLUDE", "")
    exclude_kws = env.get("FILTER_EXCLUDE", "").split(",")
    top_n = int(env.get("TOP_CAMPAIGN_COUNT", "5"))

    rows, err = fetch_insights(env, since, until)
    if err:
        return None, mo_ta_loi_meta(err)

    filtered = apply_filter(rows, include_kw, exclude_kws)

    def spend_of(r):
        return float(r.get("spend", 0) or 0)

    def purchase_count(r):
        return get_action_value(r.get("actions"), ACT_PURCHASE)

    totals = {
        "spend": sum(spend_of(r) for r in filtered),
        "msg": sum(get_action_value(r.get("actions"), ACT_MSG) for r in filtered),
        "contact": sum(get_action_value(r.get("actions"), ACT_CONTACT) for r in filtered),
        "order": sum(get_action_value(r.get("actions"), ACT_ORDER) for r in filtered),
        "purchase": sum(get_action_value(r.get("actions"), ACT_PURCHASE) for r in filtered),
        "payment": sum(get_action_value(r.get("actions"), ACT_PAYMENT) for r in filtered),
        "comment": sum(get_action_value(r.get("actions"), ACT_COMMENT) for r in filtered),
    }

    # Camp tot: xep theo CHI PHI MOI DON, re nhat len dau.
    #
    # Truoc 29/09/2026 cho nay xep theo SO LUOT MUA. Do la do QUY MO, khong
    # phai do HIEU QUA - trai voi chinh ten bang "hieu qua". Do tren 7 ngay
    # that (22-28/09/2026): 6/7 ngay hai cach chon ra hai DANH SACH KHAC NHAU,
    # khong chi khac thu tu. Vi du ngay 28/09: cach cu dua vao bang mot camp
    # 775.150 d/don trong khi bo sot mot camp 405.671 d/don.
    #
    # Camp moi co 1 don bi day xuong sau: 1 don chua du de noi len dieu gi,
    # mot don may man cung du de dung dau bang (da gap that: 1 don, 63.451 d -
    # re nhat ngay, nhung chi la mot don).
    def khoa_xep_hang(r):
        so_don = purchase_count(r)
        chua_du_chin = 0 if so_don >= 2 else 1
        return (chua_du_chin, spend_of(r) / so_don)

    good = sorted(
        (r for r in filtered if purchase_count(r) > 0), key=khoa_xep_hang
    )[:top_n]
    good_ids = {str(r.get("campaign_id", "")) for r in good}

    # Camp kem: uu tien chi tieu > 0 ma 0 don.
    #
    # Neu chua du top_n thi moi lay them camp co it don nhat - NHUNG BAT BUOC
    # phai loai nhung camp da nam o bang "hieu qua".
    #
    # Vi sao: bang "hieu qua" lay tu TREN xuong, bang "kem" lay tu DUOI len.
    # Danh sach ngan thi hai dau gap nhau. Da xay ra that ngay 28/09/2026: tai
    # khoan 5 camp deu co don => CA 5 nam o ca hai bang, ke ca camp tot nhat.
    # Giai doan 3 lam loi nay nang hon vi AI doc ca hai bang de viet nhan dinh,
    # thay cung mot camp vua "hieu qua" vua "kem" thi nhan dinh tu mau thuan.
    #
    # He qua chap nhan duoc: tai khoan it camp thi bang "kem" ngan lai, hoac
    # trong. Dung - vi khi do that su khong co camp nao kem ca.
    zero_result = [r for r in filtered if purchase_count(r) == 0]
    zero_result.sort(key=spend_of, reverse=True)
    low_result = [
        r for r in filtered
        if purchase_count(r) > 0 and str(r.get("campaign_id", "")) not in good_ids
    ]
    low_result.sort(key=purchase_count)
    bad = (zero_result + low_result)[:top_n]

    def pack(r, rank):
        pc = purchase_count(r)
        return {
            "rank": rank,
            "id": str(r.get("campaign_id", "")),
            "name": (r.get("campaign_name") or "").strip(),
            "spend": spend_of(r),
            "purchase": pc,
            "payment": get_action_value(r.get("actions"), ACT_PAYMENT),
            "msg": get_action_value(r.get("actions"), ACT_MSG),
            "cpr": (spend_of(r) / pc) if pc > 0 else None,
        }

    return {
        "total_campaigns": len(filtered),
        "totals": totals,
        "good": [pack(r, i + 1) for i, r in enumerate(good)],
        "bad": [pack(r, i + 1) for i, r in enumerate(bad)],
        "all": [pack(r, i + 1) for i, r in enumerate(filtered)],
        "include_kw": include_kw,
        "exclude_kw": env.get("FILTER_EXCLUDE", ""),
        "account_name": env.get("REPORT_ACCOUNT_NAME", ""),
    }, None


def build_report(env, stats, period_text, nhan_dinh=None, loi_ai=None):
    """Tao noi dung bao cao dang text tu so lieu DA TINH SAN.

    KHONG goi lai Meta API o day. So lieu duoc tinh dung 1 lan trong main()
    roi dung chung cho ca bao cao text lan dashboard HTML.

    nhan_dinh: chu do AI viet (main() goi AI roi truyen vao). None thi giu
    nguyen hanh vi cu - tuong thich nguoc tuyet doi.
    loi_ai: ly do AI khong viet duoc. In mot dong ghi chu thay cho phan nhan
    dinh, de nguoi doc biet vi sao thieu chu khong tuong bao cao bi loi.
    """
    include_kw = env.get("FILTER_INCLUDE", "")
    account_name = env.get("REPORT_ACCOUNT_NAME", "")

    totals = stats["totals"]
    good = stats["good"]
    bad = stats["bad"]

    # --- Soan bao cao ---
    lines = []
    lines.append(f"🔴 BÁO CÁO META ADS — {period_text}")
    lines.append(f"Tài khoản: {account_name}")
    lines.append("")

    lines.append("🔵 BỘ LỌC")
    lines.append(f"- Campaign có tên chứa: {include_kw}")
    lines.append(f"- Loại trừ campaign chứa: {env.get('FILTER_EXCLUDE', '')}")
    lines.append("- Chỉ lấy mục có chi tiêu > 0")
    lines.append("")

    lines.append("🔵 TÓM TẮT")
    lines.append(f"Có {stats['total_campaigns']} campaign đủ điều kiện.")
    lines.append(f"- Số tiền đã chi tiêu: {fmt_money(totals['spend'])} VND")
    lines.append(f"- Lượt bắt đầu cuộc trò chuyện qua tin nhắn: {totals['msg']}")
    lines.append(f"- Người liên hệ nhắn tin mới: {totals['contact']}")
    lines.append(f"- Đơn đặt hàng đã tạo: {totals['order']}")
    lines.append(f"- Lượt mua: {totals['purchase']}")
    lines.append(f"- Lượt thanh toán: {totals['payment']}")
    lines.append(f"- Bình luận về bài viết: {totals['comment']}")
    lines.append("")

    lines.append("🔵 NHẬN ĐỊNH")
    if nhan_dinh:
        lines.append(nhan_dinh.strip())
        lines.append("")
    elif loi_ai:
        lines.append(
            "⚠️ Phần nhận định do AI viết tạm không có "
            f"(lý do: {loi_ai})."
        )
        lines.append(
            "Số liệu ở trên vẫn đầy đủ — báo cáo không bị ảnh hưởng."
        )
        lines.append("")
    lines.append(f"Camp hiệu quả (top {len(good)}):")
    lines.append("(xếp theo chi phí mỗi đơn, rẻ nhất trước — không phải theo số đơn)")
    if good:
        for r in good:
            lines.append(f"- ID chiến dịch: {r['id']}")
            lines.append(
                f"  Lượt mua: {r['purchase']}; "
                f"Số tiền đã chi tiêu: {fmt_money(r['spend'])} VND"
                f"{mo_ta_moi_don(r)}"
            )
    else:
        lines.append("- Không có camp nào tạo ra lượt mua.")
    lines.append("")

    lines.append(f"Camp kém hiệu quả (top {len(bad)}):")
    if bad:
        for r in bad:
            lines.append(f"- ID chiến dịch: {r['id']}")
            if r["purchase"] == 0:
                lines.append(
                    f"  Không tạo ra kết quả nào; "
                    f"Đã chi tiêu: {fmt_money(r['spend'])} VND"
                )
            else:
                lines.append(
                    f"  Số tiền đã chi tiêu: {fmt_money(r['spend'])} VND; "
                    f"Kết quả tin nhắn mới: {r['msg']}; "
                    f"Lượt mua: {r['purchase']}"
                    f"{mo_ta_moi_don(r)}"
                )
    else:
        lines.append("- Không có camp nào kém hiệu quả.")
    lines.append("")

    return "\n".join(lines)


def send_telegram(env, text):
    token = env["TELEGRAM_BOT_TOKEN"]
    chat_id = env["TELEGRAM_CHAT_ID"]

    # Telegram gioi han 4096 ky tu moi tin
    chunks = []
    while len(text) > 4000:
        split_at = text.rfind("\n", 0, 4000)
        if split_at == -1:
            split_at = 4000
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    chunks.append(text)

    for i, chunk in enumerate(chunks, 1):
        payload = json.dumps({
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": True,
        }).encode("utf-8")
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            if not data.get("ok"):
                return False, data.get("description")
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            return False, f"HTTP {e.code}: {body[:200]}"
        except Exception as e:
            return False, str(e)

    return True, None


def send_telegram_document(env, filepath, filename, caption=""):
    """Gui 1 file (vi du dashboard HTML) len Telegram bang sendDocument."""
    token = env["TELEGRAM_BOT_TOKEN"]
    chat_id = env["TELEGRAM_CHAT_ID"]
    boundary = "----workbuddyboundary" + str(int(datetime.now().timestamp()))
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except Exception as e:
        return False, f"Khong doc duoc file: {e}"

    body = b""
    body += ("--%s\r\n" % boundary).encode()
    body += b'Content-Disposition: form-data; name="chat_id"\r\n\r\n'
    body += chat_id.encode() + b"\r\n"
    if caption:
        body += ("--%s\r\n" % boundary).encode()
        body += b'Content-Disposition: form-data; name="caption"\r\n\r\n'
        body += caption.encode("utf-8") + b"\r\n"
    body += ("--%s\r\n" % boundary).encode()
    body += (
        'Content-Disposition: form-data; name="document"; filename="%s"\r\n' % filename
    ).encode()
    body += b"Content-Type: text/html; charset=utf-8\r\n\r\n"
    body += data + b"\r\n"
    body += ("--%s--\r\n" % boundary).encode()

    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendDocument",
        data=body,
        headers={"Content-Type": "multipart/form-data; boundary=%s" % boundary},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            j = json.loads(resp.read().decode("utf-8"))
        if j.get("ok"):
            return True, None
        return False, j.get("description")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        return False, f"HTTP {e.code}: {err_body[:200]}"
    except Exception as e:
        return False, str(e)


def co_nen_ghi_lich_su(mock, dry):
    """Chi ghi lich su khi day la mot lan chay THAT.

    --mock va --dry khong gui bao cao, nen ban ghi cua chung khong tuong ung
    voi bao cao nao. Te hon: --dry khong truyen moc gio nen report.py tu doan
    moc, dan den lich su ghi SAI MOC (da xay ra that ngay 28/09/2026: mot lan
    chay luc 14h07 ghi thanh moc 12h).

    Vi Giai doan 3 lay lich su lam ky so sanh, ghi ban se lam AI nhan dinh sai.
    """
    return mock is None and not dry


def luu_lich_su(stats, ngay, moc, path_lich_su=None):
    """Luu so lieu vao lich su. KHONG BAO GIO nem loi ra ngoai.

    Muc dich: mot su co khi luu lich su khong duoc phep lam hong viec gui
    bao cao. Moi loi deu bi nuot va chi ghi nhat ky.
    """
    try:
        if path_lich_su is None:
            path_lich_su = LOG_DIR / "lich-su.json"
        if lich_su.ghi(path_lich_su, ngay, moc, stats) is False:
            log(f"Bo qua luu lich su {ngay}: da co ban ghi day du hon")
    except Exception as e:
        log(f"Khong luu duoc lich su: {e}")


def main():
    duong_dan_env = Path(__file__).parent / ".env"

    # Doc .env TRUOC argparse: danh sach moc gio la cua TUNG MAY, nen --slot va
    # --mock phai kiem tra theo dung danh sach do. Doc kieu "khong nem loi" de
    # `--help` van chay duoc khi chua co .env.
    env = {}
    try:
        env = load_env(duong_dan_env)
    except Exception:
        pass
    danh_sach_moc = doc_moc_tu_env(env)

    parser = argparse.ArgumentParser(description="Báo cáo Meta Ads → Telegram")
    parser.add_argument("--mock", type=int, choices=danh_sach_moc,
                        help="Chạy thử với mốc giờ này (không gửi Telegram)")
    parser.add_argument("--slot", type=int, choices=danh_sach_moc,
                        help="Mốc giờ do lịch Windows truyền vào (dùng khi gửi thật)")
    parser.add_argument("--dry", action="store_true",
                        help="Chạy thật nhưng không gửi Telegram")
    parser.add_argument("--force", action="store_true",
                        help="Gửi lại dù mốc này đã gửi hôm nay (bỏ qua chống trùng)")
    args = parser.parse_args()

    if not env:
        print(f"LOI: Khong doc duoc file .env tai {duong_dan_env}")
        print("Cach xu ly: copy .env.example thanh .env roi dien token vao.")
        sys.exit(1)

    now = datetime.now()

    if args.mock is not None:
        slot = args.mock
        print(f"[CHE DO THU] Moc gio: {slot}h")
    else:
        slot = chon_moc(args.slot, now.hour, danh_sach_moc)
        if args.slot is not None:
            print(f"Mốc giờ do lịch truyền vào: {slot}h")
        else:
            print(f"Moc gio hien tai: {slot}h (gio may: {now.hour}h)")

    # --- CHONG TRUNG: moi moc chi gui 1 lan trong ngay ---
    # (Xem giai thich o phan khai bao DEDUP_FILE phia tren.)
    # Chi ap dung khi gui that: bo qua che do thu (--mock/--dry) va khi dung --force.
    if args.mock is None and not args.dry and not args.force and da_gui_hom_nay(slot):
        print(f"[BO QUA] Moc {slot}h da duoc gui trong ngay hom nay - khong gui lai.")
        log(f"BO QUA - moc {slot}h (da gui hom nay, tranh trung)")
        sys.exit(0)

    since, until, period_text = determine_period(now, slot, moc_sang(danh_sach_moc))
    print(f"Khoang thoi gian: {since} -> {until}")
    print()
    log(f"BAT DAU - moc {slot}h, khoang {since} -> {until}")

    # --- TINH SO LIEU META API: DUNG 1 LAN DUY NHAT ---
    # Dung chung cho ca bao cao text lan dashboard HTML.
    # (Truoc day cho nay goi compute_stats() 2 lan -> ton gap doi han muc API,
    #  va so lieu tren Telegram co the lech voi file HTML vi goi 2 thoi diem khac nhau.)
    stats, err = compute_stats(env, since, until)
    if err:
        print(f"LOI: {err}")
        log(f"THAT BAI - moc {slot}h: {err}")
        loai = phan_loai_loi(err)
        if args.mock is None and not args.dry:
            send_error_alert(env, err)
        log(
            f"LOI {loai} - moc {slot}h"
            + (" (Nguoi truc se thu lai)" if loai == "tam_thoi"
               else " (Nguoi truc KHONG thu lai)")
        )
        sys.exit(MA_THOAT_TAM_THOI if loai == "tam_thoi" else MA_THOAT_VINH_VIEN)

    # Luu lich su TRUOC khi gui: neu gui loi thi so lieu van con.
    # Chi ghi khi chay THAT - --mock va --dry khong ghi (xem co_nen_ghi_lich_su).
    if co_nen_ghi_lich_su(args.mock, args.dry):
        luu_lich_su(stats, until, slot)

    # --- PHAN NHAN DINH DO AI VIET ---
    # Dat trong try: AI loi vi bat ky ly do gi cung KHONG duoc lam mat bao cao.
    # Chi bao cao TRON ngay moi co so ky truoc de so sanh.
    nhan_dinh = None
    loi_ai = None
    tron_ngay = la_bao_cao_tron_ngay(slot, danh_sach_moc)
    try:
        ky_truoc = None
        if tron_ngay:
            ky_truoc = lich_su.lay_ky_truoc(
                LOG_DIR / "lich-su.json", until, ai.SO_NGAY_KY_TRUOC
            )
        nhan_dinh, loi_ai = ai.viet_nhan_dinh(
            stats, ky_truoc, tao_boi_canh(env, period_text, tron_ngay), env=env
        )
        if loi_ai:
            log(f"AI viet nhan dinh that bai: {loi_ai}")
        else:
            log("AI da viet xong phan nhan dinh")
    except Exception as e:
        nhan_dinh = None
        loi_ai = str(e)
        log(f"AI viet nhan dinh that bai (ngoai du kien): {e}")

    # --- Canh bao SO LIEU BAT THUONG (ban thiet ke muc 7.3) ---
    # Dat SAU khi da luu lich su: cua so 7 ngay la 7 ngay TRUOC ky bao cao, nen
    # ban ghi vua luu khong lam nhieu ket qua.
    ly_do_bt = []
    try:
        ly_do_bt = bat_thuong.kiem_tra(
            stats, LOG_DIR / "lich-su.json", until, tron_ngay
        )
    except Exception as e:
        log(f"Khong kiem duoc so bat thuong: {e}")
    if ly_do_bt:
        log(f"CANH BAO so bat thuong: {'; '.join(ly_do_bt)}")

    report = build_report(env, stats, period_text, nhan_dinh, loi_ai)

    # --- Canh bao SOM neu token Meta sap het han ---
    # Dat LEN DAU bao cao de de thay, khong bi lan vao cuoi tin nhan.
    # Thu tu: token (nghiem trong nhat, Dai phai lam bang tay) -> so bat thuong
    # -> than bao cao.
    canh_bao_token = canh_bao_han_token(env, slot, danh_sach_moc)
    if canh_bao_token:
        report = canh_bao_token + "\n" + report
    canh_bao_bt = bat_thuong.canh_bao(ly_do_bt)
    if canh_bao_bt:
        report = canh_bao_bt + report

    print("=" * 60)
    print(report)
    print("=" * 60)

    # --- Tao dashboard HTML (dung lai chinh so lieu vua tinh, khong goi API lan 2) ---
    dashboard_path = None
    try:
        dashboard_path = save_dashboard(stats, since, until, period_text)
        print()
        print(f"DA TAO DASHBOARD: {dashboard_path}")
    except Exception as e:
        print(f"LOI TAO DASHBOARD: {e}")

    if args.mock is not None or args.dry:
        print()
        print("[Khong gui Telegram - che do thu]")
        sys.exit(0)

    print()
    ok, err = send_telegram(env, report)
    if ok:
        print("DA GUI BAO CAO VAO TELEGRAM")
        log(f"THANH CONG - moc {slot}h, da gui Telegram")
        ghi_da_gui(slot)  # danh dau da gui -> chan gui trung trong ngay
    else:
        print(f"LOI GUI TELEGRAM: {err}")
        log(f"THAT BAI GUI TELEGRAM - moc {slot}h: {err}")
        sys.exit(MA_THOAT_TAM_THOI)

    # --- Gui kem file dashboard HTML vao cung Telegram ---
    if dashboard_path:
        fname = f"baocao_{slot}h_{now.strftime('%d-%m-%Y')}.html"
        caption = (
            f"📊 BÁO CÁO META ADS — {period_text}\n"
            "Bản đầy đủ dạng HTML. Tải về và mở bằng trình duyệt để xem."
        )
        dok, derr = send_telegram_document(env, dashboard_path, fname, caption)
        if dok:
            print("DA GUI FILE HTML VAO TELEGRAM")
            log(f"THANH CONG - moc {slot}h, da gui file HTML")
        else:
            print(f"LOI GUI FILE HTML: {derr}")
            log(f"THAT BAI GUI FILE HTML - moc {slot}h: {derr}")


if __name__ == "__main__":
    main()
