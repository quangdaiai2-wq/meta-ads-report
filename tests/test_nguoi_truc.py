"""Kiem thu nguoi_truc - tien trinh thuong tru cua bao cao Meta Ads."""
import unittest
from datetime import datetime, timedelta

import nguoi_truc

TrangThaiThu = nguoi_truc.TrangThaiThu


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
                 tin_cho_san=None):
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
        )

    def _gui(self, moc):
        self.gui_roi.append(moc)
        return self._ket_qua_gui

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


if __name__ == "__main__":
    unittest.main()
