"""Cong cu GHI len Meta. Day la cho duy nhat agent cham duoc vao tien that.

Dong tac tat nhom cua Dai la HAI viec, khong phai mot (do that tren 75 lan):
  72/75 lan ha ngan sach ve 27.000d DI KEM tat nhom, lech nhau trung vi 6 giay.
  75/75 lan gia tri ngan sach truoc do la 400.000d.
Nen o day lam ca hai trong MOT lan goi, roi DOC LAI de kiem.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

import report
from agent_rao import NGAN_SACH_HA

API_VERSION = "v21.0"
GRAPH = f"https://graph.facebook.com/{API_VERSION}"


def api_post(path, params, ngu_fn=None):
    """Goi POST len Meta. Tra ve (du_lieu, loi). Loi tam thoi thi thu lai."""
    ngu = ngu_fn or time.sleep
    url = f"{GRAPH}/{path}"
    body = urllib.parse.urlencode(params).encode("utf-8")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=body)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8")), None
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8", errors="ignore")
            try:
                err = json.loads(raw).get("error", {})
            except ValueError:
                err = {"message": f"HTTP {e.code}"}
            if report._ma_nguyen(err.get("code")) in report.MA_LOI_META_TAM_THOI \
                    and attempt < 2:
                ngu(report.CHO_TRUOC_KHI_THU_LAI[attempt])
                continue
            return None, err
        except Exception as e:
            if attempt < 2:
                ngu(report.CHO_TRUOC_KHI_THU_LAI[attempt])
                continue
            return None, {"message": str(e)}
    return None, {"message": "Khong the ket noi sau 3 lan thu"}


def doc_lai_nhom(env, ma_nhom):
    """Doc trang thai + ngan sach hien tai cua nhom. Tra ve (dict, loi)."""
    tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
    if not tok:
        return None, {"message": "thieu META_ADS_ACCESS_TOKEN trong .env"}
    return report.api_get(
        ma_nhom,
        {"access_token": tok, "fields": "id,name,status,effective_status,daily_budget"})


def _doi_trang_thai_va_ngan_sach(env, ma_nhom, trang_thai, ngan_sach, ngu_fn=None):
    """Doi trang thai + dat ngan sach, roi DOC LAI kiem.

    Tra ve (thanh_cong: bool, ket_qua: str, chi_tiet: dict)
    KHONG BAO GIO nem loi.
    """
    chi_tiet = {"id": str(ma_nhom), "ngan_sach_dat": int(ngan_sach)}
    try:
        tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
        if not tok:
            return False, "thieu META_ADS_ACCESS_TOKEN trong .env", chi_tiet
        if not str(ma_nhom).strip():
            return False, "thieu ma nhom quang cao", chi_tiet
        if not (0 < int(ngan_sach)):
            return False, "ngan sach phai la so duong", chi_tiet

        truoc, _ = doc_lai_nhom(env, ma_nhom)
        if truoc:
            chi_tiet["trang_thai_truoc"] = truoc.get("status") or truoc.get("effective_status")
            chi_tiet["ngan_sach_truoc"] = truoc.get("daily_budget")

        _, loi = api_post(str(ma_nhom), {
            "access_token": tok,
            "status": trang_thai,
            "daily_budget": str(int(ngan_sach)),
        }, ngu_fn)
        if loi:
            return False, f"Meta tu choi: {loi.get('message') or loi}", chi_tiet

        sau, loi2 = doc_lai_nhom(env, ma_nhom)
        if sau is None:
            return True, ("da gui lenh, nhung doc lai khong duoc: "
                          f"{(loi2 or {}).get('message')}"), chi_tiet

        chi_tiet["trang_thai_sau"] = sau.get("status") or sau.get("effective_status")
        chi_tiet["ngan_sach_sau"] = sau.get("daily_budget")
        dung_trang_thai = str(sau.get("status") or "").upper() == str(trang_thai).upper()
        dung_ngan_sach = str(sau.get("daily_budget") or "") == str(int(ngan_sach))
        if dung_trang_thai and dung_ngan_sach:
            return True, "thanh cong (doc lai thay dung trang thai va ngan sach)", chi_tiet
        return False, (f"doc lai KHONG khop: trang thai={chi_tiet['trang_thai_sau']}, "
                       f"ngan sach={chi_tiet['ngan_sach_sau']}"), chi_tiet
    except Exception as e:
        return False, f"loi khi gui lenh: {type(e).__name__}: {e}", chi_tiet


def tam_dung_va_ha_ngan_sach(env, ma_nhom, ngan_sach=NGAN_SACH_HA, ngu_fn=None):
    """TAT nhom + HA ngan sach ve 27.000d, roi doc lai kiem.

    Dong tac that cua Dai: do tren 75 lan, 72/75 lan ha ngan sach DI KEM tat
    nhom, lech nhau trung vi 6 giay. Nen lam ca hai trong MOT lan goi.
    """
    return _doi_trang_thai_va_ngan_sach(env, ma_nhom, "PAUSED", ngan_sach, ngu_fn)


def bat_lai_va_dat_ngan_sach(env, ma_nhom, ngan_sach, ngu_fn=None):
    """HOAN TAC: BAT LAI nhom + dat ngan sach ve muc cu.

    Vi sao can: tat nham thi cai mat khong phai tien, ma la GIAI DOAN HOC cua
    Meta — nhom bi tat roi bat lai se hoc lai tu dau, mat vai ngay hieu suat.
    Nen hoan tac phai nhanh: mot lan bam, khong phai mo Trinh quan ly quang cao.
    """
    return _doi_trang_thai_va_ngan_sach(env, ma_nhom, "ACTIVE", ngan_sach, ngu_fn)
