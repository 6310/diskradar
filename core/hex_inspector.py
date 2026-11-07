"""
Módulo de Inspeção Hexadecimal e Assinaturas Mágicas 100% Read-Only do Geio DiskRadar.
Lê exclusivamente fatias controladas de bytes (ex: 512 bytes por página) de arquivos no disco
sem jamais alterar conteúdo ou metadados, calculando:
- Matriz Hexadecimal (Offset, 16 bytes Hex 8+8, ASCII printável)
- Entropia de Shannon (0.00 a 8.00 bits/byte)
- Identificação de Magic Numbers (Assinaturas Forenses)
- Intérprete de tipos primitivos (uint8, uint16 LE, uint32 LE)
- Hash SHA-256 parcial de cabeçalho (64 KB) para cadeia de custódia rápida
"""

import hashlib
import math
import os
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional


MAGIC_SIGNATURES: List[tuple[bytes, str, str]] = [
    (b"SQLite format 3\x00", "SQLite 3 Database (0x53514C69)", "Estrutura de banco SQLite (Senhas/Histórico/Mensagens)"),
    (b"PK\x03\x04", "ZIP / Office OpenXML (PK\\x03\\x04)", "Container compactado ZIP ou documento Office (.docx/.xlsx)"),
    (b"%PDF-", "Adobe PDF Document (%PDF)", "Documento portátil PDF válido"),
    (b"\x89PNG\r\n\x1a\n", "PNG Image (\\x89PNG)", "Imagem rasterizada PNG íntegra"),
    (b"\xff\xd8\xff", "JPEG / EXIF Image (\\xFF\\xD8\\xFF)", "Fotografia JPEG / EXIF"),
    (b"Rar!\x1a\x07", "RAR Archive (Rar!)", "Arquivo compactado WinRAR"),
    (b"7z\xbc\xaf\x27\x1c", "7-Zip Archive (7z)", "Arquivo compactado 7-Zip"),
    (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1", "OLE2 Compound Document (DOC/XLS/MSG)", "Documento Microsoft Office legado"),
    (b"!BDN", "Microsoft Outlook PST/OST (!BDN)", "Base de e-mails Outlook Personal Folders"),
    (b"\x03\xd9\xa2\x9a\x67\xfb\x4b\xb5", "KeePass KDBX Password Vault", "Cofre de senhas criptografado KeePass"),
    (b"-----BEGIN ", "PEM Cryptographic Key / Certificate", "Chave privada ou certificado PEM ASCII"),
    (b"AC10", "AutoCAD DWG Drawing (AC10xx)", "Projeto de engenharia AutoCAD DWG"),
    (b"8BPS", "Adobe Photoshop PSD (8BPS)", "Projeto gráfico nativo Photoshop"),
    (b"MZ", "Windows PE Executable / DLL (MZ)", "Binário executável portátil Windows"),
]


@dataclass(slots=True)
class HexRow:
    """Representa uma linha de 16 bytes no visualizador Hexadecimal."""
    offset_int: int
    offset_hex: str
    hex_bytes: List[str]
    ascii_str: str
    has_read_error: bool = False


@dataclass(slots=True)
class HexInspectionResult:
    """Resultado completo da inspeção Read-Only de um bloco/setor de arquivo."""
    file_path: str
    file_size: int
    offset: int
    length: int
    bytes_read: int
    rows: List[HexRow] = field(default_factory=list)
    entropy: float = 0.0
    entropy_label: str = "Baixa densidade"
    magic_signature: str = "Binário / Texto Genérico"
    magic_details: str = "Assinatura específica não catalogada no offset 0"
    partial_sha256: str = "N/A"
    primitives: Dict[str, str] = field(default_factory=dict)
    error_message: Optional[str] = None
    c_array_snippet: str = ""
    python_bytes_snippet: str = ""
    raw_text_dump: str = ""


def calculate_shannon_entropy(data: bytes) -> float:
    """Calcula a entropia de Shannon (0.0 a 8.0 bits por byte) de um buffer."""
    if not data:
        return 0.0
    length = len(data)
    counts = [0] * 256
    for b in data:
        counts[b] += 1

    entropy = 0.0
    for c in counts:
        if c > 0:
            p = c / length
            entropy -= p * math.log2(p)
    return round(entropy, 2)


def detect_magic_signature(header_bytes: bytes) -> tuple[str, str]:
    """Identifica a assinatura mágica (Magic Number) a partir dos primeiros bytes."""
    if not header_bytes:
        return ("Arquivo Vazio (0 bytes)", "Nenhum byte disponível para análise de cabeçalho")

    for magic, name, desc in MAGIC_SIGNATURES:
        if header_bytes.startswith(magic):
            return (name, desc)

    # Berkeley DB (usado em wallet.dat do Bitcoin Core, geralmente tem 0x00061561 no offset 12)
    if len(header_bytes) >= 16 and header_bytes[12:16] in (b"\x61\x15\x06\x00", b"\x00\x06\x15\x61"):
        return ("Berkeley DB 4.x (Bitcoin Core wallet.dat)", "Assinatura Btree 0x00061561 no offset +12")

    # Verifica se é texto UTF-8 / ASCII legível
    printable = sum(1 for b in header_bytes[:128] if 32 <= b <= 126 or b in (9, 10, 13))
    if len(header_bytes[:128]) > 0 and (printable / len(header_bytes[:128])) >= 0.85:
        return ("Texto ASCII / UTF-8 Legível", "Fluxo textual estruturado sem cabeçalho binário proprietário")

    return (
        f"Fluxo Binário (0x{header_bytes[:4].hex().upper()})",
        "Estrutura binária de dados ou bloco intermediário",
    )


def inspect_file_sector(
    file_path: str,
    offset: int = 0,
    length: int = 512,
) -> HexInspectionResult:
    """
    Lê em modo estritamente Read-Only (`rb`) uma fatia de `length` bytes a partir de `offset`
    e retorna os dados estruturados para o Modal Hex Viewer.
    """
    clean_path = os.path.abspath(file_path)
    offset = max(0, int(offset))
    length = max(16, min(int(length), 4096))

    result = HexInspectionResult(
        file_path=clean_path,
        file_size=0,
        offset=offset,
        length=length,
        bytes_read=0,
    )

    if not os.path.exists(clean_path):
        result.error_message = "Arquivo ou caminho não encontrado no disco."
        return result

    if os.path.isdir(clean_path):
        # Se for um diretório (ex: Lote XML ou pasta de perfil), tenta inspecionar o primeiro arquivo dentro dele
        try:
            with os.scandir(clean_path) as it:
                for entry in it:
                    if entry.is_file(follow_symlinks=False):
                        clean_path = entry.path
                        result.file_path = clean_path
                        break
        except OSError as exc:
            result.error_message = f"Não foi possível inspecionar diretório: {exc}"
            return result

        if os.path.isdir(clean_path):
            result.error_message = "O caminho selecionado é um diretório sem arquivos diretos para leitura Hex."
            return result

    try:
        st = os.stat(clean_path)
        result.file_size = st.st_size
    except OSError as exc:
        result.error_message = f"Erro ao ler metadados (stat): {exc}"
        return result

    try:
        with open(clean_path, "rb") as f:
            # 1. Lê os primeiros 64 KB para hash SHA-256 rápido e detecção de Magic Number no offset 0
            header_chunk = f.read(65536)
            if header_chunk:
                result.partial_sha256 = hashlib.sha256(header_chunk).hexdigest()
                sig_name, sig_desc = detect_magic_signature(header_chunk[:64])
                result.magic_signature = sig_name
                result.magic_details = sig_desc

            # 2. Posiciona no offset solicitado
            if offset >= result.file_size and result.file_size > 0:
                offset = max(0, ((result.file_size - 1) // 512) * 512)
                result.offset = offset

            f.seek(offset)
            data = f.read(length)
    except OSError as exc:
        result.error_message = f"FALHA DE LEITURA I/O (Possível Bad Block / Permissão): {exc}"
        # Gera linhas sinalizadas com erro de leitura para visualização forense
        for row_idx in range(0, min(length, 256), 16):
            abs_off = offset + row_idx
            result.rows.append(
                HexRow(
                    offset_int=abs_off,
                    offset_hex=f"{abs_off:08X}",
                    hex_bytes=["??"] * 16,
                    ascii_str="[CRC_READ_FAIL!]",
                    has_read_error=True,
                )
            )
        return result

    result.bytes_read = len(data)
    result.entropy = calculate_shannon_entropy(data)
    if result.entropy >= 7.2:
        result.entropy_label = "Alta entropia (Dados comprimidos, ZIP/ mídia ou criptografia)"
    elif result.entropy >= 4.5:
        result.entropy_label = "Média densidade (Código estruturado, banco de dados ou documento)"
    else:
        result.entropy_label = "Baixa entropia (Texto plano, tabelas esparsas ou padding zero)"

    # Decodifica tipos primitivos nos primeiros bytes do bloco atual
    if len(data) >= 1:
        u8 = data[0]
        result.primitives["uint8"] = f"{u8} (0x{u8:02X})"
    else:
        result.primitives["uint8"] = "N/A"

    if len(data) >= 2:
        u16 = struct.unpack("<H", data[:2])[0]
        result.primitives["uint16_le"] = f"{u16:,} (0x{u16:04X})"
    else:
        result.primitives["uint16_le"] = "N/A"

    if len(data) >= 4:
        u32 = struct.unpack("<I", data[:4])[0]
        result.primitives["uint32_le"] = f"{u32:,} (0x{u32:08X})"
    else:
        result.primitives["uint32_le"] = "N/A"

    # Monta as linhas de 16 bytes
    raw_lines: List[str] = []
    for i in range(0, len(data), 16):
        chunk = data[i : i + 16]
        abs_off = offset + i
        off_hex = f"{abs_off:08X}"
        hex_list = [f"{b:02X}" for b in chunk]
        if len(hex_list) < 16:
            hex_list.extend(["  "] * (16 - len(hex_list)))

        ascii_chars = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        result.rows.append(
            HexRow(
                offset_int=abs_off,
                offset_hex=off_hex,
                hex_bytes=hex_list,
                ascii_str=ascii_chars,
                has_read_error=False,
            )
        )
        left_hex = " ".join(hex_list[:8])
        right_hex = " ".join(hex_list[8:])
        raw_lines.append(f"{off_hex}  {left_hex} | {right_hex}  {ascii_chars}")

    result.raw_text_dump = "\n".join(raw_lines)
    sample_c = ", ".join(f"0x{b:02X}" for b in data[:64])
    result.c_array_snippet = f"unsigned char sector_dump[{len(data)}] = {{ {sample_c} }};"
    result.python_bytes_snippet = repr(data[:64])

    return result
