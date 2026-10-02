@echo off
chcp 65001 >nul
REM ============================================
REM  KHOI DONG LAI AGENT
REM ============================================
REM  File nay lam MOT viec: tat agent roi bat lai.
REM
REM  KHI NAO CAN BAM FILE NAY:
REM  Agent chi nap code MOT LAN luc khoi dong.
REM  Nen sau khi co BAN CODE MOI, phai khoi dong lai thi ban moi moi co tac dung.
REM  (Cac thay doi trong .env cung CAN bam file nay - TU 01/10/2026 agent da
REM   doc lai toan bo .env moi 15 giay, nen doi khoa AI / TELEGRAM / META
REM   cung co tac dung ngay ma khong can khoi dong lai. Truoc do thi khong.)
REM
REM  File nay goi lai hai file co san, khong tu lam gi khac:
REM    1. go-agent.bat       - tat agent
REM    2. cai-dat-agent.bat  - bat lai agent
REM ============================================

setlocal

echo.
echo ============================================
echo  KHOI DONG LAI AGENT
echo ============================================
echo.

echo --- Buoc 1/2: tat agent dang chay ---
call "%~dp0go-agent.bat" < nul

echo.
echo --- Buoc 2/2: bat lai agent ---
call "%~dp0cai-dat-agent.bat" < nul

echo.
echo ============================================
echo  XONG. Agent da chay ban moi nhat.
echo  Xem agent dang lam gi: mo file logs\baocao.log
echo ============================================
echo.

pause
