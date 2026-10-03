"""Kiem thu THONG BAO KHI AGENT TU HANH (Viec 1, Dai chot 03/10/2026).

Boi canh: ngay 03/10/2026 agent TU tat chien dich 120250389649450509 (luong TH2
CBO) nhung KHONG bao gi cho Dai. Dai tuong bot chet, phai tu vao Meta tat tay.
Tin nhan trong module nay la kenh MOT CHIEU agent -> Dai, khac han cac tin
"xin phep" hien co (can Dai bam nut).

KHONG goi mang, khong doc file.
"""
import unittest
from datetime import datetime, timezone, timedelta

import agent_xin_phep

GIO_VN = timezone(timedelta(hours=7))


class TestTinTuHanh(unittest.TestCase):

    def _ct_tat_chien_dich(self, **them):
        ct = {
            "tat_chien_dich": True,
            "campaign_id": "120250389649450509",
            "ten_chien_dich": "2026 - 09 - 15 - dainq - Scale - Online MUA - LTT X",
            "ha_ngan_sach": True,
            "ly_do": "còn 0 nhóm đang chạy",
        }
        ct.update(them)
        return ct

    # ---- T1: co tat chien dich + du du lieu => soan duoc tin ----
    def test_T1_tat_chien_dich_thi_co_tin(self):
        tin = agent_xin_phep.soan_tin_tu_hanh(
            self._ct_tat_chien_dich(), datetime(2026, 10, 3, 10, 59, tzinfo=GIO_VN))
        self.assertIn("AGENT TỰ LÀM", tin)
        self.assertIn("120250389649450509", tin)
        self.assertIn("LTT X", tin)
        self.assertIn("27.000", tin)
        self.assertIn("10:59 ngày 03/10/2026", tin)

    # ---- T2: KHONG tat chien dich => KHONG gui gi ----
    def test_T2_khong_tat_chien_dich_thi_khong_gui(self):
        ct = {"campaign_id": "120250389649450509",
              "chuyen_ns_ket_qua": "A1 → 400.000đ"}
        self.assertEqual(agent_xin_phep.soan_tin_tu_hanh(ct, None), "")

    # ---- T3: thieu ten chien dich => van soan duoc bang ma ----
    def test_T3_thieu_ten_thi_dung_ma(self):
        tin = agent_xin_phep.soan_tin_tu_hanh(
            {"tat_chien_dich": True, "campaign_id": "120250389649450509"}, None)
        self.assertIn("Vừa tắt CHIẾN DỊCH", tin)
        self.assertIn("120250389649450509", tin)

    # ---- T4: co chuyen ngan sach sang nhom song => them dong ----
    def test_T4_co_chuyen_ngan_sach_thi_them_dong(self):
        tin = agent_xin_phep.soan_tin_tu_hanh(
            self._ct_tat_chien_dich(chuyen_ns_ket_qua="A1 → 400.000đ"), None)
        self.assertIn("chuyển sang nhóm sống", tin)
        self.assertIn("400.000", tin)

    # ---- T5: khong co gio => bo dong "Luc:" ----
    def test_T5_khong_co_gio_thi_bo_dong_luc(self):
        tin = agent_xin_phep.soan_tin_tu_hanh(
            self._ct_tat_chien_dich(), None)
        self.assertNotIn("Lúc:", tin)

    # ---- T6: du lieu ban => chuoi rong, KHONG nem loi ----
    def test_T6_du_lieu_ban_thi_tra_rong(self):
        for bad in (None, "chuoi", 123, [], ()):
            self.assertEqual(agent_xin_phep.soan_tin_tu_hanh(bad, None), "",
                             f"Du lieu {bad!r} phai tra chuoi rong")

    # ---- T7: gio dang chuoi ISO => van doc duoc ----
    def test_T7_gio_dang_chuoi_iso_van_doc_duoc(self):
        tin = agent_xin_phep.soan_tin_tu_hanh(
            self._ct_tat_chien_dich(), "2026-10-03T10:59:10+07:00")
        self.assertIn("Lúc: 10:59 ngày 03/10/2026", tin)

    # ---- T8: ten rat dai => bi cat, khong tran tin nhan ----
    def test_T8_ten_dai_thi_bi_cat(self):
        tin = agent_xin_phep.soan_tin_tu_hanh(
            self._ct_tat_chien_dich(ten_chien_dich="x" * 500), None)
        self.assertLess(len(tin), 600)

    # ---- T9: khong co ly do => dung cau mac dinh, khong de trong ----
    def test_T9_khong_co_ly_do_thi_dung_cau_mac_dinh(self):
        ct = self._ct_tat_chien_dich()
        ct.pop("ly_do")
        tin = agent_xin_phep.soan_tin_tu_hanh(ct, None)
        self.assertIn("Lý do:", tin)
        self.assertNotIn("Lý do: \n", tin)

    # ---- T10: ha_ngan_sach=False => KHONG hien dong ngan sach ----
    def test_T10_khong_ha_ngan_sach_thi_khong_hien(self):
        tin = agent_xin_phep.soan_tin_tu_hanh(
            self._ct_tat_chien_dich(ha_ngan_sach=False), None)
        self.assertNotIn("27.000", tin)


if __name__ == "__main__":
    unittest.main(verbosity=2)
