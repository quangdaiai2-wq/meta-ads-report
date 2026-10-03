@echo off
REM ============================================
REM KIEM TRA TOKEN META - TOKEN CA NHAN HAY TOKEN APP
REM ============================================
REM File nay lam MOT viec: cho Dai biet token trong .env hien tai la
REM token CA NHAN (Meta ghi ten Dai) hay token APP (Meta ghi ten he thong).
REM
REM Khi nao bam file nay:
REM   - Sau khi lam xong HUONG-DAN-LAY-TOKEN-APP.md, de kiem tra ket qua
REM   - Khi nghiem ngo bao cao doc so bat thuong
REM   - Khi token sap het han, muon biet con bao nhieu ngay
REM
REM Dac diem quan trong:
REM   - CHI DOC, KHONG GHI gi len Meta  -> chay bao nhieu lan cung duoc
REM   - KHONG gui tin nhan Telegram nao
REM   - KHONG ton luot AI nao
REM ============================================

setlocal

REM --- Tu dong tim Python (giong cac file .bat khac cua du an) ---
set PYTHON_EXE=

if exist "C:/Users/%USERNAME%/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" set PYTHON_EXE=C:/Users/%USERNAME%/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe

if not defined PYTHON_EXE (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set PYTHON_EXE=%%P
    )
)

if not defined PYTHON_EXE if exist "C:/Python313/python.exe" set PYTHON_EXE=C:/Python313/python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

set SCRIPT_DIR=%~dp0

if not defined PYTHON_EXE (
    echo.
    echo LOI: Khong tim thay Python tren may nay!
    echo.
    echo Cach xu ly: cai Python 3.13, hoac bao AI ho tro.
    echo.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%kiem_tra_token_app.py" (
    echo.
    echo LOI: Khong tim thay file kiem_tra_token_app.py
    echo Duong dan mong doi: %SCRIPT_DIR%kiem_tra_token_app.py
    echo.
    pause
    exit /b 1
)

echo Dang kiem tra token... (cho khoang 5 giay)
echo.
"%PYTHON_EXE%" "%SCRIPT_DIR%kiem_tra_token_app.py"
set KQ=%ERRORLEVEL%

echo.
echo ============================================================
if %KQ%==0 (
    echo  XONG. Doc phan KET LUAN o tren de biet ket qua.
) else (
    echo  CO VAN DE. Doc phan "Cach xu ly" o tren.
)
echo ============================================================
echo.
pause
exit /b %KQ%
