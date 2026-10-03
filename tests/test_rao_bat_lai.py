"""Kiem thu VA RAO 8 + ham doc so `bat_lai` (Viec 2, Dai chot 03/10/2026).

LO HONG THAT (03/10/2026): Dai tra loi nhom X luc 02/10 11:45. Nhom X duoc BAT LAI
va chay lai phat sinh chi tieu. Rao 8 van chan suot 24 gio => agent IM LANG, Dai
tuong bot chet va phai tu vao Meta tat tay.

CACH VA: chi mo them MOT truong hop — nhom duoc bat lai SAU thoi diem Dai tra loi.
Moi truong hop khac giu nguyen (chan).

KHONG goi mang, khong doc file that.
"""
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import agent_ky_uc
import agent_rao

GIO_VN = timezone(timedelta(hours=7))
MA = "120250389649480509"


def _cach_day(phut):
    return datetime.now(GIO_VN) - timedelta(minutes=phut)


class TestRao8BatLai(unittest.TestCase):
    """Rao 8: khong hoi lai nhom da co cau tra loi — kem NGOAI LE moi."""

    def _de_xuat(self):
        return {
            "hanh_dong": "tam_dung",
            "doi_tuong": {
                "cap": "ad_set",
                "id": MA,
                "ten": "2026 - 09 - 15 - dainq - Scale - Online A1",
            },
            "ngan_sach_ha": agent_rao.NGAN_SACH_HA,
            "luot_mua": 0,
            "chi_phi_moi_luot": None,
        }

    def _lich_su(self, phut_tra_loi, phut_bat_lai=None, co_khoa=True):
        ls = {
            "so_hanh_dong_hom_nay": 0,
            "so_hanh_dong_gio_nay": 0,
            "nhom_da_tra_loi": {MA: _cach_day(phut_tra_loi)},
        }
        if co_khoa:
            ls["nhom_bat_lai_gan_nhat"] = (
                {} if phut_bat_lai is None
                else {MA: _cach_day(phut_bat_lai)})
        return ls

    # ---- R1: hanh vi CU giu nguyen khi nhom chua bat lai ----
    def test_R1_chua_bat_lai_thi_van_chan(self):
        ok, ly = agent_rao.kiem(self._de_xuat(), self._lich_su(120, None), None)
        self.assertFalse(ok)
        self.assertIn("24 giờ", ly)

    # ---- R2: NGOAI LE — bat lai SAU khi tra loi => cho hoi lai ----
    def test_R2_bat_lai_sau_khi_tra_loi_thi_cho_phep(self):
        ok, ly = agent_rao.kiem(self._de_xuat(), self._lich_su(120, 60), None)
        self.assertTrue(ok, f"Bat lai 1h truoc, tra loi 2h truoc => phai CHO PHEP. ly={ly}")

    # ---- R3: bat lai TRUOC khi tra loi => khong phai tinh huong moi ----
    def test_R3_bat_lai_truoc_khi_tra_loi_thi_van_chan(self):
        ok, ly = agent_rao.kiem(self._de_xuat(), self._lich_su(120, 180), None)
        self.assertFalse(ok, "Bat lai 3h truoc, tra loi 2h truoc => van la cu, phai CHAN")

    # ---- R4: thieu hoa toan khoa bat lai => an toan, van chan ----
    def test_R4_thieu_khoa_bat_lai_thi_van_chan(self):
        ok, ly = agent_rao.kiem(self._de_xuat(), self._lich_su(120, co_khoa=False), None)
        self.assertFalse(ok, "Thieu khoa => giu nguyen hanh vi cu (CHAN)")

    # ---- R5: qua 24h => het han chan ----
    def test_R5_qua_24h_thi_cho_phep(self):
        ok, ly = agent_rao.kiem(self._de_xuat(), self._lich_su(25 * 60), None)
        self.assertTrue(ok, f"Da qua 24h => CHO PHEP. ly={ly}")

    # ---- R6: du lieu ban => chan, KHONG nem loi ----
    def test_R6_du_lieu_ban_thi_chan_khong_nem_loi(self):
        for bad in ("khong-phai-dict", 123, ["a"]):
            ls = self._lich_su(120)
            ls["nhom_bat_lai_gan_nhat"] = bad
            ok, ly = agent_rao.kiem(self._de_xuat(), ls, None)
            self.assertFalse(ok, f"Du lieu {bad!r} phai CHAN (an toan)")

    # ---- R7: bien — bat lai DUNG BANG thoi diem tra loi => chan ----
    def test_R7_bat_lai_bang_dung_thoi_diem_tra_loi_thi_chan(self):
        t = _cach_day(120)
        ls = {
            "so_hanh_dong_hom_nay": 0,
            "so_hanh_dong_gio_nay": 0,
            "nhom_da_tra_loi": {MA: t},
            "nhom_bat_lai_gan_nhat": {MA: t},
        }
        ok, ly = agent_rao.kiem(self._de_xuat(), ls, None)
        self.assertFalse(ok, "Bien: bang nhau => uu tien AN TOAN, phai CHAN")

    # ---- R8: nhom KHAC khong bi anh huong ----
    def test_R8_nhom_khac_khong_bi_chan(self):
        ls = {
            "so_hanh_dong_hom_nay": 0,
            "so_hanh_dong_gio_nay": 0,
            "nhom_da_tra_loi": {"999999999": _cach_day(30)},
            "nhom_bat_lai_gan_nhat": {"999999999": _cach_day(10)},
        }
        ok, ly = agent_rao.kiem(self._de_xuat(), ls, None)
        self.assertTrue(ok, f"Nhom khac thi khong bi chan. ly={ly}")

    # ---- R9: co bat lai nhung KHONG co cau tra loi => Rao 8 khong ap dung ----
    def test_R9_chi_co_bat_lai_khong_co_tra_loi_thi_cho_phep(self):
        ls = {
            "so_hanh_dong_hom_nay": 0,
            "so_hanh_dong_gio_nay": 0,
            "nhom_da_tra_loi": {},
            "nhom_bat_lai_gan_nhat": {MA: _cach_day(10)},
        }
        ok, ly = agent_rao.kiem(self._de_xuat(), ls, None)
        self.assertTrue(ok, f"Chua tra loi lan nao => phai CHO PHEP. ly={ly}")


class TestDocSoBatLai(unittest.TestCase):
    """Ham `nhom_bat_lai_gan_nhat` — doc so agent, chi tinh lan bat lai THANH CONG."""

    def setUp(self):
        f = tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                        delete=False, encoding="utf-8")
        self.path = f.name
        f.close()

    def tearDown(self):
        try:
            os.unlink(self.path)
        except OSError:
            pass

    def _ghi(self, ds):
        Path(self.path).write_text(json.dumps(ds, ensure_ascii=False),
                                   encoding="utf-8")

    # ---- K1: ban ghi CU (chua co co da_gui_len_meta) van phai tinh ----
    def test_K1_ban_ghi_cu_van_tinh(self):
        self._ghi([{
            "luc": "2026-09-30T09:58:17+07:00", "hanh_dong": "bat_lai",
            "doi_tuong": {"id": "A"},
            "ket_qua": "thanh cong (HTTP 200, success=true, doc lai thay ACTIVE)",
        }])
        ra = agent_ky_uc.nhom_bat_lai_gan_nhat(None, self.path)
        self.assertIn("A", ra)
        self.assertEqual(ra["A"].hour, 9)

    # ---- K2: co co True NHUNG ket qua bao loi => KHONG tinh ----
    def test_K2_bat_lai_that_bai_thi_khong_tinh(self):
        self._ghi([{
            "luc": "2026-10-03T09:00:00+07:00", "hanh_dong": "bat_lai",
            "doi_tuong": {"id": "A"}, "da_gui_len_meta": True,
            "ket_qua": "loi: Meta tu choi",
        }])
        ra = agent_ky_uc.nhom_bat_lai_gan_nhat(None, self.path)
        self.assertNotIn("A", ra, "Bat lai that bai KHONG duoc tinh")

    # ---- K3: nhieu lan => lay lan MOI NHAT ----
    def test_K3_nhieu_lan_lay_lan_moi_nhat(self):
        self._ghi([
            {"luc": "2026-10-01T09:00:00+07:00", "hanh_dong": "bat_lai",
             "doi_tuong": {"id": "A"}, "da_gui_len_meta": True,
             "ket_qua": "thanh cong"},
            {"luc": "2026-10-03T09:00:00+07:00", "hanh_dong": "bat_lai",
             "doi_tuong": {"id": "A"}, "da_gui_len_meta": True,
             "ket_qua": "thanh cong"},
        ])
        ra = agent_ky_uc.nhom_bat_lai_gan_nhat(None, self.path)
        self.assertEqual(ra["A"].day, 3)

    # ---- K4: bo qua ban ghi khong phai bat_lai ----
    def test_K4_chi_lay_ban_ghi_bat_lai(self):
        self._ghi([
            {"luc": "2026-10-03T09:00:00+07:00", "hanh_dong": "tam_dung",
             "doi_tuong": {"id": "A"}, "da_gui_len_meta": True,
             "ket_qua": "thanh cong"},
            {"luc": "2026-10-03T09:00:00+07:00", "hanh_dong": "xin_phep",
             "doi_tuong": {"id": "B"}, "da_gui_len_meta": True,
             "ket_qua": "thanh cong"},
        ])
        self.assertEqual(agent_ky_uc.nhom_bat_lai_gan_nhat(None, self.path), {})

    # ---- K5: file hong / khong ton tai => dict rong, khong nem loi ----
    def test_K5_file_hong_thi_tra_dict_rong(self):
        Path(self.path).write_text("{hong", encoding="utf-8")
        self.assertEqual(agent_ky_uc.nhom_bat_lai_gan_nhat(None, self.path), {})
        self.assertEqual(
            agent_ky_uc.nhom_bat_lai_gan_nhat(None, "khong-ton-tai.json"), {})

    # ---- K6: ban ghi thieu id hoac thieu luc => bo qua ----
    def test_K6_thieu_id_hoac_luc_thi_bo_qua(self):
        self._ghi([
            {"luc": "2026-10-03T09:00:00+07:00", "hanh_dong": "bat_lai",
             "doi_tuong": {}, "da_gui_len_meta": True, "ket_qua": "thanh cong"},
            {"hanh_dong": "bat_lai", "doi_tuong": {"id": "B"},
             "da_gui_len_meta": True, "ket_qua": "thanh cong"},
        ])
        self.assertEqual(agent_ky_uc.nhom_bat_lai_gan_nhat(None, self.path), {})

    # ---- K7: doc duoc SO THAT cua repo (co 1 lan bat lai ngay 30/09) ----
    def test_K7_doc_duoc_so_that_cua_repo(self):
        that = Path(agent_ky_uc.DUONG_DAN)
        if not that.exists():
            self.skipTest("chua co so that")
        ra = agent_ky_uc.nhom_bat_lai_gan_nhat(None, str(that))
        self.assertIsInstance(ra, dict)

    # ---- K8: ban ghi co co False tuong minh => bo qua ----
    def test_K8_co_false_tuong_minh_thi_bo_qua(self):
        self._ghi([{
            "luc": "2026-10-03T09:00:00+07:00", "hanh_dong": "bat_lai",
            "doi_tuong": {"id": "A"}, "da_gui_len_meta": False,
            "ket_qua": "thanh cong",
        }])
        self.assertEqual(agent_ky_uc.nhom_bat_lai_gan_nhat(None, self.path), {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
