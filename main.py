"""
Ponto de entrada principal do Geio DiskRadar v2.2.0 — Triador e Indexador Read-Only de HDs e SSDs de Sucata.

Modos de Interface Gráfica:
- Padrão (Stitch Cyber-Forensic Precision GUI v2.2.0):
  Abre a estação de trabalho forense completa (10 telas e modais unificados:
  Pastas Quentes, Arquivos Críticos, Árvore de Usuários & Atalhos, Linha do Tempo,
  Log de Erros & Bad Blocks, Monitor de Varredura ao Vivo, Resumo Pós-Varredura,
  Modal S.M.A.R.T. Detalhado, Modal de Exportação HTML e Inspetor Hexadecimal Read-Only)
  em janela nativa dedicada (--app mode via Edge/Chrome WebView), 100% integrada ao
  motor Python Read-Only (core/).
- Modo Clássico (--classic ou --tk):
  Abre a interface nativa em CustomTkinter (ui/app.py), que também conta com botão
  para abrir a Interface Stitch sob demanda.
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
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("geio.diskradar.app.2.2.0")
    except Exception:
        pass

# Garante que o diretório raiz do projeto esteja no sys.path mesmo quando empacotado via PyInstaller
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


def _run_classic_tk_ui() -> None:
    """Inicializa a interface CustomTkinter clássica (fallback ou flag --classic)."""
    from ui.app import DiskRadarApp

    app = DiskRadarApp()
    app.mainloop()


def main() -> None:
    """Inicializa a interface gráfica Stitch Cyber-Forensic Precision (ou CustomTkinter com --classic)."""
    args = [a.lower() for a in sys.argv[1:]]
    if "--classic" in args or "--tk" in args:
        _run_classic_tk_ui()
        return

    try:
        from ui.stitch_server import launch_stitch_desktop_app

        if not launch_stitch_desktop_app():
            _run_classic_tk_ui()
    except Exception:
        # Fallback automático para CustomTkinter caso ocorra qualquer restrição de ambiente
        _run_classic_tk_ui()


if __name__ == "__main__":
    main()
