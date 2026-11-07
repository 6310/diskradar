"""
Regras de negócio, constantes de extensões, limites de tamanho, blocklists e palavras-chave
para triagem Read-Only de HDs e SSDs no Geio DiskRadar.
Otimizado com conjuntos unificados para descarte em O(1) de arquivos irrelevantes.
"""

from typing import Dict, Set, Tuple

# ==============================================================================
# BLOCKLIST DE DIRETÓRIOS (Ignorar imediatamente - comparação case-insensitive)
# ==============================================================================
# Nota: AppData é ignorado na varredura recursiva cega para evitar 50.000+ arquivos
# de cache e shaders, mas navegadores e carteiras são inspecionados de forma cirúrgica.
DIR_BLOCKLIST: Set[str] = {
    "windows",
    "program files",
    "program files (x86)",
    "programdata",
    "$recycle.bin",
    "system volume information",
    "recovery",
    "perflogs",
    "appdata",
    "node_modules",
    ".git",
    ".vscode",
    ".cache",
    "cache",
    "gpucache",
    "code cache",
}

# Usuários padrão do Windows a serem ignorados na detecção de donos do disco
IGNORED_USERS: Set[str] = {
    "public",
    "default",
    "default user",
    "all users",
    "todos os usuários",
    "usuário padrão",
    "desktop.ini",
}

# ==============================================================================
# LIMITES DE TAMANHO ANTI-LIXO (em Bytes)
# ==============================================================================
MIN_PHOTO_SIZE_BYTES: int = 50 * 1024       # 50 KB (ignora ícones, thumbnails, etc.)
MIN_VIDEO_SIZE_BYTES: int = 500 * 1024      # 500 KB (ignora animações curtas de sistema)
MAX_CATALOG_FILES: int = 50_000             # Limite inteligente para o catálogo HTML pesquisável

# ==============================================================================
# VISÃO 1: EXTENSÕES DE "PASTAS QUENTES" (Mídia & Documentos Comuns)
# ==============================================================================
PHOTO_EXTENSIONS: Set[str] = {
    ".jpg", ".jpeg", ".png", ".heic", ".webp",
    ".cr2", ".nef", ".raw", ".arw", ".dng",
}

VIDEO_EXTENSIONS: Set[str] = {
    ".mp4", ".mov", ".avi", ".mkv", ".wmv", ".3gp", ".m4v",
}

DOC_EXTENSIONS: Set[str] = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".odt", ".ods", ".txt", ".csv", ".rtf",
}

# ==============================================================================
# VISÃO 2: "AGULHAS NO PALHEIRO" (Arquivos Críticos Isolados)
# ==============================================================================

# A. E-mails e Mensagens
CRITICAL_EMAIL_EXTENSIONS: Set[str] = {
    ".pst", ".ost",
}

# B. Imposto de Renda / Receita Federal
CRITICAL_IRPF_EXTENSIONS: Set[str] = {
    ".dec", ".rec", ".dbk",
}

CRITICAL_IRPF_DIR_KEYWORDS: Tuple[str, ...] = (
    "programa irpf",
    "arquivos de programas rfb",
)

# C. Certificados Digitais e Cofres de Chaves
CRITICAL_CERT_EXTENSIONS: Set[str] = {
    ".pfx", ".p12", ".pem", ".key", ".kdbx",
}

# D. Bancos de Dados e Sistemas (ERP/PDV)
CRITICAL_DB_EXTENSIONS: Set[str] = {
    ".fdb", ".gdb", ".mdf", ".ldf", ".bak",
    ".sql", ".sqlite", ".sqlite3", ".mdb", ".accdb",
}

# E. Compactados / Imagens de Disco / Backups de Máquinas Virtuais
CRITICAL_ARCHIVE_EXTENSIONS: Set[str] = {
    ".zip", ".rar", ".7z", ".iso", ".gho", ".vhd", ".vhdx", ".vmdk",
    ".tib", ".vbk", ".ova", ".ovf", ".qcow2",
}

# F. Notas Fiscais
CRITICAL_XML_EXTENSION: str = ".xml"

# G. Engenharia / Arquitetura (CAD / 3D)
CRITICAL_CAD_EXTENSIONS: Set[str] = {
    ".dwg", ".dxf", ".rvt", ".skp", ".step", ".stp", ".iges", ".igs",
    ".stl", ".sldprt", ".sldasm", ".blend",
}

# H. Design / Gráfica Profissional
CRITICAL_DESIGN_EXTENSIONS: Set[str] = {
    ".psd", ".ai", ".cdr", ".eps", ".indd", ".prproj", ".aep",
}

# I. Criptomoedas, Carteiras & Keystores
CRITICAL_CRYPTO_FILENAMES: Set[str] = {
    "wallet.dat",
    "electrum.dat",
    "default_wallet",
    "monero-wallet-keys",
    "keystore",
    "key.dat",
    "seed.txt",
    "seeds.txt",
    "frase.txt",
    "frases.txt",
    "frase_recuperacao.txt",
    "palavras_chave.txt",
    "palavras.txt",
    "mnemonic.txt",
    "recovery.txt",
    "segredo.txt",
    "passphrase.txt",
}

CRITICAL_CRYPTO_EXTENSIONS: Set[str] = {
    ".wallet",
    ".seed",
    ".keys",
    ".sparrow",
}

# IDs conhecidos de extensões de carteiras Web3 para Chrome/Brave/Edge
WEB3_EXTENSION_IDS: Dict[str, str] = {
    "nkbihfbeogaeaoehlefnkodbefgpgknn": "MetaMask Vault",
    "bfnaelmomeimhlpmgjnjophhpkkoljpa": "Phantom Solana Vault",
    "ejbalbakoplchlghecdalmeeeajnimhm": "Ronin Vault",
    "ibnejdfjmmkpcnlpebklmnkoeoihofec": "TronLink Vault",
    "hnfanknocfeofbddgcijnmhnfnkdnaad": "Coinbase Wallet Vault",
}

# J. Caçador de Palavras-Chave no nome do arquivo ou pasta
HUNTER_KEYWORDS: Tuple[str, ...] = (
    "senha",
    "senhas",
    "password",
    "passwords",
    "credenciais",
    "login",
    "carteira",
    "wallet",
    "seed",
    "bip39",
    "mnemonic",
    "mnemonica",
    "crypto",
    "bitcoin",
    "ethereum",
    "monero",
    "sparrow",
    "wasabi",
    "exodus",
    "daedalus",
    "trezor",
    "ledger",
    "backup",
    "bkp",
    "recuperacao",
    "irpf",
    "imposto",
    "contrato",
    "escritura",
    "inventario",
    "certificado",
    "importante",
    "particular",
    "familia",
    "casamento",
)

# Conjunto global pré-compilado de todas as extensões que nos interessam (Lookup O(1))
ALL_INTERESTING_EXTENSIONS: Set[str] = (
    PHOTO_EXTENSIONS
    | VIDEO_EXTENSIONS
    | DOC_EXTENSIONS
    | CRITICAL_EMAIL_EXTENSIONS
    | CRITICAL_IRPF_EXTENSIONS
    | CRITICAL_CERT_EXTENSIONS
    | CRITICAL_DB_EXTENSIONS
    | CRITICAL_ARCHIVE_EXTENSIONS
    | CRITICAL_CAD_EXTENSIONS
    | CRITICAL_DESIGN_EXTENSIONS
    | CRITICAL_CRYPTO_EXTENSIONS
    | {CRITICAL_XML_EXTENSION, ".tar.gz"}
)

# Categorias de filtro para a Aba 2 (Arquivos Críticos)
CRITICAL_CATEGORIES: Dict[str, str] = {
    "ALL": "Todos",
    "CRYPTO_WALLETS": "Cripto & Carteiras",
    "BROWSERS_CREDS": "Navegadores & Sessões",
    "KEYWORDS": "Senhas/Keywords",
    "CAD_DESIGN": "Engenharia/CAD/Design",
    "IRPF_FISCAL": "Contábil/IRPF/XML",
    "DB_ERP": "Bancos/Sistemas",
    "EMAIL_MSG": "E-mails/PST/WhatsApp",
    "CERT_KEYS": "Certificados/Chaves",
    "ARCHIVES": "Compactados/Backups/VMs",
}


def is_file_potentially_relevant(name_lower: str, ext: str) -> bool:
    """
    Filtro relâmpago executado em O(1) de CPU antes de processar regras mais pesadas.
    Permite descartar imediatamente milhões de .dll, .sys, .ini, .log, .cat, .tmp sem overhead.
    """
    if ext in ALL_INTERESTING_EXTENSIONS:
        return True
    if name_lower in CRITICAL_CRYPTO_FILENAMES or name_lower.startswith(("msgstore.db", "utc--")):
        return True
    for kw in HUNTER_KEYWORDS:
        if kw in name_lower:
            return True
    return False


def format_size(num_bytes: int) -> str:
    """Formata tamanho em bytes para leitura humana (KB, MB, GB, TB)."""
    if num_bytes < 0:
        return "0 B"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if num_bytes < 1024.0 or unit == "TB":
            if unit == "B":
                return f"{int(num_bytes)} B"
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} TB"
