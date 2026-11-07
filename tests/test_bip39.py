import unittest
from core.bip39 import BIP39_WORDLIST, detect_bip39_seed


class TestBIP39(unittest.TestCase):
    def test_wordlist_size(self):
        """Verifica se a wordlist oficial contém exatamente 2048 palavras únicas."""
        self.assertEqual(len(BIP39_WORDLIST), 2048)
        self.assertIn("abandon", BIP39_WORDLIST)
        self.assertIn("zoo", BIP39_WORDLIST)

    def test_detect_valid_12_word_seed(self):
        """Detecta corretamente uma semente BIP-39 válida de 12 palavras."""
        text = "army van defense carry jealous true garbage claim echo media make crunch"
        result = detect_bip39_seed(text)
        self.assertEqual(result, 12)

    def test_detect_valid_24_word_seed(self):
        """Detecta corretamente uma semente BIP-39 válida de 24 palavras."""
        seed_words = [
            "abandon", "ability", "able", "about", "above", "absent",
            "absorb", "abstract", "absurd", "abuse", "access", "accident",
            "account", "accuse", "achieve", "acid", "acoustic", "acquire",
            "across", "act", "action", "actor", "actress", "actual"
        ]
        text = "Minha carteira de backup:\n" + " ".join(seed_words) + "\nGuardar com cuidado."
        result = detect_bip39_seed(text)
        self.assertEqual(result, 24)

    def test_reject_random_or_short_text(self):
        """Rejeita textos aleatórios ou sequências com menos de 12 palavras."""
        self.assertIsNone(detect_bip39_seed("ola mundo este texto nao tem nada a ver"))
        self.assertIsNone(detect_bip39_seed(""))
        self.assertIsNone(detect_bip39_seed("abandon ability able about above"))  # apenas 5 palavras


if __name__ == "__main__":
    unittest.main()
