@echo off
chcp 65001 >nul
REM ============================================
REM  CHUYEN AGENT SANG CHE DO TAP SU
REM ============================================
REM  Sau khi bam file nay: agent CHI NOI, KHONG gui lenh nao len Meta.
REM  Day la che do AN TOAN - bam nham cung khong lam gi xau.
REM
REM  File nay sua DUNG MOT DONG trong .env:  AGENT_TAP_SU=true
REM  Truoc khi sua, sao luu .env thanh .env.bak-truoc-doi-che-do.
REM  Sau khi sua, agent tu doc lai trong 15 giay - khong can khoi dong lai.
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
echo  CHUYEN SANG CHE DO TAP SU
echo ============================================
echo.
"%PYTHON_EXE%" doi_che_do_agent.py
echo.
"%PYTHON_EXE%" doi_che_do_agent.py tap-su
echo.
popd
pause
exit /b 0
