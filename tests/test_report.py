"""Kiem thu phan chon moc gio cua report.py."""
import unittest

import report


class TestChonMoc(unittest.TestCase):
    def test_co_slot_thi_tra_ve_dung_slot(self):
        self.assertEqual(report.chon_moc(22, 8, [8, 12, 17, 22]), 22)

    def test_co_slot_thi_bo_qua_gio_hien_tai(self):
        self.assertEqual(report.chon_moc(8, 23, [8, 12, 17]), 8)

    def test_khong_co_slot_thi_lay_moc_gan_nhat(self):
        self.assertEqual(report.chon_moc(None, 11, [8, 12, 17]), 12)

    def test_khong_co_slot_gio_23_lay_moc_gan_nhat(self):
        self.assertEqual(report.chon_moc(None, 23, [8, 12, 17]), 17)

    def test_khong_co_slot_dung_danh_sach_mac_dinh(self):
        self.assertEqual(report.chon_moc(None, 8), 8)

    def test_slot_khong_nam_trong_danh_sach_thi_bao_loi(self):
        with self.assertRaises(ValueError):
            report.chon_moc(22, 8, [8, 12, 17])

    def test_danh_sach_rong_thi_dung_mac_dinh(self):
        self.assertEqual(report.chon_moc(None, 8, []), 8)

    def test_moc_8h_va_22h_deu_chon_dung(self):
        for moc in (8, 12, 17, 22):
            with self.subTest(moc=moc):
                self.assertEqual(report.chon_moc(moc, 3, [8, 12, 17, 22]), moc)


if __name__ == "__main__":
    unittest.main()
