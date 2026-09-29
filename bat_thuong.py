"""
PHAT HIEN SO LIEU BAT THUONG
=============================
Ba dieu kien duy nhat duoc coi la bat thuong (ban thiet ke muc 7.3). Co tinh
KHONG them dieu kien nao khac: mot canh bao sai lam Dai mat long tin vao ca
nhung canh bao dung.

  (1) Chi tieu vot: chi tieu > 3 lan muc trung binh 7 ngay truoc do.
  (2) Chi ma khong co ket qua: chi tieu > 0, luot mua = 0, trong khi 7 ngay
      truoc do trung binh van co luot mua.
  (3) Tat ca deu bang 0: moi chi so = 0, trong khi 7 ngay truoc do NGAY NAO
      cung co chi tieu -> dau hieu token hoac bo loc hong.

Can it nhat 7 ngay lich su moi bat kiem tra. Chua du thi BO QUA, khong canh
bao - canh bao "bat thuong" khi chua co gi de so sanh la vo nghia.

Hai dieu kien (1) va (2) CHI ap dung cho bao cao TRON mot ngay. Ly do: bao cao
moc 12h, 17h chi la MOT PHAN cua ngay (so tich luy tu 0h den gio bao cao), dem
so nua ngay so voi trung binh ngay day du thi luon thay "thap bat thuong" - sai
hoan toan. Dieu kien (3) ap dung cho moi moc: moi chi so bang 0 thi du la moc
nao cung la dau hieu hong.

KHONG BAO GIO tu y chan bao cao. Chi them mot dong canh bao o dau.
"""
import lich_su

# So ngay lich su toi thieu moi duoc phep ket luan.
SO_NGAY_LICH_SU_TOI_THIEU = 7

# Chi tieu ky nay lon hon bao nhieu lan muc trung binh thi coi la vot.
HE_SO_CHI_TIEU_VOT = 3.0

CAC_CHI_SO = ("spend", "msg", "contact", "order", "purchase", "payment", "comment")


def _so(v):
    """Doi ve so thuc. Gia tri la khong doi duoc -> 0."""
    try:
        return float(v or 0)
    except (ValueError, TypeError):
        return 0.0


def _tien(v):
    """20319895 -> '20.319.895'."""
    return f"{int(round(_so(v))):,}".replace(",", ".")


def kiem_tra(stats, duong_dan_lich_su, ngay, tron_ngay=False):
    """Tra ve DANH SACH LY DO (chuoi tieng Viet). Rong = binh thuong.

    stats: dict do report.compute_stats() tra ve.
    ngay:  ngay KET THUC cua ky bao cao (date hoac 'YYYY-MM-DD').
    tron_ngay: True neu bao cao bao TRON mot ngay (thuong la moc sang).

    KHONG BAO GIO nem loi: moi truc trac deu tra ve danh sach rong.
    """
    try:
        tong = (stats or {}).get("totals") or {}
    except AttributeError:
        return []

    # Chi ket luan khi THUC SU nhan duoc du cac chi so.
    #
    # Vi sao can chan doan nay: neu `stats` rong hoac thieu chi so, moi phep doc
    # deu ra 0, va dieu kien (3) se bao "moi chi so deu bang 0" - mot canh bao
    # SAI. Da bi buoc dung thu bat duoc ngay 29/09/2026 voi stats = {} va None.
    if not isinstance(tong, dict) or not all(k in tong for k in CAC_CHI_SO):
        return []

    tu, den = lich_su.cua_so_truoc(ngay, SO_NGAY_LICH_SU_TOI_THIEU)
    if tu is None:
        return []

    try:
        truoc = lich_su.lay_khoang(duong_dan_lich_su, tu, den)
        data = lich_su.doc(duong_dan_lich_su)
    except Exception:
        return []

    so_ngay = int(truoc.get("so_ngay", 0) or 0)
    if so_ngay < SO_NGAY_LICH_SU_TOI_THIEU:
        return []

    tong_truoc = truoc.get("tong") or {}
    tb_spend = _so(tong_truoc.get("spend")) / so_ngay
    tb_purchase = _so(tong_truoc.get("purchase")) / so_ngay

    spend = _so(tong.get("spend"))
    purchase = _so(tong.get("purchase"))

    ly_do = []

    # (1) Chi tieu vot
    if tron_ngay and tb_spend > 0 and spend > HE_SO_CHI_TIEU_VOT * tb_spend:
        ly_do.append(
            f"chi tiêu {_tien(spend)} đồng, cao hơn {HE_SO_CHI_TIEU_VOT:.0f} lần "
            f"mức trung bình {_tien(tb_spend)} đồng/ngày của {so_ngay} ngày trước đó"
        )

    # (2) Chi ma khong co ket qua
    if tron_ngay and spend > 0 and purchase == 0 and tb_purchase > 0:
        ly_do.append(
            f"có chi tiêu {_tien(spend)} đồng nhưng 0 lượt mua, trong khi "
            f"{so_ngay} ngày trước đó trung bình có {tb_purchase:.1f} lượt mua/ngày"
        )

    # (3) Tat ca deu bang 0 - ap dung cho MOI moc bao cao.
    # Doi hoi NGAY NAO trong 7 ngay truoc cung co chi tieu: neu truoc do da co
    # ngay chi tieu bang 0 thi mot ngay bang 0 nua la chuyen binh thuong.
    if spend == 0 and all(_so(tong.get(k)) == 0 for k in CAC_CHI_SO):
        so_ngay_co_chi_tieu = 0
        for k in sorted(data):
            if tu <= k <= den and _so((data[k].get("tong") or {}).get("spend")) > 0:
                so_ngay_co_chi_tieu += 1
        if so_ngay_co_chi_tieu >= so_ngay:
            ly_do.append(
                f"mọi chỉ số đều bằng 0, trong khi {so_ngay} ngày trước đó "
                f"ngày nào cũng có chi tiêu"
            )

    return ly_do


def canh_bao(danh_sach_ly_do):
    """Dong canh bao dat o DAU bao cao. Khong co ly do -> chuoi rong."""
    if not danh_sach_ly_do:
        return ""
    return (
        "⚠️ Số liệu kỳ này trông bất thường: "
        + "; ".join(danh_sach_ly_do)
        + ". Nên kiểm tra lại trước khi tin.\n"
    )
