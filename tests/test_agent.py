"""Kiem thu nac 2 — rao an toan, muc tieu, doc tra loi, so ghi.

KHONG goi mang, KHONG doc file that, KHONG goi AI.
"""
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

import agent_ky_uc
import agent_lich_su
import agent_muc_tieu
import agent_rao
import agent_xin_phep
import lenh_telegram
import lich_su
import nguoi_truc
import report
from agent_rao import GIO_VN, kiem, thuoc_pham_vi


class _KhongGhiLog:
    """Chan ghi vao logs/baocao.log khi chay kiem thu.

    logs/baocao.log la file Dai mo dau tien khi co su co. Kiem thu khong duoc
    viet vao do, nhat la nhung dong mang nghia "Dai da bo qua nhom X" — Dai
    khong he lam viec do.
    """

    def setUp(self):
        self._log_cu = report.log
        report.log = lambda *a, **k: None

    def tearDown(self):
        report.log = self._log_cu

ID = "120250506886650509"
TEN = "2026 - 09 - 30 - dainq - Scale - Online 0/160 X9"


def dx(ten=TEN, hanh_dong="tam_dung", ha=27000, mua=1, cpr=480000, **kw):
    d = {"hanh_dong": hanh_dong,
         "doi_tuong": {"cap": "ad_set", "id": ID, "ten": ten},
         "ngan_sach_ha": ha, "luot_mua": mua, "chi_phi_moi_luot": cpr}
    d.update(kw)
    return d


def nhom(ma=ID, ten=TEN, trang_thai="ACTIVE"):
    return {"id": ma, "name": ten, "effective_status": trang_thai,
            "daily_budget": "400000"}


def dong(spend, mua=0, tin=0):
    """Mot dong insights cua Meta — chu y: Meta tra so dang CHUOI."""
    return {"spend": str(spend),
            "actions": [
                {"action_type": agent_muc_tieu.TEN_LUOT_MUA, "value": str(mua)},
                {"action_type": agent_muc_tieu.TEN_TIN_NHAN, "value": str(tin)},
            ]}


class A_RaoAnToan(unittest.TestCase):
    def test_ten_khong_dainq_thi_chan(self):
        ok, ly = kiem(dx(ten="2026 - 5 - 28 - Truong - Online"))
        self.assertFalse(ok)
        self.assertIn("phạm vi", ly)

    def test_ten_ma_content_thi_cho_phep(self):
        self.assertTrue(kiem(dx(ten="THC295THM295 0/500 X9-26 TN"))[0])

    def test_ten_new_dainq_thi_cho_phep(self):
        self.assertTrue(kiem(dx(ten="new - dainq - TTHC22TTHM22 0/120 X9"))[0])

    def test_chi_duoc_tam_dung(self):
        ok, ly = kiem(dx(hanh_dong="tang_ngan_sach"))
        self.assertFalse(ok)
        self.assertIn("chỉ được TẮT", ly)

    def test_nhom_dang_hieu_qua_thi_chan(self):
        ok, ly = kiem(dx(mua=1, cpr=300000))
        self.assertFalse(ok)
        self.assertIn("ĐANG HIỆU QUẢ", ly)

    def test_nhom_dat_moc_thi_cho_phep(self):
        self.assertTrue(kiem(dx(mua=1, cpr=480000))[0])

    def test_dung_bien_400000_thi_cho_phep(self):
        self.assertTrue(kiem(dx(mua=1, cpr=400000))[0])

    def test_ngan_sach_ha_sai_thi_chan(self):
        ok, ly = kiem(dx(ha=30000))
        self.assertFalse(ok)
        self.assertIn("27.000", ly)

    def test_du_3_hanh_dong_hom_nay_thi_chan(self):
        ok, ly = kiem(dx(), {"so_hanh_dong_hom_nay": 3, "so_hanh_dong_gio_nay": 0})
        self.assertFalse(ok)
        self.assertIn("Hôm nay", ly)

    def test_da_co_hanh_dong_gio_nay_thi_chan(self):
        ok, ly = kiem(dx(), {"so_hanh_dong_hom_nay": 1, "so_hanh_dong_gio_nay": 1})
        self.assertFalse(ok)
        self.assertIn("Giờ này", ly)

    def test_qua_24_gio_thi_chan(self):
        cu = datetime.now(GIO_VN) - timedelta(hours=25)
        ok, ly = kiem(dx(tao_luc=cu))
        self.assertFalse(ok)
        self.assertIn("24 giờ", ly)

    def test_trong_24_gio_thi_cho_phep(self):
        self.assertTrue(kiem(dx(tao_luc=datetime.now(GIO_VN) - timedelta(hours=3)))[0])

    def test_khong_hoi_lai_nhom_da_tra_loi(self):
        ok, ly = kiem(dx(), {"nhom_da_tra_loi": {ID: datetime.now(GIO_VN)}})
        self.assertFalse(ok)
        self.assertIn("trả lời", ly)

    def test_nhom_da_tra_loi_tu_30_gio_truoc_thi_cho_phep(self):
        cu = datetime.now(GIO_VN) - timedelta(hours=30)
        self.assertTrue(kiem(dx(), {"nhom_da_tra_loi": {ID: cu}})[0])

    def test_dau_vao_di_dang_khong_nem_loi(self):
        for xau in [None, "chuoi", 123, [], {}, {"hanh_dong": "tam_dung"},
                    dx(doi_tuong=None), dx(ten=None), dx(mua="ba"), dx(ha="nhieu")]:
            ok, ly = kiem(xau)
            self.assertFalse(ok, f"phai chan: {xau!r}")
            self.assertIsInstance(ly, str)

    def test_nhom_0_luot_mua_khong_bi_rao_hieu_qua(self):
        self.assertTrue(kiem(dx(mua=0, cpr=None))[0])

    def test_luot_mua_co_nhung_doc_khong_ra_thi_chan(self):
        """Khac han 'chua co luot mua' — day la du lieu hong."""
        ok, ly = kiem(dx(mua="khong-ro"))
        self.assertFalse(ok)
        self.assertIn("đọc không ra", ly)

    def test_thuoc_pham_vi(self):
        self.assertTrue(thuoc_pham_vi("2026 - 09 - 30 - dainq - Scale"))
        self.assertTrue(thuoc_pham_vi("new - dainq - X"))
        self.assertTrue(thuoc_pham_vi("THC295THM295 0/500"))
        self.assertFalse(thuoc_pham_vi("2026 - 5 - 28 - Truong - Online"))
        self.assertFalse(thuoc_pham_vi(""))
        self.assertFalse(thuoc_pham_vi(None))


class B_DocTraLoi(unittest.TestCase):
    CHO = [ID]

    def test_tat_co_dau(self):
        self.assertEqual(agent_xin_phep.doc_tra_loi(f"tắt {ID}", self.CHO), ("dong_y", ID))

    def test_tat_chu_hoa(self):
        self.assertEqual(agent_xin_phep.doc_tra_loi(f"TẮT {ID}", self.CHO), ("dong_y", ID))

    def test_tat_khong_dau(self):
        self.assertEqual(agent_xin_phep.doc_tra_loi(f"tat {ID}", self.CHO), ("dong_y", ID))

    def test_bo_qua(self):
        self.assertEqual(agent_xin_phep.doc_tra_loi(f"bỏ qua {ID}", self.CHO), ("tu_choi", ID))

    def test_boqua_viet_lien(self):
        self.assertEqual(agent_xin_phep.doc_tra_loi(f"boqua {ID}", self.CHO), ("tu_choi", ID))

    def test_ma_nhom_khac_thi_khong_khop(self):
        self.assertEqual(agent_xin_phep.doc_tra_loi("tắt 999999999999", self.CHO),
                         ("khong_khop", "999999999999"))

    def test_tin_rac(self):
        for rac in ["", "   ", "hello", "123", None, 123, "tắt", "ừ"]:
            kq, _ = agent_xin_phep.doc_tra_loi(rac, self.CHO)
            self.assertNotEqual(kq, "dong_y", f"khong duoc dong y voi: {rac!r}")

    def test_bo_dau(self):
        self.assertEqual(agent_xin_phep.bo_dau("TẮT ĐI"), "tat di")
        self.assertEqual(agent_xin_phep.bo_dau("Bỏ qua"), "bo qua")

    def test_soan_tin_co_du_ma_nhom(self):
        t = agent_xin_phep.soan_tin(dx())
        self.assertIn(ID, t)
        self.assertIn("XIN PHÉP TẮT NHÓM", t)
        self.assertIn("27.000", t)

    def test_soan_tin_voi_de_xuat_hong_tra_ve_rong(self):
        for xau in [None, {}, "chuoi", {"doi_tuong": None}]:
            self.assertEqual(agent_xin_phep.soan_tin(xau), "")


class C_MucTieu(unittest.TestCase):
    def _xet(self, spend, mua=0, tin=0, ten=TEN, trang_thai="ACTIVE"):
        return agent_muc_tieu.xet([nhom(ten=ten, trang_thai=trang_thai)],
                                  {ID: dong(spend, mua, tin)}, {ID: dong(spend, mua, tin)})

    def test_0_mua_65k_chua_de_xuat(self):
        self.assertEqual(self._xet(65000, 0, 1), [])

    def test_0_mua_70k_co_tin_thi_de_xuat(self):
        self.assertEqual(len(self._xet(70000, 0, 1)), 1)

    def test_0_mua_khong_tin_75k_chua_de_xuat(self):
        self.assertEqual(self._xet(75000, 0, 0), [])

    def test_0_mua_khong_tin_80k_thi_de_xuat(self):
        self.assertEqual(len(self._xet(80000, 0, 0)), 1)

    def test_1_mua_500k_thi_de_xuat(self):
        r = self._xet(500000, 1, 3)
        self.assertEqual(len(r), 1)
        self.assertEqual(r[0]["chi_phi_moi_luot"], 500000)

    def test_2_mua_700k_thi_KHONG_de_xuat(self):
        self.assertEqual(self._xet(700000, 2, 3), [])

    def test_nhom_khong_ACTIVE_thi_bo_qua(self):
        self.assertEqual(self._xet(500000, 1, 3, trang_thai="PAUSED"), [])

    def test_ten_ngoai_pham_vi_thi_bo_qua(self):
        self.assertEqual(self._xet(500000, 1, 0, ten="2026 - 5 - 28 - Truong - Online"), [])

    def test_ten_mac_dinh_cua_meta_thi_bo_qua(self):
        self.assertEqual(self._xet(500000, 1, 0, ten="Nhóm quảng cáo Lượt tương tác mới"), [])

    def test_loai_nhom_thuong_hieu(self):
        r = agent_muc_tieu.xet([nhom(ten="2026 - 09 - 01 - dainq - Brand - Online")],
                               {ID: dong(900000, 0, 0)}, {ID: dong(900000, 0, 0)},
                               ["thuonghieu", "thương hiệu", "Brand"])
        self.assertEqual(r, [])

    def test_bay_dem_trung_5_lan(self):
        """Meta tra 5 ten cho CUNG mot luot mua. Cong ca 5 la sai gap 5 lan."""
        acts = [{"action_type": t, "value": "4"} for t in
                ("omni_purchase", "onsite_conversion.purchase", "onsite_web_purchase",
                 "onsite_app_purchase", "onsite_web_app_purchase")]
        self.assertEqual(agent_muc_tieu.dem_mot_loai(acts, agent_muc_tieu.TEN_LUOT_MUA), 4)
        self.assertEqual(sum(int(a["value"]) for a in acts), 20)

    def test_meta_tra_so_dang_chuoi_van_doc_duoc(self):
        d = agent_muc_tieu.rut_so_mot_dong(dong(123456, 3, 2))
        self.assertEqual(d["spend"], 123456.0)
        self.assertEqual(d["luot_mua"], 3)

    def test_dau_vao_di_dang_khong_nem_loi(self):
        for xau in [None, "chuoi", 123, [None], [{}], [{"spend": None}]]:
            agent_muc_tieu.xet(xau, None, None)
        for xau in [None, "chuoi", 123, {}]:
            agent_muc_tieu.rut_so_mot_dong(xau)

    def test_ly_do_hien_cho_dai_phai_CO_DAU(self):
        """Quy uoc du an: chuoi hien cho Dai CO DAU, chu thich code khong dau."""
        r = self._xet(500000, 1, 3)
        self.assertTrue(any(c in r[0]["ly_do"] for c in "ăâđêôơưáàảãạ"), r[0]["ly_do"])

    def test_tien_kieu_viet_nam(self):
        self.assertEqual(agent_rao.tien(1234567), "1.234.567đ")
        self.assertEqual(agent_rao.tien(0), "0đ")
        self.assertEqual(agent_rao.tien("khong-phai-so"), "?")

    def test_sap_xep_nang_nhat_truoc(self):
        r = agent_muc_tieu.xet(
            [nhom(ma="1", ten="a - dainq - 1"), nhom(ma="2", ten="b - dainq - 2")],
            {"1": dong(90000, 0, 0), "2": dong(2000000, 1, 0)},
            {"1": dong(90000, 0, 0), "2": dong(2000000, 1, 0)})
        self.assertEqual(r[0]["doi_tuong"]["id"], "2")


class D_KyUc(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)
        self.p = self.tmp.name

    def tearDown(self):
        if os.path.exists(self.p):
            os.unlink(self.p)

    def test_doc_file_chua_co_tra_ve_rong(self):
        self.assertEqual(agent_ky_uc.doc(self.p), [])

    def test_ghi_roi_doc_lai(self):
        self.assertTrue(agent_ky_uc.ghi({"hanh_dong": "tam_dung"}, self.p))
        self.assertEqual(len(agent_ky_uc.doc(self.p)), 1)

    def test_doc_file_hong_khong_nem_loi(self):
        with open(self.p, "w", encoding="utf-8") as f:
            f.write("{khong phai json")
        self.assertEqual(agent_ky_uc.doc(self.p), [])

    def _ghi(self, gio, ma=ID, che_do="xin_phep", tra_loi=None, gui=False):
        return agent_ky_uc.ghi({
            "luc": gio.isoformat(timespec="seconds"), "che_do": che_do,
            "hanh_dong": "tam_dung", "doi_tuong": {"id": ma, "ten": TEN},
            "da_gui_len_meta": gui, "dai_phan_hoi": tra_loi}, self.p)

    def test_dem_hanh_dong_theo_ngay_va_gio(self):
        goc = datetime.now(GIO_VN)
        self._ghi(goc, gui=True)
        self._ghi(goc - timedelta(days=1), gui=True)
        d = agent_ky_uc.dem_hanh_dong(goc, self.p)
        self.assertEqual(d["so_hanh_dong_hom_nay"], 1)
        self.assertEqual(d["so_hanh_dong_gio_nay"], 1)

    def test_de_xuat_chua_gui_khong_tinh_la_hanh_dong(self):
        self._ghi(datetime.now(GIO_VN), gui=False)
        self.assertEqual(agent_ky_uc.dem_hanh_dong(None, self.p)["so_hanh_dong_hom_nay"], 0)

    def test_ban_ghi_cu_khong_co_truong_van_tinh_la_hanh_dong(self):
        """Hai ban ghi that ngay 30/09/2026 chua co truong da_gui_len_meta."""
        agent_ky_uc.ghi({"luc": datetime.now(GIO_VN).isoformat(timespec="seconds"),
                         "hanh_dong": "tam_dung", "doi_tuong": {"id": ID}}, self.p)
        self.assertEqual(agent_ky_uc.dem_hanh_dong(None, self.p)["so_hanh_dong_hom_nay"], 1)

    def test_hang_cho_va_ma_dang_cho(self):
        self._ghi(datetime.now(GIO_VN))
        self.assertEqual(len(agent_ky_uc.hang_cho(None, self.p)), 1)
        self.assertEqual(agent_ky_uc.ma_dang_cho(None, self.p), [ID])

    def test_qua_24_gio_thi_khong_con_trong_hang_cho(self):
        self._ghi(datetime.now(GIO_VN) - timedelta(hours=25))
        self.assertEqual(agent_ky_uc.hang_cho(None, self.p), [])

    def test_da_tra_loi_thi_khong_con_trong_hang_cho(self):
        self._ghi(datetime.now(GIO_VN), tra_loi="tat " + ID)
        self.assertEqual(agent_ky_uc.hang_cho(None, self.p), [])

    def test_cap_nhat_phan_hoi(self):
        self._ghi(datetime.now(GIO_VN))
        self.assertTrue(agent_ky_uc.cap_nhat_phan_hoi(ID, "tat " + ID, "xong", self.p))
        self.assertEqual(agent_ky_uc.doc(self.p)[0]["ket_qua"], "xong")

    def test_nhom_da_tra_loi(self):
        self._ghi(datetime.now(GIO_VN), tra_loi="tat " + ID)
        self.assertIn(ID, agent_ky_uc.nhom_da_tra_loi(None, self.p))

    def test_so_rong_thi_cac_ham_van_chay(self):
        self.assertEqual(agent_ky_uc.hang_cho(None, self.p), [])
        self.assertEqual(agent_ky_uc.nhom_da_tra_loi(None, self.p), {})
        self.assertEqual(agent_ky_uc.ma_dang_cho(None, self.p), [])


class E_CauHinh(unittest.TestCase):
    def test_mac_dinh_khi_env_rong(self):
        import agent
        c = agent.doc_cau_hinh({})
        self.assertEqual(c["AGENT_MUC"], 2)
        self.assertTrue(c["AGENT_TAP_SU"])
        self.assertEqual(c["AGENT_NHIP_PHUT"], 30)

    def test_doc_tu_env(self):
        import agent
        c = agent.doc_cau_hinh({"AGENT_MUC": "2", "AGENT_TAP_SU": "false",
                                "AGENT_NHIP_PHUT": "15", "AGENT_TOI_DA_NGAY": "5"})
        self.assertFalse(c["AGENT_TAP_SU"])
        self.assertEqual(c["AGENT_NHIP_PHUT"], 15)
        self.assertEqual(c["AGENT_TOI_DA_NGAY"], 5)

    def test_gia_tri_rac_thi_dung_mac_dinh(self):
        import agent
        c = agent.doc_cau_hinh({"AGENT_NHIP_PHUT": "khong-phai-so"})
        self.assertEqual(c["AGENT_NHIP_PHUT"], 30)


class F_ChuyenTiepLenh(unittest.TestCase):
    """Hai tien trinh dung chung mot bot Telegram: nguoi_truc phai chuyen tiep
    lenh cua Dai cho agent qua file hang doi, KHONG duoc tra loi bang AI."""

    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)
        self.cu = agent_ky_uc.LENH_PATH
        agent_ky_uc.LENH_PATH = Path(self.tmp.name)

    def tearDown(self):
        agent_ky_uc.LENH_PATH = self.cu
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)

    def test_la_lenh(self):
        for t in ["tắt 120250506886650509", "TẮT 120250506886650509", "tat 123456789",
                  "bỏ qua 120250506886650509", "boqua 123456789", "thôi 123456789"]:
            self.assertTrue(lenh_telegram.la_lenh(t), t)
        for t in ["", "còn sống không", "tắt", "123456789",
                  "doanh thu hôm nay thế nào", None, 123]:
            self.assertFalse(lenh_telegram.la_lenh(t), t)

    def test_nguoi_truc_chuyen_tiep_lenh_va_KHONG_goi_AI(self):
        goi_ai = []

        def ai_fn(c):
            goi_ai.append(c)
            return ("AI trả lời", None)

        chu = nguoi_truc.tra_loi_tin_nhan(
            "tắt 120250506886650509", {}, [8, 12, 17], datetime.now(), None, set(),
            tra_loi_ai_fn=ai_fn)
        self.assertEqual(goi_ai, [], "khong duoc goi AI voi lenh cua agent")
        self.assertIn("ghi nhận", chu)
        self.assertEqual(len(agent_ky_uc.doc_lenh()), 1)

    def test_tin_thuong_van_di_vao_AI(self):
        chu = nguoi_truc.tra_loi_tin_nhan(
            "hôm nay doanh thu thế nào", {}, [8, 12, 17], datetime.now(), None, set(),
            tra_loi_ai_fn=lambda c: ("câu trả lời", None))
        self.assertEqual(chu, "câu trả lời")
        self.assertEqual(agent_ky_uc.doc_lenh(), [])

    def test_ghi_roi_xoa_lenh(self):
        self.assertTrue(agent_ky_uc.ghi_lenh("tắt 123456789"))
        self.assertEqual(len(agent_ky_uc.doc_lenh()), 1)
        self.assertTrue(agent_ky_uc.xoa_lenh())
        self.assertEqual(agent_ky_uc.doc_lenh(), [])

    def test_ghi_lenh_rong_thi_khong_ghi(self):
        self.assertFalse(agent_ky_uc.ghi_lenh(""))
        self.assertFalse(agent_ky_uc.ghi_lenh(None))
        self.assertEqual(agent_ky_uc.doc_lenh(), [])


class G_LuongDaiDongY(_KhongGhiLog, unittest.TestCase):
    """Dai dong y -> o che do tap su thi CHI ghi so, KHONG gui gi len Meta."""

    def setUp(self):
        super().setUp()
        self.so = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.so.close()
        os.unlink(self.so.name)
        self.hang = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.hang.close()
        os.unlink(self.hang.name)
        self.cu_so = agent_ky_uc.DUONG_DAN
        self.cu_hang = agent_ky_uc.LENH_PATH
        agent_ky_uc.DUONG_DAN = Path(self.so.name)
        agent_ky_uc.LENH_PATH = Path(self.hang.name)

    def tearDown(self):
        agent_ky_uc.DUONG_DAN = self.cu_so
        agent_ky_uc.LENH_PATH = self.cu_hang
        for p in (self.so.name, self.hang.name):
            if os.path.exists(p):
                os.unlink(p)
        super().tearDown()

    def _dat_hang_cho(self):
        agent_ky_uc.ghi({
            "luc": datetime.now(GIO_VN).isoformat(timespec="seconds"),
            "che_do": "xin_phep", "hanh_dong": "tam_dung",
            "doi_tuong": {"cap": "ad_set", "id": ID, "ten": TEN,
                          "ngan_sach_ngay_vnd": 400000},
            "ly_do": "thu", "rao_an_toan": "cho phep",
            "da_gui_len_meta": False, "dai_phan_hoi": None})

    def test_tap_su_chi_ghi_so_khong_gui_meta(self):
        import agent
        self._dat_hang_cho()
        da_bao = []
        so_viec = agent._lam_theo_lenh({}, {"AGENT_TAP_SU": True, "AGENT_MUC": 2},
                                       datetime.now(GIO_VN), da_bao.append,
                                       f"tắt {ID}", None)
        self.assertEqual(so_viec, 0, "che do tap su khong duoc tinh la da lam")
        self.assertEqual(len(da_bao), 1)
        self.assertIn("TẬP SỰ", da_bao[0])
        rec = agent_ky_uc.doc()[-1]
        self.assertFalse(rec["da_gui_len_meta"])
        self.assertIn("TAP SU", rec["ket_qua"])

    def test_dai_bo_qua_thi_khong_lam_gi(self):
        import agent
        self._dat_hang_cho()
        da_bao = []
        so_viec = agent._lam_theo_lenh({}, {"AGENT_TAP_SU": False, "AGENT_MUC": 2},
                                       datetime.now(GIO_VN), da_bao.append,
                                       f"bỏ qua {ID}", None)
        self.assertEqual(so_viec, 0)
        # Dai chon 30/09/2026: doi tin cu thanh ket qua. Ban ghi nay khong co
        # tin_nhan_id nen phai gui tin moi, va phai noi ro la khong lam gi.
        self.assertEqual(len(da_bao), 1)
        self.assertIn("BỎ QUA", da_bao[0])
        rec = agent_ky_uc.doc()[-1]
        self.assertFalse(rec["da_gui_len_meta"])
        self.assertIn("bỏ qua", rec["ket_qua"])

    def test_lenh_sai_ma_nhom_thi_khong_lam_gi(self):
        import agent
        self._dat_hang_cho()
        da_bao = []
        agent._lam_theo_lenh({}, {"AGENT_TAP_SU": True, "AGENT_MUC": 2},
                             datetime.now(GIO_VN), da_bao.append,
                             "tắt 999999999999", None)
        self.assertEqual(da_bao, [])
        self.assertIsNone(agent_ky_uc.doc()[-1]["dai_phan_hoi"])


class H_NutBam(_KhongGhiLog, unittest.TestCase):
    """Ban phim noi: Dai bam mot cai la gui lenh luon."""

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)
        self.cu = agent_ky_uc.LENH_PATH
        agent_ky_uc.LENH_PATH = Path(self.tmp.name)

    def tearDown(self):
        agent_ky_uc.LENH_PATH = self.cu
        if os.path.exists(self.tmp.name):
            os.unlink(self.tmp.name)
        super().tearDown()

    def test_nut_bam_co_du_hai_nut_dung_ma_nhom(self):
        import json as _json
        d = _json.loads(agent_xin_phep.nut_bam(ID))
        nut = d["inline_keyboard"][0]
        self.assertEqual(len(nut), 2)
        self.assertEqual(nut[0]["callback_data"], f"tat:{ID}")
        self.assertEqual(nut[1]["callback_data"], f"boqua:{ID}")

    def test_du_lieu_nut_bam_doc_duoc_nhu_lenh_go_tay(self):
        self.assertEqual(lenh_telegram.doc_tra_loi(f"tat:{ID}", [ID]), ("dong_y", ID))
        self.assertEqual(lenh_telegram.doc_tra_loi(f"boqua:{ID}", [ID]), ("tu_choi", ID))

    def test_xin_nhan_ca_nut_bam(self):
        ts = nguoi_truc.tham_so_lay_tin(None)
        import json as _json
        self.assertIn("callback_query", _json.loads(ts["allowed_updates"]))
        self.assertIn("message", _json.loads(ts["allowed_updates"]))

    def test_doc_dung_truong_cua_lan_bam(self):
        tin = {"callback_query": {"id": "cb1", "data": f"tat:{ID}",
                                 "message": {"message_id": 99, "chat": {"id": 777}}}}
        self.assertTrue(nguoi_truc.tin_tu_dai_nut_bam(tin, 777))
        self.assertFalse(nguoi_truc.tin_tu_dai_nut_bam(tin, 888))
        self.assertEqual(nguoi_truc.du_lieu_nut_bam(tin), f"tat:{ID}")
        self.assertEqual(nguoi_truc.ma_tin_nhan_nut_bam(tin), 99)
        self.assertEqual(nguoi_truc.ma_lan_bam(tin), "cb1")

    def test_truong_thieu_khong_nem_loi(self):
        for xau in [None, {}, {"callback_query": None}, {"callback_query": {}},
                    "chuoi", {"callback_query": {"message": None}}]:
            self.assertFalse(nguoi_truc.tin_tu_dai_nut_bam(xau, 1))
            self.assertEqual(nguoi_truc.du_lieu_nut_bam(xau), "")
            self.assertIsNone(nguoi_truc.ma_tin_nhan_nut_bam(xau))
            self.assertIsNone(nguoi_truc.ma_lan_bam(xau))

    def test_bao_ket_qua_sua_tin_cu_khi_bam_nut(self):
        import agent
        da_sua = []
        cu = agent_xin_phep.sua_ket_qua
        agent_xin_phep.sua_ket_qua = lambda env, mid, text, nut=None: (
            da_sua.append((mid, text)), True)[1]
        try:
            agent._bao_ket_qua({}, {"tin_nhan_id": 55}, lambda t: None, "xong")
        finally:
            agent_xin_phep.sua_ket_qua = cu
        self.assertEqual(da_sua, [(55, "xong")])

    def test_bao_ket_qua_truyen_duoc_nut_hoan_tac(self):
        import agent
        da_sua = []
        cu = agent_xin_phep.sua_ket_qua
        agent_xin_phep.sua_ket_qua = lambda env, mid, text, nut=None: (
            da_sua.append((mid, nut)), True)[1]
        try:
            agent._bao_ket_qua({}, {"tin_nhan_id": 55}, lambda t: None, "xong",
                               nut='{"inline_keyboard":[]}')
        finally:
            agent_xin_phep.sua_ket_qua = cu
        self.assertEqual(da_sua[0][1], '{"inline_keyboard":[]}')

    def test_bao_ket_qua_gui_tin_moi_khi_go_tay(self):
        import agent
        da_gui = []
        agent._bao_ket_qua({}, {"tin_nhan_id": None}, da_gui.append, "xong")
        self.assertEqual(da_gui, ["xong"])

    def test_bao_ket_qua_van_gui_tin_moi_neu_sua_that_bai(self):
        import agent
        cu = agent_xin_phep.sua_ket_qua
        agent_xin_phep.sua_ket_qua = lambda env, mid, text, nut=None: False
        da_gui = []
        try:
            agent._bao_ket_qua({}, {"tin_nhan_id": 55}, da_gui.append, "xong")
        finally:
            agent_xin_phep.sua_ket_qua = cu
        self.assertEqual(da_gui, ["xong"], "sua hong thi phai gui tin moi")


class I_KhoaMotTienTrinh(_KhongGhiLog, unittest.TestCase):
    """Chi cho MOT agent chay cung luc.

    Ngay 30/09/2026 nhat ky ghi agent khoi dong HAI LAN cach nhau 15 giay. Hai
    agent cung chay thi de xuat trung, xu ly trung, so loan.
    """

    def setUp(self):
        super().setUp()
        self.tmp = tempfile.NamedTemporaryFile(suffix=".lock", delete=False)
        self.tmp.close()
        os.unlink(self.tmp.name)
        self.k = self.tmp.name

    def tearDown(self):
        if os.path.exists(self.k):
            os.unlink(self.k)
        super().tearDown()

    def test_lan_dau_thi_giu_duoc(self):
        giu, _ = agent_ky_uc.giu_khoa(30, duong_dan=self.k)
        self.assertTrue(giu)

    def test_lan_hai_thi_bi_tu_choi(self):
        self.assertTrue(agent_ky_uc.giu_khoa(30, duong_dan=self.k)[0])
        giu, ly = agent_ky_uc.giu_khoa(30, duong_dan=self.k)
        self.assertFalse(giu, "khong duoc cho agent thu hai chay")
        self.assertIn("đang chạy", ly)

    def test_khoa_cu_qua_han_thi_gianh_lai(self):
        self.assertTrue(agent_ky_uc.giu_khoa(30, duong_dan=self.k)[0])
        cu = datetime.now(GIO_VN) - timedelta(hours=3)
        giu, ly = agent_ky_uc.giu_khoa(30, bay_gio=cu + timedelta(hours=4), duong_dan=self.k)
        self.assertTrue(giu, "khoa cu thi phai gianh lai duoc")
        self.assertIn("qua han", ly)

    def test_cap_nhat_khoa_giu_cho_khoa_con_song(self):
        self.assertTrue(agent_ky_uc.giu_khoa(30, duong_dan=self.k)[0])
        now = datetime.now(GIO_VN)
        agent_ky_uc.cap_nhat_khoa(now, duong_dan=self.k)
        co, _ = agent_ky_uc.co_agent_khac_dang_chay(30, now + timedelta(minutes=40),
                                                    duong_dan=self.k)
        self.assertTrue(co, "khoa vua cap nhat thi van con song")

    def test_nha_khoa_thi_agent_khac_chay_duoc(self):
        self.assertTrue(agent_ky_uc.giu_khoa(30, duong_dan=self.k)[0])
        agent_ky_uc.nha_khoa(self.k)
        co, _ = agent_ky_uc.co_agent_khac_dang_chay(30, duong_dan=self.k)
        self.assertFalse(co)
        self.assertTrue(agent_ky_uc.giu_khoa(30, duong_dan=self.k)[0])

    def test_chua_co_khoa_thi_khong_ai_chay(self):
        co, _ = agent_ky_uc.co_agent_khac_dang_chay(30, duong_dan=self.k)
        self.assertFalse(co)

    def test_khoa_hong_thi_coi_nhu_khong_co(self):
        with open(self.k, "w", encoding="utf-8") as f:
            f.write("khong phai thoi diem")
        co, _ = agent_ky_uc.co_agent_khac_dang_chay(30, duong_dan=self.k)
        self.assertFalse(co)
        self.assertTrue(agent_ky_uc.giu_khoa(30, duong_dan=self.k)[0])

    def test_khong_tao_duoc_khoa_thi_van_CHO_chay(self):
        """Khoa loi thi khong duoc chan agent — the moi nguy hiem hon."""
        giu, ly = agent_ky_uc.giu_khoa(30, duong_dan="Z:\\khong\\co\\thu\\muc\\nay.lock")
        self.assertTrue(giu, "khong tao duoc khoa thi van phai cho chay")
        self.assertIn("van chay", ly)

    # --- Khoa ghi PID: biet CHAC tien trinh con song hay da chet (01/10/2026) ---

    def test_khoa_co_PID_con_song_thi_van_bi_chan(self):
        """Khoa do CHINH tien trinh nay giu (PID con song) => van phai chan."""
        agent_ky_uc._ghi_khoa(datetime.now(GIO_VN), duong_dan=self.k)
        co, _ = agent_ky_uc.co_agent_khac_dang_chay(30, duong_dan=self.k)
        self.assertTrue(co, "PID con song thi khoa van con hieu luc")

    def test_khoa_co_PID_da_chet_thi_gianh_lai_NGAY(self):
        """Loi that 01/10/2026: .bat dung agent cu roi bat lai NGAY.

        Khoa con MOI (vua ghi) nhung PID da chet => phai gianh lai duoc ngay,
        khong doi het han 60 phut.
        """
        with open(self.k, "w", encoding="utf-8") as f:
            f.write(datetime.now(GIO_VN).isoformat(timespec="seconds") + "\n999999999\n")
        co, _ = agent_ky_uc.co_agent_khac_dang_chay(30, duong_dan=self.k)
        self.assertFalse(co, "PID da chet thi khoa phai coi nhu het hieu luc")
        giu, _ = agent_ky_uc.giu_khoa(30, duong_dan=self.k)
        self.assertTrue(giu, "phai gianh lai duoc ngay, khong doi 60 phut")

    def test_khoa_khong_ghi_PID_thi_lui_ve_xet_thoi_diem(self):
        """Khoa cu (chi co mot dong, khong co PID) van phai doc duoc nhu truoc."""
        with open(self.k, "w", encoding="utf-8") as f:
            f.write(datetime.now(GIO_VN).isoformat(timespec="seconds") + "\n")
        co, _ = agent_ky_uc.co_agent_khac_dang_chay(30, duong_dan=self.k)
        self.assertTrue(co, "khong co PID thi xet theo thoi diem cap nhat")

    def test_ghi_khoa_co_ghi_PID_cua_chinh_minh(self):
        agent_ky_uc._ghi_khoa(datetime.now(GIO_VN), duong_dan=self.k)
        self.assertEqual(agent_ky_uc._doc_khoa_pid(self.k), os.getpid())


class J_HoanTac(_KhongGhiLog, unittest.TestCase):
    """Nut HOAN TAC — bat lai nhom vua tat. Tat nham thi mat giai doan hoc cua Meta."""

    def setUp(self):
        super().setUp()
        self.so = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.so.close()
        os.unlink(self.so.name)
        self.cu = agent_ky_uc.DUONG_DAN
        agent_ky_uc.DUONG_DAN = Path(self.so.name)

    def tearDown(self):
        agent_ky_uc.DUONG_DAN = self.cu
        if os.path.exists(self.so.name):
            os.unlink(self.so.name)
        super().tearDown()

    def _dx_hoan_tac(self, ha=400000, tao_luc=None, ten=TEN, **kw):
        d = {"hanh_dong": "bat_lai",
             "doi_tuong": {"cap": "ad_set", "id": ID, "ten": ten},
             "ngan_sach_khoi_phuc": ha,
             "tao_luc": tao_luc or datetime.now(GIO_VN)}
        d.update(kw)
        return d

    def test_lenh_hoan_tac_doc_dung(self):
        self.assertEqual(lenh_telegram.doc_tra_loi(f"batlai:{ID}", [ID]),
                         ("hoan_tac", ID))
        self.assertTrue(lenh_telegram.la_hoan_tac(f"batlai:{ID}"))
        self.assertTrue(lenh_telegram.la_hoan_tac(f"bật lại {ID}"))
        self.assertTrue(lenh_telegram.la_hoan_tac(f"hoàn tác {ID}"))
        self.assertFalse(lenh_telegram.la_hoan_tac(f"tắt {ID}"))
        self.assertEqual(lenh_telegram.ma_trong_lenh(f"batlai:{ID}"), ID)

    def test_hoan_tac_hop_le_thi_cho_phep(self):
        ok, _ = kiem(self._dx_hoan_tac())
        self.assertTrue(ok)

    def test_hoan_tac_ngan_sach_vo_ly_thi_chan(self):
        for xau in [0, -1, 5000001, "nhieu", None]:
            ok, ly = kiem(self._dx_hoan_tac(ha=xau))
            self.assertFalse(ok, f"phai chan ngan sach {xau!r}")
            self.assertIsInstance(ly, str)

    def test_hoan_tac_qua_24_gio_thi_chan(self):
        cu = datetime.now(GIO_VN) - timedelta(hours=25)
        ok, ly = kiem(self._dx_hoan_tac(tao_luc=cu))
        self.assertFalse(ok)
        self.assertIn("24 giờ", ly)

    def test_hoan_tac_khong_doc_duoc_thoi_diem_thi_chan(self):
        ok, _ = kiem(self._dx_hoan_tac(tao_luc="khong-phai-thoi-diem"))
        self.assertFalse(ok)

    def test_hoan_tac_ten_ngoai_pham_vi_thi_chan(self):
        ok, _ = kiem(self._dx_hoan_tac(ten="2026 - 5 - 28 - Truong - Online"))
        self.assertFalse(ok)

    def test_hoan_tac_KHONG_bi_tran_hanh_dong_chan(self):
        """Loi that do kiem thu bat duoc: chinh lenh TAT vua roi duoc tinh la
        '1 hanh dong trong gio', nen neu ap tran thi nut HOAN TAC bi chan ngay
        sau khi vua tat — dung luc can nhat."""
        ok, ly = kiem(self._dx_hoan_tac(),
                      {"so_hanh_dong_hom_nay": 3, "so_hanh_dong_gio_nay": 1})
        self.assertTrue(ok, f"hoan tac phai luon duoc phep, dang bi chan: {ly}")

    def test_hoan_tac_khong_bi_rao_hieu_qua_chan(self):
        """Nhom vua tat co the da co luot mua — hoan tac van phai duoc phep."""
        ok, _ = kiem(self._dx_hoan_tac(mua=1, chi_phi_moi_luot=100000))
        self.assertTrue(ok)

    def test_lan_tat_gan_nhat_tim_dung(self):
        agent_ky_uc.ghi({
            "luc": datetime.now(GIO_VN).isoformat(timespec="seconds"),
            "hanh_dong": "tam_dung", "da_gui_len_meta": True,
            "ket_qua": "thanh cong (doc lai thay PAUSED va dung ngan sach)",
            "doi_tuong": {"id": ID, "ten": TEN, "ngan_sach_ngay_vnd": 400000}})
        r = agent_ky_uc.lan_tat_gan_nhat(ID)
        self.assertIsNotNone(r)
        self.assertEqual(r["doi_tuong"]["ngan_sach_ngay_vnd"], 400000)

    def test_lan_tat_that_bai_thi_khong_tinh(self):
        agent_ky_uc.ghi({
            "luc": datetime.now(GIO_VN).isoformat(timespec="seconds"),
            "hanh_dong": "tam_dung", "da_gui_len_meta": True,
            "ket_qua": "Meta tu choi: loi gi do",
            "doi_tuong": {"id": ID, "ten": TEN, "ngan_sach_ngay_vnd": 400000}})
        self.assertIsNone(agent_ky_uc.lan_tat_gan_nhat(ID))

    def test_hoan_tac_o_che_do_tap_su_thi_chi_ghi_so(self):
        import agent
        agent_ky_uc.ghi({
            "luc": datetime.now(GIO_VN).isoformat(timespec="seconds"),
            "hanh_dong": "tam_dung", "da_gui_len_meta": True,
            "ket_qua": "thanh cong (doc lai thay PAUSED va dung ngan sach)",
            "doi_tuong": {"id": ID, "ten": TEN, "ngan_sach_ngay_vnd": 400000}})
        da_bao = []
        so_viec = agent._lam_hoan_tac({}, {"AGENT_TAP_SU": True, "AGENT_MUC": 2},
                                      ID, f"batlai:{ID}", 55, datetime.now(GIO_VN),
                                      da_bao.append)
        self.assertEqual(so_viec, 0, "tap su khong tinh la da lam")
        self.assertEqual(len(da_bao), 1)
        self.assertIn("TẬP SỰ", da_bao[0])
        self.assertFalse(agent_ky_uc.doc()[-1]["da_gui_len_meta"])

    def test_hoan_tac_khi_khong_co_lan_tat_nao_thi_bao_ro(self):
        import agent
        da_bao = []
        so_viec = agent._lam_hoan_tac({}, {"AGENT_TAP_SU": False, "AGENT_MUC": 2},
                                      ID, f"batlai:{ID}", None, datetime.now(GIO_VN),
                                      da_bao.append)
        self.assertEqual(so_viec, 0)
        self.assertEqual(len(da_bao), 1)
        self.assertIn("Không hoàn tác được", da_bao[0])

    def test_nut_hoan_tac_co_dung_du_lieu(self):
        import json as _json
        d = _json.loads(agent_xin_phep.nut_hoan_tac(ID))
        self.assertEqual(d["inline_keyboard"][0][0]["callback_data"], f"batlai:{ID}")


class K_ChayNgan(_KhongGhiLog, unittest.TestCase):
    """Chay NEN bang pythonw.exe: khong co console => sys.stdout la None.

    Khong co ham chan thi MOI lenh print nem loi va tien trinh chet ngay —
    nghia la bat chay an di la hong, ma khong nhin thay loi o dau.
    """

    def test_khong_co_man_hinh_thi_khong_nem_loi(self):
        import sys as _sys

        import agent
        import nguoi_truc
        cu_out, cu_err = _sys.stdout, _sys.stderr
        try:
            _sys.stdout = None
            _sys.stderr = None
            agent._an_toan_stdout()
            self.assertIsNotNone(_sys.stdout)
            nguoi_truc._an_toan_stdout()
            self.assertIsNotNone(_sys.stderr)
        finally:
            _sys.stdout, _sys.stderr = cu_out, cu_err

    def test_co_man_hinh_thi_KHONG_doi_gi(self):
        import sys as _sys

        import agent
        cu_out = _sys.stdout
        agent._an_toan_stdout()
        self.assertIs(_sys.stdout, cu_out, "co console roi thi khong duoc doi")


class L_AgentTuGhiLichSu(_KhongGhiLog, unittest.TestCase):
    """Agent tu ghi logs/lich-su.json — de phan hoi dap khong chet khi bo bao cao.

    Moi bai deu CHAN report.compute_stats / report.luu_lich_su => KHONG goi mang.
    """

    def setUp(self):
        super().setUp()
        self.so = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
        self.so.close()
        os.unlink(self.so.name)
        self.goi = []

    def tearDown(self):
        if os.path.exists(self.so.name):
            os.unlink(self.so.name)
        super().tearDown()

    def _chan(self, stats=None, loi=None, nem=None):
        """Chan report.compute_stats + report.luu_lich_su, ghi lai tung loi goi."""
        cu_cs, cu_luu = report.compute_stats, report.luu_lich_su
        self.addCleanup(setattr, report, "compute_stats", cu_cs)
        self.addCleanup(setattr, report, "luu_lich_su", cu_luu)
        mac_dinh = {"totals": {}, "all": [], "total_campaigns": 0}

        def cs(env, since, until):
            self.goi.append(("compute_stats", since, until))
            if nem is not None:
                raise nem
            return (mac_dinh if stats is None else stats), loi

        def luu(s, ngay, moc, path=None):
            self.goi.append(("luu_lich_su", ngay, moc, path))
            return lich_su.ghi(path, ngay, moc, s)

        report.compute_stats = cs
        report.luu_lich_su = luu

    def test_truoc_9h_thi_khong_lam_gi(self):
        self._chan()
        t = datetime(2026, 10, 1, 8, 59, tzinfo=GIO_VN)
        da_ghi, ly = agent_lich_su.ghi_neu_can({}, t, self.so.name)
        self.assertFalse(da_ghi)
        self.assertIn("chua toi", ly)
        self.assertEqual(self.goi, [], "truoc 9h thi KHONG duoc goi Meta")

    def test_ngay_hom_qua_dung_mui_gio_VN(self):
        for h in (0, 8, 9, 23):
            t = datetime(2026, 10, 1, h, 30, tzinfo=GIO_VN)
            self.assertEqual(str(agent_lich_su.ngay_hom_qua(t)), "2026-09-30")

    def test_moc_ghi_phai_nam_trong_MOC_DAY_DU(self):
        self.assertIn(agent_lich_su.MOC_TRON_NGAY, lich_su.MOC_DAY_DU,
                      "moc khac thi ban ghi KHONG duoc coi la tron ngay")

    def test_thieu_thi_lay_so_va_ghi(self):
        self._chan()
        t = datetime(2026, 10, 1, 9, 30, tzinfo=GIO_VN)
        da_ghi, ly = agent_lich_su.ghi_neu_can({}, t, self.so.name)
        self.assertTrue(da_ghi, ly)
        self.assertEqual([g[0] for g in self.goi], ["compute_stats", "luu_lich_su"])
        self.assertEqual(str(self.goi[0][1]), "2026-09-30", "phai lay so NGAY HOM QUA")
        self.assertEqual(str(self.goi[0][2]), "2026-09-30", "chi mot ngay tron ven")
        self.assertEqual(self.goi[1][2], 8, "moc ghi phai la 8")
        self.assertTrue(lich_su.lay_mot_ngay(self.so.name, "2026-09-30").get("day_du"))

    def test_da_co_ban_ghi_tron_ngay_thi_thoi(self):
        lich_su.ghi(self.so.name, "2026-09-30", 8,
                    {"totals": {}, "all": [], "total_campaigns": 0})
        self._chan()
        t = datetime(2026, 10, 1, 10, 0, tzinfo=GIO_VN)
        da_ghi, ly = agent_lich_su.ghi_neu_can({}, t, self.so.name)
        self.assertFalse(da_ghi)
        self.assertIn("da co ban ghi tron ngay", ly)
        self.assertEqual(self.goi, [], "da co ban ghi tron ngay thi KHONG goi Meta")

    def test_ban_ghi_khong_day_du_thi_van_ghi(self):
        lich_su.ghi(self.so.name, "2026-09-30", 17,
                    {"totals": {}, "all": [], "total_campaigns": 0})
        self._chan()
        t = datetime(2026, 10, 1, 10, 0, tzinfo=GIO_VN)
        da_ghi, ly = agent_lich_su.ghi_neu_can({}, t, self.so.name)
        self.assertTrue(da_ghi, ly)
        self.assertIn("compute_stats", [g[0] for g in self.goi])
        self.assertEqual(lich_su.lay_mot_ngay(self.so.name, "2026-09-30").get("moc"), 8)

    def test_meta_loi_thi_KHONG_nem_ra(self):
        self._chan(loi="Meta chan tam")
        t = datetime(2026, 10, 1, 10, 0, tzinfo=GIO_VN)
        da_ghi, ly = agent_lich_su.ghi_neu_can({}, t, self.so.name)
        self.assertFalse(da_ghi)
        self.assertIn("khong lay duoc so", ly)

    def test_compute_stats_nem_exception_cung_khong_sao(self):
        self._chan(nem=RuntimeError("gia lap Meta sap"))
        t = datetime(2026, 10, 1, 10, 0, tzinfo=GIO_VN)
        da_ghi, ly = agent_lich_su.ghi_neu_can({}, t, self.so.name)
        self.assertFalse(da_ghi)
        self.assertIn("loi khi ghi so", ly)
        self.assertIn("RuntimeError", ly)


class M_AgentDocTelegram(_KhongGhiLog, unittest.TestCase):
    """Agent so huu Telegram (buoc 2-4 cua ke hoach chuyen nha, 01/10/2026).

    Moi bai deu CHAN nguoi_truc.lay_tin_moi / gui_tin_nhan va chan ghi so
    => KHONG goi mang, KHONG lam ban logs/nhat-ky-agent.json that.
    """

    def setUp(self):
        super().setUp()
        import agent

        self.agent = agent
        self.gui = []
        self.nut_da_tra_loi = []

        def _chan(obj, ten, moi):
            cu = getattr(obj, ten)
            self.addCleanup(setattr, obj, ten, cu)
            setattr(obj, ten, moi)

        _chan(nguoi_truc, "lay_tin_moi", lambda env, offset: ([], None))
        _chan(nguoi_truc, "gui_tin_nhan",
              lambda env, text: (self.gui.append(text), True)[1])
        _chan(nguoi_truc, "tra_loi_nut_bam",
              lambda env, cb, text="": (self.nut_da_tra_loi.append(cb), True)[1])
        _chan(agent_ky_uc, "hang_cho", lambda bay_gio=None: [])
        _chan(agent_ky_uc, "lan_tat_gan_nhat", lambda ma, bay_gio=None: None)
        _chan(agent_ky_uc, "ghi", lambda ban_ghi: True)
        _chan(agent_ky_uc, "cap_nhat_phan_hoi", lambda ma, nd, kq: True)

        self.env = {"TELEGRAM_CHAT_ID": "123", "REPORT_ACCOUNT_NAME": "Test",
                    "REPORT_SLOTS": "8,12,17"}
        self.cau_hinh = dict(agent.MAC_DINH)
        self.bay_gio = datetime(2026, 10, 1, 10, 0, tzinfo=GIO_VN)
        self.tt = {"offset": None, "da_doc_ton_dong": True,
                   "bat_dau": self.bay_gio, "lan_gui_cuoi": None}
        self.thong_bao = lambda text: None

    def _tin(self, text, chat=123):
        return {"update_id": 1, "message": {"chat": {"id": chat}, "text": text}}

    def _nut(self, data, chat=123):
        return {"update_id": 2, "callback_query": {
            "id": "cb1", "data": data,
            "message": {"message_id": 9, "chat": {"id": chat}}}}

    def _xu_ly(self, tin):
        self.agent._xu_ly_mot_tin(self.env, self.cau_hinh, self.bay_gio,
                                  self.thong_bao, self.tt, tin)

    def test_lenh_go_tay_KHONG_di_vao_AI(self):
        def no(*a, **k):
            raise AssertionError("LENH khong duoc dua cho AI")
        cu = nguoi_truc.tra_loi_tin_nhan
        self.addCleanup(setattr, nguoi_truc, "tra_loi_tin_nhan", cu)
        nguoi_truc.tra_loi_tin_nhan = no
        self._xu_ly(self._tin("tat 120250506886650509"))
        self.assertEqual(self.gui, [])

    def test_cau_hoi_thi_tra_loi_va_gui_di(self):
        self._xu_ly(self._tin("con song khong?"))
        self.assertEqual(len(self.gui), 1, "phai gui dung mot cau tra loi")
        self.assertIn("đang chạy", self.gui[0])

    def test_cau_tra_loi_noi_ro_AGENT_tra_loi(self):
        self._xu_ly(self._tin("con song khong?"))
        self.assertIn("Agent", self.gui[0], "phai noi ro ai tra loi")

    def test_Lan_gui_gan_nhat_noi_DUNG_su_that(self):
        """Agent khong gui bao cao nen khong duoc noi 'chua co trong phien nay'.

        Loi that 01/10/2026: cau tra loi hien '- Hom nay da gui: 8h' ngay tren
        '- Lan gui gan nhat: chua co trong phien nay' — hai dong mau thuan nhau.
        """
        self._xu_ly(self._tin("con song khong?"))
        self.assertNotIn("chưa có trong phiên này", self.gui[0])
        self.assertIn("tiến trình báo cáo gửi", self.gui[0])

    # --- Bao cao theo yeu cau qua Telegram (01/10/2026) ---

    def test_nhan_dien_yeu_cau_bao_cao(self):
        import agent
        for chu in ("báo cáo", "báo cáo hôm qua", "bao cao", "báo cáo hôm nay",
                    "gui bao cao hom qua", "BÁO CÁO HÔM QUA"):
            self.assertTrue(agent._la_yeu_cau_bao_cao(chu), chu)
        for chu in ("báo cáo hôm qua thế nào?", "báo cáo tháng 9",
                    "hôm qua có bao nhiêu đơn", "còn sống không?", ""):
            self.assertFalse(agent._la_yeu_cau_bao_cao(chu), chu)

    def test_moc_mac_dinh_la_bao_cao_HOM_QUA(self):
        import agent
        t = datetime(2026, 10, 1, 13, 0, tzinfo=GIO_VN)
        self.assertEqual(agent._moc_cho_bao_cao("báo cáo", t, [8, 12, 17]), 8)
        self.assertEqual(agent._moc_cho_bao_cao("báo cáo hôm qua", t, [8, 12, 17]), 8)

    def test_moc_hom_nay_lay_moc_DA_QUA(self):
        import agent
        t = datetime(2026, 10, 1, 13, 0, tzinfo=GIO_VN)
        self.assertEqual(agent._moc_cho_bao_cao("báo cáo hôm nay", t, [8, 12, 17]), 12)
        t2 = datetime(2026, 10, 1, 9, 0, tzinfo=GIO_VN)
        self.assertEqual(agent._moc_cho_bao_cao("báo cáo hôm nay", t2, [8, 12, 17]), 8)

    def test_yeu_cau_bao_cao_CHAY_report_py_co_FORCE(self):
        import agent
        da_chay = []

        class Kq:
            returncode = 0

        cu = agent.subprocess.run
        self.addCleanup(setattr, agent.subprocess, "run", cu)
        agent.subprocess.run = lambda *a, **k: (da_chay.append(a[0]), Kq())[1]

        self._xu_ly(self._tin("báo cáo hôm qua"))
        self.assertEqual(len(da_chay), 1, "phai chay report.py dung MOT lan")
        lenh = [str(x) for x in da_chay[0]]
        self.assertIn("report.py", " ".join(lenh))
        self.assertIn("--slot", lenh)
        self.assertIn("--force", lenh, "Dai yeu cau thi phai gui, du da gui hom nay")
        self.assertEqual(len(self.gui), 1, "phai bao Dai la dang lay bao cao")

    def test_yeu_cau_bao_cao_loi_thi_bao_RO(self):
        import agent

        class Kq:
            returncode = 2

        cu = agent.subprocess.run
        self.addCleanup(setattr, agent.subprocess, "run", cu)
        agent.subprocess.run = lambda *a, **k: Kq()

        self._xu_ly(self._tin("báo cáo"))
        self.assertEqual(len(self.gui), 2, "mot tin bao dang lay + mot tin bao loi")
        self.assertIn("lỗi", self.gui[-1])

    def test_ngay_duoc_neu_cac_dinh_dang(self):
        import agent
        t = datetime(2026, 10, 1, 11, 0, tzinfo=GIO_VN)
        for chu in ("báo cáo 15/09", "báo cáo 15-09-2026", "báo cáo 2026-09-15"):
            self.assertEqual(str(agent._ngay_duoc_neu(chu, t)), "2026-09-15", chu)
        for chu in ("báo cáo hôm qua", "báo cáo", "báo cáo hôm nay",
                    "báo cáo tháng 9"):
            self.assertIsNone(agent._ngay_duoc_neu(chu, t), chu)

    def test_bao_cao_ngay_CU_THE_thi_dung_co_NGAY(self):
        """Hoi ngay bat ky -> phai dung --ngay (lay tu Meta), KHONG dung --slot."""
        import agent
        da_chay = []

        class Kq:
            returncode = 0

        cu = agent.subprocess.run
        self.addCleanup(setattr, agent.subprocess, "run", cu)
        agent.subprocess.run = lambda *a, **k: (da_chay.append(a[0]), Kq())[1]

        self._xu_ly(self._tin("báo cáo 15/09"))
        lenh = [str(x) for x in da_chay[0]]
        self.assertIn("--ngay", lenh)
        self.assertIn("2026-09-15", lenh)
        self.assertNotIn("--slot", lenh)
        self.assertIn("15/09/2026", self.gui[0], "phai noi ro dang lay ngay nao")

    def test_tin_tu_nguoi_la_bi_bo_qua(self):
        self._xu_ly(self._tin("tat 120250506886650509", chat=999))
        self.assertEqual(self.gui, [])

    def test_nut_bam_duoc_tra_loi_NGAY(self):
        self._xu_ly(self._nut("tat:120250506886650509"))
        self.assertEqual(self.nut_da_tra_loi, ["cb1"],
                         "phai answerCallbackQuery ngay, khong thi nut quay mai")

    def test_nut_bam_tu_nguoi_la_bi_bo_qua(self):
        self._xu_ly(self._nut("tat:120250506886650509", chat=999))
        self.assertEqual(self.nut_da_tra_loi, [])

    def test_nghe_telegram_bo_qua_tin_hong_khong_nem(self):
        nguoi_truc.lay_tin_moi = lambda env, offset: (
            [None, "chuoi", {}, {"update_id": 5},
             {"update_id": 6, "callback_query": None},
             {"update_id": 7, "message": None}], None)
        self.agent._nghe_telegram(self.env, self.cau_hinh, self.bay_gio,
                                  self.thong_bao, self.tt)      # khong nem
        self.assertEqual(self.gui, [])

    def test_nghe_telegram_cap_nhat_offset(self):
        nguoi_truc.lay_tin_moi = lambda env, offset: (
            [{"update_id": 41}, {"update_id": 47}], None)
        self.agent._nghe_telegram(self.env, self.cau_hinh, self.bay_gio,
                                  self.thong_bao, self.tt)
        self.assertEqual(self.tt["offset"], 48)

    def test_tin_ton_dong_xu_ly_LENH_bo_CAU_HOI(self):
        nguoi_truc.lay_tin_moi = lambda env, offset: ([
            self._tin("tat 120250506886650509"),
            self._tin("hom qua co bao nhieu don?"),
        ], None)
        self.tt["da_doc_ton_dong"] = False
        self.agent._nghe_telegram(self.env, self.cau_hinh, self.bay_gio,
                                  self.thong_bao, self.tt)
        self.assertTrue(self.tt["da_doc_ton_dong"])
        self.assertEqual(self.gui, [], "cau hoi CU khong duoc tra loi")

    def test_nhan_mac_dinh_van_la_Nguoi_truc(self):
        """Khong truyen `nhan` thi cau tra loi giu nguyen nhu truoc."""
        chu = nguoi_truc.tra_loi_tin_nhan(
            "con song khong?", {"REPORT_ACCOUNT_NAME": "Test"}, [8, 12, 17],
            datetime(2026, 10, 1, 9, 0), None, set())
        self.assertIn("Người trực đang chạy", chu)


if __name__ == "__main__":
    unittest.main(verbosity=2)
