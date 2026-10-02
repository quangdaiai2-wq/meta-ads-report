@echo off
chcp 65001 >nul
REM ============================================
REM  CHUYEN AGENT SANG CHE DO LAM THAT
REM ============================================
REM  *** DOC KY TRUOC KHI BAM ***
REM  Sau khi bam file nay: agent se TU GUI LENH TAT NHOM len Meta.
REM  Tien that bi tac dong. Day la che do NGUY HIEM.
REM
REM  Truoc khi doi, can biet:
REM    1. Neu may KHAC cung dang chay THAT tren CUNG tai khoan Meta,
REM       hai may co the cung tac dong vao mot nhom.
REM    2. File nay hoi lai mot lan - phai go dung chu "co" moi doi.
REM
REM  File nay sua DUNG MOT DONG trong .env:  AGENT_TAP_SU=false
REM  Truoc khi sua, sao luu .env thanh .env.bak-truoc-doi-che-do.
REM ============================================

setlocal
set PYTHON_EXE=
set SCRIPT_DIR=%~dp0

if exist "C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe" set PYTHON_EXE=C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe
if not defined PYTHON_EXE (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set PYTHON_EXE=%%P
    )
)
if not defined PYTHON_EXE if exist "C:\Python313\python.exe" set PYTHON_EXE=C:\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe

if not defined PYTHON_EXE (
    echo LOI: Khong tim thay Python tren may nay.
    pause
    exit /b 1
)
if not exist "%SCRIPT_DIR%doi_che_do_agent.py" (
    echo LOI: Khong tim thay doi_che_do_agent.py trong: %SCRIPT_DIR%
    pause
    exit /b 1
)

pushd "%SCRIPT_DIR%"
echo.
echo ============================================
echo  CHUYEN SANG CHE DO LAM THAT
echo ============================================
echo.
"%PYTHON_EXE%" doi_che_do_agent.py
echo.
echo *** CANH BAO ***
echo Tu day agent se TU GUI LENH TAT NHOM len Meta.
echo Neu may khac cung dang chay THAT tren CUNG tai khoan Meta,
echo hai may co the cung tac dong vao mot nhom.
echo.
set /p XACNHAN=Go chu "co" roi bam Enter de xac nhan: 

if /i "%XACNHAN%"=="co" goto lamthat
echo.
echo Da huy - khong doi gi.
goto ketthuc

:lamthat
echo.
"%PYTHON_EXE%" doi_che_do_agent.py chay-that

:ketthuc
echo.
popd
pause
exit /b 0
