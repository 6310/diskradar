"""
Ponto de entrada principal do Geio DiskRadar v2.3.0 — Triador e Indexador Read-Only de HDs e SSDs de Sucata.

Modos de Interface Gráfica:
- Padrão (Stitch Cyber-Forensic Precision GUI v2.3.0):
  Abre a estação de trabalho forense completa (10 telas e modais unificados:
  Pastas Quentes, Arquivos Críticos, Árvore de Usuários & Atalhos, Linha do Tempo,
  Log de Erros & Bad Blocks, Monitor de Varredura ao Vivo, Resumo Pós-Varredura,
  Modal S.M.A.R.T. Detalhado, Modal de Exportação HTML, Inspetor Hexadecimal Read-Only
  e Recuperação Rápida de Apagados) em janela nativa dedicada (--app mode via Edge/Chrome WebView),
  100% integrada ao motor Python Read-Only (core/).
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
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("geio.diskradar.app.2.3.0")

        # 3. Otimização Anti-Travamento: Rebaixa prioridade de I/O e CPU para segundo plano no kernel NT
        # Garante que o Windows, mouse, Explorer e outros apps continuem 100% responsivos mesmo com HD morrendo
        try:
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            # Tenta ativar PROCESS_MODE_BACKGROUND_BEGIN (0x00100000) ou fallback BELOW_NORMAL (0x00004000)
            if not ctypes.windll.kernel32.SetPriorityClass(handle, 0x00100000):
                ctypes.windll.kernel32.SetPriorityClass(handle, 0x00004000)
        except Exception:
            pass
    except Exception:
        pass


def _enable_live_ota_override() -> str:
    """
    Garante que atualizações OTA (Over-The-Air) aplicadas na pasta da aplicação
    sejam importadas com prioridade máxima, mesmo quando executando sob um
    binário compilado pelo PyInstaller (sys.frozen = True).
    Retorna o diretório base da aplicação.
    """
    if getattr(sys, "frozen", False):
        app_dir = os.path.dirname(os.path.abspath(sys.executable))
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    if app_dir not in sys.path or sys.path[0] != app_dir:
        sys.path.insert(0, app_dir)

    return app_dir


BASE_DIR = _enable_live_ota_override()


def _check_existing_instance_and_focus(port: int = 8080) -> bool:
    """
    Proteção Single-Instance: Verifica se o servidor Geio DiskRadar já está
    respondendo na porta local. Se estiver ativo, dispara o navegador para
    reutilizar a sessão e retorna True para encerrar o processo duplicado.
    """
    import urllib.request
    try:
        url = f"http://127.0.0.1:{port}/api/version_status"
        req = urllib.request.Request(url, headers={"User-Agent": "GeioDiskRadar-Launcher"})
        with urllib.request.urlopen(req, timeout=0.6) as resp:
            if resp.status == 200:
                import webbrowser
                webbrowser.open(f"http://127.0.0.1:{port}/")
                return True
    except Exception:
        pass
    return False


def _run_classic_tk_ui() -> None:
    """Inicializa a interface CustomTkinter clássica (fallback ou flag --classic)."""
    from ui.app import DiskRadarApp

    app = DiskRadarApp()
    app.mainloop()


def main() -> None:
    """Inicializa a interface gráfica Stitch Cyber-Forensic Precision (ou CustomTkinter com --classic)."""
    # Proteção contra inicialização de processos múltiplos concorrentes
    if _check_existing_instance_and_focus():
        return

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
