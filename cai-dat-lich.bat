@echo off
REM ============================================
REM CAI DAT LICH CHAY TU DONG CHO BAO CAO META ADS
REM ============================================
REM Chay file nay 1 lan duy nhat de tao 3 lich trong Windows Task Scheduler.
REM Sau khi chay xong, script se tu dong gui bao cao vao 8h, 12h, 17h hang ngay.
REM
REM CACH CHAY: bam dup chuot vao file nay
REM Neu bao loi quyen: chuot phai -> Run as administrator
REM
REM File nay TU DONG TIM PYTHON tren may, nen dung duoc cho ca may khac.
REM ============================================

setlocal

REM --- Tu dong tim Python ---
set PYTHON_EXE=

REM Uu tien 1: Python cua WorkBuddy (cung ten nguoi dung Windows)
if exist "C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe" set PYTHON_EXE=C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe

REM Uu tien 2: Tim Python trong PATH cua may
if not defined PYTHON_EXE (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set PYTHON_EXE=%%P
    )
)

REM Uu tien 3: Duong dan cai dat Python mac dinh
if not defined PYTHON_EXE if exist "C:\Python313\python.exe" set PYTHON_EXE=C:\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%report.py

echo.
echo ============================================
echo  CAI DAT LICH BAO CAO META ADS
echo ============================================
echo.

REM --- Kiem tra tim thay Python chua ---
if not defined PYTHON_EXE (
    echo LOI: Khong tim thay Python tren may nay!
    echo.
    echo Cach xu ly:
    echo   1. Cai Python tu python.org ^(ban 3.12 hoac 3.13^)
    echo   2. Hoac mo file nay bang Notepad, sua dong bat dau bang
    echo      "set PYTHON_EXE=" thanh duong dan Python tren may nay
    echo.
    pause
    exit /b 1
)

echo Python : %PYTHON_EXE%
echo Script : %SCRIPT_PATH%
echo.

REM --- Kiem tra file script ton tai ---
if not exist "%SCRIPT_PATH%" (
    echo LOI: Khong tim thay file report.py trong %SCRIPT_DIR%
    pause
    exit /b 1
)

REM --- Kiem tra file .env ton tai ---
if not exist "%SCRIPT_DIR%.env" (
    echo CANH BAO: Chua co file .env trong thu muc nay!
    echo.
    echo Cach xu ly:
    echo   1. Copy file .env.example thanh .env
    echo   2. Mo .env bang Notepad va dien token vao
    echo   3. Xem huong dan trong HUONG-DAN-DIEN-TOKEN.md
    echo.
    pause
    exit /b 1
)

REM --- Xoa lich cu neu co (de tranh trung) ---
for %%H in (08 12 17 22) do (
    schtasks /Delete /TN "BaoCaoMetaAds_%%H" /F >nul 2>&1
)
for %%H in (8 12 17 22) do (
    schtasks /Delete /TN "BaoCaoMetaAds_%%H" /F >nul 2>&1
)

echo Dang tao 3 lich...
echo.

REM Ngay 28/09/2026: bo moc 22h. Ly do: kiem tra logs/baocao.log cho thay moc 22h
REM CHUA TUNG chay mot lan nao (0 lan trong toan bo nhat ky), va khi may thuc day
REM buoi sang thi lich 22h chay bu va tu doan ra moc 8h -> gay bao cao trung.
call :TaoLich 08
call :TaoLich 12
call :TaoLich 17

REM --- Buoc 2: dat 3 thiet lap quan trong cho lich vua tao ---
REM Ly do (phat hien thuc te ngay 28/09/2026): cac lenh /Delete o tren XOA lich cu
REM roi tao lai, ma schtasks /Create KHONG dat StartWhenAvailable, WakeToRun va
REM AllowStartIfOnBatteries. Neu khong dat lai thi may ngu dung gio se KHONG chay bu
REM -> mat bao cao. Truoc day phai chay them bat-chay-bu.bat moi co; gio file nay
REM tu lam luon, nen chay lai bao nhieu lan cung khong bi mat.
echo Dang dat thiet lap chay bu + tu thuc may...
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo [CANH BAO] Chua chay bang quyen Admin, nen THIEU 3 thiet lap:
    echo   - chay bu khi may bat lai sau khi lo gio
    echo   - tu thuc may de chay bao cao dung gio
    echo   - cho phep chay khi may dung pin
    echo.
    echo Cach xu ly: dong cua so nay, chuot phai vao file nay,
    echo chon "Run as administrator", roi bam lai.
    echo Hoac chay rieng file bat-chay-bu.bat bang quyen Admin.
    echo.
) else (
    powershell -NoProfile -Command "$s = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 15); foreach ($n in @('BaoCaoMetaAds_08','BaoCaoMetaAds_12','BaoCaoMetaAds_17')) { try { Set-ScheduledTask -TaskName $n -Settings $s -ErrorAction Stop | Out-Null; Write-Host ('  [OK]  ' + $n + ' - da dat thiet lap') } catch { Write-Host ('  [LOI] ' + $n + ' - ' + $_.Exception.Message) } }"
    echo.
)

echo.
echo ============================================
echo  KIEM TRA LAI
echo ============================================
echo.

schtasks /Query /TN "BaoCaoMetaAds_08" >nul 2>&1
if errorlevel 1 (
    echo [CANH BAO] Khong tao duoc lich nao!
    echo.
    echo Nguyen nhan thuong gap:
    echo   1. Chua chay bang quyen Admin
    echo      -^> Chuot phai vao file nay, chon "Run as administrator"
    echo   2. Chinh sach cong ty chan Task Scheduler
    echo      -^> Lien he bo phan IT
    echo.
    pause
    exit /b 1
)

echo [OK] Da tao lich thanh cong.
echo.
echo Kiem tra lai thiet lap (ca hai phai la True):
powershell -NoProfile -Command "foreach ($n in @('BaoCaoMetaAds_08','BaoCaoMetaAds_12','BaoCaoMetaAds_17')) { $t = Get-ScheduledTask -TaskName $n -ErrorAction SilentlyContinue; if ($t) { Write-Host ('  ' + $n + ' : chay bu=' + $t.Settings.StartWhenAvailable + '  tu thuc=' + $t.Settings.WakeToRun) } else { Write-Host ('  ' + $n + ' : KHONG TIM THAY') } }"
echo.
echo Cac moc gio: 08:00, 12:00, 17:00 hang ngay
echo (Moc 22h da bo tu 28/09/2026 - xem ghi chu trong file nay)
echo.
echo Kiem tra nhat ky chay tai: logs\baocao.log
echo De XOA lich, chay file: go-lich.bat
echo.
pause
exit /b 0


REM ============================================
REM Ham tao 1 lich
REM ============================================
:TaoLich
set MOC=%~1
schtasks /Create /TN "BaoCaoMetaAds_%MOC%" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --slot %MOC%" /SC DAILY /ST %MOC%:00 /F >nul 2>&1
if errorlevel 1 (
    echo   [LOI] Moc %MOC%:00 - tao that bai
    echo         --- Chi tiet loi tu Windows: ---
    schtasks /Create /TN "BaoCaoMetaAds_%MOC%" /TR "\"%PYTHON_EXE%\" \"%SCRIPT_PATH%\" --slot %MOC%" /SC DAILY /ST %MOC%:00 /F
    echo         --------------------------------
) else (
    echo   [OK]  Moc %MOC%:00 - da tao
)
exit /b 0
