"""Kiem thu ai.py - lop AI cua bao cao Meta Ads. KHONG goi mang."""
import io
import json
import unittest
import urllib.error

import ai


STATS = {
    "total_campaigns": 19,
    "totals": {
        "spend": 7034942.0,
        "msg": 43,
        "contact": 40,
        "order": 15,
        "purchase": 15,
        "payment": 15,
        "comment": 0,
    },
    "all": [
        {"id": "111", "name": "dainq - camp A", "spend": 3000000.0, "purchase": 9},
        {"id": "222", "name": "dainq - camp B", "spend": 4034942.0, "purchase": 6},
    ],
    "good": [{"id": "111", "name": "dainq - camp A", "spend": 3000000.0, "purchase": 9}],
    "bad": [{"id": "222", "name": "dainq - camp B", "spend": 4034942.0, "purchase": 6}],
}

KY_TRUOC_CO_SO = {
    "tong": {"spend": 6100000.0, "msg": 95, "contact": 31, "order": 7,
             "purchase": 11, "payment": 9, "comment": 2},
    "so_ngay": 7,
}

KY_TRUOC_RONG = {
    "tong": {"spend": 0.0, "msg": 0, "contact": 0, "order": 0,
             "purchase": 0, "payment": 0, "comment": 0},
    "so_ngay": 0,
}

# Co so ngay nhung tong bang 0: truong hop rieng, khong chia phan tram duoc.
KY_TRUOC_CO_NGAY_TONG_0 = {
    "tong": {"spend": 0.0, "msg": 0, "contact": 0, "order": 0,
             "purchase": 0, "payment": 0, "comment": 0},
    "so_ngay": 3,
}


class TestBangSoSanh(unittest.TestCase):
    """CODE tinh bang so sanh. AI KHONG duoc tu tinh."""

    def test_tinh_dung_chenh_lech_tang(self):
        b = ai.bang_so_sanh(STATS, KY_TRUOC_CO_SO)
        self.assertIn("7.034.942", b)
        self.assertIn("6.100.000", b)
        self.assertIn("+934.942", b)
        self.assertIn("+15%", b)

    def test_tinh_dung_chenh_lech_giam(self):
        b = ai.bang_so_sanh(STATS, KY_TRUOC_CO_SO)
        self.assertIn("-52", b)
        self.assertIn("-55%", b)

    def test_ky_truoc_bang_0_thi_ghi_ro(self):
        b = ai.bang_so_sanh(STATS, KY_TRUOC_CO_NGAY_TONG_0)
        self.assertIn("(ky truoc bang 0)", b)

    def test_khong_co_ky_truoc_thi_ghi_khong_so_sanh(self):
        b = ai.bang_so_sanh(STATS, None)
        self.assertIn("(khong so sanh)", b)
        self.assertNotIn("+", b)

    def test_so_ngay_0_cung_la_khong_co_ky_truoc(self):
        b = ai.bang_so_sanh(STATS, KY_TRUOC_RONG)
        self.assertIn("(khong so sanh)", b)


class TestSoanPrompt(unittest.TestCase):
    def test_co_bang_so_lieu(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "bao cao ngay 27/09/2026")
        self.assertIn("BANG SO LIEU", p)
        self.assertIn("7.034.942", p)

    def test_co_ten_camp(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("dainq - camp A", p)

    def test_co_boi_canh(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "bao cao ngay 27/09/2026")
        self.assertIn("bao cao ngay 27/09/2026", p)

    def test_khong_co_ky_truoc_thi_bang_ghi_khong_so_sanh(self):
        p = ai.soan_prompt(STATS, None, "x")
        self.assertIn("(khong so sanh)", p)

    def test_co_ky_truoc_thi_KHONG_ghi_khong_so_sanh(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertNotIn("(khong so sanh)", p)

    def test_prompt_cam_AI_tu_tinh(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("Không tự tính", p)

    def test_prompt_bat_buoc_viet_co_dau(self):
        # Gemini bat chuoc giong van cua cau lenh. Cau lenh khong dau thi no
        # tra ve khong dau (da gap that ~50% so lan ngay 28/09/2026), rat kho
        # doc. Quy tac nay khong duoc xoa.
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("CÓ DẤU", p)

    def test_stats_rong_khong_no(self):
        p = ai.soan_prompt({}, None, "x")
        self.assertIsInstance(p, str)
        self.assertTrue(p)

    def test_khong_nhan_env_nen_khong_the_lo_token(self):
        # soan_prompt KHONG co tham so env -> ve cau truc khong the lo token.
        import inspect
        self.assertNotIn("env", inspect.signature(ai.soan_prompt).parameters)


class TestDocCauTraLoi(unittest.TestCase):
    def _goi(self, text):
        return {"candidates": [{"content": {"parts": [{"text": text}]}}]}

    def test_boc_duoc_chu(self):
        self.assertEqual(ai.doc_cau_tra_loi(self._goi("  Nam camp tot.  ")), "Nam camp tot.")

    def test_json_hong_tra_ve_rong(self):
        self.assertEqual(ai.doc_cau_tra_loi({"candidates": []}), "")

    def test_thieu_truong_tra_ve_rong(self):
        self.assertEqual(ai.doc_cau_tra_loi({}), "")

    def test_khong_phai_dict_tra_ve_rong(self):
        self.assertEqual(ai.doc_cau_tra_loi(None), "")


class TestGoiGemini(unittest.TestCase):
    def test_thieu_chia_khoa_thi_bao_loi_ro(self):
        text, loi = ai.goi_gemini({}, "hoi gi do")
        self.assertIsNone(text)
        self.assertIn("GEMINI_API_KEY", loi)

    def test_goi_thanh_cong(self):
        def gia(url, payload, timeout):
            return {"candidates": [{"content": {"parts": [{"text": "Nhan dinh thu."}]}}]}

        text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertEqual(text, "Nhan dinh thu.")
        self.assertIsNone(loi)

    def test_mang_loi_thi_tra_ve_loi_chu_khong_nem(self):
        def gia(url, payload, timeout):
            raise OSError("mat mang")

        text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertIn("mat mang", loi)

    def test_ai_tra_rong_thi_coi_nhu_loi(self):
        def gia(url, payload, timeout):
            return {"candidates": []}

        text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertTrue(loi)

    def test_dung_model_trong_env(self):
        da_goi = []

        def gia(url, payload, timeout):
            da_goi.append(url)
            return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

        ai.goi_gemini({"GEMINI_API_KEY": "k", "GEMINI_MODEL": "model-rieng"},
                      "x", goi_mang_fn=gia)
        self.assertIn("model-rieng", da_goi[0])

    def test_gap_503_thi_thu_lai_mot_lan(self):
        # Gemini thinh thoang tra 503 (qua tai). Da gap that ngay 28/09/2026.
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            if dem["n"] == 1:
                raise urllib.error.HTTPError(url, 503, "qua tai", {}, None)
            return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

        cu = ai.CHO_GIUA_HAI_LAN
        ai.CHO_GIUA_HAI_LAN = 0
        try:
            text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        finally:
            ai.CHO_GIUA_HAI_LAN = cu
        self.assertEqual(text, "ok")
        self.assertIsNone(loi)
        self.assertEqual(dem["n"], 2)

    def test_gap_503_lien_tuc_thi_bo_cuoc_chu_khong_lap_vo_han(self):
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            raise urllib.error.HTTPError(url, 503, "qua tai", {}, None)

        cu = ai.CHO_GIUA_HAI_LAN
        ai.CHO_GIUA_HAI_LAN = 0
        try:
            text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        finally:
            ai.CHO_GIUA_HAI_LAN = cu
        self.assertIsNone(text)
        self.assertIn("503", loi)
        # Phai thu DUNG so lan da dinh, khong it hon (mat nhan dinh oan) va
        # khong nhieu hon (bao cao bi tre).
        self.assertEqual(dem["n"], ai.SO_LAN_THU_LAI + 1)

    def test_loi_400_thi_KHONG_thu_lai(self):
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            raise urllib.error.HTTPError(url, 400, "key sai", {}, None)

        text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertEqual(dem["n"], 1)

    def test_loi_429_thi_ghi_ro_ly_do_bang_tieng_Viet(self):
        # Gemini tra 429 kem ly do trong phan than loi. Phai dich ra tieng
        # Viet, khong de Dai doc mot dong "HTTP 429" tro troi.
        def gia(url, payload, timeout):
            than = io.BytesIO(json.dumps({
                "error": {"status": "RESOURCE_EXHAUSTED",
                          "message": "You exceeded your current quota"}
            }).encode("utf-8"))
            raise urllib.error.HTTPError(url, 429, "quota", {}, than)

        cu = ai.CHO_GIUA_HAI_LAN
        ai.CHO_GIUA_HAI_LAN = 0
        try:
            text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        finally:
            ai.CHO_GIUA_HAI_LAN = cu
        self.assertIsNone(text)
        self.assertIn("429", loi)
        self.assertIn("het han muc", loi)
        self.assertIn("RESOURCE_EXHAUSTED", loi)

    def test_loi_404_thi_chi_dung_ten_model(self):
        def gia(url, payload, timeout):
            raise urllib.error.HTTPError(url, 404, "not found", {}, None)

        text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertIn("ten model", loi)

    def test_ma_loi_la_khong_no(self):
        # Ma loi khong nam trong bang dich, va phan than khong doc duoc.
        def gia(url, payload, timeout):
            raise urllib.error.HTTPError(url, 418, "teapot", {}, None)

        text, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertEqual(loi, "HTTP 418")


class TestVietNhanDinh(unittest.TestCase):
    def test_thanh_cong(self):
        def gia(url, payload, timeout):
            return {"candidates": [{"content": {"parts": [{"text": "Ba cau nhan dinh."}]}}]}

        text, loi = ai.viet_nhan_dinh(STATS, KY_TRUOC_CO_SO, "x",
                                      env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertEqual(text, "Ba cau nhan dinh.")
        self.assertIsNone(loi)

    def test_loi_thi_tra_ve_loi_chu_khong_nem(self):
        def gia(url, payload, timeout):
            raise OSError("het han muc")

        text, loi = ai.viet_nhan_dinh(STATS, None, "x",
                                      env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertIn("het han muc", loi)

    def test_stats_rong_van_khong_no(self):
        def gia(url, payload, timeout):
            return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

        text, loi = ai.viet_nhan_dinh({}, None, "x",
                                      env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertEqual(text, "ok")
        self.assertIsNone(loi)


if __name__ == "__main__":
    unittest.main()
