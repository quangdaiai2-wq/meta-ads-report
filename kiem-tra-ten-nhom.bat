@echo off
chcp 65001 >nul
REM ============================================
REM  KIEM TRA TEN NHOM CO DUNG CHUAN KHONG
REM ============================================
REM  File nay CHI DOC, KHONG gui lenh nao len Meta.
REM
REM  No tim nhung nhom co hau to ten SAI - thieu nam.
REM  Vi du SAI:  '... 0/350 X10 TN'   (thieu -26)
REM  Vi du DUNG: '... 0/350 X10-26 TN'
REM
REM  Loi nay xay ra khi agent chay BAN CODE CU.
REM  Agent chi nap code MOT LAN luc khoi dong => sau khi sua code
REM  PHAI bam  khoi-dong-lai-agent.bat  thi ban moi moi co tac dung.
REM
REM  Cach chay: bam dup file nay. Xem ket qua, roi bam phim bat ky de dong.
REM ============================================

setlocal
cd /d "%~dp0"

echo.
echo ============================================
echo  KIEM TRA TEN NHOM
echo ============================================
echo.

set PY=C:\Users\nguye\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe
if not exist "%PY%" set PY=python

"%PY%" "%~dp0kiem-tra-ten-nhom.py"

echo.
echo ============================================
pause
