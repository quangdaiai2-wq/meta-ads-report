@echo off
REM ============================================
REM DOI CHIEU SO CUA AGENT VOI NHAT KY META
REM ============================================
REM File nay lam MOT viec: in ra bang doi chieu de tra loi cau hoi
REM "viec nay AI LAM - may hay Dai?".
REM
REM VI SAO CAN:
REM   Dai khong phai chu tai khoan doanh nghiep Meta, vai tro la EMPLOYEE
REM   nen KHONG tao duoc System User => khong co "token App". Moi thao tac
REM   gui len Meta deu mang ten chu token ca nhan la "Nam Duc Pham".
REM   Nghia la NHAT KY META KHONG PHAN BIET DUOC nguoi va may.
REM   => Phai doi chieu voi so cua agent.
REM
REM AN TOAN TUYET DOI:
REM   - CHI DOC. Khong tat, khong sua, khong tao gi tren Meta.
REM   - Khong gui tin nhan Telegram nao.
REM   - Khong sua file so cua agent.
REM   Bam bao nhieu lan cung duoc, khong so hong gi.
REM
REM Khi nao bam file nay:
REM   - Khi muon biet viec nao may lam, viec nao Dai lam tay
REM   - Khi nghi agent ghi so sai, hoac nghi co nguoi khac vao tai khoan
REM ============================================

setlocal

REM --- Tu dong tim Python (giong chay-kiem-thu.bat) ---
set PYTHON_EXE=

if exist "C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe" set PYTHON_EXE=C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe

if not defined PYTHON_EXE (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set PYTHON_EXE=%%P
    )
)

if not defined PYTHON_EXE if exist "C:\Python313\python.exe" set PYTHON_EXE=C:\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

set SCRIPT_DIR=%~dp0

echo.
echo ============================================
echo  DOI CHIEU SO AGENT VOI NHAT KY META
echo ============================================
echo.

if not defined PYTHON_EXE (
    echo LOI: Khong tim thay Python tren may nay!
    echo.
    echo Cach xu ly: cai Python tu python.org, hoac nho AI ho tro.
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%doi_chieu_meta.py" (
    echo LOI: Khong tim thay file "doi_chieu_meta.py" trong:
    echo   %SCRIPT_DIR%
    echo.
    echo Cach xu ly: file nay phai nam ngay trong thu muc du an.
    echo.
    pause
    exit /b 1
)

echo Python : %PYTHON_EXE%
echo Thu muc: %SCRIPT_DIR%
echo.
echo Dang doc nhat ky Meta, cho khoang 10-30 giay...
echo.

pushd "%SCRIPT_DIR%"
"%PYTHON_EXE%" doi_chieu_meta.py --ngay 7
set KQ=%ERRORLEVEL%
popd

echo.
echo ============================================
if "%KQ%"=="0" (
    echo  [OK]  DA IN XONG BANG DOI CHIEU
    echo.
    echo  Doc phan "KET LUAN" o tren cung:
    echo    - Muc KHOP            : ca so lan Meta deu co
    echo    - Muc CHI CO TREN META: Dai tu lam tay, khong qua agent
    echo    - Muc CHI CO TRONG SO : nghi van, nho AI xem
    echo    - Muc MO COI          : dau vet loi cu, nho AI xem
) else (
    echo  [LOI] KHONG CHAY DUOC
    echo.
    echo  Cach xu ly: chup man hinh phan phia tren roi gui cho AI.
)
echo ============================================
echo.

pause
exit /b %KQ%
