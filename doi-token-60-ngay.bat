@echo off
REM ============================================
REM DOI TOKEN NGAN HAN THANH TOKEN 60 NGAY
REM ============================================
REM File nay lam MOT viec: doi token vua lay tu Graph API Explorer
REM (token do chi song 1-2 gio) thanh token song 60 ngay.
REM
REM VI SAO BAT BUOC PHAI LAM: neu dan thang token ngan han vao he thong
REM thi hom sau bao cao se loi. Da gap that ngay 14/09/2026: token chi
REM song 1 gio 44 phut ma bai kiem tra van bao DAT.
REM
REM TRUOC KHI BAM FILE NAY, trong .env phai co du 3 dong:
REM   META_ADS_ACCESS_TOKEN=<token ngan han vua lay>
REM   META_APP_ID=...
REM   META_APP_SECRET=...
REM
REM File nay TU GHI token moi vao .env, va TU SAO LUU file cu thanh .env.bak.
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
echo  DOI TOKEN NGAN HAN -> TOKEN 60 NGAY
echo ============================================
echo.
echo Python : %PYTHON_EXE%
echo.
echo Dang doi token, cho khoang 10 giay...
echo.

pushd "%SCRIPT_DIR%"
"%PYTHON_EXE%" doi-token-60-ngay.py
set KQ=%ERRORLEVEL%
popd

echo.
echo ============================================
if "%KQ%"=="0" goto XONG
goto LOI

:XONG
echo  [OK]  DA DOI TOKEN 60 NGAY
echo.
echo  Buoc tiep theo: bam dup file kiem-tra-quyen-ghi.bat
echo  de kiem tra token moi co quyen GHI chua.
goto KET_THUC

:LOI
echo  [LOI]  DOI TOKEN KHONG THANH CONG
echo.
echo  Cach xu ly: doc dong bao loi o phan tren.
echo  Neu bao thieu META_APP_ID / META_APP_SECRET: bam dup mo-file-env.bat
echo  roi dien cho du.
echo  Neu van khong duoc: chup man hinh roi gui cho AI.
goto KET_THUC

:KET_THUC
echo ============================================
echo.

pause
exit /b %KQ%
