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

# ==========================================================================
# PHAM VI DUY NHAT: ten doi tuong PHAI chua "dainq".
# ==========================================================================
#
# Dai chot lai 15:23-15:27 ngay 02/10/2026, nguyen van:
#   "phai nho chi lam voi nhung chien dich, nhom va quang cao co chua 'dainq'"
#   "nhung quang cao nay deu co dinh dang la new - dainq - THC....ma.
#    Cai THC la ma content lan dau toi len quang cao"
#
# Truoc day rao con nhan them 2 kieu: "new - dainq" (da nam trong 'dainq')
# va "ten bat dau bang MA CONTENT VIET HOA" (RE_MA_CONTENT).
#
# DO THAT tren act_ (doc het 4200 nhom):
#   - Rao CU  (dainq | new-dainq | ma content) : 4005 nhom
#   - Rao MOI (chi 'dainq')                    : 4005 nhom
#   - Chenh lech                               : 0 nhom
#   - So nhom bat dau bang ma content KHONG chua 'dainq': 0
# => Nhanh ma content la THUA, BO DI KHONG MAT NHOM NAO CUA DAI.
#    Va bo di thi khong con cua mo cho nguoi khac.
#
# ⚠️ RUI RO THAT SU da do duoc: tai khoan co 101 nhom KHONG chua 'dainq'
#    (90 cua Truong + 11 cua Thao), trong do 40 nhom dang ACTIVE.
#    Neu rao rong qua thi agent dong vao TAI SAN CUA NGUOI KHAC.
RE_MA_CONTENT = re.compile(r"^[A-Z]{2,}\d")   # giu lai chi de tuong thich nguoc
                                              # — KHONG dung trong thuoc_pham_vi

MOC_CPR = 390000          # nguong gia moi luot mua cua TH3 (Dai chot 01/10/2026)
NGAN_SACH_HA = 27000      # ngan sach ha ve khi tat
# Tran hanh dong. 0 = KHONG GIOI HAN.
# Doi 01/10/2026 theo yeu cau cua Dai: "khong gioi han so lan bao".
# Vi sao bo: moi hanh dong deu PHAI co Dai bam nut moi chay, nen tran nay khong
# ngan duoc agent lam bua — no chi ngan CHINH DAI lam viec. Thuc te 01/10: Dai
# tat 1 nhom luc 12:07 thi ca gio sau khong tat duoc nhom nao nua.
# Muon dat lai tran: sua hai so duoi day (vi du 20 va 5).
TOI_DA_NGAY = 0           # tran hanh dong moi ngay (0 = khong gioi han)
TOI_DA_GIO = 0            # tran hanh dong moi gio (0 = khong gioi han)
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

    ==========================================================================
    LUAT DUY NHAT: ten PHAI chua "dainq". Khong co ngoai le nao khac.
    ==========================================================================

    Dai chot lai 15:23 ngay 02/10/2026:
        "phai nho chi lam voi nhung chien dich, nhom va quang cao co chua
         'dainq' la duoc"

    Truoc day ham nay con nhan 2 kieu nua (nay BO):
      - "new - dainq": da nam trong 'dainq', viet rieng la thua.
      - "ten bat dau bang MA CONTENT VIET HOA" (vd THC295THM295):
        Dai giai thich 15:27 — quang cao kieu do LUON co dang
        "new - dainq - THC..." nen DA chua 'dainq'.
        Do that: 0/4200 nhom bat dau bang ma content ma thieu 'dainq';
        siet lai KHONG lam mat nhom nao cua Dai (4005 -> 4005).

    ⚠️ VI SAO KHONG DUOC NOI LONG RAO NAY:
       Do that tren act_ — co 101 nhom KHONG chua 'dainq'
       (90 cua Truong + 11 cua Thao), trong do 40 nhom dang ACTIVE.
       Ten quang cao ben trong do META TU SINH ('Quảng cáo Lượt tương tác mới')
       nen KHONG BAO GIO co 'dainq'.
       => Pham vi LUON kiem theo TEN NHOM. Tuyet doi KHONG kiem theo ten
          quang cao: lam vay thi ad cua chinh Dai cung bi loai.
    """
    if not isinstance(ten, str) or not ten.strip():
        return False
    return "dainq" in ten.strip().lower()


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
        #
        # ⚠️ CAP "ad" KHONG kiem ten QUANG CAO o day — xem giai thich o nhanh
        # cap == "ad" ben duoi. Ten o day la ten QUANG CAO (Meta tu sinh), va
        # no CO THE khong chua 'dainq'. Pham vi that su duoc kiem theo TEN NHOM
        # trong nhanh cap == "ad" (va kiem lai lan nua khi ghi len Meta).
        cap = doi_tuong.get("cap") or "ad_set"
        ten = doi_tuong.get("ten")
        if cap != "ad":
            if not thuoc_pham_vi(ten):
                return False, (f"Tên nhóm không thuộc phạm vi của Đại "
                               f"(phải có 'dainq'): {str(ten)[:60]}")

        ma = doi_tuong.get("id")
        if not ma:
            return False, ("Đề xuất thiếu mã quảng cáo" if cap == "ad"
                           else "Đề xuất thiếu mã nhóm quảng cáo")
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

        # ================= TAT LE QUANG CAO (Viec B) =================
        if cap == "ad":
            # Dai chot 02/10/2026: tat le quang cao CHI TAT + DOI TEN.
            # KHONG ha ngan sach — ha ngan sach la viec cua CA NHOM.
            # Vi vay rao 4 (ngan sach ha ve dung 27.000) KHONG ap o day;
            # thay vao do bat buoc PHẢI None de khong ai vo tinh gui tien len.
            if de_xuat.get("ngan_sach_ha") is not None:
                return False, ("Tắt lẻ quảng cáo KHÔNG được hạ ngân sách "
                               "(hạ ngân sách là việc của cả nhóm)")
            # Phai biet ten nhom de kiem pham vi — xem agent_cong_cu_ghi.
            # tat_mot_quang_cao (do lai ten nhom that truoc khi ghi).
            if not (doi_tuong.get("ten_nhom") or "").strip():
                return False, "Đề xuất thiếu tên nhóm chứa quảng cáo"
            if not (doi_tuong.get("adset_id") or "").strip():
                return False, "Đề xuất thiếu mã nhóm chứa quảng cáo"
            # Kiem luon ten nhom chua no (quy tac sat: pham vi theo TEN NHOM).
            if not thuoc_pham_vi(doi_tuong.get("ten_nhom")):
                return False, (f"Tên nhóm không thuộc phạm vi của Đại "
                               f"(phải có 'dainq'): "
                               f"{str(doi_tuong.get('ten_nhom'))[:60]}")
            # Cac rao con lai (hieu qua / 24 gio / da tra loi / bo qua /
            # han muc) VAN ap dung nhu tắt nhóm — chay tiep xuong duoi.
            # `ma` o day la ma QUANG CAO, va so tay ghi theo ma quang cao.
        else:
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
                # ⚠️ NGOAI LE (Dai chot 03/10/2026): cau tra loi cu KHONG con gia
                # tri neu nhom da duoc BAT LAI SAU do roi chay lai phat sinh chi
                # tieu. Truong hop that 03/10: Dai tra loi nhom 120250389649480509
                # luc 02/10 11:45; nhom duoc bat lai, chay lai; nhom cham nguong
                # lan nua nhung agent im lang suot 24 gio => Dai tuong bot chet
                # va tu vao Meta tat tay.
                # Xem docs/superpowers/plans/2026-10-03-thong-bao-khi-tu-hanh-va-va-rao-8.md
                #
                # Khoanh vung HEP co chu dich: chi mo dung truong hop nay. Moi
                # truong hop khac (chua bat lai / bat lai truoc khi tra loi /
                # bat lai dung bang thoi diem tra loi) VAN CHAN nhu cu.
                t_bat_lai = None
                ban_lai = ls.get("nhom_bat_lai_gan_nhat")
                if isinstance(ban_lai, dict):
                    t_bat_lai = _gio(ban_lai.get(ma))
                # `<=` chu KHONG phai `<`: bat lai dung bang thoi diem tra loi
                # thi khong tinh la tinh huong moi — uu tien AN TOAN.
                if t_bat_lai is None or t_bat_lai <= t_cu:
                    return False, "Nhóm này Đại đã trả lời trong 24 giờ qua"

        # --- Rao: Dai da bam "Bo qua 24h" tren tin bao loi (02/10/2026) ---
        dang_bo_qua = ls.get("nhom_dang_bo_qua")
        if isinstance(dang_bo_qua, dict):
            den = _gio(dang_bo_qua.get(ma)) or _gio(dang_bo_qua.get(str(ma)))
            if den is not None and goc < den:
                return False, (f"Đại đã chọn BỎ QUA nhóm này đến "
                               f"{den.strftime('%H:%M ngày %d/%m')}")

        # --- Rao 5: han muc hanh dong (0 = khong gioi han) ---
        n_ngay = _so(ls.get("so_hanh_dong_hom_nay")) or 0
        n_gio = _so(ls.get("so_hanh_dong_gio_nay")) or 0
        if TOI_DA_NGAY > 0 and n_ngay >= TOI_DA_NGAY:
            return False, f"Hôm nay đã đủ {TOI_DA_NGAY} hành động"
        if TOI_DA_GIO > 0 and n_gio >= TOI_DA_GIO:
            return False, "Giờ này đã có một hành động rồi"

        return True, "cho phép"
    except Exception as e:                      # khong bao gio nem loi
        return False, f"Lỗi khi kiểm rào an toàn: {type(e).__name__}: {e}"
