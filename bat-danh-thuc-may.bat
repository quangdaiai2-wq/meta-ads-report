@echo off
REM ============================================
REM BAT "CHO PHEP DANH THUC MAY"
REM ============================================
REM Muc dich: cho Windows TU THUC MAY de chay bao cao
REM           dung gio, ke ca khi may dang ngu.
REM
REM Vi sao can: Mac dinh Windows TAT tinh nang nay,
REM             nhat la khi may chay bang PIN -> bao cao bi lo.
REM
REM CAN CHAY BANG QUYEN ADMIN:
REM   Chuot phai vao file nay -> "Run as administrator"
REM
REM Chi can chay 1 lan.
REM ============================================

echo.
echo ============================================
echo  BAT "CHO PHEP DANH THUC MAY"
echo ============================================
echo.

REM --- Kiem tra quyen Admin ---
net session >nul 2>&1
if errorlevel 1 (
    echo [LOI] Ban chua chay bang quyen Admin.
    echo.
    echo Cach lam:
    echo   1. Dong cua so nay lai
    echo   2. Chuot phai vao file nay
    echo   3. Chon "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Da co quyen Admin. Dang bat...
echo.

echo [1/3] Cho phep danh thuc khi CAM SAC...
powercfg /SETACVALUEINDEX SCHEME_CURRENT SUB_SLEEP BD3B718A-0680-4D9D-8AB2-E1D2B4AC806D 1

echo [2/3] Cho phep danh thuc khi DUNG PIN...
powercfg /SETDCVALUEINDEX SCHEME_CURRENT SUB_SLEEP BD3B718A-0680-4D9D-8AB2-E1D2B4AC806D 1

echo [3/3] Ap dung thay doi...
powercfg /SETACTIVE SCHEME_CURRENT

echo.
echo ============================================
echo  KIEM TRA LAI
echo ============================================
echo Tim dong "Allow wake timers" - mong doi la "Enable".
echo.
powercfg /q SCHEME_CURRENT SUB_SLEEP

echo.
echo ============================================
echo  XONG
echo ============================================
echo Neu o tren thay "Enable" la THANH CONG.
echo.
echo LUU Y QUAN TRONG:
echo   - Cam SAC may thuong xuyen (dung de pin can).
echo   - KHONG tat may (chi de may ngu la duoc).
echo.
pause
