# 📡 Geio DiskRadar (v2.1+) — Triador e Indexador Read-Only de HDs e SSDs

Software Desktop em Python 3.11+ para triagem ultra-rápida, forense e **100% Read-Only (somente leitura)** de HDs e SSDs conectados via Dock USB/SATA. Projetado para operadores de bancada, recuperadores de ativos e técnicos que precisam avaliar lotes de discos descartados ou sucata.

O **DiskRadar** lê metadados do sistema de arquivos (`os.scandir` / `stat`) sem nunca alterar, criar, mover ou deletar dados na unidade, preservando discos com falhas físicas e *Bad Blocks*.

---

## ✨ Principais Funcionalidades

1. **Seletor de Unidade e "Crachá do Disco" (Telemetria S.M.A.R.T. & Hardware):**
   - Detecta Modelo Físico, Número de Série (`S/N`), Tipo de Mídia (`HDD`/`SSD`/`NVMe`), Rotação (`RPM`), Temperatura e Saúde S.M.A.R.T. no Windows via PowerShell nativo (`Get-Partition`, `Get-Disk`, `Get-PhysicalDisk` e `MSStorageDriver_ATAPISmartData` com `ConvertTo-Json` e `CREATE_NO_WINDOW`, sem depender de drivers externos).
   - **Horas de Uso (Power-On Hours):** Informa exatamente quantas horas o disco já operou ligado (ex: `14.280h (~595 dias)` e contagem de ciclos de ligamento), essencial para precificar lotes de sucata.
   - Possui fallback no Linux para desenvolvimento e testes em bancada/VM.
   - Identifica automaticamente os perfis de usuários no disco (`Users` / `Documents and Settings`) e estima a data do último uso com base em arquivos recentes.
   - Alerta visual imediato caso haja risco físico, setores realocados ou pendentes.

2. **Motor de Varredura Assíncrono Anti-Travamento (`os.scandir`):**
   - Executa em `threading.Thread` dedicada com comunicação em tempo real via `queue.Queue`.
   - Ignora imediatamente diretórios de sistema e cache (`Windows`, `Program Files`, `AppData`, `node_modules`, `.git`, etc.) na varredura recursiva cega para economizar tempo.
   - Realiza sondagem cirúrgica e segura em locais de alto valor sem varrer gigabytes de caches irrelevantes.
   - Isola erros `OSError`, `PermissionError` e registra possíveis *Bad Blocks* sem travar a interface.

3. **Motor de Classificação Inteligente (`core/rules.py` & `core/classifier.py`):**
   - **Visão 1 — Pastas Quentes:** Agrupa fotos (`> 50 KB`), vídeos (`> 500 KB`) e documentos comuns por diretório, calculando contadores, volume total e data recente para cópia rápida.
   - **Visão 2 — Agulhas no Palheiro (Achados Críticos):**
     - **Cripto, Carteiras & BIP-39:** Detecta `wallet.dat` (Bitcoin Core, Dogecoin, Litecoin), `electrum.dat`, `*.wallet`, `*.seed`, `*.sparrow` (Sparrow Wallet), `*.keys` (Monero), Wasabi Wallet, Daedalus (Cardano), Atomic Wallet, rastros de Trezor Suite e Ledger Live, e extensões Web3 (MetaMask, Phantom, Ronin, TronLink, Coinbase).
     - **Detector de Sementes BIP-39:** Inspeciona com segurança arquivos de texto leves buscando sequências mnemônicas de 12 a 24 palavras do dicionário oficial de 2048 palavras BIP-39, sem nunca gravar ou expor as palavras em disco.
     - **Navegadores & Sessões:** Localiza `Login Data` (senhas salvas), `Web Data`, `Bookmarks` e `History` dos principais navegadores (Chrome, Edge, Brave, Opera, Firefox).
     - **Engenharia / Arquitetura (CAD / 3D):** `.dwg`, `.dxf`, `.rvt`, `.skp`, `.step`, `.stp`, `.iges`, `.stl`, `.sldprt`, `.sldasm`, `.blend`.
     - **Design / Gráfica:** `.psd`, `.ai`, `.cdr`, `.eps`, `.indd`, `.prproj`, `.aep`.
     - **E-mails & Mensagens:** `.pst`, `.ost` (Outlook), `msgstore.db*` (WhatsApp), perfis Thunderbird.
     - **Contábil / IRPF & Lotes Fiscais:** Declarações `.dec`, `.rec`, `.dbk` e agrupamento inteligente de pastas com arquivos `.xml` fiscais.
     - **Bancos de Dados ERP/PDV:** `.fdb`, `.gdb`, `.mdf`, `.ldf`, `.bak`, `.sql`, `.sqlite`, `.sqlite3`.
     - **Backups & Imagens:** `.tib` (Acronis), `.vbk` (Veeam), `.gho`, `.iso`, `.vhd`, `.vhdx`, `.vmdk`, `.ova`, `.zip`, `.rar`, `.7z`.

4. **Linha do Tempo Forense & Histograma de Atividade (Aba 4):**
   - Contabiliza arquivos ano a ano identificando o período exato de uso do HD e destacando o **Ano de Pico de Uso**.

5. **Ponte com Windows Explorer & Área de Transferência:**
   - Para arquivos: executa `explorer.exe /select,"<caminho>"` destacando o item na pasta original.
   - Para pastas: abre diretamente o diretório para exploração imediata.
   - Botões de cópia rápida com feedback tátil (`✔ Copiado!`).

6. **Relatório HTML Autocontido ("Catálogo de Autópsia"):**
   - Exporta um arquivo `.html` 100% offline com CSS Dark Mode e motor de busca rápida em JavaScript para consultas mesmo após a desconexão ou descarte do disco.

---

## 📂 Estrutura do Repositório

```text
diskradar/
├── main.py                 # Ponto de entrada (DPI Awareness Windows + inicialização da UI)
├── requirements.txt        # Dependências de produção
├── .env.example            # Exemplo de variáveis de ambiente opcionais
├── .gitignore              # Regras estratégicas de exclusão Git
├── run_linux.sh            # Script de inicialização rápida no Linux
├── Executar_DiskRadar.bat  # Inicializador direto no Windows (sem precisar compilar)
├── Compilar_EXE.bat        # Compilador PyInstaller automatizado (.exe standalone)
├── LEIAME.txt              # Guia rápido de uso em português para Windows
├── README.md               # Esta documentação
├── core/                   # Motor Forense Read-Only (100% testado)
│   ├── bip39.py            # Dicionário de 2048 palavras e detector ultraleve de sementes BIP-39
│   ├── classifier.py       # Motor de classificação e dataclasses de resultados
│   ├── disk_info.py        # Coleta de Hardware, S/N, S.M.A.R.T. e Usuários
│   ├── explorer_bridge.py  # Integração segura com o Windows Explorer (/select) e xdg-open
│   ├── exporter.py         # Gerador de relatório HTML offline com busca JS
│   ├── rules.py            # Regras, extensões, blocklists e limites de relevância
│   └── scanner.py          # Thread assíncrona (AsyncDiskScanner) com fila de eventos
├── tests/                  # Suíte de testes unitários automatizados
│   ├── test_bip39.py       # Testes do detector de sementes BIP-39
│   ├── test_classifier.py  # Testes de agrupamento e scores de relevância
│   ├── test_disk_info.py   # Testes dos resumos de telemetria e crachá do disco
│   ├── test_explorer_bridge.py # Testes da ponte do gerenciador de arquivos
│   └── test_rules.py       # Testes de regras de negócio e limites
└── ui/                     # Camada de Interface Gráfica Desktop
    └── app.py              # Interface Gráfica CustomTkinter (5 abas + HUD)
```

---

## 🚀 Como Executar

### No Linux (Desenvolvimento / Bancada):
Basta rodar o script utilitário incluído:
```bash
./run_linux.sh
```
Ou manualmente com Python virtualenv:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

### No Windows:
- **Execução direta (sem compilar):** dê dois cliques em `Executar_DiskRadar.bat`.
- **Gerar o executável único `.exe`:** dê dois cliques em `Compilar_EXE.bat`. O binário standalone será gerado em `dist\DiskRadar-v2.1.0.exe` e copiado automaticamente para a raiz.

---

## 🧪 Suíte de Testes Automatizados

Para executar os testes unitários da suíte `tests/`:
```bash
python3 -m unittest discover -s tests
```

---

## 🔒 Garantia de Segurança Inegociável

- O Geio DiskRadar opera **EXCLUSIVAMENTE em modo LEITURA (Read-Only)**.
- O software não contém nenhuma rotina de formatação, particionamento, deleção, sobrescrita ou movimentação de arquivos na unidade analisada.
- A única operação de escrita existente é a exportação voluntária de relatórios HTML no local escolhido pelo usuário.
