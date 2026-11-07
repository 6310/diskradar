"""
Motor Canônico de Instalação, Controle de Versão (SemVer) e Auto-Update para Windows do Geio DiskRadar.
Garante:
1. Instância única instalada no sistema (%LocalAppData%\\Programs\\GeioDiskRadar).
2. Verificação de versionamento antes de qualquer operação (Upgrade In-Place, Reparo ou Bloqueio de Downgrade).
3. Transação por manifesto (install_manifest.json) que remove arquivos obsoletos de versões antigas sem deixar lixo.
4. Registro oficial no Painel de Controle / Configurações do Windows (HKCU\\...\\Uninstall) sem duplicar entradas.
5. Atalho único "Geio DiskRadar.lnk" com ícone .ico nativo, removendo atalhos antigos versionados.
6. Atualização Over-The-Air (OTA) via repositório oficial no GitHub.
"""

import argparse
import datetime
import hashlib
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from typing import Any, Dict, List, Optional, Set, Tuple

APP_GUID = "8B49E7C2-1C2A-4D4F-9E62-F9F71B39D4E2"
APP_NAME = "Geio DiskRadar"
PUBLISHER = "Geio Forensics & Security"
DEFAULT_VERSION = "2.3.0"
UNINSTALL_REG_KEY = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{{{APP_GUID}}}"

# Pastas e arquivos que NUNCA devem ser copiados como código nem apagados como obsoletos de usuário
_IGNORED_DIRS: Set[str] = {
    ".git",
    "__pycache__",
    "venv",
    ".venv",
    "build",
    "dist",
    "dist_installer",
    "Evidencias_DiskRadar",
    "Recuperados_Apagados",
}

_IGNORED_FILES: Set[str] = {
    "cases.db",
    "compilacao.log",
    "instalacao.log",
    "install_manifest.json",
}


# ==============================================================================
# 1. VERSIONAMENTO SEMÂNTICO (SEMVER)
# ==============================================================================

def parse_semver(version_str: str) -> Tuple[int, int, int]:
    """
    Converte uma string de versão (ex: 'v2.3.0', '2.2.1-beta', '2.10') em tupla (major, minor, patch).
    """
    if not version_str:
        return (0, 0, 0)
    clean = version_str.strip().lstrip("vV")
    clean = clean.split("-")[0].split("+")[0]
    parts = clean.split(".")
    nums: List[int] = []
    for p in parts[:3]:
        digits = "".join(ch for ch in p if ch.isdigit())
        nums.append(int(digits) if digits else 0)
    while len(nums) < 3:
        nums.append(0)
    return (nums[0], nums[1], nums[2])


def compare_semver(v_new: str, v_old: str) -> int:
    """
    Compara duas versões semânticas:
    Retorna:
       1 se v_new > v_old (Upgrade)
       0 se v_new == v_old (Mesma versão / Reparo)
      -1 se v_new < v_old (Downgrade)
    """
    t_new = parse_semver(v_new)
    t_old = parse_semver(v_old)
    if t_new > t_old:
        return 1
    if t_new < t_old:
        return -1
    return 0


def get_project_root() -> str:
    """Retorna o diretório raiz de onde o código atual está sendo executado."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_version_json(base_dir: Optional[str] = None) -> Dict[str, Any]:
    """Lê o arquivo version.json de um diretório (ou usa fallback seguro)."""
    root = base_dir or get_project_root()
    v_path = os.path.join(root, "version.json")
    default_data = {
        "app_id": APP_GUID,
        "app_name": APP_NAME,
        "version": DEFAULT_VERSION,
        "channel": "stable",
        "release_date": "2026-11-07",
        "publisher": PUBLISHER,
        "repo_url": "https://github.com/6310/diskradar",
        "raw_version_url": "https://raw.githubusercontent.com/6310/diskradar/main/version.json",
        "zip_download_url": "https://github.com/6310/diskradar/archive/refs/heads/main.zip",
    }
    if os.path.isfile(v_path):
        try:
            with open(v_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                default_data.update(loaded)
        except Exception:
            pass
    return default_data


def get_app_version(base_dir: Optional[str] = None) -> str:
    """Retorna a string de versão com prefixo 'v' (ex: 'v2.3.0')."""
    raw = str(load_version_json(base_dir).get("version") or DEFAULT_VERSION).strip().lstrip("vV")
    return f"v{raw}"


# ==============================================================================
# 2. CAMINHO CANÔNICO ÚNICO DE INSTALAÇÃO NO WINDOWS
# ==============================================================================

def get_canonical_install_dir() -> str:
    """
    Retorna o diretório único oficial de instalação do Geio DiskRadar no sistema:
    No Windows: %LocalAppData%\\Programs\\GeioDiskRadar
    No Linux (testes/dev): ~/.local/share/GeioDiskRadar
    """
    if sys.platform == "win32":
        local_appdata = os.environ.get("LOCALAPPDATA")
        if not local_appdata:
            local_appdata = os.path.join(os.path.expanduser("~"), "AppData", "Local")
        return os.path.join(local_appdata, "Programs", "GeioDiskRadar")
    else:
        return os.path.join(os.path.expanduser("~"), ".local", "share", "GeioDiskRadar")


# ==============================================================================
# 3. GERADOR BINÁRIO NATIVO DE ÍCONE CYBER-FORENSIC (.ICO)
# ==============================================================================

def generate_cyber_radar_ico(dest_path: str) -> str:
    """
    Gera programaticamente um arquivo de ícone Windows (.ico) 32x32 32-bit BGRA válido,
    desenhando um radar circular Cyber-Forensic (#00F0FF e #4EDEA3 sobre #0C0E14),
    sem depender de bibliotecas externas de imagem (PIL/Pillow).
    """
    os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
    width = 32
    height = 32
    cx, cy = 15.5, 15.5

    # Pixels em formato BGRA bottom-up (padrão DIB do ICO)
    pixel_data = bytearray()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            dx = x - cx
            dy = y - cy
            dist = math.hypot(dx, dy)

            if dist > 15.2:
                # Fora do círculo: transparente
                pixel_data.extend((0, 0, 0, 0))
            elif 13.6 <= dist <= 15.2:
                # Anel externo Ciano (#00F0FF -> B=255, G=240, R=0, A=255)
                pixel_data.extend((255, 240, 0, 255))
            elif 7.8 <= dist <= 9.0:
                # Anel intermediário Verde Forense (#4EDEA3 -> B=163, G=222, R=78, A=255)
                pixel_data.extend((163, 222, 78, 255))
            elif dist <= 2.4:
                # Núcleo central brilhante Ciano
                pixel_data.extend((255, 250, 120, 255))
            elif abs(dx - dy) < 1.1 and dx > 0 and dy < 0:
                # Feixe de varredura do radar (45 graus)
                pixel_data.extend((163, 222, 78, 255))
            else:
                # Fundo escuro Cyber (#0C0E14 -> B=20, G=14, R=12, A=255)
                pixel_data.extend((20, 14, 12, 255))

    # Máscara AND (1 bit por pixel, alinhada a 32 bits = 4 bytes por linha * 32 linhas = 128 bytes)
    and_mask = b"\x00" * (4 * height)

    # BITMAPINFOHEADER (40 bytes) — no ICO a altura declarada no header é height * 2 (XOR + AND)
    bmp_header = struct.pack(
        "<IiiHHIIiiII",
        40,                         # biSize
        width,                      # biWidth
        height * 2,                 # biHeight (XOR + AND mask)
        1,                          # biPlanes
        32,                         # biBitCount (32-bit BGRA)
        0,                          # biCompression (BI_RGB)
        len(pixel_data) + len(and_mask),
        0, 0, 0, 0
    )

    image_bytes = bmp_header + bytes(pixel_data) + and_mask

    # ICONDIR (6 bytes) + ICONDIRENTRY (16 bytes) = 22 bytes
    icondir = struct.pack("<HHH", 0, 1, 1)  # Reserved=0, Type=1 (ICO), Count=1
    icondirentry = struct.pack(
        "<BBBBHHII",
        width,                      # bWidth
        height,                     # bHeight
        0,                          # bColorCount
        0,                          # bReserved
        1,                          # wPlanes
        32,                         # wBitCount
        len(image_bytes),           # dwBytesInRes
        22,                         # dwImageOffset (6 + 16)
    )

    with open(dest_path, "wb") as f:
        f.write(icondir + icondirentry + image_bytes)

    return dest_path


# ==============================================================================
# 4. INSPEÇÃO DE INSTALAÇÃO EXISTENTE & INTEGRIDADE DE MANIFESTO
# ==============================================================================

def _sha256_file(filepath: str) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def get_installed_info(custom_install_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Inspeciona se já existe uma versão do Geio DiskRadar instalada no diretório canônico
    (ou custom_install_dir) e consulta o Registro do Windows quando aplicável.
    """
    target_dir = custom_install_dir or get_canonical_install_dir()
    v_file = os.path.join(target_dir, "version.json")
    m_file = os.path.join(target_dir, "install_manifest.json")
    main_py = os.path.join(target_dir, "main.py")

    is_installed = os.path.isdir(target_dir) and (os.path.isfile(v_file) or os.path.isfile(main_py))
    installed_version: Optional[str] = None
    installed_at: Optional[str] = None
    manifest_files_count = 0
    registry_registered = False

    if is_installed:
        if os.path.isfile(v_file):
            try:
                with open(v_file, "r", encoding="utf-8") as f:
                    v_data = json.load(f)
                    installed_version = str(v_data.get("version") or "").strip().lstrip("vV")
            except Exception:
                pass
        if os.path.isfile(m_file):
            try:
                with open(m_file, "r", encoding="utf-8") as f:
                    m_data = json.load(f)
                    if not installed_version:
                        installed_version = str(m_data.get("version") or "").strip().lstrip("vV")
                    installed_at = m_data.get("installed_at_utc")
                    manifest_files_count = len(m_data.get("files") or {})
            except Exception:
                pass

    # Verifica Registro do Windows se em win32 e usando o diretório padrão
    if sys.platform == "win32" and custom_install_dir is None:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, UNINSTALL_REG_KEY, 0, winreg.KEY_READ) as key:
                reg_ver, _ = winreg.QueryValueEx(key, "DisplayVersion")
                registry_registered = True
                if not installed_version and reg_ver:
                    installed_version = str(reg_ver).strip().lstrip("vV")
        except Exception:
            pass

    current_running_root = os.path.normcase(os.path.abspath(get_project_root()))
    canonical_norm = os.path.normcase(os.path.abspath(target_dir))
    is_running_from_canonical = (current_running_root == canonical_norm)

    return {
        "is_installed": is_installed and bool(installed_version),
        "installed_version": installed_version,
        "installed_at_utc": installed_at,
        "install_dir": target_dir,
        "manifest_files_count": manifest_files_count,
        "registry_registered": registry_registered,
        "is_running_from_canonical": is_running_from_canonical,
        "running_version": load_version_json().get("version", DEFAULT_VERSION),
        "running_dir": get_project_root(),
    }


# ==============================================================================
# 5. REGISTRO NO WINDOWS E CRIAÇÃO DE ATALHO ÚNICO (SEM DUPLICATAS)
# ==============================================================================

def _register_windows_uninstall(install_dir: str, version_str: str, ico_path: str) -> bool:
    """
    Registra ou atualiza a entrada ÚNICA do Geio DiskRadar em
    HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{APP_GUID}.
    Nunca cria entradas duplicadas: sobrescreve a chave do mesmo GUID.
    """
    if sys.platform != "win32":
        return False
    try:
        import winreg
        uninstall_bat = os.path.join(install_dir, "Desinstalar_DiskRadar.bat")
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, UNINSTALL_REG_KEY) as key:
            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, APP_NAME)
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, version_str.lstrip("vV"))
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, PUBLISHER)
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, install_dir)
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, ico_path)
            winreg.SetValueEx(key, "UninstallString", 0, winreg.REG_SZ, f'cmd.exe /c "{uninstall_bat}"')
            winreg.SetValueEx(key, "NoModify", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(key, "NoRepair", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(
                key,
                "InstallDate",
                0,
                winreg.REG_SZ,
                datetime.datetime.now().strftime("%Y%m%d"),
            )
        return True
    except Exception:
        return False


def _remove_windows_uninstall_registry() -> bool:
    """Remove a chave Uninstall do Registro do Windows."""
    if sys.platform != "win32":
        return False
    try:
        import winreg
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, UNINSTALL_REG_KEY)
        return True
    except Exception:
        return False


def _cleanup_legacy_versioned_shortcuts(desktop_dir: str, start_menu_dir: str) -> List[str]:
    """
    Remove atalhos antigos que continham número de versão no nome (ex: 'DiskRadar v2.1.lnk',
    'Geio DiskRadar v2.2.0.lnk'), mantendo apenas o atalho canônico 'Geio DiskRadar.lnk'.
    """
    removed: List[str] = []
    for folder in (desktop_dir, start_menu_dir):
        if not folder or not os.path.isdir(folder):
            continue
        try:
            for fname in os.listdir(folder):
                low = fname.lower()
                if not low.endswith(".lnk"):
                    continue
                if ("diskradar" in low or "disk radar" in low) and fname != f"{APP_NAME}.lnk":
                    full_p = os.path.join(folder, fname)
                    try:
                        os.remove(full_p)
                        removed.append(full_p)
                    except Exception:
                        pass
        except Exception:
            pass
    return removed


def _create_windows_shortcuts(install_dir: str, ico_path: str) -> Dict[str, Any]:
    """
    Cria o atalho único 'Geio DiskRadar.lnk' na Área de Trabalho e no Menu Iniciar
    usando WScript.Shell via PowerShell nativo do Windows.
    """
    if sys.platform != "win32":
        return {"created": False, "reason": "Not running on win32"}

    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    appdata = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
    start_menu_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs")

    removed_legacy = _cleanup_legacy_versioned_shortcuts(desktop_dir, start_menu_dir)

    # Cria launcher VBS invisível para iniciar o DiskRadar sem janela preta de prompt
    vbs_launcher = os.path.join(install_dir, "Iniciar_Silencioso.vbs")
    bat_launcher = os.path.join(install_dir, "Executar_DiskRadar.bat")
    vbs_content = (
        'Set WshShell = CreateObject("WScript.Shell")\r\n'
        f'WshShell.CurrentDirectory = "{install_dir}"\r\n'
        f'WshShell.Run chr(34) & "{bat_launcher}" & chr(34), 0, False\r\n'
        'Set WshShell = Nothing\r\n'
    )
    try:
        with open(vbs_launcher, "w", encoding="utf-8") as f:
            f.write(vbs_content)
    except Exception:
        pass

    shortcuts_to_make = []
    if os.path.isdir(desktop_dir):
        shortcuts_to_make.append(os.path.join(desktop_dir, f"{APP_NAME}.lnk"))
    if os.path.isdir(start_menu_dir):
        shortcuts_to_make.append(os.path.join(start_menu_dir, f"{APP_NAME}.lnk"))

    created_paths: List[str] = []
    for lnk_path in shortcuts_to_make:
        ps_script = (
            "$ws = New-Object -ComObject WScript.Shell; "
            f"$s = $ws.CreateShortcut('{lnk_path}'); "
            f"$s.TargetPath = 'wscript.exe'; "
            f"$s.Arguments = '\"{vbs_launcher}\"'; "
            f"$s.WorkingDirectory = '{install_dir}'; "
            f"$s.IconLocation = '{ico_path},0'; "
            f"$s.Description = 'Geio DiskRadar — Triagem Forense & Recuperação 100% Read-Only'; "
            "$s.Save()"
        )
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=8,
            )
            if os.path.isfile(lnk_path):
                created_paths.append(lnk_path)
        except Exception:
            pass

    return {
        "created": len(created_paths) > 0,
        "shortcuts": created_paths,
        "removed_legacy_shortcuts": removed_legacy,
    }


# ==============================================================================
# 6. MOTOR TRANSACIONAL DE INSTALAÇÃO E UPGRADE IN-PLACE (SEM DUPLICATAS)
# ==============================================================================

def _collect_project_files(source_dir: str) -> List[str]:
    """Lista caminhos relativos de todos os arquivos do projeto que devem ser instalados."""
    rel_files: List[str] = []
    for root, dirs, files in os.walk(source_dir):
        # Filtra pastas ignoradas in-place
        dirs[:] = [d for d in dirs if d not in _IGNORED_DIRS and not d.startswith(".git")]
        for f in files:
            if f in _IGNORED_FILES or f.endswith((".pyc", ".pyo", ".pyd")):
                continue
            full_p = os.path.join(root, f)
            rel_p = os.path.relpath(full_p, source_dir)
            rel_files.append(rel_p)
    return sorted(rel_files)


def install_or_upgrade_local(
    source_dir: Optional[str] = None,
    target_dir: Optional[str] = None,
    force_downgrade: bool = False,
    create_shortcuts: bool = True,
) -> Dict[str, Any]:
    """
    Executa a instalação inicial ou atualização inteligente (In-Place Upgrade) do Geio DiskRadar:
    1. Verifica se já existe versão instalada em `target_dir`.
    2. Compara versão SemVer (`v_new` vs `v_old`):
       - Se `v_new < v_old` e `not force_downgrade`: bloqueia downgrade para evitar corrupção.
       - Se `v_new > v_old`: executa UPGRADE removendo arquivos obsoletos da versão antiga.
       - Se `v_new == v_old`: executa REPARO/ATUALIZAÇÃO mantendo instalação única.
    3. Grava `install_manifest.json` com hashes SHA-256 de todos os arquivos instalados.
    4. Atualiza Registro do Windows e atalho único na Área de Trabalho / Menu Iniciar.
    """
    src_root = os.path.abspath(source_dir or get_project_root())
    dst_root = os.path.abspath(target_dir or get_canonical_install_dir())

    src_ver_info = load_version_json(src_root)
    new_version = str(src_ver_info.get("version") or DEFAULT_VERSION).strip().lstrip("vV")

    # 1. Inspeciona instalação existente no destino
    existing = get_installed_info(custom_install_dir=dst_root)
    old_version = existing.get("installed_version")

    if existing["is_installed"] and old_version:
        cmp_res = compare_semver(new_version, old_version)
        if cmp_res < 0 and not force_downgrade:
            return {
                "ok": False,
                "action": "DOWNGRADE_BLOCKED",
                "previous_version": old_version,
                "new_version": new_version,
                "install_dir": dst_root,
                "error": (
                    f"Bloqueio de versão: Uma versão mais recente (v{old_version}) já está instalada em "
                    f"'{dst_root}'. Não é permitido instalar uma versão anterior (v{new_version}) por cima."
                ),
            }
        elif cmp_res > 0:
            action = "UPGRADE"
            action_label = f"Atualização de v{old_version} para v{new_version}"
        else:
            action = "REPAIR_REINSTALL"
            action_label = f"Reinstalação / Sincronização da versão v{new_version}"
    else:
        action = "FRESH_INSTALL"
        action_label = f"Instalação limpa da versão v{new_version}"

    os.makedirs(dst_root, exist_ok=True)

    # 2. Carrega manifesto antigo para identificar arquivos obsoletos que saíram de linha
    old_manifest_path = os.path.join(dst_root, "install_manifest.json")
    old_tracked_files: Set[str] = set()
    if os.path.isfile(old_manifest_path):
        try:
            with open(old_manifest_path, "r", encoding="utf-8") as f:
                old_m = json.load(f)
                old_tracked_files = set((old_m.get("files") or {}).keys())
        except Exception:
            pass

    # 3. Copia os arquivos novos se src_root != dst_root
    same_directory = (os.path.normcase(src_root) == os.path.normcase(dst_root))
    rel_files = _collect_project_files(src_root)
    new_tracked_hashes: Dict[str, str] = {}
    copied_count = 0

    for rel_p in rel_files:
        src_file = os.path.join(src_root, rel_p)
        dst_file = os.path.join(dst_root, rel_p)
        norm_rel = rel_p.replace("\\", "/")

        if not same_directory:
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            shutil.copy2(src_file, dst_file)
            copied_count += 1

        try:
            new_tracked_hashes[norm_rel] = _sha256_file(dst_file)
        except Exception:
            pass

    # 4. Gera ícone oficial .ico dentro da instalação antes de comparar obsoletos
    ico_rel = "ui/assets/diskradar.ico"
    ico_full = os.path.join(dst_root, "ui", "assets", "diskradar.ico")
    try:
        generate_cyber_radar_ico(ico_full)
        new_tracked_hashes[ico_rel] = _sha256_file(ico_full)
    except Exception:
        pass

    # 5. Remove cirurgicamente arquivos obsoletos que existiam na versão anterior mas não na nova
    removed_obsolete: List[str] = []
    if old_tracked_files and not same_directory:
        for old_rel in old_tracked_files:
            if old_rel not in new_tracked_hashes:
                obsolete_full = os.path.join(dst_root, old_rel.replace("/", os.sep))
                if os.path.isfile(obsolete_full):
                    try:
                        os.remove(obsolete_full)
                        removed_obsolete.append(old_rel)
                    except Exception:
                        pass

    # 6. Salva o novo install_manifest.json
    manifest_payload = {
        "app_id": APP_GUID,
        "app_name": APP_NAME,
        "version": new_version,
        "previous_version": old_version,
        "last_action": action,
        "installed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "install_dir": dst_root,
        "files_count": len(new_tracked_hashes),
        "removed_obsolete_files": removed_obsolete,
        "files": new_tracked_hashes,
    }
    with open(old_manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_payload, f, indent=2, ensure_ascii=False)

    # 7. Integração com Registro do Windows e Atalhos (somente quando instalado no Windows)
    reg_ok = False
    shortcut_info: Dict[str, Any] = {"created": False}
    if create_shortcuts and sys.platform == "win32":
        reg_ok = _register_windows_uninstall(dst_root, new_version, ico_full)
        shortcut_info = _create_windows_shortcuts(dst_root, ico_full)

    return {
        "ok": True,
        "action": action,
        "action_label": action_label,
        "previous_version": old_version,
        "new_version": new_version,
        "install_dir": dst_root,
        "files_installed": len(new_tracked_hashes),
        "removed_obsolete_count": len(removed_obsolete),
        "removed_obsolete_files": removed_obsolete,
        "registry_updated": reg_ok,
        "shortcuts": shortcut_info,
    }


def uninstall_canonical(custom_install_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Desinstala limpa e completamente a instalação canônica do Geio DiskRadar,
    removendo atalhos e registro, mas preservando a pasta Desktop\\Evidencias_DiskRadar.
    """
    target_dir = os.path.abspath(custom_install_dir or get_canonical_install_dir())
    removed_shortcuts: List[str] = []

    if sys.platform == "win32" and custom_install_dir is None:
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        appdata = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        start_menu_dir = os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs")
        for folder in (desktop_dir, start_menu_dir):
            lnk = os.path.join(folder, f"{APP_NAME}.lnk")
            if os.path.isfile(lnk):
                try:
                    os.remove(lnk)
                    removed_shortcuts.append(lnk)
                except Exception:
                    pass
        _cleanup_legacy_versioned_shortcuts(desktop_dir, start_menu_dir)
        _remove_windows_uninstall_registry()

    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir, ignore_errors=True)

    return {
        "ok": True,
        "uninstalled_dir": target_dir,
        "removed_shortcuts": removed_shortcuts,
    }


# ==============================================================================
# 7. AUTO-UPDATER OVER-THE-AIR (OTA) VIA GITHUB
# ==============================================================================

def check_github_update(timeout: float = 4.0) -> Dict[str, Any]:
    """
    Consulta o arquivo version.json no repositório oficial do GitHub e compara
    com a versão local em execução e com a versão instalada.
    """
    local_info = load_version_json()
    local_ver = str(local_info.get("version") or DEFAULT_VERSION).strip().lstrip("vV")
    raw_url = str(local_info.get("raw_version_url") or "https://raw.githubusercontent.com/6310/diskradar/main/version.json")

    try:
        req = urllib.request.Request(
            raw_url,
            headers={"User-Agent": f"GeioDiskRadar-Updater/{local_ver}"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            remote_data = json.loads(resp.read().decode("utf-8"))
        remote_ver = str(remote_data.get("version") or local_ver).strip().lstrip("vV")
        cmp_val = compare_semver(remote_ver, local_ver)
        return {
            "ok": True,
            "online": True,
            "local_version": local_ver,
            "remote_version": remote_ver,
            "release_date": remote_data.get("release_date", ""),
            "update_available": cmp_val > 0,
            "comparison": cmp_val,
            "message": (
                f"Nova versão v{remote_ver} disponível no GitHub!"
                if cmp_val > 0
                else f"Você já está na versão mais recente (v{local_ver})."
            ),
        }
    except Exception as exc:
        return {
            "ok": False,
            "online": False,
            "local_version": local_ver,
            "remote_version": None,
            "update_available": False,
            "message": f"Bancada offline ou sem acesso ao GitHub ({exc}). Use o instalador local.",
        }


def apply_github_ota_update(
    target_dir: Optional[str] = None,
    zip_url: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Baixa o pacote oficial da branch main do GitHub e aplica a atualização atômica
    na instalação canônica do sistema (e no diretório atual se aplicável).
    """
    local_info = load_version_json()
    download_url = zip_url or str(
        local_info.get("zip_download_url") or "https://github.com/6310/diskradar/archive/refs/heads/main.zip"
    )
    temp_dir = tempfile.mkdtemp(prefix="diskradar_ota_")
    try:
        zip_path = os.path.join(temp_dir, "update.zip")
        req = urllib.request.Request(
            download_url,
            headers={"User-Agent": "GeioDiskRadar-OTA-Updater"},
        )
        with urllib.request.urlopen(req, timeout=20) as resp, open(zip_path, "wb") as f_out:
            shutil.copyfileobj(resp, f_out)

        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(extract_dir)

        # Localiza a subpasta extraída que contém main.py
        extracted_root = extract_dir
        for item in os.listdir(extract_dir):
            cand = os.path.join(extract_dir, item)
            if os.path.isdir(cand) and os.path.isfile(os.path.join(cand, "main.py")):
                extracted_root = cand
                break

        res = install_or_upgrade_local(
            source_dir=extracted_root,
            target_dir=target_dir,
            force_downgrade=False,
            create_shortcuts=True,
        )
        return res
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Falha ao baixar/aplicar atualização OTA do GitHub: {exc}",
        }
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


# ==============================================================================
# 8. CLI PARA CHAMADA DIRETA PELOS SCRIPTS .BAT DO WINDOWS
# ==============================================================================

def _cli_main() -> int:
    parser = argparse.ArgumentParser(description="Instalador & Atualizador Canônico do Geio DiskRadar")
    parser.add_argument("--install", action="store_true", help="Instala ou atualiza na pasta canônica do sistema")
    parser.add_argument("--uninstall", action="store_true", help="Desinstala a versão canônica do sistema")
    parser.add_argument("--status", action="store_true", help="Exibe o status da instalação em JSON")
    parser.add_argument("--force", action="store_true", help="Força instalação mesmo se versão for anterior")
    parser.add_argument("--target-dir", type=str, default=None, help="Diretório alvo customizado")
    args = parser.parse_args()

    if args.status:
        info = get_installed_info(custom_install_dir=args.target_dir)
        print(json.dumps(info, indent=2, ensure_ascii=False))
        return 0

    if args.uninstall:
        print("=" * 74)
        print("  GEIO DISKRADAR // DESINSTALADOR DO SISTEMA")
        print("=" * 74)
        res = uninstall_canonical(custom_install_dir=args.target_dir)
        print(f"  [OK] Instalação removida de: {res['uninstalled_dir']}")
        print("  [OK] Atalhos e registro limpos com sucesso.")
        print("  [INFO] Suas evidências extraídas na Área de Trabalho foram preservadas.")
        print("=" * 74)
        return 0

    # Default ou --install
    print("=" * 74)
    print(f"  GEIO DISKRADAR // INSTALADOR & ATUALIZADOR INTELIGENTE ({get_app_version()})")
    print("=" * 74)
    existing = get_installed_info(custom_install_dir=args.target_dir)
    if existing["is_installed"]:
        print(f"  [*] Versão já instalada detectada: v{existing['installed_version']}")
        print(f"  [*] Diretório canônico existente : {existing['install_dir']}")
    else:
        print("  [*] Nenhuma instalação anterior detectada neste usuário.")
        print(f"  [*] Diretório canônico de destino: {existing['install_dir']}")

    res = install_or_upgrade_local(
        target_dir=args.target_dir,
        force_downgrade=args.force,
        create_shortcuts=(args.target_dir is None),
    )

    if not res["ok"]:
        print(f"\n  [ERRO / BLOQUEIO] {res.get('error')}")
        print("=" * 74)
        return 1

    print(f"\n  [SUCESSO] Operação realizada: {res['action_label']}")
    print(f"  [SUCESSO] Pasta Única Oficial: {res['install_dir']}")
    print(f"  [SUCESSO] Arquivos validados (SHA-256): {res['files_installed']}")
    if res["removed_obsolete_count"] > 0:
        print(f"  [LIMPEZA] {res['removed_obsolete_count']} arquivos obsoletos da versão antiga removidos.")
    if res.get("shortcuts", {}).get("created"):
        print("  [ATALHO] Atalho único 'Geio DiskRadar' atualizado na Área de Trabalho e Menu Iniciar!")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(_cli_main())
