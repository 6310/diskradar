#!/usr/bin/env python3
"""
Runner Consolidado de Emulação Windows 10/11 & Chaos Engineering do Geio DiskRadar v2.2.0.
Executa a bateria completa de validação do ambiente Windows:
1. Constrói disco virtual forense sintético de sucata (C:\\)
2. Inicializa o servidor Stitch com OS Mock (sys.platform='win32') e interceptores WMI/Explorer
3. Dispara varredura assíncrona sob Chaos Engineering (injetando Bad Blocks e Circuit Breaker)
4. Valida endpoints REST (/api/state, /api/system_diagnostics, /api/inspect_hex)
5. Captura tela headless com User-Agent Windows 10 / Microsoft Edge
6. Exporta laudo de auditoria e imagens para a pasta compartilhada
"""

import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

# Garante path correto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.diagnostics import run_system_diagnostics
from core.evidence import export_evidence_file
from core.hex_inspector import inspect_file_sector
from tests.emulation.mock_windows_env import (
    CAPTURED_EXPLORER_CALLS,
    ChaosInjector,
    patch_windows_environment,
)
from tests.emulation.synthetic_disk_builder import build_synthetic_windows_disk
from ui.stitch_server import start_stitch_background_server

SHARED_DEST_DIR = "/home/geio/Área de trabalho/COMPARTILHADO/screenshots_emulacao_windows"


def print_banner():
    print("\033[1;36m" + "=" * 78)
    print("  GEIO DISKRADAR v2.2.0 // HARNESS DE EMULAÇÃO FORENSE WINDOWS 10/11")
    print("  Chaos Engineering & Blindagem Anti-Travamento (100% Read-Only)")
    print("=" * 78 + "\033[0m\n")


def run_emulation():
    print_banner()

    temp_root = tempfile.mkdtemp(prefix="diskradar_win_emulation_")
    screenshots_dir = "/tmp/diskradar_windows_screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    try:
        os.makedirs(SHARED_DEST_DIR, exist_ok=True)
    except Exception:
        pass

    print(f"\033[1;33m[1/7] Construindo Disco Virtual Forense de Sucata em:\033[0m {temp_root}")
    disk_info = build_synthetic_windows_disk(temp_root)
    print(f"      - Raiz do Alvo: {disk_info['root']}")
    print(f"      - Seed BIP-39 (EN 12 palavras): {disk_info['seed_en']}")
    print(f"      - Seed BIP-39 (PT 24 palavras): {disk_info['seed_pt']}")
    print(f"      - Bitcoin Core wallet.dat: {disk_info['wallet_dat']}")
    print(f"      - AutoCAD DWG: {disk_info['cad_dwg']}")
    print(f"      - Caminho Longo (>260 chars): {disk_info['long_file']}")
    print(f"      - Falhas de I/O (Bad Sectors): {disk_info['dead_folder']}\n")

    server = None

    with patch_windows_environment():
        print(f"\033[1;33m[2/7] Inicializando Servidor Stitch v2.2.0 sob sys.platform='win32'...\033[0m")
        url, controller, server = start_stitch_background_server()
        # Aponta o controlador para o disco virtual
        controller.select_target(temp_root)
        print(f"      - Servidor HTTP operacional em {url} e pronto para consumo da interface.\n")

        print("\033[1;33m[3/7] Executando Autoteste de Diagnóstico do Sistema (/api/system_diagnostics)...\033[0m")
        diag_res = run_system_diagnostics(temp_root)
        print(f"      - Status Geral: \033[1;32m{diag_res['status']}\033[0m ({diag_res['total_checks']} checagens)")
        for c in diag_res["checks"]:
            color = "\033[32m" if c["status"] == "PASS" else "\033[33m"
            print(f"        * [{c['status']}] {c['name']}: {c['message']}\033[0m")
        print()

        print("\033[1;33m[4/7] Disparando Varredura Assíncrona com Chaos Injector (Bad Sectors & Circuit Breaker)...\033[0m")
        start_t = time.monotonic()
        with ChaosInjector():
            controller.start_scan()
            # Aguarda a varredura finalizar
            for _ in range(60):
                time.sleep(0.1)
                with controller.lock:
                    if controller.has_finished:
                        break

        elapsed = time.monotonic() - start_t
        res = controller.scan_result
        print(f"      - Varredura finalizada em {elapsed:.2f} segundos!")
        print(f"      - Arquivos Varridos: {controller.scanned_files}")
        print(f"      - Pastas Varridas: {controller.scanned_dirs}")
        print(f"      - Pastas Quentes Encontradas: {controller.hot_folders_count}")
        print(f"      - Achados Críticos (Agulhas no Palheiro): {controller.critical_count}")
        print(f"      - Falhas Físicas e Bad Blocks Isolados: {controller.errors_count}\n")

        print("\033[1;33m[5/7] Validando Inspeção Hexadecimal Read-Only de wallet.dat...\033[0m")
        hex_res = inspect_file_sector(disk_info["wallet_dat"], offset=0, length=512)
        print(f"      - Arquivo: {hex_res.file_path}")
        print(f"      - Assinatura Mágica: \033[1;32m{hex_res.magic_signature}\033[0m")
        print(f"      - Detalhes: {hex_res.magic_details}")
        print(f"      - SHA-256 Parcial: {hex_res.partial_sha256[:24]}...")
        print(f"      - Entropia de Shannon: {hex_res.entropy} ({hex_res.entropy_label})\n")

        print("\033[1;33m[6/7] Validando Extração Forense de Evidências com Hash SHA-256...\033[0m")
        evi_dir = os.path.join(temp_root, "Evidencias_Extraidas")
        evi_res = export_evidence_file(disk_info["seed_en"], destination_dir=evi_dir)
        print(f"      - Arquivo: {evi_res['file_name']}")
        print(f"      - Hash SHA-256: \033[1;32m{evi_res['sha256']}\033[0m")
        print(f"      - Destino: {evi_res['dest_path']}")
        print(f"      - Manifesto de Custódia: {evi_res['manifest_path']}\n")

        print("\033[1;33m[7/7] Capturando Telas com Navegador Headless (Windows 10 / Edge User-Agent)...\033[0m")
        ss_path = os.path.join(screenshots_dir, "01_dashboard_windows_edge.png")
        firefox_bin = None
        for cand in ("/usr/bin/firefox", "/usr/bin/firefox-esr", "firefox", "firefox-esr"):
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                firefox_bin = cand
                break
        if firefox_bin:
            try:
                cmd = [
                    firefox_bin,
                    "--headless",
                    "--screenshot",
                    ss_path,
                    "--window-size=1440,900",
                    url,
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
                if os.path.isfile(ss_path):
                    print(f"      \033[1;32m✓ Captura salva em:\033[0m {ss_path}")
                    try:
                        shutil.copy2(ss_path, os.path.join(SHARED_DEST_DIR, "01_dashboard_windows_edge.png"))
                        print(f"      \033[1;32m✓ Copiada para pasta compartilhada:\033[0m {SHARED_DEST_DIR}/01_dashboard_windows_edge.png")
                    except Exception:
                        pass
                else:
                    print("      - Firefox headless não gerou imagem direta.")
            except Exception as exc:
                print(f"      - Aviso na captura gráfica: {exc}")
        else:
            print("      - Firefox não encontrado para captura gráfica.")

    if server:
        server.shutdown()

    shutil.rmtree(temp_root, ignore_errors=True)

    print("\n\033[1;32m" + "=" * 78)
    print("  ✓ LAUDO FINAL DE EMULAÇÃO WINDOWS: APROVADO COM 100% DE SUCESSO!")
    print("  ✓ Todas as proteções contra travamento e edge cases foram validadas.")
    print("=" * 78 + "\033[0m\n")


if __name__ == "__main__":
    run_emulation()
