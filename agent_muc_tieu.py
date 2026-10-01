"""Tinh ra danh sach nhom DANG DE XUAT TAT. Chi doc so, khong goi AI.

Vi sao khong dung logs/lich-su.json: file do chi co cap CHIEN DICH
(id, name, spend, purchase, payment, msg, cpr), khong co cap NHOM quang cao.
Nhung ngan sach va nguong cua Dai nam o cap nhom. Nen phai doc thang tu Meta
o level=adset. (Ban thiet ke 28/09 da canh bao truoc cho nay.)

BAY DA GAP THAT khi dung thu 30/09/2026:
  - Meta tra `spend` va `value` dang CHUOI, khong phai so.
  - Lay chi tieu CA THANG cho nguong TRONG NGAY => 298 de xuat sai.
  - Khong loc nhom dang chay + khong loai nhom thuong hieu => de xuat rac.
Ca ba deu da duoc chan trong file nay.
"""
from agent_rao import MOC_CPR, NGAN_SACH_HA, _so, thuoc_pham_vi, tien

# Nguong TRONG NGAY (Dai noi "chi tieu trong ngay" - C3, 30/09/2026)
NGUONG_CO_TIN = 70000      # co tin nhan nhung 0 luot mua
NGUONG_KHONG_TIN = 80000   # khong co tin nhan nao

# Meta tra ve NHIEU ten cho CUNG mot luot mua. Chi duoc dung MOT ten, neu khong
# se dem trung gap 5 lan. Bay da gap that ngay 30/09/2026.
TEN_LUOT_MUA = "onsite_conversion.purchase"
TEN_TIN_NHAN = "onsite_conversion.messaging_conversation_started_7d"

# Ten mac dinh do Meta tu sinh - khong phai viec cua Dai.
TEN_MAC_DINH = ("quảng cáo lượt tương tác mới", "nhóm quảng cáo lượt tương tác mới",
                "chiến dịch lượt tương tác mới")


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


def xet(nhom, chi_tieu_hom_nay=None, chi_tieu_thang=None, loai_ten=None):
    """Tra ve danh sach de xuat, da sap xep dang chu y nhat truoc.

    nhom              : danh sach tu /act_X/adsets (co id, name, effective_status,
                        daily_budget). Chi nhom ACTIVE moi duoc xet.
    chi_tieu_hom_nay  : {adset_id: dong insights hom nay}
    chi_tieu_thang    : {adset_id: dong insights thang nay}
    loai_ten          : danh sach tu khoa loai (tu FILTER_EXCLUDE)
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

        t = rut_so_mot_dong(thang.get(ma)) or {"spend": 0, "luot_mua": 0, "tin_nhan": 0}
        h = rut_so_mot_dong(hom_nay.get(ma)) or {"spend": 0, "luot_mua": 0, "tin_nhan": 0}
        mua_thang, chi_thang = t["luot_mua"], t["spend"]
        chi_hom_nay, tin_hom_nay = h["spend"], h["tin_nhan"]

        if mua_thang >= 1:
            # Chi so CA THANG: chi phi trung binh moi luot mua
            cpr = chi_thang / mua_thang
            if cpr < MOC_CPR:
                continue
            ly_do = (f"Chi {tien(chi_thang)} cho {mua_thang} lượt mua tháng này "
                     f"=> {tien(cpr)}/lượt, chạm mốc {tien(MOC_CPR)}")
            uu_tien = cpr
        elif tin_hom_nay > 0:
            # Chi so TRONG NGAY: co tin nhan nhung chua ra luot mua
            if chi_hom_nay < NGUONG_CO_TIN:
                continue
            ly_do = (f"Hôm nay chi {tien(chi_hom_nay)}, có {tin_hom_nay} tin nhắn "
                     f"nhưng 0 lượt mua (ngưỡng {tien(NGUONG_CO_TIN)})")
            uu_tien = NGUONG_CO_TIN + chi_hom_nay
        else:
            # Chi so TRONG NGAY: khong co tin nhan nao
            if chi_hom_nay < NGUONG_KHONG_TIN:
                continue
            ly_do = (f"Hôm nay chi {tien(chi_hom_nay)}, không có tin nhắn nào "
                     f"(ngưỡng {tien(NGUONG_KHONG_TIN)})")
            uu_tien = NGUONG_KHONG_TIN + chi_hom_nay

        ra.append({
            "hanh_dong": "tam_dung",
            "doi_tuong": {
                "cap": "ad_set",
                "id": ma,
                "ten": ten,
                "ngan_sach_ngay_vnd": _so(a.get("daily_budget")),
            },
            "chi_tieu_thang": chi_thang,
            "chi_tieu_hom_nay": chi_hom_nay,
            "luot_mua": mua_thang,
            "tin_nhan": tin_hom_nay,
            "chi_phi_moi_luot": (chi_thang / mua_thang) if mua_thang else None,
            "ngan_sach_ha": NGAN_SACH_HA,
            "ly_do": ly_do,
            "_uu_tien": uu_tien,
        })

    ra.sort(key=lambda z: -z["_uu_tien"])
    return ra
