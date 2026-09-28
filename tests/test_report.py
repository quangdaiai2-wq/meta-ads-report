"""Kiem thu phan chon moc gio cua report.py."""
import tempfile
import unittest
from datetime import date
from pathlib import Path

import lich_su
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


def _hang_camp(cid, ten, spend, purchase):
    """Tao mot dong du lieu giong Meta tra ve."""
    actions = []
    if purchase:
        actions.append(
            {"action_type": "onsite_conversion.purchase", "value": str(purchase)}
        )
    return {
        "campaign_id": cid,
        "campaign_name": ten,
        "spend": str(spend),
        "actions": actions,
    }


class TestComputeStatsCoDanhSachDayDu(unittest.TestCase):
    def setUp(self):
        self.goc = report.fetch_insights
        # 6 camp "dainq" du dieu kien — nhieu hon TOP_CAMPAIGN_COUNT (5),
        # de bai test "all khong bi cat theo top-N" that su bat duoc loi.
        self.rows = [
            _hang_camp("1", "dainq A", 100, 5),
            _hang_camp("2", "dainq B", 50, 0),
            _hang_camp("3", "thuonghieu X", 999, 9),
            _hang_camp("4", "dainq C", 10, 1),
            _hang_camp("5", "dainq D", 20, 2),
            _hang_camp("6", "dainq E", 30, 3),
            _hang_camp("7", "dainq F", 40, 4),
        ]
        report.fetch_insights = lambda env, since, until: (self.rows, None)
        self.env = {
            "FILTER_INCLUDE": "dainq",
            "FILTER_EXCLUDE": "thuonghieu,thương hiệu,Brand",
            "TOP_CAMPAIGN_COUNT": "5",
            "REPORT_ACCOUNT_NAME": "Test",
        }

    def tearDown(self):
        report.fetch_insights = self.goc

    def test_co_khoa_all(self):
        stats, err = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        self.assertIsNone(err)
        self.assertIn("all", stats)

    def test_all_chua_moi_camp_du_dieu_kien_khong_chi_top(self):
        stats, _ = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        self.assertEqual(len(stats["all"]), 6)

    def test_all_loai_bo_camp_bi_loc(self):
        stats, _ = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        ten = [c["name"] for c in stats["all"]]
        self.assertNotIn("thuonghieu X", ten)

    def test_all_co_du_cac_truong_can_thiet(self):
        stats, _ = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        self.assertEqual(
            set(stats["all"][0].keys()),
            {"rank", "id", "name", "spend", "purchase", "payment", "msg", "cpr"},
        )

    def test_good_va_bad_van_nhu_cu(self):
        stats, _ = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        self.assertEqual(len(stats["good"]), 5)
        self.assertEqual(len(stats["bad"]), 5)


class TestLuuLichSu(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "lich-su.json"
        # Chan ghi vao logs/baocao.log THAT: bai test khong duoc lam ban nhat ky
        # san xuat (truoc day chay test la thay dong "Khong luu duoc lich su").
        self._log_goc = report.log
        report.log = lambda *a, **k: None

    def tearDown(self):
        report.log = self._log_goc
        self.tmp.cleanup()

    def test_luu_duoc_so_lieu(self):
        stats = {
            "total_campaigns": 2,
            "totals": {"spend": 100.0, "msg": 1, "contact": 1,
                       "order": 1, "purchase": 2, "payment": 1, "comment": 0},
            "all": [],
        }
        report.luu_lich_su(stats, "2026-09-27", 8, path_lich_su=self.path)
        ban_ghi = lich_su.lay_mot_ngay(self.path, "2026-09-27")
        self.assertIsNotNone(ban_ghi)
        self.assertEqual(ban_ghi["tong"]["spend"], 100.0)

    def test_loi_ghi_lich_su_KHONG_lam_no_chuong_trinh(self):
        # Truyen vao mot THU MUC thay vi file -> viec ghi se loi.
        # Ham phai nuot loi, khong duoc nem ra ngoai.
        report.luu_lich_su({"totals": {}, "all": []}, "2026-09-27", 8,
                           path_lich_su=Path(self.tmp.name))

    def test_stats_thieu_khoa_cung_khong_no(self):
        report.luu_lich_su({}, "2026-09-27", 8, path_lich_su=self.path)
        self.assertIsNotNone(lich_su.lay_mot_ngay(self.path, "2026-09-27"))


if __name__ == "__main__":
    unittest.main()
