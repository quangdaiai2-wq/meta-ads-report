@echo off
chcp 65001 >nul
REM ============================================
REM  CAI DAT LICH TU CHAY CHO AGENT NAC 2
REM ============================================
REM  File nay lam ba viec:
REM    1. Xoa lich "AgentNac2" cu (neu co)
REM    2. Tao lich "AgentNac2": chay khi dang nhap + tu bat lai neu tat
REM    3. Khoi dong agent ngay
REM
REM  VI SAO CAN FILE NAY:
REM  Agent la tien trinh chay nen. Neu may khoi dong lai ma agent khong tu
REM  chay, no chet IM LANG - Dai se tuong "khong co de xuat nao la tin tot"
REM  trong khi that ra agent khong he chay. Do la kieu hong nguy hiem nhat.
REM
REM  Muon go: bam go-agent.bat
REM ============================================

setlocal

set TASK_NAME=AgentNac2

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
set SCRIPT_PATH=%SCRIPT_DIR%agent.py

if not defined PYTHON_EXE (
    echo LOI: Khong tim thay Python tren may nay!
    echo Mo file nay bang Notepad, sua dong "set PYTHON_EXE=" thanh duong dan Python.
    pause
    exit /b 1
)

if not exist "%SCRIPT_PATH%" (
    echo LOI: Khong tim thay agent.py trong: %SCRIPT_DIR%
    echo File nay phai nam ngay trong thu muc du an.
    pause
    exit /b 1
)

echo.
echo ============================================
echo  CAI DAT LICH TU CHAY CHO AGENT
echo ============================================
echo  Python : %PYTHON_EXE%
echo  Chuong trinh: %SCRIPT_PATH%
echo.

echo [1/4] Xoa lich cu neu co...
schtasks /Delete /TN "%TASK_NAME%" /F >nul 2>&1
echo       xong.

echo [2/4] Tao lich moi...
REM --- Chay NEN: dung pythonw.exe de KHONG hien cua so console ---
set PYTHONW_EXE=%PYTHON_EXE:python.exe=pythonw.exe%
if not exist "%PYTHONW_EXE%" set PYTHONW_EXE=%PYTHON_EXE%
powershell -NoProfile -Command "$py=$env:PYTHONW_EXE; $sp=$env:SCRIPT_PATH; $wd=$env:SCRIPT_DIR; $a = New-ScheduledTaskAction -Execute $py -Argument ([char]34 + $sp + [char]34) -WorkingDirectory $wd; $t1 = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME; $t2 = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5); $s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -RestartInterval (New-TimeSpan -Minutes 5) -RestartCount 3 -MultipleInstances IgnoreNew; try { Register-ScheduledTask -TaskName 'AgentNac2' -Action $a -Trigger $t1, $t2 -Settings $s -Force -ErrorAction Stop | Out-Null; Write-Host '      [OK]  Da tao lich AgentNac2' } catch { Write-Host ('      [LOI] ' + $_.Exception.Message) }"

echo [3/4] Khoi dong agent ngay...
powershell -NoProfile -Command "try { Start-ScheduledTask -TaskName 'AgentNac2' -ErrorAction Stop; Start-Sleep -Seconds 8; Write-Host '      [OK]  Da khoi dong agent' } catch { Write-Host ('      [LOI] Khong khoi dong duoc: ' + $_.Exception.Message); Write-Host '      Cach xu ly: dang xuat Windows roi dang nhap lai.' }"

echo [4/4] Kiem tra lai...
powershell -NoProfile -Command "$t = Get-ScheduledTask -TaskName 'AgentNac2' -ErrorAction SilentlyContinue; if (-not $t) { Write-Host '      [LOI] KHONG TIM THAY lich AgentNac2.'; Write-Host '      Cach xu ly: chuot phai vao file nay, chon Run as administrator, roi bam lai.' } else { Write-Host ('      Ten lich    : ' + $t.TaskName); Write-Host ('      Trang thai  : ' + $t.State); Write-Host ('      Chay khi dung pin: ' + (-not $t.Settings.DisallowStartIfOnBatteries)); Write-Host ('      Khong tat khi sang pin: ' + (-not $t.Settings.StopIfGoingOnBatteries)); Write-Host ('      Tu bat lai khi tat: ' + $t.Settings.RestartCount + ' lan, cach ' + $t.Settings.RestartInterval) }; $p = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '*python*' -and $_.CommandLine -like '*agent.py*' }; if (-not $p) { Write-Host '      Tien trinh   : CHUA CHAY - xem huong dan o tren' } else { foreach ($d in $p) { Write-Host ('      Tien trinh   : dang chay (PID ' + $d.ProcessId + ')') } }"

echo.
echo ============================================
echo  XONG.
echo.
echo  Agent se tu chay moi khi dang nhap Windows.
echo  Agent TU CHOI khoi dong neu da co mot agent khac dang chay,
echo  nen bam file nay nhieu lan cung khong sao.
echo.
echo  De xem agent dang lam gi: mo file logs\baocao.log
echo  Muon go han: bam go-agent.bat
echo ============================================
echo.

pause
