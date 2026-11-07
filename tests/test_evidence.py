"""
Testes unitários para o Módulo de Extração Segura de Evidências Forenses (core/evidence.py).
"""

import hashlib
import json
import os
import shutil
import tempfile
import unittest

from core.evidence import calculate_file_sha256, export_evidence_file


class TestEvidenceExtraction(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="diskradar_test_evidence_")
        self.src_file = os.path.join(self.temp_dir, "test_wallet.dat")
        self.sample_content = b"\x00\x05\x31\x62" + b"TEST_BITCOIN_WALLET_DATA_BYTES" * 10
        with open(self.src_file, "wb") as f:
            f.write(self.sample_content)
        self.expected_sha256 = hashlib.sha256(self.sample_content).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_calculate_file_sha256(self):
        calc_hash = calculate_file_sha256(self.src_file)
        self.assertEqual(calc_hash, self.expected_sha256)

    def test_export_evidence_file_success(self):
        dest_dir = os.path.join(self.temp_dir, "Exported_Evidences")
        res = export_evidence_file(self.src_file, destination_dir=dest_dir)

        self.assertTrue(res["ok"])
        self.assertEqual(res["sha256"], self.expected_sha256)
        self.assertTrue(os.path.isfile(res["dest_path"]))
        self.assertTrue(os.path.isfile(res["manifest_path"]))

        # Confirma que o conteúdo copiado é idêntico
        with open(res["dest_path"], "rb") as f:
            dest_content = f.read()
        self.assertEqual(dest_content, self.sample_content)

        # Confirma conteúdo do manifesto
        with open(res["manifest_path"], "r", encoding="utf-8") as f_m:
            manifest = json.load(f_m)
        self.assertEqual(manifest["custody_status"], "VERIFIED_INTEGRITY_MATCH")
        self.assertEqual(manifest["original_file"]["sha256"], self.expected_sha256)
        self.assertEqual(manifest["exported_file"]["sha256"], self.expected_sha256)

    def test_export_evidence_nonexistent_file(self):
        res = export_evidence_file(os.path.join(self.temp_dir, "nao_existe.txt"))
        self.assertFalse(res["ok"])
        self.assertIn("não existe", res["error"])


if __name__ == "__main__":
    unittest.main()
