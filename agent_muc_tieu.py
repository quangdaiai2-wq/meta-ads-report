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

# 🔴 RANH GIOI TAT LE QUANG CAO — Dai chot 15:5x 02/10/2026, nguyen van:
#     "Bao gio co tu 02 quang cao tro len trong nhom thi tu dong chuyen sang
#      xet duyet nhu vay."
#
# TAT LE chi co nghia khi CO THU DE BAO VE — mot quang cao khac dang con co hoi.
# Nhom chi co 1 quang cao thi tat le cung lam nhom ngung chi tieu y nhu tat
# nhom, NHUNG so lai KHONG DOI o lan quet sau (vi ad = 100% chi tieu nhom, VA
# insights THANG con giu dong lich su cua ad da tat) => de xuat LAP VO TAN,
# nhom khong bao gio bi tat, ngan sach khong bao gio ha.
#
# DO THAT 02/10/2026 tren 82 nhom thuoc pham vi Dai:
#     66 nhom 0 quang cao | 16 nhom DUNG 1 quang cao | 0 nhom >= 2
#   Ca 16 nhom mot-quang-cao deu co chi tieu ad = 100,0% chi tieu nhom
#   (vd nhom 120250213748540509: nhom 779.615d, ad 779.615d).
SO_AD_TOI_THIEU_DE_TAT_LE = 2

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


def _goc_khong():
    """Bo so 0 dung chung — de khong lap lai dict o nhieu noi."""
    return {"spend": 0, "luot_mua": 0, "tin_nhan": 0, "lien_he": 0}


def _so_khong(dong):
    """Mot dong insights -> dict gon, thieu thi coi nhu 0."""
    return rut_so_mot_dong(dong) or _goc_khong()


def gom_theo_nhom(ds_dong_ad):
    """{adset_id: [dong ad, ...]} — sap xep chi tieu GIAM DAN trong moi nhom.

    Sap giam dan de quang cao chi nhieu nhat duoc xet truoc => de xuat dang chu
    y nhat len dau danh sach.

    ⚠️ Dong thieu `adset_id` bi BO QUA — khong biet no thuoc nhom nao thi khong
    the kiem pham vi (quy tac sat: pham vi kiem theo TEN NHOM). Bo qua la DUNG,
    khong phai thieu sot.
    """
    gom = {}
    if not isinstance(ds_dong_ad, (list, tuple)):
        return gom
    for d in ds_dong_ad:
        if not isinstance(d, dict):
            continue
        k = str(d.get("adset_id") or "")
        if not k:
            continue
        gom.setdefault(k, []).append(d)
    for k in gom:
        gom[k].sort(key=lambda z: -(_so(z.get("spend")) or 0))
    return gom


def _xet_nguong(chi_hom_nay, chi_thang, mua_thang, co_tin_nhan, la_gi=None):
    """Ap BA truong hop TH3 -> TH2 -> TH1. Tra ve (th, ly_do, uu_tien, cpr)
    hoac None neu chua cham nguong.

    VIEC B — Dai chot 02/10/2026
    ==========================================================================
    Dai chot: moi quang cao TU CHON MOC CUA CHINH NO, khong muon moc cua nhom.
    Nhung BO QUY TAC thi GIONG HET nhau.

    => Neu viet hai doan code rieng cho nhom va cho quang cao thi som muon cung
    LECH NHAU. Mot ham dung chung bao dam khong the lech.

    `la_gi` chi de chen vao cau ly do cho de doc ('nhóm' / 'quảng cáo').
    """
    ai = f" {la_gi}" if la_gi else ""
    if mua_thang >= 1:
        # ---- TH3: da co luot mua. Xet gia moi luot mua TINH THEO THANG ----
        cpr = chi_thang / mua_thang
        if cpr < MOC_CPR:
            return None
        return (3,
                f"Đã có {mua_thang} lượt mua tháng này, chi {tien(chi_thang)} "
                f"=> {tien(cpr)}/lượt, chạm mốc {tien(MOC_CPR)}",
                cpr, cpr)
    if co_tin_nhan:
        # ---- TH2: co tin nhan nhung chua ra luot mua ----
        if chi_hom_nay < NGUONG_TH2:
            return None
        return (2,
                f"{ai.strip().capitalize() or 'Hôm nay'} chi {tien(chi_hom_nay)}, "
                f"có tin nhắn nhưng 0 lượt mua (ngưỡng {tien(NGUONG_TH2)})",
                NGUONG_TH2 + chi_hom_nay, None)
    # ---- TH1: khong co tin nhan nao ----
    if chi_hom_nay < NGUONG_TH1:
        return None
    return (1,
            f"{ai.strip().capitalize() or 'Hôm nay'} chi {tien(chi_hom_nay)}, "
            f"không có tin nhắn nào (ngưỡng {tien(NGUONG_TH1)})",
            NGUONG_TH1 + chi_hom_nay, None)


def _de_xuat_ad(dong_ad, ten_nhom, truong_hop, chi_hom_nay, mua_thang,
                ly_do, uu_tien, cpr, bay_gio):
    """Dung mot de xuat cap QUANG CAO.

    ⚠️ `ten_nhom` la TEN NHOM chua quang cao — dung de:
       (a) kiem pham vi (KHONG dung ten quang cao, xem quy tac sat)
       (b) lay hau to cho ten quang cao moi (quang cao dung chung hau to voi nhom)
    """
    ma_ad = str(dong_ad.get("ad_id") or "")
    ten_ad = dong_ad.get("ad_name") or ""
    return {
        "hanh_dong": "tam_dung",
        "truong_hop": truong_hop,
        "doi_tuong": {
            "cap": "ad",
            "id": ma_ad,
            "ten": ten_ad,
            # 🔴 Truong nay la BAT BUOC: noi goi phai doc lai TEN NHOM nay
            #    roi kiem thuoc_pham_vi TRUOC khi ghi len Meta.
            "adset_id": str(dong_ad.get("adset_id") or ""),
            "ten_nhom": ten_nhom,
            "campaign_id": dong_ad.get("campaign_id"),
        },
        # Quang cao dung CHUNG hau to voi NHOM chua no (Dai chot 02/10/2026).
        "ten_moi": ten_moi(ten_ad, truong_hop, chi_hom_nay, mua_thang, bay_gio),
        "chi_tieu_thang": _so(dong_ad.get("spend")) or 0,
        "chi_tieu_hom_nay": chi_hom_nay,
        "luot_mua": mua_thang,
        "tin_nhan": 0,
        "chi_phi_moi_luot": cpr,
        # 🔴 Tat le quang cao KHONG ha ngan sach. None = khong dung toi.
        "ngan_sach_ha": None,
        "ly_do": ly_do,
        "_uu_tien": uu_tien,
    }


def xet(nhom, chi_tieu_hom_nay=None, chi_tieu_thang=None, loai_ten=None,
        bay_gio=None, ad_hom_nay=None, ad_thang=None):
    """Tra ve danh sach de xuat, da sap xep dang chu y nhat truoc.

    nhom              : danh sach tu /act_X/adsets (co id, name, effective_status,
                        daily_budget). Chi nhom ACTIVE moi duoc xet.
    chi_tieu_hom_nay  : {adset_id: dong insights hom nay}
    chi_tieu_thang    : {adset_id: dong insights thang nay}
    loai_ten          : danh sach tu khoa loai (tu FILTER_EXCLUDE)
    bay_gio           : thoi diem chay — dung de ghi so thang vao ten moi
    ad_hom_nay        : {ad_id: dong insights hom nay}    <-- MOI (Viec B)
    ad_thang          : {ad_id: dong insights thang nay}  <-- MOI (Viec B)
    """
    if not isinstance(nhom, (list, tuple)):
        return []
    hom_nay = chi_tieu_hom_nay if isinstance(chi_tieu_hom_nay, dict) else {}
    thang = chi_tieu_thang if isinstance(chi_tieu_thang, dict) else {}
    ad_h = ad_hom_nay if isinstance(ad_hom_nay, dict) else {}
    ad_t = ad_thang if isinstance(ad_thang, dict) else {}

    # Gom quang cao ve theo nhom MOT LAN cho ca tai khoan (re hon goi tung nhom).
    theo_nhom = gom_theo_nhom([d for d in ad_t.values() if isinstance(d, dict)])
    theo_nhom_hom = gom_theo_nhom([d for d in ad_h.values() if isinstance(d, dict)])

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

        t = _so_khong(thang.get(ma))
        h = _so_khong(hom_nay.get(ma))
        mua_thang, chi_thang = t["luot_mua"], t["spend"]
        chi_hom_nay = h["spend"]
        co_tin_nhan = (h["tin_nhan"] + h["lien_he"]) > 0

        # ---- 1. Danh sach quang cao cua nhom nay (Viec B) ----
        ds_ad = []
        for d in theo_nhom.get(ma, []):
            ma_ad = str(d.get("ad_id") or "")
            ha = _so_khong(ad_h.get(ma_ad))
            ds_ad.append({
                "dong": d,
                "chi_hom_nay": ha["spend"],
                "chi_thang": _so(d.get("spend")) or 0,
                "mua_thang": dem_mot_loai(d.get("actions"), TEN_LUOT_MUA),
                "co_tin_nhan": (ha["tin_nhan"] + ha["lien_he"]) > 0,
            })

        # ---- 2. Xet NHOM ----
        kq_nhom = _xet_nguong(chi_hom_nay, chi_thang, mua_thang, co_tin_nhan,
                              la_gi="nhóm")

        # ---- 3. Xet tung QUANG CAO (neu nhom du quang cao de tat le) ----
        de_xuat_ad = []
        if len(ds_ad) >= SO_AD_TOI_THIEU_DE_TAT_LE:
            for x in ds_ad:
                kq = _xet_nguong(x["chi_hom_nay"], x["chi_thang"],
                                 x["mua_thang"], x["co_tin_nhan"],
                                 la_gi="quảng cáo")
                if kq is None:
                    continue
                th, ly, uu, cpr = kq
                de = _de_xuat_ad(x["dong"], ten, th, x["chi_hom_nay"],
                                 x["mua_thang"], ly, uu, cpr, bay_gio)
                if de["doi_tuong"]["id"]:
                    de_xuat_ad.append(de)

        if kq_nhom is not None:
            th, ly, uu, cpr = kq_nhom
            if de_xuat_ad:
                # Nhom >=2 quang cao VA co quang cao cham => TAT LE, giu nhom.
                ra.extend(de_xuat_ad)
                continue
            # Con lai (nhom 0/1 quang cao, hoac >=2 ma khong ad nao cham) =>
            # TAT CA NHOM — ngan sach ha, ten doi.
            ra.append({
                "hanh_dong": "tam_dung",
                "truong_hop": th,
                "doi_tuong": {
                    "cap": "ad_set",
                    "id": ma,
                    "ten": ten,
                    "campaign_id": a.get("campaign_id"),
                    "ngan_sach_ngay_vnd": _so(a.get("daily_budget")),
                },
                "ten_moi": ten_moi(ten, th, chi_hom_nay, mua_thang, bay_gio),
                "chi_tieu_thang": chi_thang,
                "chi_tieu_hom_nay": chi_hom_nay,
                "luot_mua": mua_thang,
                "tin_nhan": h["tin_nhan"] + h["lien_he"],
                "chi_phi_moi_luot": cpr,
                "ngan_sach_ha": NGAN_SACH_HA,
                "ly_do": ly,
                "_uu_tien": uu,
            })
            continue

        # Nhom CHUA cham: van co the tat le quang cao cham (neu nhom >=2 ad).
        ra.extend(de_xuat_ad)

    ra.sort(key=lambda z: -z["_uu_tien"])
    return ra
