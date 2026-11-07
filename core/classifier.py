"""
Motor de Classificação Inteligente do Geio DiskRadar.
Processa metadados de arquivos (sem nunca ler conteúdo) e organiza em:
1. Pastas Quentes (agrupamento por diretório de Fotos >50KB, Vídeos >500KB e Documentos)
2. Agulhas no Palheiro (Arquivos Críticos isolados, CAD, Design, Cripto, Navegadores e Lotes de XML Fiscal)
3. Catálogo Pesquisável de Arquivos Relevantes (para exportação HTML)

Otimizado com dataclasses(slots=True) para redução drástica de uso de memória RAM.
"""

import datetime
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from core.bip39 import detect_bip39_seed

from core.rules import (
    ALL_INTERESTING_EXTENSIONS,
    CRITICAL_ARCHIVE_EXTENSIONS,
    CRITICAL_CAD_EXTENSIONS,
    CRITICAL_CERT_EXTENSIONS,
    CRITICAL_CRYPTO_EXTENSIONS,
    CRITICAL_CRYPTO_FILENAMES,
    CRITICAL_DB_EXTENSIONS,
    CRITICAL_DESIGN_EXTENSIONS,
    CRITICAL_EMAIL_EXTENSIONS,
    CRITICAL_IRPF_DIR_KEYWORDS,
    CRITICAL_IRPF_EXTENSIONS,
    CRITICAL_XML_EXTENSION,
    DOC_EXTENSIONS,
    HUNTER_KEYWORDS,
    MAX_CATALOG_FILES,
    MIN_PHOTO_SIZE_BYTES,
    MIN_VIDEO_SIZE_BYTES,
    PHOTO_EXTENSIONS,
    VIDEO_EXTENSIONS,
    format_size,
    is_file_potentially_relevant,
)


# Pesos de Prioridade Forense para Triagem de Ativos (Cripto e Senhas sempre têm precedência)
FORENSIC_CATEGORY_PRIORITY: Dict[str, int] = {
    "CRYPTO_WALLETS": 100,
    "BROWSERS_CREDS": 90,
    "CERT_KEYS": 85,
    "KEYWORDS": 75,
    "DATABASE_ERP": 70,
    "CAD_DESIGN": 60,
    "EMAIL_MSG": 50,
    "IRPF_FISCAL": 40,
    "ARCHIVES": 30,
}


@dataclass(slots=True)
class HotFolderItem:
    """Representa um diretório agrupado na Visão 1 ('Pastas Quentes')."""
    folder_path: str
    photos_count: int = 0
    videos_count: int = 0
    docs_count: int = 0
    total_bytes: int = 0
    latest_mtime: float = 0.0

    @property
    def total_files(self) -> int:
        return self.photos_count + self.videos_count + self.docs_count

    @property
    def dominant_icon_tag(self) -> str:
        if self.photos_count >= self.videos_count and self.photos_count >= self.docs_count and self.photos_count > 0:
            return "[FOTOS]"
        if self.videos_count >= self.photos_count and self.videos_count >= self.docs_count and self.videos_count > 0:
            return "[VÍDEOS]"
        if self.docs_count > 0:
            return "[DOCS]"
        return "[MISTO]"

    @property
    def formatted_size(self) -> str:
        return format_size(self.total_bytes)

    @property
    def formatted_date(self) -> str:
        if self.latest_mtime <= 0:
            return "N/A"
        try:
            return datetime.datetime.fromtimestamp(self.latest_mtime).strftime("%d/%m/%Y")
        except Exception:
            return "N/A"

    @property
    def relevance_score(self) -> float:
        """Pontuação combinada de quantidade de arquivos e volume para ordenação."""
        size_mb = self.total_bytes / (1024 * 1024)
        return (self.total_files * 10.0) + min(size_mb, 50_000.0)


@dataclass(slots=True)
class CriticalFileItem:
    """Representa um achado na Visão 2 ('Agulhas no Palheiro' / Arquivos Críticos)."""
    name: str
    full_path: str
    category_key: str     # Chave em CRITICAL_CATEGORIES
    tag_label: str        # Ex: "[Cripto Wallet]", "[Chrome Senhas]", "[CAD DWG]", "[E-mail/PST]"
    size_bytes: int
    mtime: float
    matched_reason: str = ""
    is_directory_batch: bool = False

    @property
    def formatted_size(self) -> str:
        return format_size(self.size_bytes)

    @property
    def formatted_date(self) -> str:
        if self.mtime <= 0:
            return "N/A"
        try:
            return datetime.datetime.fromtimestamp(self.mtime).strftime("%d/%m/%Y %H:%M")
        except Exception:
            return "N/A"


@dataclass(slots=True)
class CatalogEntry:
    """Entrada enxuta para o catálogo pesquisável do relatório HTML."""
    rel_path: str
    name: str
    category: str
    size_bytes: int
    mtime: float

    @property
    def formatted_size(self) -> str:
        return format_size(self.size_bytes)

    @property
    def formatted_date(self) -> str:
        if self.mtime <= 0:
            return "N/A"
        try:
            return datetime.datetime.fromtimestamp(self.mtime).strftime("%Y-%m-%d %H:%M")
        except Exception:
            return "N/A"


@dataclass(slots=True)
class ScanErrorEntry:
    """Registra erros de leitura / permissão / possíveis bad blocks."""
    path: str
    error_type: str
    message: str
    timestamp: str


@dataclass(slots=True)
class YearActivityStats:
    """Estatísticas anuais de atividade de arquivos para a Linha do Tempo Forense."""
    year: int
    total_files: int = 0
    total_bytes: int = 0
    photos_count: int = 0
    videos_count: int = 0
    docs_count: int = 0
    critical_count: int = 0

    @property
    def formatted_size(self) -> str:
        return format_size(self.total_bytes)


class _XmlBatchTracker:
    """Acumula arquivos .xml por pasta para agrupar lotes fiscais sem poluir a lista individual."""
    __slots__ = ("folder_path", "count", "total_bytes", "latest_mtime", "sample_file")

    def __init__(self, folder_path: str) -> None:
        self.folder_path = folder_path
        self.count = 0
        self.total_bytes = 0
        self.latest_mtime = 0.0
        self.sample_file = ""


class DiskClassifier:
    """
    Classificador em tempo real chamado pelo motor de varredura para cada arquivo lido via os.scandir.
    """

    def __init__(self, root_path: str) -> None:
        self.root_path = os.path.abspath(root_path)
        self._hot_folders: Dict[str, HotFolderItem] = {}
        self._critical_items: List[CriticalFileItem] = []
        self._xml_batches: Dict[str, _XmlBatchTracker] = {}
        self._catalog: List[CatalogEntry] = []
        self._seen_critical_paths: set = set()
        self._years_distribution: Dict[int, YearActivityStats] = {}

        # Contadores rápidos para barra de status
        self.total_Photos: int = 0
        self.total_Videos: int = 0
        self.total_Docs: int = 0
        self.total_Critical: int = 0

    def _record_timeline(
        self,
        mtime: float,
        size_bytes: int,
        is_photo: bool = False,
        is_video: bool = False,
        is_doc: bool = False,
        is_critical: bool = False,
    ) -> None:
        """Registra a atividade no histograma anual filtrando datas razoáveis."""
        if mtime <= 0:
            return
        try:
            dt = datetime.datetime.fromtimestamp(mtime)
            year = dt.year
        except (ValueError, OSError, OverflowError):
            return

        # Sanity check: descarta datas corrompidas de MFT ou épocas irreais
        if not (1990 <= year <= 2040):
            return

        stat = self._years_distribution.get(year)
        if stat is None:
            stat = YearActivityStats(year=year)
            self._years_distribution[year] = stat

        stat.total_files += 1
        stat.total_bytes += size_bytes
        if is_photo:
            stat.photos_count += 1
        if is_video:
            stat.videos_count += 1
        if is_doc:
            stat.docs_count += 1
        if is_critical:
            stat.critical_count += 1

    def process_file(
        self,
        file_path: str,
        file_name: str,
        parent_dir: str,
        size_bytes: int,
        mtime: float,
    ) -> None:
        """
        Analisa apenas os metadados de um único arquivo e o classifica nas visões.
        Usa descarte prévio em O(1) de CPU para arquivos sem relevância.
        """
        name_lower = file_name.lower()

        # Extração rápida de extensão
        if name_lower.endswith(".tar.gz"):
            ext = ".tar.gz"
        else:
            dot_idx = name_lower.rfind(".")
            ext = name_lower[dot_idx:] if dot_idx != -1 else ""

        # FAST PATH: Descarta imediatamente arquivos irrelevantes
        parent_lower = parent_dir.lower()
        if not is_file_potentially_relevant(name_lower, ext):
            # Checagem residual caso a pasta em si seja do IRPF/RFB
            if not any(kw in parent_lower for kw in CRITICAL_IRPF_DIR_KEYWORDS):
                return

        is_relevant_for_catalog = False
        catalog_category = "Outro"

        # ----------------------------------------------------------------------
        # 1. VISÃO 1: PASTAS QUENTES (Mídia e Documentos Comuns com filtro anti-lixo)
        # ----------------------------------------------------------------------
        is_photo = ext in PHOTO_EXTENSIONS and size_bytes >= MIN_PHOTO_SIZE_BYTES
        is_video = ext in VIDEO_EXTENSIONS and size_bytes >= MIN_VIDEO_SIZE_BYTES
        is_doc = ext in DOC_EXTENSIONS and size_bytes > 0

        if is_photo or is_video or is_doc:
            folder_item = self._hot_folders.get(parent_dir)
            if folder_item is None:
                folder_item = HotFolderItem(folder_path=parent_dir)
                self._hot_folders[parent_dir] = folder_item

            if is_photo:
                folder_item.photos_count += 1
                self.total_Photos += 1
                catalog_category = "Foto"
            elif is_video:
                folder_item.videos_count += 1
                self.total_Videos += 1
                catalog_category = "Vídeo"
            elif is_doc:
                folder_item.docs_count += 1
                self.total_Docs += 1
                catalog_category = "Documento"

            folder_item.total_bytes += size_bytes
            if mtime > folder_item.latest_mtime:
                folder_item.latest_mtime = mtime

            is_relevant_for_catalog = True
            self._record_timeline(
                mtime=mtime,
                size_bytes=size_bytes,
                is_photo=is_photo,
                is_video=is_video,
                is_doc=is_doc,
                is_critical=False,
            )

        # ----------------------------------------------------------------------
        # 2. VISÃO 2: AGULHAS NO PALHEIRO (Arquivos Críticos Isolados)
        # ----------------------------------------------------------------------
        crit_match = self._check_critical_rules(
            file_path=file_path,
            file_name=file_name,
            name_lower=name_lower,
            parent_dir=parent_dir,
            parent_lower=parent_lower,
            ext=ext,
            size_bytes=size_bytes,
            mtime=mtime,
        )
        if crit_match is not None and file_path not in self._seen_critical_paths:
            self._seen_critical_paths.add(file_path)
            self._critical_items.append(crit_match)
            self.total_Critical += 1
            is_relevant_for_catalog = True
            catalog_category = crit_match.tag_label.strip("[]")
            self._record_timeline(
                mtime=mtime,
                size_bytes=size_bytes,
                is_photo=False,
                is_video=False,
                is_doc=False,
                is_critical=True,
            )

        # ----------------------------------------------------------------------
        # 3. CATÁLOGO PESQUISÁVEL (Limitado a MAX_CATALOG_FILES)
        # ----------------------------------------------------------------------
        if is_relevant_for_catalog and len(self._catalog) < MAX_CATALOG_FILES:
            try:
                rel = os.path.relpath(file_path, self.root_path)
            except ValueError:
                rel = file_path
            self._catalog.append(
                CatalogEntry(
                    rel_path=rel,
                    name=file_name,
                    category=catalog_category,
                    size_bytes=size_bytes,
                    mtime=mtime,
                )
            )

    def _check_critical_rules(
        self,
        file_path: str,
        file_name: str,
        name_lower: str,
        parent_dir: str,
        parent_lower: str,
        ext: str,
        size_bytes: int,
        mtime: float,
    ) -> Optional[CriticalFileItem]:
        """Verifica se o arquivo se enquadra em alguma regra de Agulha no Palheiro."""

        # 1. Criptomoedas, Carteiras & Keystores (Prioridade máxima de valor em sucata)
        if name_lower in CRITICAL_CRYPTO_FILENAMES or ext in CRITICAL_CRYPTO_EXTENSIONS or name_lower.startswith("utc--"):
            tag = "[Cripto Wallet]"
            if name_lower.startswith("utc--"):
                tag = "[Keystore ETH]"
            elif "sparrow" in ext or "sparrow" in name_lower:
                tag = "[Sparrow Wallet]"
            elif ext == ".keys" or "monero" in name_lower:
                tag = "[Monero Wallet]"
            elif "wasabi" in name_lower:
                tag = "[Wasabi Wallet]"
            elif "electrum" in name_lower:
                tag = "[Electrum Wallet]"
            elif "wallet.dat" in name_lower:
                tag = "[Bitcoin Core Dat]"
            elif name_lower.startswith("seed") or "palavras" in name_lower or "mnemonic" in name_lower:
                tag = "[Seed/Palavras]"

            return CriticalFileItem(
                name=file_name,
                full_path=file_path,
                category_key="CRYPTO_WALLETS",
                tag_label=tag,
                size_bytes=size_bytes,
                mtime=mtime,
                matched_reason="Arquivo de carteira / chaves de criptomoedas",
            )

        # 1.1 Verificador ultraleve de Frases BIP-39 em textos leves (<32 KB) com palavras suspeitas
        if ext in (".txt", ".rtf", ".note", ".md", "") and 25 <= size_bytes <= 32_768:
            suspect_terms = (
                "seed", "frase", "palavra", "recupera", "bip39", "mnemonic",
                "carteira", "wallet", "crypto", "btc", "segredo", "secret", "passphrase",
            )
            immediate_folder = os.path.basename(parent_lower)
            if any(t in name_lower or t in immediate_folder for t in suspect_terms):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        sample = f.read(2048)
                    words_count = detect_bip39_seed(sample)
                    if words_count:
                        return CriticalFileItem(
                            name=file_name,
                            full_path=file_path,
                            category_key="CRYPTO_WALLETS",
                            tag_label=f"[Seed BIP-39 ({words_count}w)]",
                            size_bytes=size_bytes,
                            mtime=mtime,
                            matched_reason=f"Frase mnemônica BIP-39 ({words_count} palavras de recuperação cripto)",
                        )
                except OSError:
                    pass

        # 2. Engenharia / Arquitetura (CAD / 3D)
        if ext in CRITICAL_CAD_EXTENSIONS:
            tag = f"[CAD {ext[1:].upper()}]" if ext in (".dwg", ".dxf", ".rvt", ".skp") else f"[3D {ext[1:].upper()}]"
            return CriticalFileItem(
                name=file_name,
                full_path=file_path,
                category_key="CAD_DESIGN",
                tag_label=tag,
                size_bytes=size_bytes,
                mtime=mtime,
                matched_reason="Projeto de Engenharia / Arquitetura / CAD",
            )

        # 3. Design / Gráfica Profissional
        if ext in CRITICAL_DESIGN_EXTENSIONS:
            tag = f"[Design {ext[1:].upper()}]"
            return CriticalFileItem(
                name=file_name,
                full_path=file_path,
                category_key="CAD_DESIGN",
                tag_label=tag,
                size_bytes=size_bytes,
                mtime=mtime,
                matched_reason="Arquivo de Design / Gráfica / Projeto",
            )

        # 4. E-mails e Mensagens (.pst, .ost, msgstore.db*)
        if ext in CRITICAL_EMAIL_EXTENSIONS or name_lower.startswith("msgstore.db"):
            tag = "[WhatsApp DB]" if name_lower.startswith("msgstore.db") else "[Outlook PST/OST]"
            return CriticalFileItem(
                name=file_name,
                full_path=file_path,
                category_key="EMAIL_MSG",
                tag_label=tag,
                size_bytes=size_bytes,
                mtime=mtime,
                matched_reason="Base de e-mails/mensagens",
            )

        # 5. Certificados Digitais e Cofres de Chaves (.pfx, .p12, .pem, .key, .kdbx)
        if ext in CRITICAL_CERT_EXTENSIONS:
            tag = "[KeePass KDBX]" if ext == ".kdbx" else "[Certificado/Chave]"
            return CriticalFileItem(
                name=file_name,
                full_path=file_path,
                category_key="CERT_KEYS",
                tag_label=tag,
                size_bytes=size_bytes,
                mtime=mtime,
                matched_reason=f"Extensão de segurança ({ext})",
            )

        # 6. Imposto de Renda / Receita Federal (.dec, .rec, .dbk ou pastas RFB/IRPF)
        if ext in CRITICAL_IRPF_EXTENSIONS or any(kw in parent_lower for kw in CRITICAL_IRPF_DIR_KEYWORDS):
            if ext not in (".exe", ".dll", ".jar", ".png", ".gif", ".ico", ".properties"):
                return CriticalFileItem(
                    name=file_name,
                    full_path=file_path,
                    category_key="IRPF_FISCAL",
                    tag_label="[IRPF / Receita]",
                    size_bytes=size_bytes,
                    mtime=mtime,
                    matched_reason="Declaração/Recibo IRPF",
                )

        # 7. Bancos de Dados e Sistemas ERP/PDV
        if ext in CRITICAL_DB_EXTENSIONS:
            return CriticalFileItem(
                name=file_name,
                full_path=file_path,
                category_key="DB_ERP",
                tag_label=f"[Banco {ext.upper()}]",
                size_bytes=size_bytes,
                mtime=mtime,
                matched_reason=f"Banco de dados ({ext})",
            )

        # 8. Notas Fiscais (.xml agrupados por pasta para não poluir a lista individual)
        if ext == CRITICAL_XML_EXTENSION:
            tracker = self._xml_batches.get(parent_dir)
            if tracker is None:
                tracker = _XmlBatchTracker(folder_path=parent_dir)
                self._xml_batches[parent_dir] = tracker
                self.total_Critical += 1
            tracker.count += 1
            tracker.total_bytes += size_bytes
            if mtime > tracker.latest_mtime:
                tracker.latest_mtime = mtime
            if not tracker.sample_file:
                tracker.sample_file = file_path
            self._record_timeline(
                mtime=mtime,
                size_bytes=size_bytes,
                is_photo=False,
                is_video=False,
                is_doc=False,
                is_critical=True,
            )
            return None

        # 9. Compactados / Imagens de Disco / Backups VM
        if ext in CRITICAL_ARCHIVE_EXTENSIONS or ext == ".tar.gz":
            tag = f"[Imagem VM {ext.upper()}]" if ext in (".vhd", ".vhdx", ".vmdk", ".ova", ".ovf", ".qcow2") else (
                f"[Backup {ext.upper()}]" if ext in (".tib", ".vbk", ".gho") else f"[Arquivo {ext.upper()}]"
            )
            return CriticalFileItem(
                name=file_name,
                full_path=file_path,
                category_key="ARCHIVES",
                tag_label=tag,
                size_bytes=size_bytes,
                mtime=mtime,
                matched_reason="Compactado / Imagem de Disco / Backup",
            )

        # 10. Caçador de Palavras-Chave no nome do arquivo ou pasta imediata
        immediate_folder_name = os.path.basename(parent_lower)
        for kw in HUNTER_KEYWORDS:
            if kw in name_lower or kw in immediate_folder_name:
                return CriticalFileItem(
                    name=file_name,
                    full_path=file_path,
                    category_key="KEYWORDS",
                    tag_label=f"[Keyword: {kw}]",
                    size_bytes=size_bytes,
                    mtime=mtime,
                    matched_reason=f"Palavra-chave '{kw}' detectada",
                )

        return None

    def add_targeted_critical_item(
        self,
        name: str,
        full_path: str,
        category_key: str,
        tag_label: str,
        size_bytes: int,
        mtime: float,
        matched_reason: str,
    ) -> None:
        """Adiciona um item crítico descoberto via inspeção cirúrgica direcionada (ex: navegadores/carteiras)."""
        if full_path in self._seen_critical_paths:
            return
        self._seen_critical_paths.add(full_path)

        item = CriticalFileItem(
            name=name,
            full_path=full_path,
            category_key=category_key,
            tag_label=tag_label,
            size_bytes=size_bytes,
            mtime=mtime,
            matched_reason=matched_reason,
        )
        self._critical_items.append(item)
        self.total_Critical += 1
        self._record_timeline(
            mtime=mtime,
            size_bytes=size_bytes,
            is_photo=False,
            is_video=False,
            is_doc=False,
            is_critical=True,
        )

        if len(self._catalog) < MAX_CATALOG_FILES:
            try:
                rel = os.path.relpath(full_path, self.root_path)
            except ValueError:
                rel = full_path
            self._catalog.append(
                CatalogEntry(
                    rel_path=rel,
                    name=name,
                    category=tag_label.strip("[]"),
                    size_bytes=size_bytes,
                    mtime=mtime,
                )
            )

    def get_sorted_hot_folders(self) -> List[HotFolderItem]:
        """Retorna as Pastas Quentes ordenadas por relevância (quantidade de arquivos / tamanho)."""
        folders = list(self._hot_folders.values())
        folders.sort(key=lambda item: (item.relevance_score, item.total_bytes), reverse=True)
        return folders

    def get_all_critical_items(self) -> List[CriticalFileItem]:
        """
        Retorna a lista consolidada de Arquivos Críticos + Lotes de XML Fiscal agrupados por pasta.
        """
        combined: List[CriticalFileItem] = list(self._critical_items)

        for folder_path, tracker in self._xml_batches.items():
            folder_display = os.path.basename(folder_path.rstrip("\\/")) or folder_path
            combined.append(
                CriticalFileItem(
                    name=f"Lote com {tracker.count} arquivo(s) .XML em '{folder_display}'",
                    full_path=tracker.sample_file or folder_path,
                    category_key="IRPF_FISCAL",
                    tag_label=f"[Lote XML ({tracker.count})]",
                    size_bytes=tracker.total_bytes,
                    mtime=tracker.latest_mtime,
                    matched_reason=f"Agrupamento de {tracker.count} XMLs na pasta",
                    is_directory_batch=True,
                )
            )

        combined.sort(
            key=lambda x: (
                FORENSIC_CATEGORY_PRIORITY.get(x.category_key, 10),
                x.mtime,
                x.size_bytes,
            ),
            reverse=True,
        )
        return combined

    def get_catalog_entries(self) -> List[CatalogEntry]:
        """Retorna os arquivos catalogados para o relatório HTML pesquisável."""
        return self._catalog

    def get_timeline_stats(self) -> List[YearActivityStats]:
        """Retorna as estatísticas de atividade ordenadas por ano crescente."""
        return [self._years_distribution[y] for y in sorted(self._years_distribution.keys())]

    def get_timeline_summary(self) -> Tuple[Optional[int], Optional[int], Optional[YearActivityStats], str]:
        """
        Retorna (ano_inicio, ano_fim, pico_stats, texto_resumo).
        """
        if not self._years_distribution:
            return (None, None, None, "Sem dados de linha do tempo registrados.")

        sorted_years = sorted(self._years_distribution.keys())
        start_year = sorted_years[0]
        end_year = sorted_years[-1]

        peak_stats = max(self._years_distribution.values(), key=lambda s: s.total_files)

        span_years = (end_year - start_year) + 1
        summary = (
            f"Atividade detectada entre {start_year} e {end_year} ({span_years} ano{'s' if span_years > 1 else ''}). "
            f"Pico de atividade em {peak_stats.year} com {peak_stats.total_files:,} arquivos relevantes ({peak_stats.formatted_size})."
        )
        return (start_year, end_year, peak_stats, summary)
