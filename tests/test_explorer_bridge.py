import unittest
from core.explorer_bridge import open_in_explorer


class TestExplorerBridge(unittest.TestCase):
    def test_empty_path(self):
        """Verifica se caminhos vazios retornam False com segurança sem lançar exceções."""
        self.assertFalse(open_in_explorer(""))
        self.assertFalse(open_in_explorer(None))  # type: ignore


if __name__ == "__main__":
    unittest.main()
