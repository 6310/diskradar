@echo off
setlocal
cd /d "%~dp0"

echo ============================================================================
echo   GEIO DISKRADAR - DESINSTALADOR DO SISTEMA
echo ============================================================================
echo.

set "PY_EXE="
set "PY_ARGS="

where python.exe >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_EXE=python"
    goto :PYTHON_OK
)

where py.exe >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_EXE=py"
    set "PY_ARGS=-3"
    goto :PYTHON_OK
)

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"

:PYTHON_OK
if defined PY_EXE (
    "%PY_EXE%" %PY_ARGS% -m core.installer --uninstall
)

if exist "%USERPROFILE%\Desktop\Geio DiskRadar.lnk" del /f /q "%USERPROFILE%\Desktop\Geio DiskRadar.lnk" >nul 2>&1
if exist "%USERPROFILE%\Área de Trabalho\Geio DiskRadar.lnk" del /f /q "%USERPROFILE%\Área de Trabalho\Geio DiskRadar.lnk" >nul 2>&1
if exist "%USERPROFILE%\OneDrive\Desktop\Geio DiskRadar.lnk" del /f /q "%USERPROFILE%\OneDrive\Desktop\Geio DiskRadar.lnk" >nul 2>&1
if exist "%USERPROFILE%\OneDrive\Área de Trabalho\Geio DiskRadar.lnk" del /f /q "%USERPROFILE%\OneDrive\Área de Trabalho\Geio DiskRadar.lnk" >nul 2>&1
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Geio DiskRadar.lnk" del /f /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Geio DiskRadar.lnk" >nul 2>&1

reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{8B49E7C2-1C2A-4D4F-9E62-F9F71B39D4E2}" /f >nul 2>&1
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Uninstall\{8B49E7C2-1C2A-4D4F-9E62-F9F71B39D4E2}_is1" /f >nul 2>&1

echo.
echo Desinstalacao concluida com sucesso!
echo Suas evidencias extraidas na pasta Evidencias_DiskRadar foram preservadas.

rem Se executado de dentro da pasta de instalacao oficial, agenda remocao residual
if /i "%~dp0"=="%LOCALAPPDATA%\Programs\GeioDiskRadar\" (
    start "" /min cmd.exe /c "timeout /t 1 /nobreak >nul & rd /s /q \"%~dp0\""
)

pause
exit /b 0
