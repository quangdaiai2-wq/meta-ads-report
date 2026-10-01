@echo off
chcp 65001 >nul
REM ============================================
REM  CHAY AGENT NAC 2 - XIN PHEP ROI MOI TAT NHOM
REM ============================================
REM  File nay lam MOT viec: bat agent chay nen.
REM
REM  Agent se tu thuc day theo nhip trong .env (mac dinh 30 phut), tu phat
REM  hien nhom quang cao cham nguong, roi XIN PHEP Dai qua Telegram.
REM  Dai tra loi "tat <ma>" thi agent moi gui lenh len Meta.
REM
REM  *** QUAN TRONG - DOC KY ***
REM  Mac dinh agent dang o CHE DO TAP SU (AGENT_TAP_SU=true):
REM    -> agent CHI NOI, KHONG gui lenh nao len Meta.
REM    -> Dai cu de vay 1-2 tuan, doi chieu xem agent doan dung bao nhieu
REM       phan tram, roi moi cho no cam quyen that.
REM  Muon agent lam THAT: bam mo-file-env.bat, doi dong
REM       AGENT_TAP_SU=true   thanh   AGENT_TAP_SU=false
REM
REM  Cua so nay phai de MO. Dong cua so = tat agent.
REM  Muon chay thu truoc, khong gui gi: mo Command Prompt tai thu muc nay
REM  roi go:  python agent.py --thu
REM ============================================

setlocal

set PYTHON_EXE=

if exist "C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe" set PYTHON_EXE=C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe

if not defined PYTHON_EXE (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set PYTHON_EXE=%%P
    )
)

if not defined PYTHON_EXE if exist "C:\Python313\python.exe" set PYTHON_EXE=C:\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe

set SCRIPT_DIR=%~dp0

if not defined PYTHON_EXE (
    echo LOI: Khong tim thay Python tren may nay!
    echo Mo file nay bang Notepad, sua dong "set PYTHON_EXE=" thanh duong dan Python.
    pause
    exit /b 1
)

if not exist "%SCRIPT_DIR%agent.py" (
    echo LOI: Khong tim thay agent.py trong: %SCRIPT_DIR%
    echo File nay phai nam ngay trong thu muc du an.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  AGENT NAC 2 DANG CHAY
echo ============================================
echo  Python : %PYTHON_EXE%
echo  Thu muc: %SCRIPT_DIR%
echo.
echo  De cua so nay MO. Dong cua so = tat agent.
echo  Tat agent bang cach bam Ctrl + C, roi bam Y.
echo ============================================
echo.

pushd "%SCRIPT_DIR%"
"%PYTHON_EXE%" agent.py
popd

echo.
echo Agent da dung.
pause
