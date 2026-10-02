@echo off
chcp 65001 >nul
REM ============================================
REM  KHOI DONG LAI NGUOI TRUC
REM ============================================
REM  File nay lam MOT viec: tat nguoi truc roi bat lai.
REM
REM  KHI NAO CAN BAM:
REM  Nguoi truc chi nap code MOT LAN luc khoi dong. Sau khi co BAN CODE MOI
REM  thi phai khoi dong lai thi ban moi moi co tac dung.
REM
REM  Neu bi bao loi quyen: chuot phai vao file nay, chon
REM  "Run as administrator", roi bam lai.
REM
REM  File nay goi lai hai file co san:
REM    1. go-nguoi-truc.bat      - tat nguoi truc
REM    2. cai-dat-nguoi-truc.bat - bat lai nguoi truc
REM ============================================

setlocal

echo.
echo ============================================
echo  KHOI DONG LAI NGUOI TRUC
echo ============================================
echo.

echo --- Buoc 1/2: tat nguoi truc dang chay ---
call "%~dp0go-nguoi-truc.bat" < nul

echo.
echo --- Buoc 2/2: bat lai nguoi truc ---
call "%~dp0cai-dat-nguoi-truc.bat" < nul

echo.
echo ============================================
echo  XONG. Nguoi truc da chay ban moi nhat.
echo  Kiem tra: mo file logs\baocao.log, tim dong
echo  "NGUOI TRUC: bat dau"
echo ============================================
echo.

pause
