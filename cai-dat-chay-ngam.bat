@echo off
chcp 65001 >nul
REM ============================================
REM  CAI LAI CA HAI - DE CHAY NGAN (khong hien cua so)
REM ============================================
REM  File nay lam MOT viec: cai lai lich cho ca hai tien trinh, lan nay
REM  chay bang pythonw.exe nen KHONG hien cua so console nao nua.
REM
REM  Sau khi bam xong:
REM    · Khong con hai cua so den chiem cho tren thanh tac vu
REM    · Ca hai van chay binh thuong, chi la khong hien cua so
REM    · Muon xem chung dang lam gi: mo file logs\baocao.log
REM
REM  Neu bi bao loi quyen: chuot phai vao file nay, chon
REM  "Run as administrator", roi bam lai.
REM ============================================

setlocal

echo.
echo ============================================
echo  CAI LAI CA HAI TIEN TRINH - CHE DO CHAY NGAN
echo ============================================
echo.

echo --- 0/3: dung hai tien trinh cu (neu dang chay) ---
REM Vi sao phai dung TRUOC: dang ky lai lich KHONG tu dung tien trinh dang chay.
REM Neu bo qua buoc nay, co the co HAI tien trinh cung luc. Hai nguoi truc cung
REM doc Telegram thi tin cua nhau bi NUOT MAT, im lang, khong bao loi.
powershell -NoProfile -Command "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' -and ($_.CommandLine -like '*agent.py*' -or $_.CommandLine -like '*nguoi_truc.py*') } | ForEach-Object { try { Stop-Process -Id $_.ProcessId -Force -ErrorAction Stop; Write-Host ('   [DUNG] PID ' + $_.ProcessId) } catch { Write-Host ('   [--]  Khong dung duoc PID ' + $_.ProcessId) } }"
powershell -NoProfile -Command "Start-Sleep -Seconds 2; Write-Host '   da dung xong.'"

echo --- 1/3: nguoi truc ---
call "%~dp0cai-dat-nguoi-truc.bat" < nul

echo.
echo --- 2/3: agent ---
call "%~dp0cai-dat-agent.bat" < nul

echo.
echo ============================================
echo  XONG.
echo.
echo  Kiem tra: mo file logs\baocao.log
echo    - Tim dong "NGUOI TRUC: bat dau"
echo    - Tim dong "AGENT: khoi dong"
echo  Neu co ca hai la chay dung.
echo.
echo  Khong con cua so nao hien ra nua.
echo ============================================
echo.

pause
