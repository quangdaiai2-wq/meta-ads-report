@echo off
chcp 65001 >nul
REM ============================================
REM  KHOI DONG LAI AGENT
REM ============================================
REM  File nay lam MOT viec: tat agent roi bat lai.
REM
REM  KHI NAO CAN BAM FILE NAY:
REM  Agent chi nap code va doc file cau hinh .env MOT LAN luc khoi dong.
REM  Nen sau khi co BAN CODE MOI, phai khoi dong lai thi ban moi moi co tac dung.
REM  (Rieng cac thay doi trong .env thi KHONG can bam file nay nua — tu 30/09/2026
REM   agent tu doc lai .env moi 15 giay, nen doi cau hinh la co tac dung ngay.)
REM
REM  File nay goi lai hai file co san, khong tu lam gi khac:
REM    1. go-agent.bat       — tat agent
REM    2. cai-dat-agent.bat  — bat lai agent
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
