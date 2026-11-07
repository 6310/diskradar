@echo off
setlocal
cd /d "%~dp0"

REM Se nao estiver em modo interno, reinicia gravando tudo em compilacao.log
if "%~1"=="--internal-run" goto :INTERNAL_RUN

echo ============================================================================
echo   GEIO DISKRADAR v2.3.0 - COMPILADOR AUTOMATIZADO (.EXE & INSTALADOR)
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
set "VERSION=2.3.0"
set "EXE_NAME=DiskRadar.exe"

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
    exit /b 1
)

REM 2. Busca o Python 3
echo [PASSO 1/5] Procurando interpretador Python 3 no sistema...
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

if exist "C:\Program Files\Python314\python.exe" set "PY_EXE=C:\Program Files\Python314\python.exe"
if exist "C:\Program Files\Python313\python.exe" set "PY_EXE=C:\Program Files\Python313\python.exe"
if exist "C:\Program Files\Python312\python.exe" set "PY_EXE=C:\Program Files\Python312\python.exe"
if exist "C:\Program Files\Python311\python.exe" set "PY_EXE=C:\Program Files\Python311\python.exe"

:PYTHON_OK
if not defined PY_EXE (
    echo [ERRO FATAL] Python 3 nao encontrado!
    echo Instale o Python marcando a opcao "Add python.exe to PATH".
    exit /b 1
)

echo Python detectado:
"%PY_EXE%" %PY_ARGS% --version
echo.

REM 3. Dependencias
echo [PASSO 2/5] Instalando/atualizando dependencias (pip, customtkinter, pyinstaller)...
"%PY_EXE%" %PY_ARGS% -m pip install --upgrade pip
"%PY_EXE%" %PY_ARGS% -m pip install -r requirements.txt pyinstaller
if errorlevel 1 (
    echo.
    echo [ERRO] O comando pip falhou ao instalar as dependencias.
    exit /b 1
)

REM 4. Geracao do Icone .ico oficial
echo.
echo [PASSO 3/5] Validando icone oficial ui\assets\diskradar.ico...
"%PY_EXE%" %PY_ARGS% -c "from core.installer import generate_cyber_radar_ico; generate_cyber_radar_ico('ui/assets/diskradar.ico')"

REM 5. Compilacao PyInstaller (--onedir ultra-rapido)
echo.
echo [PASSO 4/5] Gerando binario nativo autonomo via PyInstaller...
echo Compilando em modo --onedir para abertura instantanea sem delay de descompactacao...

set "VER_FILE_FLAG="
if exist "installer\file_version_info.txt" set "VER_FILE_FLAG=--version-file=installer\file_version_info.txt"

"%PY_EXE%" %PY_ARGS% -m PyInstaller --clean --noconfirm --onedir --windowed --name "DiskRadar" --icon="ui\assets\diskradar.ico" %VER_FILE_FLAG% --collect-all customtkinter main.py
if errorlevel 1 goto :BUILD_FAIL

if exist "dist\DiskRadar\DiskRadar.exe" (
    copy /y "dist\DiskRadar\DiskRadar.exe" "DiskRadar.exe" >nul 2>&1
    echo [OK] Binario standalone gerado em: dist\DiskRadar\DiskRadar.exe
)

REM 6. Inno Setup 6 (Opcional - gera o instalador final .exe de 1 clique)
echo.
echo [PASSO 5/5] Verificando compilador do Inno Setup 6 (ISCC.exe)...
set "ISCC_BIN="
where iscc.exe >nul 2>&1
if %errorlevel% equ 0 set "ISCC_BIN=iscc.exe"

if not defined ISCC_BIN (
    if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC_BIN=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
    if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC_BIN=%ProgramFiles%\Inno Setup 6\ISCC.exe"
    if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" set "ISCC_BIN=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)

if defined ISCC_BIN (
    echo   Compilador Inno Setup encontrado em: "%ISCC_BIN%"
    echo   Empacotando instalador final unico com compressao LZMA2...
    "%ISCC_BIN%" /O"dist_installer" installer\diskradar_setup.iss
    if errorlevel 1 (
        echo   [AVISO] Falha ao compilar com Inno Setup.
    ) else (
        echo   [SUCESSO] Instalador final gerado em: dist_installer\Geio_DiskRadar_Setup_v%VERSION%.exe
    )
) else (
    echo   [INFO] Inno Setup 6 nao detectado nesta maquina.
    echo   A pasta dist\DiskRadar\ pode ser distribuida diretamente ou compilada na nuvem via GitHub Actions.
)

echo.
echo ============================================================================
echo [SUCESSO TOTAL] COMPILACAO CONCLUIDA!
echo ============================================================================
echo Artefatos gerados:
if exist "dist\DiskRadar\DiskRadar.exe" echo   - dist\DiskRadar\ (Executavel nativo + runtime Python embutido)
if exist "dist_installer\Geio_DiskRadar_Setup_v%VERSION%.exe" echo   - dist_installer\Geio_DiskRadar_Setup_v%VERSION%.exe (Instalador Unico)
echo ============================================================================
exit /b 0

:BUILD_FAIL
echo.
echo ============================================================================
echo [ERRO] O PyInstaller falhou na compilacao.
echo ============================================================================
exit /b 1
