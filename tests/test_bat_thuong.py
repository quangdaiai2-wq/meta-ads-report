"""Kiem thu bat_thuong - phat hien so lieu bat thuong (ban thiet ke muc 7.3).

Ba dieu kien duy nhat:
  (1) chi tieu vot  : > 3 lan muc trung binh 7 ngay truoc do
  (2) chi ma khong co ket qua: chi tieu > 0, luot mua = 0
  (3) tat ca deu bang 0

Kiem thu KHONG cham mang va KHONG dung file lich su that cua Dai.
"""
import json
import tempfile
import unittest
from datetime import date, datetime, timedelta
from pathlib import Path

import bat_thuong

NGAY_KY = date(2026, 9, 29)


def _ghi_lich_su(thu_muc, ds_ngay):
    """Ghi file lich su gia.

    ds_ngay: danh sach (ngay, spend, purchase). Ngay la doi tuong date.
    """
    data = {}
    for ngay, spend, purchase in ds_ngay:
        k = ngay.strftime("%Y-%m-%d")
        data[k] = {
            "moc": 8,
            "thoi_diem": f"{k} 08:05:00",
            "day_du": True,
            "so_camp": 3,
            "tong": {"spend": float(spend), "msg": 10, "contact": 5,
                     "order": 2, "purchase": purchase, "payment": 3, "comment": 1},
            "camp": [],
        }
    duong_dan = Path(thu_muc) / "lich-su.json"
    duong_dan.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return duong_dan


def _bay_ngay_truoc(spend=1_000_000, purchase=10):
    """7 ngay NGAY TRUOC ngay ky bao cao."""
    return [(NGAY_KY - timedelta(days=i), spend, purchase) for i in range(1, 8)]


def _stats(spend=1_000_000, purchase=10, **them):
    tong = {"spend": float(spend), "msg": 10, "contact": 5, "order": 2,
            "purchase": purchase, "payment": 3, "comment": 1}
    tong.update(them)
    return {"total_campaigns": 3, "totals": tong, "good": [], "bad": [], "all": []}


def _stats_khong():
    """Stats voi MOI chi so bang 0 - dung cho dieu kien (3).

    Phai dat TAT CA cac chi so ve 0: chi can mot chi so khac 0 thi day khong con
    la "tat ca deu bang 0" nua.
    """
    return _stats(spend=0, purchase=0, msg=0, contact=0, order=0,
                  payment=0, comment=0)


class TestChuaDuLichSu(unittest.TestCase):
    """Chua du 7 ngay thi KHONG duoc ket luan gi."""

    def test_sau_ngay_thi_bo_qua(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc()[:6])
            self.assertEqual(
                bat_thuong.kiem_tra(_stats(spend=99_000_000), p, NGAY_KY, True), [])

    def test_khong_co_ngay_nao_thi_bo_qua(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, [])
            self.assertEqual(
                bat_thuong.kiem_tra(_stats(spend=99_000_000), p, NGAY_KY, True), [])

    def test_file_chua_ton_tai_thi_bo_qua(self):
        with tempfile.TemporaryDirectory() as tm:
            p = Path(tm) / "khong-co.json"
            self.assertEqual(
                bat_thuong.kiem_tra(_stats(spend=99_000_000), p, NGAY_KY, True), [])

    def test_dung_7_ngay_thi_bat_dau_kiem(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            ly_do = bat_thuong.kiem_tra(_stats(spend=99_000_000), p, NGAY_KY, True)
            self.assertEqual(len(ly_do), 1)

    def test_ngay_sai_dinh_dang_khong_nem_loi(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            self.assertEqual(
                bat_thuong.kiem_tra(_stats(), p, "29-09-2026", True), [])


class TestDieuKien1ChiTieuVot(unittest.TestCase):

    def _chay(self, spend, tron_ngay=True, spend_truoc=1_000_000):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc(spend=spend_truoc))
            return bat_thuong.kiem_tra(_stats(spend=spend), p, NGAY_KY, tron_ngay)

    def test_gap_bon_lan_thi_canh_bao(self):
        ly_do = self._chay(4_000_000)
        self.assertEqual(len(ly_do), 1)
        self.assertIn("chi tiêu", ly_do[0])
        self.assertIn("4.000.000", ly_do[0])

    def test_dung_bang_ba_lan_thi_KHONG_canh_bao(self):
        # Dieu kien la "lon hon 3 lan", khong phai "tu 3 lan tro len".
        self.assertEqual(self._chay(3_000_000), [])

    def test_chi_hon_ba_lan_mot_chut_thi_canh_bao(self):
        self.assertEqual(len(self._chay(3_000_001)), 1)

    def test_thap_hon_thi_khong_canh_bao(self):
        self.assertEqual(self._chay(2_000_000), [])

    def test_bao_cao_MOT_PHAN_ngay_thi_khong_canh_bao(self):
        """Bao cao moc 12h chi la nua ngay - so voi ngay day du la sai."""
        self.assertEqual(self._chay(4_000_000, tron_ngay=False), [])

    def test_truoc_do_khong_co_chi_tieu_thi_khong_canh_bao(self):
        # Moi ngay truoc do chi tieu = 0 thi trung binh = 0, khong chia duoc.
        self.assertEqual(self._chay(4_000_000, spend_truoc=0), [])

    def test_dung_bay_ngay_gan_nhat_khong_phai_tat_ca(self):
        """Chi tinh 7 ngay TRUOC ky bao cao, khong tinh ngay khac."""
        with tempfile.TemporaryDirectory() as tm:
            # 7 ngay gan nhat: chi tieu 1.000.000/ngay
            ds = _bay_ngay_truoc(spend=1_000_000)
            # Ngay cu hon (ngoai cua so) chi tieu 100.000.000 -> phai bi bo qua
            ds.append((NGAY_KY - timedelta(days=8), 100_000_000, 10))
            p = _ghi_lich_su(tm, ds)
            # 4.000.000 = 4 lan trung binh 7 ngay (1.000.000) -> co canh bao.
            # Neu tinh ca ngay cu thi trung binh vot len ~13 trieu -> khong canh bao.
            ly_do = bat_thuong.kiem_tra(_stats(spend=4_000_000), p, NGAY_KY, True)
            self.assertEqual(len(ly_do), 1)


class TestDieuKien2ChiMaKhongCoKetQua(unittest.TestCase):

    def _chay(self, spend, purchase, purchase_truoc=10, tron_ngay=True):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc(purchase=purchase_truoc))
            return bat_thuong.kiem_tra(
                _stats(spend=spend, purchase=purchase), p, NGAY_KY, tron_ngay)

    def test_chi_tieu_duong_ma_khong_co_don_thi_canh_bao(self):
        ly_do = self._chay(1_000_000, 0)
        self.assertEqual(len(ly_do), 1)
        self.assertIn("0 lượt mua", ly_do[0])

    def test_co_don_thi_khong_canh_bao(self):
        self.assertEqual(self._chay(1_000_000, 5), [])

    def test_khong_chi_tieu_cung_khong_co_don_thi_khong_canh_bao(self):
        # Truong hop nay thuoc dieu kien (3), khong phai (2).
        self.assertEqual(self._chay(0, 0), [])

    def test_truoc_do_cung_khong_co_don_thi_khong_canh_bao(self):
        self.assertEqual(self._chay(1_000_000, 0, purchase_truoc=0), [])

    def test_bao_cao_MOT_PHAN_ngay_thi_khong_canh_bao(self):
        self.assertEqual(self._chay(1_000_000, 0, tron_ngay=False), [])


class TestDieuKien3TatCaBang0(unittest.TestCase):

    def _chay(self, tron_ngay=False, spend_truoc=1_000_000, mot_ngay_bang_0=False):
        with tempfile.TemporaryDirectory() as tm:
            ds = _bay_ngay_truoc(spend=spend_truoc)
            if mot_ngay_bang_0:
                ngay, _, purchase = ds[3]
                ds[3] = (ngay, 0, 0)
            p = _ghi_lich_su(tm, ds)
            return bat_thuong.kiem_tra(_stats_khong(), p, NGAY_KY, tron_ngay)

    def test_tat_ca_bang_0_thi_canh_bao(self):
        ly_do = self._chay()
        self.assertEqual(len(ly_do), 1)
        self.assertIn("đều bằng 0", ly_do[0])

    def test_ap_dung_cho_ca_bao_cao_MOT_PHAN_ngay(self):
        """Moi chi so bang 0 thi du la moc nao cung la dau hieu hong."""
        self.assertEqual(len(self._chay(tron_ngay=False)), 1)

    def test_truoc_do_khong_co_chi_tieu_thi_khong_canh_bao(self):
        self.assertEqual(self._chay(spend_truoc=0), [])

    def test_truoc_do_co_mot_ngay_bang_0_thi_khong_canh_bao(self):
        """Neu truoc do da co ngay chi tieu = 0 thi hom nay bang 0 la binh thuong."""
        self.assertEqual(self._chay(mot_ngay_bang_0=True), [])

    def test_chi_can_MOT_chi_so_khac_0_thi_khong_canh_bao(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            stats = _stats(spend=0, purchase=0)
            stats["totals"]["msg"] = 1
            self.assertEqual(bat_thuong.kiem_tra(stats, p, NGAY_KY, False), [])


class TestNhieuLyDoVaDuLieuHong(unittest.TestCase):

    def test_hai_dieu_kien_cung_luc_thi_hai_ly_do(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            ly_do = bat_thuong.kiem_tra(
                _stats(spend=5_000_000, purchase=0), p, NGAY_KY, True)
            self.assertEqual(len(ly_do), 2)

    def test_stats_rong_khong_nem_loi(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            self.assertEqual(bat_thuong.kiem_tra({}, p, NGAY_KY, True), [])

    def test_stats_None_khong_nem_loi(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            self.assertEqual(bat_thuong.kiem_tra(None, p, NGAY_KY, True), [])

    def test_tong_toan_chu_khong_nem_loi(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            stats = {"totals": {"spend": "khong-phai-so", "purchase": None}}
            self.assertEqual(bat_thuong.kiem_tra(stats, p, NGAY_KY, True), [])

    def test_stats_rong_KHONG_bao_dong_sai(self):
        """Loi THAT bi buoc dung thu bat duoc 29/09/2026.

        `stats` rong lam moi phep doc ra 0, va dieu kien (3) bao "moi chi so
        deu bang 0" - mot canh bao SAI. Chua nhan du chi so thi khong duoc ket
        luan gi.
        """
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            self.assertEqual(bat_thuong.kiem_tra({"totals": {}}, p, NGAY_KY, True), [])

    def test_stats_thieu_mot_chi_so_cung_khong_ket_luan(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            thieu = _stats_khong()
            del thieu["totals"]["comment"]
            self.assertEqual(bat_thuong.kiem_tra(thieu, p, NGAY_KY, True), [])

    def test_stats_du_chi_so_thi_van_ket_luan(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            self.assertEqual(len(bat_thuong.kiem_tra(_stats_khong(), p, NGAY_KY, True)), 1)

    def test_ngay_dang_doi_tuong_date_van_chay(self):
        with tempfile.TemporaryDirectory() as tm:
            p = _ghi_lich_su(tm, _bay_ngay_truoc())
            ly_do = bat_thuong.kiem_tra(_stats(spend=9_000_000), p, NGAY_KY, True)
            self.assertEqual(len(ly_do), 1)


class TestCanhBao(unittest.TestCase):

    def test_khong_co_ly_do_thi_chuoi_rong(self):
        self.assertEqual(bat_thuong.canh_bao([]), "")

    def test_co_ly_do_thi_co_chu_bat_thuong(self):
        chu = bat_thuong.canh_bao(["chi tiêu vọt"])
        self.assertIn("bất thường", chu)
        self.assertIn("chi tiêu vọt", chu)
        self.assertIn("kiểm tra lại trước khi tin", chu)

    def test_nhieu_ly_do_thi_ghep_lai(self):
        chu = bat_thuong.canh_bao(["ly do 1", "ly do 2"])
        self.assertIn("ly do 1", chu)
        self.assertIn("ly do 2", chu)

    def test_canh_bao_khong_bao_gio_chan_bao_cao(self):
        """Canh bao chi la CHU them vao. No khong duoc co co che chan gi."""
        self.assertIsInstance(bat_thuong.canh_bao(["x"]), str)


if __name__ == "__main__":
    unittest.main()
