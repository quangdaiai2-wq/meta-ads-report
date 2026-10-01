"""Cong cu GHI len Meta. Day la cho duy nhat agent cham duoc vao tien that.

Dong tac tat nhom cua Dai gom BON viec (do tu so thao tac that):
  1. Tat nhom quang cao (adset)
  2. Tat luon QUANG CAO (ad) ben trong
  3. Ha ngan sach ve 27.000d
  4. Doi ten nhom thanh '<ten cu> x/y X<thang>'

Ba viec dau nam tren CUNG mot doi tuong adset nen GOP DUOC vao MOT lan goi
(da kiem chung that 01/10/2026). Viec tat quang cao nam tren doi tuong khac
nen phai goi rieng.

GIOI HAN GHI CUA META — da gap that 01/10/2026:
  '(#613) Calls to this API have exceeded the concurrent request rate limit of
   1 calls per 30 seconds.'
  Do that: ghi lien tuc 4 lan thi lan thu 4 bi chan; cho 10 giay thi qua;
  nhung co lan phai cho 35 giay. Nen:
    - CHO_GIUA_HAI_LAN_GHI: nghi bat buoc giua hai lan ghi.
    - Cho LAU hon han khi gap ma 613 (report.CHO_TRUOC_KHI_THU_LAI chi 5/15 giay
      — KHONG DU, da kiem chung).

PHAM VI: moi ham o day deu KIEM LAI ten doi tuong truoc khi ghi. Dai chot
01/10/2026: chi duoc dung vao doi tuong co chua 'dainq'.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

import report
from agent_rao import NGAN_SACH_HA, thuoc_pham_vi

API_VERSION = "v21.0"
GRAPH = f"https://graph.facebook.com/{API_VERSION}"

# Ma loi Meta tra ve khi ghi qua nhanh.
MA_QUA_NHIEU_YEU_CAU = 613

# Nghi giua hai lan GHI. Do that: 10 giay da qua, nhung 20 giay moi an toan.
CHO_GIUA_HAI_LAN_GHI = 20

# Bi chan thi phai cho LAU. Do that: cho 5-15 giay KHONG du, 35 giay moi qua.
CHO_KHI_BI_CHAN = (35, 35)


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
            ma = report._ma_nguyen(err.get("code"))
            if attempt < 2:
                # Ghi qua nhanh: phai cho LAU. Cac ma tam thoi khac: cho ngan.
                if ma == MA_QUA_NHIEU_YEU_CAU:
                    ngu(CHO_KHI_BI_CHAN[attempt])
                    continue
                if ma in report.MA_LOI_META_TAM_THOI:
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


def doc_quang_cao(env, ma_nhom):
    """Danh sach QUANG CAO (ad) ben trong nhom. Tra ve (list, loi)."""
    tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
    if not tok:
        return [], {"message": "thieu META_ADS_ACCESS_TOKEN trong .env"}
    d, loi = report.api_get(f"{ma_nhom}/ads", {
        "access_token": tok, "fields": "id,name,status", "limit": 50})
    if loi:
        return [], loi
    return (d or {}).get("data", []) or [], None


def _doi_trang_thai_va_ngan_sach(env, ma_nhom, trang_thai, ngan_sach, ten_moi=None,
                                 ngu_fn=None):
    """Tat/bat nhom + dat ngan sach + (tuy chon) doi ten, roi DOC LAI kiem.

    GOP CA BA vao MOT lan goi — da kiem chung that 01/10/2026 rang Meta nhan
    `name` + `status` + `daily_budget` cung luc. Nho vay tiet kiem 2/3 so lan
    ghi, rat quan trong vi Meta gioi han ghi rat chat.

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
            # Hang rao PHAM VI: chi duoc dung vao doi tuong cua Dai.
            if not thuoc_pham_vi(truoc.get("name")):
                return False, (f"Tên nhóm không thuộc phạm vi của Đại: "
                               f"{str(truoc.get('name'))[:60]}"), chi_tiet
            chi_tiet["ten_truoc"] = truoc.get("name")
            chi_tiet["trang_thai_truoc"] = truoc.get("status") or truoc.get("effective_status")
            chi_tiet["ngan_sach_truoc"] = truoc.get("daily_budget")

        goi = {
            "access_token": tok,
            "status": trang_thai,
            "daily_budget": str(int(ngan_sach)),
        }
        if ten_moi:
            goi["name"] = str(ten_moi)
            chi_tiet["ten_dat"] = str(ten_moi)

        _, loi = api_post(str(ma_nhom), goi, ngu_fn)
        if loi:
            return False, f"Meta tu choi: {loi.get('message') or loi}", chi_tiet

        sau, loi2 = doc_lai_nhom(env, ma_nhom)
        if sau is None:
            return True, ("da gui lenh, nhung doc lai khong duoc: "
                          f"{(loi2 or {}).get('message')}"), chi_tiet

        chi_tiet["trang_thai_sau"] = sau.get("status") or sau.get("effective_status")
        chi_tiet["ngan_sach_sau"] = sau.get("daily_budget")
        chi_tiet["ten_sau"] = sau.get("name")
        dung_trang_thai = str(sau.get("status") or "").upper() == str(trang_thai).upper()
        dung_ngan_sach = str(sau.get("daily_budget") or "") == str(int(ngan_sach))
        dung_ten = (not ten_moi) or (sau.get("name") == ten_moi)
        if dung_trang_thai and dung_ngan_sach and dung_ten:
            return True, "thanh cong (doc lai thay dung trang thai va ngan sach)", chi_tiet
        return False, (f"doc lai KHONG khop: trang thai={chi_tiet['trang_thai_sau']}, "
                       f"ngan sach={chi_tiet['ngan_sach_sau']}, "
                       f"ten={chi_tiet.get('ten_sau')!r}"), chi_tiet
    except Exception as e:
        return False, f"loi khi gui lenh: {type(e).__name__}: {e}", chi_tiet


def tam_dung_va_ha_ngan_sach(env, ma_nhom, ngan_sach=NGAN_SACH_HA, ten_moi=None,
                             ngu_fn=None):
    """TAT nhom + HA ngan sach ve 27.000d + (tuy chon) DOI TEN, roi doc lai kiem.

    Dong tac that cua Dai: do tren 75 lan, 72/75 lan ha ngan sach DI KEM tat
    nhom, lech nhau trung vi 6 giay. Nen lam ca ba trong MOT lan goi.
    """
    return _doi_trang_thai_va_ngan_sach(env, ma_nhom, "PAUSED", ngan_sach,
                                        ten_moi, ngu_fn)


def bat_lai_va_dat_ngan_sach(env, ma_nhom, ngan_sach, ngu_fn=None):
    """HOAN TAC: BAT LAI nhom + dat ngan sach ve muc cu.

    Vi sao can: tat nham thi cai mat khong phai tien, ma la GIAI DOAN HOC cua
    Meta — nhom bi tat roi bat lai se hoc lai tu dau, mat vai ngay hieu suat.
    Nen hoan tac phai nhanh: mot lan bam, khong phai mo Trinh quan ly quang cao.
    """
    return _doi_trang_thai_va_ngan_sach(env, ma_nhom, "ACTIVE", ngan_sach, None,
                                        ngu_fn)


def tat_quang_cao(env, ma_nhom, ten_nhom=None, ngu_fn=None):
    """Tat HET quang cao (ad) ben trong nhom. Tra ve (thanh_cong, ket_qua, chi_tiet).

    Dai chot 01/10/2026: khi tat nhom thi tat LUON quang cao ben trong.

    Hang rao PHAM VI: truoc khi dung vao quang cao, phai doc lai TEN NHOM va
    kiem no thuoc pham vi cua Dai. Ly do: Meta tu sinh ten quang cao, nhieu cai
    KHONG chua 'dainq' du chung nam trong nhom cua Dai — nen khong the loc theo
    ten quang cao. Loc theo NHOM la dung, va da kiem chung bang so thao tac that.

    KHONG BAO GIO nem loi.
    """
    ngu = ngu_fn or time.sleep
    chi_tiet = {"id": str(ma_nhom), "so_quang_cao": 0, "da_tat": []}
    try:
        nhom, loi0 = doc_lai_nhom(env, ma_nhom)
        if nhom is None:
            return False, f"khong doc duoc nhom: {(loi0 or {}).get('message')}", chi_tiet
        ten = ten_nhom or nhom.get("name")
        if not thuoc_pham_vi(ten):
            return False, (f"Tên nhóm không thuộc phạm vi của Đại, KHÔNG đụng vào "
                           f"quang cáo bên trong: {str(ten)[:60]}"), chi_tiet

        ads, loi = doc_quang_cao(env, ma_nhom)
        if loi:
            return False, f"khong doc duoc danh sach quang cao: {loi.get('message') or loi}", chi_tiet
        chi_tiet["so_quang_cao"] = len(ads)
        if not ads:
            return True, "nhom khong co quang cao nao", chi_tiet

        tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
        for a in ads:
            ma_ad = str(a.get("id") or "")
            if not ma_ad:
                continue
            if str(a.get("status") or "").upper() == "PAUSED":
                chi_tiet["da_tat"].append({"id": ma_ad, "ket_qua": "da tat san"})
                continue
            ngu(CHO_GIUA_HAI_LAN_GHI)
            _, loi2 = api_post(ma_ad, {"access_token": tok, "status": "PAUSED"}, ngu)
            if loi2:
                chi_tiet["da_tat"].append({"id": ma_ad,
                                           "ket_qua": f"loi: {loi2.get('message') or loi2}"})
                continue
            chi_tiet["da_tat"].append({"id": ma_ad, "ket_qua": "da tat"})

        # Doc lai de kiem THAT SU tat het chua.
        lai, _ = doc_quang_cao(env, ma_nhom)
        con_chay = [str(x.get("id")) for x in (lai or [])
                    if str(x.get("status") or "").upper() != "PAUSED"]
        chi_tiet["con_chay"] = con_chay
        if con_chay:
            return False, f"van con {len(con_chay)} quang cao chua tat", chi_tiet
        return True, f"da tat het {len(ads)} quang cao", chi_tiet
    except Exception as e:
        return False, f"loi khi tat quang cao: {type(e).__name__}: {e}", chi_tiet
