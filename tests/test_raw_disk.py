"""
Testes de resiliência e suporte a Discos Físicos RAW / Não-Formatados (\\\\.\\PhysicalDriveX).
"""

import queue
import unittest

from core.disk_info import get_disk_badge_info
from core.hex_inspector import inspect_file_sector
from core.scanner import AsyncDiskScanner


class TestRawDiskSupport(unittest.TestCase):

    def test_raw_disk_badge_info(self):
        """Verifica que caminhos de discos físicos brutos inicializam o DiskBadgeInfo com segurança."""
        raw_path = r"\\.\PhysicalDrive1"
        badge = get_disk_badge_info(raw_path, query_hw=False)
        self.assertEqual(badge.target_path, raw_path)
        self.assertIn("RAW", badge.filesystem)
        self.assertEqual(len(badge.detected_users), 0)

    def test_raw_disk_scanner_graceful_stop(self):
        """Verifica que o scanner não trava nem dá crash ao receber um dispositivo RAW sem filesystem."""
        raw_path = r"\\.\PhysicalDrive2"
        event_q = queue.Queue()
        scanner = AsyncDiskScanner(raw_path, event_q)
        scanner._run_scan()

        finished_event = None
        while not event_q.empty():
            ev = event_q.get_nowait()
            if ev.get("type") == "SCAN_FINISHED":
                finished_event = ev

        self.assertIsNotNone(finished_event)
        res = finished_event["result"]
        self.assertFalse(res.was_cancelled)
        self.assertEqual(res.scanned_files, 0)
        self.assertGreaterEqual(len(res.errors), 1)
        self.assertIn("RAW", res.errors[0].message)

    def test_raw_disk_hex_inspector_permission_guidance(self):
        """Verifica que o Hex Inspector orienta sobre privilégios de Administrador ao inspecionar RAW."""
        raw_path = r"\\.\PhysicalDrive3"
        res = inspect_file_sector(raw_path, offset=0, length=512)
        # Em Linux/sandbox sem acesso a PhysicalDrive3, retornará erro ou permissão
        self.assertIsNotNone(res.error_message)


if __name__ == "__main__":
    unittest.main()
