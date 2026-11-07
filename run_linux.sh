#!/usr/bin/env bash
# ==============================================================================
# Geio DiskRadar - Script de Inicialização Rápida no Linux
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Geio DiskRadar (Modo Read-Only) ==="

# Verifica / cria ambiente virtual Python
if [ ! -d "venv" ]; then
    echo "[1/2] Criando ambiente virtual Python (venv)..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip --quiet
    echo "[2/2] Instalando dependências..."
    ./venv/bin/pip install -r requirements.txt --quiet
else
    echo "[1/2] Ambiente virtual (venv) encontrado."
fi

echo "Iniciando interface gráfica do Geio DiskRadar..."
./venv/bin/python3 main.py
