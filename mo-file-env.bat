@echo off
REM ============================================
REM MO FILE .env BANG NOTEPAD
REM ============================================
REM File .env la file BI MAT: chua token Telegram, token Meta, chia khoa AI.
REM
REM CACH DUNG: bam dup chuot vao file nay -> Notepad mo .env ra.
REM Sua xong: bam Ctrl + S de luu, roi dong cua so Notepad.
REM
REM LUU Y QUAN TRONG:
REM   - File can sua ten dung la ".env"
REM     (khong co duoi .txt, khong phai .bak, khong phai .example)
REM   - Trong thu muc con 3 file giong giong, DUNG SUA NHAM:
REM       .env.example         = ban mau, khong phai file that
REM       .env.bak             = ban sao luu cu
REM       .env.bak-truoc-gd2   = ban sao luu cu
REM   - KHONG doi ten file, KHONG luu thanh .env.txt
REM   - KHONG gui file nay qua Zalo / Telegram / email
REM ============================================

setlocal
set TEP=%~dp0.env

echo.
echo ============================================
echo  MO FILE .env
echo ============================================
echo.
echo Duong dan: %TEP%
echo.

if not exist "%TEP%" (
    echo LOI: Khong tim thay file .env trong thu muc nay.
    echo.
    echo Cach xu ly: copy file .env.example thanh .env roi bam lai file nay.
    echo   Lenh copy ^(mo cua so lenh tai thu muc nay^):
    echo       copy .env.example .env
    echo.
    pause
    exit /b 1
)

echo Dang mo bang Notepad...
echo.
echo Sau khi sua xong:
echo   1. Bam Ctrl + S de luu
echo   2. Dong cua so Notepad
echo.
echo CANH BAO: chi sua file ".env". Dung sua .env.example / .env.bak
echo.
start "" notepad "%TEP%"
exit /b 0
