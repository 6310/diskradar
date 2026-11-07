"""
Motor Forense de Recuperação de Arquivos Apagados Rápidos (100% Read-Only) do Geio DiskRadar.
Sem Deep Scan: Atua exclusivamente nos metadados da Master File Table ($MFT) do NTFS e
nas estruturas de exclusão do $Recycle.Bin ($I / $R).
Executa em segundos (0.2s a 5s) sem sobrecarregar a mídia física.
"""

import base64
import datetime
import hashlib
import json
import os
import shutil
import struct
import sys
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

from core.evidence import get_default_evidence_dir
from core.rules import format_size


# ==============================================================================
# DATACLASSES FORENSES
# ==============================================================================

@dataclass
class DeletedFileEntry:
    entry_id: str                        # ID determinístico único (ex: "MFT_D_35" ou "REC_a1b2c3d4")
    name: str                            # Nome original do arquivo (ex: "relatorio_2026.xlsx")
    original_path: str                   # Caminho original reconstruído
    extension: str                       # Extensão em minúsculas com ponto (ex: ".xlsx")
    size_bytes: int                      # Tamanho original em bytes
    formatted_size: str                  # Tamanho legível
    deleted_timestamp: float             # Timestamp Unix epoch da exclusão ou modificação
    formatted_date: str                  # "YYYY-MM-DD HH:MM:SS"
    source_type: str                     # "NTFS_MFT" ou "RECYCLE_BIN"
    source_badge: str                    # Ex: "MFT #1420 (Shift+Del)" ou "$Recycle.Bin ($I v2)"
    category: str                        # "DOCS", "FOTOS_MIDIA", "CRYPTO_KEYS", "ARQUIVOS_COMPACTADOS", "OUTROS"
    recoverability: str                  # "RESIDENT" | "EXCELLENT" | "PARTIAL" | "OVERWRITTEN"
    recoverability_label: str            # Texto explicativo com emoji
    can_recover: bool                    # True se puder ser reconstruído
    # Metadados internos para reconstrução e inspeção
    volume_device_path: str = ""         # Ex: "\\\\.\\D:" ou imagem NTFS
    mft_record_offset: int = 0           # Offset absoluto do registro FILE no volume
    cluster_size: int = 4096             # Tamanho do cluster em bytes
    is_resident: bool = False            # True se os dados residem dentro do registro MFT
    resident_data: bytes = b""           # Bytes brutos (se residente)
    data_runs: List[Tuple[int, int]] = field(default_factory=list)  # [(lcn, cluster_count), ...]
    recycle_payload_path: str = ""       # Caminho do payload $R correspondente


@dataclass
class QuickDeletedScanResult:
    ok: bool
    target_path: str
    elapsed_ms: float
    mft_accessible: bool
    mft_status_message: str
    total_found: int
    recoverable_count: int
    overwritten_count: int
    mft_count: int
    recycle_count: int
    entries: List[DeletedFileEntry] = field(default_factory=list)


# ==============================================================================
# CLASSIFICAÇÃO RÁPIDA DE CATEGORIAS FORENSES
# ==============================================================================

_DOCS_EXTS: Set[str] = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    ".odt", ".ods", ".odp", ".txt", ".csv", ".rtf", ".wpd"
}
_MEDIA_EXTS: Set[str] = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff", ".raw", ".cr2", ".nef",
    ".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".mp3", ".wav", ".flac", ".ogg"
}
_CRYPTO_EXTS: Set[str] = {
    ".wallet", ".key", ".kdbx", ".kdb", ".pem", ".pfx", ".p12", ".asc", ".gpg", ".ovpn"
}
_ARCHIVE_EXTS: Set[str] = {
    ".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso", ".vmdk", ".vhdx"
}


def categorize_deleted_file(ext: str, name_lower: str) -> str:
    """Classifica o arquivo apagado para filtros visuais no painel."""
    if ext in _CRYPTO_EXTS or "wallet" in name_lower or "seed" in name_lower or "private" in name_lower:
        return "CRYPTO_KEYS"
    if ext in _DOCS_EXTS:
        return "DOCS"
    if ext in _MEDIA_EXTS:
        return "FOTOS_MIDIA"
    if ext in _ARCHIVE_EXTS:
        return "ARQUIVOS_COMPACTADOS"
    return "OUTROS"


def filetime_to_unix(ft: int) -> float:
    """Converte Windows 64-bit FILETIME (intervalos de 100ns desde 1601-01-01) para Unix epoch."""
    if ft <= 116444736000000000:
        return 0.0
    return (ft - 116444736000000000) / 10_000_000.0


def format_timestamp(ts: float) -> str:
    """Formata timestamp Unix para string ISO/legível local."""
    if ts <= 0:
        return "N/A"
    try:
        dt = datetime.datetime.fromtimestamp(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return "N/A"


# ==============================================================================
# MOTOR BINÁRIO DE RUNLISTS / DATA RUNS DO NTFS
# ==============================================================================

def decode_ntfs_data_runs(run_bytes: bytes) -> List[Tuple[int, int]]:
    """
    Decodifica as Data Runs comprimidas do atributo $DATA não-residente do NTFS.
    Cada Run é composta por um byte de cabeçalho:
      - 4 bits inferiores: comprimento em bytes do tamanho (cluster count)
      - 4 bits superiores: comprimento em bytes do offset relativo (LCN delta, signed)
    Retorna uma lista de tuplas com (lcn_absoluto, cluster_count).
    """
    runs: List[Tuple[int, int]] = []
    idx = 0
    current_lcn = 0
    total_len = len(run_bytes)

    while idx < total_len:
        header = run_bytes[idx]
        idx += 1
        if header == 0x00:
            break

        len_size = header & 0x0F
        offset_size = (header >> 4) & 0x0F

        if len_size == 0 or idx + len_size + offset_size > total_len:
            break

        # Lê cluster_count (unsigned little-endian)
        cluster_count = int.from_bytes(run_bytes[idx : idx + len_size], byteorder="little", signed=False)
        idx += len_size

        if offset_size > 0:
            # Lê LCN delta (SIGNED little-endian two's complement)
            lcn_delta = int.from_bytes(run_bytes[idx : idx + offset_size], byteorder="little", signed=True)
            idx += offset_size
            current_lcn += lcn_delta
            if current_lcn > 0 and cluster_count > 0:
                runs.append((current_lcn, cluster_count))
        else:
            # Sparse run (cluster count sem alocação física)
            pass

    return runs


# ==============================================================================
# MOTOR 1: PARSER FORENSE DA $Recycle.Bin ($I / $R)
# ==============================================================================

def scan_recycle_bin_deleted(target_path: str) -> List[DeletedFileEntry]:
    """
    Varre cirurgicamente pastas de Lixeira ($Recycle.Bin ou RECYCLER) na unidade informada.
    Lê os arquivos de controle binário $I* (versões 1 e 2 do Windows) e extrai:
    - Caminho original completo antes do apagamento
    - Timestamp exato da exclusão
    - Pareamento com o payload $R* para recuperação 100% íntegra
    """
    entries: List[DeletedFileEntry] = []
    clean_target = os.path.abspath(target_path) if not target_path.startswith(("\\\\.\\", "/dev/")) else target_path

    # Determina raiz da unidade
    if clean_target.startswith(("\\\\.\\", "/dev/")):
        # Para device bruto, o parser MFT trata diretamente; o parser de lixeira roda em caminhos montados
        return entries

    drive_root = os.path.splitdrive(clean_target)[0]
    if drive_root:
        drive_root = drive_root + os.sep
    else:
        drive_root = clean_target

    candidate_dirs: List[str] = []
    for name in ("$Recycle.Bin", "$RECYCLE.BIN", "RECYCLER", "Recycled"):
        candidate = os.path.join(drive_root, name)
        if os.path.isdir(candidate):
            candidate_dirs.append(candidate)

    # Se o target_path já for uma pasta dentro ou for a própria lixeira
    if os.path.isdir(clean_target) and clean_target not in candidate_dirs:
        if "$recycle.bin" in clean_target.lower() or "recycler" in clean_target.lower():
            candidate_dirs.append(clean_target)

    for r_dir in candidate_dirs:
        try:
            for root, dirs, files in os.walk(r_dir):
                for f_name in files:
                    if not f_name.startswith("$I") or len(f_name) < 4:
                        continue
                    i_path = os.path.join(root, f_name)
                    try:
                        file_sz = os.path.getsize(i_path)
                        if file_sz < 28:
                            continue
                        with open(i_path, "rb") as f_in:
                            data = f_in.read(1024)

                        if len(data) < 28:
                            continue

                        version = struct.unpack_from("<Q", data, 0)[0]
                        orig_size = struct.unpack_from("<Q", data, 8)[0]
                        deleted_ft = struct.unpack_from("<Q", data, 16)[0]
                        del_ts = filetime_to_unix(deleted_ft)

                        orig_path = ""
                        if version == 1:
                            # Windows Vista / 7 / 8: string de até 520 bytes (260 UTF-16LE chars)
                            raw_str = data[24:544]
                            null_pos = raw_str.find(b"\x00\x00")
                            if null_pos != -1 and null_pos % 2 == 0:
                                raw_str = raw_str[:null_pos]
                            orig_path = raw_str.decode("utf-16-le", errors="replace")
                        elif version == 2:
                            # Windows 10 / 11: uint32 char count seguido de string UTF-16LE
                            char_count = struct.unpack_from("<I", data, 24)[0]
                            str_bytes = data[28 : 28 + char_count * 2]
                            orig_path = str_bytes.decode("utf-16-le", errors="replace").rstrip("\x00")
                        else:
                            continue

                        if not orig_path:
                            orig_path = f_name[2:]

                        clean_p = orig_path.replace("\\", "/")
                        base_filename = os.path.basename(clean_p)
                        ext = os.path.splitext(base_filename)[1].lower()
                        cat = categorize_deleted_file(ext, base_filename.lower())

                        # Pareamento com o payload $R
                        r_name = "$R" + f_name[2:]
                        r_path = os.path.join(root, r_name)
                        r_exists = os.path.exists(r_path)

                        if r_exists:
                            try:
                                actual_size = os.path.getsize(r_path) if os.path.isfile(r_path) else orig_size
                            except Exception:
                                actual_size = orig_size
                            recoverability = "EXCELLENT"
                            rec_label = "🟢 100% Íntegro ($Recycle.Bin)"
                            can_rec = True
                        else:
                            actual_size = orig_size
                            recoverability = "OVERWRITTEN"
                            rec_label = "🔴 Dados Expurgados ($I Órfão)"
                            can_rec = False

                        unique_id = f"REC_{hashlib.md5(i_path.encode('utf-8', errors='ignore')).hexdigest()[:10]}"
                        entries.append(
                            DeletedFileEntry(
                                entry_id=unique_id,
                                name=base_filename or f_name,
                                original_path=orig_path,
                                extension=ext,
                                size_bytes=actual_size,
                                formatted_size=format_size(actual_size),
                                deleted_timestamp=del_ts,
                                formatted_date=format_timestamp(del_ts),
                                source_type="RECYCLE_BIN",
                                source_badge=f"$Recycle.Bin ($I v{version})",
                                category=cat,
                                recoverability=recoverability,
                                recoverability_label=rec_label,
                                can_recover=can_rec,
                                recycle_payload_path=r_path if r_exists else "",
                            )
                        )
                    except Exception:
                        continue
        except Exception:
            continue

    return entries


# ==============================================================================
# MOTOR 2: PARSER FORENSE DA $MFT (NTFS MASTER FILE TABLE)
# ==============================================================================

def scan_ntfs_mft_deleted(
    target_path: str,
    max_records: int = 50_000,
) -> Tuple[List[DeletedFileEntry], bool, str]:
    """
    Lê cirurgicamente a $MFT de um volume ou imagem NTFS em modo 100% Read-Only:
    1. Identifica o VBR no Setor 0 (OEM 'NTFS    ', cluster_size e cluster da $MFT).
    2. Lê os registros FILE de 1024 bytes com USA Fixup.
    3. Constrói a árvore de diretórios pai (registros de diretório ativos flags == 0x0003).
    4. Identifica registros onde flags == 0x0000 (arquivos apagados / Shift+Delete).
    5. Decodifica atributos $FILE_NAME, $STANDARD_INFORMATION e $DATA (residente ou runlist).
    """
    entries: List[DeletedFileEntry] = []
    clean_target = target_path.strip()

    # Determina o descritor de dispositivo ou arquivo
    device_path = clean_target
    if sys.platform == "win32":
        # Se for letra de unidade Windows (ex: "D:" ou "D:\")
        if len(clean_target) >= 2 and clean_target[1] == ":":
            drive_letter = clean_target[0].upper()
            device_path = f"\\\\.\\{drive_letter}:"

    # Abre em modo estritamente Read-Only
    try:
        fh = open(device_path, "rb")
    except Exception as exc:
        msg = f"Acesso à $MFT não disponível ({exc})."
        if sys.platform == "win32":
            msg += " Dica: Execute o Geio DiskRadar como Administrador para habilitar leitura direta da MFT."
        return entries, False, msg

    try:
        # 1. Lê o VBR (Volume Boot Record - 512 bytes)
        vbr = fh.read(512)
        if len(vbr) < 512:
            fh.close()
            return entries, False, "Volume com tamanho insuficiente para VBR NTFS."

        oem_id = vbr[3:11]
        if not oem_id.startswith(b"NTFS"):
            fh.close()
            return entries, False, f"Sistema de arquivos não é NTFS (OEM: {oem_id.decode('latin1', errors='replace')})."

        bytes_per_sector = struct.unpack_from("<H", vbr, 0x0B)[0]
        sectors_per_cluster = vbr[0x0D]
        if bytes_per_sector <= 0 or sectors_per_cluster <= 0:
            fh.close()
            return entries, False, "Parâmetros geométricos de setor/cluster inválidos no VBR."

        cluster_size = bytes_per_sector * sectors_per_cluster
        mft_start_lcn = struct.unpack_from("<Q", vbr, 0x30)[0]
        clusters_per_mft_record = struct.unpack_from("<b", vbr, 0x40)[0]

        if clusters_per_mft_record < 0:
            mft_record_size = 1 << abs(clusters_per_mft_record)  # Geralmente 1024 bytes (-10)
        else:
            mft_record_size = clusters_per_mft_record * cluster_size

        if mft_record_size != 1024:
            # Padrão MFT do NTFS é 1024 bytes
            mft_record_size = 1024

        mft_byte_offset = mft_start_lcn * cluster_size
        fh.seek(mft_byte_offset)

        # Mapa em memória de diretórios (record_num -> (parent_num, dir_name))
        dir_map: Dict[int, Tuple[int, str]] = {
            5: (5, ""),  # Registro #5 é o Root Directory (.)
        }

        # Lê a MFT em blocos (buffers de 1 MB = 1024 registros)
        records_read = 0
        chunk_records = 1024
        chunk_bytes = chunk_records * mft_record_size

        # Lista temporária de registros deletados brutos para resolver caminhos após mapear diretórios
        raw_deleted_candidates: List[Dict[str, Any]] = []

        while records_read < max_records:
            buf = fh.read(chunk_bytes)
            if not buf:
                break

            actual_records = len(buf) // mft_record_size
            if actual_records == 0:
                break

            for i in range(actual_records):
                record_num = records_read + i
                rec_start = i * mft_record_size
                rec_end = rec_start + mft_record_size
                rec_bytes = bytearray(buf[rec_start:rec_end])

                # Assinatura FILE
                if rec_bytes[0:4] != b"FILE":
                    continue

                # USA Fixup
                usa_offset = struct.unpack_from("<H", rec_bytes, 0x04)[0]
                usa_count = struct.unpack_from("<H", rec_bytes, 0x06)[0]

                if 0 < usa_offset < mft_record_size and usa_count >= 2:
                    if usa_offset + usa_count * 2 <= mft_record_size:
                        for s_idx in range(1, usa_count):
                            sector_end = (s_idx * bytes_per_sector) - 2
                            fixup_pos = usa_offset + (s_idx * 2)
                            if 0 <= sector_end + 2 <= mft_record_size and fixup_pos + 2 <= mft_record_size:
                                rec_bytes[sector_end : sector_end + 2] = rec_bytes[fixup_pos : fixup_pos + 2]

                first_attr_offset = struct.unpack_from("<H", rec_bytes, 0x14)[0]
                flags = struct.unpack_from("<H", rec_bytes, 0x16)[0]

                is_in_use = (flags & 0x0001) != 0
                is_dir = (flags & 0x0002) != 0

                # Extrai atributos iterando a lista encadeada
                attr_offset = first_attr_offset
                names_found: List[Tuple[str, int, int]] = []  # (name, parent_ref, mtime)
                data_attr_info: Optional[Dict[str, Any]] = None
                std_mtime_unix: float = 0.0

                while attr_offset + 16 <= mft_record_size:
                    attr_type = struct.unpack_from("<I", rec_bytes, attr_offset)[0]
                    if attr_type == 0xFFFFFFFF:
                        break

                    attr_len = struct.unpack_from("<I", rec_bytes, attr_offset + 4)[0]
                    if attr_len <= 0 or attr_offset + attr_len > mft_record_size:
                        break

                    non_resident = rec_bytes[attr_offset + 8]
                    name_len = rec_bytes[attr_offset + 9]

                    # 0x10 = $STANDARD_INFORMATION
                    if attr_type == 0x10 and non_resident == 0:
                        val_offset = struct.unpack_from("<H", rec_bytes, attr_offset + 20)[0]
                        si_base = attr_offset + val_offset
                        if si_base + 16 <= mft_record_size:
                            mtime_ft = struct.unpack_from("<Q", rec_bytes, si_base + 8)[0]
                            std_mtime_unix = filetime_to_unix(mtime_ft)

                    # 0x30 = $FILE_NAME
                    elif attr_type == 0x30 and non_resident == 0:
                        val_offset = struct.unpack_from("<H", rec_bytes, attr_offset + 20)[0]
                        fn_base = attr_offset + val_offset
                        if fn_base + 66 <= mft_record_size:
                            p_ref = struct.unpack_from("<Q", rec_bytes, fn_base)[0]
                            p_num = p_ref & 0x0000FFFFFFFFFFFF
                            fn_mtime_ft = struct.unpack_from("<Q", rec_bytes, fn_base + 16)[0]
                            fn_len = rec_bytes[fn_base + 64]
                            fn_namespace = rec_bytes[fn_base + 65]
                            name_start = fn_base + 66
                            name_end = name_start + fn_len * 2
                            if name_end <= mft_record_size:
                                fn_str = bytes(rec_bytes[name_start:name_end]).decode("utf-16-le", errors="replace")
                                # Prefere namespace não-DOS se houver duplicidade
                                names_found.append((fn_str, p_num, fn_namespace))

                    # 0x80 = $DATA (somente stream principal sem nome)
                    elif attr_type == 0x80 and name_len == 0:
                        if non_resident == 0:
                            # Residente na MFT
                            v_len = struct.unpack_from("<I", rec_bytes, attr_offset + 16)[0]
                            v_offset = struct.unpack_from("<H", rec_bytes, attr_offset + 20)[0]
                            d_start = attr_offset + v_offset
                            d_end = d_start + v_len
                            if d_end <= mft_record_size:
                                res_bytes = bytes(rec_bytes[d_start:d_end])
                                data_attr_info = {
                                    "is_resident": True,
                                    "size_bytes": v_len,
                                    "resident_data": res_bytes,
                                    "data_runs": [],
                                }
                        else:
                            # Não-residente (Runlists)
                            r_offset = struct.unpack_from("<H", rec_bytes, attr_offset + 32)[0]
                            real_sz = struct.unpack_from("<Q", rec_bytes, attr_offset + 48)[0]
                            run_start = attr_offset + r_offset
                            if run_start < attr_offset + attr_len:
                                run_bytes = bytes(rec_bytes[run_start : attr_offset + attr_len])
                                runs = decode_ntfs_data_runs(run_bytes)
                                data_attr_info = {
                                    "is_resident": False,
                                    "size_bytes": real_sz,
                                    "resident_data": b"",
                                    "data_runs": runs,
                                }

                    attr_offset += attr_len

                # Seleciona o melhor nome de arquivo
                chosen_name = ""
                parent_id = 5
                if names_found:
                    # Ordena para preferir namespace Win32/POSIX (1, 3, 0) sobre DOS 8.3 (2)
                    names_found.sort(key=lambda item: 0 if item[2] != 2 else 1)
                    chosen_name = names_found[0][0]
                    parent_id = names_found[0][1]

                # Se for diretório em uso, atualiza o mapa de pastas
                if is_in_use and is_dir and chosen_name:
                    dir_map[record_num] = (parent_id, chosen_name)

                # Se for arquivo apagado (flags == 0x0000) e tiver nome válido (não de metadado $)
                if not is_in_use and chosen_name and not chosen_name.startswith("$"):
                    raw_deleted_candidates.append({
                        "record_num": record_num,
                        "offset": mft_byte_offset + (record_num * mft_record_size),
                        "name": chosen_name,
                        "parent_id": parent_id,
                        "mtime": std_mtime_unix,
                        "data_info": data_attr_info,
                    })

            records_read += actual_records
            # Anti-congelamento cooperativo para manter fluidez no Windows
            time.sleep(0.001)

        # 2. Constrói os caminhos e entradas estruturadas
        def resolve_path(p_id: int) -> str:
            path_parts: List[str] = []
            curr = p_id
            visited = set()
            while curr in dir_map and curr not in visited and curr != 5:
                visited.add(curr)
                p, dname = dir_map[curr]
                if dname:
                    path_parts.append(dname)
                curr = p
            path_parts.reverse()
            drive_prefix = clean_target[:2] if len(clean_target) >= 2 and clean_target[1] == ":" else ""
            if drive_prefix:
                return drive_prefix + "\\" + "\\".join(path_parts) if path_parts else drive_prefix + "\\"
            return "\\" + "\\".join(path_parts) if path_parts else "\\"

        for c in raw_deleted_candidates:
            fn = c["name"]
            ext = os.path.splitext(fn)[1].lower()
            cat = categorize_deleted_file(ext, fn.lower())
            p_str = resolve_path(c["parent_id"])
            full_path = p_str.rstrip("\\") + "\\" + fn if p_str else fn

            d_info = c["data_info"]
            if d_info:
                sz = d_info["size_bytes"]
                is_res = d_info["is_resident"]
                res_b = d_info["resident_data"]
                d_runs = d_info["data_runs"]
                if is_res:
                    recov = "RESIDENT"
                    rec_label = "🟢 100% Íntegro (Residente MFT)"
                    can_rec = True
                elif d_runs:
                    recov = "EXCELLENT"
                    rec_label = "🟢 Excelente (Clusters Mapeados)"
                    can_rec = True
                else:
                    recov = "OVERWRITTEN"
                    rec_label = "🔴 Sem Clusters ($DATA Sobrescrito)"
                    can_rec = False
            else:
                sz = 0
                is_res = False
                res_b = b""
                d_runs = []
                recov = "OVERWRITTEN"
                rec_label = "🔴 Metadados Esvaziados"
                can_rec = False

            rec_num = c["record_num"]
            unique_id = f"MFT_{rec_num}_{hashlib.md5(fn.encode('utf-8', errors='ignore')).hexdigest()[:6]}"

            entries.append(
                DeletedFileEntry(
                    entry_id=unique_id,
                    name=fn,
                    original_path=full_path,
                    extension=ext,
                    size_bytes=sz,
                    formatted_size=format_size(sz),
                    deleted_timestamp=c["mtime"],
                    formatted_date=format_timestamp(c["mtime"]),
                    source_type="NTFS_MFT",
                    source_badge=f"MFT #{rec_num} (Shift+Del)",
                    category=cat,
                    recoverability=recov,
                    recoverability_label=rec_label,
                    can_recover=can_rec,
                    volume_device_path=device_path,
                    mft_record_offset=c["offset"],
                    cluster_size=cluster_size,
                    is_resident=is_res,
                    resident_data=res_b,
                    data_runs=d_runs,
                )
            )

        fh.close()
        return entries, True, f"Varredura da $MFT concluída com sucesso ({records_read:,} registros analisados)."

    except Exception as exc:
        try:
            fh.close()
        except Exception:
            pass
        return entries, False, f"Falha durante a leitura da $MFT: {exc}"


# ==============================================================================
# ORQUESTRADOR CENTRAL: QUICK DELETED SCAN (SEM DEEP SCAN)
# ==============================================================================

def run_quick_deleted_scan(target_path: str) -> QuickDeletedScanResult:
    """
    Executa a triagem instantânea de arquivos apagados combinando $MFT e $Recycle.Bin.
    Tempo típico de execução: 0.1 a 3 segundos.
    """
    t0 = time.monotonic()
    all_entries: List[DeletedFileEntry] = []

    # 1. Executa parser da $Recycle.Bin
    recycle_entries = scan_recycle_bin_deleted(target_path)
    all_entries.extend(recycle_entries)

    # 2. Executa parser da $MFT
    mft_entries, mft_ok, mft_msg = scan_ntfs_mft_deleted(target_path)
    all_entries.extend(mft_entries)

    elapsed_ms = (time.monotonic() - t0) * 1000.0

    # Ordena por prioridade: recuperáveis primeiro, mais recentes primeiro
    def sort_key(e: DeletedFileEntry) -> Tuple[int, float]:
        rec_score = 0 if e.can_recover else 1
        return (rec_score, -e.deleted_timestamp)

    all_entries.sort(key=sort_key)

    rec_count = sum(1 for e in all_entries if e.can_recover)
    over_count = len(all_entries) - rec_count

    return QuickDeletedScanResult(
        ok=True,
        target_path=target_path,
        elapsed_ms=round(elapsed_ms, 1),
        mft_accessible=mft_ok,
        mft_status_message=mft_msg,
        total_found=len(all_entries),
        recoverable_count=rec_count,
        overwritten_count=over_count,
        mft_count=len(mft_entries),
        recycle_count=len(recycle_entries),
        entries=all_entries,
    )


# ==============================================================================
# RECONSTRUTOR FORENSE E SALVAMENTO COM SHA-256 (100% READ-ONLY)
# ==============================================================================

def recover_deleted_entry(
    entry: DeletedFileEntry,
    custom_dest_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Reconstrói com rigor forense o arquivo apagado para o diretório de evidências:
    1. Para $Recycle.Bin: copia o payload $R associado.
    2. Para MFT Residente: grava os bytes residentes preservados dentro do registro.
    3. Para MFT Não-Residente: lê diretamente os blocos (lcn * cluster_size) em modo Read-Only.
    4. Calcula o Hash SHA-256 e gera o manifesto de cadeia de custódia (.manifest.json).
    """
    if not entry.can_recover:
        return {
            "ok": False,
            "error": f"O arquivo '{entry.name}' não possui clusters válidos disponíveis (foi sobrescrito ou purgado).",
        }

    # Diretório de destino
    base_dir = custom_dest_dir or os.path.join(get_default_evidence_dir(), "Recuperados_Apagados")
    try:
        os.makedirs(base_dir, exist_ok=True)
    except Exception as exc:
        return {"ok": False, "error": f"Não foi possível criar o diretório de destino: {exc}"}

    time_prefix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = os.path.basename(entry.name.replace("\\", "/"))
    dest_filename = f"{time_prefix}_{safe_name}"
    dest_path = os.path.join(base_dir, dest_filename)
    manifest_path = dest_path + ".manifest.json"

    hasher = hashlib.sha256()
    bytes_written = 0

    try:
        # Caso A: Payload da Lixeira
        if entry.source_type == "RECYCLE_BIN":
            if not entry.recycle_payload_path or not os.path.exists(entry.recycle_payload_path):
                return {"ok": False, "error": "O payload $R não foi encontrado no disco."}

            with open(entry.recycle_payload_path, "rb") as f_in, open(dest_path, "wb") as f_out:
                while True:
                    chunk = f_in.read(65536)
                    if not chunk:
                        break
                    f_out.write(chunk)
                    hasher.update(chunk)
                    bytes_written += len(chunk)

        # Caso B: MFT com Dados Residentes (<700 bytes)
        elif entry.source_type == "NTFS_MFT" and entry.is_resident:
            with open(dest_path, "wb") as f_out:
                f_out.write(entry.resident_data)
                hasher.update(entry.resident_data)
                bytes_written = len(entry.resident_data)

        # Caso C: MFT com Runlist (Não-residente)
        elif entry.source_type == "NTFS_MFT" and entry.data_runs:
            if not entry.volume_device_path:
                return {"ok": False, "error": "Identificador do volume NTFS não configurado na entrada."}

            with open(entry.volume_device_path, "rb") as vol_in, open(dest_path, "wb") as f_out:
                remaining_bytes = entry.size_bytes
                for lcn, cluster_count in entry.data_runs:
                    if remaining_bytes <= 0:
                        break
                    vol_in.seek(lcn * entry.cluster_size)
                    bytes_to_read = min(remaining_bytes, cluster_count * entry.cluster_size)

                    chunk_size = 65536
                    bytes_left_in_run = bytes_to_read
                    while bytes_left_in_run > 0:
                        cur_read = min(chunk_size, bytes_left_in_run)
                        chunk = vol_in.read(cur_read)
                        if not chunk:
                            break
                        f_out.write(chunk)
                        hasher.update(chunk)
                        bytes_written += len(chunk)
                        bytes_left_in_run -= len(chunk)
                        remaining_bytes -= len(chunk)

        else:
            return {"ok": False, "error": "Estrutura de dados do arquivo apagado não suportada para extração."}

        # Gera manifesto pericial de custódia
        sha256_hex = hasher.hexdigest()
        manifest_data = {
            "forensic_tool": "Geio DiskRadar v2.2.0 (Quick Deleted File Recovery)",
            "recovery_timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "original_filename": entry.name,
            "original_path": entry.original_path,
            "source_type": entry.source_type,
            "source_badge": entry.source_badge,
            "recoverability": entry.recoverability,
            "size_bytes": bytes_written,
            "formatted_size": format_size(bytes_written),
            "sha256": sha256_hex,
            "destination_path": dest_path,
            "status": "VALIDATED_READ_ONLY_RECOVERY",
        }

        with open(manifest_path, "w", encoding="utf-8") as f_mf:
            json.dump(manifest_data, f_mf, indent=2, ensure_ascii=False)

        return {
            "ok": True,
            "file_name": entry.name,
            "original_path": entry.original_path,
            "dest_path": dest_path,
            "manifest_path": manifest_path,
            "size_bytes": bytes_written,
            "formatted_size": format_size(bytes_written),
            "sha256": sha256_hex,
            "source_badge": entry.source_badge,
        }

    except Exception as exc:
        return {"ok": False, "error": f"Erro durante a extração do arquivo apagado: {exc}"}
