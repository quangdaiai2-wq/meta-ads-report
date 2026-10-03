"""Cong cu GHI len Meta. Day la cho duy nhat agent cham duoc vao tien that.

Dong tac tat NHOM cua Dai gom BON viec (do tu so thao tac that):
  1. Tat nhom quang cao (adset)
  2. Tat luon QUANG CAO (ad) ben trong
  3. Ha ngan sach ve 27.000d
  4. Doi ten nhom thanh '<ten cu> x/y X<thang>-<nam>'

Ba viec dau nam tren CUNG mot doi tuong adset nen GOP DUOC vao MOT lan goi
(da kiem chung that 01/10/2026). Viec tat quang cao nam tren doi tuong khac
nen phai goi rieng.

RIENG VIEC B (Dai chot 02/10/2026): khi nhom co TU 2 QUANG CAO TRO LEN thi
tat LE mot quang cao cham nguong — xem `tat_mot_quang_cao()`. Tat le CHI TAT
+ DOI TEN, KHONG dung toi ngan sach (ha ngan sach la viec cua CA NHOM).

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

================================================================================
XU LY CBO (Dai chot 09:22 03/10/2026)
================================================================================
Khi nhom thuoc chien dich Advantage+ (ngan sach cap chien dich):
  TH1: Chiem dich co >=2 nhóm → sau khi tat 1 nhóm: CHUYỂN NS cho nhóm còn sống
       → gọi `tat_nhom_cbo()` thay vì `tam_dung_va_ha_ngan_sach()`.
  TH2: Tat hết cả chiến dịch → ha NS chiến dịch về 27.000đ.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

import report
from agent_rao import NGAN_SACH_HA, thuoc_pham_vi

# Phien ban API lay tu MOT nguon duy nhat la report.py — dung tu viet lai chuoi
# "v26.0" o day. Xem giai thich day du o report.API_VERSION.
API_VERSION = report.API_VERSION
GRAPH = f"https://graph.facebook.com/{API_VERSION}"

# Ma loi Meta tra ve khi ghi qua nhanh.
MA_QUA_NHIEU_YEU_CAU = 613

# Nghi giua hai lan GHI. Do that: 10 giay da qua, nhung 20 giay moi an toan.
CHO_GIUA_HAI_LAN_GHI = 20

# Bi chan thi phai cho LAU. Do that: cho 5-15 giay KHONG du, 35 giay moi qua.
CHO_KHI_BI_CHAN = (35, 35)

# Ngân sách mặc định của chiến dịch CBO đang chạy (theo data thật).
NGAN_SACH_CHIEN_DICH_MAC_DINH = 400000


def api_post(path, params, ngu_fn=None):
    """Goi POST len Meta. Tra ve (du_lieu, loi). Loi tam thoi thi thu lai."""
    ngu = ngu_fn or time.sleep
    url = f"{GRAPH}/{path}"
    body = urllib.parse.urlencode(params).encode("utf-8")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, data=body)
            with urllib.request.urlopen(req, timeout=60) as resp:
                report.kiem_canh_bao_phien_ban(getattr(resp, "headers", None))
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


def mo_ta_loi(err):
    """Gom MOI thong tin loi Meta tra ve thanh mot chuoi de doc.

    LOI THAT 02/10/2026: code cu chi ghi `loi.get('message')` nen nhat duoc
    dung chu "Invalid parameter" — khong biet tham so nao sai, khong the sua.
    Meta con tra `code`, `error_subcode`, `error_user_msg`, `error_data`.
    """
    if not isinstance(err, dict):
        return str(err)
    phan = [str(err.get("message") or err)]
    for nhan, khoa in (("ma", "code"), ("ma phu", "error_subcode"),
                       ("chi tiet", "error_user_msg")):
        v = err.get(khoa)
        if v not in (None, "", 0, "0"):
            phan.append(f"{nhan}={v}")
    if err.get("error_data"):
        phan.append(f"du lieu={err['error_data']}")
    return " | ".join(phan)


def doan_nguyen_nhan(err):
    """Doan NGUYEN NHAN loi Meta bang tieng nguoi thuong. Tra ve chuoi.

    Dai yeu cau 02/10/2026: "phai bao loi nay la loi do dau". Nhung KHONG duoc
    doan bua — khong khop bang thi tra ve chuoi rong, de tin nhan ghi nguyen
    van loi Meta kem chu "chua ro nguyen nhan".

    Cap nhat 03/10/2026: nhận diện CBO 1885621 + hướng dẫn xử lý đúng cách.
    """
    if not isinstance(err, dict):
        return ""
    ma = report._ma_nguyen(err.get("code"))
    chu = " ".join(str(err.get(k) or "") for k in
                   ("message", "error_user_msg", "error_data")).lower()
    if ma == 613:
        return "Ghi quá nhanh — Meta tạm chặn, chờ vài chục giây là gửi lại được"
    if ma == 190:
        return "Token Meta hết hạn hoặc sai — cần lấy token mới"
    if ma in (200, 272):
        return "Token Meta thiếu quyền thao tác quảng cáo"
    if ma == 17:
        return "Tài khoản quảng cáo đã chạm hạn mức của Meta"
    ma_phu = report._ma_nguyen(err.get("error_subcode"))
    if ma == 100 and ma_phu == 1885621:
        return ("Nhóm này thuộc chiến dịch Advantage+ (ngân sách cấp chiến dịch) "
                "nên Meta KHÔNG cho đặt ngân sách cấp nhóm. Agent sẽ chuyển ngân sách "
                "sang nhóm còn đang chạy thay vì hạ ngân sách.")
    if "budget" in chu or "ngan_sach" in chu or "ngân sách" in chu:
        return "Ngân sách đặt vào không hợp lệ cho nhóm này"
    if ma == 100:
        return ("Meta không nhận tham số gửi lên. Hay gặp nhất là nhóm VỪA TẠO "
                "trong ngày — Meta chưa duyệt xong. Chờ lần quét sau thử lại.")
    return ""


# ====================================================================
# DOC NHÓM TRONG CHIẾN DỊCH (CBO)
# ====================================================================

def doc_tat_ca_nhom_trong_chien_dich(env, ma_chien_dich):
    """Doc TẤT CẢ nhóm trong chiến dịch (ACTIVE + PAUSED). Tra ve (list, loi).

    Dung direct API /{campaign_id}/adsets — dat thanh voi ID 120250500099510509
    va cac chién dich Advantage+ khac (da doc thuc te 03/10/2026).
    """
    tok = env.get("META_ADS_ACCESS_TOKEN", "") or ""
    if not tok:
        return [], {"message": "thieu META_ADS_ACCESS_TOKEN"}
    d, loi = report.api_get(f"{ma_chien_dich}/adsets", {
        "access_token": tok,
        "fields": "id,name,status,effective_status,daily_budget",
        "limit": 100,
    })
    if loi:
        return [], loi
    rows = (d or {}).get("data", []) if isinstance(d, dict) else []
    nxt = (d or {}).get("paging", {}).get("next") if isinstance(d, dict) else None
    while nxt:
        d2, _ = report.api_get(nxt, {})
        if isinstance(d2, dict):
            rows.extend(d2.get("data", []))
            nxt = d2.get("paging", {}).get("next")
        else:
            break
    return rows, None


# ====================================================================
# CHUYỂN NGÂN SÁCH CHIẾN DỊCH SANG NHÓM SỐNG (TH1 — CBO)
# ====================================================================

def chuyen_ns_ve_nhom_song(env, ma_chien_dich, danh_sach_hau_to, ten_nhom_dang_chay,
                           ngan_sach_moi=None, _post=None, _time=None):
    """Chuyển NS từ chiến dịch sang cho NHÓM ĐANG CHẠY còn lại.

    GỌI SAU KHI nhóm bị tụt đã đóng hậu tố.
    Tìm các nhóm còn ACTIVE trong chiến dịch (không có hậu tố tên) rồi đặt NS riêng.

    Tham so:
      ma_chien_dich: ID chiến dịch chứa nhóm này
      danh_sach_hau_to: list các hậu tố tên (vd ["X10-26"]) để loại nhóm khỏi danh sách chọn
      ten_nhom_dang_chay: tên nhóm vừa bị tụt (để tránh nhầm)
      ngan_sach_moi: ngân sách muốn gán — mặc định NGAN_SACH_CHIEN_DICH_MAC_DINH (400k)

    Tra ve (thanh_cong: bool, message: str, ma_nhom_cap: str or None).
    """
    tim = _time or time.sleep
    post_fn = _post or api_post
    ns = ngan_sach_moi or NGAN_SACH_CHIEN_DICH_MAC_DINH

    nhoms, loi = doc_tat_ca_nhom_trong_chien_dich(env, ma_chien_dich)
    if loi:
        return False, f"lỗi đọc nhóm: {loi.get('message')}", None

    # Lọc nhóm CÒN SỐNG (ACTIVE) và KHÔNG có hậu tố (chưa bị tụt)
    nhom_song = [n for n in nhoms
                 if str(n.get("effective_status")) == "ACTIVE"
                 and not any(h in n.get("name", "") for h in danh_sach_hau_to)]

    if not nhom_song:
        return False, "KHÔNG CÓ NHÓM NÀO CÒN CHẠY ĐỂ CHUYỂN NGÂN SÁCH", None

    # Chọn nhóm còn sống đầu tiên
    m_doc_cap = str(nhom_song[0].get("id"))
    ten_group = nhom_song[0].get("name")[:60]

    # Đặt daily_budget = NS cho nhóm sống → Meta tự động chuyển từ NS chiến dịch sang NS nhóm
    tim(CHO_GIUA_HAI_LAN_GHI)
    _, loi_api = post_fn(m_doc_cap, {
        "access_token": env.get("META_ADS_ACCESS_TOKEN", ""),
        "daily_budget": str(int(ns)),
    }, tim)

    if loi_api:
        return False, (f"Không chuyển được ngân sách cho nhóm sống: "
                       f"{loi_api.get('message', loi_api)}"), None

    return True, f"đã chuyển ngân sách {ns:,}đ về nhóm {ten_group} ({m_doc_cap})", m_doc_cap


# ====================================================================
# HÀM CHÍNH: TẮT NHÓM CBO (TH1 — chuyển NS cho nhóm sống)
# ====================================================================

def tat_nhom_cbo(env, ma_nhom, ma_chien_dich, danh_sach_hau_to,
                 ten_nhom, ten_moi=None, ngu_fn=None):
    """TẠT NHÓM CBO HOÀN CHỈNH: tắt nhóm + tắt ad + đổi tên + chuyển NS cho nhóm sống.

    Đây là hàm ENTRY POINT dành cho CBO. Gọi thay vì
    `tam_dung_va_ha_ngan_sach()` + `tat_quang_cao()` + thủ công chuyển NS.

    Tham số:
      ma_chien_dich: ID chiến dịch (để tìm nhóm anh em)
      danh_sach_hau_to: các hậu tố tên cần kiểm (vd ["X10-26"])
      ten_nhom: tên gốc của nhóm trước khi đổi
      ten_moi: tên mới đã có hậu tố
      ngu_fn: hàm sleep tùy chỉnh (cho test)

    Trả về (thành_công, kết_qua, chi_tiết). Không bao giờ ném lỗi.
    """
    ngu = ngu_fn or time.sleep
    chi_tiet = {"id": str(ma_nhom), "loai": "CBO"}

    # ---- Bước 1: Tắt nhóm + đổi tên (giữ nguyên NS cấp nhóm = không đặt) ----
    ok, kq, ct = _doi_trang_thai_va_ngan_sach(env, ma_nhom, "PAUSED", None, ten_moi, ngu)
    chi_tiet["tat_nhom"] = ok
    chi_tiet["tat_nhom_ket_qua"] = kq

    if not ok:
        return ok, kq, chi_tiet

    # ---- Bước 2: Tắt ad bên trong nhóm ----
    ads, loi_ads = doc_quang_cao(env, ma_nhom)
    chi_tiet["so_ad"] = len(ads)
    if loi_ads:
        chi_tiet["ad_error"] = loi_ads.get("message")
    elif ads:
        tok = env.get("META_ADS_ACCESS_TOKEN", "") or ""
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
                chi_tiet["ad_errors"] = chi_tiet.get("ad_errors", [])
                chi_tiet["ad_errors"].append({"id": ma_ad, "error": loi2.get("message") or loi2})
            else:
                chi_tiet["da_tat"] = chi_tiet.get("da_tat", [])
                chi_tiet["da_tat"].append({"id": ma_ad, "ket_qua": "da tat"})

    # ---- Bước 3: Chuyển NS cho nhóm sống ----
    ok_ns, msg_ns, m_ns = chuyen_ns_ve_nhom_song(
        env, ma_chien_dich, danh_sach_hau_to, ten_nhom,
        ngan_sach_moi=NGAN_SACH_CHIEN_DICH_MAC_DINH, _time=ngu)
    chi_tiet["chuyen_ns"] = ok_ns
    chi_tiet["chuyen_ns_ket_qua"] = msg_ns
    chi_tiet["nhom_duoc_cap_ns"] = m_ns

    if ok_ns:
        return True, f"đã tắt nhóm + đổi tên + chuyển NS {NGAN_SACH_CHIEN_DICH_MAC_DINH:,}đ về nhóm sống", chi_tiet

    return True, f"đã tắt nhóm + đổi tên. KHÔNG CHUYỂN ĐƯỢC NS: {msg_ns}", chi_tiet


# ====================================================================
# HÀM CŨ: TẮT NHÓM THÔNG THƯỜNG (không CBO)
# ====================================================================

def _doi_trang_thai_va_ngan_sach(env, ma_nhom, trang_thai, ngan_sach, ten_moi=None,
                                 ngu_fn=None):
    """Tăt/bat nhom + (tuy chon) dat ngan sach + (tuy chon) doi ten, roi DOC LAI kiem.

    `ngan_sach=None` nghia la KHONG DUNG TOI NGAN SACH — chi tat nhom va doi ten.

    GOP CA BA vao MOT lan goi — da kiem chung that 01/10/2026 rang Meta nhan
    `name` + `status` + `daily_budget` cung luc. Tiet kiem 2/3 so lan ghi, rat
    quan trong vi Meta gioi han ghi rat chat.

    ⚠️ DA BO CO CHE "TACH LENH" (Dai chot 02/10/2026):
    Buoi chieu 02/10 toi tung lam: gop loi thi tu tach ra gui `status` rieng de
    van tat duoc nhom. Dai KHONG muon the. Ly do: Meta da tu choi thi co gi do
    chua san sang; co tat se tao TRANG THAI NUA VOI (tat duoc nhom nhung khong
    ha duoc ngan sach), kho kiem tra ve sau.
    => Nay: Meta tu choi thi tra ve THAT BAI ngay, KHONG tat gi ca.
    Xem `docs/superpowers/plans/2026-10-02-nhanh-loi-khi-meta-tu-choi.md`.

    Tra ve (thanh_cong: bool, ket_qua: str, chi_tiet: dict)
    KHONG BAO GIO nem loi.
    """
    chi_tiet = {"id": str(ma_nhom), "da_tat": False, "da_ha_ngan_sach": False}
    if ngan_sach is not None:
        chi_tiet["ngan_sach_dat"] = int(ngan_sach)
    try:
        tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
        if not tok:
            return False, "thieu META_ADS_ACCESS_TOKEN trong .env", chi_tiet
        if not str(ma_nhom).strip():
            return False, "thieu ma nhom quang cao", chi_tiet
        if ngan_sach is not None and not (0 < int(ngan_sach)):
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

        goi = {"access_token": tok, "status": trang_thai}
        if ngan_sach is not None:
            goi["daily_budget"] = str(int(ngan_sach))
        if ten_moi:
            goi["name"] = str(ten_moi)
            chi_tiet["ten_dat"] = str(ten_moi)

        _, loi = api_post(str(ma_nhom), goi, ngu_fn)
        if loi:
            chi_tiet["loi"] = mo_ta_loi(loi)
            chi_tiet["nguyen_nhan"] = doan_nguyen_nhan(loi)
            return False, f"Meta từ chối: {mo_ta_loi(loi)}", chi_tiet

        sau, loi2 = doc_lai_nhom(env, ma_nhom)
        if sau is None:
            return True, ("da gui lenh, nhung doc lai khong duoc: "
                          f"{(loi2 or {}).get('message')}"), chi_tiet

        chi_tiet["trang_thai_sau"] = sau.get("status") or sau.get("effective_status")
        chi_tiet["ngan_sach_sau"] = sau.get("daily_budget")
        chi_tiet["ten_sau"] = sau.get("name")
        dung_trang_thai = (str(sau.get("status") or "").upper()
                           == str(trang_thai).upper())
        dung_ngan_sach = (ngan_sach is None
                          or str(sau.get("daily_budget") or "") == str(int(ngan_sach)))
        dung_ten = (not ten_moi) or (sau.get("name") == ten_moi)
        chi_tiet["da_tat"] = dung_trang_thai
        chi_tiet["da_ha_ngan_sach"] = (ngan_sach is not None) and dung_ngan_sach

        if dung_trang_thai and dung_ngan_sach and dung_ten:
            return True, "thanh cong (doc lai thay dung trang thai va ngan sach)", chi_tiet

        if dung_trang_thai and dung_ten and not dung_ngan_sach:
            # TAT duoc la xong viec chinh. Noi ro phan con thieu, dung bao that bai.
            return True, (f"da tat nhom, NHUNG chua ha duoc ngan sach "
                          f"(ngan sach dang {chi_tiet['ngan_sach_sau']})"), chi_tiet

        return False, (f"doc lai KHONG khop: trang thai={chi_tiet['trang_thai_sau']}, "
                       f"ngan sach={chi_tiet['ngan_sach_sau']}, "
                       f"ten={chi_tiet.get('ten_sau')!r}"), chi_tiet
    except Exception as e:
        return False, f"loi khi gui lenh: {type(e).__name__}: {e}", chi_tiet


def tam_dung_va_ha_ngan_sach(env, ma_nhom, ngan_sach=NGAN_SACH_HA, ten_moi=None,
                             ngu_fn=None):
    """TAT nhom + (tuy chon) HA ngan sach + (tuy chon) DOI TEN, roi doc lai kiem.

    `ngan_sach=None` = chi tat nhom, GIU NGUYEN ngan sach (Dai chot 02/10/2026).

    Dong tac that cua Dai: do tren 75 lan, 72/75 lan ha ngan sach DI KEM tat
    nhom, lech nhau trung vi 6 giay. Nen mac dinh lam ca ba trong MOT lan goi.
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


def doc_mot_quang_cao(env, ma_ad):
    """Doc MOT quang cao. Tra ve (du_lieu, loi). `du_lieu` None neu khong doc duoc."""
    tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
    if not tok:
        return None, {"message": "thieu META_ADS_ACCESS_TOKEN trong .env"}
    d, loi = report.api_get(str(ma_ad), {
        "access_token": tok, "fields": "id,name,status,adset_id"})
    if loi:
        return None, loi
    return d, None


def tat_mot_quang_cao(env, ma_ad, ten_nhom=None, ten_moi=None, ngu_fn=None,
                      _doc_ad=None, _doc_nhom=None, _post=None):
    """Tat MOT quang cao + (tuy chon) doi ten. KHONG dung toi ngan sach.

    ==========================================================================
    VIEC B — Dai chot 02/10/2026
    ==========================================================================
    Dai: "chi tat quang cao dang chay va chi tieu den nguong thoi"
    => Tat le quang cao CHI TAT + DOI TEN. KHONG ha ngan sach.
       (Ha ngan sach la viec cua CA NHOM, do nut `TAT NHOM + HA NGAN SACH`.)

    🔴🔴 RAO PHAM VI — QUY TAC SAT (Dai chot 15:3x 02/10/2026):
       "chi duoc phep dong den chien dich, nhom quang cao, quang cao co chua
        'dainq' ngoai ra thi khong duoc phep dong den"

       Pham vi LUON kiem theo TEN NHOM chua quang cao — TUYET DOI KHONG kiem
       theo ten quang cao. Vi sao (do that 02/10/2026):
         - Ten quang cao do Meta tu sinh: 11/55 ten KHONG chua 'dainq'
           (vd 'Quang cao Muc do nhan biet moi').
         - Toan tai khoan co 101 nhom KHONG chua 'dainq' (90 Truong + 11 Thao),
           40 nhom dang ACTIVE.
       => Kiem theo ten quang cao thi (a) ad cua chinh Dai cung bi loai, hoac
          (b) dong vao tai san cua Truong. CA HAI CHIEU DEU SAI.

    Vi vay tham so `ten_nhom` la BAT BUOC tren thuc te: neu khong truyen, ham
    TU DOC LAI nhom chua quang cao de lay ten.

    ⚠️ GOP `status` + `name` vao MOT lan goi — da kiem chung Meta nhan ca hai.
    ⚠️ Khong bao gio gui `daily_budget`.
    ⚠️ Cho `CHO_GIUA_HAI_LAN_GHI` (20 giay) truoc khi ghi, giong moi cho khac.

    Tra ve (thanh_cong: bool, ket_qua: str, chi_tiet: dict).
    KHONG BAO GIO nem loi.
    """
    ngu = ngu_fn or time.sleep
    doc_ad = _doc_ad or doc_mot_quang_cao
    doc_nhom = _doc_nhom or doc_lai_nhom
    post = _post or api_post
    chi_tiet = {"id": str(ma_ad), "da_tat": False, "da_doi_ten": False,
                "ngan_sach_dung_toi": False}
    try:
        tok = (env or {}).get("META_ADS_ACCESS_TOKEN", "").strip()
        if not tok:
            return False, "thieu META_ADS_ACCESS_TOKEN trong .env", chi_tiet
        if not str(ma_ad).strip():
            return False, "thieu ma quang cao", chi_tiet

        # ---- Doc quang cao de biet no nam trong nhom nao ----
        ad, loi0 = doc_ad(env, ma_ad)
        if ad is None:
            return False, f"khong doc duoc quang cao: {(loi0 or {}).get('message')}", chi_tiet
        ma_nhom = str(ad.get("adset_id") or "")
        chi_tiet["adset_id"] = ma_nhom
        chi_tiet["ten_truoc"] = ad.get("name")
        chi_tiet["trang_thai_truoc"] = ad.get("status")
        if not ma_nhom:
            return False, ("quang cao khong co adset_id — khong the kiem pham vi, "
                           "KHONG dung vao"), chi_tiet

        # ---- RAO PHAM VI: doc lai TEN NHOM, KHONG dung ten quang cao ----
        tt_nhom = ten_nhom
        if not tt_nhom:
            nhom, loi1 = doc_nhom(env, ma_nhom)
            if nhom is None:
                return False, (f"khong doc duoc nhom chua quang cao: "
                               f"{(loi1 or {}).get('message')}"), chi_tiet
            tt_nhom = nhom.get("name")
        chi_tiet["ten_nhom"] = tt_nhom
        if not thuoc_pham_vi(tt_nhom):
            return False, (f"Ten nhom khong thuoc pham vi cua Dai, KHONG dung vao "
                           f"quang cao ben trong: {str(tt_nhom)[:60]}"), chi_tiet

        # ---- Da PAUSED san thi khong POST lai ----
        if str(ad.get("status") or "").upper() == "PAUSED":
            chi_tiet["da_tat"] = True
            return True, "quang cao da tat san", chi_tiet

        # ---- GOP status + name vao MOT lan goi. KHONG co daily_budget. ----
        goi = {"access_token": tok, "status": "PAUSED"}
        if ten_moi:
            goi["name"] = str(ten_moi)
            chi_tiet["ten_dat"] = str(ten_moi)
        assert "daily_budget" not in goi, "tat le quang cao KHONG duoc dung ngan sach"

        ngu(CHO_GIUA_HAI_LAN_GHI)
        _, loi2 = post(str(ma_ad), goi, ngu)
        if loi2:
            chi_tiet["loi"] = mo_ta_loi(loi2)
            chi_tiet["nguyen_nhan"] = doan_nguyen_nhan(loi2)
            return False, f"Meta tu choi: {mo_ta_loi(loi2)}", chi_tiet

        # ---- Doc lai kiem that su ----
        sau, loi3 = doc_ad(env, ma_ad)
        if sau is None:
            return True, ("da gui lenh, nhung doc lai khong duoc: "
                          f"{(loi3 or {}).get('message')}"), chi_tiet
        chi_tiet["trang_thai_sau"] = sau.get("status")
        chi_tiet["ten_sau"] = sau.get("name")
        dung_tt = str(sau.get("status") or "").upper() == "PAUSED"
        dung_ten = (not ten_moi) or (sau.get("name") == ten_moi)
        chi_tiet["da_tat"] = dung_tt
        chi_tiet["da_doi_ten"] = bool(ten_moi) and dung_ten
        if dung_tt and dung_ten:
            return True, "thanh cong (doc lai thay dung trang thai)", chi_tiet
        if dung_tt and not dung_ten:
            return True, ("da tat duoc quang cao, nhung ten doc lai CHUA khop "
                          "(khong phai that bai)"), chi_tiet
        return False, "doc lai thay quang cao VAN CHUA tat", chi_tiet
    except Exception as e:
        return False, f"loi khi tat mot quang cao: {type(e).__name__}: {e}", chi_tiet
