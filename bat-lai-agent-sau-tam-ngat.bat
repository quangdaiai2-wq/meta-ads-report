@echo off
chcp 65001 >nul
REM ============================================
REM  BAT LAI AGENT SAU TAM NGAT
REM ============================================
REM  Tu 03/10/2026, cong tac tam ngat la SU TON TAI cua mot FILE:
REM      logs\TAM-NGAT-AGENT.txt
REM  Khong con tien trinh giu khoa nao nua => khong co gi chet khi tat may.
REM
REM  File nay lam BON viec:
REM    1. Xoa file cong tac tam ngat   -> agent duoc phep chay lai
REM    2. Xoa lich AgentTamNgat (cu)   -> don sach lich cua cach chan cu
REM    3. Xoa file khoa con lai        -> de agent khoi dong sach
REM    4. Kiem tra agent da chay lai chua
REM
REM  Khong dung `schtasks` de XOA lich AgentNac2 -- chi xoa lich cu
REM  AgentTamNgat (neu con). Lich AgentNac2 phai GIU NGUYEN.
REM ============================================

setlocal
set GOC=%~dp0

echo.
echo ============================================
echo  BAT LAI AGENT SAU TAM NGAT
echo ============================================
echo.

echo [1/4] Xoa file cong tac tam ngat...
if exist "%GOC%logs\TAM-NGAT-AGENT.txt" (
    del /f /q "%GOC%logs\TAM-NGAT-AGENT.txt"
    echo       [XOA] Da xoa logs\TAM-NGAT-AGENT.txt
    echo       Agent se duoc phep chay lai o lan quet ke tiep.
) else (
    echo       [--]  Khong co file tam ngat ^(da bat lai roi^)
)

echo [2/4] Xoa lich AgentTamNgat cu...
schtasks /Delete /TN "AgentTamNgat" /F >nul 2>&1
if errorlevel 1 (
    echo       [--]  Lich AgentTamNgat khong ton tai ^(binh thuong^)
) else (
    echo       [XOA] Da xoa lich AgentTamNgat
)

echo [3/4] Don tien trinh giu khoa cu va file khoa...
powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'python*' -and $_.CommandLine -like '*giu_khoa_tam_ngat*' }; if ($p) { foreach ($d in $p) { try { Stop-Process -Id $d.ProcessId -Force -ErrorAction Stop; Write-Host ('      [DUNG] Da dung tien trinh giu khoa cu (PID ' + $d.ProcessId + ')') } catch { Write-Host ('      [LOI]  Khong dung duoc PID ' + $d.ProcessId) } } } else { Write-Host '      [--]  Khong co tien trinh giu khoa cu nao' }"
if exist "%GOC%logs\agent-dang-chay.lock" (
    del /f /q "%GOC%logs\agent-dang-chay.lock"
    echo       [XOA] Da xoa logs\agent-dang-chay.lock
)

echo [4/4] Kiem tra agent...
echo       Cho toi da 6 phut de lich AgentNac2 tu khoi dong lai.
echo       (Neu muon nhanh: bam khoi-dong-lai-agent.bat)
echo.
powershell -NoProfile -Command "$deadline = (Get-Date).AddMinutes(6); $tim_thay = $false; while ((Get-Date) -lt $deadline) { $a = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'python*' -and $_.CommandLine -like '*agent.py*' }; if ($a) { foreach ($d in $a) { Write-Host ('      [OK]  Agent dang chay (PID ' + $d.ProcessId + ')'); $tim_thay = $true }; break }; Start-Sleep -Seconds 15 }; if (-not $tim_thay) { Write-Host '      [--]  Chua thay agent chay sau 6 phut.'; Write-Host '      Cach xu ly: bam khoi-dong-lai-agent.bat' }"

echo.
echo ============================================
echo  XONG.
echo.
echo  Agent da duoc bat lai (hoac dang cho lich tu bat).
echo  Kiem tra: mo file logs\baocao.log, tim dong moi nhat
echo  co chu "AGENT:".
echo ============================================
echo.
pause
