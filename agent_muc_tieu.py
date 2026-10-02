"""Tinh ra danh sach nhom DANG DE XUAT TAT. Chi doc so, khong goi AI.

BA TRUONG HOP — Dai chot 01/10/2026. Xet theo THU TU TH3 -> TH2 -> TH1,
nhom co luot mua LUON roi vao TH3 du no co tin nhan hay khong:

  TH1  KHONG co tin nhan nao (ca lien he lan bat dau tro chuyen deu = 0)
       -> chi tieu HOM NAY >= 70.000d
  TH2  CO tin nhan (>=1) nhung CHUA ra luot mua
       -> chi tieu HOM NAY >= 290.000d
  TH3  DA co luot mua (du co tin nhan hay khong)
       -> gia moi luot mua TINH THEO THANG >= 390.000d

Vi sao khong dung logs/lich-su.json: file do chi co cap CHIEN DICH, khong co
cap NHOM quang cao. Nhung ngan sach va nguong cua Dai nam o cap nhom.

BAY DA GAP THAT khi dung thu 30/09/2026:
  - Meta tra `spend` va `value` dang CHUOI, khong phai so.
  - Lay chi tieu CA THANG cho nguong TRONG NGAY => 298 de xuat sai.
  - Khong loc nhom dang chay + khong loai nhom thuong hieu => de xuat rac.
Ca ba deu da duoc chan trong file nay.
"""
import re
from datetime import datetime

from agent_rao import (GIO_VN, MOC_CPR, NGAN_SACH_HA, _so, thuoc_pham_vi,
                       tien)

# Nguong TRONG NGAY (Dai noi "chi tieu trong ngay").
NGUONG_TH1 = 70000         # TH1: khong co tin nhan nao
NGUONG_TH2 = 290000        # TH2: co tin nhan nhung chua ra luot mua

# Cot moc CHAN ghi vao ten nhom khi tat. TH2/TH3 dung so co dinh.
MOC_CHAN_TH2 = 350000
MOC_CHAN_TH3 = 450000

# Meta tra ve NHIEU ten cho CUNG mot luot mua. Chi duoc dung MOT ten, neu khong
# se dem trung gap 5 lan. Bay da gap that ngay 30/09/2026.
TEN_LUOT_MUA = "onsite_conversion.purchase"
TEN_TIN_NHAN = "onsite_conversion.messaging_conversation_started_7d"
TEN_LIEN_HE = "onsite_conversion.messaging_first_reply"

# Ten mac dinh do Meta tu sinh - khong phai viec cua Dai.
TEN_MAC_DINH = ("quảng cáo lượt tương tác mới", "nhóm quảng cáo lượt tương tác mới",
                "chiến dịch lượt tương tác mới")

# Phan hau to cu trong ten nhom: " 0/160 X9", " 0/300 X8-26 TN", " 11/450 X10-26",
# " 0/500 X11 => Lỗi".
#
# 🔴 SUA 02/10/2026 — Dai chot ten moi PHAI kem NAM, dang GACH NOI (X10-26):
#   - do that: 396 ten nhom dung "X9-26", 0 ten dung "X9 26"  => gach noi
#   - rieng nhanh "=> <chu>" la LOI DUNG THU BAT DUOC: ten "... X11 => Lỗi" CO THAT
#     tren tai khoan (2 nhom). Khong cat duoc thi tat lan hai se CHONG TEN.
RE_HAU_TO = re.compile(
    r"\s+\d+\s*/\s*\d+(\s+X\d+(-\d+)?)?(\s+[A-Za-zÀ-ỹ]+)*(\s*=>\s*[^\s]+)?\s*$")


def dem_mot_loai(actions, ten):
    """Dem dung MOT loai hanh dong. Khong cong don nhieu ten."""
    if not isinstance(actions, list):
        return 0
    for a in actions:
        if isinstance(a, dict) and a.get("action_type") == ten:
            v = _so(a.get("value"))
            return int(v) if v is not None else 0
    return 0


def rut_so_mot_dong(row):
    """Tu mot dong insights cua Meta -> dict gon. Doc khong duoc -> None."""
    if not isinstance(row, dict):
        return None
    spend = _so(row.get("spend"))
    if spend is None:
        return None
    acts = row.get("actions")
    return {
        "id": str(row.get("adset_id") or row.get("id") or ""),
        "ten": str(row.get("adset_name") or row.get("name") or ""),
        "spend": spend,
        "luot_mua": dem_mot_loai(acts, TEN_LUOT_MUA),
        "tin_nhan": dem_mot_loai(acts, TEN_TIN_NHAN),
        "lien_he": dem_mot_loai(acts, TEN_LIEN_HE),
    }


def _bi_loai_ten(ten, loai_ten):
    """True neu ten chua tu khoa can loai (thuonghieu / thương hiệu / Brand)."""
    if not loai_ten:
        return False
    tl = (ten or "").lower()
    return any(str(x).strip().lower() in tl for x in loai_ten if str(x).strip())


def _la_ten_mac_dinh(ten):
    tl = (ten or "").lower()
    return any(x in tl for x in TEN_MAC_DINH)


def bo_hau_to_cu(ten):
    """Cat phan 'x/y X<n>' cu ra khoi ten nhom. Khong co thi tra ve nguyen ten.

    Vi sao phai cat: neu khong, tat lan hai se ra ten kieu
    '... Online 0/160 X9 0/140 X10' — chong hai lan.
    """
    if not isinstance(ten, str):
        return ""
    return RE_HAU_TO.sub("", ten).strip()


def _duoi_thoi_gian(bay_gio=None):
    """Hau to thoi gian: 'X<thang>-<2 chu so nam>'. Vi du 02/10/2026 -> 'X10-26'.

    Dai giai ma 02/10/2026: "X9-26 nghia la tat vao thang 9 nam 2026".
    => X<n> la THANG DAT TEN, khong phai "lan thu n", khong phai thang tao nhom.
       Kiem chung 14/14 ca khop bang /activities.
    """
    t = bay_gio if isinstance(bay_gio, datetime) else datetime.now(GIO_VN)
    return f"X{t.month}-{t.year % 100:02d}"


def ten_moi(ten_goc, truong_hop, chi_hom_nay, mua_thang, bay_gio=None):
    """Ten nhom sau khi tat, theo dung quy uoc cua Dai.

    TH1: 0/<gap doi chi tieu> X<thang>-<nam>     vi du  0/140 X10-26
    TH2: 0/350 X<thang>-<nam> TN                 vi du  0/350 X10-26 TN
    TH3: <luot mua thang>/450 X<thang>-<nam>     vi du  1/450 X10-26

    🔴 CA BA truong hop deu ghi nam (Dai chot 02/10/2026). Luat cu
    "TH1 khong ghi nam" DA BO.
    """
    goc = bo_hau_to_cu(ten_goc)
    duoi = _duoi_thoi_gian(bay_gio)
    if truong_hop == 1:
        # Gap doi so tien DANG chi tieu (khong phai gap doi nguong).
        moc = int(round(float(chi_hom_nay or 0) * 2))
        return f"{goc} 0/{moc // 1000} {duoi}"
    if truong_hop == 2:
        return f"{goc} 0/{MOC_CHAN_TH2 // 1000} {duoi} TN"
    if truong_hop == 3:
        return f"{goc} {int(mua_thang or 0)}/{MOC_CHAN_TH3 // 1000} {duoi}"
    # LOI DUNG THU BAT DUOC: truong_hop la thi AM THAM roi vao TH3 (0/450).
    # Nay nem loi ro rang de khong tao ten sai ma khong ai biet.
    raise ValueError(f"truong_hop khong hop le: {truong_hop!r} (chi nhan 1/2/3)")


def xet(nhom, chi_tieu_hom_nay=None, chi_tieu_thang=None, loai_ten=None,
        bay_gio=None):
    """Tra ve danh sach de xuat, da sap xep dang chu y nhat truoc.

    nhom              : danh sach tu /act_X/adsets (co id, name, effective_status,
                        daily_budget). Chi nhom ACTIVE moi duoc xet.
    chi_tieu_hom_nay  : {adset_id: dong insights hom nay}
    chi_tieu_thang    : {adset_id: dong insights thang nay}
    loai_ten          : danh sach tu khoa loai (tu FILTER_EXCLUDE)
    bay_gio           : thoi diem chay — dung de ghi so thang vao ten moi
    """
    if not isinstance(nhom, (list, tuple)):
        return []
    hom_nay = chi_tieu_hom_nay if isinstance(chi_tieu_hom_nay, dict) else {}
    thang = chi_tieu_thang if isinstance(chi_tieu_thang, dict) else {}

    ra = []
    for a in nhom:
        if not isinstance(a, dict):
            continue
        if a.get("effective_status") != "ACTIVE":
            continue
        ma = str(a.get("id") or "")
        ten = a.get("name") or ""
        if not ma or not thuoc_pham_vi(ten) or _bi_loai_ten(ten, loai_ten):
            continue
        if _la_ten_mac_dinh(ten):
            continue

        t = rut_so_mot_dong(thang.get(ma)) or {"spend": 0, "luot_mua": 0,
                                               "tin_nhan": 0, "lien_he": 0}
        h = rut_so_mot_dong(hom_nay.get(ma)) or {"spend": 0, "luot_mua": 0,
                                                 "tin_nhan": 0, "lien_he": 0}
        mua_thang, chi_thang = t["luot_mua"], t["spend"]
        chi_hom_nay = h["spend"]
        co_tin_nhan = (h["tin_nhan"] + h["lien_he"]) > 0

        if mua_thang >= 1:
            # ---- TH3: da co luot mua. Xet gia moi luot mua TINH THEO THANG ----
            cpr = chi_thang / mua_thang
            if cpr < MOC_CPR:
                continue
            truong_hop = 3
            ly_do = (f"Đã có {mua_thang} lượt mua tháng này, chi {tien(chi_thang)} "
                     f"=> {tien(cpr)}/lượt, chạm mốc {tien(MOC_CPR)}")
            uu_tien = cpr
        elif co_tin_nhan:
            # ---- TH2: co tin nhan nhung chua ra luot mua ----
            if chi_hom_nay < NGUONG_TH2:
                continue
            truong_hop = 2
            ly_do = (f"Hôm nay chi {tien(chi_hom_nay)}, có tin nhắn nhưng 0 lượt mua "
                     f"(ngưỡng {tien(NGUONG_TH2)})")
            uu_tien = NGUONG_TH2 + chi_hom_nay
        else:
            # ---- TH1: khong co tin nhan nao ----
            if chi_hom_nay < NGUONG_TH1:
                continue
            truong_hop = 1
            ly_do = (f"Hôm nay chi {tien(chi_hom_nay)}, không có tin nhắn nào "
                     f"(ngưỡng {tien(NGUONG_TH1)})")
            uu_tien = NGUONG_TH1 + chi_hom_nay

        ra.append({
            "hanh_dong": "tam_dung",
            "truong_hop": truong_hop,
            "doi_tuong": {
                "cap": "ad_set",
                "id": ma,
                "ten": ten,
                "campaign_id": a.get("campaign_id"),
                "ngan_sach_ngay_vnd": _so(a.get("daily_budget")),
            },
            "ten_moi": ten_moi(ten, truong_hop, chi_hom_nay, mua_thang, bay_gio),
            "chi_tieu_thang": chi_thang,
            "chi_tieu_hom_nay": chi_hom_nay,
            "luot_mua": mua_thang,
            "tin_nhan": h["tin_nhan"] + h["lien_he"],
            "chi_phi_moi_luot": (chi_thang / mua_thang) if mua_thang else None,
            "ngan_sach_ha": NGAN_SACH_HA,
            "ly_do": ly_do,
            "_uu_tien": uu_tien,
        })

    ra.sort(key=lambda z: -z["_uu_tien"])
    return ra
