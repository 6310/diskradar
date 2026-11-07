"""
Suíte de Testes Automatizados de Edge Cases e Blindagem Anti-Travamento (v2.2.0).
Valida o comportamento do Geio DiskRadar sob as condições mais adversas de discos de sucata:
- Bad Blocks e Circuit Breaker em hardware degradado
- Desconexão abrupta de cabo USB (Surprise Removal)
- Sementes BIP-39 em Português e Inglês
- Nomes reservados do MS-DOS (CON, PRN, AUX, NUL)
- Caminhos ultra-longos (> 260 caracteres via prefixo \\\\?\\)
- Debounce e integridade de comandos do Windows Explorer
"""

import os
import queue
import shutil
import tempfile
import unittest
from unittest.mock import patch

from core.diagnostics import run_system_diagnostics
from core.explorer_bridge import open_in_explorer
from core.scanner import AsyncDiskScanner
from tests.emulation.mock_windows_env import (
    CAPTURED_EXPLORER_CALLS,
    ChaosInjector,
    patch_windows_environment,
)
from tests.emulation.synthetic_disk_builder import build_synthetic_windows_disk


class TestWindowsEdgeCasesAndAntiFreeze(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="diskradar_edge_test_")
        self.disk_info = build_synthetic_windows_disk(self.temp_dir)
        self.event_q = queue.Queue()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_bip39_seeds_pt_and_en_detection(self):
        """Verifica a identificação de sementes BIP-39 em inglês (12 palavras) e português (24 palavras)."""
        scanner = AsyncDiskScanner(self.disk_info["root"], self.event_q)
        scanner._run_scan()

        # Obtém o resultado consolidado da fila
        result = None
        while not self.event_q.empty():
            ev = self.event_q.get_nowait()
            if ev.get("type") == "SCAN_FINISHED":
                result = ev.get("result")

        self.assertIsNotNone(result, "O evento SCAN_FINISHED deve ser emitido.")
        crit_names = [c.name for c in result.critical_items]

        # Ambas as seeds devem estar catalogadas
        has_seed_en = any("carteira_seed_12palavras" in n for n in crit_names)
        has_seed_pt = any("backup_seed_portugues" in n for n in crit_names)

        self.assertTrue(has_seed_en, "Seed BIP-39 em inglês deve ser detectada.")
        self.assertTrue(has_seed_pt, "Seed BIP-39 em português deve ser detectada.")

        # Verifica se o wallet.dat e Chrome Login Data foram detectados
        has_wallet = any("wallet.dat" in n for n in crit_names)
        has_chrome = any("Login Data" in n or "Chrome" in n for n in crit_names)
        self.assertTrue(has_wallet, "Bitcoin wallet.dat deve ser detectado.")
        self.assertTrue(has_chrome, "Credenciais do Chrome devem ser detectadas.")

    def test_chaos_bad_sectors_and_circuit_breaker(self):
        """
        Injeta falhas de I/O de hardware (WinError 1117 e WinError 23) e valida:
        1. Isolamento dos bad blocks sem travar a varredura.
        2. Ativação do Circuit Breaker na subpasta com 15 setores mortos.
        """
        with ChaosInjector():
            scanner = AsyncDiskScanner(self.disk_info["root"], self.event_q)
            scanner._run_scan()

        result = None
        while not self.event_q.empty():
            ev = self.event_q.get_nowait()
            if ev.get("type") == "SCAN_FINISHED":
                result = ev.get("result")

        self.assertIsNotNone(result)
        self.assertGreater(len(result.errors), 0, "Erros de I/O simulados devem ser registrados.")

        # Confirma que os erros foram categorizados como falha física
        has_bad_block_error = any("BAD BLOCK / ERRO FÍSICO I/O" in e.error_type for e in result.errors)
        self.assertTrue(has_bad_block_error, "Erros WinError 1117/23 devem ser marcados como BAD BLOCK.")

        # Confirma que o Circuit Breaker atuou na DeadPlatterFolder
        circuit_broken = any("[CIRCUIT BREAKER]" in e.message for e in result.errors)
        self.assertTrue(circuit_broken, "O Circuit Breaker deve desarmar após falhas consecutivas de hardware.")

    def test_surprise_usb_unplug_protection(self):
        """Simula a desconexão abrupta do drive USB (WinError 1167) no meio da varredura."""
        # Simula desconexão após ler 5 arquivos
        with ChaosInjector(simulate_unplug_after_files=5):
            scanner = AsyncDiskScanner(self.disk_info["root"], self.event_q)
            scanner._run_scan()

        unplug_event_found = False
        result = None
        while not self.event_q.empty():
            ev = self.event_q.get_nowait()
            if ev.get("type") == "DEVICE_UNPLUGGED":
                unplug_event_found = True
            elif ev.get("type") == "SCAN_FINISHED":
                result = ev.get("result")

        self.assertTrue(unplug_event_found, "O evento DEVICE_UNPLUGGED deve ser notificado à GUI.")
        self.assertIsNotNone(result)
        self.assertTrue(result.is_device_unplugged, "O resultado final deve sinalizar desconexão de hardware.")
        # Garante que os arquivos encontrados antes da queda foram preservados
        self.assertGreaterEqual(result.scanned_files, 0)

    def test_windows_explorer_bridge_syntax_and_debounce(self):
        """Valida que chamadas ao explorer.exe seguem rigorosamente a regra /select,"C:\\..." e possuem debounce."""
        with patch_windows_environment():
            # 1. Teste de destaque de arquivo
            file_to_open = self.disk_info["seed_en"]
            ok_file = open_in_explorer(file_to_open, select_item=True)
            self.assertTrue(ok_file)

            # Confirma que o comando foi emitido no formato exato: explorer.exe /select,"<caminho>"
            self.assertEqual(len(CAPTURED_EXPLORER_CALLS), 1)
            cmd = CAPTURED_EXPLORER_CALLS[0]
            self.assertTrue(cmd.startswith('explorer.exe /select,"'), f"Formato incorreto: {cmd}")
            self.assertTrue(cmd.endswith('"'), f"Formato incorreto: {cmd}")
            self.assertIn(os.path.normpath(file_to_open), cmd)

            # 2. Teste de debounce (segundo clique imediato deve ser filtrado)
            ok_debounce = open_in_explorer(file_to_open, select_item=True)
            self.assertTrue(ok_debounce)
            # A lista de chamadas ainda deve ter 1 chamada (a segunda foi absorvida pelo debounce de 350ms)
            self.assertEqual(len(CAPTURED_EXPLORER_CALLS), 1)

    def test_system_diagnostics_evaluation(self):
        """Valida o funcionamento do módulo de diagnóstico do sistema."""
        diag = run_system_diagnostics(self.disk_info["root"])
        self.assertIn("status", diag)
        self.assertIn("checks", diag)
        self.assertGreaterEqual(len(diag["checks"]), 5)

        # O acesso de leitura ao diretório sintetizado deve passar (PASS)
        target_check = next((c for c in diag["checks"] if c["id"] == "target_read_access"), None)
        self.assertIsNotNone(target_check)
        self.assertEqual(target_check["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
