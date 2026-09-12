@echo off
REM ============================================
REM BAT TINH NANG "CHAY BU KHI LO GIO"
REM ============================================
REM Mac dinh: neu may tat hoac ngu dung luc 8h, bao cao 8h se BI BO QUA.
REM File nay bat 2 tinh nang:
REM   1. Chay bu khi may bat lai sau khi lo gio  (StartWhenAvailable)
REM   2. Danh thuc may de chay bao cao dung gio (WakeToRun)
REM
REM CAN CHAY BANG QUYEN ADMIN:
REM   Chuot phai vao file nay -> "Run as administrator"
REM
REM Chi can chay 1 lan duy nhat.
REM ============================================

echo.
echo ============================================
echo  BAT CHAY BU KHI LO GIO
echo ============================================
echo.

REM --- Kiem tra quyen Admin ---
net session >nul 2>&1
if errorlevel 1 (
    echo [LOI] Ban chua chay bang quyen Admin.
    echo.
    echo Cach lam:
    echo   1. Dong cua so nay lai
    echo   2. Chuot phai vao file nay
    echo   3. Chon "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo Da co quyen Admin. Dang bat tinh nang...
echo.

powershell -NoProfile -Command "$s = New-ScheduledTaskSettingsSet -StartWhenAvailable -WakeToRun -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 15); foreach ($n in @('BaoCaoMetaAds_08','BaoCaoMetaAds_12','BaoCaoMetaAds_17','BaoCaoMetaAds_22')) { try { Set-ScheduledTask -TaskName $n -Settings $s -ErrorAction Stop | Out-Null; Write-Host ('  [OK]  ' + $n) } catch { Write-Host ('  [LOI] ' + $n + ' - ' + $_.Exception.Message) } }"

echo.
echo ============================================
echo  HOAN THANH
echo ============================================
echo.
echo Tu gio, Windows se:
echo   - Tu danh thuc may de chay bao cao dung gio (neu may dang ngu)
echo   - Tu chay bu bao cao da lo ngay khi may duoc bat lai (neu may da tat)
echo.
pause
