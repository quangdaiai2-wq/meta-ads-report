@echo off
REM ============================================
REM CHAY BO KIEM THU TU DONG
REM ============================================
REM File nay lam MOT viec: chay 392 bai kiem tra cua chuong trinh
REM de biet code con dung hay khong.
REM
REM Dac diem quan trong:
REM   - KHONG gui tin nhan Telegram nao
REM   - KHONG goi Meta, KHONG goi AI  -> KHONG ton luot mien phi
REM   - KHONG sua so lieu, KHONG dung toi lich Windows
REM   - Chay xong tu bao DAT hay HONG
REM
REM Khi nao bam file nay:
REM   - Sau khi nho AI sua code (de chac khong lam hong cho nao khac)
REM   - Khi nghiem ngo bao cao co gi do bat thuong
REM ============================================

setlocal

REM --- Tu dong tim Python (giong cai-dat-nguoi-truc.bat) ---
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
echo  CHAY BO KIEM THU TU DONG
echo ============================================
echo.

if not defined PYTHON_EXE (
    echo LOI: Khong tim thay Python tren may nay!
    echo.
    echo Cach xu ly:
    echo   1. Cai Python tu python.org ^(ban 3.12 hoac 3.13^)
    echo   2. Hoac mo file nay bang Notepad, sua dong bat dau bang
    echo      "set PYTHON_EXE=" thanh duong dan Python tren may nay
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%tests" (
    echo LOI: Khong tim thay thu muc "tests" trong:
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
echo Dang chay kiem thu, cho khoang 5 giay...
echo.

pushd "%SCRIPT_DIR%"
"%PYTHON_EXE%" -m unittest discover -s tests -t .
set KQ=%ERRORLEVEL%
popd

echo.
echo ============================================
if "%KQ%"=="0" (
    echo  [OK]  TAT CA DEU DAT - chuong trinh binh thuong
    echo.
    echo  Khong co gi phai lam them.
) else (
    echo  [LOI] CO BAI KIEM THU THAT BAI
    echo.
    echo  Cach xu ly: chup man hinh phan phia tren roi gui cho AI.
    echo  Dung tu sua gi.
)
echo ============================================
echo.

pause
exit /b %KQ%
