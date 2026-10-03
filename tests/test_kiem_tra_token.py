"""Kiem thu CONG CU KIEM TRA TOKEN (kiem_tra_token_app.py).

Cong cu nay la diem tua de Dai biet da doi sang token App chua. No phai:
  - Nhan dien dung token USER (ca nhan) va token he thong (App).
  - KHONG GHI gi len Meta (chi doc).
  - Khong nem loi khi thieu du lieu.

Cac bai kiem o day dung STUB, khong goi mang that.
"""
import unittest
from unittest import mock

import kiem_tra_token_app as kt


class TestNhanDienLoaiToken(unittest.TestCase):
    """Phan quan trong nhat: phan biet token ca nhan voi token App."""

    def _chay_voi(self, data, doc_ok=True):
        """Chay main() voi debug_token tra ve `data` gia. Tra ve ma thoat."""
        with mock.patch.object(kt, "_doc_env", return_value={
                "META_ADS_ACCESS_TOKEN": "EAA" + "x" * 100,
                "META_APP_ID": "123", "META_APP_SECRET": "abc",
                "META_AD_ACCOUNT_ID": "act_1"}), \
             mock.patch.object(kt, "_debug_token", return_value=(data, None)), \
             mock.patch.object(kt, "_kiem_quyen_thuc_te",
                               return_value=(doc_ok, "doc duoc 1 nhom thu")), \
             mock.patch("builtins.print") as p:
            ma = kt.main()
        return ma, "\n".join(str(c.args[0]) for c in p.call_args_list if c.args)

    # ---- Q1: token ca nhan => bao ro chua doi duoc ----
    def test_Q1_token_user_thi_canh_bao_chua_doi(self):
        ma, out = self._chay_voi({"type": "USER", "is_valid": True,
                                  "application": "MCP ADS",
                                  "app_id": "",
                                  "user_id": "",
                                  "scopes": ["ads_management", "ads_read"]})
        self.assertEqual(ma, 0, "Van la token ca nhan thi ket qua la 0 (chay duoc)")
        self.assertIn("VAN LA TOKEN CA NHAN", out)
        self.assertIn("type = USER", out)

    # ---- Q2: token he thong => bao dat yeu cau ----
    def test_Q2_token_he_thong_thi_bao_dat(self):
        ma, out = self._chay_voi({"type": "SYSTEM_USER", "is_valid": True,
                                  "application": "MCP ADS",
                                  "app_id": "",
                                  "scopes": ["ads_management", "ads_read"]})
        self.assertEqual(ma, 0)
        self.assertIn("TOKEN APP — DA DUNG", out)
        self.assertIn("TOKEN APP — DAT YEU CAU", out)

    # ---- Q3: token het han => bao het han ----
    def test_Q3_token_het_han_thi_canh_bao(self):
        ma, out = self._chay_voi({"type": "SYSTEM_USER", "is_valid": True,
                                  "expires_at": 1000000000,
                                  "scopes": ["ads_management", "ads_read"]})
        self.assertIn("DA HET HAN", out)

    # ---- Q4: het han trong 7 ngay => canh bao som ----
    def test_Q4_sap_het_han_thi_canh_bao_som(self):
        import time
        sap = int(time.time()) + 3 * 86400
        ma, out = self._chay_voi({"type": "SYSTEM_USER", "is_valid": True,
                                  "expires_at": sap,
                                  "scopes": ["ads_management", "ads_read"]})
        self.assertIn("sap het han", out.lower())

    # ---- Q5: khong co expires_at => bao khong bao gio het han ----
    def test_Q5_khong_het_han_thi_bao_tot(self):
        ma, out = self._chay_voi({"type": "SYSTEM_USER", "is_valid": True,
                                  "expires_at": 0,
                                  "scopes": ["ads_management", "ads_read"]})
        self.assertIn("KHONG BAO GIO HET HAN", out)

    # ---- Q6: thieu quyen => chi ro quyen nao thieu ----
    def test_Q6_thieu_quyen_thi_chi_ro(self):
        ma, out = self._chay_voi({"type": "SYSTEM_USER", "is_valid": True,
                                  "scopes": ["ads_read"]})
        self.assertIn("THIEU QUYEN", out)
        self.assertIn("ads_management", out)

    # ---- Q7: debug_token loi => huong dan xu ly ----
    def test_Q7_debug_token_loi_thi_bao_loi(self):
        with mock.patch.object(kt, "_doc_env", return_value={
                "META_ADS_ACCESS_TOKEN": "EAA" + "x" * 100,
                "META_APP_ID": "123", "META_APP_SECRET": "abc"}), \
             mock.patch.object(kt, "_debug_token",
                               return_value=(None, "Invalid OAuth token")), \
             mock.patch("builtins.print") as p:
            ma = kt.main()
        out = "\n".join(str(c.args[0]) for c in p.call_args_list if c.args)
        self.assertEqual(ma, 1)
        self.assertIn("Invalid OAuth token", out)

    # ---- Q8: thieu token trong .env => huong dan mo .env ----
    def test_Q8_thieu_token_thi_huong_dan(self):
        with mock.patch.object(kt, "_doc_env", return_value={}), \
             mock.patch("builtins.print") as p:
            ma = kt.main()
        out = "\n".join(str(c.args[0]) for c in p.call_args_list if c.args)
        self.assertEqual(ma, 1)
        self.assertIn("mo-file-env.bat", out)

    # ---- Q9: doc that that bai => nhac gan tai san (loi hay gap nhat) ----
    def test_Q9_doc_that_that_bai_thi_nhac_gan_tai_san(self):
        ma, out = self._chay_voi({"type": "SYSTEM_USER", "is_valid": True,
                                  "scopes": ["ads_management", "ads_read"]},
                                 doc_ok=False)
        self.assertEqual(ma, 1)
        self.assertIn("GAN TAI KHOAN QUANG CAO", out)


class TestKhongGhiLenMeta(unittest.TestCase):
    """Rang buoc an toan: cong cu nay CHI DUOC DOC."""

    def test_chi_dung_api_get_khong_dung_api_post(self):
        import inspect
        nguon = inspect.getsource(kt)
        self.assertNotIn("api_post", nguon,
                         "Cong cu kiem tra khong duoc GHI gi len Meta")
        self.assertIn("api_get", nguon)

    def test_khong_gui_telegram(self):
        import inspect
        nguon = inspect.getsource(kt)
        self.assertNotIn("gui_tin_nhan", nguon,
                         "Cong cu kiem tra khong duoc gui tin Telegram")


if __name__ == "__main__":
    unittest.main(verbosity=2)
