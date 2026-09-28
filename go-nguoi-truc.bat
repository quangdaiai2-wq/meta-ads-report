@echo off
REM ============================================
REM TAT NGUOI TRUC
REM ============================================
REM File nay lam hai viec:
REM   1. Xoa lich Windows "NguoiTruc"
REM   2. Dung tien trinh nguoi_truc.py dang chay (neu co)
REM
REM Sau khi chay file nay, he thong NGUNG gui bao cao hoan toan.
REM Muon quay lai cach cu (3 lich): bam cai-dat-lich.bat
REM ============================================

echo.
echo ============================================
echo  TAT NGUOI TRUC
echo ============================================
echo.

REM --- Buoc 1: xoa lich ---
schtasks /Delete /TN "NguoiTruc" /F >nul 2>&1
if errorlevel 1 (
    echo   [--]  Lich NguoiTruc khong ton tai
) else (
    echo   [XOA] Da xoa lich NguoiTruc
)

REM --- Buoc 2: dung tien trinh dang chay ---
REM Tim tien trinh python co dong lenh chua nguoi_truc.py.
REM Chi dung dau nhay DON trong lenh PowerShell nay, de khong dinh bay dau nhay
REM cua cmd (bai hoc tu cai-dat-lich.bat ngay 28/09/2026).
echo Dang dung tien trinh nguoi_truc.py...
powershell -NoProfile -Command "$ds = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*nguoi_truc.py*' }; if (-not $ds) { Write-Host '  [--]  Khong co tien trinh nao dang chay' } else { foreach ($d in $ds) { try { Stop-Process -Id $d.ProcessId -Force -ErrorAction Stop; Write-Host ('  [XOA] Da dung tien trinh PID ' + $d.ProcessId) } catch { Write-Host ('  [LOI] Khong dung duoc PID ' + $d.ProcessId) } } }"

echo.
echo Da tat Nguoi truc.
echo.
echo Neu van thay bao cao gui ve, mo Task Manager (Ctrl+Shift+Esc),
echo tim tien trinh python.exe dang chay nguoi_truc.py va bam End task.
echo.
pause
exit /b 0
