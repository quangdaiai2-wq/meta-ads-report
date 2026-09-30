@echo off
REM ============================================
REM KIEM TRA QUYEN GHI CUA TOKEN META
REM ============================================
REM File nay tra loi MOT cau hoi:
REM   Token Meta hien tai co quyen TAM DUNG chien dich quang cao khong?
REM
REM Dac diem quan trong:
REM   - CHI DOC. KHONG tao, KHONG sua, KHONG xoa gi trong tai khoan quang cao.
REM   - KHONG gui tin nhan Telegram nao.
REM   - KHONG ton luot AI.
REM
REM Khi nao bam file nay:
REM   - Sau khi vua lay token Meta moi (de biet da co quyen ghi chua)
REM   - Khi he thong bao loi lien quan toi quyen
REM ============================================

setlocal

REM --- Tu dong tim Python (giong cai-dat-nguoi-truc.bat) ---
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
    echo LOI: Khong tim thay Python tren may nay!
    echo.
    echo Cach xu ly: mo file nay bang Notepad, sua dong bat dau bang
    echo   "set PYTHON_EXE=" thanh duong dan Python tren may nay.
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  KIEM TRA QUYEN GHI CUA TOKEN META
echo ============================================
echo.
echo Python : %PYTHON_EXE%
echo.
echo Dang kiem tra, cho khoang 5 giay...
echo.

pushd "%SCRIPT_DIR%"
"%PYTHON_EXE%" kiem-tra-quyen-ghi.py
set KQ=%ERRORLEVEL%
popd

echo.
echo ============================================
if "%KQ%"=="0" goto CO_QUYEN
if "%KQ%"=="3" goto CHUA_CO
goto LOI

:CO_QUYEN
echo  [OK]  TOKEN DA CO QUYEN GHI
echo.
echo  Buoc tiep theo: nhan tin cho tro ly AI biet tin nay.
echo  (Viec dau tien se lam la kiem chung that: tat thu MOT chien dich
echo   ma Dai da dong y tat.)
goto KET_THUC

:CHUA_CO
echo  [CHUA CO]  TOKEN CHUA CO QUYEN GHI
echo.
echo  Nghia la: he thong CHUA the tam dung chien dich nao.
echo  Cach xu ly: lam theo file HUONG-DAN-LAY-TOKEN-QUYEN-GHI.md
goto KET_THUC

:LOI
echo  [LOI]  KHONG KIEM TRA DUOC
echo.
echo  Cach xu ly: chup man hinh phan phia tren roi gui cho AI.
echo  Dung tu sua gi.
goto KET_THUC

:KET_THUC
echo ============================================
echo.

pause
exit /b %KQ%
