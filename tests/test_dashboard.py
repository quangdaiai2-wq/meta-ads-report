"""Kiem thu dashboard.py — bao cao HTML.

Truoc 29/09/2026 file nay KHONG co bai kiem thu nao, du no la thu Dai mo ra doc.
Bo sung khi doi giao dien va khi chuyen phan NHAN DINH vao file HTML.

Kiem thu KHONG cham mang, KHONG ghi vao file that (tru bai kiem save_dashboard,
bai do ghi vao thu muc tam).
"""
import tempfile
import unittest
from pathlib import Path

import dashboard


def _stats(**doi):
    """So lieu mau. Giong cau truc compute_stats() tra ve."""
    s = {
        "total_campaigns": 16,
        "totals": {"spend": 8198223.0, "msg": 59, "contact": 55, "order": 19,
                   "purchase": 19, "payment": 21, "comment": 1},
        "good": [{"rank": 1, "id": "120250213748430509", "name": "dainq_he_03",
                  "spend": 950385.0, "purchase": 5, "payment": 1, "msg": 4,
                  "cpr": 190077.0}],
        "bad": [{"rank": 1, "id": "999", "name": "dainq_te",
                 "spend": 500000.0, "purchase": 0, "payment": 0, "msg": 0,
                 "cpr": None}],
        "all": [],
        "include_kw": "dainq",
        "exclude_kw": "thuonghieu,Brand",
        "account_name": "",
    }
    s.update(doi)
    return s


class TestSoLieuTrongHTML(unittest.TestCase):

    def _html(self, **doi):
        return dashboard.build_html(_stats(**doi), None, None,
                                    "29/09/2026 (00:00 - 12:00)")

    def test_co_tai_khoan(self):
        self.assertIn("", self._html())

    def test_co_ky_bao_cao(self):
        self.assertIn("29/09/2026 (00:00 - 12:00)", self._html())

    def test_so_tien_co_dau_cham_ngan_nghin(self):
        self.assertIn("8.198.223", self._html())

    def test_du_7_chi_so(self):
        html = self._html()
        self.assertIn("8.198.223", html)      # chi tieu
        self.assertIn(">59<", html)           # tin nhan moi
        self.assertIn(">55<", html)           # lien he moi
        self.assertIn(">19<", html)           # don hang
        self.assertIn(">21<", html)           # thanh toan
        self.assertIn(">1<", html)            # binh luan

    def test_chi_phi_moi_don_tong(self):
        # 8.198.223 / 19 = 431.485,4 -> lam tron 431.485
        self.assertIn("431.485", self._html())

    def test_0_luot_mua_thi_chi_phi_moi_don_la_gach(self):
        s = _stats()
        s["totals"] = dict(s["totals"], purchase=0)
        html = dashboard.build_html(s, None, None, "29/09/2026")
        self.assertIn("—", html)

    def test_so_camp_du_dieu_kien(self):
        self.assertIn("16 campaign đủ điều kiện", self._html())


class TestNhanDinhTrongHTML(unittest.TestCase):
    """Phan NHAN DINH do AI viet nam trong FILE NAY (chuyen tu tin nhan Telegram)."""

    def test_co_nhan_dinh_thi_hien_ra(self):
        html = dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    nhan_dinh="Chi tieu tang 20 phan tram.")
        self.assertIn("Nhận định", html)
        self.assertIn("Chi tieu tang 20 phan tram.", html)

    def test_xuong_dong_thanh_nhieu_doan(self):
        html = dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    nhan_dinh="Doan mot.\nDoan hai.")
        self.assertIn("<p>Doan mot.</p>", html)
        self.assertIn("<p>Doan hai.</p>", html)

    def test_dong_trong_khong_sinh_doan_rong(self):
        html = dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    nhan_dinh="A\n\n\nB")
        self.assertNotIn("<p></p>", html)

    def test_chu_cua_AI_duoc_ESCAPE(self):
        """Chu do AI sinh ra khong duoc tin tuyet doi.

        Neu khong escape thi mot the <script> trong cau nhan dinh se chay duoc
        khi Dai mo file.
        """
        html = dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    nhan_dinh='<script>alert(1)</script>')
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_loi_AI_thi_ghi_chu_ro_ly_do(self):
        html = dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    loi_ai="HTTP 429 - het han muc")
        self.assertIn("HTTP 429", html)
        self.assertIn("vẫn đầy đủ", html)

    def test_loi_AI_cung_duoc_escape(self):
        html = dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    loi_ai="<b>hong</b>")
        self.assertNotIn("<b>hong</b>", html)

    def test_co_nhan_dinh_thi_KHONG_hien_loi_AI(self):
        html = dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    nhan_dinh="CAU_KIEM_THU", loi_ai="HTTP 429")
        self.assertIn("CAU_KIEM_THU", html)
        self.assertNotIn("HTTP 429", html)

    def test_khong_co_gi_thi_khong_co_khoi_nhan_dinh(self):
        html = dashboard.build_html(_stats(), None, None, "29/09/2026")
        self.assertNotIn("Nhận định", html)

    def test_AI_tra_ve_None_khong_lam_hong(self):
        html = dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    nhan_dinh=None, loi_ai=None)
        self.assertIn("Báo cáo Meta Ads", html)

    def test_AI_tra_ve_chuoi_rong_khong_sinh_khoi_rong(self):
        html = dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    nhan_dinh="")
        self.assertNotIn("Nhận định", html)


class TestHaiBangCamp(unittest.TestCase):

    def _html(self, **doi):
        return dashboard.build_html(_stats(**doi), None, None, "29/09/2026")

    def test_co_tieu_de_hai_bang(self):
        html = self._html()
        self.assertIn("Camp hiệu quả", html)
        self.assertIn("Camp kém hiệu quả", html)

    def test_ghi_ro_tieu_chi_xep_hang(self):
        """Dai phai biet vi sao camp 10 don khong dung dau. DUNG XOA DONG NAY."""
        self.assertIn("rẻ nhất trước", self._html())

    def test_ghi_ro_ly_do_bang_kem_co_the_trong(self):
        self.assertIn("MỘT trong hai bảng", self._html())

    def test_hien_id_va_ten_camp(self):
        html = self._html()
        self.assertIn("120250213748430509", html)
        self.assertIn("dainq_he_03", html)

    def test_ten_camp_co_ky_tu_HTML_duoc_escape(self):
        s = _stats()
        s["good"] = [{"rank": 1, "id": "1", "name": 'dainq <img src=x onerror=1>',
                      "spend": 100.0, "purchase": 1, "payment": 0, "msg": 0,
                      "cpr": 100.0}]
        html = dashboard.build_html(s, None, None, "29/09/2026")
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;img", html)

    def test_bang_rong_thi_ghi_khong_co_du_lieu(self):
        html = self._html(good=[], bad=[])
        self.assertIn("Không có dữ liệu", html)

    def test_camp_0_don_hien_gach_khong_hien_0(self):
        """So 0 trong nhu re nhat — da biet la sai."""
        html = self._html()
        i = html.index("dainq_te")
        hang = html[i:html.index("</tr>", i)]
        self.assertIn("—", hang)
        self.assertNotIn(">0<", hang)


class TestGiaoDienMoi(unittest.TestCase):
    """Kiem nhung thu thuoc ve GIAO DIEN, de doi sau nay biet ma sua bai."""

    def _html(self):
        return dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    nhan_dinh="Nhan dinh thu.")

    def test_co_nut_doi_nen_sang_toi(self):
        html = self._html()
        self.assertIn('id="doi-mau"', html)
        self.assertIn("<button", html)

    def test_co_CA_HAI_bo_mau(self):
        html = self._html()
        self.assertIn('data-theme="dark"', html)
        self.assertIn('html[data-theme="light"]', html)

    def test_mac_dinh_la_nen_toi(self):
        self.assertIn('<html lang="vi" data-theme="dark">', self._html())

    def test_nho_lua_chon_bang_localStorage(self):
        self.assertIn("localStorage", self._html())

    def test_co_the_meta_viewport_cho_dien_thoai(self):
        self.assertIn("width=device-width", self._html())

    def test_co_media_query_cho_man_hinh_hep(self):
        self.assertIn("@media (max-width: 640px)", self._html())

    def test_bo_loc_nam_o_chan_trang(self):
        html = self._html()
        chan = html.split("<footer>")[1]
        self.assertIn("dainq", chan)
        self.assertIn("thuonghieu,Brand", chan)

    def test_la_file_HTML_doc_lap(self):
        """Mo bang trinh duyet la xem duoc: khong can internet, khong can server."""
        html = self._html()
        self.assertTrue(html.startswith("<!DOCTYPE html>"))
        self.assertIn('charset="UTF-8"', html)
        self.assertNotIn("http://", html.replace("http://www.w3.org", ""))
        self.assertNotIn("https://", html.replace("https://www.w3.org", ""))


class TestSaveDashboard(unittest.TestCase):

    def test_ghi_duoc_file(self):
        with tempfile.TemporaryDirectory() as tm:
            p = Path(tm) / "ra.html"
            ket_qua = dashboard.save_dashboard(
                _stats(), None, None, "29/09/2026",
                nhan_dinh="Nhan dinh thu.", out_path=p)
            self.assertEqual(str(ket_qua), str(p))
            self.assertTrue(p.exists())
            noi_dung = p.read_text(encoding="utf-8")
            self.assertIn("Báo cáo Meta Ads", noi_dung)
            self.assertIn("Nhan dinh thu.", noi_dung)

    def test_nhan_dinh_di_qua_duoc_save_dashboard(self):
        with tempfile.TemporaryDirectory() as tm:
            p = Path(tm) / "ra.html"
            dashboard.save_dashboard(_stats(), None, None, "29/09/2026",
                                     loi_ai="het han muc", out_path=p)
            self.assertIn("het han muc", p.read_text(encoding="utf-8"))


DE_XUAT_MAU = [{
    "id": "120250350059260509",
    "ten": "2026 - 09 - 11 - dainq - Scale - Online MESS - LTT",
    "spend": 858562.0,
    "purchase": 0,
    "viec": "tam_dung",
    "ly_do": "Chi 858.562 d trong 4 ngay ma khong ra don nao.",
}]


class TestKhoiDeXuatTrongHTML(unittest.TestCase):

    def _html(self, de_xuat):
        return dashboard.build_html(_stats(), None, None, "29/09/2026",
                                    de_xuat=de_xuat)

    def test_co_khoi_de_xuat_khi_co(self):
        html = self._html(DE_XUAT_MAU)
        self.assertIn("Đề xuất", html)
        self.assertIn("analysis suggest", html)
        self.assertIn("120250350059260509", html)
        self.assertIn("858.562", html)

    def test_noi_ro_chua_thuc_hien_gi(self):
        """Dieu quan trong nhat voi Dai: phai noi ro AI CHUA lam gi."""
        html = self._html(DE_XUAT_MAU)
        self.assertIn("Chưa có gì được thực hiện", html)

    def test_khong_co_khoi_de_xuat_khi_rong(self):
        for rong in ([], None):
            with self.subTest(rong=rong):
                html = self._html(rong)
                self.assertNotIn("analysis suggest", html)
                self.assertNotIn("Đề xuất</div>", html)

    def test_khong_co_de_xuat_thi_trang_van_day_du(self):
        html = self._html(None)
        self.assertIn("Báo cáo Meta Ads", html)
        self.assertIn("8.198.223", html)

    def test_ten_camp_duoc_escape(self):
        xau = [dict(DE_XUAT_MAU[0], ten='<script>alert(1)</script>')]
        html = self._html(xau)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_ly_do_duoc_escape(self):
        xau = [dict(DE_XUAT_MAU[0], ly_do='<b>dam</b>')]
        html = self._html(xau)
        self.assertIn("&lt;b&gt;dam&lt;/b&gt;", html)

    def test_thieu_truong_khong_nem_loi(self):
        for tho in ([{}], [{"id": "1"}], [{"ten": "x", "spend": None}]):
            with self.subTest(tho=tho):
                html = self._html(tho)
                self.assertIn("Báo cáo Meta Ads", html)

    def test_de_xuat_di_qua_duoc_save_dashboard(self):
        with tempfile.TemporaryDirectory() as tm:
            p = Path(tm) / "ra.html"
            dashboard.save_dashboard(_stats(), None, None, "29/09/2026",
                                     de_xuat=DE_XUAT_MAU, out_path=p)
            self.assertIn("120250350059260509", p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
