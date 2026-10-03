@echo off
setlocal
chcp 65001 >nul
REM ============================================
REM TAT NGUOI TRUC
REM ============================================
REM Chi go lich NguoiTruc va dung nguoi_truc.py.
REM KHONG dung agent.py; agent van can file nguoi_truc.py de dung Telegram.
REM ============================================

set "WATCHER_PATH=%~dp0nguoi_truc.py"

echo.
echo ============================================
echo  TAT NGUOI TRUC
echo ============================================
echo.

REM Xoa va xac nhan lich truoc; neu khong xoa duoc thi KHONG dung tien trinh.
echo Dang go lich NguoiTruc...
powershell -NoProfile -Command "$scriptPath = [IO.Path]::GetFullPath($env:WATCHER_PATH); try { $task = Get-ScheduledTask -TaskName 'NguoiTruc' -ErrorAction SilentlyContinue; if ($task) { Unregister-ScheduledTask -TaskName 'NguoiTruc' -Confirm:$false -ErrorAction Stop }; if (Get-ScheduledTask -TaskName 'NguoiTruc' -ErrorAction SilentlyContinue) { throw 'Lich NguoiTruc van con sau khi go' }; Write-Host '  [OK] Da go lich NguoiTruc'; $ds = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -in @('python.exe','pythonw.exe') -and $_.CommandLine -like ('*' + $scriptPath + '*') }); if (-not $ds) { Write-Host '  [--] Khong co tien trinh nguoi_truc.py dang chay' }; foreach ($d in $ds) { Stop-Process -Id $d.ProcessId -Force -ErrorAction Stop; Write-Host ('  [DUNG] Da dung nguoi_truc.py PID ' + $d.ProcessId) }; Start-Sleep -Seconds 1; $con = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object { $_.Name -in @('python.exe','pythonw.exe') -and $_.CommandLine -like ('*' + $scriptPath + '*') }); if ($con.Count -gt 0) { throw ('Van con tien trinh nguoi_truc.py: ' + (($con | ForEach-Object { $_.ProcessId }) -join ', ')) }; Write-Host 'Da tat Nguoi truc.' } catch { Write-Host ('[LOI] ' + $_.Exception.Message); exit 1 }"
if errorlevel 1 goto loi

echo.
echo Nguoi truc da duoc go. Agent van tiep tuc chay rieng.
echo Kiem tra Task Manager: nguoi_truc.py khong con; agent.py van con.
echo.
pause
exit /b 0

:loi
echo.
echo KHONG GO DUOC HOAN TOAN. Neu bao loi quyen, chay lai bang Run as administrator.
echo Khong dong agent.py va khong xoa nguoi_truc.py.
echo.
pause
exit /b 1
