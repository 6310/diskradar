@echo off
setlocal
cd /d "%~dp0"

echo ============================================================================
echo   GEIO DISKRADAR - DESINSTALADOR DO SISTEMA
echo ============================================================================
echo.

set "PY_BIN="
where python.exe >nul 2>&1
if %errorlevel% equ 0 set "PY_BIN=python"

if not defined PY_BIN (
    where py.exe >nul 2>&1
    if %errorlevel% equ 0 set "PY_BIN=py -3"
)

if defined PY_BIN (
    "%PY_BIN%" -m core.installer --uninstall
)

if exist "%USERPROFILE%\Desktop\Geio DiskRadar.lnk" del /f /q "%USERPROFILE%\Desktop\Geio DiskRadar.lnk" >nul 2>&1
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Geio DiskRadar.lnk" del /f /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Geio DiskRadar.lnk" >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{8B49E7C2-1C2A-4D4F-9E62-F9F71B39D4E2}" /f >nul 2>&1

echo.
echo Desinstalacao concluida com sucesso!
pause
exit /b 0
