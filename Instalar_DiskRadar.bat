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

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    goto :PYTHON_OK
)
if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :PYTHON_OK
)
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :PYTHON_OK
)
if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PY_EXE=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :PYTHON_OK
)

if exist "C:\Program Files\Python314\python.exe" (
    set "PY_EXE=C:\Program Files\Python314\python.exe"
    goto :PYTHON_OK
)
if exist "C:\Program Files\Python313\python.exe" (
    set "PY_EXE=C:\Program Files\Python313\python.exe"
    goto :PYTHON_OK
)
if exist "C:\Program Files\Python312\python.exe" (
    set "PY_EXE=C:\Program Files\Python312\python.exe"
    goto :PYTHON_OK
)
if exist "C:\Program Files\Python311\python.exe" (
    set "PY_EXE=C:\Program Files\Python311\python.exe"
    goto :PYTHON_OK
)

:PYTHON_OK
if not defined PY_EXE (
    echo [ERRO FATAL] Python 3 nao encontrado neste computador!
    echo Instale o Python 3 marcando a opcao "Add python.exe to PATH".
    pause
    exit /b 1
)

echo [1/2] Verificando versoes existentes e atualizando instalacao central...
echo.
"%PY_EXE%" %PY_ARGS% -m core.installer --install
if errorlevel 1 goto :ERRO_INSTALACAO

echo.
echo [2/2] Instalacao/Atualizacao concluida com sucesso!
echo Iniciando o Geio DiskRadar a partir da instalacao central...
start "" /D "%LOCALAPPDATA%\Programs\GeioDiskRadar" "%LOCALAPPDATA%\Programs\GeioDiskRadar\Executar_DiskRadar.bat"
echo.
timeout /t 4 >nul
exit /b 0

:ERRO_INSTALACAO
echo.
echo [AVISO] A instalacao foi interrompida ou bloqueada pela protecao de versao.
pause
exit /b 1
