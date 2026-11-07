@echo off
setlocal
cd /d "%~dp0"

REM Se nao estiver em modo interno, reinicia gravando tudo em compilacao.log
if "%~1"=="--internal-run" goto :INTERNAL_RUN

echo ============================================================================
echo   GEIO DISKRADAR v2.2.0 - INICIANDO COMPILADOR PyInstaller COM LOG
echo ============================================================================
echo.
echo Gravando log em tempo real no arquivo: compilacao.log
echo Por favor, aguarde alguns instantes...
echo.
cmd.exe /c ""%~f0" --internal-run" > "%~dp0compilacao.log" 2>&1

if not exist "%~dp0compilacao.log" goto :SEM_LOG
type "%~dp0compilacao.log"
goto :FIM_LOG

:SEM_LOG
echo [AVISO] Arquivo compilacao.log nao encontrado.

:FIM_LOG
echo.
echo ============================================================================
echo Registro salvo em: %~dp0compilacao.log
echo ============================================================================
echo.
echo Pressione qualquer tecla para fechar esta janela...
pause >nul
exit /b %errorlevel%


:INTERNAL_RUN
set "VERSION=2.2.0"
set "EXE_NAME=DiskRadar-v%VERSION%.exe"

echo ============================================================================
echo   GEIO DISKRADAR v%VERSION% - LOG DE COMPILACAO
echo ============================================================================
echo Data e Hora: %DATE% %TIME%
echo Diretorio de Trabalho: %CD%
echo Executavel Alvo: %EXE_NAME%
echo.

REM 1. Valida descompactacao
if not exist "%~dp0main.py" (
    echo [ERRO CRITICO] O arquivo main.py nao foi encontrado neste diretorio!
    echo Voce precisa extrair o arquivo .ZIP antes de executar.
    echo Solucao: Clique com o botao direito no arquivo .ZIP e escolha "Extrair Tudo".
    exit /b 1
)

REM 2. Busca o Python 3
echo [PASSO 1/4] Procurando interpretador Python 3 no sistema...
set "PY_BIN="

where python.exe >nul 2>&1
if %errorlevel% equ 0 (
    set "PY_BIN=python"
    echo   Encontrado no PATH: python
)

if not defined PY_BIN (
    where py.exe >nul 2>&1
    if %errorlevel% equ 0 (
        set "PY_BIN=py -3"
        echo   Encontrado via py launcher: py -3
    )
)

if not defined PY_BIN (
    if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY_BIN=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    if defined PY_BIN echo   Encontrado em LocalAppData: %PY_BIN%
)

if not defined PY_BIN (
    if exist "C:\Program Files\Python314\python.exe" set "PY_BIN=C:\Program Files\Python314\python.exe"
    if exist "C:\Program Files\Python313\python.exe" set "PY_BIN=C:\Program Files\Python313\python.exe"
    if exist "C:\Program Files\Python312\python.exe" set "PY_BIN=C:\Program Files\Python312\python.exe"
    if exist "C:\Program Files\Python311\python.exe" set "PY_BIN=C:\Program Files\Python311\python.exe"
    if defined PY_BIN echo   Encontrado em Program Files: %PY_BIN%
)

if not defined PY_BIN (
    echo [ERRO FATAL] Python 3 nao encontrado!
    echo Verifique se o Python esta instalado ou reinstale marcando "Add python.exe to PATH".
    exit /b 1
)

echo.
echo [PASSO 2/4] Informacoes da versao do Python:
%PY_BIN% --version
echo Localizacao: %PY_BIN%
echo.

REM 3. Dependencias
echo [PASSO 3/4] Instalando/atualizando dependencias (pip, customtkinter, pyinstaller)...
%PY_BIN% -m pip install --upgrade pip
%PY_BIN% -m pip install -r requirements.txt pyinstaller
if %errorlevel% neq 0 (
    echo.
    echo [ERRO] O comando pip falhou ao instalar as dependencias.
    exit /b 1
)

REM 4. Compilacao PyInstaller
echo.
echo [PASSO 4/4] Gerando executavel %EXE_NAME% via PyInstaller...
echo Isso pode levar de 30 a 60 segundos...
%PY_BIN% -m PyInstaller --clean --noconfirm --onefile --windowed --name "DiskRadar-v%VERSION%" --collect-all customtkinter main.py
if errorlevel 1 goto :BUILD_FAIL

echo.
echo ============================================================================
echo [SUCESSO TOTAL] COMPILACAO CONCLUIDA!
echo ============================================================================
copy /y "dist\%EXE_NAME%" "%EXE_NAME%" >nul 2>&1
copy /y "dist\%EXE_NAME%" "DiskRadar.exe" >nul 2>&1
echo Arquivos gerados com sucesso:
echo   - dist\%EXE_NAME%
echo   - %EXE_NAME%
echo   - DiskRadar.exe
echo ============================================================================
exit /b 0

:BUILD_FAIL
echo.
echo ============================================================================
echo [ERRO] O PyInstaller falhou na compilacao (codigo: %errorlevel%).
echo ============================================================================
exit /b 1
