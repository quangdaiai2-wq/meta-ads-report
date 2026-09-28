@echo off
REM ============================================
REM CAI DAT NGUOI TRUC - thay 3 lich bang 1 tien trinh chay suot
REM ============================================
REM File nay lam BA viec:
REM   1. Tao MOT lich Windows ten "NguoiTruc", chay khi dang nhap.
REM   2. XOA ba lich cu (BaoCaoMetaAds_08/12/17) - co ly do:
REM      de hai lich cung song la co hai nguon gui bao cao, se bi trung.
REM   3. Kiem tra lai bang cach doc lich vua tao (khong tin dong [OK]).
REM
REM CACH CHAY: bam dup chuot vao file nay
REM Neu bao loi quyen: chuot phai -> Run as administrator
REM
REM Chay lai file nay bao nhieu lan cung duoc - no tu xoa lich cu roi tao lai.
REM ============================================

setlocal

REM --- Tu dong tim Python (giong cai-dat-lich.bat) ---
set PYTHON_EXE=

if exist "C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe" set PYTHON_EXE=C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\python.exe

if not defined PYTHON_EXE (
    for /f "delims=" %%P in ('where python 2^>nul') do (
        if not defined PYTHON_EXE set PYTHON_EXE=%%P
    )
)

if not defined PYTHON_EXE if exist "C:\Python313\python.exe" set PYTHON_EXE=C:\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe
if not defined PYTHON_EXE if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe

set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%nguoi_truc.py
set TASK_NAME=NguoiTruc

echo.
echo ============================================
echo  CAI DAT NGUOI TRUC
echo ============================================
echo.

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

if not exist "%SCRIPT_PATH%" (
    echo LOI: Khong tim thay file nguoi_truc.py trong %SCRIPT_DIR%
    pause
    exit /b 1
)

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

echo Python : %PYTHON_EXE%
echo Script : %SCRIPT_PATH%
echo.

REM --- Kiem tra .env co khoa REPORT_SLOTS khong ---
REM Neu thieu thi he thong dung mac dinh 8,12,17,22 -> moc 22h quay tro lai
REM tren may cong ty. Canh bao truoc de Dai biet.
findstr /B /C:"REPORT_SLOTS=" "%SCRIPT_DIR%.env" >nul 2>&1
if errorlevel 1 (
    echo [CANH BAO] File .env CHUA co dong REPORT_SLOTS=
    echo   He thong se dung mac dinh 8,12,17,22, tuc la MOC 22H QUAY TRO LAI.
    echo   Cach xu ly: mo .env bang Notepad, them mot dong:
    echo       REPORT_SLOTS=8,12,17
    echo   roi bam lai file nay.
    echo.
)

REM --- Buoc 1: xoa lich NguoiTruc cu neu co ---
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1

REM --- Buoc 2: xoa ba lich cu (BaoCaoMetaAds_08/12/17/22 va dang khong co so 0) ---
echo Dang tat ba lich cu...
for %%H in (08 12 17 22 8) do (
    schtasks /Delete /TN "BaoCaoMetaAds_%%H" /F >nul 2>&1
    if errorlevel 1 (
        echo   [--]  Lich cu BaoCaoMetaAds_%%H khong ton tai
    ) else (
        echo   [XOA] Da xoa lich cu BaoCaoMetaAds_%%H
    )
)
echo.

REM --- Buoc 3: tao lich NguoiTruc bang PowerShell ---
REM Duong dan duoc truyen qua BIEN MOI TRUONG, khong nhung vao chuoi lenh,
REM nen khong dinh bay dau nhay (bai hoc tu cai-dat-lich.bat ngay 28/09/2026).
echo Dang tao lich "%TASK_NAME%"...
powershell -NoProfile -Command "$py=$env:PYTHON_EXE; $sp=$env:SCRIPT_PATH; $wd=$env:SCRIPT_DIR; $a = New-ScheduledTaskAction -Execute $py -Argument ([char]34 + $sp + [char]34) -WorkingDirectory $wd; $t = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME; $s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -RestartInterval (New-TimeSpan -Minutes 5) -RestartCount 3 -MultipleInstances IgnoreNew; try { Register-ScheduledTask -TaskName 'NguoiTruc' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null; Write-Host '  [OK]  Da tao lich NguoiTruc' } catch { Write-Host ('  [LOI] ' + $_.Exception.Message) }"

echo.
echo ============================================
echo  KIEM TRA LAI (doc lai lich, khong tin dong [OK])
echo ============================================
echo.

powershell -NoProfile -Command "$t = Get-ScheduledTask -TaskName 'NguoiTruc' -ErrorAction SilentlyContinue; if (-not $t) { Write-Host '  [LOI] KHONG TIM THAY lich NguoiTruc.'; Write-Host '  Cach xu ly: chuot phai vao file nay, chon Run as administrator, roi bam lai.' } else { Write-Host ('  Ten lich    : ' + $t.TaskName); Write-Host ('  Trang thai  : ' + $t.State); foreach ($a in $t.Actions) { Write-Host ('  Chuong trinh: ' + $a.Execute); Write-Host ('  Tham so     : ' + $a.Arguments); Write-Host ('  Thu muc lam viec: ' + $a.WorkingDirectory) }; Write-Host ('  So trigger  : ' + $t.Triggers.Count); Write-Host ('  Chay khi dung pin: ' + (-not $t.Settings.DisallowStartIfOnBatteries)); Write-Host ('  Khong tat khi sang pin: ' + (-not $t.Settings.StopIfGoingOnBatteries)); Write-Host ('  Chay bu khi lo gio: ' + $t.Settings.StartWhenAvailable); Write-Host ('  Gioi han thoi gian: ' + $t.Settings.ExecutionTimeLimit); Write-Host ('  So lan tu bat lai: ' + $t.Settings.RestartCount) }"

echo.
echo ============================================
echo  BUOC TIEP THEO
echo ============================================
echo.
echo   1. Kiem tra lich: dong "Tham so" o tren PHAI ket thuc bang nguoi_truc.py"
echo   2. Nhan tin "con song khong?" cho bot Telegram de thu
echo   3. Xem nhat ky: logs\baocao.log
echo.
echo De TAT hoan toan: bam file go-nguoi-truc.bat
echo De quay lai cach cu (3 lich): bam file cai-dat-lich.bat
echo.
pause
exit /b 0
