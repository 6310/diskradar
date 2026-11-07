import unittest
from core.classifier import (
    CriticalFileItem,
    HotFolderItem,
    YearActivityStats,
)


class TestClassifier(unittest.TestCase):
    def test_hot_folder_item_properties(self):
        """Testa propriedades computadas de agrupamento de pastas quentes."""
        item = HotFolderItem(
            folder_path="/home/user/Pictures/Viagem",
            photos_count=150,
            videos_count=5,
            docs_count=2,
            total_bytes=500 * 1024 * 1024,  # 500 MB
            latest_mtime=1600000000.0,
        )
        self.assertEqual(item.total_files, 157)
        self.assertEqual(item.dominant_icon_tag, "[FOTOS]")
        self.assertEqual(item.formatted_size, "500.00 MB")
        self.assertNotEqual(item.formatted_date, "N/A")
        self.assertGreater(item.relevance_score, 0)

    def test_hot_folder_item_dominant_tag(self):
        """Testa identificação do tipo dominante de arquivo na pasta."""
        video_folder = HotFolderItem(
            folder_path="/videos",
            photos_count=2,
            videos_count=20,
            docs_count=1,
        )
        self.assertEqual(video_folder.dominant_icon_tag, "[VÍDEOS]")

        doc_folder = HotFolderItem(
            folder_path="/docs",
            photos_count=0,
            videos_count=0,
            docs_count=10,
        )
        self.assertEqual(doc_folder.dominant_icon_tag, "[DOCS]")

    def test_critical_file_item(self):
        """Testa a estrutura e métodos de apresentação de achados críticos."""
        crit = CriticalFileItem(
            name="wallet.dat",
            full_path="D:\\Wallets\\wallet.dat",
            category_key="CRYPTO_WALLETS",
            tag_label="[Cripto Wallet]",
            size_bytes=64 * 1024,
            mtime=1650000000.0,
            matched_reason="Carteira Bitcoin Core",
        )
        self.assertEqual(crit.formatted_size, "64.00 KB")
        self.assertIn("2022", crit.formatted_date)
        self.assertEqual(crit.category_key, "CRYPTO_WALLETS")

    def test_year_activity_stats(self):
        """Testa resumo de atividades da linha do tempo forense."""
        stats = YearActivityStats(
            year=2021,
            total_files=500,
            total_bytes=1024 * 1024 * 1024,
            photos_count=300,
            videos_count=50,
            docs_count=140,
            critical_count=10,
        )
        self.assertEqual(stats.year, 2021)
        self.assertEqual(stats.formatted_size, "1.00 GB")


if __name__ == "__main__":
    unittest.main()
