@echo off
chcp 65001 >nul
REM ============================================
REM  TAM NGAT AGENT
REM ============================================
REM  Tu 03/10/2026, cong tac tam ngat la SU TON TAI cua mot FILE:
REM      logs\TAM-NGAT-AGENT.txt
REM
REM  KHONG con tien trinh giu khoa nao. Ly do (lo hong cua cach cu):
REM  tien trinh giu khoa chet khi TAT MAY / DANG XUAT. May bat lai thi
REM  lich AgentNac2 chay, khong con ai giu khoa => agent TU KHOI DONG LAI.
REM        Dai phat hien: "neu toi tat may nay va t2 quay tro lai cong ty
REM                        no tu bat lai thi con noi chuyen gi nua?"
REM
REM  Cai moi: agent doc file cong tac va TU CHOI ngay khi file con do.
REM  Khong co gi phai chay => khong co gi chet theo.
REM
REM  File nay lam HAI viec:
REM    1. Dung agent dang chay (neu co)
REM    2. Bao dam file cong tac ton tai
REM
REM  KHONG xoa lich AgentNac2. Muon bat lai chi can xoa file cong tac
REM  (hoac bam bat-lai-agent-sau-tam-ngat.bat), khong can quyen Admin.
REM ============================================

setlocal
set GOC=%~dp0

echo.
echo ============================================
echo  TAM NGAT AGENT
echo ============================================
echo.

if not exist "%GOC%logs\TAM-NGAT-AGENT.txt" (
    echo LOI: Thieu file "%GOC%logs\TAM-NGAT-AGENT.txt"
    echo File do CHINH LA cong tac tam ngat. Tao no truoc roi bam lai.
    pause
    exit /b 1
)

echo [1/3] Dung tien trinh agent dang chay...
powershell -NoProfile -Command "$ds = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'python*' -and $_.CommandLine -like '*agent.py*' }; if (-not $ds) { Write-Host '      [--]  Khong co agent nao dang chay' } else { foreach ($d in $ds) { try { Stop-Process -Id $d.ProcessId -Force -ErrorAction Stop; Write-Host ('      [DUNG] Da dung agent (PID ' + $d.ProcessId + ')') } catch { Write-Host ('      [LOI]  Khong dung duoc PID ' + $d.ProcessId) } } }"

echo [2/3] Don tien trinh giu khoa CU (neu con tu cach chan truoc)...
powershell -NoProfile -Command "$p = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'python*' -and $_.CommandLine -like '*giu_khoa_tam_ngat*' }; if (-not $p) { Write-Host '      [--]  Khong con tien trinh giu khoa cu' } else { foreach ($d in $p) { try { Stop-Process -Id $d.ProcessId -Force -ErrorAction Stop; Write-Host ('      [DUNG] Da dung tien trinh giu khoa cu (PID ' + $d.ProcessId + ')') } catch { Write-Host ('      [LOI]  Khong dung duoc PID ' + $d.ProcessId) } } }"
schtasks /Delete /TN "AgentTamNgat" /F >nul 2>&1
if not errorlevel 1 echo       [XOA] Da xoa lich AgentTamNgat cu
if exist "%GOC%logs\agent-dang-chay.lock" (
    del /f /q "%GOC%logs\agent-dang-chay.lock"
    echo       [XOA] Da xoa logs\agent-dang-chay.lock
)

echo [3/3] Kiem tra lai...
powershell -NoProfile -Command "Start-Sleep -Seconds 3; if (Test-Path '%GOC%logs\TAM-NGAT-AGENT.txt') { Write-Host '      Cong tac : DANG BAT (file con do -- dung nhu mong muon)' } else { Write-Host '      Cong tac : KHONG CO -- tam ngat KHONG hoat dong!' }; $a = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'python*' -and $_.CommandLine -like '*agent.py*' }; if (-not $a) { Write-Host '      Agent    : DA DUNG (dung nhu mong muon)' } else { foreach ($d in $a) { Write-Host ('      Agent    : VAN CHAY (PID ' + $d.ProcessId + ') -- can kiem tra!') } }"

echo.
echo ============================================
echo  XONG.
echo.
echo  Agent da ngung va KHONG THE tu chay lai, ke ca khi:
echo    - Tat may roi bat lai
echo    - Dang xuat roi dang nhap lai
echo    - Lich AgentNac2 chay (5 phut/lan)
echo.
echo  BAT LAI: bam bat-lai-agent-sau-tam-ngat.bat
echo  (hoac xoa file logs\TAM-NGAT-AGENT.txt)
echo ============================================
echo.
pause
