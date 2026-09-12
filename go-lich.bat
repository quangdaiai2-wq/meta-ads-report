@echo off
REM ============================================
REM XOA LICH CHAY TU DONG
REM ============================================
REM Chay file nay neu muon TAT bao cao tu dong.
REM ============================================

echo.
echo ============================================
echo  XOA LICH BAO CAO META ADS
echo ============================================
echo.

REM Xoa ca ten cu (8, 12, 17, 22) va ten moi (08, 12, 17, 22)
for %%H in (8 08 12 17 22) do (
    schtasks /Delete /TN "BaoCaoMetaAds_%%H" /F >nul 2>&1
    if errorlevel 1 (
        echo   [--]  Moc %%H:00 - khong ton tai
    ) else (
        echo   [XOA] Moc %%H:00 - da xoa
    )
)

echo.
echo Da tat bao cao tu dong.
echo.
pause
