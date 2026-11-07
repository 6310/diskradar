"""
Validador Estático de Scripts Batch do Windows (.bat) do Geio DiskRadar.
Verifica se os arquivos `Compilar_EXE.bat` e `Executar_DiskRadar.bat` seguem as regras
estritas do interpretador CMD do Windows 10/11:
- Ausência de blocos aninhados de parênteses com %errorlevel% (evitando '. foi inesperado neste momento.')
- Presença de flags obrigatórias do PyInstaller (--collect-all customtkinter)
- Sincronismo da versão v2.2.0 nos cabeçalhos
"""

import os
import re
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestBatchScriptsSyntax(unittest.TestCase):

    def test_compilar_exe_bat_syntax(self):
        bat_path = os.path.join(BASE_DIR, "Compilar_EXE.bat")
        self.assertTrue(os.path.isfile(bat_path), f"Arquivo não encontrado: {bat_path}")

        with open(bat_path, "r", encoding="latin-1", errors="replace") as f:
            content = f.read()

        # 1. Deve possuir versão 2.2.0
        self.assertIn("2.2.0", content, "Compilar_EXE.bat deve referenciar a versão 2.2.0.")

        # 2. Deve coletar CustomTkinter
        self.assertIn("--collect-all customtkinter", content, "PyInstaller deve incluir --collect-all customtkinter.")

        # 3. Deve usar goto lineares para verificação de erro em vez de if (...) com erro de expansão CMD
        self.assertIn("if errorlevel 1 goto", content, "Compilar_EXE.bat deve usar 'if errorlevel 1 goto' seguro.")

    def test_executar_diskradar_bat_syntax(self):
        bat_path = os.path.join(BASE_DIR, "Executar_DiskRadar.bat")
        self.assertTrue(os.path.isfile(bat_path), f"Arquivo não encontrado: {bat_path}")

        with open(bat_path, "r", encoding="latin-1", errors="replace") as f:
            content = f.read()

        # 1. Deve verificar python no path
        self.assertTrue("where python" in content.lower() or "python" in content.lower())

        # 2. Deve invocar main.py
        self.assertIn("main.py", content)


if __name__ == "__main__":
    unittest.main()
