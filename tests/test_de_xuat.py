"""Kiem thu rao kiem de xuat. KHONG goi mang, khong doc file.

Du lieu dung trong day lay tu logs/lich-su.json THAT ngay 29/09/2026:
  - id 120250350059260509, ten "2026 - 09 - 11 - dainq - Scale - Online MESS - LTT"
    chi 858.562d ngay 28/09, 0 don.
  - id 120249610332380509 chi 1.061.015d, 1 don.
Lay tu nguon that de bai kiem khong phai chay tren du lieu gia.
"""
import unittest

import de_xuat


STATS = {
    "all": [
        {"id": "120250350059260509",
         "name": "2026 - 09 - 11 - dainq - Scale - Online MESS - LTT",
         "spend": 858562.0, "purchase": 0, "payment": 0, "msg": 0, "cpr": None},
        {"id": "120249610332380509",
         "name": "2026 - 09 - 02 - dainq - Scale - Online MESS - LTT",
         "spend": 1061015.0, "purchase": 1, "payment": 1, "msg": 4,
         "cpr": 1061015.0},
        {"id": "120250574677130509",
         "name": "2026 - 09 - 28 - dainq - Scale - Offline MESS",
         "spend": 181052.0, "purchase": 0, "payment": 0, "msg": 0, "cpr": None},
        {"id": "120250611763460509",
         "name": "camp chi nho", "spend": 39532.0, "purchase": 0,
         "payment": 0, "msg": 0, "cpr": None},
    ]
}

ID_CHI_858K_0_DON = "120250350059260509"
ID_CO_1_DON = "120249610332380509"
ID_CHI_181K = "120250574677130509"
ID_CHI_39K = "120250611763460509"


class KiemDeXuatTest(unittest.TestCase):

    def test_id_dung_thi_nhan(self):
        hop_le, bi_loai = de_xuat.kiem(
            [{"id": ID_CHI_858K_0_DON, "viec": "tam_dung", "ly_do": "0 don"}],
            STATS,
        )
        self.assertEqual(len(hop_le), 1)
        self.assertEqual([], bi_loai)
        self.assertEqual(ID_CHI_858K_0_DON, hop_le[0]["id"])
        self.assertEqual(858562.0, hop_le[0]["spend"])
        self.assertEqual(0, hop_le[0]["purchase"])

    def test_AI_bia_so_thi_so_cua_code_thang(self):
        """AI tra ve ten va so BIA -> ket qua van la ten va so THAT cua code."""
        hop_le, _ = de_xuat.kiem(
            [{"id": ID_CHI_858K_0_DON, "viec": "tam_dung", "ly_do": "x",
              "ten": "TEN BIA DAT", "spend": 999999999, "purchase": 77}],
            STATS,
        )
        self.assertEqual(1, len(hop_le))
        self.assertEqual(
            "2026 - 09 - 11 - dainq - Scale - Online MESS - LTT", hop_le[0]["ten"])
        self.assertEqual(858562.0, hop_le[0]["spend"])
        self.assertEqual(0, hop_le[0]["purchase"])

    def test_id_la_thi_loai(self):
        hop_le, bi_loai = de_xuat.kiem(
            [{"id": "999999999999", "viec": "tam_dung", "ly_do": "x"}], STATS)
        self.assertEqual([], hop_le)
        self.assertEqual(1, len(bi_loai))
        self.assertIn("khong co trong du lieu", bi_loai[0][1])

    def test_camp_co_don_thi_loai(self):
        """Rao quan trong nhat: khong bao gio de xuat tat camp dang co don."""
        hop_le, bi_loai = de_xuat.kiem(
            [{"id": ID_CO_1_DON, "viec": "tam_dung", "ly_do": "x"}], STATS)
        self.assertEqual([], hop_le)
        self.assertEqual(1, len(bi_loai))
        self.assertIn("da co 1 don", bi_loai[0][1])

    def test_duoi_nguong_thi_loai(self):
        hop_le, bi_loai = de_xuat.kiem(
            [{"id": ID_CHI_39K, "viec": "tam_dung", "ly_do": "x"}], STATS)
        self.assertEqual([], hop_le)
        self.assertIn("nguong", bi_loai[0][1])

    def test_dung_bang_nguong_thi_nhan(self):
        """Nguong nghia la 'tu muc nay tro len', nen bang dung phai duoc nhan."""
        stats = {"all": [{"id": "1", "name": "vua du", "spend": 200000.0,
                          "purchase": 0}]}
        hop_le, bi_loai = de_xuat.kiem(
            [{"id": "1", "viec": "tam_dung", "ly_do": "x"}], stats)
        self.assertEqual(1, len(hop_le))
        self.assertEqual([], bi_loai)

    def test_viec_khac_tam_dung_thi_loai(self):
        hop_le, bi_loai = de_xuat.kiem(
            [{"id": ID_CHI_858K_0_DON, "viec": "tang_ngan_sach", "ly_do": "x"}],
            STATS)
        self.assertEqual([], hop_le)
        self.assertIn("viec khong duoc phep", bi_loai[0][1])

    def test_trung_id_thi_loai(self):
        hop_le, bi_loai = de_xuat.kiem(
            [{"id": ID_CHI_858K_0_DON, "viec": "tam_dung", "ly_do": "a"},
             {"id": ID_CHI_858K_0_DON, "viec": "tam_dung", "ly_do": "b"}],
            STATS)
        self.assertEqual(1, len(hop_le))
        self.assertEqual(1, len(bi_loai))
        self.assertEqual("trung id", bi_loai[0][1])

    def test_vuot_toi_da_thi_cat(self):
        stats = {"all": [
            {"id": str(i), "name": f"camp {i}", "spend": 500000.0, "purchase": 0}
            for i in range(5)
        ]}
        ds = [{"id": str(i), "viec": "tam_dung", "ly_do": "x"} for i in range(5)]
        hop_le, bi_loai = de_xuat.kiem(ds, stats)
        self.assertEqual(3, len(hop_le))
        self.assertEqual(2, len(bi_loai))
        self.assertIn("toi da", bi_loai[0][1])

    def test_vuot_toi_da_khong_che_lap_ly_do_that(self):
        """De xuat thu 4 khong hop le phai bao dung ly do THAT, khong phai 'vuot toi da'."""
        stats = {"all": [
            {"id": str(i), "name": f"camp {i}", "spend": 500000.0, "purchase": 0}
            for i in range(3)
        ]}
        ds = ([{"id": str(i), "viec": "tam_dung", "ly_do": "x"} for i in range(3)]
              + [{"id": "khong-ton-tai", "viec": "tam_dung", "ly_do": "x"}])
        hop_le, bi_loai = de_xuat.kiem(ds, stats)
        self.assertEqual(3, len(hop_le))
        self.assertIn("khong co trong du lieu", bi_loai[0][1])

    def test_danh_sach_rong(self):
        hop_le, bi_loai = de_xuat.kiem([], STATS)
        self.assertEqual([], hop_le)
        self.assertEqual([], bi_loai)

    def test_dau_vao_rac_khong_nem_loi(self):
        for rac in (None, "chuoi", 123, [1, 2, 3], [{}], [None], [{"id": 5}],
                    [{"id": "  "}], [{"id": ID_CHI_858K_0_DON}]):
            with self.subTest(rac=rac):
                hop_le, bi_loai = de_xuat.kiem(rac, STATS)
                self.assertIsInstance(hop_le, list)
                self.assertIsInstance(bi_loai, list)

    def test_stats_rong_khong_nem_loi(self):
        hop_le, bi_loai = de_xuat.kiem(
            [{"id": ID_CHI_858K_0_DON, "viec": "tam_dung", "ly_do": "x"}], {})
        self.assertEqual([], hop_le)
        self.assertEqual(1, len(bi_loai))

    def test_cau_hinh_sai_dinh_dang_dung_mac_dinh(self):
        nguong, toi_da = de_xuat.doc_cau_hinh(
            {"DE_XUAT_NGUONG_CHI": "abc", "DE_XUAT_TOI_DA": ""})
        self.assertEqual(de_xuat.NGUONG_CHI_MAC_DINH, nguong)
        self.assertEqual(de_xuat.TOI_DA_MAC_DINH, toi_da)

    def test_cau_hinh_doc_dung_khi_hop_le(self):
        nguong, toi_da = de_xuat.doc_cau_hinh(
            {"DE_XUAT_NGUONG_CHI": "500000", "DE_XUAT_TOI_DA": "5"})
        self.assertEqual(500000, nguong)
        self.assertEqual(5, toi_da)

    def test_cau_hinh_am_thi_ve_0(self):
        nguong, toi_da = de_xuat.doc_cau_hinh(
            {"DE_XUAT_NGUONG_CHI": "-5", "DE_XUAT_TOI_DA": "-1"})
        self.assertEqual(0, nguong)
        self.assertEqual(0, toi_da)

    def test_toi_da_bang_0_thi_khong_nhan_gi(self):
        hop_le, bi_loai = de_xuat.kiem(
            [{"id": ID_CHI_858K_0_DON, "viec": "tam_dung", "ly_do": "x"}],
            STATS, env={"DE_XUAT_TOI_DA": "0"})
        self.assertEqual([], hop_le)
        self.assertEqual(1, len(bi_loai))

    def test_nguong_0_thi_moi_camp_0_don_deu_duoc(self):
        hop_le, _ = de_xuat.kiem(
            [{"id": ID_CHI_39K, "viec": "tam_dung", "ly_do": "x"}],
            STATS, env={"DE_XUAT_NGUONG_CHI": "0"})
        self.assertEqual(1, len(hop_le))
        self.assertEqual(39532.0, hop_le[0]["spend"])

    def test_ly_do_rong_van_nhan(self):
        """Thieu ly do khong phai loi chan - chi la cau van trong."""
        hop_le, _ = de_xuat.kiem(
            [{"id": ID_CHI_858K_0_DON, "viec": "tam_dung"}], STATS)
        self.assertEqual(1, len(hop_le))
        self.assertEqual("", hop_le[0]["ly_do"])

    def test_mac_dinh_200k_cho_ra_2_de_xuat_tren_du_lieu_that(self):
        """Do THAT tren 4 camp cua STATS: chi 858k va 181k duoi nguong... """
        ds = [{"id": c["id"], "viec": "tam_dung", "ly_do": "x"} for c in STATS["all"]]
        hop_le, bi_loai = de_xuat.kiem(ds, STATS)
        # 858.562 >= 200.000 -> nhan; 1.061.015 co 1 don -> loai;
        # 181.052 < 200.000 -> loai; 39.532 < 200.000 -> loai
        self.assertEqual([ID_CHI_858K_0_DON], [d["id"] for d in hop_le])
        self.assertEqual(3, len(bi_loai))


if __name__ == "__main__":
    unittest.main()
