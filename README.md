# 📡 Geio DiskRadar (v2.2.0) — Triador e Indexador Read-Only de HDs e SSDs

Software Desktop em Python 3.11+ para triagem ultra-rápida, forense e **100% Read-Only (somente leitura)** de HDs e SSDs conectados via Dock USB/SATA. Projetado para operadores de bancada, recuperadores de ativos e técnicos que precisam avaliar lotes de discos descartados ou sucata.

O **DiskRadar v2.2.0** traz a nova interface gráfica **Stitch "Cyber-Forensic Precision"** (10 telas e modais unificados) acoplada ao motor Python Read-Only (`core/`), lendo metadados e blocos iniciais (`os.scandir` / `stat` / `rb`) sem nunca alterar, criar, mover ou deletar dados na unidade analisada.

---

## ✨ Principais Funcionalidades (v2.2.0)

1. **Estação Forense Stitch "Cyber-Forensic Precision" (10 Telas & Modais):**
   - **Tela 1 — Pastas Quentes (`pastas-quentes`):** 4 cartões Bento KPI, filtros por tipo (`TODAS`, `FOTOS`, `VÍDEOS`, `DOCS`, `MISTO`), ordenação por Score Forense (`0-100 pts`), Volume, Arquivos ou Recência, e botões `Copiar` e `Explorar` (`explorer.exe`).
   - **Tela 2 — Arquivos Críticos (`arquivos-criticos`):** Filtros instantâneos pelas 10 categorias forenses, busca com debounce, e botões `Ver Hex` (abre o Inspetor Hexadecimal no arquivo), `Copiar` e `Abrir no Explorer` (`explorer.exe /select,"..."`).
   - **Tela 3 — Árvore de Usuários & Atalhos Rápidos (`usuarios-atalhos`):** Cartões dinâmicos por perfil de usuário com 8 atalhos 1-clique (`Desktop`, `Documents`, `Downloads`, `Pictures`, `Videos`, `AppData`, `Browsers`, `SSH`) + Diretórios Globais do Sistema.
   - **Tela 4 — Linha do Tempo & Atividade (`linha-do-tempo`):** Cronogeografia de atividade, Card de Insight Forense (Ano de Pico), gráfico de barras horizontais segmentadas ano a ano e matriz analítica consolidada.
   - **Tela 5 — Log de Erros & Bad Blocks (`log-erros`):** 4 KPIs de telemetria física (`I/O Read Errors`, `PermissionError / ACL`, `Total de Incidentes`, `Setores Críticos 05/C5`), filtro de ACLs e exportação de dump `.TXT`.
   - **Tela 6 — Monitor de Varredura ao Vivo (`live-monitor`):** Console de I/O em tempo real (`[KERNEL]`, `[SONDAGEM]`, `[IO_READ]`, `[HOT_FOLDER]`, `[MATCH_CRITICAL]`, `[SECTOR_WARN]`, `[FINISHED]`) e feed instantâneo de achados críticos.
   - **Tela 7 — Resumo Executivo Pós-Varredura (`resumo-pos-varredura`):** Balanço final da sessão com hash SHA-256 da cadeia de custódia, top achados críticos e top pastas quentes.
   - **Modal 8 — Diagnóstico S.M.A.R.T. Detalhado (`modal-smart`):** Score Eletromecânico (`0-100%`), 6 micro-cards de telemetria e tabela ATA/NVMe com alternância `RAW HEX` / `DECIMAL`.
   - **Modal 9 — Exportação de Relatório HTML (`modal-export`):** Configuração e preview interativo do Catálogo de Autópsia `.html` 100% offline com seletor nativo de destino (`Salvar Como...`).
   - **Modal 10 — Inspetor Hexadecimal Read-Only (`modal-hex`):** Leitura pura (`rb`) de blocos de 512 bytes com navegação de setores (`-512B` / `+512B`), cálculo de Entropia de Shannon (`0.00 - 8.00 bits/byte`), detector de assinatura Magic Number (`SQLite 3`, `Wallet.dat Berkeley DB`, `ZIP/OOXML`, `PDF`, `PST`, `KDBX`, `DWG`, `PSD`, etc.), Data Inspector (`uint8`, `uint16_le`, `uint32_le`) e SHA-256 parcial.

2. **Motor de Varredura Assíncrono Anti-Travamento (`os.scandir`):**
   - Executa em `threading.Thread` dedicada com comunicação em tempo real via `queue.Queue` e snapshots thread-safe (`get_live_snapshot()`).
   - Ignora diretórios de sistema e cache (`Windows`, `Program Files`, `AppData`, `node_modules`, `.git`, etc.) na varredura recursiva cega e aplica sondagem cirúrgica (`TARGETED_USER_SUBPATHS`) em locais de alto valor (carteiras cripto, cofres de navegadores, Outlook, WhatsApp, SSH).

---

## 📂 Estrutura do Repositório

```text
diskradar/
├── main.py                 # Ponto de entrada (abre Stitch GUI v2.2.0 ou CustomTkinter com --classic)
├── requirements.txt        # Dependências de produção
├── .env.example            # Exemplo de variáveis de ambiente opcionais
├── .gitignore              # Regras estratégicas de exclusão Git
├── run_linux.sh            # Script de inicialização rápida no Linux
├── Executar_DiskRadar.bat  # Inicializador direto no Windows (sem precisar compilar)
├── Compilar_EXE.bat        # Compilador PyInstaller automatizado (gera DiskRadar-v2.2.0.exe)
├── LEIAME.txt              # Guia rápido de uso em português para Windows
├── README.md               # Esta documentação
├── core/                   # Motor Forense Read-Only (100% testado)
│   ├── bip39.py            # Dicionário de 2048 palavras e detector ultraleve de sementes BIP-39
│   ├── classifier.py       # Motor de classificação e dataclasses de resultados
│   ├── disk_info.py        # Coleta de Hardware, S/N, S.M.A.R.T. e Usuários
│   ├── explorer_bridge.py  # Integração segura com o Windows Explorer (/select) e xdg-open
│   ├── exporter.py         # Gerador de relatório HTML offline com busca JS
│   ├── hex_inspector.py    # Inspetor Hexadecimal Read-Only (512B, Entropia de Shannon, Magic Bytes)
│   ├── rules.py            # Regras, extensões, blocklists e limites de relevância
│   └── scanner.py          # Thread assíncrona (AsyncDiskScanner) com fila de eventos e live snapshot
├── tests/                  # Suíte de testes unitários automatizados
│   ├── test_bip39.py       # Testes do detector de sementes BIP-39
│   ├── test_classifier.py  # Testes de agrupamento e scores de relevância
│   ├── test_disk_info.py   # Testes dos resumos de telemetria e crachá do disco
│   ├── test_explorer_bridge.py # Testes da ponte do gerenciador de arquivos
│   ├── test_hex_inspector.py   # Testes do inspetor hexadecimal Read-Only e entropia
│   └── test_rules.py       # Testes de regras de negócio e limites
└── ui/                     # Camada de Interface Gráfica Desktop
    ├── stitch_server.py    # Servidor local ThreadingHTTPServer + Launcher nativo (--app mode)
    ├── stitch_template.py  # Template SPA unificado das 10 telas Stitch Cyber-Forensic Precision
    └── app.py              # Interface Gráfica CustomTkinter clássica (--classic)
```

---

## 🚀 Como Executar

### No Linux (Desenvolvimento / Bancada):
```bash
./run_linux.sh
```
Ou manualmente:
```bash
python3 main.py            # Abre a Interface Stitch v2.2.0 (10 Telas)
python3 main.py --classic  # Abre a Interface CustomTkinter Clássica
```

### No Windows:
- **Execução direta (sem compilar):** dê dois cliques em `Executar_DiskRadar.bat`.
- **Gerar o executável único `.exe`:** dê dois cliques em `Compilar_EXE.bat`. O binário standalone será gerado em `dist\DiskRadar-v2.2.0.exe` e copiado automaticamente para a raiz.

---

## 🧪 Suíte de Testes Automatizados

```bash
python3 -m unittest discover -s tests -v
```

---

## 🔒 Garantia de Segurança Inegociável

- O Geio DiskRadar opera **EXCLUSIVAMENTE em modo LEITURA (Read-Only)**.
- O software não contém nenhuma rotina de formatação, particionamento, deleção, sobrescrita ou movimentação de arquivos na unidade analisada.
