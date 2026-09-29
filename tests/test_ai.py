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
        {"id": "111", "name": "dainq - camp A", "spend": 3000000.0, "purchase": 9,
         "cpr": 333333.33},
        {"id": "222", "name": "dainq - camp B", "spend": 4034942.0, "purchase": 6,
         "cpr": 672490.33},
        {"id": "333", "name": "dainq - camp C", "spend": 500000.0, "purchase": 0,
         "cpr": None},
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

    def test_prompt_co_chi_phi_moi_don(self):
        # AI phai duoc CHO SAN chi phi moi don, khong duoc tu chia.
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("chi phi moi don", p)
        self.assertIn("333.333", p)

    def test_camp_0_don_thi_ghi_ro_chua_co_don(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("chua co don", p)

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


# ============================================================================
# GIAI DOAN 4 - PHAN HOI DAP
# ============================================================================


def _content_chu(text):
    return {"parts": [{"text": text}], "role": "model"}


def _content_goi_cong_cu(ten, args):
    return {"parts": [{"functionCall": {"name": ten, "args": args}}],
            "role": "model"}


def _kq_gemini(content):
    return {"candidates": [{"content": content}]}


class BoCongCuGia:
    """Bo cong cu gia: ghi lai moi lan duoc goi, tra ket qua tu dinh san."""

    def __init__(self, ket_qua=None, loi=None):
        self.ket_qua = ket_qua or {}
        self.loi = loi
        self.da_goi = []

    def khai_bao(self):
        return [{"functionDeclarations": [
            {"name": "lay_khoang", "description": "x",
             "parameters": {"properties": {}}}]}]

    def thuc_thi(self, ten, args):
        self.da_goi.append((ten, args))
        if self.loi:
            raise self.loi
        return self.ket_qua.get(ten, {"ok": True})


class TestBocContent(unittest.TestCase):
    def test_boc_duoc_chu(self):
        chu, goi = ai.boc_content(_content_chu("Xin chao"))
        self.assertEqual(chu, "Xin chao")
        self.assertIsNone(goi)

    def test_boc_duoc_function_call(self):
        chu, goi = ai.boc_content(_content_goi_cong_cu("lay_khoang", {"tu": "a"}))
        self.assertEqual(chu, "")
        self.assertEqual(goi["name"], "lay_khoang")
        self.assertEqual(goi["args"], {"tu": "a"})

    def test_content_rong_tra_ve_rong(self):
        self.assertEqual(ai.boc_content({}), ("", None))
        self.assertEqual(ai.boc_content(None), ("", None))

    def test_uu_tien_chu_khi_co_ca_hai(self):
        c = {"parts": [{"text": "Day la cau tra loi"},
                       {"functionCall": {"name": "x", "args": {}}}]}
        chu, goi = ai.boc_content(c)
        self.assertEqual(chu, "Day la cau tra loi")
        self.assertIsNotNone(goi)


class TestSoanPromptHoiDap(unittest.TestCase):
    def test_prompt_co_cau_hoi(self):
        self.assertIn("camp nao te nhat?", ai.soan_prompt_hoi_dap("camp nao te nhat?"))

    def test_prompt_co_moc_thoi_gian(self):
        p = ai.soan_prompt_hoi_dap("x", "Hôm nay: 29/09/2026")
        self.assertIn("29/09/2026", p)

    def test_prompt_bat_buoc_viet_co_dau(self):
        self.assertIn("CÓ DẤU", ai.soan_prompt_hoi_dap("x"))

    def test_prompt_cam_markdown(self):
        self.assertIn("KHÔNG dùng dấu sao", ai.soan_prompt_hoi_dap("x"))

    def test_prompt_khong_nhan_env(self):
        import inspect
        tham_so = inspect.signature(ai.soan_prompt_hoi_dap).parameters
        self.assertNotIn("env", tham_so)


class TestChonModelHoiDap(unittest.TestCase):
    def test_mac_dinh_dung_model_da_kiem_chung(self):
        self.assertEqual(ai._chon_model_hoi_dap({}),
                         ["gemini-3.8-flash", "gemini-3.5-flash"])

    def test_doc_duoc_tu_env(self):
        ds = ai._chon_model_hoi_dap({"GEMINI_MODEL_HOI_DAP": "model-a"})
        self.assertEqual(ds[0], "model-a")

    def test_model_du_phong_khac_model_chinh_thi_them_vao(self):
        ds = ai._chon_model_hoi_dap({"GEMINI_MODEL_HOI_DAP": "a",
                                     "GEMINI_MODEL_HOI_DAP_DU_PHONG": "b"})
        self.assertEqual(ds, ["a", "b"])

    def test_du_phong_trung_chinh_thi_khong_them(self):
        ds = ai._chon_model_hoi_dap({"GEMINI_MODEL_HOI_DAP": "a",
                                     "GEMINI_MODEL_HOI_DAP_DU_PHONG": "a"})
        self.assertEqual(ds, ["a"])


class TestGoiGeminiCongCu(unittest.TestCase):
    def setUp(self):
        # Tat cho giua hai lan thu de kiem thu khong phai ngoi cho.
        cu = ai.CHO_GIUA_HAI_LAN
        ai.CHO_GIUA_HAI_LAN = 0
        self.addCleanup(lambda: setattr(ai, "CHO_GIUA_HAI_LAN", cu))

    def _goi(self, khai_bao=None, goi_mang_fn=None, env=None):
        return ai.goi_gemini_cong_cu(
            env or {"GEMINI_API_KEY": "k"},
            [{"role": "user", "parts": [{"text": "x"}]}],
            khai_bao_cong_cu=khai_bao, goi_mang_fn=goi_mang_fn)

    def test_gui_kem_tools_khi_co_khai_bao(self):
        thay = {}

        def gia(url, payload, timeout):
            thay.update(payload)
            return _kq_gemini(_content_chu("ok"))

        self._goi(khai_bao=[{"functionDeclarations": []}], goi_mang_fn=gia)
        self.assertIn("tools", thay)

    def test_khong_gui_tools_khi_khong_khai_bao(self):
        thay = {}

        def gia(url, payload, timeout):
            thay.update(payload)
            return _kq_gemini(_content_chu("ok"))

        self._goi(goi_mang_fn=gia)
        self.assertNotIn("tools", thay)

    def test_co_maxOutputTokens(self):
        thay = {}

        def gia(url, payload, timeout):
            thay.update(payload)
            return _kq_gemini(_content_chu("ok"))

        self._goi(goi_mang_fn=gia)
        self.assertEqual(thay["generationConfig"]["maxOutputTokens"],
                         ai.TOI_DA_TOKEN_TRA_LOI)

    def test_dung_model_hoi_dap_khong_dung_model_bao_cao(self):
        thay = {"url": None}

        def gia(url, payload, timeout):
            thay["url"] = url
            return _kq_gemini(_content_chu("ok"))

        ai.goi_gemini_cong_cu(
            {"GEMINI_API_KEY": "k", "GEMINI_MODEL": "model-bao-cao"},
            [{"role": "user", "parts": [{"text": "x"}]}], goi_mang_fn=gia)
        self.assertIn("gemini-3.8-flash", thay["url"])
        self.assertNotIn("model-bao-cao", thay["url"])

    def test_503_thi_thu_model_du_phong(self):
        dem = {"n": 0}
        nguong = ai.SO_LAN_THU_LAI + 1

        def gia(url, payload, timeout):
            dem["n"] += 1
            if dem["n"] <= nguong:
                raise urllib.error.HTTPError(url, 503, "qua tai", {}, io.BytesIO(b"{}"))
            return _kq_gemini(_content_chu("ok"))

        content, loi = self._goi(goi_mang_fn=gia)
        self.assertIsNone(loi)
        self.assertIsNotNone(content)
        self.assertEqual(dem["n"], nguong + 1)

    def test_ca_hai_model_deu_loi_thi_tra_loi(self):
        def gia(url, payload, timeout):
            raise urllib.error.HTTPError(url, 404, "khong co model", {},
                                         io.BytesIO(b"{}"))

        content, loi = self._goi(goi_mang_fn=gia)
        self.assertIsNone(content)
        self.assertIn("404", loi)

    def test_sai_cau_truc_thi_tra_loi(self):
        def gia(url, payload, timeout):
            return {"khong_co_candidates": True}

        content, loi = self._goi(goi_mang_fn=gia)
        self.assertIsNone(content)
        self.assertIn("sai cau truc", loi)


class TestTraLoi(unittest.TestCase):
    def setUp(self):
        cu = ai.CHO_GIUA_HAI_LAN
        ai.CHO_GIUA_HAI_LAN = 0
        self.addCleanup(lambda: setattr(ai, "CHO_GIUA_HAI_LAN", cu))

    def _env(self, **kw):
        e = {"GEMINI_API_KEY": "k"}
        e.update(kw)
        return e

    def test_ai_tra_loi_ngay_khong_goi_cong_cu(self):
        bo = BoCongCuGia()

        def gia(url, payload, timeout):
            return _kq_gemini(_content_chu("Chi tieu hom qua la 7.034.942 dong."))

        chu, loi = ai.tra_loi("hom qua the nao?", bo, env=self._env(),
                              goi_mang_fn=gia)
        self.assertIn("7.034.942", chu)
        self.assertIsNone(loi)
        self.assertEqual(bo.da_goi, [])

    def test_ai_xin_cong_cu_roi_tra_loi(self):
        bo = BoCongCuGia({"lay_khoang": {"tong": {"spend": 100}}})
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            if dem["n"] == 1:
                return _kq_gemini(_content_goi_cong_cu(
                    "lay_khoang", {"tu": "2026-09-27", "den": "2026-09-28"}))
            return _kq_gemini(_content_chu("Tong chi tieu la 100 dong."))

        chu, loi = ai.tra_loi("tuan nay?", bo, env=self._env(), goi_mang_fn=gia)
        self.assertIn("100", chu)
        self.assertEqual(len(bo.da_goi), 1)
        self.assertEqual(bo.da_goi[0][0], "lay_khoang")
        self.assertEqual(bo.da_goi[0][1],
                         {"tu": "2026-09-27", "den": "2026-09-28"})

    def test_ket_qua_cong_cu_duoc_gui_lai_cho_ai(self):
        bo = BoCongCuGia({"lay_khoang": {"tong": {"spend": 987654}}})
        thay = {"payload": None}
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            if dem["n"] == 1:
                return _kq_gemini(_content_goi_cong_cu(
                    "lay_khoang", {"tu": "a", "den": "b"}))
            thay["payload"] = payload
            return _kq_gemini(_content_chu("xong"))

        ai.tra_loi("?", bo, env=self._env(), goi_mang_fn=gia)
        chuoi = json.dumps(thay["payload"], ensure_ascii=False)
        self.assertIn("functionResponse", chuoi)
        self.assertIn("987654", chuoi)

    def test_het_luot_thi_luot_cuoi_khong_kem_tools(self):
        bo = BoCongCuGia()
        ds_tools = []

        def gia(url, payload, timeout):
            ds_tools.append("tools" in payload)
            return _kq_gemini(_content_goi_cong_cu("lay_khoang", {"tu": "a"}))

        chu, loi = ai.tra_loi("?", bo, env=self._env(), goi_mang_fn=gia)
        self.assertIsNone(chu)
        self.assertEqual(len(ds_tools), ai.TOI_DA_LUOT_CONG_CU + 1)
        self.assertTrue(all(ds_tools[:-1]))
        self.assertFalse(ds_tools[-1])

    def test_het_luot_van_khong_tra_loi_thi_bao_loi(self):
        bo = BoCongCuGia()

        def gia(url, payload, timeout):
            return _kq_gemini(_content_goi_cong_cu("lay_khoang", {}))

        chu, loi = ai.tra_loi("?", bo, env=self._env(), goi_mang_fn=gia)
        self.assertIsNone(chu)
        self.assertIn("qua nhieu luot", loi)

    def test_cong_cu_loi_khong_lam_chet_vong_lap(self):
        bo = BoCongCuGia(loi=RuntimeError("no ra"))
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            if dem["n"] == 1:
                return _kq_gemini(_content_goi_cong_cu("lay_khoang", {}))
            return _kq_gemini(_content_chu("Xin loi, khong lay duoc so."))

        chu, loi = ai.tra_loi("?", bo, env=self._env(), goi_mang_fn=gia)
        self.assertIn("Xin loi", chu)

    def test_ai_loi_mang_tra_ve_loi(self):
        bo = BoCongCuGia()

        def gia(url, payload, timeout):
            raise OSError("mat mang")

        chu, loi = ai.tra_loi("?", bo, env=self._env(), goi_mang_fn=gia)
        self.assertIsNone(chu)
        self.assertIn("mat mang", loi)

    def test_bo_cong_cu_hong_thi_tra_loi_chu_khong_nem(self):
        class BoHong:
            def khai_bao(self):
                raise RuntimeError("khai bao hong")

        chu, loi = ai.tra_loi("?", BoHong(), env=self._env(),
                              goi_mang_fn=lambda *a: None)
        self.assertIsNone(chu)
        self.assertIn("khai bao", loi)

    def test_thieu_chia_khoa_tra_ve_loi(self):
        chu, loi = ai.tra_loi("?", BoCongCuGia(), env={})
        self.assertIsNone(chu)
        self.assertIn("GEMINI_API_KEY", loi)

    def test_khong_co_cong_cu_van_tra_loi_duoc(self):
        def gia(url, payload, timeout):
            return _kq_gemini(_content_chu("Tra loi khong can cong cu."))

        chu, loi = ai.tra_loi("?", None, env=self._env(), goi_mang_fn=gia)
        self.assertIn("khong can cong cu", chu)

    def test_khong_gui_token_cho_ai(self):
        bo = BoCongCuGia()
        thay = {"payload": None}

        def gia(url, payload, timeout):
            thay["payload"] = payload
            return _kq_gemini(_content_chu("ok"))

        ai.tra_loi("hoi gi do", bo, env=self._env(GEMINI_API_KEY="BIMAT123"),
                   moc_tg="Hom nay 29/09/2026", goi_mang_fn=gia)
        self.assertNotIn("BIMAT123",
                         json.dumps(thay["payload"], ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
