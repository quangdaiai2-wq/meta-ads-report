"""Kiem thu an toan cho script go Nguoi truc."""
import unittest
from pathlib import Path


SCRIPT = (Path(__file__).resolve().parents[1] / "go-nguoi-truc.bat").read_text(
    encoding="utf-8"
)


class TestGoNguoiTruc(unittest.TestCase):
    def test_go_duoc_python_va_pythonw_nhung_chi_dung_nguoi_truc(self):
        self.assertIn("Name -in @('python.exe','pythonw.exe')", SCRIPT)
        self.assertIn("GetFullPath($env:WATCHER_PATH)", SCRIPT)
        self.assertIn("$_.CommandLine -like ('*' + $scriptPath + '*')", SCRIPT)

    def test_xoa_va_xac_nhan_lich_truoc_khi_dung_tien_trinh(self):
        xoa_lich = SCRIPT.index("Unregister-ScheduledTask")
        xac_nhan_lich = SCRIPT.index("Get-ScheduledTask -TaskName 'NguoiTruc'", xoa_lich)
        dung_tien_trinh = SCRIPT.index("Stop-Process")
        self.assertLess(xoa_lich, xac_nhan_lich)
        self.assertLess(xac_nhan_lich, dung_tien_trinh)

    def test_khong_co_bo_loc_agent(self):
        self.assertNotIn("*agent.py*", SCRIPT)


if __name__ == "__main__":
    unittest.main()
