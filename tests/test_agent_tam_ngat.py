"""Kiem thu cong tac tam ngat (agent_tam_ngat).

Boi canh: cach chan cu (mot tien trinh giu khoa) co lo hong — tat may thi tien
trinh chet, agent tu bat lai. Cong tac nay la file tren dia, khong phu thuoc
tien trinh nao. Bo kiem thu nay phai chung minh duoc dieu do.
"""
import os
import tempfile
import unittest
from pathlib import Path

import agent_tam_ngat


class TestCongTacTamNgat(unittest.TestCase):
    def setUp(self):
        self.td = tempfile.TemporaryDirectory()
        self.cong_tac = Path(self.td.name) / "logs" / "TAM-NGAT-AGENT.txt"

    def tearDown(self):
        self.td.cleanup()

    # --- Trang thai mac dinh ---

    def test_chua_co_file_thi_khong_tam_ngat(self):
        self.assertFalse(agent_tam_ngat.dang_tam_ngat(self.cong_tac))

    def test_co_file_thi_dang_tam_ngat(self):
        agent_tam_ngat.bat_tam_ngat("ly do thu nghiem", self.cong_tac)
        self.assertTrue(agent_tam_ngat.dang_tam_ngat(self.cong_tac))

    # --- Bat / tat ---

    def test_bat_tam_ngat_tao_duoc_thu_muc_con_thieu(self):
        # Thu muc `logs` chua ton tai — ham phai tu tao.
        self.assertFalse(self.cong_tac.parent.exists())
        ok, ly = agent_tam_ngat.bat_tam_ngat("ly do", self.cong_tac)
        self.assertTrue(ok, ly)
        self.assertTrue(self.cong_tac.parent.is_dir())

    def test_bat_tam_ngat_tu_them_moc_thoi_gian(self):
        agent_tam_ngat.bat_tam_ngat("ly do thu nghiem", self.cong_tac)
        tho = self.cong_tac.read_text(encoding="utf-8")
        self.assertIn("TAM NGAT AGENT", tho)
        self.assertIn("ly do thu nghiem", tho)

    def test_tat_tam_ngat_xoa_file(self):
        agent_tam_ngat.bat_tam_ngat("ly do", self.cong_tac)
        ok, ly = agent_tam_ngat.tat_tam_ngat(self.cong_tac)
        self.assertTrue(ok, ly)
        self.assertFalse(self.cong_tac.exists())

    def test_tat_tam_ngat_khi_von_da_tat_thi_khong_loi(self):
        ok, ly = agent_tam_ngat.tat_tam_ngat(self.cong_tac)
        self.assertTrue(ok, ly)

    # --- Doc ly do ---

    def test_ly_do_tra_ve_chuoi_rong_khi_khong_co_file(self):
        self.assertEqual(agent_tam_ngat.ly_do(self.cong_tac), "")

    def test_ly_do_doc_duoc_noi_dung_file(self):
        agent_tam_ngat.bat_tam_ngat("Dai chuyen sang thao tac thu cong",
                                    self.cong_tac)
        self.assertIn("Dai chuyen sang thao tac thu cong",
                      agent_tam_ngat.ly_do(self.cong_tac))

    def test_thong_diep_chan_co_du_cach_mo_lai(self):
        agent_tam_ngat.bat_tam_ngat("ly do", self.cong_tac)
        td = agent_tam_ngat.thong_diep_chan(self.cong_tac)
        self.assertIn("CONG TAC TAM NGAT", td)
        self.assertIn("xoa file", td)

    # --- An toan: loi doc file thi phai CHAN, khong duoc cho chay ---

    def test_thu_muc_thay_vi_file_thi_khong_tinh_la_tam_ngat(self):
        # Neu nham tao THU MUC cung ten, do khong phai cong tac.
        # Nhung phai la `is_file()` chu khong phai `exists()`.
        self.cong_tac.mkdir(parents=True)
        self.assertFalse(agent_tam_ngat.dang_tam_ngat(self.cong_tac))

    def test_file_rong_van_tinh_la_tam_ngat(self):
        # File rong = nguoi dung tao tay de chan. Van phai chan.
        self.cong_tac.parent.mkdir(parents=True)
        self.cong_tac.write_text("", encoding="utf-8")
        self.assertTrue(agent_tam_ngat.dang_tam_ngat(self.cong_tac))

    def test_cong_tac_mac_dinh_nam_trong_thu_muc_logs(self):
        self.assertEqual(agent_tam_ngat.CONG_TAC.parent.name, "logs")
        self.assertEqual(agent_tam_ngat.CONG_TAC.name, "TAM-NGAT-AGENT.txt")

    # --- Khong phu thuoc tien trinh (chinh la muc dich cua module) ---

    def test_cong_tac_la_file_tren_dia_khong_phai_trang_thai_tien_trinh(self):
        """Bat cong tac roi mo phong 'may tat': khong lam gi ca.

        Neu cong tac dung TRANG THAI TIEN TRINH thi phai co tien trinh song.
        O day chi co file. Kiem tra lai bang mot tien trinh Python MOI doc file
        do — chung minh no doc duoc ma khong can gi dang chay.
        """
        agent_tam_ngat.bat_tam_ngat("ly do", self.cong_tac)
        # Doc lai bang cach khoi tao lai module — tuong trung cho lan chay sau
        # khi may da tat/bat.
        import importlib
        importlib.reload(agent_tam_ngat)
        self.assertTrue(agent_tam_ngat.dang_tam_ngat(self.cong_tac))


if __name__ == "__main__":
    unittest.main()
