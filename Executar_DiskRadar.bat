@echo off
setlocal
cd /d "%~dp0"

if "%~1"=="--internal-run" goto :INTERNAL_RUN

echo ============================================================================
echo   GEIO DISKRADAR v2.3.0 - INICIANDO EXECUCAO DIRETA
echo ============================================================================
echo.
cmd.exe /c ""%~f0" --internal-run" > "%~dp0execucao.log" 2>&1

if not exist "%~dp0execucao.log" goto :SEM_LOG
type "%~dp0execucao.log"
goto :FIM_LOG

:SEM_LOG
echo [AVISO] Arquivo execucao.log nao encontrado.

:FIM_LOG
echo.
echo Pressione qualquer tecla para sair...
pause >nul
exit /b %errorlevel%


:INTERNAL_RUN
echo Data e Hora: %DATE% %TIME%
echo Diretorio de Trabalho: %CD%
echo.

if not exist "%~dp0main.py" (
    echo [ERRO CRITICO] O arquivo main.py nao foi encontrado neste diretorio!
    echo Voce precisa extrair o arquivo .ZIP antes de executar.
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
    if exist "C:\Program Files\Python314\python.exe" set "PY_BIN=C:\Program Files\Python314\python.exe"
    if exist "C:\Program Files\Python313\python.exe" set "PY_BIN=C:\Program Files\Python313\python.exe"
    if exist "C:\Program Files\Python312\python.exe" set "PY_BIN=C:\Program Files\Python312\python.exe"
    if exist "C:\Program Files\Python311\python.exe" set "PY_BIN=C:\Program Files\Python311\python.exe"
)

if not defined PY_BIN (
    echo [ERRO FATAL] Python 3 nao encontrado!
    exit /b 1
)

echo Python detectado:
%PY_BIN% --version
echo.

echo Instalando/verificando dependencias...
%PY_BIN% -m pip install -r requirements.txt --quiet

echo Abrindo interface grafica do Geio DiskRadar v2.2.0...
start "" "%PY_BIN%" main.py
echo [OK] Processo disparado com sucesso.
exit /b 0
