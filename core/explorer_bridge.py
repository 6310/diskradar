r"""
Ponte de integração Read-Only com o gerenciador de arquivos do sistema operacional.
No Windows, utiliza explorer.exe /select,"C:\caminho\arquivo" para destacar arquivos,
ou explorer.exe "C:\caminho\pasta" para abrir diretórios diretamente.
No Linux, utiliza xdg-open no diretório correspondente.

Correções críticas para Windows 10/11:
- O parâmetro /select, deve ficar RIGOROSAMENTE FORA das aspas (ex: explorer.exe /select,"C:\...")
  evitando que o Windows Explorer confunda o comando e abra "Meus Documentos".
- Pastas (Hot Folders e Atalhos) são abertas diretamente para visualização imediata do conteúdo.
- Limpeza segura do prefixo estendido \\?\ e \\?\UNC\ antes de invocar o Explorer.
- Tratamento para raiz de unidade (ex: C:\ ou D:\).
"""

import os
import subprocess
import sys
from pathlib import Path


def open_in_explorer(target_path: str, select_item: bool = True) -> bool:
    """
    Abre o caminho especificado no Windows Explorer ou xdg-open no Linux.
    - Se for um diretório: abre a pasta diretamente.
    - Se for um arquivo e select_item=True: abre a pasta pai e destaca o arquivo (/select).
    - Se o arquivo não existir mais: abre a pasta pai onde ele estava.
    Retorna True se o comando foi disparado com sucesso, False caso contrário.
    """
    if not target_path:
        return False

    try:
        if sys.platform == "win32":
            # 1. Limpeza do prefixo estendido de caminhos longos (MAX_PATH)
            clean_path = target_path
            if clean_path.startswith("\\\\?\\UNC\\"):
                clean_path = "\\\\" + clean_path[8:]
            elif clean_path.startswith("\\\\?\\"):
                clean_path = clean_path[4:]

            norm_path = os.path.normpath(clean_path)

            # 2. Raiz de unidade (ex: C:\ ou D:\)
            split_drive = os.path.splitdrive(norm_path)
            is_drive_root = bool(split_drive[0] and split_drive[1] in ("\\", "/", ""))
            if is_drive_root:
                subprocess.Popen(f'explorer.exe "{norm_path}"')
                return True

            # 3. Se for um diretório existente, abre diretamente a pasta para ver o conteúdo
            if os.path.isdir(norm_path):
                subprocess.Popen(f'explorer.exe "{norm_path}"')
                return True

            # 4. Se for um arquivo existente e select_item for True, destaca o arquivo
            # ATENÇÃO: /select, PRECISA ficar fora das aspas para não abrir "Meus Documentos"
            if select_item and os.path.isfile(norm_path):
                subprocess.Popen(f'explorer.exe /select,"{norm_path}"')
                return True

            # 5. Se o arquivo não existir ou for caminho sem arquivo, abre a pasta pai
            parent = os.path.dirname(norm_path)
            if parent and os.path.isdir(parent):
                subprocess.Popen(f'explorer.exe "{parent}"')
                return True
            elif os.path.exists(norm_path):
                subprocess.Popen(f'explorer.exe "{norm_path}"')
                return True

            return False
        else:
            # Linux / macOS fallback
            p = Path(os.path.abspath(target_path))
            if p.is_file():
                folder_to_open = str(p.parent)
            elif p.is_dir():
                folder_to_open = str(p)
            else:
                folder_to_open = str(p.parent)

            if not os.path.exists(folder_to_open):
                return False

            if sys.platform == "darwin":
                subprocess.Popen(["open", folder_to_open])
            else:
                subprocess.Popen(
                    ["xdg-open", folder_to_open],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            return True
    except Exception:
        return False
