"""Rao kiem de xuat cua AI (nac 1).

Nguyen tac: AI DE XUAT, CODE QUYET DINH. Giong tinh than "phep so sanh do code lam"
trong ai.py - khi giao cho AI mot viec ma no de lam sai, hay lay lai.

Dac biet: AI chi duoc tra ve `id` va cau ly do. TEN va SO TIEN do CODE dien tu `stats`.
Nho vay AI khong the bia so, ke ca khi no muon.

Ham thuan: khong goi mang, khong doc file -> kiem thu duoc tung truong hop.
Day la tien than cua rao_an_toan.py o nac 3, nen viet tach rieng ngay tu bay gio.
"""

# Chi cho phep MOT viec o nac 1. Nac 3 se mo rong danh sach nay.
VIEC_CHO_PHEP = ("tam_dung",)

NGUONG_CHI_MAC_DINH = 200000
TOI_DA_MAC_DINH = 3


def _so_nguyen(v, mac_dinh):
    """Doc mot so nguyen tu chuoi cau hinh. Sai gi -> tra ve mac dinh."""
    try:
        return int(str(v).strip())
    except (ValueError, TypeError, AttributeError):
        return mac_dinh


def doc_cau_hinh(env):
    """Doc nguong chi va so de xuat toi da tu .env. Thieu thi dung mac dinh.

    Khong bao gio nem loi: .env sai dinh dang thi quay ve mac dinh.
    """
    env = env or {}
    nguong = _so_nguyen(env.get("DE_XUAT_NGUONG_CHI"), NGUONG_CHI_MAC_DINH)
    toi_da = _so_nguyen(env.get("DE_XUAT_TOI_DA"), TOI_DA_MAC_DINH)
    return max(0, nguong), max(0, toi_da)


def _tim_camp(stats, ma):
    """Tim chien dich theo ma trong stats['all']. Khong thay -> None."""
    for c in ((stats or {}).get("all") or []):
        if not isinstance(c, dict):
            continue
        if str(c.get("id", "")) == ma:
            return c
    return None


def kiem(ds_tho, stats, env=None):
    """Loc danh sach de xuat AI tra ve. Tra ve (hop_le, bi_loai).

    hop_le: danh sach dict da lam sach, moi phan tu gom
            {"id", "ten", "spend", "purchase", "viec", "ly_do"}
            - `ten`, `spend`, `purchase` lay TU CODE, khong lay tu AI.
    bi_loai: danh sach (de_xuat_tho, ly_do_bi_loai) de ghi nhat ky.

    KHONG BAO GIO nem loi.
    """
    nguong, toi_da = doc_cau_hinh(env)

    if not isinstance(ds_tho, (list, tuple)):
        return [], [(ds_tho, "khong phai danh sach")]

    hop_le = []
    bi_loai = []
    da_gap = set()

    for dx in ds_tho:
        if not isinstance(dx, dict):
            bi_loai.append((dx, "khong phai kieu dict"))
            continue

        ma = dx.get("id")
        if not isinstance(ma, str) or not ma.strip():
            bi_loai.append((dx, "thieu id"))
            continue
        ma = ma.strip()

        viec = str(dx.get("viec", "")).strip()
        if viec not in VIEC_CHO_PHEP:
            bi_loai.append((dx, f"viec khong duoc phep: {viec or '(rong)'}"))
            continue

        camp = _tim_camp(stats, ma)
        if camp is None:
            bi_loai.append((dx, f"id khong co trong du lieu: {ma}"))
            continue

        so_don = int(camp.get("purchase") or 0)
        if so_don > 0:
            bi_loai.append((dx, f"camp da co {so_don} don"))
            continue

        chi = float(camp.get("spend") or 0)
        if chi < nguong:
            bi_loai.append((dx, f"chi {chi:.0f} < nguong {nguong}"))
            continue

        if ma in da_gap:
            bi_loai.append((dx, "trung id"))
            continue

        if len(hop_le) >= toi_da:
            bi_loai.append((dx, f"vuot qua so de xuat toi da ({toi_da})"))
            continue

        da_gap.add(ma)
        hop_le.append({
            "id": ma,
            "ten": str(camp.get("name") or "").strip(),
            "spend": chi,
            "purchase": so_don,
            "viec": viec,
            "ly_do": str(dx.get("ly_do", "") or "").strip(),
        })

    return hop_le, bi_loai
