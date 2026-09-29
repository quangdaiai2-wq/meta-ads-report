"""Kiem thu module lich_su - kho luu lich su so lieu bao cao."""
import json
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

import lich_su


def stats_mau(spend=1000.0, purchase=10, ten_camp="Camp A"):
    """Tao mot dict stats gia, giong cau truc compute_stats() tra ve."""
    return {
        "total_campaigns": 1,
        "totals": {
            "spend": spend, "msg": 5, "contact": 4, "order": 3,
            "purchase": purchase, "payment": 2, "comment": 1,
        },
        "all": [
            {
                "id": "1", "name": ten_camp, "spend": spend,
                "purchase": purchase, "payment": 2, "msg": 5,
                "cpr": (spend / purchase) if purchase else None,
            }
        ],
    }


class TestDocVaGhi(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "lich-su.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_file_chua_co_thi_doc_tra_ve_rong(self):
        self.assertEqual(lich_su.doc(self.path), {})

    def test_ghi_roi_doc_lai_duoc(self):
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau())
        ban_ghi = lich_su.lay_mot_ngay(self.path, "2026-09-27")
        self.assertIsNotNone(ban_ghi)
        self.assertEqual(ban_ghi["moc"], 8)
        self.assertTrue(ban_ghi["day_du"])
        self.assertEqual(ban_ghi["tong"]["spend"], 1000.0)
        self.assertEqual(ban_ghi["so_camp"], 1)
        self.assertEqual(len(ban_ghi["camp"]), 1)
        self.assertEqual(ban_ghi["camp"][0]["name"], "Camp A")

    def test_moc_12h_khong_phai_ban_day_du(self):
        lich_su.ghi(self.path, "2026-09-28", 12, stats_mau())
        self.assertFalse(lich_su.lay_mot_ngay(self.path, "2026-09-28")["day_du"])

    def test_moc_22h_la_ban_day_du(self):
        lich_su.ghi(self.path, "2026-09-28", 22, stats_mau())
        self.assertTrue(lich_su.lay_mot_ngay(self.path, "2026-09-28")["day_du"])

    def test_ban_day_du_ghi_de_ban_so_khong_day_du(self):
        lich_su.ghi(self.path, "2026-09-28", 17, stats_mau(spend=500.0))
        lich_su.ghi(self.path, "2026-09-28", 8, stats_mau(spend=900.0))
        self.assertEqual(
            lich_su.lay_mot_ngay(self.path, "2026-09-28")["tong"]["spend"], 900.0
        )

    def test_ban_so_khong_day_du_KHONG_ghi_de_ban_day_du(self):
        lich_su.ghi(self.path, "2026-09-28", 8, stats_mau(spend=900.0))
        ket_qua = lich_su.ghi(self.path, "2026-09-28", 17, stats_mau(spend=500.0))
        self.assertFalse(ket_qua)
        self.assertEqual(
            lich_su.lay_mot_ngay(self.path, "2026-09-28")["tong"]["spend"], 900.0
        )

    def test_ban_day_du_ghi_de_ban_day_du_khac_cung_ngay(self):
        # Cac giai doan sau dua vao quy tac nay: moc 8h ghi ban ca ngay cho
        # hom truoc, roi moc 22h ghi ban ca ngay moi hon cho cung khoa ngay.
        lich_su.ghi(self.path, "2026-09-28", 8, stats_mau(spend=900.0))
        lich_su.ghi(self.path, "2026-09-28", 22, stats_mau(spend=950.0))
        ban_ghi = lich_su.lay_mot_ngay(self.path, "2026-09-28")
        self.assertTrue(ban_ghi["day_du"])
        self.assertEqual(ban_ghi["moc"], 22)
        self.assertEqual(ban_ghi["tong"]["spend"], 950.0)

    def test_nhan_doi_tuong_date_chu_khong_chi_chuoi(self):
        lich_su.ghi(self.path, date(2026, 9, 27), 8, stats_mau())
        self.assertIsNotNone(lich_su.lay_mot_ngay(self.path, "2026-09-27"))

    def test_lay_mot_ngay_khong_co_tra_ve_None(self):
        self.assertIsNone(lich_su.lay_mot_ngay(self.path, "2020-01-01"))

    def test_file_hong_thi_doc_tra_ve_rong_khong_no(self):
        self.path.write_text("{ day khong phai json", encoding="utf-8")
        self.assertEqual(lich_su.doc(self.path), {})

    def test_gia_tri_khong_phai_dict_khong_lam_no_ghi(self):
        # File co mot gia tri hong (so thay vi dict) khong duoc lam ghi() no,
        # va khong duoc lam mat cac ban ghi tot khac.
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=100.0))
        du_lieu = json.loads(self.path.read_text(encoding="utf-8"))
        du_lieu["2026-09-28"] = 5
        self.path.write_text(json.dumps(du_lieu), encoding="utf-8")

        lich_su.ghi(self.path, "2026-09-29", 8, stats_mau(spend=300.0))

        self.assertEqual(
            lich_su.lay_mot_ngay(self.path, "2026-09-27")["tong"]["spend"], 100.0
        )
        self.assertIsNotNone(lich_su.lay_mot_ngay(self.path, "2026-09-29"))

    def test_ghi_tu_tao_thu_muc_neu_chua_co(self):
        sau = Path(self.tmp.name) / "logs" / "lich-su.json"
        lich_su.ghi(sau, "2026-09-27", 8, stats_mau())
        self.assertTrue(sau.exists())

    def test_don_dep_ban_ghi_cu_hon_180_ngay(self):
        hom_nay = date.today()
        cu = (hom_nay - timedelta(days=200)).strftime("%Y-%m-%d")
        moi = hom_nay.strftime("%Y-%m-%d")
        lich_su.ghi(self.path, cu, 8, stats_mau())
        lich_su.ghi(self.path, moi, 8, stats_mau())
        self.assertIsNone(lich_su.lay_mot_ngay(self.path, cu))


class TestLayKhoang(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "lich-su.json"

    def tearDown(self):
        self.tmp.cleanup()

    def test_cong_dung_cac_ngay_trong_khoang(self):
        lich_su.ghi(self.path, "2026-09-26", 8, stats_mau(spend=100.0, purchase=1))
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=200.0, purchase=2))
        lich_su.ghi(self.path, "2026-09-28", 8, stats_mau(spend=400.0, purchase=4))
        kq = lich_su.lay_khoang(self.path, "2026-09-26", "2026-09-27")
        self.assertEqual(kq["tong"]["spend"], 300.0)
        self.assertEqual(kq["tong"]["purchase"], 3)
        self.assertEqual(kq["so_ngay"], 2)

    def test_bao_gom_ca_hai_dau_mut(self):
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=200.0))
        kq = lich_su.lay_khoang(self.path, "2026-09-27", "2026-09-27")
        self.assertEqual(kq["tong"]["spend"], 200.0)
        self.assertEqual(kq["so_ngay"], 1)

    def test_bo_qua_ngay_chua_co_du_lieu(self):
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=200.0))
        kq = lich_su.lay_khoang(self.path, "2026-09-25", "2026-09-27")
        self.assertEqual(kq["tong"]["spend"], 200.0)
        self.assertEqual(kq["so_ngay"], 1)

    def test_khoang_rong_tra_ve_tong_0(self):
        kq = lich_su.lay_khoang(self.path, "2020-01-01", "2020-12-31")
        self.assertEqual(kq["so_ngay"], 0)
        self.assertEqual(kq["tong"]["spend"], 0.0)

    def test_lay_ky_truoc_lay_dung_so_ngay_ngay_truoc(self):
        lich_su.ghi(self.path, "2026-09-25", 8, stats_mau(spend=100.0))
        lich_su.ghi(self.path, "2026-09-26", 8, stats_mau(spend=200.0))
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=400.0))
        kq = lich_su.lay_ky_truoc(self.path, "2026-09-27", 2)
        self.assertEqual(kq["tong"]["spend"], 300.0)
        self.assertEqual(kq["so_ngay"], 2)

    def test_lay_ky_truoc_khong_bao_gom_chinh_ngay_do(self):
        lich_su.ghi(self.path, "2026-09-27", 8, stats_mau(spend=400.0))
        kq = lich_su.lay_ky_truoc(self.path, "2026-09-27", 1)
        self.assertEqual(kq["so_ngay"], 0)

    def test_lay_ky_truoc_ngay_sai_dinh_dang_tra_ve_tong_rong(self):
        kq = lich_su.lay_ky_truoc(self.path, "khong-phai-ngay", 7)
        self.assertEqual(kq["so_ngay"], 0)
        self.assertEqual(kq["tong"]["spend"], 0.0)


class TestCuaSoTruoc(unittest.TestCase):
    """Khoang ngay cua `so_ngay` ngay NGAY TRUOC mot ngay.

    Ham nay tach ra o Giai doan 5 vi bat_thuong.py cung can DUNG khoang do.
    Chep phep tinh ngay o hai noi thi som muon hai noi se lech nhau.
    """

    def test_bay_ngay_truoc(self):
        self.assertEqual(
            lich_su.cua_so_truoc("2026-09-29", 7), ("2026-09-22", "2026-09-28"))

    def test_khong_bao_gom_chinh_ngay_do(self):
        tu, den = lich_su.cua_so_truoc("2026-09-29", 1)
        self.assertEqual((tu, den), ("2026-09-28", "2026-09-28"))

    def test_vuot_qua_dau_thang(self):
        self.assertEqual(
            lich_su.cua_so_truoc("2026-10-03", 7), ("2026-09-26", "2026-10-02"))

    def test_vuot_qua_dau_nam(self):
        self.assertEqual(
            lich_su.cua_so_truoc("2027-01-02", 7), ("2026-12-26", "2027-01-01"))

    def test_ngay_sai_dinh_dang_tra_ve_None(self):
        self.assertEqual(lich_su.cua_so_truoc("khong-phai-ngay", 7), (None, None))

    def test_nhan_doi_tuong_date(self):
        from datetime import date
        self.assertEqual(
            lich_su.cua_so_truoc(date(2026, 9, 29), 7), ("2026-09-22", "2026-09-28"))

    def test_lay_ky_truoc_dung_cung_khoang_voi_cua_so_truoc(self):
        """Hai ham phai cho ra cung mot khoang - neu lech thi canh bao sai."""
        with tempfile.TemporaryDirectory() as tm:
            path = Path(tm) / "lich-su.json"
            lich_su.ghi(path, "2026-09-28", 8, stats_mau(spend=100.0))
            tu, den = lich_su.cua_so_truoc("2026-09-29", 7)
            kq1 = lich_su.lay_khoang(path, tu, den)
            kq2 = lich_su.lay_ky_truoc(path, "2026-09-29", 7)
            self.assertEqual(kq1["tong"]["spend"], kq2["tong"]["spend"])
            self.assertEqual(kq1["so_ngay"], kq2["so_ngay"])


if __name__ == "__main__":
    unittest.main()
