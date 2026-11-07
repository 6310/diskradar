# 📡 Geio DiskRadar — Triador e Indexador Read-Only de HDs e SSDs de Sucata

Aplicação Desktop em Python 3.11+ com interface Dark Mode em **CustomTkinter** projetada para triagem ultra-rápida e **100% Read-Only (somente leitura)** de HDs e SSDs conectados via Dock USB.

O **DiskRadar** lê apenas metadados do sistema de arquivos (`os.scandir` / `stat`) sem nunca abrir o conteúdo dos arquivos nem calcular hashes, evitando travamentos em discos com *Bad Blocks* físicos.

---

## ✨ Principais Funcionalidades

1. **Seletor de Unidade e "Crachá do Disco" (Header Instantâneo & Telemetria S.M.A.R.T.):**
   - Detecta Modelo Físico, Número de Série (`Serial Number`), Tipo de Mídia (`HDD`/`SSD`/`NVMe`), Rotação (`RPM`) e Saúde S.M.A.R.T. no Windows via PowerShell nativo (`Get-Partition`, `Get-Disk`, `Get-PhysicalDisk` e `MSStorageDriver_ATAPISmartData` com `ConvertTo-Json` e `CREATE_NO_WINDOW`, sem depender de `pywin32`/`wmi`).
   - **Horas de Uso (Power-On Hours):** Informa exatamente quantas horas o disco já operou ligado (ex: `14.280h (~595 dias)` e quantidade de ciclos de ligamento), essencial para precificar lotes de sucata.
   - Possui fallback gracioso no Linux para desenvolvimento e testes em VM.
   - Identifica automaticamente os possíveis donos do HD (`Users` / `Documents and Settings`) e estima a data do último uso com base em `Desktop`, `Documents` e `Downloads`.
   - Exibe alerta visual imediato caso a saúde S.M.A.R.T. indique falha física, setores realocados ou pendentes.

2. **Motor de Varredura Assíncrono Anti-Travamento (`os.scandir`):**
   - Executa em `threading.Thread` dedicada com comunicação em tempo real via `queue.Queue`.
   - Ignora imediatamente diretórios de sistema e cache (`Windows`, `Program Files`, `AppData`, `node_modules`, `.git`, etc.).
   - Isola erros `OSError`, `PermissionError` e `FileNotFoundError` individualmente e registra possíveis *Bad Blocks* sem interromper a triagem.

3. **Motor de Classificação Inteligente (`core/rules.py` & `core/classifier.py`):**
   - **Visão 1 — Pastas Quentes:** Agrupa por diretório fotos (`> 50 KB`), vídeos (`> 500 KB`) e documentos comuns, ordenando por relevância e tamanho para facilitar o *drag-and-drop*.
   - **Visão 2 — Agulhas no Palheiro (Caça a Dados Valiosos em Sucata):**
     - **Cripto, Carteiras & BIP-39:** Detecta `wallet.dat` (Bitcoin Core, Dogecoin, Litecoin), `electrum.dat`, `*.wallet`, `*.seed`, `*.sparrow` (Sparrow Wallet), `*.keys` (Monero), Wasabi Wallet, Daedalus (Cardano), Atomic Wallet, rastros de Trezor Suite e Ledger Live, e cofres de extensões Web3 (MetaMask, Phantom, Ronin, TronLink, Coinbase).
     - **Detector Ultraleve de Frases BIP-39:** Inspeciona com segurança arquivos de texto leves (`.txt`, `.rtf`, `.note` menores que 32 KB) buscando sequências de 12 ou 24 palavras do dicionário mnemônico oficial de 2048 palavras BIP-39, sem nunca expor nem gravar as palavras em disco.
     - **Navegadores & Sessões:** Sondagem cirúrgica e segura nos perfis de usuários (Chrome, Edge, Brave, Opera, Firefox) para extrair `Login Data` (senhas salvas), `Web Data` (autofill/cartões), `Bookmarks` e `History`, sem varrer gigabytes de caches inúteis.
     - **Engenharia / Arquitetura (CAD / 3D):** `.dwg`, `.dxf`, `.rvt`, `.skp`, `.step`, `.stp`, `.iges`, `.stl`, `.sldprt`, `.sldasm`, `.blend`.
     - **Design / Gráfica:** `.psd`, `.ai`, `.cdr`, `.eps`, `.indd`, `.prproj`, `.aep`.
     - **E-mails & Mensagens:** `.pst`, `.ost` (Outlook), `msgstore.db*` (WhatsApp), perfis Thunderbird.
     - **Contábil / IRPF & Lotes Fiscais:** Declarações `.dec`, `.rec`, `.dbk` e agrupamento inteligente de pastas com centenas de arquivos `.xml` fiscais.
     - **Bancos de Dados ERP/PDV:** `.fdb`, `.gdb`, `.mdf`, `.ldf`, `.bak`, `.sql`, `.sqlite`, `.sqlite3`.
     - **Backups & Imagens de Disco / VM:** `.tib` (Acronis), `.vbk` (Veeam), `.gho`, `.iso`, `.vhd`, `.vhdx`, `.vmdk`, `.ova`, `.ovf`, `.zip`, `.rar`, `.7z`.
     - **Caçador de Palavras-Chave:** Varre nomes de arquivos e pastas buscando termos como `senha`, `wallet`, `seed`, `bitcoin`, `escritura`, `contrato`, `inventario`, `familia`, etc.

4. **Calculadora Forense de Linha do Tempo & Histograma de Atividade (Aba 4):**
   - Agrupa e contabiliza a atividade ano a ano (fotos, vídeos, documentos, arquivos críticos e volume em MB/GB).
   - Identifica o período exato de uso do disco (ex: 2011 a 2018) e destaca o **Ano de Pico de Uso** com badge dourado (`★ PICO`).
   - Filtro forense anti-corrupção: ignora timestamps corrompidos ou padrões de MFT/FAT (ex: 1980 ou 2099+).
   - Botão de salto rápido `🎯 Ver Críticos de <Ano>` que direciona imediatamente para a Aba 2 com os achados daquele ano.

5. **Ponte Direta com o Windows Explorer e Área de Transferência:**
   - Botões **"Abrir no Explorer"** executam `explorer.exe /select,"<caminho>"` no Windows para abrir a janela já com o arquivo ou pasta selecionado e destacado. No Linux, utiliza `xdg-open`.
   - Botões **"📋 Copiar"** integrados em todas as linhas (Pastas, Arquivos, Usuários e Erros) com feedback tátil no botão (`✔ Copiado!`), permitindo colar caminhos em scripts de terminal, robocopy ou inventários.
   - Botão para copiar o relatório completo de erros/bad blocks de uma só vez para a área de transferência.

6. **Interface Gráfica Moderna & Ergonômica (CustomTkinter Dark Mode em 5 Abas):**
   - **Header & Command Bar:** Identidade visual com comandos principais agrupados e responsivos.
   - **Crachá do Disco Interativo:** Dashboard com medidor visual de capacidade (gauge bar de % usado vs livre), cópia rápida de Serial Number e badge S.M.A.R.T. colorido.
   - **HUD ao Vivo:** Pílulas de métricas em tempo real (`Pastas`, `Arquivos`, `Fotos`, `Vídeos`, `Docs`, `Pastas Quentes`, `Críticos`, `Erros`).
   - **Ordenação Dinâmica:** Permite ordenar Pastas Quentes por Relevância, Maior Tamanho, Quantidade de Arquivos ou Data Mais Recente diretamente na interface.
   - **Cartões de Usuários Estruturados:** Separação visual clara entre pastas pessoais (`Desktop`, `Documents`, `Pictures`, `Downloads`) e sessões de navegadores (`Chrome`, `Edge`, `Firefox`, `AppData`).

7. **Gerador de "Catálogo de Autópsia" (Relatório HTML Único Autocontido):**
   - Exporta um único arquivo `.html` 100% offline (`Relatorio_YYYY-MM-DD_<Usuarios>_<Modelo>_SN-<Serial>.html`) com CSS Dark Mode, gráfico de barras da Linha do Tempo e busca instantânea em JavaScript para consultar até 50.000 arquivos mesmo meses após o descarte do HD.

8. **Otimizações de Alto Desempenho (Performance Engine):**
   - **Descarte em $O(1)$ de CPU:** Conjunto unificado `ALL_INTERESTING_EXTENSIONS` e filtro relâmpago `is_file_potentially_relevant` que descarta milhões de arquivos de sistema (`.dll`, `.sys`, `.ini`, `.cat`) sem chamadas desnecessárias de sistema.
   - **Economia de RAM via `slots=True`:** Todas as estruturas de dados (`HotFolderItem`, `CriticalFileItem`, `CatalogEntry`, `DiskBadgeInfo`) usam slots nativos do Python 3.10+, reduzindo o consumo de memória em mais de 60%.
   - **PowerShell em Thread Assíncrona:** A troca de unidade e o carregamento do app respondem em 0ms (sem congelar a interface enquanto o PowerShell consulta o hardware).
   - **Debounce de 200ms & Lazy Loading na GUI:** A busca rápida possui debounce para evitar redesenho por tecla e renderiza sob demanda em blocos de 35 itens, eliminando gargalos de widgets do CustomTkinter.

---

## 📂 Estrutura do Projeto

```text
diskradar/
├── main.py                 # Ponto de entrada da aplicação
├── requirements.txt        # Dependências do projeto
├── build_exe.bat           # Script automatizado para gerar DiskRadar.exe no Windows
├── README.md               # Documentação de uso e compilação
├── ui/
│   └── app.py              # Interface gráfica CustomTkinter em 5 abas + Crachá do Disco
└── core/
    ├── disk_info.py        # Coleta de Hardware, Serial, S.M.A.R.T. (PowerShell/Linux) e Usuários
    ├── scanner.py          # Motor os.scandir multithread com Blocklist e captura de Bad Blocks
    ├── classifier.py       # Classificação de Pastas Quentes, Agulhas no Palheiro e Catálogo
    ├── bip39.py            # Dicionário de 2048 palavras e detector ultraleve de seed BIP-39
    ├── rules.py            # Extensões, limites em bytes, blocklists e palavras-chave
    ├── exporter.py         # Gerador de relatório HTML autocontido com busca JS
    └── explorer_bridge.py  # Integração com explorer.exe /select e xdg-open
```

---

## 🚀 Como Executar em Desenvolvimento (Linux ou Windows)

1. Crie e ative um ambiente virtual Python 3.11+:
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # No Linux
   # ou: venv\Scripts\activate.bat (No Windows)
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```bash
   python3 main.py
   ```

> **Nota para Linux (Debian/Ubuntu):** Caso o `tkinter` não esteja instalado no sistema base, instale com `sudo apt-get install python3-tk`.

---

## 📦 Como Gerar o Executável `.exe` no Windows 10/11

No PC Windows, basta dar um duplo-clique em **`build_exe.bat`** (ou executá-lo pelo Prompt de Comando):

```bat
build_exe.bat
```

O script irá automaticamente:
1. Criar o ambiente virtual `venv` (se ainda não existir).
2. Instalar `customtkinter`, `psutil` e `pyinstaller`.
3. Executar:
   ```bat
   pyinstaller --noconfirm --onefile --windowed --name "DiskRadar" --collect-all customtkinter main.py
   ```
4. Disponibilizar o executável portátil em **`dist\DiskRadar.exe`**.
