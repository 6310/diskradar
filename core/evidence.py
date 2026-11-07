"""
Módulo de Extração Segura de Evidências Forenses (1-Clique) do Geio DiskRadar v2.2.0.
Copia artefatos sensíveis (carteiras cripto, senhas, chaves, arquivos CAD) de forma
rigorosamente Read-Only na origem, calculando o Hash SHA-256 antes e depois da cópia
para validação matemática de integridade e geração da cadeia de custódia (.manifest.json).
"""

import datetime
import hashlib
import json
import os
import shutil
import sys
from typing import Any, Dict, Optional


def calculate_file_sha256(file_path: str, chunk_size: int = 65536) -> str:
    """Calcula o hash criptográfico SHA-256 de um arquivo em fatias controladas."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            hasher.update(chunk)
    return hasher.hexdigest()


def get_default_evidence_dir() -> str:
    """Retorna o diretório padrão para exportação de evidências (Desktop/Evidencias_DiskRadar)."""
    import tempfile
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    if not os.path.isdir(desktop):
        desktop = os.path.expanduser("~")
    target_dir = os.path.join(desktop, "Evidencias_DiskRadar")
    try:
        os.makedirs(target_dir, exist_ok=True)
        return target_dir
    except (OSError, PermissionError):
        fallback = os.path.join(tempfile.gettempdir(), "Evidencias_DiskRadar")
        os.makedirs(fallback, exist_ok=True)
        return fallback


def export_evidence_file(
    source_path: str,
    destination_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Exporta com segurança forense um arquivo sensível:
    1. Valida existência e permissão de leitura na origem.
    2. Calcula SHA-256 original (cadeia de custódia inicial).
    3. Copia o arquivo para a pasta de evidências preservando timestamp.
    4. Calcula SHA-256 do arquivo copiado e valida correspondência exata.
    5. Gera o arquivo de metadados de custódia (.manifest.json).
    """
    clean_src = os.path.normpath(source_path)
    if clean_src.startswith("\\\\?\\UNC\\"):
        clean_src = "\\\\" + clean_src[8:]
    elif clean_src.startswith("\\\\?\\"):
        clean_src = clean_src[4:]

    if not os.path.isfile(clean_src):
        return {
            "ok": False,
            "error": f"O arquivo de origem não existe ou é um diretório: {clean_src}",
        }

    try:
        # 1. Metadados de origem e cálculo do SHA-256 original
        st_src = os.stat(clean_src)
        src_size = st_src.st_size
        src_sha256 = calculate_file_sha256(clean_src)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Falha ao ler o arquivo de origem para cálculo de Hash: {exc}",
        }

    # 2. Prepara pasta de destino
    dest_dir = destination_dir or get_default_evidence_dir()
    try:
        os.makedirs(dest_dir, exist_ok=True)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Não foi possível criar o diretório de destino das evidências: {exc}",
        }

    # 3. Monta nome de destino com prefixo temporal para evitar colisões
    now_ts = datetime.datetime.now()
    time_prefix = now_ts.strftime("%Y%m%d_%H%M%S")
    base_name = os.path.basename(clean_src)
    dest_filename = f"{time_prefix}_{base_name}"
    dest_file_path = os.path.join(dest_dir, dest_filename)

    # 4. Copia binária segura em blocos (100% Read-Only na origem)
    try:
        with open(clean_src, "rb") as f_in, open(dest_file_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out, length=65536)
        # Preserva timestamps de modificação originais
        os.utime(dest_file_path, (st_src.st_atime, st_src.st_mtime))
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Falha durante a cópia segura do arquivo: {exc}",
        }

    # 5. Validação de Integridade Criptográfica (Hash matching)
    try:
        dest_sha256 = calculate_file_sha256(dest_file_path)
    except Exception as exc:
        return {
            "ok": False,
            "error": f"Falha ao validar Hash do arquivo copiado: {exc}",
        }

    is_verified = (src_sha256 == dest_sha256)
    if not is_verified:
        return {
            "ok": False,
            "error": "ALERTA FORENSE CRÍTICO: O Hash do arquivo copiado diverge do original!",
            "src_sha256": src_sha256,
            "dest_sha256": dest_sha256,
        }

    # 6. Criação do Arquivo de Manifesto de Custódia (.manifest.json)
    manifest_data = {
        "tool": "Geio DiskRadar v2.2.0",
        "evidence_type": "Digital Forensic Artifact Extraction",
        "extracted_at": now_ts.isoformat(),
        "custody_status": "VERIFIED_INTEGRITY_MATCH",
        "original_file": {
            "name": base_name,
            "source_path": clean_src,
            "size_bytes": src_size,
            "sha256": src_sha256,
            "original_mtime": datetime.datetime.fromtimestamp(st_src.st_mtime).isoformat() if st_src.st_mtime > 0 else "N/A",
        },
        "exported_file": {
            "destination_path": dest_file_path,
            "sha256": dest_sha256,
            "verified": True,
        },
    }

    manifest_path = f"{dest_file_path}.manifest.json"
    try:
        with open(manifest_path, "w", encoding="utf-8") as f_m:
            json.dump(manifest_data, f_m, indent=2, ensure_ascii=False)
    except Exception:
        pass  # Não bloqueia se o manifesto falhar

    return {
        "ok": True,
        "message": "Evidência extraída e validada com sucesso criptográfico!",
        "file_name": base_name,
        "source_path": clean_src,
        "dest_path": dest_file_path,
        "manifest_path": manifest_path,
        "sha256": src_sha256,
        "size_bytes": src_size,
        "destination_dir": dest_dir,
    }
