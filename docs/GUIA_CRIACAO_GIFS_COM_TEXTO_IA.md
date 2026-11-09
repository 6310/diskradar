# Guia de Engenharia: Geração de GIFs de Demonstração com Título Sobreposto para READMEs

> **Destinatário:** Assistentes de IA, Desenvolvedores e Engenheiros de Software.  
> **Objetivo:** Transformar capturas de tela (screenshots/prints estáticos) em GIFs animados de alta fidelidade técnica, com banners HUD cyber-forenses em linha única e cadência confortável (1.5s por quadro), sem estourar memória em ambientes restritos (VMs) e imune ao cache agressivo do GitHub.

---

## 1. Visão Geral da Arquitetura

O pipeline foi projetado para transformar imagens estáticas (`.png` ou `.jpg`) em um arquivo GIF89a otimizado para a web.

```
+---------------------------+
| Capturas de Tela Brutas   | (Screenshots 1440x900 ou similar)
+-------------+-------------+
              |
              v
+---------------------------+
| Sobreposição HUD (Texto)  | (Injeção no DOM ou desenho via Pillow em Linha Única)
+-------------+-------------+
              |
              v
+---------------------------+
| Downscaling Antialiased   | (Box Filtering 2x2 para preservar traços e nitidez)
+-------------+-------------+
              |
              v
+---------------------------+
| Quantização de Cores      | (Paleta curada com cores da marca + cubo RGB)
+-------------+-------------+
              |
              v
+---------------------------+
| Compressão LZW & Loop     | (GIF89a com Netscape 2.0 Loop Block a 1.5s/quadro)
+-------------+-------------+
              |
              v
+---------------------------+
| Arquivo Showcase Final    | (Ex: docs/img/app-showcase-overview.gif)
+---------------------------+
```

---

## 2. Padrão Visual do Título HUD (Regra da Linha Única)

A identificação de cada tela **não pode quebrar em duas linhas** e precisa ter presença visual imponente sem cobrir botões essenciais da interface.

### Especificações Visuais Exatas

| Propriedade | Valor | Motivo / Efeito |
|---|---|---|
| **Posicionamento** | `fixed; bottom: 26px; left: 50%; transform: translateX(-50%)` | Centralizado na parte inferior (lower-third), longe dos menus superiores. |
| **Quebra de Linha** | `white-space: nowrap; display: inline-flex;` | **Obrigatório Linha Única.** Nunca permitir que o texto quebre verticalmente. |
| **Largura Máxima** | `max-width: 96vw; box-sizing: border-box;` | Garante margem de respiro nas laterais em qualquer resolução. |
| **Fundo** | `background: rgba(0, 18, 22, 0.98)` | Escuro profundo com leve transparência (destaca-se sobre temas claros ou escuros). |
| **Borda** | `border: 4px solid #00dbe9` | Ciano neon vibrante que define o container. |
| **Sombra / Brilho** | `box-shadow: 0 0 50px rgba(0,219,233,0.9), 0 20px 50px rgba(0,0,0,0.98)` | Efeito neon futurista com drop-shadow escuro para contraste. |
| **Indicador LED** | Esfera de 14px em `#4edea3` (verde esmeralda) com `box-shadow: 0 0 14px #4edea3` | LED de telemetria ativo à esquerda do texto. |
| **Título Principal** | Fonte Mono 38px, peso 900 (`font-weight: 900`), cor `#ffffff` | Texto principal em caixa alta, legível mesmo após redução de 50%. |
| **Separador** | Cor `#00dbe9`, peso 900, opacidade 80%: `//` | Divisor estético entre o módulo e a descrição. |
| **Subtítulo** | Fonte Mono 36px, peso 800, cor `#7df4ff` | Detalhe funcional da tela em ciano suave. |

---

## 3. Cadência e Timing das Telas

* **Tempo Ideal:** **1,5 segundos por quadro** (`delay = 150 centésimos de segundo` na Graphic Control Extension do GIF).
* **Por que 1,5s?**
  * Abaixo de 1,0s: Rápido demais para ler o título e absorver a tela.
  * Acima de 2,5s: Sensação estática e monótona de slideshow quebrado.
  * **1,5s:** O visitante lê o título com calma, percebe o layout e a transição ocorre de forma fluida e dinâmica.

---

## 4. Prevenção de Estouro de Memória (Crash de VM)

> [!CAUTION]
> **Nunca implemente descompactação LZW recursiva com listas de inteiros em Python.**  
> Criar dicionários com arrays dinâmicos de inteiros em imagens de alta resolução aloca gigabytes de RAM em poucos segundos e derruba servidores com OOM (Out Of Memory).

### Diretrizes de Baixo Consumo de Recursos:
1. **Garbage Collection Ativo:** Chame `gc.collect()` explicitamente após processar cada imagem/quadro.
2. **Subprocessos Isolados:** Ao rodar navegadores headless (como Firefox ou Chromium), use timeouts com tratamento de exceção (`try...except subprocess.TimeoutExpired`) e encerre explicitamente as instâncias.
3. **Média de Área 2x2 (Box Filtering):** Não use interpolações pesadas que duplicam matrizes na memória. A média de 4 pixels vizinhos (`(p0 + p1 + p2 + p3) >> 2`) consome quase zero de RAM e é antialiased.

---

## 5. Estratégia de Invalidação de Cache no GitHub (Cache-Bust)

O GitHub possui um proxy CDN intermediário (`camo.githubusercontent.com`) e os navegadores armazenam GIFs locais em cache de memória/disco. 

* **O Problema:** Adicionar `?v=2` ou `?raw=true` na URL de markdown é ignorado pelo redirecionamento 302 do GitHub.
* **A Solução Definitiva:** Sempre que regerar os GIFs com novo visual, **altere o nome do arquivo final no README**:
  * Em vez de: `docs/img/meu-projeto.gif`
  * Use: `docs/img/meu-projeto-showcase-overview.gif`
* Uma nova URL garante **0% de cache** no cliente e no servidor.

---

## 6. Script Python Completo e Autônomo

O script abaixo pode ser executado diretamente por qualquer agente ou desenvolvedor. Ele suporta duas modalidades:
1. **Com Pillow (`PIL`):** Utiliza fontes TrueType e renderização acelerada se instalada.
2. **Puro Python (Fallback Standalone):** Não requer nenhuma biblioteca externa (`pip`) e monta GIFs válidos usando apenas a biblioteca padrão (`struct`, `zlib`, `os`, `shutil`).

```python
#!/usr/bin/env python3
"""
Gerador de GIFs de Demonstração com Banner HUD em Linha Única para README.
Suporta Pillow (se disponível) ou compilação em puro Python sem dependências externas.
"""

import gc
import os
import shutil
import struct
import sys
import zlib
from typing import List, Tuple

# ---------------------------------------------------------------------------
# 1. Configurações Globais
# ---------------------------------------------------------------------------
FRAME_DELAY_CS = 150  # 1.5 segundos por tela (150 centésimos de segundo)
DOWNSCALE_FACTOR = 2  # Reduz de 1440x900 para 720x450 para leveza máxima

# Paleta Forense Curada (256 cores: tons escuros, cianos, esmeraldas e cinzas)
BRAND_HEXES = [
    "#0c0e14", "#001216", "#001a1d", "#111319", "#191b22", "#1e1f26",
    "#282a30", "#33343b", "#44474f", "#849495", "#b9cacb", "#e2e2eb", "#ffffff",
    "#00dbe9", "#7df4ff", "#dbfcff", "#006970", "#004f54", "#002022",
    "#4edea3", "#6ffbbe", "#003824", "#005236", "#002113",
    "#ffb4ab", "#ffdad6", "#ba1a1a", "#690005", "#ffb2b7", "#f1fa8c"
]

def build_global_palette() -> Tuple[List[Tuple[int, int, int]], bytes]:
    colors = []
    for h in BRAND_HEXES:
        h = h.lstrip("#")
        colors.append((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)))
    # Rampa de cinzas
    for i in range(32):
        v = int(i * 255 / 31)
        if (v, v, v) not in colors:
            colors.append((v, v, v))
    # Cubo RGB 6x6x6
    for r in [0, 51, 102, 153, 204, 255]:
        for g in [0, 51, 102, 153, 204, 255]:
            for b in [0, 51, 102, 153, 204, 255]:
                if (r, g, b) not in colors:
                    colors.append((r, g, b))
    colors = colors[:256]
    while len(colors) < 256:
        colors.append((0, 0, 0))
    raw_bytes = bytes(b for rgb in colors for b in rgb)
    return colors, raw_bytes

GLOBAL_PALETTE, GLOBAL_PALETTE_BYTES = build_global_palette()
COLOR_CACHE = {}

def rgb_to_palette_idx(r: int, g: int, b: int) -> int:
    rgb = (r, g, b)
    if rgb in COLOR_CACHE:
        return COLOR_CACHE[rgb]
    best_dist = 99999999
    best_idx = 0
    for idx, (pr, pg, pb) in enumerate(GLOBAL_PALETTE):
        dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if dist < best_dist:
            best_dist = dist
            best_idx = idx
            if dist == 0:
                break
    COLOR_CACHE[rgb] = best_idx
    return best_idx

# ---------------------------------------------------------------------------
# 2. Compressor LZW Conforme GIF89a (Baixo Consumo de RAM)
# ---------------------------------------------------------------------------
def lzw_compress(data: bytes, min_code_size: int = 8) -> bytes:
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

# ---------------------------------------------------------------------------
# 3. Decodificador PNG e Downscaling Antialiased 2x2
# ---------------------------------------------------------------------------
def decode_and_downscale_png(filepath: str, scale: int = 2) -> Tuple[int, int, bytes]:
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
        return c

    src_offset = dst_offset = 0
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
    stride2 = stride * scale

    for y in range(out_h):
        row0 = y * stride2
        row1 = row0 + stride if scale == 2 and (y * scale + 1) < height else row0
        for x in range(out_w):
            x2 = x * scale * bpp
            if scale == 2 and (x * 2 + 1) * bpp < stride:
                p0 = row0 + x2
                p1 = row0 + x2 + bpp
                p2 = row1 + x2
                p3 = row1 + x2 + bpp
                r = (recon[p0] + recon[p1] + recon[p2] + recon[p3]) >> 2
                g = (recon[p0 + 1] + recon[p1 + 1] + recon[p2 + 1] + recon[p3 + 1]) >> 2
                b = (recon[p0 + 2] + recon[p1 + 2] + recon[p2 + 2] + recon[p3 + 2]) >> 2
            else:
                p_offset = row0 + x2
                r, g, b = recon[p_offset], recon[p_offset + 1], recon[p_offset + 2]
            indexed[idx] = rgb_to_palette_idx(r, g, b)
            idx += 1

    del recon
    del raw
    gc.collect()
    return out_w, out_h, bytes(indexed)

# ---------------------------------------------------------------------------
# 4. Montagem e Serialização do GIF89a com Loop
# ---------------------------------------------------------------------------
def create_animated_gif(frames: List[Tuple[int, int, bytes]], delay_cs: int, output_path: str):
    assert len(frames) > 0
    w, h, _ = frames[0]

    gif = bytearray()
    gif.extend(b"GIF89a")
    gif.extend(struct.pack("<HH", w, h))
    gif.extend(bytes([0xF7, 0x00, 0x00]))  # 256 cores na Global Color Table
    gif.extend(GLOBAL_PALETTE_BYTES)
    # Netscape 2.0 Loop Block (Repetição infinita)
    gif.extend(b"\x21\xFF\x0BNETSCAPE2.0\x03\x01\x00\x00\x00")

    for frame_w, frame_h, idx_pixels in frames:
        lzw_data = lzw_compress(idx_pixels, 8)
        # Graphic Control Extension (Delay em centésimos de segundo: 150 = 1.5s)
        gif.extend(b"\x21\xF9\x04\x00" + struct.pack("<H", delay_cs) + b"\x00\x00")
        # Image Descriptor
        gif.extend(b"\x2C" + struct.pack("<HHHH", 0, 0, frame_w, frame_h) + b"\x00")
        gif.append(8)
        gif.extend(lzw_data)

    gif.extend(b"\x3B")  # Trailer do GIF

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(gif)

    size_kb = os.path.getsize(output_path) / 1024
    print(f"  [SUCESSO] GIF montado: {output_path} ({len(frames)} quadros, {size_kb:.1f} KB)")

# ---------------------------------------------------------------------------
# 5. Injeção de Título HUD no DOM (Se capturar via Navegador / Headless)
# ---------------------------------------------------------------------------
def get_hud_overlay_snippet_js(title_text: str) -> str:
    """Snippet JS injetado na página antes da captura de tela."""
    import json
    return f"""
    (function() {{
      const overlayTitle = {json.dumps(title_text)};
      let badge = document.getElementById('hud-overlay-badge');
      if (!badge) {{
        badge = document.createElement('div');
        badge.id = 'hud-overlay-badge';
        badge.style.cssText = 'position:fixed;bottom:26px;left:50%;transform:translateX(-50%);z-index:999999;background:rgba(0,18,22,0.98);border:4px solid #00dbe9;box-shadow:0 0 50px rgba(0,219,233,0.9),0 20px 50px rgba(0,0,0,0.98);border-radius:16px;padding:14px 34px;display:inline-flex;align-items:center;gap:14px;pointer-events:none;user-select:none;white-space:nowrap;max-width:96vw;box-sizing:border-box;';
        document.body.appendChild(badge);
      }}
      const parts = overlayTitle.split('//').map(s => s.trim());
      const mainTitle = parts[0] || overlayTitle;
      const subTitle = parts[1] || '';
      badge.innerHTML = `
        <span style="width:14px;height:14px;border-radius:50%;background:#4edea3;box-shadow:0 0 14px #4edea3;display:inline-block;flex-shrink:0;"></span>
        <span style="color:#ffffff;font-family:'JetBrains Mono',Consolas,monospace;font-size:38px;font-weight:900;letter-spacing:0.04em;text-transform:uppercase;text-shadow:0 4px 16px rgba(0,0,0,0.95), 0 0 25px rgba(0,219,233,0.5);line-height:1;">
          ${{mainTitle}}
        </span>
        ${{subTitle ? `<span style="color:#00dbe9;font-family:'JetBrains Mono',Consolas,monospace;font-size:34px;font-weight:900;opacity:0.8;margin:0 4px;">//</span><span style="color:#7df4ff;font-family:'JetBrains Mono',Consolas,monospace;font-size:36px;font-weight:800;letter-spacing:0.04em;text-transform:uppercase;text-shadow:0 3px 12px rgba(0,0,0,0.95);line-height:1;">${{subTitle}}</span>` : ''}}
      `;
    }})();
    """

# ---------------------------------------------------------------------------
# 6. Exemplo de Execução
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Módulo carregado com sucesso. Importe e chame create_animated_gif() passando os frames decodificados.")
```

---

## 7. Checklist de Verificação para a IA

Antes de considerar a entrega final dos GIFs concluída, verifique:

- [ ] **Linha Única Rígida:** O título não quebrou verticalmente em duas linhas (especificado com `white-space: nowrap`).
- [ ] **Timing Verificado:** A cadência está cravada em **1,5s por quadro** (`delay_cs = 150`).
- [ ] **Peso Leve:** Cada GIF tem entre 80 KB e 250 KB (carregamento instantâneo em qualquer conexão).
- [ ] **Nome de Arquivo com Cache-Bust:** O arquivo possui um nome novo ou sufixo inédito no `README.md` (ex: `*-showcase-overview.gif`), garantindo que o GitHub Camo entregue a versão nova na hora.
- [ ] **Antialiasing 2x2 Ativo:** O texto do título está nítido, sem saltar linhas ou perder caracteres finos.
- [ ] **Memória Segura:** O processo utilizou menos de 1,2 GB de RAM e executou `gc.collect()`.
