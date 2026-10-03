@echo off
chcp 65001 >nul
REM ============================================
REM  TAM NGAT AGENT -- chan agent chay tu 03/10 den het 06/10/2026
REM ============================================
REM  File nay lam HAI viec:
REM    1. Dung agent dang chay (neu co)
REM    2. Chay mot tien trinh nho GIU KHOA de lich AgentNac2 co chay
REM       cung khong the khoi dong agent
REM
REM  KHONG xoa lich AgentNac2 -- chi giu khoa. Nho vay khi muon bat lai
REM  chi can xoa logs\TAM-NGAT-AGENT.txt la xong, khong can quyen Admin.
REM
REM  BAT LAI: bam file bat-lai-agent-sau-tam-ngat.bat
REM ============================================

setlocal
set GOC=%~dp0
set PYTHONW=C:\Users\%USERNAME%\.workbuddy-ai\binaries\python\versions\3.13.12\pythonw.exe

echo.
echo ============================================
echo  TAM NGAT AGENT
echo ============================================
echo.

if not exist "%PYTHONW%" (
    echo LOI: Khong tim thay pythonw.exe tai:
    echo    %PYTHONW%
    echo Mo file nay bang Notepad, sua dong "set PYTHONW=" thanh duong dan dung.
    pause
    exit /b 1
)

if not exist "%GOC%logs\TAM-NGAT-AGENT.txt" (
    echo LOI: Thieu file "%GOC%logs\TAM-NGAT-AGENT.txt"
    echo File do ghi LY DO va HAN tam ngat. Tao no truoc roi bam lai.
    pause
    exit /b 1
)

echo [1/3] Dung tien trinh agent dang chay...
powershell -NoProfile -Command "$ds = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '*python*' -and $_.CommandLine -like '*agent.py*' }; if (-not $ds) { Write-Host '      [--]  Khong co agent nao dang chay' } else { foreach ($d in $ds) { try { Stop-Process -Id $d.ProcessId -Force -ErrorAction Stop; Write-Host ('      [DUNG] Da dung agent (PID ' + $d.ProcessId + ')') } catch { Write-Host ('      [LOI]  Khong dung duoc PID ' + $d.ProcessId) } } }"
if errorlevel 1 echo       [CANH BAO] Lenh dung agent bao loi -- kiem tra lai.

echo [2/3] Chay tien trinh GIU KHOA de chan agent khoi dong lai...
powershell -NoProfile -Command "$py='%PYTHONW%'; $wd='%GOC%'; $a = New-ScheduledTaskAction -Execute $py -Argument 'giu_khoa_tam_ngat.py' -WorkingDirectory $wd; $t = New-ScheduledTaskTrigger -AtLogOn -User $env:USERNAME; $s = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Seconds 0) -MultipleInstances IgnoreNew; try { Register-ScheduledTask -TaskName 'AgentTamNgat' -Action $a -Trigger $t -Settings $s -Force -ErrorAction Stop | Out-Null; Write-Host '      [OK]  Da tao lich AgentTamNgat' } catch { Write-Host ('      [LOI] ' + $_.Exception.Message) }"
powershell -NoProfile -Command "try { Start-ScheduledTask -TaskName 'AgentTamNgat' -ErrorAction Stop; Start-Sleep -Seconds 6; Write-Host '      [OK]  Da chay tien trinh giu khoa' } catch { Write-Host ('      [LOI] ' + $_.Exception.Message) }"

echo [3/3] Kiem tra lai...
powershell -NoProfile -Command "Start-Sleep -Seconds 4; $k = Get-Content -LiteralPath 'logs\agent-dang-chay.lock' -ErrorAction SilentlyContinue; if ($k) { Write-Host ('      Khoa     : ' + $k[0] + ' -- PID ' + $k[1]) } else { Write-Host '      Khoa     : CHUA CO -- tien trinh giu khoa chua chay' }; $p = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*giu_khoa_tam_ngat*' }; if (-not $p) { Write-Host '      Giu khoa : CHUA CHAY' } else { foreach ($d in $p) { Write-Host ('      Giu khoa : dang chay (PID ' + $d.ProcessId + ')') } }; $a = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like '*agent.py*' }; if (-not $a) { Write-Host '      Agent    : DA DUNG (dung nhu mong muon)' } else { foreach ($d in $a) { Write-Host ('      Agent    : VAN CHAY (PID ' + $d.ProcessId + ') -- can kiem tra!') } }"

echo.
echo ============================================
echo  XONG.
echo.
echo  Agent da ngung. Mot tien trinh nho dang giu khoa
echo  nen lich AgentNac2 (5 phut/lan) co chay cung
echo  KHONG khoi dong duoc agent.
echo.
echo  BAT LAI: bam bat-lai-agent-sau-tam-ngat.bat
echo  (hoac xoa file logs\TAM-NGAT-AGENT.txt)
echo ============================================
echo.
pause
