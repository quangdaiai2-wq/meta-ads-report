"""CAI TRAN — ham THUAN. Khong goi mang, khong doc file, khong co AI trong do.

Day la file quan trong nhat cua nac 2. AI co the xin gi cung duoc; rao chan la
thu quyet dinh. Neu AI bi lua hoac hieu sai, rao van dung.

Vi sao phai la HAM THUAN: nho vay kiem thu duoc tung truong hop mot, va nho vay
no KHONG THE bi AI thuyet phuc.

Quy uoc: chu thich tieng Viet KHONG dau; chuoi hien cho Dai CO DAU (vi ly do
chan duoc gui thang vao Telegram cho Dai doc).

Quy tac lay tu TONG-HOP-CACH-CHAY-QUANG-CAO.md (da kiem chung bang du lieu that
ngay 30/09/2026). Khong co quy tac nao o day la phong doan.
"""
import re
from datetime import datetime, timedelta, timezone

GIO_VN = timezone(timedelta(hours=7))

# Ten doi tuong thuoc pham vi Dai: chua "dainq", hoac bat dau bang ma content
# viet hoa (THC295THM295), hoac co "new - dainq".
RE_MA_CONTENT = re.compile(r"^[A-Z]{2,}\d")

MOC_CPR = 400000          # chi phi moi luot mua toi da (moc CO DINH, khong doi)
NGAN_SACH_HA = 27000      # ngan sach ha ve khi tat
TOI_DA_NGAY = 3           # tran hanh dong moi ngay
TOI_DA_GIO = 1            # tran hanh dong moi gio
HAN_CHO_PHUT = 24 * 60    # de xuat qua 24 gio thi het hieu luc
HAN_HOI_LAI_PHUT = 24 * 60  # khong hoi lai nhom da co cau tra loi trong 24 gio
HAN_HOAN_TAC_PHUT = 24 * 60  # chi duoc bat lai trong 24 gio ke tu luc tat

# Hai viec agent duoc phep lam. Ngoai hai viec nay: chan tuyet doi.
HANH_DONG_CHO_PHEP = ("tam_dung", "bat_lai")

# Tran ngan sach khi BAT LAI. Khong the khong co tran: neu so ghi trong so bi
# hong thi khong duoc phep dat ra mot con so khong lo.
TRAN_NGAN_SACH_KHOI_PHUC = 5000000


def tien(v):
    """1234567 -> '1.234.567đ' (kieu Viet Nam)."""
    try:
        return f"{int(v):,}".replace(",", ".") + "đ"
    except (TypeError, ValueError):
        return "?"


def thuoc_pham_vi(ten):
    """Ten doi tuong co thuoc pham vi Dai khong.

    Dai chot 30/09/2026: chi quan tam doi tuong co chua "dainq". Nhung co nhom
    chay content moi duoc dat ten bang MA CONTENT (vd THC295THM295) nen khong co
    chu "dainq" - da kiem chung 6 thao tac that. Phai nhan ca truong hop do.
    """
    if not isinstance(ten, str) or not ten.strip():
        return False
    t = ten.strip()
    tl = t.lower()
    if "dainq" in tl:
        return True
    if "new - dainq" in tl:
        return True
    if RE_MA_CONTENT.match(t):
        return True
    return False


def _so(v):
    """Doc so an toan.

    BAY THAT da gap khi dung thu (30/09/2026): Meta tra ve `spend` va `value`
    dang CHUOI ("70000"), khong phai so. Neu chi nhan int/float thi MOI dong
    deu bi bo qua => agent khong bao gio de xuat gi, va khong he nem loi.
    Day la loai loi im lang nguy hiem nhat. Phai nhan chuoi so.
    """
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        try:
            return float(v.strip())
        except ValueError:
            return None
    return None


def _gio(t):
    """Chuan hoa mot thoi diem ve co mui gio Viet Nam. Khong doc duoc -> None.

    LOI THAT do kiem thu bat duoc (30/09/2026): ban dau ham nay CHI nhan
    `datetime`. Nhung `agent.py` doc lai ban ghi tu `logs/nhat-ky-agent.json`,
    noi thoi diem luu dang CHUOI ISO ("2026-09-30T14:30:44+07:00"). Ket qua:
    rao an toan tra ve "Thoi diem tao de xuat khong doc duoc" => agent TU CHOI
    MOI lenh Dai da dong y => tinh nang khong bao gio tắt duoc nhom nao.
    Phai nhan ca chuoi ISO.
    """
    if isinstance(t, str):
        try:
            t = datetime.fromisoformat(t)
        except ValueError:
            return None
    if not isinstance(t, datetime):
        return None
    return t if t.tzinfo else t.replace(tzinfo=GIO_VN)


def kiem(de_xuat, lich_su=None, bay_gio=None):
    """Kiem mot de xuat. Tra ve (cho_phep: bool, ly_do: str).

    `lich_su` la dict, co the thieu khoa:
        so_hanh_dong_hom_nay : int
        so_hanh_dong_gio_nay : int
        nhom_da_tra_loi       : {id_nhom: thoi_diem_tra_loi}

    KHONG BAO GIO nem loi. Dau vao di dang thi tra ve "chan".
    """
    try:
        if not isinstance(de_xuat, dict):
            return False, "Đề xuất không phải là dữ liệu hợp lệ"

        # --- Rao 2: chi duoc lam MOT TRONG HAI viec ---
        hanh_dong = de_xuat.get("hanh_dong")
        if hanh_dong not in HANH_DONG_CHO_PHEP:
            return False, (f"Agent chỉ được TẮT nhóm hoặc BẬT LẠI nhóm, "
                           f"không được làm việc '{hanh_dong}'")

        doi_tuong = de_xuat.get("doi_tuong")
        if not isinstance(doi_tuong, dict):
            return False, "Đề xuất thiếu thông tin nhóm quảng cáo"

        # --- Rao 1: danh sach trang ---
        ten = doi_tuong.get("ten")
        if not thuoc_pham_vi(ten):
            return False, (f"Tên nhóm không thuộc phạm vi của Đại "
                           f"(phải có 'dainq'): {str(ten)[:60]}")

        ma = doi_tuong.get("id")
        if not ma:
            return False, "Đề xuất thiếu mã nhóm quảng cáo"
        ma = str(ma)

        ls = lich_su if isinstance(lich_su, dict) else {}
        goc = _gio(bay_gio) or datetime.now(GIO_VN)

        # ================= BAT LAI: bo qua cac rao cua viec TAT =================
        if hanh_dong == "bat_lai":
            # Ngan sach khoi phuc phai la so duong va khong vuot tran.
            # Khong the khong co tran: so trong so co the hong.
            khoi_phuc = _so(de_xuat.get("ngan_sach_khoi_phuc"))
            if khoi_phuc is None:
                return False, "Thiếu ngân sách khôi phục"
            if not (0 < khoi_phuc <= TRAN_NGAN_SACH_KHOI_PHUC):
                return False, (f"Ngân sách khôi phục phải từ 1 đến "
                               f"{tien(TRAN_NGAN_SACH_KHOI_PHUC)}, "
                               f"đang là {tien(khoi_phuc)}")
            # Chi duoc hoan tac trong 24 gio ke tu luc tat
            tat_luc = _gio(de_xuat.get("tao_luc"))
            if tat_luc is None:
                return False, "Không đọc được thời điểm đã tắt nhóm"
            if (goc - tat_luc) > timedelta(minutes=HAN_HOAN_TAC_PHUT):
                return False, "Nhóm đã tắt quá 24 giờ, không hoàn tác tự động nữa"
            # KHONG ap tran hanh dong cho viec HOAN TAC.
            #
            # LOI THAT do kiem thu bat duoc (30/09/2026): chinh lenh TAT vua roi
            # duoc tinh la "1 hanh dong trong gio", nen neu ap tran thi nut HOAN
            # TAC bi chan NGAY SAU KHI VUA TAT — dung luc can nhat. Hoan tac la
            # sua lai mot viec vua lam, khong phai mot quyet dinh moi, nen khong
            # the tinh nhu mot hanh dong doc lap.
            # Van giu: ten phai thuoc pham vi, ngan sach khong vuot tran, va chi
            # trong 24 gio ke tu luc tat.
            return True, "cho phép"

        # ================= TAT NHOM =================
        # --- Rao 4: ngan sach ha ve dung 27.000 ---
        ha = _so(de_xuat.get("ngan_sach_ha"))
        if ha is None:
            return False, "Đề xuất thiếu ngân sách hạ về"
        if int(ha) != NGAN_SACH_HA:
            return False, (f"Ngân sách hạ về phải đúng {tien(NGAN_SACH_HA)}, "
                           f"đang là {tien(ha)}")

        # --- Rao 3: cam tat nhom dang hieu qua ---
        # Phan biet "KHONG CO luot mua" (hop le - nhom moi chay) voi
        # "co truong nhung DOC KHONG RA" (du lieu hong - phai chan, khong duoc
        # coi nhu 0). Da gap that khi dung thu.
        if "luot_mua" in de_xuat and de_xuat.get("luot_mua") is not None:
            if _so(de_xuat.get("luot_mua")) is None:
                return False, (f"Số lượt mua đọc không ra: "
                               f"{de_xuat.get('luot_mua')!r}")
        mua = _so(de_xuat.get("luot_mua"))
        cpr = _so(de_xuat.get("chi_phi_moi_luot"))
        if mua is not None and mua >= 1:
            if cpr is None:
                return False, "Nhóm có lượt mua nhưng không đọc được chi phí mỗi lượt"
            if cpr < MOC_CPR:
                return False, (f"Nhóm ĐANG HIỆU QUẢ: {tien(cpr)}/lượt mua, "
                               f"dưới mốc {tien(MOC_CPR)}")

        # --- Rao 6: de xuat qua 24 gio thi het hieu luc ---
        tao_luc = _gio(de_xuat.get("tao_luc"))
        if de_xuat.get("tao_luc") is not None and tao_luc is None:
            return False, "Thời điểm tạo đề xuất không đọc được"
        if tao_luc is not None and (goc - tao_luc) > timedelta(minutes=HAN_CHO_PHUT):
            return False, "Đề xuất đã quá 24 giờ, không còn hiệu lực"

        # --- Rao 8: khong hoi lai nhom da co cau tra loi ---
        da_tra_loi = ls.get("nhom_da_tra_loi")
        if isinstance(da_tra_loi, dict):
            t_cu = _gio(da_tra_loi.get(ma))
            if t_cu is not None and (goc - t_cu) < timedelta(minutes=HAN_HOI_LAI_PHUT):
                return False, "Nhóm này Đại đã trả lời trong 24 giờ qua"

        # --- Rao 5: han muc hanh dong ---
        n_ngay = _so(ls.get("so_hanh_dong_hom_nay")) or 0
        n_gio = _so(ls.get("so_hanh_dong_gio_nay")) or 0
        if n_ngay >= TOI_DA_NGAY:
            return False, f"Hôm nay đã đủ {TOI_DA_NGAY} hành động"
        if n_gio >= TOI_DA_GIO:
            return False, "Giờ này đã có một hành động rồi"

        return True, "cho phép"
    except Exception as e:                      # khong bao gio nem loi
        return False, f"Lỗi khi kiểm rào an toàn: {type(e).__name__}: {e}"
