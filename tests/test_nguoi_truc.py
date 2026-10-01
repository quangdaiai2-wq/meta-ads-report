"""Kiem thu nguoi_truc - tien trinh thuong tru cua bao cao Meta Ads."""
import unittest
from datetime import datetime, timedelta

import nguoi_truc

TrangThaiThu = nguoi_truc.TrangThaiThu


def setUpModule():
    """Kiem thu KHONG duoc ghi vao logs/baocao.log that.

    report.log() ghi thang vao file nhat ky san xuat, nen chay kiem thu se
    lam ban chinh file Dai mo dau tien khi co su co (thay cac dong nhu
    "da tra loi mot tin nhan" cho nhung tin khong he ton tai).
    """
    nguoi_truc.report.log = lambda message: None


def luc(gio, phut=0, giay=0, ngay=28):
    """Mot thoi diem gia de kiem thu, khong phu thuoc dong ho that."""
    return datetime(2026, 9, ngay, gio, phut, giay)


class TestMocDaToi(unittest.TestCase):
    def test_truoc_moc_thi_chua_toi(self):
        self.assertEqual(nguoi_truc.moc_da_toi(luc(7, 59, 59), [8, 12, 17]), [])

    def test_dung_moc_thi_da_toi(self):
        self.assertEqual(nguoi_truc.moc_da_toi(luc(8, 0, 0), [8, 12, 17]), [8])

    def test_sau_moc_30_giay_van_da_toi(self):
        self.assertEqual(nguoi_truc.moc_da_toi(luc(8, 0, 30), [8, 12, 17]), [8])

    def test_qua_nhieu_moc_thi_tra_ve_het(self):
        self.assertEqual(nguoi_truc.moc_da_toi(luc(13), [8, 12, 17]), [8, 12])


class TestChonMocCanGui(unittest.TestCase):
    def test_chua_toi_moc_nao_thi_khong_gui(self):
        moc, bo_qua = nguoi_truc.chon_moc_can_gui(
            luc(7), [8, 12, 17], set(), TrangThaiThu()
        )
        self.assertIsNone(moc)
        self.assertEqual(bo_qua, [])

    def test_toi_moc_8_thi_gui_moc_8(self):
        moc, bo_qua = nguoi_truc.chon_moc_can_gui(
            luc(8, 0, 5), [8, 12, 17], set(), TrangThaiThu()
        )
        self.assertEqual(moc, 8)
        self.assertEqual(bo_qua, [])

    def test_moc_8_da_gui_roi_thi_toi_moc_12_gui_moc_12(self):
        moc, _ = nguoi_truc.chon_moc_can_gui(
            luc(12, 0, 5), [8, 12, 17], {8}, TrangThaiThu()
        )
        self.assertEqual(moc, 12)

    def test_thuc_day_luc_12h05_khi_chua_gui_gi_chi_gui_MOT_bao_cao_moc_12(self):
        # Bai quan trong nhat cua ca giai doan. Truoc day ba lich chay bu cung
        # luc se gui ca bao cao 8h, 12h, 17h. Nguoi truc chi gui DUNG MOT bao
        # cao, cho moc gan nhat.
        moc, bo_qua = nguoi_truc.chon_moc_can_gui(
            luc(12, 5), [8, 12, 17], set(), TrangThaiThu()
        )
        self.assertEqual(moc, 12)
        self.assertEqual(bo_qua, [8])

    def test_bat_may_luc_9h30_sau_hai_ngay_tat_chi_gui_moc_8(self):
        moc, bo_qua = nguoi_truc.chon_moc_can_gui(
            luc(9, 30), [8, 12, 17], set(), TrangThaiThu()
        )
        self.assertEqual(moc, 8)
        self.assertEqual(bo_qua, [])

    def test_moc_17_con_o_tuong_lai_thi_khong_gui(self):
        moc, _ = nguoi_truc.chon_moc_can_gui(
            luc(14), [8, 12, 17], {8, 12}, TrangThaiThu()
        )
        self.assertIsNone(moc)

    def test_moc_gan_nhat_het_luot_thu_thi_KHONG_gui_moc_cu_hon(self):
        # Moc 12 da thu het luot va that bai -> KHONG duoc gui moc 8, vi bao
        # cao moc 8 la bao cao cu hon.
        tt = TrangThaiThu()
        now = luc(12, 5)
        for _ in range(nguoi_truc.MAX_LAN_THU_MOI_MOC):
            tt.ghi_lan_thu(12, now)
        moc, _ = nguoi_truc.chon_moc_can_gui(now, [8, 12, 17], set(), tt)
        self.assertIsNone(moc)


class TestTrangThaiThu(unittest.TestCase):
    def test_lan_dau_thi_duoc_thu(self):
        self.assertTrue(TrangThaiThu().duoc_thu(12, luc(12)))

    def test_vua_thu_xong_thi_chua_duoc_thu_lai(self):
        tt = TrangThaiThu()
        now = luc(12)
        tt.ghi_lan_thu(12, now)
        self.assertFalse(tt.duoc_thu(12, now + timedelta(seconds=60)))

    def test_qua_khoang_nghi_thi_duoc_thu_lai(self):
        tt = TrangThaiThu()
        now = luc(12)
        tt.ghi_lan_thu(12, now)
        self.assertTrue(
            tt.duoc_thu(12, now + timedelta(seconds=nguoi_truc.KHOANG_NGHI_GIUA_HAI_LAN_THU))
        )

    def test_thu_qua_so_lan_thi_khong_thu_nua(self):
        tt = TrangThaiThu()
        now = luc(12)
        for i in range(nguoi_truc.MAX_LAN_THU_MOI_MOC):
            tt.ghi_lan_thu(12, now + timedelta(seconds=i * 10000))
        # Van trong CUNG NGAY (23h) -> het luot thi khong thu nua.
        # (Neu lui qua ngay hom sau thi dem lai tu dau - do la bai duoi.)
        self.assertFalse(tt.duoc_thu(12, luc(23)))

    def test_sang_ngay_moi_thi_dem_lai_tu_dau(self):
        tt = TrangThaiThu()
        for _ in range(nguoi_truc.MAX_LAN_THU_MOI_MOC):
            tt.ghi_lan_thu(12, luc(12))
        self.assertTrue(tt.duoc_thu(12, luc(12, ngay=29)))

    def test_moc_khac_khong_bi_anh_huong(self):
        tt = TrangThaiThu()
        now = luc(12)
        for _ in range(nguoi_truc.MAX_LAN_THU_MOI_MOC):
            tt.ghi_lan_thu(12, now)
        self.assertTrue(tt.duoc_thu(17, now))


class TrucGia:
    """Mot NguoiTruc voi dong ho va moi thu ben ngoai deu gia - khong goi mang.

    Dung chung cho ca Task 2 va Task 3. Doi gio bang cach gan `tg.now`.
    """

    def __init__(self, now, da_gui=None, che_do_thu=False, ket_qua_gui=True,
                 tin_cho_san=None, tra_loi_ai_fn=None, doc_han_fn=None):
        self.now = now
        self.da_gui = set(da_gui or ())
        self.gui_roi = []
        self.tin_da_gui = []
        self._ket_qua_gui = ket_qua_gui
        self._tin_cho_san = list(tin_cho_san or [])
        self.so_lan_lay_tin = 0
        self.truc = nguoi_truc.NguoiTruc(
            env={"TELEGRAM_CHAT_ID": "123", "REPORT_ACCOUNT_NAME": "Test"},
            danh_sach_moc=[8, 12, 17],
            che_do_thu=che_do_thu,
            gui_bao_cao_fn=self._gui,
            gui_tin_fn=self._gui_tin,
            doc_da_gui_fn=lambda ngay: sorted(self.da_gui),
            dong_ho=lambda: self.now,
            xa_tin_fn=lambda env: (None, None),
            lay_tin_fn=self._lay_tin,
            tra_loi_ai_fn=tra_loi_ai_fn,
            doc_han_fn=doc_han_fn,
        )

    def _gui(self, moc):
        """Tra ve MA THOAT (0 thanh cong / 1 tam thoi / 2 vinh vien).

        `ket_qua_gui` nhan True/False nhu truoc (True -> 0, False -> 1) HOAC
        mot ma thoat cu the, de kiem duoc truong hop loi vinh vien.
        """
        self.gui_roi.append(moc)
        kq = self._ket_qua_gui
        if kq is True:
            return nguoi_truc.report.MA_THOAT_OK
        if kq is False:
            return nguoi_truc.report.MA_THOAT_TAM_THOI
        return kq

    def _gui_tin(self, text):
        self.tin_da_gui.append(text)
        return True

    def _lay_tin(self, env, offset):
        """Tra ve tin cho san o lan goi dau, cac lan sau tra ve rong."""
        self.so_lan_lay_tin += 1
        if self.so_lan_lay_tin == 1 and self._tin_cho_san:
            return list(self._tin_cho_san), None
        return [], None


class TestCanhMoc(unittest.TestCase):
    def test_toi_moc_thi_gui_dung_mot_lan(self):
        tg = TrucGia(luc(8, 0, 5))
        tg.truc.canh_moc(luc(8, 0, 5))
        tg.truc.canh_moc(luc(8, 0, 35))
        self.assertEqual(tg.gui_roi, [8])

    def test_chua_toi_moc_thi_khong_gui(self):
        tg = TrucGia(luc(7, 30))
        tg.truc.canh_moc(luc(7, 30))
        self.assertEqual(tg.gui_roi, [])

    def test_moc_da_gui_trong_ngay_thi_khong_gui_lai(self):
        tg = TrucGia(luc(12, 0, 5), da_gui={8, 12})
        tg.truc.canh_moc(luc(12, 0, 5))
        self.assertEqual(tg.gui_roi, [])

    def test_thuc_day_luc_12h05_chi_gui_mot_bao_cao(self):
        tg = TrucGia(luc(12, 5))
        tg.truc.canh_moc(luc(12, 5))
        self.assertEqual(tg.gui_roi, [12])

    def test_gui_that_bai_thi_con_luot_thu_lai(self):
        tg = TrucGia(luc(12, 0, 5), ket_qua_gui=False)
        tg.truc.canh_moc(luc(12, 0, 5))
        self.assertEqual(tg.gui_roi, [12])
        # Chua qua khoang nghi -> khong thu lai ngay lap tuc
        tg.truc.canh_moc(luc(12, 1, 0))
        self.assertEqual(tg.gui_roi, [12])

    def test_qua_khoang_nghi_thi_thu_lai(self):
        tg = TrucGia(luc(12, 0, 5), ket_qua_gui=False)
        tg.truc.canh_moc(luc(12, 0, 5))
        sau = luc(12, 0, 5) + timedelta(seconds=nguoi_truc.KHOANG_NGHI_GIUA_HAI_LAN_THU)
        tg.truc.canh_moc(sau)
        self.assertEqual(tg.gui_roi, [12, 12])


class TestTinTuDai(unittest.TestCase):
    def _tin(self, chat_id, text="hi"):
        return {"update_id": 1, "message": {"chat": {"id": chat_id}, "text": text}}

    def test_dung_chat_id_thi_nhan(self):
        self.assertTrue(nguoi_truc.tin_tu_dai(self._tin(123), "123"))

    def test_chat_id_khac_thi_bo_qua(self):
        self.assertFalse(nguoi_truc.tin_tu_dai(self._tin(999), "123"))

    def test_so_va_chuoi_deu_khop(self):
        self.assertTrue(nguoi_truc.tin_tu_dai(self._tin(123), 123))

    def test_tin_khong_co_message_thi_bo_qua(self):
        self.assertFalse(nguoi_truc.tin_tu_dai({"update_id": 1}, "123"))

    def test_tin_khong_co_chat_thi_bo_qua(self):
        self.assertFalse(nguoi_truc.tin_tu_dai({"update_id": 1, "message": {}}, "123"))


class TestNoiDungTin(unittest.TestCase):
    def test_lay_duoc_chu(self):
        tin = {"message": {"chat": {"id": 1}, "text": "  còn sống không?  "}}
        self.assertEqual(nguoi_truc.noi_dung_tin(tin), "còn sống không?")

    def test_tin_khong_co_chu_tra_ve_rong(self):
        self.assertEqual(nguoi_truc.noi_dung_tin({"message": {"chat": {"id": 1}}}), "")

    def test_tin_hong_tra_ve_rong(self):
        self.assertEqual(nguoi_truc.noi_dung_tin({}), "")


class TestThamSoLayTin(unittest.TestCase):
    def test_co_offset_thi_truyen_offset(self):
        self.assertEqual(nguoi_truc.tham_so_lay_tin(100)["offset"], 100)

    def test_offset_None_thi_khong_truyen(self):
        self.assertNotIn("offset", nguoi_truc.tham_so_lay_tin(None))

    def test_chi_nhan_update_loai_message_va_nut_bam(self):
        """Tu 30/09/2026 xin nhan CA `callback_query` (lan BAM NUT cua agent nac 2).

        Bat buoc phai xin nhan: Telegram chi giao mot update cho MOT nguoi goi,
        ma `offset` thi xoa vinh vien moi update co ma nho hon. Loai nao khong
        xin nhan o day se bi nuot mat truoc khi agent kip thay — nghia la nut
        bam cua Dai khong bao gio toi duoc agent.
        """
        import json as _json
        ds = _json.loads(nguoi_truc.tham_so_lay_tin(None)["allowed_updates"])
        self.assertEqual(sorted(ds), ["callback_query", "message"])


class TestOffsetMoi(unittest.TestCase):
    def test_khong_co_tin_thi_None(self):
        self.assertIsNone(nguoi_truc.offset_moi_tu_ket_qua([]))

    def test_lay_tin_cuoi_cong_mot(self):
        self.assertEqual(
            nguoi_truc.offset_moi_tu_ket_qua([{"update_id": 5}, {"update_id": 9}]), 10
        )


class TestTraLoiTinNhan(unittest.TestCase):
    def _tra_loi(self, cau_hoi, tra_loi_ai_fn=None):
        return nguoi_truc.tra_loi_tin_nhan(
            cau_hoi=cau_hoi,
            env={"REPORT_ACCOUNT_NAME": "Test"},
            danh_sach_moc=[8, 12, 17],
            bat_dau=luc(6),
            lan_gui_cuoi=luc(12, 1),
            da_gui={8, 12},
            now=luc(13),
            tra_loi_ai_fn=tra_loi_ai_fn,
        )

    def test_hoi_con_song_thi_tra_loi_tinh_trang(self):
        tl = self._tra_loi("còn sống không?")
        self.assertIn("đang chạy", tl)
        self.assertIn("17h", tl)

    def test_hoi_khong_dau_cung_hieu(self):
        self.assertIn("đang chạy", self._tra_loi("con song khong"))

    def test_tinh_trang_liet_ke_moc_da_gui_hom_nay(self):
        tl = self._tra_loi("còn sống không?")
        self.assertIn("8h", tl)
        self.assertIn("12h", tl)

    def test_hoi_con_song_thi_khong_goi_ai(self):
        """Cau hoi suc khoe phai tra loi ngay, KHONG ton luot AI."""
        da_goi = []

        def ai_gia(cau_hoi):
            da_goi.append(cau_hoi)
            return "khong bao gio toi day", None

        self._tra_loi("còn sống không?", tra_loi_ai_fn=ai_gia)
        self.assertEqual(da_goi, [])

    def test_cau_hoi_so_lieu_thi_goi_ai(self):
        da_goi = []

        def ai_gia(cau_hoi):
            da_goi.append(cau_hoi)
            return "Chi tieu hom qua la 7.034.942 dong.", None

        tl = self._tra_loi("camp nào tệ nhất tuần này?", tra_loi_ai_fn=ai_gia)
        self.assertEqual(da_goi, ["camp nào tệ nhất tuần này?"])
        self.assertIn("7.034.942", tl)

    def test_ai_loi_thi_tra_loi_kem_ly_do(self):
        def ai_gia(cau_hoi):
            return None, "HTTP 429 - het han muc goi AI"

        tl = self._tra_loi("doanh thu hôm nay?", tra_loi_ai_fn=ai_gia)
        self.assertIn("chưa trả lời được", tl)
        self.assertIn("HTTP 429", tl)

    def test_ai_nem_loi_cung_khong_lam_chet(self):
        def ai_gia(cau_hoi):
            raise RuntimeError("no ra")

        tl = self._tra_loi("số hôm nay?", tra_loi_ai_fn=ai_gia)
        self.assertIn("chưa trả lời được", tl)

    def test_tin_rong_thi_khong_goi_ai(self):
        da_goi = []

        def ai_gia(cau_hoi):
            da_goi.append(cau_hoi)
            return "x", None

        self._tra_loi("   ", tra_loi_ai_fn=ai_gia)
        self.assertEqual(da_goi, [])

    def test_cau_hoi_rong_thi_bao_khong_thay_noi_dung(self):
        """Tin rong KHONG duoc goi AI (khong ton luot AI vo ich)."""
        self.assertIn("chưa thấy nội dung", self._tra_loi(""))


class TestDinhDangThoiGian(unittest.TestCase):
    def test_duoi_mot_gio_thi_ra_phut(self):
        self.assertEqual(nguoi_truc._thoi_gian_da_chay(90), "1 phút")

    def test_vai_gio_thi_ra_gio_va_phut(self):
        self.assertEqual(nguoi_truc._thoi_gian_da_chay(3 * 3600 + 120), "3 giờ 2 phút")

    def test_qua_mot_ngay_thi_ra_ngay(self):
        self.assertEqual(
            nguoi_truc._thoi_gian_da_chay(86400 + 2 * 3600), "1 ngày 2 giờ"
        )


class TestXuLyTin(unittest.TestCase):
    """Dung lai TrucGia da dinh nghia trong Task 2."""

    def test_tin_tu_nguoi_la_thi_khong_tra_loi(self):
        tg = TrucGia(luc(13))
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 999}, "text": "cho xin so lieu"},
        })
        self.assertEqual(tg.tin_da_gui, [])

    def test_tin_tu_dai_hoi_con_song_thi_tra_loi(self):
        tg = TrucGia(luc(13))
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "còn sống không?"},
        })
        self.assertEqual(len(tg.tin_da_gui), 1)
        self.assertIn("đang chạy", tg.tin_da_gui[0])

    def test_tin_tu_dai_hoi_so_lieu_thi_goi_ai(self):
        """Giai doan 4: cau hoi so lieu duoc lop AI tra loi, khong con bao 'chua co'."""
        tg = TrucGia(luc(13), tra_loi_ai_fn=lambda c: ("Chi tieu 7.034.942 dong.", None))
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "camp nào tệ nhất tuần này?"},
        })
        self.assertEqual(len(tg.tin_da_gui), 1)
        self.assertIn("7.034.942", tg.tin_da_gui[0])

    def test_tin_tu_dai_hoi_so_lieu_ai_loi_thi_noi_ro_ly_do(self):
        tg = TrucGia(luc(13), tra_loi_ai_fn=lambda c: (None, "HTTP 429 - het han muc"))
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "camp nào tệ nhất tuần này?"},
        })
        self.assertEqual(len(tg.tin_da_gui), 1)
        self.assertIn("HTTP 429", tg.tin_da_gui[0])

    def test_che_do_thu_thi_khong_gui_tin_ra_ngoai(self):
        tg = TrucGia(luc(13), che_do_thu=True)
        tg.truc.xu_ly_tin({
            "update_id": 1,
            "message": {"chat": {"id": 123}, "text": "còn sống không?"},
        })
        self.assertEqual(tg.tin_da_gui, [])


class TestMotVong(unittest.TestCase):
    """Ca mot vong lap. `nghe_telegram` vong dau chi xa tin ton dong."""

    def test_vong_dau_khong_gui_gi_khi_chua_toi_moc(self):
        tg = TrucGia(luc(7, 30))
        tg.truc.mot_vong()
        self.assertEqual(tg.gui_roi, [])

    def test_vong_dau_xa_tin_ton_dong_roi_moi_nghe(self):
        tg = TrucGia(luc(13))
        self.assertFalse(tg.truc.da_xa_tin_ton_dong)
        tg.truc.mot_vong()
        self.assertTrue(tg.truc.da_xa_tin_ton_dong)

    def test_nhip_tim_ghi_sau_dung_so_vong(self):
        tg = TrucGia(luc(13))
        tg.truc.so_vong = nguoi_truc.NHIP_TIM_MOI_VONG - 1
        tg.truc.mot_vong()
        self.assertEqual(tg.truc.so_vong, nguoi_truc.NHIP_TIM_MOI_VONG)


class TestGuiBaoCaoBangMaUtf8(unittest.TestCase):
    """report.py phai duoc goi voi bang ma UTF-8.

    Loi THAT 28/09/2026: khi Windows Task Scheduler khoi dong Nguoi truc,
    tien trinh con (report.py) lay bang ma theo locale cua Windows (cp1252),
    nen in bao cao co dau tieng Viet lam no CHET va bao cao KHONG duoc gui.
    """

    class KetQuaGia:
        returncode = 0
        stdout = ""
        stderr = ""

    def _chay_voi_ket_qua(self, ket_qua):
        da_goi = {}

        def chay_gia(lenh, **kw):
            da_goi["lenh"] = lenh
            da_goi["kw"] = kw
            return ket_qua

        goc = nguoi_truc.subprocess.run
        nguoi_truc.subprocess.run = chay_gia
        try:
            ket_qua_tra_ve = nguoi_truc.gui_bao_cao(8)
        finally:
            nguoi_truc.subprocess.run = goc
        return ket_qua_tra_ve, da_goi

    def test_truyen_encoding_utf8(self):
        _, da_goi = self._chay_voi_ket_qua(self.KetQuaGia())
        self.assertEqual(da_goi["kw"].get("encoding"), "utf-8")

    def test_truyen_errors_replace(self):
        # Ky tu nao khong ma hoa duoc thi thay bang '?', KHONG lam chet bao cao.
        _, da_goi = self._chay_voi_ket_qua(self.KetQuaGia())
        self.assertEqual(da_goi["kw"].get("errors"), "replace")

    def test_dat_PYTHONIOENCODING_cho_tien_trinh_con(self):
        _, da_goi = self._chay_voi_ket_qua(self.KetQuaGia())
        moi_truong = da_goi["kw"].get("env") or {}
        self.assertEqual(moi_truong.get("PYTHONIOENCODING"), "utf-8")

    def test_van_giu_bien_moi_truong_cu(self):
        # Dat them bien chu KHONG duoc xoa sach moi truong cua tien trinh cha.
        _, da_goi = self._chay_voi_ket_qua(self.KetQuaGia())
        moi_truong = da_goi["kw"].get("env") or {}
        self.assertIn("PATH", moi_truong)

    def test_van_tra_ve_MA_THOAT_OK_khi_thanh_cong(self):
        ma, _ = self._chay_voi_ket_qua(self.KetQuaGia())
        self.assertEqual(ma, nguoi_truc.report.MA_THOAT_OK)


class TestMaThoatCuaReport(unittest.TestCase):
    """Nguoi truc phai phan biet duoc loi TAM THOI va loi VINH VIEN.

    Loi THAT: token Meta chet thi ca ba moc gio deu that bai, va moi moc Nguoi
    truc thu lai 3 lan - moi lan report.py lai gui mot tin canh bao. Ket qua la
    9 tin canh bao GIONG HET NHAU moi ngay, trong khi viec can lam chi co MOT.
    """

    class KetQuaGia:
        def __init__(self, returncode=0):
            self.returncode = returncode
            self.stdout = ""
            self.stderr = ""

    def _chay(self, returncode):
        goc = nguoi_truc.subprocess.run
        nguoi_truc.subprocess.run = lambda lenh, **kw: self.KetQuaGia(returncode)
        try:
            return nguoi_truc.gui_bao_cao(8)
        finally:
            nguoi_truc.subprocess.run = goc

    def test_ma_0_la_thanh_cong(self):
        self.assertEqual(self._chay(0), nguoi_truc.report.MA_THOAT_OK)

    def test_ma_2_la_loi_vinh_vien(self):
        self.assertEqual(self._chay(2), nguoi_truc.report.MA_THOAT_VINH_VIEN)

    def test_ma_1_la_loi_tam_thoi(self):
        self.assertEqual(self._chay(1), nguoi_truc.report.MA_THOAT_TAM_THOI)

    def test_ma_la_khac_1_va_2_van_la_tam_thoi(self):
        """Chi dung ma 2 moi la vinh vien.

        Rat nhieu duong khac trong report.py thoat voi ma 1 ma KHONG phai loi
        Meta (khong doc duoc .env, khong gui duoc Telegram). Coi chung la vinh
        vien thi bao cao se im lang khong bao gio gui lai.
        """
        for ma in (1, 3, 7, 99, 130):
            with self.subTest(ma=ma):
                self.assertEqual(self._chay(ma), nguoi_truc.report.MA_THOAT_TAM_THOI)

    def test_loi_vinh_vien_thi_KHONG_thu_lai(self):
        tg = TrucGia(luc(12, 0, 5), ket_qua_gui=nguoi_truc.report.MA_THOAT_VINH_VIEN)
        tg.truc.canh_moc(luc(12, 0, 5))
        self.assertEqual(tg.gui_roi, [12])
        # Qua khoang nghi: van KHONG thu lai
        sau = luc(12, 0, 5) + timedelta(seconds=nguoi_truc.KHOANG_NGHI_GIUA_HAI_LAN_THU)
        tg.truc.canh_moc(sau)
        self.assertEqual(tg.gui_roi, [12])
        self.assertIn(12, tg.truc.moc_hong_vinh_vien)

    def test_loi_tam_thoi_thi_VAN_thu_lai(self):
        tg = TrucGia(luc(12, 0, 5), ket_qua_gui=nguoi_truc.report.MA_THOAT_TAM_THOI)
        tg.truc.canh_moc(luc(12, 0, 5))
        sau = luc(12, 0, 5) + timedelta(seconds=nguoi_truc.KHOANG_NGHI_GIUA_HAI_LAN_THU)
        tg.truc.canh_moc(sau)
        self.assertEqual(tg.gui_roi, [12, 12])
        self.assertNotIn(12, tg.truc.moc_hong_vinh_vien)

    def test_moc_hong_vinh_vien_khong_chan_moc_sau(self):
        """Token chet luc 8h, Dai sua xong thi moc 12h phai gui binh thuong."""
        tg = TrucGia(luc(8, 0, 5), ket_qua_gui=nguoi_truc.report.MA_THOAT_VINH_VIEN)
        tg.truc.canh_moc(luc(8, 0, 5))
        tg._ket_qua_gui = True
        tg.truc.canh_moc(luc(12, 0, 5))
        self.assertEqual(tg.gui_roi, [8, 12])


class TestLenhToken(unittest.TestCase):
    """Lenh nhanh `token`: Dai tu kiem duoc han token, KHONG ton luot AI.

    Day la thay the cho tinh nang "tu gia han token" - da chung minh ngay
    29/09/2026 la Meta KHONG cho.
    """

    def _doc_gia(self, so_ngay, het_han=None, loi=None):
        return lambda env: (so_ngay, het_han, loi)

    def test_con_nhieu_ngay_thi_bao_chua_can_lam_gi(self):
        chu = nguoi_truc.tra_loi_han_token(
            {"REPORT_ACCOUNT_NAME": "May A"}, doc_han_fn=self._doc_gia(45))
        self.assertIn("45 ngày", chu)
        self.assertIn("chưa cần làm gì", chu)

    def test_duoi_7_ngay_thi_bao_lay_token_moi_ngay(self):
        chu = nguoi_truc.tra_loi_han_token(
            {"REPORT_ACCOUNT_NAME": "May A"}, doc_han_fn=self._doc_gia(5))
        self.assertIn("LẤY TOKEN MỚI NGAY", chu)

    def test_tu_7_den_30_ngay_thi_nhac_nhe(self):
        chu = nguoi_truc.tra_loi_han_token(
            {"REPORT_ACCOUNT_NAME": "May A"}, doc_han_fn=self._doc_gia(20))
        self.assertIn("chưa gấp", chu)
        self.assertNotIn("LẤY TOKEN MỚI NGAY", chu)

    def test_hien_moc_het_han_cu_the(self):
        het_han = datetime(2026, 11, 13, 8, 15)
        chu = nguoi_truc.tra_loi_han_token(
            {"REPORT_ACCOUNT_NAME": "May A"},
            doc_han_fn=self._doc_gia(20, het_han))
        self.assertIn("", chu)
        self.assertIn("08:15", chu)

    def test_token_da_het_han(self):
        chu = nguoi_truc.tra_loi_han_token(
            {"REPORT_ACCOUNT_NAME": "May A"}, doc_han_fn=self._doc_gia(0.0))
        self.assertIn("ĐÃ HẾT HẠN", chu)

    def test_token_khong_bao_gio_het_han(self):
        chu = nguoi_truc.tra_loi_han_token(
            {"REPORT_ACCOUNT_NAME": "May A"}, doc_han_fn=self._doc_gia(None))
        self.assertIn("không bao giờ hết hạn", chu)

    def test_doc_han_loi_thi_noi_ro_ly_do(self):
        chu = nguoi_truc.tra_loi_han_token(
            {"REPORT_ACCOUNT_NAME": "May A"},
            doc_han_fn=self._doc_gia(None, None, "HTTP 400"))
        self.assertIn("HTTP 400", chu)

    def test_doc_han_nem_loi_cung_khong_lam_chet(self):
        def no_loi(env):
            raise RuntimeError("mang hong")
        chu = nguoi_truc.tra_loi_han_token({}, doc_han_fn=no_loi)
        self.assertIn("mang hong", chu)

    def test_moi_cau_tra_loi_deu_noi_ro_KHONG_tu_gia_han_duoc(self):
        for so_ngay in (45, 20, 5, 0.0):
            with self.subTest(so_ngay=so_ngay):
                chu = nguoi_truc.tra_loi_han_token(
                    {}, doc_han_fn=self._doc_gia(so_ngay))
                self.assertIn("KHÔNG tự gia hạn được", chu)

    def test_nhan_chu_token_thi_tra_loi_han_token(self):
        chu = nguoi_truc.tra_loi_tin_nhan(
            cau_hoi="token",
            env={"REPORT_ACCOUNT_NAME": "May A"},
            danh_sach_moc=[8, 12, 17],
            bat_dau=luc(8), lan_gui_cuoi=None, da_gui=set(),
            now=luc(13),
            doc_han_fn=self._doc_gia(20),
        )
        self.assertIn("TOKEN META", chu)
        self.assertIn("20 ngày", chu)

    def test_nhan_chu_token_KHONG_goi_AI(self):
        """Cau hoi ve token khong duoc ton luot AI."""
        da_goi_ai = []

        def ai_gia(c):
            da_goi_ai.append(c)
            return "cau tra loi cua AI", None

        nguoi_truc.tra_loi_tin_nhan(
            cau_hoi="token còn bao lâu?",
            env={}, danh_sach_moc=[8, 12, 17],
            bat_dau=luc(8), lan_gui_cuoi=None, da_gui=set(),
            now=luc(13), tra_loi_ai_fn=ai_gia,
            doc_han_fn=self._doc_gia(20),
        )
        self.assertEqual(da_goi_ai, [])

    def test_cau_hoi_so_lieu_van_di_duong_AI(self):
        """Nhanh token KHONG duoc chan cau hoi so lieu binh thuong."""
        chu = nguoi_truc.tra_loi_tin_nhan(
            cau_hoi="camp nào tệ nhất tuần này?",
            env={}, danh_sach_moc=[8, 12, 17],
            bat_dau=luc(8), lan_gui_cuoi=None, da_gui=set(),
            now=luc(13),
            tra_loi_ai_fn=lambda c: ("Chi tieu 7.034.942 dong.", None),
            doc_han_fn=self._doc_gia(20),
        )
        self.assertEqual(chu, "Chi tieu 7.034.942 dong.")

    def test_cau_hoi_con_song_van_uu_tien_truoc(self):
        """'còn sống không?' phai di duong suc khoe, khong bi nhanh token bat."""
        chu = nguoi_truc.tra_loi_tin_nhan(
            cau_hoi="còn sống không?",
            env={"REPORT_ACCOUNT_NAME": "May A"},
            danh_sach_moc=[8, 12, 17],
            bat_dau=luc(8), lan_gui_cuoi=None, da_gui=set(),
            now=luc(13),
            doc_han_fn=self._doc_gia(20),
        )
        self.assertIn("Người trực đang chạy", chu)


class TestChuyenTiepTinTonDong(unittest.TestCase):
    """LOI THAT ngay 30/09/2026: nguoi truc bi tat luc 15:21, Dai bam nut trong
    luc no khong chay, den khi bat lai thi lan bam da bi XOA SACH — mat lenh im
    lang va Dai tuong agent hong. Nay phai CHUYEN TIEP truoc khi bo."""

    def setUp(self):
        import os
        import tempfile
        from pathlib import Path

        import agent_ky_uc
        self.agent_ky_uc = agent_ky_uc
        self.os = os
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)
        self.cu = agent_ky_uc.LENH_PATH
        agent_ky_uc.LENH_PATH = Path(self.tmp.name)

    def tearDown(self):
        self.agent_ky_uc.LENH_PATH = self.cu
        if self.os.path.exists(self.tmp.name):
            self.os.unlink(self.tmp.name)

    def _chay(self, tin_cho_san):
        tg = TrucGia(luc(13), tin_cho_san=tin_cho_san)
        tg.truc.mot_vong()
        return tg

    def test_lan_bam_nut_ton_dong_duoc_chuyen_tiep(self):
        self._chay([{"update_id": 1, "callback_query": {
            "id": "cb1", "data": "tat:120250506886650509",
            "message": {"message_id": 99, "chat": {"id": 123}}}}])
        hang = self.agent_ky_uc.doc_lenh()
        self.assertEqual(len(hang), 1, "lan bam nut bi mat")
        self.assertEqual(hang[0]["noi_dung"], "tat:120250506886650509")
        self.assertEqual(hang[0]["tin_nhan_id"], 99)

    def test_lenh_go_tay_ton_dong_duoc_chuyen_tiep(self):
        self._chay([{"update_id": 1, "message": {
            "chat": {"id": 123}, "text": "tắt 120250506886650509"}}])
        self.assertEqual(len(self.agent_ky_uc.doc_lenh()), 1)

    def test_cau_hoi_cu_thi_KHONG_chuyen_tiep(self):
        self._chay([{"update_id": 1, "message": {
            "chat": {"id": 123}, "text": "doanh thu hôm nay thế nào"}}])
        self.assertEqual(self.agent_ky_uc.doc_lenh(), [])

    def test_tin_tu_nguoi_la_khong_chuyen_tiep(self):
        self._chay([{"update_id": 1, "message": {
            "chat": {"id": 999}, "text": "tắt 120250506886650509"}}])
        self.assertEqual(self.agent_ky_uc.doc_lenh(), [])

    def test_nut_bam_tu_nguoi_la_khong_chuyen_tiep(self):
        self._chay([{"update_id": 1, "callback_query": {
            "id": "cb1", "data": "tat:120250506886650509",
            "message": {"message_id": 99, "chat": {"id": 999}}}}])
        self.assertEqual(self.agent_ky_uc.doc_lenh(), [])

    def test_van_danh_dau_da_doc_ton_dong(self):
        tg = self._chay([])
        self.assertTrue(tg.truc.da_xa_tin_ton_dong)

    def test_tin_hong_khong_lam_sap(self):
        self._chay([None, "chuoi", {}, {"update_id": 2},
                    {"update_id": 3, "callback_query": None}])
        self.assertEqual(self.agent_ky_uc.doc_lenh(), [])


if __name__ == "__main__":
    unittest.main()
