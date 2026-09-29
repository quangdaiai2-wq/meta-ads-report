"""Kiem thu phan chon moc gio cua report.py."""
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

import lich_su
import report


def setUpModule():
    """Kiem thu KHONG duoc ghi vao logs/baocao.log that.

    report.log() ghi thang vao file nhat ky san xuat. Chay kiem thu ma ghi
    vao do se lam ban file Dai mo dau tien khi co su co.
    """
    report.log = lambda message: None


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

    def test_bang_kem_khong_lap_bang_hieu_qua(self):
        """Truoc 28/09/2026 bai nay khang dinh len(bad) == 5.

        Con so do khoa lai MOT LOI THAT: voi 6 camp nay, 4 camp vua nam o
        bang "hieu qua" vua nam o bang "kem hieu qua" (C, D, E, F). Da sua
        ngay 28/09/2026 - xem class TestKhongLapGiuaHaiBang ben duoi.
        """
        stats, _ = report.compute_stats(self.env, date(2026, 9, 27), date(2026, 9, 27))
        self.assertEqual(len(stats["good"]), 5)
        # 6 camp: 5 camp co don (A, C, D, E, F) deu vao bang hieu qua;
        # chi con B (0 don) la thuc su kem => bang kem dung 1 dong.
        self.assertEqual(len(stats["bad"]), 1)
        self.assertEqual(stats["bad"][0]["id"], "2")


class TestKhongLapGiuaHaiBang(unittest.TestCase):
    """Mot camp KHONG duoc nam o CA HAI bang xep hang.

    Loi that phat hien ngay 28/09/2026: bang "kem hieu qua" uu tien camp 0 don,
    nhung khi tai khoan it camp thi het camp 0 don, no lay bu bang nhung camp
    CO don - va lay tu duoi len, tuc la trung voi bang "hieu qua" (lay tu tren
    xuong). Tai khoan 5 camp deu co don thi CA 5 nam o ca hai bang, ke ca camp
    tot nhat. Giai doan 3 lam loi nay nang hon vi AI doc ca hai bang de viet
    nhan dinh => nhan dinh tu mau thuan.
    """

    def _chay(self, rows, top="5"):
        goc = report.fetch_insights
        report.fetch_insights = lambda env, since, until: (rows, None)
        try:
            env = {
                "FILTER_INCLUDE": "dainq",
                "FILTER_EXCLUDE": "",
                "TOP_CAMPAIGN_COUNT": top,
                "REPORT_ACCOUNT_NAME": "Test",
            }
            stats, err = report.compute_stats(env, date(2026, 9, 27), date(2026, 9, 27))
            self.assertIsNone(err)
            return stats
        finally:
            report.fetch_insights = goc

    def _id(self, ds):
        return {c["id"] for c in ds}

    def test_5_camp_deu_co_don_thi_bang_kem_RONG(self):
        rows = [_hang_camp(str(i), f"dainq {i}", 1000 * i, i) for i in range(5, 0, -1)]
        stats = self._chay(rows)
        self.assertEqual(len(stats["good"]), 5)
        self.assertEqual(stats["bad"], [])

    def test_5_camp_deu_co_don_KHONG_camp_nao_nam_ca_hai_bang(self):
        rows = [_hang_camp(str(i), f"dainq {i}", 1000 * i, i) for i in range(5, 0, -1)]
        stats = self._chay(rows)
        self.assertEqual(self._id(stats["good"]) & self._id(stats["bad"]), set())

    def test_camp_0_don_VAN_nam_trong_bang_kem(self):
        rows = [
            _hang_camp("a", "dainq A", 100, 5),
            _hang_camp("b", "dainq B", 200, 0),
        ]
        stats = self._chay(rows)
        self.assertIn("b", self._id(stats["bad"]))
        self.assertNotIn("b", self._id(stats["good"]))

    def test_tai_khoan_nhieu_camp_bang_kem_van_du_5_dong(self):
        # Giong du lieu that ngay 28/09/2026: 13 camp, 2 camp 0 don.
        rows = [_hang_camp(f"c{i}", f"dainq {i}", 100 * i, i) for i in range(1, 12)]
        rows.append(_hang_camp("z1", "dainq Z1", 5000, 0))
        rows.append(_hang_camp("z2", "dainq Z2", 4000, 0))
        stats = self._chay(rows)
        self.assertEqual(len(stats["bad"]), 5)
        self.assertEqual(self._id(stats["good"]) & self._id(stats["bad"]), set())

    def test_khong_bao_gio_lap_voi_moi_co_tai_khoan(self):
        for so_camp in (1, 2, 3, 5, 6, 8, 13, 30):
            with self.subTest(so_camp=so_camp):
                rows = [
                    _hang_camp(f"c{i}", f"dainq {i}", 100 * i, i % 4)
                    for i in range(1, so_camp + 1)
                ]
                stats = self._chay(rows)
                chung = self._id(stats["good"]) & self._id(stats["bad"])
                self.assertEqual(chung, set(), f"so_camp={so_camp} bi lap: {chung}")

    def test_bang_kem_khong_dai_hon_top(self):
        rows = [_hang_camp(f"c{i}", f"dainq {i}", 100 * i, 0) for i in range(1, 30)]
        stats = self._chay(rows)
        self.assertLessEqual(len(stats["bad"]), 5)


class TestXepHangTheoChiPhiMoiDon(unittest.TestCase):
    """Bang "hieu qua" phai xep theo CHI PHI MOI DON, khong phai so don.

    Xep theo so don la do QUY MO, khong phai do HIEU QUA - trai voi chinh ten
    bang. Do tren 7 ngay that (22-28/09/2026): 6/7 ngay hai cach chon ra hai
    danh sach camp KHAC NHAU, khong chi khac thu tu.
    """

    def _chay(self, rows):
        goc = report.fetch_insights
        report.fetch_insights = lambda env, since, until: (rows, None)
        try:
            env = {
                "FILTER_INCLUDE": "dainq",
                "FILTER_EXCLUDE": "",
                "TOP_CAMPAIGN_COUNT": "5",
                "REPORT_ACCOUNT_NAME": "Test",
            }
            stats, err = report.compute_stats(env, date(2026, 9, 27), date(2026, 9, 27))
            self.assertIsNone(err)
            return stats
        finally:
            report.fetch_insights = goc

    def _id(self, ds):
        return [c["id"] for c in ds]

    def test_camp_re_hon_xep_truoc(self):
        rows = [
            _hang_camp("a", "dainq A", 2000, 4),
            _hang_camp("b", "dainq B", 1000, 4),
        ]
        stats = self._chay(rows)
        self.assertEqual(self._id(stats["good"]), ["b", "a"])

    def test_camp_dat_tien_bi_day_ra_khoi_bang_hieu_qua(self):
        rows = [_hang_camp(f"r{i}", f"dainq R{i}", 1000, 4) for i in range(1, 6)]
        rows.append(_hang_camp("dat", "dainq DAT", 9000, 6))
        stats = self._chay(rows)
        self.assertNotIn("dat", self._id(stats["good"]))

    def test_camp_1_don_bi_xep_sau_camp_2_don(self):
        # Camp 1 don re hon nhung chua du chin => phai xep sau.
        rows = [
            _hang_camp("mot", "dainq MOT", 100, 1),
            _hang_camp("hai", "dainq HAI", 1000, 2),
        ]
        stats = self._chay(rows)
        self.assertEqual(self._id(stats["good"]), ["hai", "mot"])

    def test_camp_0_don_van_khong_vao_bang_hieu_qua(self):
        rows = [
            _hang_camp("a", "dainq A", 1000, 3),
            _hang_camp("z", "dainq Z", 50, 0),
        ]
        stats = self._chay(rows)
        self.assertNotIn("z", self._id(stats["good"]))

    def test_du_lieu_that_28_09_camp_dat_bi_loai(self):
        # Dung so that ngay 28/09/2026: mot camp 3 don chi 2.325.449 d
        # (775.150 d/don) tung nam trong bang hieu qua, trong khi mot camp
        # 3 don chi 1.217.013 d (405.671 d/don) bi bo sot.
        rows = [
            _hang_camp("tot1", "dainq T1", 2745366, 10),
            _hang_camp("tot2", "dainq T2", 2437319, 8),
            _hang_camp("tot3", "dainq T3", 1070484, 4),
            _hang_camp("tot4", "dainq T4", 1731168, 4),
            _hang_camp("dat", "dainq DAT", 2325449, 3),
            _hang_camp("bo_sot", "dainq BS", 1217013, 3),
        ]
        stats = self._chay(rows)
        self.assertNotIn("dat", self._id(stats["good"]))
        self.assertIn("bo_sot", self._id(stats["good"]))


class TestEpStdoutUtf8(unittest.TestCase):
    """Bao cao PHAI in duoc tieng Viet co dau du chay qua duong ong.

    Loi THAT ngay 28/09/2026: Windows Task Scheduler khoi dong Nguoi truc,
    Python lay bang ma theo locale cua Windows (may nay la cp1252), nen
    print() bao cao co dau lam report.py CHET voi UnicodeEncodeError va
    bao cao KHONG duoc gui. Da tai hien duoc bang cach dat
    PYTHONIOENCODING=cp1252.
    """

    def _voi_luong(self, luong_out, luong_err):
        goc_out, goc_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = luong_out, luong_err
        try:
            report._ep_stdout_utf8()
        finally:
            sys.stdout, sys.stderr = goc_out, goc_err

    def test_dat_lai_ca_hai_luong_thanh_utf8(self):
        goi = []

        class LuongGia:
            def reconfigure(self, **kw):
                goi.append(kw)

        self._voi_luong(LuongGia(), LuongGia())
        self.assertEqual(len(goi), 2)
        for kw in goi:
            self.assertEqual(kw.get("encoding"), "utf-8")
            self.assertEqual(kw.get("errors"), "replace")

    def test_khong_no_khi_luong_khong_co_reconfigure(self):
        self._voi_luong(object(), object())

    def test_khong_no_khi_luong_la_None(self):
        self._voi_luong(None, None)

    def test_reconfigure_loi_thi_khong_no(self):
        class LuongHong:
            def reconfigure(self, **kw):
                raise ValueError("khong doi duoc bang ma")

        self._voi_luong(LuongHong(), LuongHong())

    def test_goi_duoc_nhieu_lan_lien_tiep(self):
        goi = []

        class LuongGia:
            def reconfigure(self, **kw):
                goi.append(kw)

        self._voi_luong(LuongGia(), LuongGia())
        self._voi_luong(LuongGia(), LuongGia())
        self.assertEqual(len(goi), 4)


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


from datetime import datetime


class TestDocMocTuEnv(unittest.TestCase):
    def test_doc_danh_sach_thuong(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": "8,12,17"}), [8, 12, 17]
        )

    def test_co_khoang_trang(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": "8, 12, 17"}), [8, 12, 17]
        )

    def test_sap_xep_lai_va_bo_trung(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": "17,8,8,12"}), [8, 12, 17]
        )

    def test_thieu_khoa_thi_dung_mac_dinh(self):
        self.assertEqual(report.doc_moc_tu_env({}), report.REPORT_SLOTS)

    def test_rong_thi_dung_mac_dinh(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": ""}), report.REPORT_SLOTS
        )

    def test_chu_thi_dung_mac_dinh(self):
        self.assertEqual(
            report.doc_moc_tu_env({"REPORT_SLOTS": "tam,muoi"}), report.REPORT_SLOTS
        )

    def test_bo_qua_phan_tu_sai_giu_phan_tu_dung(self):
        self.assertEqual(report.doc_moc_tu_env({"REPORT_SLOTS": "8,abc,17"}), [8, 17])

    def test_so_ngoai_khoang_bi_bo_qua(self):
        self.assertEqual(report.doc_moc_tu_env({"REPORT_SLOTS": "8,99,-1"}), [8])

    def test_dung_dau_cham_phay(self):
        self.assertEqual(report.doc_moc_tu_env({"REPORT_SLOTS": "8;12;17"}), [8, 12, 17])

    def test_None_cung_dung_mac_dinh(self):
        self.assertEqual(report.doc_moc_tu_env(None), report.REPORT_SLOTS)


class TestMocSang(unittest.TestCase):
    def test_lay_moc_nho_nhat(self):
        self.assertEqual(report.moc_sang([8, 12, 17]), 8)

    def test_danh_sach_khac_van_lay_min(self):
        self.assertEqual(report.moc_sang([7, 13, 20]), 7)

    def test_danh_sach_rong_tra_ve_mac_dinh(self):
        self.assertEqual(report.moc_sang([]), report.MOC_SANG_MAC_DINH)


class TestDeterminePeriodTheoMocSang(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 9, 28, 9, 0, 0)

    def test_moc_8_la_bao_cao_hom_qua(self):
        since, until, _ = report.determine_period(self.now, 8, 8)
        self.assertEqual(since, date(2026, 9, 27))
        self.assertEqual(until, date(2026, 9, 27))

    def test_moc_12_la_bao_cao_trong_ngay(self):
        since, _, _ = report.determine_period(self.now, 12, 8)
        self.assertEqual(since, date(2026, 9, 28))

    def test_khong_truyen_moc_sang_thi_mac_dinh_8(self):
        since, _, _ = report.determine_period(self.now, 8)
        self.assertEqual(since, date(2026, 9, 27))

    def test_doi_moc_sang_thanh_7_thi_moc_7_la_hom_qua(self):
        since, _, _ = report.determine_period(self.now, 7, 7)
        self.assertEqual(since, date(2026, 9, 27))

    def test_doi_moc_sang_thanh_7_thi_moc_8_la_trong_ngay(self):
        since, _, _ = report.determine_period(self.now, 8, 7)
        self.assertEqual(since, date(2026, 9, 28))


class TestBuildReportCoNhanDinhAI(unittest.TestCase):
    """Kiem thu phan nhan dinh do AI viet, chen vao bao cao."""

    def setUp(self):
        self.env = {
            "FILTER_INCLUDE": "dainq",
            "FILTER_EXCLUDE": "thuonghieu",
            "REPORT_ACCOUNT_NAME": "Test",
        }
        self.stats = {
            "total_campaigns": 2,
            "totals": {"spend": 1000.0, "msg": 1, "contact": 1, "order": 1,
                       "purchase": 2, "payment": 1, "comment": 0},
            "good": [{"rank": 1, "id": "1", "name": "a", "spend": 500.0,
                      "purchase": 2, "payment": 1, "msg": 1, "cpr": 250.0}],
            "bad": [
                {"rank": 1, "id": "2", "name": "b", "spend": 500.0,
                 "purchase": 0, "payment": 0, "msg": 0, "cpr": None},
                {"rank": 2, "id": "3", "name": "c", "spend": 900.0,
                 "purchase": 3, "payment": 1, "msg": 2, "cpr": 300.0},
            ],
            "all": [],
            "include_kw": "dainq",
            "exclude_kw": "thuonghieu",
            "account_name": "Test",
        }

    def test_khong_co_nhan_dinh_thi_giu_nguyen_hanh_vi_cu(self):
        text = report.build_report(self.env, self.stats, "27/09/2026")
        self.assertIn("🔵 NHẬN ĐỊNH", text)
        self.assertNotIn("AI", text.split("🔵 NHẬN ĐỊNH")[1][:200])

    def test_co_nhan_dinh_thi_chen_vao(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   nhan_dinh="Hom nay chi tieu tang 20 phan tram.")
        self.assertIn("Hom nay chi tieu tang 20 phan tram.", text)

    def test_nhan_dinh_nam_TRONG_muc_nhan_dinh(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   nhan_dinh="CAU_KIEM_THU")
        phan = text.split("🔵 NHẬN ĐỊNH")[1]
        self.assertIn("CAU_KIEM_THU", phan)

    def test_co_loi_ai_thi_ghi_chu_ro_va_bao_cao_van_day_du(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   loi_ai="HTTP 429")
        self.assertIn("HTTP 429", text)
        self.assertIn("Camp hiệu quả", text)
        self.assertIn("Camp kém hiệu quả", text)

    def test_co_loi_ai_thi_noi_ro_bao_cao_van_day_du(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   loi_ai="het han muc")
        self.assertIn("vẫn đầy đủ", text)

    def test_co_ca_nhan_dinh_lan_loi_thi_uutien_nhan_dinh(self):
        text = report.build_report(self.env, self.stats, "27/09/2026",
                                   nhan_dinh="CAU_KIEM_THU", loi_ai="HTTP 429")
        self.assertIn("CAU_KIEM_THU", text)
        self.assertNotIn("HTTP 429", text)

    def test_bang_hieu_qua_ghi_ro_xep_theo_chi_phi_moi_don(self):
        # Dai doc bang phai biet vi sao camp 10 don khong dung dau.
        text = report.build_report(self.env, self.stats, "27/09/2026")
        self.assertIn("xếp theo chi phí mỗi đơn", text)

    def test_bang_hieu_qua_ghi_ro_moi_don_bao_nhieu(self):
        # 500.000 d / 2 don = 250.000 d moi don
        text = report.build_report(self.env, self.stats, "27/09/2026")
        self.assertIn("Mỗi đơn: 250 VND", text)

    def test_bang_kem_camp_CO_don_cung_ghi_moi_don(self):
        # 900.000 d / 3 don = 300.000 d moi don
        text = report.build_report(self.env, self.stats, "27/09/2026")
        self.assertIn("Mỗi đơn: 300 VND", text)

    def test_camp_0_don_thi_KHONG_ghi_moi_don(self):
        # Chia cho 0 don la vo nghia -> khong duoc in "Mỗi đơn".
        text = report.build_report(self.env, self.stats, "27/09/2026")
        khoi = text.split("- ID chiến dịch: 2")[1].split("- ID chiến dịch")[0]
        self.assertNotIn("Mỗi đơn", khoi)

    def test_chi_phi_moi_don_tra_ve_None_khi_0_don(self):
        self.assertIsNone(report.chi_phi_moi_don({"spend": 500.0, "purchase": 0}))

    def test_chi_phi_moi_don_tinh_dung(self):
        self.assertEqual(report.chi_phi_moi_don({"spend": 900.0, "purchase": 3}), 300.0)

    def test_chi_phi_moi_don_khong_no_khi_thieu_du_lieu(self):
        self.assertIsNone(report.chi_phi_moi_don({}))
        self.assertIsNone(report.chi_phi_moi_don({"spend": "abc", "purchase": "xyz"}))


class TestQuyetDinhKySoSanh(unittest.TestCase):
    """Kiem thu ham quyet dinh co lay so ky truoc hay khong."""

    def test_moc_sang_thi_CO_so_sanh(self):
        self.assertTrue(report.la_bao_cao_tron_ngay(8, [8, 12, 17]))

    def test_moc_12_thi_KHONG_so_sanh(self):
        self.assertFalse(report.la_bao_cao_tron_ngay(12, [8, 12, 17]))

    def test_moc_17_thi_KHONG_so_sanh(self):
        self.assertFalse(report.la_bao_cao_tron_ngay(17, [8, 12, 17]))

    def test_may_khong_co_moc_8_thi_moc_nho_nhat_la_tron_ngay(self):
        self.assertTrue(report.la_bao_cao_tron_ngay(7, [7, 13, 20]))

    def test_danh_sach_rong_thi_khong_so_sanh(self):
        self.assertFalse(report.la_bao_cao_tron_ngay(8, []))


class TestBoiCanh(unittest.TestCase):
    def test_mo_ta_co_ten_tai_khoan_va_ky(self):
        bc = report.tao_boi_canh({"REPORT_ACCOUNT_NAME": "HBR"}, "27/09/2026", True)
        self.assertIn("HBR", bc)
        self.assertIn("27/09/2026", bc)

    def test_moc_tron_ngay_thi_noi_ro(self):
        bc = report.tao_boi_canh({"REPORT_ACCOUNT_NAME": "HBR"}, "27/09/2026", True)
        self.assertIn("TRON ngay", bc)

    def test_moc_mot_phan_thi_noi_ro_va_khong_so_sanh(self):
        bc = report.tao_boi_canh({"REPORT_ACCOUNT_NAME": "HBR"}, "28/09/2026", False)
        self.assertIn("MOT PHAN", bc)
        self.assertIn("khong so sanh", bc)


class TestCoNenGhiLichSu(unittest.TestCase):
    def test_chay_that_thi_ghi(self):
        self.assertTrue(report.co_nen_ghi_lich_su(mock=None, dry=False))

    def test_dry_thi_KHONG_ghi(self):
        self.assertFalse(report.co_nen_ghi_lich_su(mock=None, dry=True))

    def test_mock_thi_KHONG_ghi(self):
        self.assertFalse(report.co_nen_ghi_lich_su(mock=12, dry=False))

    def test_mock_va_dry_deu_khong_ghi(self):
        self.assertFalse(report.co_nen_ghi_lich_su(mock=12, dry=True))


# ============================================================================
# GIAI DOAN 5 - TU XU LY LOI
# ============================================================================


class TestApiGetLuiDan(unittest.TestCase):
    """Meta chan vi qua nhieu yeu cau thi phai CHO roi moi thu lai.

    Loi THAT cua code cu: vong lap thu lai NGAY LAP TUC, khong cho giay nao.
    Dung luc Meta dang chan vi qua nhieu yeu cau thi thu lai ngay chi ton them
    mot lan goi nua, gan nhu chac chan that bai ca ba lan.
    """

    def _chay(self, cac_loi):
        """`cac_loi`: danh sach loi se tra ve theo tung lan goi (None = thanh cong).

        Tra ve (du_lieu, loi, danh_sach_thoi_gian_da_cho).
        """
        da_cho = []
        so_lan = {"n": 0}

        def urlopen_gia(url, timeout=None):
            i = so_lan["n"]
            so_lan["n"] += 1
            loi = cac_loi[i] if i < len(cac_loi) else cac_loi[-1]
            if loi is None:
                return _TraLoiGia({"data": [1]})
            raise _LoiHTTPGia(400, loi)

        goc = report.urllib.request.urlopen
        report.urllib.request.urlopen = urlopen_gia
        try:
            du_lieu, err = report.api_get("x", {}, ngu_fn=da_cho.append)
        finally:
            report.urllib.request.urlopen = goc
        return du_lieu, err, da_cho

    def test_ma_17_thi_cho_roi_thu_lai(self):
        # Lan 1 chan, lan 2 thanh cong -> chi cho MOT lan.
        _, err, da_cho = self._chay([{"code": 17, "message": "chan tam"}, None])
        self.assertIsNone(err)
        self.assertEqual(da_cho, [report.CHO_TRUOC_KHI_THU_LAI[0]])

    def test_ma_80004_thi_cho_roi_thu_lai(self):
        _, err, da_cho = self._chay([{"code": 80004, "message": "chan tam"}, None])
        self.assertIsNone(err)
        self.assertEqual(da_cho, [report.CHO_TRUOC_KHI_THU_LAI[0]])

    def test_chan_ba_lan_thi_cho_du_hai_lan(self):
        _, err, da_cho = self._chay([{"code": 17, "message": "chan tam"}])
        self.assertIsNotNone(err)
        self.assertEqual(da_cho, list(report.CHO_TRUOC_KHI_THU_LAI))

    def test_cho_lau_dan(self):
        self.assertLess(report.CHO_TRUOC_KHI_THU_LAI[0],
                        report.CHO_TRUOC_KHI_THU_LAI[1])

    def test_ma_190_thi_tra_loi_NGAY_khong_cho(self):
        _, err, da_cho = self._chay([{"code": 190, "message": "token het han"}])
        self.assertEqual(err.get("code"), 190)
        self.assertEqual(da_cho, [])

    def test_ma_100_thi_tra_loi_ngay_khong_cho(self):
        _, err, da_cho = self._chay([{"code": 100, "message": "sai tham so"}])
        self.assertEqual(da_cho, [])

    def test_ma_dang_CHUOI_van_nhan_ra_tam_thoi(self):
        """Meta co the tra ma dang chuoi. So sanh '17' in (4, 17) la False.

        Neu khong chuan hoa thi tinh nang lui dan im lang mat tac dung ma
        khong ai biet.
        """
        _, err, da_cho = self._chay([{"code": "17", "message": "chan tam"}, None])
        self.assertIsNone(err)
        self.assertEqual(da_cho, [report.CHO_TRUOC_KHI_THU_LAI[0]])

    def test_ba_lan_deu_chan_thi_tra_loi_cuoi_cung(self):
        """Het 3 luot thu ma Meta van chan thi phai TRA LOI, khong treo."""
        _, err, da_cho = self._chay([{"code": 17, "message": "van chan"}])
        self.assertIsNotNone(err)
        self.assertEqual(err.get("code"), 17)
        self.assertEqual(da_cho, list(report.CHO_TRUOC_KHI_THU_LAI))

    def test_thanh_cong_ngay_lan_dau_thi_khong_cho(self):
        du_lieu, err, da_cho = self._chay([None])
        self.assertEqual(du_lieu, {"data": [1]})
        self.assertEqual(da_cho, [])

    def test_loi_mang_thi_cung_cho_roi_thu_lai(self):
        da_cho = []

        def urlopen_gia(url, timeout=None):
            raise OSError("mang hong")

        goc = report.urllib.request.urlopen
        report.urllib.request.urlopen = urlopen_gia
        try:
            _, err = report.api_get("x", {}, ngu_fn=da_cho.append)
        finally:
            report.urllib.request.urlopen = goc
        self.assertIsNotNone(err)
        self.assertEqual(len(da_cho), 2)


class _TraLoiGia:
    """Gia lap doi tuong tra ve cua urllib.request.urlopen."""

    def __init__(self, du_lieu):
        self._du_lieu = du_lieu

    def read(self):
        import json as _json
        return _json.dumps(self._du_lieu).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _LoiHTTPGia(report.urllib.error.HTTPError):
    """Gia lap HTTPError cua urllib, mang theo phan than JSON cua Meta."""

    def __init__(self, code, than):
        import json as _json
        super().__init__("http://x", code, "loi", {}, None)
        self._than = _json.dumps({"error": than}).encode("utf-8")

    def read(self):
        return self._than


class TestPhanLoaiLoi(unittest.TestCase):

    def test_chin_ma_vinh_vien(self):
        for ma in report.MA_LOI_META_VINH_VIEN:
            with self.subTest(ma=ma):
                chuoi = report.mo_ta_loi_meta({"code": ma, "message": "x"})
                self.assertEqual(report.phan_loai_loi(chuoi), "vinh_vien")

    def test_nam_ma_tam_thoi(self):
        for ma in report.MA_LOI_META_TAM_THOI:
            with self.subTest(ma=ma):
                chuoi = report.mo_ta_loi_meta({"code": ma, "message": "x"})
                self.assertEqual(report.phan_loai_loi(chuoi), "tam_thoi")

    def test_token_het_han_la_vinh_vien(self):
        chuoi = report.mo_ta_loi_meta(
            {"code": 190, "message": "Session has expired"})
        self.assertEqual(report.phan_loai_loi(chuoi), "vinh_vien")

    def test_khong_ro_thi_mac_dinh_TAM_THOI(self):
        """Thu lai mot lan nua la vo hai; tu bo mot loi that su thi te hon."""
        self.assertEqual(report.phan_loai_loi("loi gi do khong ro"), "tam_thoi")

    def test_chuoi_rong_van_tra_ve_tam_thoi(self):
        self.assertEqual(report.phan_loai_loi(""), "tam_thoi")
        self.assertEqual(report.phan_loai_loi(None), "tam_thoi")

    def test_doan_ma_loi_tu_chuoi(self):
        self.assertEqual(report.doc_ma_loi("Loi lay du lieu Meta (ma 190): x"), 190)
        self.assertEqual(report.doc_ma_loi("Loi lay du lieu Meta (ma 80004): x"), 80004)
        self.assertIsNone(report.doc_ma_loi("Loi lay du lieu Meta: khong co ma"))

    def test_mo_ta_loi_kem_ma_de_doc_duoc(self):
        chuoi = report.mo_ta_loi_meta({"code": 190, "message": "token chet"})
        self.assertIn("190", chuoi)
        self.assertIn("token chet", chuoi)

    def test_mo_ta_loi_khi_khong_co_ma(self):
        chuoi = report.mo_ta_loi_meta({"message": "mang hong"})
        self.assertIn("mang hong", chuoi)
        self.assertIsNone(report.doc_ma_loi(chuoi))


class TestMaThoat(unittest.TestCase):

    def test_ba_ma_thoat_khac_nhau(self):
        self.assertEqual(report.MA_THOAT_OK, 0)
        self.assertEqual(report.MA_THOAT_TAM_THOI, 1)
        self.assertEqual(report.MA_THOAT_VINH_VIEN, 2)


class TestChongLapCanhBao(unittest.TestCase):
    """Cung MOT loai loi thi khong gui canh bao lai trong 12 gio.

    Loi THAT: token chet gay 9 tin canh bao giong nhau moi ngay (3 moc x 3 lan
    thu), trong khi viec can lam chi co MOT.
    """

    def _nen(self, loai, luc, kho):
        return report.nen_gui_canh_bao(
            loai, now=luc,
            doc_fn=lambda: dict(kho),
            ghi_fn=lambda k, ts: kho.__setitem__(k, ts),
        )

    def test_lan_dau_thi_gui(self):
        kho = {}
        self.assertTrue(self._nen("vinh_vien:190", _luc(8, 0), kho))

    def test_lan_hai_trong_12_gio_thi_KHONG_gui(self):
        kho = {}
        self._nen("vinh_vien:190", _luc(8, 0), kho)
        self.assertFalse(self._nen("vinh_vien:190", _luc(12, 0), kho))

    def test_sau_12_gio_thi_gui_lai(self):
        kho = {}
        self._nen("vinh_vien:190", _luc(8, 0), kho)
        self.assertTrue(self._nen("vinh_vien:190", _luc(20, 30), kho))

    def test_hai_loai_loi_khac_nhau_thi_deu_gui(self):
        """Token het han va loi mang la hai chuyen khac nhau."""
        kho = {}
        self.assertTrue(self._nen("vinh_vien:190", _luc(8, 0), kho))
        self.assertTrue(self._nen("tam_thoi:khong-ro", _luc(8, 5), kho))

    def test_khoa_canh_bao_ghep_ca_loai_lan_ma(self):
        self.assertEqual(
            report.loai_canh_bao(report.mo_ta_loi_meta(
                {"code": 190, "message": "x"})), "vinh_vien:190")
        self.assertEqual(
            report.loai_canh_bao(report.mo_ta_loi_meta(
                {"code": 17, "message": "x"})), "tam_thoi:17")

    def test_doc_file_hong_thi_van_gui(self):
        """Bo sot mot canh bao loi te hon la gui thua mot tin."""
        def doc_hong():
            raise OSError("file hong")
        self.assertTrue(report.nen_gui_canh_bao(
            "x", now=_luc(8, 0), doc_fn=doc_hong, ghi_fn=lambda k, ts: None))

    def test_ghi_file_hong_khong_nem_loi(self):
        def ghi_hong(k, ts):
            raise OSError("khong ghi duoc")
        self.assertTrue(report.nen_gui_canh_bao(
            "x", now=_luc(8, 0), doc_fn=lambda: {}, ghi_fn=ghi_hong))


def _luc(gio, phut=0, ngay=29):
    from datetime import datetime as _dt
    return _dt(2026, 9, ngay, gio, phut)


class TestCanhBaoHanTokenHaiMuc(unittest.TestCase):
    """Hai muc nhac: 30 ngay (nhe, mot tin/ngay) va 7 ngay (moi bao cao)."""

    def _chay(self, so_ngay, slot=None, danh_sach_moc=None, het_han=None):
        goc = report.doc_han_token_chi_tiet
        report.doc_han_token_chi_tiet = lambda env: (so_ngay, het_han, None)
        try:
            return report.canh_bao_han_token(
                {}, slot=slot, danh_sach_moc=danh_sach_moc)
        finally:
            report.doc_han_token_chi_tiet = goc

    def test_con_45_ngay_thi_khong_nhac_gi(self):
        self.assertEqual(self._chay(45, slot=8, danh_sach_moc=[8, 12, 17]), "")

    def test_dung_30_ngay_thi_chua_nhac(self):
        self.assertEqual(self._chay(30, slot=8, danh_sach_moc=[8, 12, 17]), "")

    def test_con_20_ngay_thi_nhac_o_moc_sang(self):
        chu = self._chay(20, slot=8, danh_sach_moc=[8, 12, 17])
        self.assertIn("NHẮC TOKEN META", chu)

    def test_con_20_ngay_thi_KHONG_nhac_o_moc_17h(self):
        self.assertEqual(self._chay(20, slot=17, danh_sach_moc=[8, 12, 17]), "")

    def test_con_20_ngay_thi_KHONG_nhac_o_moc_12h(self):
        self.assertEqual(self._chay(20, slot=12, danh_sach_moc=[8, 12, 17]), "")

    def test_con_5_ngay_thi_nhac_o_MOI_moc(self):
        for slot in (8, 12, 17):
            with self.subTest(slot=slot):
                chu = self._chay(5, slot=slot, danh_sach_moc=[8, 12, 17])
                self.assertIn("CẢNH BÁO TOKEN META", chu)

    def test_con_5_ngay_thi_khong_con_la_nhac_nhe(self):
        chu = self._chay(5, slot=8, danh_sach_moc=[8, 12, 17])
        self.assertNotIn("NHẮC TOKEN META", chu)

    def test_het_han_thi_bao_do(self):
        chu = self._chay(0.0, slot=12, danh_sach_moc=[8, 12, 17])
        self.assertIn("HẾT HẠN", chu)

    def test_duoi_mot_ngay_thi_hien_theo_gio(self):
        chu = self._chay(0.5, slot=8, danh_sach_moc=[8, 12, 17])
        self.assertIn("12 giờ", chu)

    def test_token_khong_bao_gio_het_han_thi_khong_nhac(self):
        self.assertEqual(self._chay(None, slot=8, danh_sach_moc=[8, 12, 17]), "")

    def test_hien_moc_het_han_cu_the(self):
        from datetime import datetime as _dt
        chu = self._chay(5, slot=8, danh_sach_moc=[8, 12, 17],
                         het_han=_dt(2026, 11, 13, 8, 15))
        self.assertIn("", chu)

    def test_moi_muc_deu_noi_ro_KHONG_tu_gia_han_duoc(self):
        for so_ngay in (20, 5, 0.0):
            with self.subTest(so_ngay=so_ngay):
                chu = self._chay(so_ngay, slot=8, danh_sach_moc=[8, 12, 17])
                self.assertIn("KHÔNG tự gia hạn được", chu)

    def test_cach_goi_cu_khong_truyen_slot_van_chay(self):
        """Goi canh_bao_han_token(env) nhu truoc day: hien o moi bao cao."""
        self.assertEqual(self._chay(20), "")

    def test_loi_doc_han_thi_khong_lam_hong_bao_cao(self):
        goc = report.doc_han_token_chi_tiet

        def no_loi(env):
            raise RuntimeError("mang hong")
        report.doc_han_token_chi_tiet = no_loi
        try:
            self.assertEqual(report.canh_bao_han_token({}, 8, [8, 12, 17]), "")
        finally:
            report.doc_han_token_chi_tiet = goc


class TestDocHanTokenChiTiet(unittest.TestCase):

    def _chay(self, du_lieu, loi=None):
        goc = report.api_get
        report.api_get = lambda path, params, **kw: (du_lieu, loi)
        try:
            return report.doc_han_token_chi_tiet({
                "META_ADS_ACCESS_TOKEN": "t", "META_APP_ID": "a",
                "META_APP_SECRET": "s"})
        finally:
            report.api_get = goc

    def test_token_hop_le_tra_ve_so_ngay_va_moc_het_han(self):
        from datetime import datetime as _dt, timezone as _tz, timedelta as _td
        het_han = _dt.now(_tz.utc) + _td(days=10)
        so_ngay, moc, loi = self._chay(
            {"data": {"is_valid": True, "expires_at": het_han.timestamp()}})
        self.assertIsNone(loi)
        self.assertAlmostEqual(so_ngay, 10, delta=0.01)
        self.assertIsNotNone(moc)

    def test_token_khong_bao_gio_het_han(self):
        so_ngay, moc, loi = self._chay(
            {"data": {"is_valid": True, "expires_at": 0}})
        self.assertIsNone(so_ngay)
        self.assertIsNone(moc)
        self.assertIsNone(loi)

    def test_token_khong_hop_le_tra_ve_0(self):
        so_ngay, _, loi = self._chay({"data": {"is_valid": False}})
        self.assertEqual(so_ngay, 0.0)

    def test_thieu_app_id_thi_bao_loi(self):
        so_ngay, moc, loi = report.doc_han_token_chi_tiet(
            {"META_ADS_ACCESS_TOKEN": "t"})
        self.assertIsNotNone(loi)

    def test_loi_mang_thi_tra_ve_ly_do(self):
        so_ngay, moc, loi = self._chay(None, loi={"message": "mang hong"})
        self.assertIn("mang hong", loi)

    def test_doc_han_token_cu_van_chay(self):
        goc = report.doc_han_token_chi_tiet
        report.doc_han_token_chi_tiet = lambda env: (12.0, None, None)
        try:
            self.assertEqual(report.doc_han_token({}), (12.0, None))
        finally:
            report.doc_han_token_chi_tiet = goc


if __name__ == "__main__":
    unittest.main()
