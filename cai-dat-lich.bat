@echo off
REM ============================================
REM CAI DAT LICH CHAY TU DONG CHO BAO CAO META ADS
REM ============================================
REM Chay file nay 1 lan duy nhat de tao 4 lich trong Windows Task Scheduler.
REM Sau khi chay xong, script se tu dong gui bao cao vao 8h, 12h, 17h, 22h hang ngay.
REM
REM CACH CHAY: bam dup chuot vao file nay
REM Neu bao loi quyen: chuot phai -> Run as administrator
REM ============================================

setlocal

REM --- Duong dan ---
set PYTHON_EXE=C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe
set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%report.py

echo.
echo ============================================
echo  CAI DAT LICH BAO CAO META ADS
echo ============================================
echo.
echo Python : %PYTHON_EXE%
echo Script : %SCRIPT_PATH%
echo.

REM --- Kiem tra file ton tai ---
if not exist "%PYTHON_EXE%" (
    echo LOI: Khong tim thay Python tai %PYTHON_EXE%
    echo Hay sua lai duong dan trong file nay.
    pause
    exit /b 1
)

if not exist "%SCRIPT_PATH%" (
    echo LOI: Khong tim thay file report.py trong %SCRIPT_DIR%
    pause
    exit /b 1
)

REM --- Xoa lich cu neu co (de tranh trung) ---
for %%H in (08 12 17 22) do (
    schtasks /Delete /TN "BaoCaoMetaAds_%%H" /F >nul 2>&1
)

echo Dang tao 4 lich...
echo.

call :TaoLich 08
call :TaoLich 12
call :TaoLich 17
call :TaoLich 22

echo.
echo ============================================
echo  KIEM TRA LAI
echo ============================================
echo.

schtasks /Query /TN "BaoCaoMetaAds_08" >nul 2>&1
if errorlevel 1 (
    echo [CANH BAO] Khong tao duoc lich nao!
    echo.
    echo Nguyen nhan thuong gap:
    echo   1. Chua chay bang quyen Admin
    echo      -^> Chuot phai vao file nay, chon "Run as administrator"
    echo   2. Chinh sach cong ty chan Task Scheduler
    echo      -^> Lien he bo phan IT
    echo.
    pause
    exit /b 1
)

echo [OK] Da tao lich thanh cong.
echo.
echo Cac moc gio: 08:00, 12:00, 17:00, 22:00 hang ngay
echo.
echo Kiem tra nhat ky chay tai: logs\baocao.log
echo De XOA lich, chay file: go-lich.bat
echo.
pause
exit /b 0


REM ============================================
REM Ham tao 1 lich
REM ============================================
:TaoLich
set MOC=%~1
schtasks /Create /TN "BaoCaoMetaAds_%MOC%" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" /SC DAILY /ST %MOC%:00 /F >nul 2>&1
if errorlevel 1 (
    echo   [LOI] Moc %MOC%:00 - tao that bai
    echo         --- Chi tiet loi tu Windows: ---
    schtasks /Create /TN "BaoCaoMetaAds_%MOC%" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\"" /SC DAILY /ST %MOC%:00 /F
    echo         --------------------------------
) else (
    echo   [OK]  Moc %MOC%:00 - da tao
)
exit /b 0
