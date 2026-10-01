"""Kiem thu ai.py - lop AI cua bao cao Meta Ads. KHONG goi mang."""
import io
import json
import unittest
import urllib.error

import ai


# Tat thoi gian cho giua hai lan thu cho TOAN BO file nay.
#
# Nhieu bai kiem thu gia lap loi mang / het thoi gian cho, va tu 29/09/2026
# ai.py THU LAI ca nhung loi do (dung - do la loi tam thoi). De nguyen
# CHO_GIUA_HAI_LAN = 5 thi moi bai nhu vay phai ngoi cho ~10 giay, lam ca file
# cham them ~20 giay ma khong kiem them duoc gi.
_CHO_GIUA_HAI_LAN_CU = None


def setUpModule():
    global _CHO_GIUA_HAI_LAN_CU
    _CHO_GIUA_HAI_LAN_CU = ai.CHO_GIUA_HAI_LAN
    ai.CHO_GIUA_HAI_LAN = 0


def tearDownModule():
    if _CHO_GIUA_HAI_LAN_CU is not None:
        ai.CHO_GIUA_HAI_LAN = _CHO_GIUA_HAI_LAN_CU


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

    def test_PHAI_co_dong_chi_phi_moi_don(self):
        """Loi that 01/10/2026: bang cu thieu dong nay.

        Ngay 30/09 moi dong khac deu GIAM (chi tieu -63%, tin nhan -60%, don
        hang -52%) nen AI viet "chi phi moi don khong may tich cuc, hieu qua
        kem" — trong khi chi phi moi don GIAM 22%, tuc moi don RE HON.
        Mot dong thieu lam ca ban nhan dinh sai.
        """
        b = ai.bang_so_sanh(
            {"totals": {"spend": 6756895, "purchase": 25}},
            {"tong": {"spend": 18122527, "purchase": 52}, "so_ngay": 1})
        self.assertIn("chi phi moi don (dong)", b)
        self.assertIn("270.276", b)
        self.assertIn("348.510", b)
        self.assertIn("RE HON (tot len)", b)

    def test_chi_phi_moi_don_dat_hon_thi_ghi_ro_chieu_xau(self):
        b = ai.bang_so_sanh(
            {"totals": {"spend": 500000, "purchase": 1}},
            {"tong": {"spend": 100000, "purchase": 1}, "so_ngay": 1})
        self.assertIn("DAT HON (xau di)", b)

    def test_chua_co_don_thi_khong_so_sanh_chi_phi(self):
        b = ai.bang_so_sanh(
            {"totals": {"spend": 100000, "purchase": 0}},
            {"tong": {"spend": 100000, "purchase": 5}, "so_ngay": 1})
        self.assertIn("(chua co don)", b)


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


class TestModelDuPhongChoNhanDinh(unittest.TestCase):
    """Model bao cao hong thi phai thu model du phong.

    Loi THAT ngay 29/09/2026: `gemini-3.6-flash` tra HTTP 503 BA LAN LIEN TIEP
    trong buoi chieu (12:00, 15:48, 15:49). Moi lan da thu lai 3 luot theo
    SO_LAN_THU_LAI ma van hong. Do tung model mot thi thay `gemini-3.5-flash`
    VAN CHAY TOT. Khong co du phong thi bao cao mat phan nhan dinh suot nhieu gio.
    """

    def _gia_theo_model(self, model_hong, so_lan_hong=None):
        """Ham goi mang gia: hong voi `model_hong`, thanh cong voi model khac.

        Tra ve (ham_gia, danh_sach_model_da_goi).
        """
        da_goi = []

        def gia(url, payload, timeout):
            for m in ("gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.8-flash"):
                if f"/{m}:" in url:
                    da_goi.append(m)
                    if m == model_hong:
                        raise urllib.error.HTTPError(url, 503, "qua tai", {}, None)
                    return {"candidates": [{"content": {"parts": [{"text": "Nhan dinh du phong."}]}}]}
            raise AssertionError(f"URL khong nhan ra model nao: {url}")

        return gia, da_goi

    def test_503_o_model_chinh_thi_dung_model_du_phong(self):
        gia, da_goi = self._gia_theo_model("gemini-3.6-flash")
        text, loi = ai.viet_nhan_dinh(
            STATS, None, "x", env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertEqual(text, "Nhan dinh du phong.")
        self.assertIsNone(loi)
        self.assertIn("gemini-3.5-flash", da_goi)

    def test_ca_hai_model_deu_hong_thi_loi_ghi_ro_CA_HAI(self):
        """Dai doc phai biet da thu nhung model nao, khong chi model cuoi."""
        def gia(url, payload, timeout):
            raise urllib.error.HTTPError(url, 503, "qua tai", {}, None)

        text, loi = ai.viet_nhan_dinh(
            STATS, None, "x", env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertIsNone(text)
        self.assertIn(ai.MODEL_MAC_DINH, loi)
        self.assertIn(ai.MODEL_BAO_CAO_DU_PHONG_MAC_DINH, loi)

    def test_mac_dinh_la_model_chinh_roi_model_du_phong(self):
        self.assertEqual(
            ai.chon_model_bao_cao({}),
            [ai.MODEL_MAC_DINH, ai.MODEL_BAO_CAO_DU_PHONG_MAC_DINH])

    def test_doi_duoc_model_chinh_bang_env(self):
        ds = ai.chon_model_bao_cao({"GEMINI_MODEL": "model-rieng"})
        self.assertEqual(ds[0], "model-rieng")

    def test_doi_duoc_model_du_phong_bang_env(self):
        ds = ai.chon_model_bao_cao(
            {"GEMINI_MODEL": "a", "GEMINI_MODEL_BAO_CAO_DU_PHONG": "b"})
        self.assertEqual(ds, ["a", "b"])

    def test_du_phong_TRUNG_model_chinh_thi_bo_qua(self):
        """Khong duoc goi cung mot model hai lan."""
        ds = ai.chon_model_bao_cao(
            {"GEMINI_MODEL": "x", "GEMINI_MODEL_BAO_CAO_DU_PHONG": "x"})
        self.assertEqual(ds, ["x"])

    def test_du_phong_rong_thi_chi_dung_model_chinh(self):
        ds = ai.chon_model_bao_cao(
            {"GEMINI_MODEL": "x", "GEMINI_MODEL_BAO_CAO_DU_PHONG": ""})
        # Rong thi lay mac dinh trong code, khong phai bo du phong
        self.assertEqual(ds, ["x", ai.MODEL_BAO_CAO_DU_PHONG_MAC_DINH])

    def test_thanh_cong_ngay_lan_dau_thi_KHONG_goi_du_phong(self):
        """Du phong khong duoc goi khi model chinh da chay duoc."""
        gia, da_goi = self._gia_theo_model("khong-model-nao-hong")
        ai.viet_nhan_dinh(STATS, None, "x",
                          env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertEqual(da_goi, [ai.MODEL_MAC_DINH])

    def test_goi_gemini_KHONG_bi_doi_hanh_vi(self):
        """Du phong nam o viet_nhan_dinh, KHONG nam trong goi_gemini.

        Neu nhet vao goi_gemini thi moi loi goi deu ton gap doi va cac bai kiem
        thu dem so lan goi se hong.
        """
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

        ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertEqual(dem["n"], 1)


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

    def test_cau_tra_loi_bi_cat_thi_bao_loi_chu_khong_tra_chuoi_cut(self):
        """Het tran token -> tra LOI, khong tra chuoi cut.

        Da xay ra that 29/09/2026: cau tra loi dung o '...la 20' roi het.
        Mot cau cut con te hon mot loi ro rang, vi Dai se tuong bot doc sai so.
        """
        def gia(url, payload, timeout):
            return {"candidates": [{
                "content": {"parts": [{"text": "cau tra loi bi cat giua"}],
                            "role": "model"},
                "finishReason": "MAX_TOKENS"}]}

        content, loi = self._goi(goi_mang_fn=gia)
        self.assertIsNone(content)
        self.assertIn("bi cat", loi)

    def test_finish_reason_STOP_thi_tra_ve_binh_thuong(self):
        def gia(url, payload, timeout):
            return {"candidates": [{
                "content": {"parts": [{"text": "xong"}], "role": "model"},
                "finishReason": "STOP"}]}

        content, loi = self._goi(goi_mang_fn=gia)
        self.assertIsNotNone(content)
        self.assertIsNone(loi)


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


class TestThuLaiLoiTamThoi(unittest.TestCase):
    """Loi mang / het thoi gian cho la loi TAM THOI - phai THU LAI.

    Loi that ngay 29/09/2026: Dai nhan hoi luc 12:00, Gemini qua tai toan he
    thong, ca hai model deu tra ve 'The read operation timed out'. Truoc khi
    sua, ai.py roi thang xuong `except Exception` va TRA LOI NGAY, khong thu
    lai - nen mot lan mang chap chon la Dai mat cau tra loi.
    """

    def _dem_lan_goi(self, ham_nem_loi):
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            raise ham_nem_loi(url)

        ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        return dem["n"]

    def test_loi_mang_thi_thu_lai(self):
        self.assertEqual(self._dem_lan_goi(lambda url: OSError("mat mang")),
                         ai.SO_LAN_THU_LAI + 1)

    def test_het_thoi_gian_cho_thi_thu_lai(self):
        self.assertEqual(self._dem_lan_goi(lambda url: TimeoutError("het gio")),
                         ai.SO_LAN_THU_LAI + 1)

    def test_urlerror_thi_thu_lai(self):
        self.assertEqual(
            self._dem_lan_goi(lambda url: urllib.error.URLError("khong ket noi")),
            ai.SO_LAN_THU_LAI + 1)

    def test_ma_500_thu_lai(self):
        def gia(url, payload, timeout):
            raise urllib.error.HTTPError(url, 500, "loi may chu", {},
                                         io.BytesIO(b"{}"))
        dem = {"n": 0}

        def gia_dem(url, payload, timeout):
            dem["n"] += 1
            return gia(url, payload, timeout)

        ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia_dem)
        self.assertEqual(dem["n"], ai.SO_LAN_THU_LAI + 1)

    def test_ma_404_khong_thu_lai(self):
        """404 = ten model sai, thu lai chi ton thoi gian."""
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            raise urllib.error.HTTPError(url, 404, "khong co model", {},
                                         io.BytesIO(b"{}"))

        ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertEqual(dem["n"], 1)

    def test_danh_sach_ma_tam_thoi(self):
        for ma in (429, 500, 502, 503, 504):
            self.assertIn(ma, ai.MA_LOI_TAM_THOI, ma)
        for ma in (400, 403, 404):
            self.assertNotIn(ma, ai.MA_LOI_TAM_THOI, ma)

    def test_loi_mang_het_luot_thi_bao_loi_ro(self):
        def gia(url, payload, timeout):
            raise OSError("mat mang")

        chu, loi = ai.goi_gemini({"GEMINI_API_KEY": "k"}, "x", goi_mang_fn=gia)
        self.assertIsNone(chu)
        self.assertIn("mat mang", loi)
        self.assertIn("het thoi gian cho", loi)


class TestThongBaoLoiNhieuModel(unittest.TestCase):
    """Thong bao loi phai ghi TAT CA cac model da thu, khong chi model cuoi.

    Loi that ngay 29/09/2026: model chinh gap HTTP 503 (qua tai), model du
    phong het thoi gian cho. Thong bao chi hien loi cua model du phong, nen Dai
    doc khong biet la AI dang qua tai ma tuong hong gi do.
    """

    def test_ghi_ca_hai_model(self):
        def gia(url, payload, timeout):
            raise urllib.error.HTTPError(url, 503, "qua tai", {}, io.BytesIO(b"{}"))

        content, loi = ai.goi_gemini_cong_cu(
            {"GEMINI_API_KEY": "k"},
            [{"role": "user", "parts": [{"text": "x"}]}], goi_mang_fn=gia)
        self.assertIsNone(content)
        self.assertIn("gemini-3.8-flash", loi)
        self.assertIn("gemini-3.5-flash", loi)
        self.assertIn("503", loi)

    def test_loi_cua_hai_model_ngan_cach_bang_gach_dung(self):
        def gia(url, payload, timeout):
            raise OSError("mat mang")

        _, loi = ai.goi_gemini_cong_cu(
            {"GEMINI_API_KEY": "k"},
            [{"role": "user", "parts": [{"text": "x"}]}], goi_mang_fn=gia)
        self.assertIn(" | ", loi)


class TestNganSachThoiGianTraLoi(unittest.TestCase):
    """Het ngan sach thi BO CUOC, de moc gio khong bi tre."""

    def _env(self):
        return {"GEMINI_API_KEY": "k"}

    def test_het_ngan_sach_thi_bo_cuoc(self):
        bo = BoCongCuGia()

        def gia(url, payload, timeout):
            return _kq_gemini(_content_goi_cong_cu("lay_khoang", {}))

        gio = {"t": 0.0}

        def dong_ho():
            gio["t"] += 100.0
            return gio["t"]

        chu, loi = ai.tra_loi("?", bo, env=self._env(), goi_mang_fn=gia,
                              dong_ho_fn=dong_ho)
        self.assertIsNone(chu)
        self.assertIn("qua tai", loi)

    def test_con_thoi_gian_thi_khong_cat_som(self):
        bo = BoCongCuGia()
        dem = {"n": 0}

        def gia(url, payload, timeout):
            dem["n"] += 1
            if dem["n"] == 1:
                return _kq_gemini(_content_goi_cong_cu("lay_khoang", {}))
            return _kq_gemini(_content_chu("xong roi"))

        chu, loi = ai.tra_loi("?", bo, env=self._env(), goi_mang_fn=gia,
                              dong_ho_fn=lambda: 0.0)
        self.assertEqual(chu, "xong roi")
        self.assertIsNone(loi)

    def test_ngan_sach_duoc_dat_ro_rang(self):
        self.assertEqual(ai.THOI_GIAN_TOI_DA_HOI_DAP, 180)
        self.assertGreater(ai.TIMEOUT_HOI_DAP, 30)

    def test_tran_token_du_rong_cho_token_suy_nghi(self):
        """Model 3.x tinh token SUY NGHI vao tran nay.

        Do that: moi luot ton 477-1132 token chi rieng cho suy nghi. Tran 2000
        tung lam cau tra loi bi cat giua dong.
        """
        self.assertGreaterEqual(ai.TOI_DA_TOKEN_TRA_LOI, 4000)


# ============================================================================
# PHAN DE XUAT (nac 1)
# ============================================================================


class TestBocJson(unittest.TestCase):
    """Boc JSON chiu loi. Gemini hay boc trong ```json va hay them cau dan."""

    def test_boc_json_truc_tiep(self):
        self.assertEqual({"a": 1}, ai.boc_json('{"a": 1}'))

    def test_boc_json_trong_khoi_ma(self):
        self.assertEqual({"a": 1}, ai.boc_json('```json\n{"a": 1}\n```'))

    def test_boc_json_trong_khoi_ma_khong_ghi_json(self):
        self.assertEqual({"a": 1}, ai.boc_json('```\n{"a": 1}\n```'))

    def test_boc_json_co_cau_dan_truoc(self):
        self.assertEqual(
            {"a": 1}, ai.boc_json('Đây là kết quả: {"a": 1} cảm ơn bạn'))

    def test_boc_json_hong_tra_ve_none(self):
        for rac in ('{abc', 'khong phai json', '', None, 123, '[1, 2]', '{}'):
            with self.subTest(rac=rac):
                kq = ai.boc_json(rac)
                # '{}' la JSON hop le nhung rong -> tra ve dict rong, khong phai None
                if rac == '{}':
                    self.assertEqual({}, kq)
                else:
                    self.assertIsNone(kq)

    def test_boc_json_nhieu_khoi_lay_khoi_dau_dung_duoc(self):
        t = '```json\n{hong\n```\n```json\n{"a": 2}\n```'
        self.assertEqual({"a": 2}, ai.boc_json(t))


class TestVietNhanDinhVaDeXuat(unittest.TestCase):

    def _gia(self, text):
        def fn(url, payload, timeout):
            return {"candidates": [{"content": {"parts": [{"text": text}]}}]}
        return fn

    def _goi(self, text, env=None):
        return ai.viet_nhan_dinh_va_de_xuat(
            STATS, KY_TRUOC_CO_SO, "x",
            env=env or {"GEMINI_API_KEY": "k"}, goi_mang_fn=self._gia(text))

    def test_json_hop_le_tach_duoc_hai_phan(self):
        t = ('{"nhan_dinh": "Hai camp dang dot tien.", '
             '"de_xuat": [{"id": "333", "viec": "tam_dung", "ly_do": "0 don"}]}')
        nhan_dinh, ds, loi = self._goi(t)
        self.assertEqual("Hai camp dang dot tien.", nhan_dinh)
        self.assertEqual(1, len(ds))
        self.assertEqual("333", ds[0]["id"])
        self.assertIsNone(loi)

    def test_json_hop_le_de_xuat_rong_la_binh_thuong(self):
        nhan_dinh, ds, loi = self._goi('{"nhan_dinh": "Moi thu deu on.", "de_xuat": []}')
        self.assertEqual("Moi thu deu on.", nhan_dinh)
        self.assertEqual([], ds)
        self.assertIsNone(loi)

    def test_de_xuat_khong_phai_danh_sach_thi_coi_nhu_rong(self):
        nhan_dinh, ds, loi = self._goi('{"nhan_dinh": "ok", "de_xuat": "khong phai list"}')
        self.assertEqual("ok", nhan_dinh)
        self.assertEqual([], ds)
        self.assertIsNone(loi)

    def test_AI_tra_chu_thuong_van_giu_nhan_dinh(self):
        nhan_dinh, ds, loi = self._goi("Chi phi moi don dang tang manh.")
        self.assertEqual("Chi phi moi don dang tang manh.", nhan_dinh)
        self.assertEqual([], ds)
        self.assertIsNone(loi)

    def test_AI_tra_JSON_hong_thi_KHONG_hien_JSON_do(self):
        nhan_dinh, ds, loi = self._goi('{"nhan_dinh": "Chi phi... bi cat giua dong')
        self.assertIsNone(nhan_dinh)
        self.assertEqual([], ds)
        self.assertIn("JSON hong", loi)

    def test_JSON_thieu_nhan_dinh_thi_thu_model_ke_tiep(self):
        nhan_dinh, ds, loi = self._goi('{"de_xuat": []}')
        self.assertIsNone(nhan_dinh)
        self.assertIn("thieu truong nhan_dinh", loi)

    def test_AI_loi_thi_tra_ve_loi_chu_khong_nem(self):
        def gia(url, payload, timeout):
            raise OSError("mat mang")

        nhan_dinh, ds, loi = ai.viet_nhan_dinh_va_de_xuat(
            STATS, KY_TRUOC_CO_SO, "x",
            env={"GEMINI_API_KEY": "k"}, goi_mang_fn=gia)
        self.assertIsNone(nhan_dinh)
        self.assertEqual([], ds)
        self.assertIn("mat mang", loi)

    def test_khong_co_chia_khoa_thi_bao_loi_ro(self):
        nhan_dinh, ds, loi = ai.viet_nhan_dinh_va_de_xuat(
            STATS, KY_TRUOC_CO_SO, "x", env={}, goi_mang_fn=self._gia("x"))
        self.assertIsNone(nhan_dinh)
        self.assertEqual([], ds)
        self.assertIn("GEMINI_API_KEY", loi)

    def test_bang_camp_co_ma_chien_dich(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("ma 111", p)
        self.assertIn("ma 333", p)

    def test_camp_0_don_len_truoc(self):
        """Camp chi tien ma khong ra don phai nam TRUOC trong cau lenh."""
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        vi_tri_camp_c = p.index("ma 333")     # camp C: 0 don
        vi_tri_camp_a = p.index("ma 111")     # camp A: 9 don
        self.assertLess(vi_tri_camp_c, vi_tri_camp_a)

    def test_cau_lenh_yeu_cau_tra_json(self):
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("nhan_dinh", p)
        self.assertIn("de_xuat", p)
        self.assertIn("tam_dung", p)

    def test_cau_lenh_van_bat_buoc_so_do_code_tinh(self):
        """Rang buoc cu KHONG duoc mat khi doi cau lenh sang JSON."""
        p = ai.soan_prompt(STATS, KY_TRUOC_CO_SO, "x")
        self.assertIn("Không tự tính", p)
        self.assertIn("CÓ DẤU", p)

    def test_so_camp_gui_kem_bi_cat_dung_muc(self):
        nhieu = {"all": [
            {"id": str(i), "name": f"camp {i}", "spend": 100000.0, "purchase": 1}
            for i in range(ai.TOI_DA_CAMP_GUI_AI + 15)
        ]}
        p = ai.soan_prompt(nhieu, None, "x")
        self.assertEqual(ai.TOI_DA_CAMP_GUI_AI, p.count("- ma "))




class TestNhaCungCapNous(unittest.TestCase):
    """Nha cung cap AI thu hai: Nous (OpenAI-compatible). Them 01/10/2026.

    Vi sao phai co lop nay: API cua Nous noi chuyen bang KIEU OPENAI, con toan bo
    ai.py doc KIEU GEMINI. Chi doi qua lai o mot cho. Neu doi sai thi phan hoi dap
    (co vong lap cong cu) se hong trong im lang - dung kieu loi te nhat.
    """

    def test_mac_dinh_VAN_LA_GEMINI(self):
        self.assertEqual(ai.nha_cung_cap({}), "gemini")
        self.assertEqual(ai.nha_cung_cap(None), "gemini")
        self.assertEqual(ai.nha_cung_cap({"AI_NHA_CUNG_CAP": ""}), "gemini")

    def test_chon_duoc_nous(self):
        self.assertEqual(ai.nha_cung_cap({"AI_NHA_CUNG_CAP": "nous"}), "nous")
        self.assertEqual(ai.nha_cung_cap({"AI_NHA_CUNG_CAP": " NOUS "}), "nous")

    def test_model_nous_doi_duoc_bang_env(self):
        self.assertEqual(ai.model_nous({}), ai.MODEL_NOUS_MAC_DINH)
        self.assertEqual(ai.model_nous({"NOUS_MODEL": "openai/gpt-4o-mini"}),
                         "openai/gpt-4o-mini")

    def test_danh_sach_model_doi_theo_nha_cung_cap(self):
        gem = ai.chon_model_bao_cao({})
        nous = ai.chon_model_bao_cao({"AI_NHA_CUNG_CAP": "nous"})
        self.assertTrue(all(m.startswith("gemini") for m in gem), gem)
        self.assertTrue(all("/" in m for m in nous), nous)
        self.assertEqual(ai._chon_model_hoi_dap({"AI_NHA_CUNG_CAP": "nous"}),
                         nous)

    # ---- Doi payload Gemini -> OpenAI ----

    def test_doi_text_co_ban(self):
        p = {"contents": [{"role": "user", "parts": [{"text": "Xin chao"}]}]}
        ra = ai._gemini_sang_openai(p, "m")
        self.assertEqual(ra["model"], "m")
        self.assertEqual(ra["messages"],
                         [{"role": "user", "content": "Xin chao"}])

    def test_doi_cong_cu_va_HA_THAP_kieu_tham_so(self):
        p = {"contents": [], "tools": [{"functionDeclarations": [{
            "name": "lay_mot_ngay", "description": "x",
            "parameters": {"type": "OBJECT", "properties": {
                "ngay": {"type": "STRING"}}}}]}]}
        ra = ai._gemini_sang_openai(p, "m")
        f = ra["tools"][0]
        self.assertEqual(f["type"], "function")
        self.assertEqual(f["function"]["name"], "lay_mot_ngay")
        self.assertEqual(f["function"]["parameters"]["type"], "object")
        self.assertEqual(f["function"]["parameters"]["properties"]["ngay"]["type"],
                         "string")

    def test_doi_maxOutputTokens_sang_max_tokens(self):
        p = {"contents": [], "generationConfig": {"maxOutputTokens": 900}}
        self.assertEqual(ai._gemini_sang_openai(p, "m")["max_tokens"], 900)

    def test_doi_vai_model_thanh_assistant(self):
        p = {"contents": [{"role": "model", "parts": [{"text": "Da"}]}]}
        ra = ai._gemini_sang_openai(p, "m")
        self.assertEqual(ra["messages"][0]["role"], "assistant")

    def test_hoi_thoai_cong_cu_GHEP_DUNG_tool_call_id(self):
        """Cho de sai nhat: Gemini chi co TEN cong cu, OpenAI can tool_call_id."""
        p = {"contents": [
            {"role": "user", "parts": [{"text": "may don?"}]},
            {"role": "model", "parts": [{"functionCall": {
                "name": "lay_mot_ngay", "args": {"ngay": "2026-09-30"}}}]},
            {"role": "user", "parts": [{"functionResponse": {
                "name": "lay_mot_ngay", "response": {"purchase": 25}}}]},
        ]}
        ra = ai._gemini_sang_openai(p, "m")
        self.assertEqual([m["role"] for m in ra["messages"]],
                         ["user", "assistant", "tool"])
        goi = ra["messages"][1]["tool_calls"][0]
        self.assertEqual(goi["function"]["name"], "lay_mot_ngay")
        self.assertEqual(json.loads(goi["function"]["arguments"])["ngay"],
                         "2026-09-30")
        self.assertEqual(ra["messages"][2]["tool_call_id"], goi["id"],
                         "tool_call_id PHAI khop id cua lan goi")

    # ---- Doi ket qua OpenAI -> Gemini ----

    def test_doi_ket_qua_chu(self):
        kq = {"choices": [{"message": {"content": "25 don"},
                             "finish_reason": "stop"}]}
        ra = ai._openai_sang_gemini(kq)
        self.assertEqual(ra["candidates"][0]["content"]["parts"][0]["text"], "25 don")
        self.assertEqual(ra["candidates"][0]["finishReason"], "STOP")

    def test_doi_ket_qua_xin_goi_cong_cu(self):
        kq = {"choices": [{"message": {"content": None, "tool_calls": [{
            "id": "call_1", "type": "function", "function": {
                "name": "lay_mot_ngay",
                "arguments": "{\"ngay\": \"2026-09-15\"}"}}]},
            "finish_reason": "tool_calls"}]}
        ra = ai._openai_sang_gemini(kq)
        fc = ra["candidates"][0]["content"]["parts"][0]["functionCall"]
        self.assertEqual(fc["name"], "lay_mot_ngay")
        self.assertEqual(fc["args"], {"ngay": "2026-09-15"},
                         "arguments phai duoc giai tu chuoi JSON")

    def test_cat_vi_het_token_van_nhan_ra(self):
        """OpenAI bao "length"; phan kiem tra san co doi thanh MAX_TOKENS."""
        kq = {"choices": [{"message": {"content": "abc"},
                             "finish_reason": "length"}]}
        ra = ai._openai_sang_gemini(kq)
        self.assertEqual(ra["candidates"][0]["finishReason"], "MAX_TOKENS")

    def test_ket_qua_hong_tra_ve_None_khong_nem(self):
        for xau in (None, {}, {"choices": []}, {"choices": [{}]},
                    "chuoi", {"choices": [{"message": {}}]}):
            self.assertIsNone(ai._openai_sang_gemini(xau), repr(xau))

    def test_thieu_NOUS_API_KEY_thi_bao_ro(self):
        chu, loi = ai.goi_gemini({"AI_NHA_CUNG_CAP": "nous"}, "hi", timeout=5)
        self.assertIsNone(chu)
        self.assertIn("NOUS_API_KEY", loi)


if __name__ == "__main__":
    unittest.main()
