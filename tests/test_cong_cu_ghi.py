# -*- coding: utf-8 -*-
"""KIEM THU module ghi len Meta. Dung mang GIA — khong goi Meta that."""
import io
import json
import unittest
import urllib.error

import agent_cong_cu_ghi as ghi

ENV = {"META_ADS_ACCESS_TOKEN": "token-gia"}
NHOM_OK = "2026 - 09 - 30 - dainq - Scale - Online"
NHOM_LA = "2026 - 09 - 30 - Truong - Scale - Online"


class Base(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self._that = (ghi.api_post, ghi.doc_lai_nhom, ghi.doc_quang_cao)

    def tearDown(self):
        ghi.api_post, ghi.doc_lai_nhom, ghi.doc_quang_cao = self._that


class A_GopBaViec(Base):
    def test_gop_ten_trang_thai_ngan_sach_vao_MOT_lan_goi(self):
        ghi.doc_lai_nhom = lambda env, ma: (
            {"id": ma, "name": NHOM_OK, "status": "ACTIVE", "daily_budget": "400000"}, None)

        def post(path, params, ngu_fn=None):
            self.calls.append((path, dict(params)))
            if len(self.calls) == 1:
                ghi.doc_lai_nhom = lambda e, m: (
                    {"id": m, "name": NHOM_OK + " 0/140 X10", "status": "PAUSED",
                     "daily_budget": "27000"}, None)
            return {"success": True}, None

        ghi.api_post = post
        ok, ly, ct = ghi.tam_dung_va_ha_ngan_sach(
            ENV, "123", 27000, ten_moi=NHOM_OK + " 0/140 X10", ngu_fn=lambda s: None)
        self.assertTrue(ok, ly)
        self.assertEqual(len(self.calls), 1, "phai chi MOT lan goi len Meta")
        _, p = self.calls[0]
        self.assertEqual(p["name"], NHOM_OK + " 0/140 X10")
        self.assertEqual(p["status"], "PAUSED")
        self.assertEqual(p["daily_budget"], "27000")

    def test_khong_co_ten_moi_thi_khong_gui_truong_name(self):
        ghi.doc_lai_nhom = lambda env, ma: (
            {"id": ma, "name": NHOM_OK, "status": "PAUSED", "daily_budget": "27000"}, None)

        def post(path, params, ngu_fn=None):
            self.calls.append((path, dict(params)))
            return {"success": True}, None

        ghi.api_post = post
        ok, ly, _ = ghi.tam_dung_va_ha_ngan_sach(ENV, "123", 27000,
                                                 ngu_fn=lambda s: None)
        self.assertTrue(ok, ly)
        self.assertNotIn("name", self.calls[0][1])

    def test_doc_lai_khong_khop_thi_bao_that_bai(self):
        ghi.doc_lai_nhom = lambda env, ma: (
            {"id": ma, "name": NHOM_OK, "status": "ACTIVE", "daily_budget": "400000"}, None)
        ghi.api_post = lambda p, q, ngu_fn=None: ({"success": True}, None)
        ok, ly, _ = ghi.tam_dung_va_ha_ngan_sach(ENV, "123", 27000,
                                                 ngu_fn=lambda s: None)
        self.assertFalse(ok, "doc lai van ACTIVE thi phai bao that bai")
        self.assertIn("KHONG khop", ly)


class B_HangRaoPhamVi(Base):
    def test_nhom_ngoai_pham_vi_thi_KHONG_doi_ten(self):
        ghi.doc_lai_nhom = lambda env, ma: (
            {"id": ma, "name": NHOM_LA, "status": "ACTIVE", "daily_budget": "400000"}, None)
        ghi.api_post = lambda p, q, ngu_fn=None: self.calls.append(q) or ({"success": True}, None)
        ok, ly, _ = ghi.tam_dung_va_ha_ngan_sach(ENV, "123", 27000,
                                                 ngu_fn=lambda s: None)
        self.assertFalse(ok)
        self.assertIn("phạm vi", ly)
        self.assertEqual(self.calls, [], "KHONG duoc gui lenh nao len Meta")

    def test_tat_quang_cao_nhom_ngoai_pham_vi_thi_tu_choi(self):
        ghi.doc_lai_nhom = lambda env, ma: ({"id": ma, "name": NHOM_LA}, None)
        goi = []
        ghi.api_post = lambda p, q, ngu_fn=None: goi.append(q) or ({"success": True}, None)
        ok, ly, _ = ghi.tat_quang_cao(ENV, "123", ngu_fn=lambda s: None)
        self.assertFalse(ok)
        self.assertIn("phạm vi", ly)
        self.assertEqual(goi, [], "KHONG duoc dung vao quang cao")


class C_TatQuangCao(Base):
    def _dat(self, ads_truoc, ads_sau):
        ghi.doc_lai_nhom = lambda env, ma: ({"id": ma, "name": NHOM_OK}, None)
        hang = [ads_truoc, ads_sau]
        ghi.doc_quang_cao = lambda env, ma: (hang.pop(0), None)

    def test_tat_het_quang_cao(self):
        self._dat([{"id": "ad1", "status": "ACTIVE"}, {"id": "ad2", "status": "ACTIVE"}],
                  [{"id": "ad1", "status": "PAUSED"}, {"id": "ad2", "status": "PAUSED"}])
        ghi.api_post = lambda p, q, ngu_fn=None: ({"success": True}, None)
        ok, ly, ct = ghi.tat_quang_cao(ENV, "123", ngu_fn=lambda s: None)
        self.assertTrue(ok, ly)
        self.assertEqual(len(ct["da_tat"]), 2)
        self.assertEqual(ct["con_chay"], [])

    def test_quang_cao_da_tat_san_thi_KHONG_goi_lai(self):
        self._dat([{"id": "ad1", "status": "PAUSED"}],
                  [{"id": "ad1", "status": "PAUSED"}])
        goi = []
        ghi.api_post = lambda p, q, ngu_fn=None: goi.append(q) or ({"success": True}, None)
        ok, ly, ct = ghi.tat_quang_cao(ENV, "123", ngu_fn=lambda s: None)
        self.assertTrue(ok, ly)
        self.assertEqual(goi, [], "da tat san thi khong goi len Meta nua")
        self.assertEqual(ct["da_tat"][0]["ket_qua"], "da tat san")

    def test_con_quang_cao_chua_tat_thi_bao_that_bai(self):
        self._dat([{"id": "ad1", "status": "ACTIVE"}],
                  [{"id": "ad1", "status": "ACTIVE"}])
        ghi.api_post = lambda p, q, ngu_fn=None: ({"success": True}, None)
        ok, ly, _ = ghi.tat_quang_cao(ENV, "123", ngu_fn=lambda s: None)
        self.assertFalse(ok)
        self.assertIn("chua tat", ly)

    def test_nhom_khong_co_quang_cao_nao_van_thanh_cong(self):
        ghi.doc_lai_nhom = lambda env, ma: ({"id": ma, "name": NHOM_OK}, None)
        ghi.doc_quang_cao = lambda env, ma: ([], None)
        ok, ly, _ = ghi.tat_quang_cao(ENV, "123", ngu_fn=lambda s: None)
        self.assertTrue(ok, ly)


class D_ChoKhiBiChan(unittest.TestCase):
    def _loi_613(self):
        body = json.dumps({"error": {"message": "rate limit", "code": 613}}).encode()
        return urllib.error.HTTPError("u", 400, "Bad", {}, io.BytesIO(body))

    def test_gap_613_thi_cho_LAU_roi_thu_lai(self):
        da_cho = []
        lan = {"n": 0}
        that = ghi.urllib.request.urlopen

        def gia(req, timeout=None):
            lan["n"] += 1
            if lan["n"] == 1:
                raise self._loi_613()
            return io.BytesIO(json.dumps({"success": True}).encode())

        ghi.urllib.request.urlopen = gia
        self.addCleanup(setattr, ghi.urllib.request, "urlopen", that)
        kq, loi = ghi.api_post("123", {"a": "b"}, ngu_fn=da_cho.append)
        self.assertIsNone(loi, str(loi))
        self.assertEqual(kq, {"success": True})
        self.assertEqual(da_cho, [ghi.CHO_KHI_BI_CHAN[0]],
                         "gap 613 phai cho dung CHO_KHI_BI_CHAN, KHONG dung 5/15 giay")
        self.assertGreaterEqual(ghi.CHO_KHI_BI_CHAN[0], 30,
                                "cho 5-15 giay KHONG du — da kiem chung that")

    def test_loi_khac_thi_cho_ngan_nhu_cu(self):
        da_cho = []
        lan = {"n": 0}
        that = ghi.urllib.request.urlopen

        def gia(req, timeout=None):
            lan["n"] += 1
            if lan["n"] == 1:
                body = json.dumps({"error": {"message": "server", "code": 17}}).encode()
                raise urllib.error.HTTPError("u", 500, "Bad", {}, io.BytesIO(body))
            return io.BytesIO(json.dumps({"success": True}).encode())

        ghi.urllib.request.urlopen = gia
        self.addCleanup(setattr, ghi.urllib.request, "urlopen", that)
        ghi.api_post("123", {"a": "b"}, ngu_fn=da_cho.append)
        self.assertEqual(da_cho, [ghi.report.CHO_TRUOC_KHI_THU_LAI[0]])


if __name__ == "__main__":
    unittest.main(verbosity=2)
