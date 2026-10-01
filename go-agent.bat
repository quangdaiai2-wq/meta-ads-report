@echo off
chcp 65001 >nul
REM ============================================
REM  GO AGENT NAC 2
REM ============================================
REM  File nay lam hai viec:
REM    1. Xoa lich "AgentNac2"
REM    2. Dung tien trinh agent dang chay (neu co)
REM
REM  Sau khi bam file nay, agent NGUNG HOAN TOAN: khong de xuat, khong
REM  nghe nut bam. Cac tin xin phep da gui truoc do van con nut, nhung
REM  bam se khong co tac dung gi cho toi khi bat lai.
REM
REM  Muon bat lai: bam cai-dat-agent.bat
REM ============================================

setlocal

echo.
echo ============================================
echo  GO AGENT NAC 2
echo ============================================
echo.

schtasks /Delete /TN "AgentNac2" /F >nul 2>&1
if errorlevel 1 (
    echo   [--]  Lich AgentNac2 khong ton tai
) else (
    echo   [XOA] Da xoa lich AgentNac2
)

echo   Dang dung tien trinh agent...
powershell -NoProfile -Command "$ds = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -like '*python*' -and $_.CommandLine -like '*agent.py*' }; if (-not $ds) { Write-Host '  [--]  Khong co tien trinh agent nao dang chay' } else { foreach ($d in $ds) { try { Stop-Process -Id $d.ProcessId -Force -ErrorAction Stop; Write-Host ('  [DUNG] Da dung agent (PID ' + $d.ProcessId + ')') } catch { Write-Host ('  [LOI]  Khong dung duoc PID ' + $d.ProcessId + ': ' + $_.Exception.Message) } } }"

echo.
echo ============================================
echo  XONG. Agent da ngung.
echo  Muon bat lai: bam cai-dat-agent.bat
echo ============================================
echo.

pause
