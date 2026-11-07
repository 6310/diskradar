"""
Ponto de entrada principal do Geio DiskRadar — Triador e Indexador Read-Only de HDs e SSDs de Sucata.

Otimizações de inicialização para Windows:
- Ativação de Per-Monitor DPI Awareness no Windows 10/11 (evita fontes borradas/embaçadas)
- Redirecionamento seguro de sys.stdout/sys.stderr quando empacotado em modo --windowed
- Registro de AppUserModelID para ícone e agrupamento independente na Barra de Tarefas
"""

import io
import os
import sys

# Proteção contra falhas de 'NoneType.write' no PyInstaller --windowed
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

# Otimizações de exibição nativas do Windows
if sys.platform == "win32":
    try:
        import ctypes
        # 1. Ativa Per-Monitor DPI Awareness (evita desfoque pelo DWM do Windows)
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()

        # 2. Define identificador de processo para ícone independente na Barra de Tarefas
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("geio.diskradar.app.2.1.0")
    except Exception:
        pass

# Garante que o diretório raiz do projeto esteja no sys.path mesmo quando empacotado via PyInstaller
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ui.app import DiskRadarApp


def main() -> None:
    """Inicializa e executa a aplicação Desktop CustomTkinter."""
    app = DiskRadarApp()
    app.mainloop()


if __name__ == "__main__":
    main()
