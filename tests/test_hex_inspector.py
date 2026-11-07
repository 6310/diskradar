"""Testes unitários do Inspetor Hexadecimal Read-Only (core/hex_inspector.py) e Controlador Stitch."""

import os
import tempfile
import unittest

from core.hex_inspector import (
    calculate_shannon_entropy,
    detect_magic_signature,
    inspect_file_sector,
)


class TestHexInspector(unittest.TestCase):
    """Valida leitura Read-Only de setores de 512 bytes, entropia e assinaturas Magic Bytes."""

    def test_shannon_entropy_zero_and_high(self) -> None:
        self.assertEqual(calculate_shannon_entropy(b""), 0.0)
        self.assertEqual(calculate_shannon_entropy(b"\x00" * 512), 0.0)
        # Sequência uniforme de 0..255 tem entropia máxima de 8.0 bits/byte
        uniform = bytes(range(256)) * 2
        self.assertAlmostEqual(calculate_shannon_entropy(uniform), 8.0, places=2)

    def test_detect_magic_signatures(self) -> None:
        name_sqlite, _desc = detect_magic_signature(b"SQLite format 3\x00" + b"\x00" * 32)
        self.assertIn("SQLite 3", name_sqlite)

        name_pdf, _desc = detect_magic_signature(b"%PDF-1.7\n" + b"\x00" * 32)
        self.assertIn("PDF", name_pdf)

        name_bdb, _desc = detect_magic_signature(b"\x00" * 12 + b"\x61\x15\x06\x00" + b"\x00" * 32)
        self.assertIn("Berkeley DB", name_bdb)

    def test_inspect_file_sector_readonly(self) -> None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            payload = b"SQLite format 3\x00" + bytes(range(256)) * 3
            tmp.write(payload)
            tmp_path = tmp.name

        try:
            res = inspect_file_sector(tmp_path, offset=0, length=512)
            self.assertIsNone(res.error_message)
            self.assertEqual(res.bytes_read, 512)
            self.assertEqual(len(res.rows), 32)  # 32 linhas x 16 bytes = 512B
            self.assertIn("SQLite 3", res.magic_signature)
            self.assertGreater(res.entropy, 5.0)
            self.assertEqual(len(res.partial_sha256), 64)

            # Testa navegação para o segundo setor (+512B)
            res2 = inspect_file_sector(tmp_path, offset=512, length=512)
            self.assertIsNone(res2.error_message)
            self.assertEqual(res2.offset, 512)
            self.assertEqual(res2.bytes_read, len(payload) - 512)
        finally:
            os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
