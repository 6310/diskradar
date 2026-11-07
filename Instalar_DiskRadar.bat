@echo off
setlocal
cd /d "%~dp0"

echo ============================================================================
echo   GEIO DISKRADAR - INSTALADOR E ATUALIZADOR INTELIGENTE PARA WINDOWS
echo   Garante instalacao unica sem duplicar versoes no sistema
echo ============================================================================
echo.

if not exist "%~dp0main.py" (
    echo [ERRO CRITICO] Arquivo main.py nao encontrado!
    echo Extraia todo o conteudo do arquivo .ZIP antes de executar o instalador.
    pause
    exit /b 1
)

set "PY_BIN="
where python.exe >nul 2>&1
if %errorlevel% equ 0 set "PY_BIN=python"

if not defined PY_BIN (
    where py.exe >nul 2>&1
    if %errorlevel% equ 0 set "PY_BIN=py -3"
)

if not defined PY_BIN (
    if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
)

if not defined PY_BIN (
    echo [ERRO FATAL] Python 3 nao encontrado neste computador!
    echo Instale o Python 3 marcando a opcao "Add python.exe to PATH".
    pause
    exit /b 1
)

echo [1/2] Verificando versoes existentes e atualizando instalacao central...
echo.
"%PY_BIN%" -m core.installer --install
if errorlevel 1 goto :ERRO_INSTALACAO

echo.
echo [2/2] Instalacao/Atualizacao concluida com sucesso!
echo Iniciando o Geio DiskRadar a partir da instalacao central...
start "" "%LOCALAPPDATA%\Programs\GeioDiskRadar\Executar_DiskRadar.bat"
echo.
timeout /t 4 >nul
exit /b 0

:ERRO_INSTALACAO
echo.
echo [AVISO] A instalacao foi interrompida ou bloqueada pela protecao de versao.
pause
exit /b 1
