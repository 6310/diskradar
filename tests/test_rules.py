import unittest
from core.rules import (
    ALL_INTERESTING_EXTENSIONS,
    CRITICAL_CATEGORIES,
    format_size,
    is_file_potentially_relevant,
)


class TestRules(unittest.TestCase):
    def test_format_size(self):
        """Valida a conversão legível de bytes para KB, MB, GB, TB."""
        self.assertEqual(format_size(0), "0 B")
        self.assertEqual(format_size(500), "500 B")
        self.assertEqual(format_size(1024), "1.00 KB")
        self.assertEqual(format_size(1024 * 1024), "1.00 MB")
        self.assertEqual(format_size(1024 * 1024 * 1024), "1.00 GB")
        self.assertEqual(format_size(2 * 1024 * 1024 * 1024 * 1024), "2.00 TB")

    def test_is_file_potentially_relevant(self):
        """Testa o filtro relâmpago O(1) de arquivos de interesse."""
        # Extensões conhecidas
        self.assertTrue(is_file_potentially_relevant("foto.jpg", ".jpg"))
        self.assertTrue(is_file_potentially_relevant("planilha.xlsx", ".xlsx"))
        self.assertTrue(is_file_potentially_relevant("backup.tar.gz", ".tar.gz"))
        self.assertTrue(is_file_potentially_relevant("projeto.dwg", ".dwg"))

        # Nomes exatos de carteiras
        self.assertTrue(is_file_potentially_relevant("wallet.dat", ".dat"))
        self.assertTrue(is_file_potentially_relevant("monero-wallet-keys", ""))

        # Palavras-chave no nome
        self.assertTrue(is_file_potentially_relevant("minhas_senhas.txt", ".txt"))
        self.assertTrue(is_file_potentially_relevant("seed_backup.md", ".md"))

        # Lixo de sistema ignorado
        self.assertFalse(is_file_potentially_relevant("kernel32.dll", ".dll"))
        self.assertFalse(is_file_potentially_relevant("pagefile.sys", ".sys"))
        self.assertFalse(is_file_potentially_relevant("temp_cache.tmp", ".tmp"))

    def test_categories_dict(self):
        """Verifica se todas as categorias críticas necessárias estão registradas."""
        expected = [
            "ALL",
            "CRYPTO_WALLETS",
            "BROWSERS_CREDS",
            "KEYWORDS",
            "CAD_DESIGN",
            "IRPF_FISCAL",
            "DB_ERP",
            "EMAIL_MSG",
            "CERT_KEYS",
            "ARCHIVES",
        ]
        for key in expected:
            self.assertIn(key, CRITICAL_CATEGORIES)


if __name__ == "__main__":
    unittest.main()
