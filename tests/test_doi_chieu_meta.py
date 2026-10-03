"""Kiem thu DOI CHIEU so agent voi nhat ky Meta (Dai chot 03/10/2026).

BOI CANH: Dai khong phai chu tai khoan doanh nghiep Meta, vai tro EMPLOYEE nen
KHONG tao duoc System User. Moi thao tac cua agent deu hien ten chu token ca nhan
("Nam Duc Pham"), nen nhat ky Meta KHONG phan biet duoc nguoi va may.

=> Duong 2: ghi ro NGUON GOC trong so agent + lam cong cu DOI CHIEU chi doc.

BA PHAT HIEN THAT (da do bang so that trong logs/nhat-ky-agent.json, 40 ban ghi):
  1. "Ghi trung" KHONG phai loi ghi trung. 17 nhom co dung 2 ban ghi, nhung do la
     HAI VAI: ban 1 = luc HOI Dai (che_do="xin_phep", da_gui=False),
     ban 2 = GHI TRUOC KHI GUI META (da_gui=True). Luat du an bat buoc.
  2. Loi THAT: `cap_nhat_phan_hoi` chot ket qua vao SAI ban ghi => ban ghi da gui
     len Meta (da_gui=True) MAI MAI trong ket qua ("ban ghi mo coi").
  3. Tran GIO bi dem gap doi vi `dem_hanh_dong` dem theo BAN GHI, khong theo viec.

KHONG goi mang, khong doc file that (moi bai dung thu muc tam).
"""
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

import agent_ky_uc

GIO_VN = timezone(timedelta(hours=7))
MA = "120250389649480509"
MA2 = "120250204184200509"


def _bg1(luc, che_do="xin_phep", da_gui=False, dai_phan_hoi=None, ket_qua=None,
         ma=MA):
    """Ban ghi 1 — luc HOI Dai. Y nguyen `_soan_ban_ghi()` trong agent.py."""
    return {
        "luc": luc, "che_do": che_do, "ai_lam": "agent nac 2",
        "hanh_dong": "tam_dung",
        "doi_tuong": {"cap": "ad_set", "id": ma, "ten": "Nhom A"},
        "ly_do": "test", "rao_an_toan": "cho phep",
        "da_gui_len_meta": da_gui, "tin_nhan_id": 111,
        "dai_phan_hoi": dai_phan_hoi, "ket_qua": ket_qua,
        "ket_qua_sau_24h": None,
    }


def _bg2(luc, da_gui=True, dai_phan_hoi="tat:120250389649480509", ket_qua=None,
         ma=MA):
    """Ban ghi 2 — GHI TRUOC KHI GUI META. Y nguyen `_lam_theo_dong_y()`."""
    r = _bg1(luc, da_gui=da_gui, dai_phan_hoi=dai_phan_hoi, ket_qua=ket_qua, ma=ma)
    r["tin_nhan_id"] = None
    return r


class _CoSo(unittest.TestCase):
    """Tao thu muc tam, khong bao gio dung vao so that."""

    def setUp(self):
        self.tam = tempfile.TemporaryDirectory()
        self.p = Path(self.tam.name) / "nhat-ky-agent.json"
        self.them = []

    def tearDown(self):
        self.tam.cleanup()

    def _ghi_so(self, ds):
        self.p.write_text(json.dumps(ds, ensure_ascii=False, indent=2),
                          encoding="utf-8")

    def _doc_so(self):
        return json.loads(self.p.read_text(encoding="utf-8"))


# ===========================================================================
#  N12 — CHOT KET QUA VAO DUNG BAN GHI (loi "ban ghi mo coi")
# ===========================================================================
class TestChotKetQuaDungBanGhi(_CoSo):
    """N12 + N13: `cap_nhat_phan_hoi` phai chot vao ban ghi DA GUI LEN META."""

    def test_N12_ket_qua_vao_ban_ghi_da_gui(self):
        """N12: co 2 ban ghi -> ket qua phai nam o ban ghi da_gui=True."""
        self._ghi_so([
            _bg1("2026-10-02T11:45:09+07:00"),
            _bg2("2026-10-02T11:46:55+07:00"),
        ])
        ok = agent_ky_uc.cap_nhat_phan_hoi(
            MA, "tat:120250389649480509", "thanh cong (doc lai thay dung)",
            duong_dan=str(self.p))
        self.assertTrue(ok)
        ds = self._doc_so()
        b1 = next(r for r in ds if r["da_gui_len_meta"] is False)
        b2 = next(r for r in ds if r["da_gui_len_meta"] is True)

        # Ket qua PHAI nam o ban ghi da gui len Meta.
        self.assertIsNotNone(b2.get("ket_qua"),
                             "Ban ghi da_gui=True bi mo coi — ket qua khong duoc ghi vao")
        self.assertIsNone(b1.get("ket_qua"),
                          "Ban ghi chi de HOI Dai khong duoc mang ket qua")
        # N13: khong con ban ghi mo coi.
        mo_coi = [r for r in ds
                  if r.get("da_gui_len_meta") is True and not r.get("ket_qua")]
        self.assertEqual(mo_coi, [], "Con ban ghi mo coi sau khi chot ket qua")

    def test_N13_phat_hien_ban_ghi_mo_coi(self):
        """N13: ham chan doan phai CHI RA duoc ban ghi mo coi."""
        self.assertTrue(hasattr(agent_ky_uc, "tim_ban_ghi_mo_coi"),
                        "Thieu ham tim_ban_ghi_mo_coi")
        self._ghi_so([
            _bg1("2026-10-02T11:45:09+07:00"),
            _bg2("2026-10-02T11:46:55+07:00"),   # da gui, thieu ket qua
            _bg1("2026-10-02T13:00:00+07:00", ma=MA2),
        ])
        ra = agent_ky_uc.tim_ban_ghi_mo_coi(duong_dan=str(self.p))
        self.assertEqual([str(r["doi_tuong"]["id"]) for r in ra], [MA])

    def test_khong_co_mo_coi_thi_rong(self):
        """Khi moi ban ghi da gui deu co ket qua -> danh sach rong."""
        self._ghi_so([
            _bg1("2026-10-02T11:45:09+07:00"),
            _bg2("2026-10-02T11:46:55+07:00", ket_qua="thanh cong"),
        ])
        self.assertEqual(agent_ky_uc.tim_ban_ghi_mo_coi(duong_dan=str(self.p)), [])

    def test_mot_ban_ghi_thi_giu_hanh_vi_cu(self):
        """Tuong thich nguoc: chi 1 ban ghi (so cu) van chot duoc nhu truoc."""
        self._ghi_so([_bg1("2026-10-02T11:45:09+07:00")])
        self.assertTrue(agent_ky_uc.cap_nhat_phan_hoi(
            MA, "tat:120250389649480509", "thanh cong", duong_dan=str(self.p)))
        ds = self._doc_so()
        self.assertEqual(ds[0]["ket_qua"], "thanh cong")

    def test_that_bai_ghi_vao_ban_ghi_da_gui(self):
        """`ghi_meta_that_bai` cung phai nam o ban ghi da gui (de Rao 8 bo qua)."""
        self._ghi_so([
            _bg1("2026-10-02T11:45:09+07:00"),
            _bg2("2026-10-02T11:46:55+07:00"),
        ])
        agent_ky_uc.cap_nhat_phan_hoi(
            MA, "tat:120250389649480509", "loi: Meta tu choi",
            duong_dan=str(self.p), ghi_meta_that_bai=True)
        ds = self._doc_so()
        b2 = next(r for r in ds if r["da_gui_len_meta"] is True)
        self.assertTrue(b2.get("ghi_meta_that_bai"))
        # Va Rao 8 van phai bo qua ban ghi nay.
        self.assertNotIn(MA, agent_ky_uc.nhom_da_tra_loi(duong_dan=str(self.p)))


# ===========================================================================
#  DEM HANH DONG — GHI CHU: da KIEM CHUNG la KHONG co loi
# ===========================================================================
#  Toi tung NGHI `dem_hanh_dong` dem gap doi (vi mot viec sinh 2 ban ghi) va
#  da viet kiem thu N15 cho gia thuyet do. Kiem thu do XANH NGAY TU DAU => gia
#  thuyet SAI. Ly do: `_la_hanh_dong_that()` doi hoi `da_gui_len_meta is True`,
#  ma ban ghi "luc hoi Dai" co `da_gui=False` => bi loai. Nen chi con 1 ban ghi
#  duoc dem cho moi viec. Do lai tren so that cung khop:
#      02/10: 10 hanh dong that | 10 nhom khac nhau
#      03/10:  5 hanh dong that |  5 nhom khac nhau
#  => KHONG sua gi. Cac bai duoi day giu lai de CANH, khong phai de sua.
class TestDemHanhDongKhongGapDoi(_CoSo):
    """Canh rang buoc: mot viec chi duoc dem MOT lan (khong phai loi can sua)."""

    def test_mot_nhom_hai_ban_ghi_dem_mot(self):
        goc = datetime(2026, 10, 2, 11, 50, tzinfo=GIO_VN)
        self._ghi_so([
            _bg1("2026-10-02T11:45:09+07:00"),
            _bg2("2026-10-02T11:46:55+07:00"),
        ])
        ra = agent_ky_uc.dem_hanh_dong(goc, duong_dan=str(self.p))
        self.assertEqual(ra["so_hanh_dong_gio_nay"], 1)
        self.assertEqual(ra["so_hanh_dong_hom_nay"], 1)

    def test_hai_nhom_khac_nhau_dem_hai(self):
        goc = datetime(2026, 10, 2, 11, 50, tzinfo=GIO_VN)
        self._ghi_so([
            _bg1("2026-10-02T11:45:09+07:00"),
            _bg2("2026-10-02T11:46:55+07:00"),
            _bg1("2026-10-02T11:46:28+07:00", ma=MA2),
            _bg2("2026-10-02T11:47:00+07:00", ma=MA2),
        ])
        ra = agent_ky_uc.dem_hanh_dong(goc, duong_dan=str(self.p))
        self.assertEqual(ra["so_hanh_dong_gio_nay"], 2)

    def test_viec_that_bai_lan_sau_van_dem(self):
        """Lan lam lai sau khi that bai la viec MOI -> phai dem."""
        goc = datetime(2026, 10, 2, 15, 0, tzinfo=GIO_VN)
        self._ghi_so([
            _bg1("2026-10-02T11:45:09+07:00"),
            _bg2("2026-10-02T11:46:55+07:00", ket_qua="loi: Meta tu choi"),
            _bg1("2026-10-02T14:00:00+07:00"),
            _bg2("2026-10-02T14:00:30+07:00"),
        ])
        ra = agent_ky_uc.dem_hanh_dong(goc, duong_dan=str(self.p))
        self.assertEqual(ra["so_hanh_dong_hom_nay"], 2)

    def test_ban_ghi_hoi_chua_tra_loi_khong_dem(self):
        """Ban ghi chi HOI Dai (chua gui Meta) khong phai hanh dong da lam."""
        goc = datetime(2026, 10, 2, 11, 50, tzinfo=GIO_VN)
        self._ghi_so([_bg1("2026-10-02T11:45:09+07:00")])
        ra = agent_ky_uc.dem_hanh_dong(goc, duong_dan=str(self.p))
        self.assertEqual(ra["so_hanh_dong_hom_nay"], 0)


# ===========================================================================
#  N10 / N11 — NGUON GOC
# ===========================================================================
class TestNguonGoc(_CoSo):
    def test_N10_ban_ghi_moi_co_nguon_goc(self):
        """N10: ham suy nguon goc tra dung gia tri moi."""
        self.assertTrue(hasattr(agent_ky_uc, "nguon_goc_cua"),
                        "Thieu ham nguon_goc_cua")
        r = _bg2("2026-10-02T11:46:55+07:00")
        r["nguon_goc"] = "agent_tu_hanh"
        self.assertEqual(agent_ky_uc.nguon_goc_cua(r), "agent_tu_hanh")

    def test_N11_ban_ghi_cu_suy_ra_nguon_goc(self):
        """N11: ban ghi CU khong co `nguon_goc` -> phai suy, khong de trong."""
        # Da gui len Meta + co cau tra loi cua Dai => Dai bam nut.
        r = _bg2("2026-10-02T11:46:55+07:00")
        self.assertNotIn("nguon_goc", r)
        self.assertEqual(agent_ky_uc.nguon_goc_cua(r), "dai_bam_nut")

        # Chua gui len Meta, chua co tra loi => moi la de xuat cho.
        r2 = _bg1("2026-10-02T11:45:09+07:00")
        self.assertEqual(agent_ky_uc.nguon_goc_cua(r2), "cho_duyet")

    def test_N11_ban_ghi_tu_hanh_cu_doan_duoc(self):
        """Ban ghi cu cua `bat_lai` (che_do=None) -> suy la Dai bam nut."""
        r = {"che_do": None, "hanh_dong": "bat_lai", "da_gui_len_meta": True,
             "dai_phan_hoi": "hoan_tac:120250506886650509",
             "luc": "2026-09-30T09:58:17+07:00"}
        self.assertEqual(agent_ky_uc.nguon_goc_cua(r), "dai_bam_nut")

    def test_khong_co_dau_hieu_gi_thi_rong(self):
        """Ban ghi rac -> tra chuoi rong, khong nem loi."""
        self.assertEqual(agent_ky_uc.nguon_goc_cua({}), "")
        self.assertEqual(agent_ky_uc.nguon_goc_cua(None), "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
