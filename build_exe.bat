@echo off
chcp 65001 >nul
title Geio DiskRadar - Compilador PyInstaller (.EXE)
echo ============================================================================
echo   GEIO DISKRADAR - GERADOR DE EXECUTAVEL UNICO WINDOWS (PyInstaller)
echo ============================================================================
echo.

REM Verifica se o Python esta disponivel no PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado no PATH do Windows!
    echo Instale o Python 3.11+ marcando a opcao "Add Python to PATH".
    pause
    exit /b 1
)

REM Cria ambiente virtual se nao existir
if not exist "venv\Scripts\activate.bat" (
    echo [1/4] Criando ambiente virtual Python ^(venv^)...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERRO] Falha ao criar venv.
        pause
        exit /b 1
    )
) else (
    echo [1/4] Ambiente virtual ^(venv^) ja encontrado.
)

echo [2/4] Ativando venv e instalando dependencias...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias do requirements.txt.
    pause
    exit /b 1
)

echo [3/4] Compilando executavel unico DiskRadar.exe via PyInstaller...
pyinstaller --clean --noconfirm --onefile --windowed --name "DiskRadar" --collect-all customtkinter main.py
if %errorlevel% neq 0 (
    echo [ERRO] A compilacao com PyInstaller falhou.
    pause
    exit /b 1
)

echo.
echo ============================================================================
echo [4/4] COMPILACAO CONCLUIDA COM SUCESSO!
echo O executavel final esta disponivel em:
echo   dist\DiskRadar.exe
echo ============================================================================
echo.
pause
