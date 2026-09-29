"""Kiem thu cong_cu.py - bon cong cu tra loi cau hoi. KHONG goi mang."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

import cong_cu


LICH_SU = {
    "2026-09-27": {
        "moc": 8, "day_du": True, "so_camp": 2,
        "tong": {"spend": 5000000, "msg": 60, "contact": 20, "order": 5,
                 "purchase": 20, "payment": 18, "comment": 1},
        "camp": [
            {"id": "A", "name": "dainq A", "spend": 3000000, "purchase": 18,
             "payment": 16, "msg": 40, "cpr": 166666},
            {"id": "B", "name": "dainq B", "spend": 2000000, "purchase": 2,
             "payment": 2, "msg": 20, "cpr": 1000000},
        ],
    },
    "2026-09-28": {
        "moc": 8, "day_du": True, "so_camp": 2,
        "tong": {"spend": 7000000, "msg": 90, "contact": 30, "order": 8,
                 "purchase": 15, "payment": 12, "comment": 3},
        "camp": [
            {"id": "A", "name": "dainq A", "spend": 4000000, "purchase": 12,
             "payment": 10, "msg": 50, "cpr": 333333},
            {"id": "B", "name": "dainq B", "spend": 3000000, "purchase": 3,
             "payment": 2, "msg": 40, "cpr": 1000000},
            {"id": "C", "name": "dainq C", "spend": 500000, "purchase": 0,
             "payment": 0, "msg": 10, "cpr": None},
        ],
    },
}


class CoThuMucTam(unittest.TestCase):
    """Lop cha: tao file lich su tam cho tung bai kiem thu."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "lich-su.json"
        self.path.write_text(json.dumps(LICH_SU, ensure_ascii=False),
                             encoding="utf-8")

    def bo(self, **kw):
        return cong_cu.BoCongCu(duong_dan=self.path, hom_nay=date(2026, 9, 29), **kw)


class TestMocThoiGian(CoThuMucTam):
    def test_ghi_ro_hom_nay_va_thu(self):
        t = cong_cu.moc_thoi_gian(self.path, hom_nay=date(2026, 9, 29))
        self.assertIn("29/09/2026", t)
        self.assertIn("Thứ Ba", t)

    def test_chi_ro_ngay_cuoi_co_so(self):
        t = cong_cu.moc_thoi_gian(self.path, hom_nay=date(2026, 9, 29))
        self.assertIn("28/09/2026", t)

    def test_khoang_7_ngay_gan_nhat(self):
        t = cong_cu.moc_thoi_gian(self.path, hom_nay=date(2026, 9, 29))
        self.assertIn("27/09/2026", t)
        self.assertIn("28/09/2026", t)

    def test_chua_du_7_ngay_thi_noi_ro_chua_so_sanh_duoc(self):
        t = cong_cu.moc_thoi_gian(self.path, hom_nay=date(2026, 9, 29))
        self.assertIn("CHƯA CÓ số liệu, không so sánh được", t)

    def test_lich_su_rong_thi_noi_that(self):
        p = Path(self.tmp.name) / "rong.json"
        p.write_text("{}", encoding="utf-8")
        t = cong_cu.moc_thoi_gian(p, hom_nay=date(2026, 9, 29))
        self.assertIn("CHƯA CÓ ngày nào", t)

    def test_file_hong_khong_nem_loi(self):
        p = Path(self.tmp.name) / "hong.json"
        p.write_text("day khong phai json", encoding="utf-8")
        t = cong_cu.moc_thoi_gian(p, hom_nay=date(2026, 9, 29))
        self.assertIn("CHƯA CÓ ngày nào", t)

    def test_khong_bao_gio_nem_loi_khi_thieu_file(self):
        t = cong_cu.moc_thoi_gian(Path(self.tmp.name) / "khong-ton-tai.json")
        self.assertIsInstance(t, str)


class TestKhaiBao(CoThuMucTam):
    def test_co_du_bon_cong_cu(self):
        ds = self.bo().khai_bao()[0]["functionDeclarations"]
        ten = {c["name"] for c in ds}
        self.assertEqual(ten, {"lay_mot_ngay", "lay_khoang", "xep_hang_camp",
                               "so_sanh"})

    def test_moi_cong_cu_co_description_va_parameters(self):
        for c in self.bo().khai_bao()[0]["functionDeclarations"]:
            self.assertTrue(c.get("description"), c["name"])
            self.assertIn("properties", c.get("parameters", {}), c["name"])

    def test_ten_cong_cu_khop_voi_thuc_thi(self):
        """Ten trong khai bao PHAI chay duoc qua thuc_thi.

        Neu lech nhau thi AI goi dung ten ma he thong khong chay duoc -> cau tra
        loi se bao 'khong co cong cu nao ten ...'.
        """
        bo = self.bo()
        for c in bo.khai_bao()[0]["functionDeclarations"]:
            kq = bo.thuc_thi(c["name"], {})
            self.assertNotIn("Khong co cong cu nao ten", str(kq.get("loi", "")),
                             c["name"])


class TestLayMotNgay(CoThuMucTam):
    def test_lay_dung_so_mot_ngay(self):
        kq = self.bo().lay_mot_ngay("2026-09-28")
        self.assertEqual(kq["tong"]["spend"], 7000000)
        self.assertTrue(kq["day_du_ca_ngay"])

    def test_ngay_sai_dinh_dang_tra_loi(self):
        self.assertIn("loi", self.bo().lay_mot_ngay("28/09/2026"))

    def test_ngay_khong_co_trong_lich_su_tra_loi_kem_ngay_cuoi(self):
        kq = self.bo().lay_mot_ngay("2026-09-01")
        self.assertIn("loi", kq)
        self.assertIn("2026-09-28", kq["loi"])

    def test_hom_nay_chua_co_thi_goi_meta(self):
        dem = {"n": 0}

        def meta_gia(ngay):
            dem["n"] += 1
            return {"totals": {"spend": 123456, "purchase": 1},
                    "total_campaigns": 3}

        bo = self.bo(lay_so_hom_nay_fn=meta_gia)
        kq = bo.lay_mot_ngay("2026-09-29")
        self.assertEqual(kq["tong"]["spend"], 123456)
        self.assertFalse(kq["day_du_ca_ngay"])
        self.assertEqual(dem["n"], 1)

    def test_hom_nay_goi_meta_hai_lan_chi_chay_that_mot_lan(self):
        dem = {"n": 0}

        def meta_gia(ngay):
            dem["n"] += 1
            return {"totals": {"spend": 1}, "total_campaigns": 1}

        bo = self.bo(lay_so_hom_nay_fn=meta_gia)
        bo.lay_mot_ngay("2026-09-29")
        bo.lay_mot_ngay("2026-09-29")
        self.assertEqual(dem["n"], 1)

    def test_ngay_cu_thi_khong_goi_meta(self):
        dem = {"n": 0}

        def meta_gia(ngay):
            dem["n"] += 1
            return {"totals": {"spend": 1}, "total_campaigns": 1}

        bo = self.bo(lay_so_hom_nay_fn=meta_gia)
        bo.lay_mot_ngay("2026-09-01")
        self.assertEqual(dem["n"], 0)

    def test_meta_loi_thi_tra_loi_chu_khong_nem(self):
        def meta_hong(ngay):
            raise RuntimeError("mang dut")

        kq = self.bo(lay_so_hom_nay_fn=meta_hong).lay_mot_ngay("2026-09-29")
        self.assertIn("loi", kq)

    def test_meta_tra_ve_None_thi_tra_loi(self):
        kq = self.bo(lay_so_hom_nay_fn=lambda ngay: None).lay_mot_ngay("2026-09-29")
        self.assertIn("loi", kq)

    def test_khong_tiem_ham_meta_thi_khong_goi(self):
        kq = self.bo().lay_mot_ngay("2026-09-29")
        self.assertIn("loi", kq)


class TestLayKhoang(CoThuMucTam):
    def test_cong_don_dung_hai_ngay(self):
        kq = self.bo().lay_khoang("2026-09-27", "2026-09-28")
        self.assertEqual(kq["so_ngay"], 2)
        self.assertEqual(kq["tong"]["spend"], 12000000)

    def test_khoang_khong_co_du_lieu_tra_loi(self):
        kq = self.bo().lay_khoang("2026-08-01", "2026-08-05")
        self.assertIn("loi", kq)

    def test_ngay_sai_dinh_dang_tra_loi(self):
        self.assertIn("loi", self.bo().lay_khoang("hom qua", "2026-09-28"))

    def test_mot_ngay_van_tinh_la_mot_ngay(self):
        kq = self.bo().lay_khoang("2026-09-28", "2026-09-28")
        self.assertEqual(kq["so_ngay"], 1)
        self.assertEqual(kq["tong"]["spend"], 7000000)


class TestXepHangCamp(CoThuMucTam):
    def test_gop_camp_qua_hai_ngay(self):
        kq = self.bo().xep_hang_camp("2026-09-27", "2026-09-28", "spend")
        theo_ten = {c["name"]: c for c in kq["danh_sach"]}
        self.assertEqual(theo_ten["dainq A"]["spend"], 7000000)
        self.assertEqual(theo_ten["dainq A"]["purchase"], 30)

    def test_sap_theo_chi_tieu_giam_dan_mac_dinh(self):
        kq = self.bo().xep_hang_camp("2026-09-28", "2026-09-28", "spend")
        spends = [c["spend"] for c in kq["danh_sach"]]
        self.assertEqual(spends, sorted(spends, reverse=True))

    def test_tang_dan_true_thi_nho_nhat_len_dau(self):
        kq = self.bo().xep_hang_camp("2026-09-28", "2026-09-28", "spend",
                                     tang_dan=True)
        spends = [c["spend"] for c in kq["danh_sach"]]
        self.assertEqual(spends, sorted(spends))

    def test_camp_chua_co_don_bi_day_xuong_cuoi_khi_sap_theo_cpr(self):
        """Camp chua co don KHONG duoc coi la cpr = 0 (0 trong nhu re nhat)."""
        kq = self.bo().xep_hang_camp("2026-09-28", "2026-09-28", "cpr",
                                     tang_dan=True)
        cuoi = kq["danh_sach"][-1]
        self.assertEqual(cuoi["name"], "dainq C")
        self.assertIsNone(cuoi["cpr"])

    def test_chi_so_sai_tra_loi_kem_danh_sach_hop_le(self):
        kq = self.bo().xep_hang_camp("2026-09-28", "2026-09-28", "doanh_thu")
        self.assertIn("loi", kq)
        self.assertIn("cpr", kq["loi"])

    def test_khoang_rong_tra_loi(self):
        kq = self.bo().xep_hang_camp("2026-08-01", "2026-08-02", "spend")
        self.assertIn("loi", kq)

    def test_chi_phi_moi_don_bang_chi_tieu_chia_luot_mua(self):
        kq = self.bo().xep_hang_camp("2026-09-28", "2026-09-28", "spend")
        a = [c for c in kq["danh_sach"] if c["name"] == "dainq A"][0]
        self.assertEqual(a["cpr"], round(4000000 / 12))
        self.assertEqual(a["chi_phi_moi_don"], a["cpr"])

    def test_co_ghi_so_ngay_xuat_hien(self):
        kq = self.bo().xep_hang_camp("2026-09-27", "2026-09-28", "spend")
        a = [c for c in kq["danh_sach"] if c["name"] == "dainq A"][0]
        self.assertEqual(a["so_ngay_xuat_hien"], 2)


class TestSoSanh(CoThuMucTam):
    def test_tinh_dung_chenh_lech(self):
        kq = self.bo().so_sanh("2026-09-28", "2026-09-28",
                               "2026-09-27", "2026-09-27")
        chi_tieu = [d for d in kq["bang"] if d["ten"] == "chi tieu"][0]
        self.assertEqual(chi_tieu["ky_nay"], 7000000)
        self.assertEqual(chi_tieu["ky_truoc"], 5000000)
        self.assertEqual(chi_tieu["chenh_lech"], 2000000)
        self.assertEqual(chi_tieu["phan_tram"], 40)

    def test_ky_truoc_rong_thi_ky_truoc_la_None(self):
        kq = self.bo().so_sanh("2026-09-28", "2026-09-28",
                               "2026-08-01", "2026-08-05")
        self.assertIsNone(kq["ky_truoc"])
        self.assertEqual(kq["so_ngay_ky_truoc"], 0)
        for d in kq["bang"]:
            self.assertIsNone(d["ky_truoc"])
            self.assertIsNone(d["chenh_lech"])

    def test_ky_nay_rong_thi_tra_loi(self):
        kq = self.bo().so_sanh("2026-08-01", "2026-08-05",
                               "2026-09-27", "2026-09-28")
        self.assertIn("loi", kq)

    def test_chia_cho_khong_khi_ky_truoc_bang_0(self):
        """Ky truoc co so nhung chi so bang 0 -> phan_tram phai la None."""
        p = Path(self.tmp.name) / "co-khong.json"
        p.write_text(json.dumps({
            "2026-09-27": {"moc": 8, "day_du": True,
                           "tong": {"spend": 0, "msg": 0, "contact": 0, "order": 0,
                                    "purchase": 0, "payment": 0, "comment": 0},
                           "camp": []},
            "2026-09-28": {"moc": 8, "day_du": True,
                           "tong": {"spend": 100, "msg": 0, "contact": 0, "order": 0,
                                    "purchase": 0, "payment": 0, "comment": 0},
                           "camp": []},
        }, ensure_ascii=False), encoding="utf-8")
        bo = cong_cu.BoCongCu(duong_dan=p, hom_nay=date(2026, 9, 29))
        kq = bo.so_sanh("2026-09-28", "2026-09-28", "2026-09-27", "2026-09-27")
        chi_tieu = [d for d in kq["bang"] if d["ten"] == "chi tieu"][0]
        self.assertIsNone(chi_tieu["phan_tram"])

    def test_ngay_sai_dinh_dang_tra_loi(self):
        kq = self.bo().so_sanh("28/09/2026", "2026-09-28",
                               "2026-09-27", "2026-09-27")
        self.assertIn("loi", kq)


class TestAnToan(CoThuMucTam):
    def test_cong_cu_la_tra_loi_chu_khong_nem(self):
        bo = self.bo()
        kq = bo.thuc_thi("khong_co_cong_cu_nay", {})
        self.assertIn("loi", kq)

    def test_tham_so_rong_khong_lam_chet(self):
        bo = self.bo()
        for ten in ("lay_mot_ngay", "lay_khoang", "xep_hang_camp", "so_sanh"):
            kq = bo.thuc_thi(ten, {})
            self.assertIsInstance(kq, dict, ten)

    def test_tham_so_None_khong_lam_chet(self):
        bo = self.bo()
        for ten in ("lay_mot_ngay", "lay_khoang", "xep_hang_camp", "so_sanh"):
            self.assertIsInstance(bo.thuc_thi(ten, None), dict, ten)

    def test_file_lich_su_khong_ton_tai_khong_lam_chet(self):
        bo = cong_cu.BoCongCu(duong_dan=Path(self.tmp.name) / "khong-co.json")
        self.assertIn("loi", bo.lay_mot_ngay("2026-09-28"))
        self.assertIn("loi", bo.lay_khoang("2026-09-27", "2026-09-28"))
        self.assertIn("loi", bo.xep_hang_camp("2026-09-27", "2026-09-28", "spend"))

    def test_file_lich_su_hong_khong_lam_chet(self):
        p = Path(self.tmp.name) / "hong.json"
        p.write_text("{{{ hong", encoding="utf-8")
        bo = cong_cu.BoCongCu(duong_dan=p)
        self.assertIn("loi", bo.lay_khoang("2026-09-27", "2026-09-28"))


class TestDinhDangTien(CoThuMucTam):
    """So tien phai duoc CODE dinh dang san, khong de AI tu them dau phan cach.

    Loi that gap ngay 29/09/2026: AI chep so tho tu JSON nen viet ra
    '20319895 dong', doc rat met (bao cao cua Dai van ghi '20.319.895').
    """

    def test_tien_dinh_dang_kieu_viet_nam(self):
        self.assertEqual(cong_cu._tien(20319895), "20.319.895")
        self.assertEqual(cong_cu._tien(0), "0")
        self.assertEqual(cong_cu._tien(1234567.4), "1.234.567")

    def test_lay_mot_ngay_co_truong_hien_thi(self):
        kq = self.bo().lay_mot_ngay("2026-09-28")
        self.assertEqual(kq["tong_hien_thi"]["chi tieu"], "7.000.000")
        self.assertEqual(kq["tong_hien_thi"]["luot mua"], "15")

    def test_lay_khoang_co_truong_hien_thi(self):
        kq = self.bo().lay_khoang("2026-09-27", "2026-09-28")
        self.assertEqual(kq["tong_hien_thi"]["chi tieu"], "12.000.000")

    def test_xep_hang_camp_co_truong_hien_thi(self):
        kq = self.bo().xep_hang_camp("2026-09-28", "2026-09-28", "spend")
        a = [c for c in kq["danh_sach"] if c["name"] == "dainq A"][0]
        self.assertEqual(a["chi_tieu_hien_thi"], "4.000.000")
        self.assertEqual(a["chi_phi_moi_don_hien_thi"], "333.333 d")

    def test_camp_chua_co_don_hien_thi_ro_chu(self):
        kq = self.bo().xep_hang_camp("2026-09-28", "2026-09-28", "cpr",
                                     tang_dan=True)
        c = [x for x in kq["danh_sach"] if x["name"] == "dainq C"][0]
        self.assertEqual(c["chi_phi_moi_don_hien_thi"], "chua co don")

    def test_so_sanh_co_truong_hien_thi(self):
        kq = self.bo().so_sanh("2026-09-28", "2026-09-28",
                               "2026-09-27", "2026-09-27")
        d = [x for x in kq["bang"] if x["ten"] == "chi tieu"][0]
        self.assertEqual(d["ky_nay_hien_thi"], "7.000.000")
        self.assertEqual(d["ky_truoc_hien_thi"], "5.000.000")
        self.assertEqual(d["chenh_lech_hien_thi"], "+2.000.000")

    def test_chenh_lech_am_co_dau_tru(self):
        kq = self.bo().so_sanh("2026-09-27", "2026-09-27",
                               "2026-09-28", "2026-09-28")
        d = [x for x in kq["bang"] if x["ten"] == "chi tieu"][0]
        self.assertEqual(d["chenh_lech_hien_thi"], "-2.000.000")

    def test_ky_truoc_rong_thi_truong_hien_thi_la_None(self):
        kq = self.bo().so_sanh("2026-09-28", "2026-09-28",
                               "2026-08-01", "2026-08-05")
        for d in kq["bang"]:
            self.assertIsNone(d["ky_truoc_hien_thi"])
            self.assertIsNone(d["chenh_lech_hien_thi"])


if __name__ == "__main__":
    unittest.main()
