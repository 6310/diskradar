#!/usr/bin/env python3
"""
Gerador automatizado de GIFs animados de alta qualidade para o README do Geio DiskRadar.
Utiliza Firefox Headless para capturar as telas da interface Stitch em tempo real
sobre o disco virtual forense e monta os GIFs animados em puro Python (sem Pillow/ImageMagick).
"""

import os
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zlib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from tests.emulation.mock_windows_env import patch_windows_environment
from tests.emulation.synthetic_disk_builder import build_synthetic_windows_disk
from ui.stitch_server import start_stitch_background_server


def lzw_compress(data: bytes, min_code_size: int = 8) -> bytes:
    """Comprime fluxo de bytes em blocos LZW válidos para GIF89a."""
    clear_code = 1 << min_code_size
    end_code = clear_code + 1
    code_size = min_code_size + 1
    next_code = end_code + 1
    max_code = 1 << code_size

    table = {bytes([i]): i for i in range(clear_code)}
    bits = []

    def emit(code, size):
        for i in range(size):
            bits.append((code >> i) & 1)

    emit(clear_code, code_size)
    prefix = b""
    for byte in data:
        pattern = prefix + bytes([byte])
        if pattern in table:
            prefix = pattern
        else:
            emit(table[prefix], code_size)
            if next_code < 4096:
                table[pattern] = next_code
                next_code += 1
                if next_code > max_code and code_size < 12:
                    code_size += 1
                    max_code = 1 << code_size
            else:
                emit(clear_code, code_size)
                table = {bytes([i]): i for i in range(clear_code)}
                code_size = min_code_size + 1
                max_code = 1 << code_size
                next_code = end_code + 1
            prefix = bytes([byte])
    if prefix:
        emit(table[prefix], code_size)
    emit(end_code, code_size)

    packed_bytes = bytearray()
    byte_val = 0
    bit_count = 0
    for b in bits:
        byte_val |= (b << bit_count)
        bit_count += 1
        if bit_count == 8:
            packed_bytes.append(byte_val)
            byte_val = 0
            bit_count = 0
    if bit_count > 0:
        packed_bytes.append(byte_val)

    out = bytearray()
    pos = 0
    while pos < len(packed_bytes):
        chunk = packed_bytes[pos:pos + 255]
        out.append(len(chunk))
        out.extend(chunk)
        pos += len(chunk)
    out.append(0)
    return bytes(out)


def build_global_palette() -> bytes:
    """Cria paleta global otimizada de 256 cores (cubo 6x6x6 + 16 tons de cinza forense + acentos ciano/verde)."""
    palette = bytearray()
    levels = [0, 51, 102, 153, 204, 255]
    for r in levels:
        for g in levels:
            for b in levels:
                palette.extend((r, g, b))
    for i in range(16):
        val = int(i * 255 / 15)
        palette.extend((val, val, val))
    while len(palette) < 768:
        palette.extend((0, 0, 0))
    return bytes(palette)


def rgb_to_palette_idx(r: int, g: int, b: int) -> int:
    """Mapeamento ultrarrápido O(1) de cor RGB para a paleta global."""
    if abs(r - g) < 10 and abs(g - b) < 10:
        gray = (r + g + b) // 3
        idx = int(gray * 15 / 255)
        return 216 + idx
    ri = (r * 5 + 127) // 255
    gi = (g * 5 + 127) // 255
    bi = (b * 5 + 127) // 255
    return ri * 36 + gi * 6 + bi


def decode_and_downscale_png(filepath: str, scale: int = 2):
    """Lê arquivo PNG decodificando scanlines e filtros nativos zlib e reduz resolução para scale."""
    with open(filepath, "rb") as f:
        data = f.read()
    pos = 8
    width = height = None
    idat = []
    while pos < len(data):
        length, ctype = struct.unpack(">I4s", data[pos:pos + 8])
        cdata = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if ctype == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", cdata[:10])
            bpp = 3 if color_type == 2 else 4
        elif ctype == b"IDAT":
            idat.append(cdata)
        elif ctype == b"IEND":
            break

    raw = zlib.decompress(b"".join(idat))
    stride = width * bpp
    recon = bytearray(width * height * bpp)

    def paeth(a, b, c):
        p = a + b - c
        pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
        if pa <= pb and pa <= pc:
            return a
        elif pb <= pc:
            return b
        else:
            return c

    src_offset = 0
    dst_offset = 0
    for y in range(height):
        ftype = raw[src_offset]
        src_offset += 1
        line = raw[src_offset:src_offset + stride]
        src_offset += stride
        prior_offset = dst_offset - stride
        for x in range(stride):
            val = line[x]
            left = recon[dst_offset + x - bpp] if x >= bpp else 0
            up = recon[prior_offset + x] if y > 0 else 0
            upleft = recon[prior_offset + x - bpp] if (y > 0 and x >= bpp) else 0

            if ftype == 0:
                recon[dst_offset + x] = val
            elif ftype == 1:
                recon[dst_offset + x] = (val + left) & 0xFF
            elif ftype == 2:
                recon[dst_offset + x] = (val + up) & 0xFF
            elif ftype == 3:
                recon[dst_offset + x] = (val + ((left + up) >> 1)) & 0xFF
            elif ftype == 4:
                recon[dst_offset + x] = (val + paeth(left, up, upleft)) & 0xFF
        dst_offset += stride

    out_w = width // scale
    out_h = height // scale
    indexed = bytearray(out_w * out_h)
    idx = 0
    for y in range(out_h):
        orig_y = y * scale
        row_start = orig_y * stride
        for x in range(out_w):
            orig_x = x * scale
            p_offset = row_start + orig_x * bpp
            r, g, b = recon[p_offset], recon[p_offset + 1], recon[p_offset + 2]
            indexed[idx] = rgb_to_palette_idx(r, g, b)
            idx += 1

    return out_w, out_h, bytes(indexed)


def create_animated_gif(frames, delays_cs, output_gif_path):
    """
    Empacota múltiplos frames indexados em um arquivo GIF89a com Netscape loop block.
    delays_cs: lista de inteiros representando delay em centésimos de segundo (100 = 1.0s).
    """
    assert len(frames) > 0
    w, h, _ = frames[0]
    pal = build_global_palette()

    gif = bytearray()
    gif.extend(b"GIF89a")
    gif.extend(struct.pack("<HH", w, h))
    gif.extend(bytes([0xF7, 0x00, 0x00]))  # 256 colors
    gif.extend(pal)
    # Netscape 2.0 loop block
    gif.extend(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")

    for i, (frame_w, frame_h, idx_pixels) in enumerate(frames):
        delay = delays_cs[i] if i < len(delays_cs) else 200
        lzw_data = lzw_compress(idx_pixels, 8)
        # Graphic Control Extension
        gif.extend(b"\x21\xF9\x04\x00" + struct.pack("<H", delay) + b"\x00\x00")
        # Image Descriptor
        gif.extend(b"\x2C" + struct.pack("<HHHH", 0, 0, frame_w, frame_h) + b"\x00")
        gif.append(8)  # Minimum code size
        gif.extend(lzw_data)

    gif.extend(b"\x3B")  # Trailer

    os.makedirs(os.path.dirname(os.path.abspath(output_gif_path)), exist_ok=True)
    with open(output_gif_path, "wb") as f:
        f.write(gif)

    size_kb = os.path.getsize(output_gif_path) / 1024
    print(f"  [OK] GIF gerado com sucesso: {output_gif_path} ({len(frames)} frames, {size_kb:.1f} KB)")


def main():
    print("=" * 74)
    print("  GEIO DISKRADAR // GERADOR AUTOMATIZADO DE GIFS PARA O README")
    print("=" * 74)

    temp_root = tempfile.mkdtemp(prefix="diskradar_win_disk_")
    build_synthetic_windows_disk(temp_root)
    temp_dir = tempfile.mkdtemp(prefix="diskradar_gifs_")

    firefox_bin = None
    for cand in ("/usr/bin/firefox", "/usr/bin/firefox-esr", "firefox", "firefox-esr"):
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            firefox_bin = cand
            break

    if not firefox_bin:
        print("[ERRO] Navegador Firefox headless não encontrado.")
        return 1

    with patch_windows_environment():
        url, controller, server = start_stitch_background_server()
        controller.select_target(temp_root)
        controller.start_scan()
        time.sleep(1.2)

        views = [
            ("01_pastas_quentes.png", f"{url}?tab=pastas-quentes"),
            ("02_arquivos_criticos.png", f"{url}?tab=arquivos-criticos"),
            ("03_linha_do_tempo.png", f"{url}?tab=linha-do-tempo"),
            ("04_apagados_rapidos.png", f"{url}?tab=apagados-rapidos"),
            ("05_hex_inspector.png", f"{url}?modal=modal-hex"),
        ]

        print("[1/3] Capturando telas com Firefox Headless (1440x900)...")
        png_paths = {}
        for name, view_url in views:
            dest_png = os.path.join(temp_dir, name)
            cmd = [
                firefox_bin,
                "--headless",
                f"--screenshot={dest_png}",
                "--window-size=1440,900",
                view_url,
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
            if os.path.isfile(dest_png):
                png_paths[name] = dest_png
                print(f"  - Captura salva: {name}")
            else:
                print(f"  [AVISO] Falha ao capturar {name}")

        server.shutdown()

    print("\n[2/3] Processando e decodificando frames PNG...")
    decoded_frames = {}
    for name, path in png_paths.items():
        w, h, idx_px = decode_and_downscale_png(path, scale=2)
        decoded_frames[name] = (w, h, idx_px)

    print("\n[3/3] Compilando GIFs animados em docs/img/...")
    docs_img_dir = os.path.join(BASE_DIR, "docs", "img")

    # GIF 1: Overview do Dashboard (Pastas Quentes -> Arquivos Críticos -> Linha do Tempo)
    overview_names = ["01_pastas_quentes.png", "02_arquivos_criticos.png", "03_linha_do_tempo.png"]
    overview_frames = [decoded_frames[n] for n in overview_names if n in decoded_frames]
    if overview_frames:
        gif1_path = os.path.join(docs_img_dir, "diskradar-overview.gif")
        create_animated_gif(overview_frames, [250, 250, 250], gif1_path)

    # GIF 2: Apagados Rápidos & Inspetor Hexadecimal
    forensic_names = ["04_apagados_rapidos.png", "05_hex_inspector.png"]
    forensic_frames = [decoded_frames[n] for n in forensic_names if n in decoded_frames]
    if forensic_frames:
        gif2_path = os.path.join(docs_img_dir, "diskradar-quick-deleted.gif")
        create_animated_gif(forensic_frames, [280, 280], gif2_path)

    shutil.rmtree(temp_dir, ignore_errors=True)
    shutil.rmtree(temp_root, ignore_errors=True)

    print("\n" + "=" * 74)
    print("  [CONCLUIDO] GIFs gerados e prontos para incorporacao no README.md!")
    print("=" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
