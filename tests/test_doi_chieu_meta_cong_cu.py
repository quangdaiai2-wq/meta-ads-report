"""Kiem thu CONG CU DOI CHIEU `doi_chieu_meta.py`. KHONG goi mang.

Cong cu nay thay the viec ma token App le ra lam duoc: tra loi "viec nay ai lam"
khi nhat ky Meta khong phan biet duoc nguoi va may (Dai la EMPLOYEE, khong tao
duoc System User, moi thao tac hien ten chu token ca nhan).
"""
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doi_chieu_meta as dc

GIO_VN = timezone(timedelta(hours=7))
MA = "120250389649480509"
MA2 = "120250204184200509"


def _bg(ma, luc, hanh_dong="tam_dung", ket_qua="thanh cong", nguon_goc=None,
        da_gui=True):
    r = {
        "luc": luc, "che_do": "xin_phep", "ai_lam": "agent nac 2",
        "hanh_dong": hanh_dong,
        "doi_tuong": {"cap": "ad_set", "id": ma, "ten": "Nhom"},
        "da_gui_len_meta": da_gui, "dai_phan_hoi": "tat:" + ma,
        "ket_qua": ket_qua,
    }
    if nguon_goc:
        r["nguon_goc"] = nguon_goc
    return r


def _sk(ma, luc_utc, loai="update_adset_run_status", nguoi=""):
    return {"object_id": ma, "event_time": luc_utc, "event_type": loai,
            "actor_name": nguoi, "actor_id": ""}


class TestKhop(unittest.TestCase):
    """N1–N3: khop theo object_id + cua so +-2 phut, KHONG phu thuoc ten."""

    def test_N1_cung_id_cung_phut_thi_khop(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        meta = [_sk(MA, "2026-10-02T04:46:50+00:00")]      # = 11:46:50 VN
        kq = dc.doi_chieu(so, meta)
        self.assertEqual(len(kq["khop"]), 1)
        self.assertEqual(kq["chi_meta"], [])
        self.assertEqual(kq["chi_agent"], [])

    def test_N2_lech_3_phut_thi_khong_khop(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        meta = [_sk(MA, "2026-10-02T04:50:00+00:00")]      # lech ~3 phut
        kq = dc.doi_chieu(so, meta)
        self.assertEqual(kq["khop"], [])
        self.assertEqual(len(kq["chi_meta"]), 1)
        self.assertEqual(len(kq["chi_agent"]), 1)

    def test_N2_dung_bien_2_phut_van_khop(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        meta = [_sk(MA, "2026-10-02T04:48:55+00:00")]      # dung 2 phut
        self.assertEqual(len(dc.doi_chieu(so, meta)["khop"]), 1)

    def test_N3_meta_ghi_ten_nguoi_van_khop(self):
        """Meta luon ghi ten chu token ca nhan — KHONG duoc lam hong phep khop."""
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        meta = [_sk(MA, "2026-10-02T04:46:50+00:00", nguoi="")]
        kq = dc.doi_chieu(so, meta)
        self.assertEqual(len(kq["khop"]), 1)
        self.assertEqual(kq["khop"][0][1]["actor_name"], "")

    def test_khac_id_thi_khong_khop(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        meta = [_sk(MA2, "2026-10-02T04:46:50+00:00")]
        kq = dc.doi_chieu(so, meta)
        self.assertEqual(kq["khop"], [])
        self.assertEqual(len(kq["chi_meta"]), 1)
        self.assertEqual(len(kq["chi_agent"]), 1)


class TestHaiNguonLech(unittest.TestCase):
    """N4–N5: viec chi co o mot ben."""

    def test_N4_chi_co_o_meta_la_dai_tu_lam(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        meta = [
            _sk(MA, "2026-10-02T04:46:50+00:00"),
            _sk(MA2, "2026-10-03T03:00:00+00:00"),        # Dai tu lam tay
        ]
        kq = dc.doi_chieu(so, meta)
        self.assertEqual(len(kq["khop"]), 1)
        self.assertEqual([s["object_id"] for s in kq["chi_meta"]], [MA2])

    def test_N5_chi_co_trong_so_la_nghi_van(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        meta = []
        kq = dc.doi_chieu(so, meta)
        self.assertEqual([r["doi_tuong"]["id"] for r in kq["chi_agent"]], [MA])

    def test_bang_in_neu_ro_hai_nhom(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        meta = [_sk(MA2, "2026-10-03T03:00:00+00:00")]
        chuoi = dc.in_bang(dc.doi_chieu(so, meta), meta)
        self.assertIn("CHỈ CÓ TRÊN META", chuoi)
        self.assertIn("ĐẠI TỰ LÀM TAY", chuoi)
        self.assertIn("CHỈ CÓ TRONG SỔ AGENT", chuoi)


class TestKhongSap(unittest.TestCase):
    """N6, N8: dau vao xau -> khong nem loi."""

    def test_N6_meta_rong_tra_bang_rong(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        kq = dc.doi_chieu(so, [])
        self.assertEqual(kq["khop"], [])
        self.assertEqual(len(kq["chi_agent"]), 1)
        chuoi = dc.in_bang(kq, [], "loi mang gia dinh")
        self.assertIn("Không đọc được nhật ký Meta", chuoi)

    def test_N6_meta_khong_phai_danh_sach(self):
        kq = dc.doi_chieu([], None)
        self.assertEqual(kq["khop"], [])
        self.assertIsInstance(dc.in_bang(kq, None), str)

    def test_N8_ban_ghi_thieu_luc_hoac_id_bi_bo_qua(self):
        """Ban ghi thieu `luc`, thieu id, hoac `luc` sai dinh dang -> loai het."""
        so = [
            {"da_gui_len_meta": True, "ket_qua": "ok", "doi_tuong": {"id": MA}},
            {"da_gui_len_meta": True, "ket_qua": "ok", "luc": "2026-10-02T11:00:00+07:00",
             "doi_tuong": {}},
            {"luc": "khong-phai-gio", "da_gui_len_meta": True, "ket_qua": "ok",
             "doi_tuong": {"id": MA2}},
        ]
        kq = dc.doi_chieu(so, [])
        # Khong nem loi, va ca ba deu khong the doi chieu => bi loai.
        self.assertEqual(kq["chi_agent"], [])

    def test_N8_ban_ghi_du_du_lieu_thi_giu(self):
        """Doi chung: ban ghi du `luc` + id thi PHAI duoc giu lai."""
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]
        kq = dc.doi_chieu(so, [])
        self.assertEqual(len(kq["chi_agent"]), 1)

    def test_so_file_khong_ton_tai(self):
        self.assertEqual(dc.doc_so_agent("khong/co/file/nay.json"), [])

    def test_so_file_hong(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "hong.json")
            Path(p).write_text("{ khong phai json", encoding="utf-8")
            self.assertEqual(dc.doc_so_agent(p), [])


class TestTrungVaMoCoi(unittest.TestCase):
    """N7, N13, N14: trung so + ban ghi mo coi."""

    def test_N7_canh_bao_trung_so(self):
        so = [
            _bg(MA, "2026-10-02T11:46:55+07:00"),
            _bg(MA, "2026-10-02T11:46:58+07:00"),     # cung phut, cung id
        ]
        kq = dc.doi_chieu(so, [])
        self.assertEqual(len(kq["trung_so"]), 1)
        chuoi = dc.in_bang(kq, [])
        self.assertIn("BẢN GHI TRÙNG", chuoi)

    def test_N13_liet_ke_ban_ghi_mo_coi(self):
        so = [
            _bg(MA, "2026-10-02T11:46:55+07:00", ket_qua=None),   # mo coi
            _bg(MA2, "2026-10-02T13:00:00+07:00"),                # lanh lan
        ]
        kq = dc.doi_chieu(so, [])
        self.assertEqual(len(kq["mo_coi"]), 1)
        self.assertEqual([r["doi_tuong"]["id"] for r in kq["mo_coi"]], [MA])

    def test_N14_ban_ghi_mo_coi_bi_bo_qua_khi_doi_chieu(self):
        """Ban ghi mo coi KHONG duoc bao 'Meta khong nhan' — no la loi so, khac."""
        so = [_bg(MA, "2026-10-02T11:46:55+07:00", ket_qua=None)]
        meta = []
        kq = dc.doi_chieu(so, meta)
        self.assertEqual(kq["chi_agent"], [],
                         "Ban ghi mo coi bi tinh nham la 'chi co trong so'")
        self.assertEqual(len(kq["mo_coi"]), 1)


class TestAnToan(unittest.TestCase):
    """N9: cong cu CHI DOC — khong duoc co duong GHI len Meta."""

    def test_N9_khong_goi_api_post(self):
        nguon = Path(dc.__file__).read_text(encoding="utf-8")
        self.assertNotIn("api_post", nguon,
                         "Cong cu doi chieu KHONG duoc ghi len Meta")
        self.assertNotIn("agent_cong_cu_ghi", nguon)

    def test_N9_khong_gui_telegram(self):
        nguon = Path(dc.__file__).read_text(encoding="utf-8")
        self.assertNotIn("gui_tin_nhan", nguon)
        self.assertNotIn("sendMessage", nguon)

    def test_N9_khong_ghi_file_so(self):
        """Chay doi chieu khong duoc lam doi file so."""
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / "so.json"
            goc = [_bg(MA, "2026-10-02T11:46:55+07:00")]
            import json
            p.write_text(json.dumps(goc, ensure_ascii=False), encoding="utf-8")
            truoc = p.read_bytes()
            dc.doi_chieu(dc.doc_so_agent(str(p)), [])
            dc.in_bang(dc.doi_chieu(dc.doc_so_agent(str(p)), []), [])
            self.assertEqual(p.read_bytes(), truoc, "File so bi thay doi!")


class TestNguonGocTrongBang(unittest.TestCase):
    """N10–N11: bang phai noi ro AI LAM hay DAI LAM."""

    def test_nguon_goc_moi_hien_dung(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00", nguon_goc="agent_tu_hanh")]
        chuoi = dc.in_bang(dc.doi_chieu(so, []), [])
        self.assertIn("MAY TU LAM", chuoi)

    def test_nguon_goc_cu_suy_ra(self):
        """So cu khong co truong nguon_goc -> van phai hien nhan, khong de trong."""
        so = [_bg(MA, "2026-10-02T11:46:55+07:00")]     # khong co nguon_goc
        chuoi = dc.in_bang(dc.doi_chieu(so, []), [])
        self.assertIn("Đại bấm nút", chuoi)

    def test_dai_go_tay_hien_dung(self):
        so = [_bg(MA, "2026-10-02T11:46:55+07:00", nguon_goc="dai_go_tay")]
        chuoi = dc.in_bang(dc.doi_chieu(so, []), [])
        self.assertIn("Đại gõ tay", chuoi)


class TestDocMetaKhongSap(unittest.TestCase):
    """Doc Meta khi thieu cau hinh -> tra loi ro rang, khong nem."""

    def test_thieu_meta_ad_account_id(self):
        ds, ly = dc.doc_nhat_ky_meta(env={})
        self.assertEqual(ds, [])
        self.assertIn("META_AD_ACCOUNT_ID", ly)

    def test_api_get_tra_tuple_khong_phai_dict(self):
        """LOI THAT 03/10/2026: `report.api_get` tra TUPLE `(du_lieu, loi)`.

        Toi da viet cong cu doc `kq["data"]` nhu the no tra dict => im lang bao
        "Meta tra ve du lieu la" MAI MAI, du Meta van chay tot. Bai nay canh
        dung cho do.
        """
        import types
        gia_report = types.ModuleType("report")
        gia_report.api_get = lambda path, params, **kw: (
            {"data": [_sk(MA, "2026-10-02T04:46:50+00:00")]}, None)
        gia_report.load_env = lambda p: {}
        cu = sys.modules.get("report")
        sys.modules["report"] = gia_report
        try:
            ds, ly = dc.doc_nhat_ky_meta(env={"META_AD_ACCOUNT_ID": "act_123", "META_ADS_ACCESS_TOKEN": "tok"})
            self.assertEqual(ly, "")
            self.assertEqual(len(ds), 1)
            self.assertEqual(ds[0]["object_id"], MA)
        finally:
            if cu is None:
                sys.modules.pop("report", None)
            else:
                sys.modules["report"] = cu

    def test_api_get_tra_loi_thi_neu_ro(self):
        """Meta bao loi -> tra loi ro rang, khong nem."""
        import types
        gia_report = types.ModuleType("report")
        gia_report.api_get = lambda path, params, **kw: (
            None, {"message": "(#200) Provide valid app ID", "code": 200})
        gia_report.load_env = lambda p: {}
        cu = sys.modules.get("report")
        sys.modules["report"] = gia_report
        try:
            ds, ly = dc.doc_nhat_ky_meta(env={"META_AD_ACCOUNT_ID": "act_123", "META_ADS_ACCESS_TOKEN": "tok"})
            self.assertEqual(ds, [])
            self.assertIn("Provide valid app ID", ly)
        finally:
            if cu is None:
                sys.modules.pop("report", None)
            else:
                sys.modules["report"] = cu

    def test_chay_offline_khong_goi_meta(self):
        """`chay()` voi env rong van tra chuoi, khong nem."""
        with tempfile.TemporaryDirectory() as t:
            import json
            p = os.path.join(t, "so.json")
            Path(p).write_text(json.dumps([_bg(MA, "2026-10-02T11:46:55+07:00")],
                                          ensure_ascii=False), encoding="utf-8")
            chuoi = dc.chay(p, env={})
            self.assertIn("ĐỐI CHIẾU", chuoi)


if __name__ == "__main__":
    unittest.main(verbosity=2)
