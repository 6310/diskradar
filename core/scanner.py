"""
Motor de Varredura Assíncrono (Anti-Travamento) do Geio DiskRadar.
Executa os.scandir() recursivo em uma Thread separada, lendo exclusivamente metadados (stat),
aplicando a Blocklist de diretórios case-insensitive e isolando falhas de leitura (Bad Blocks / Permissão).

Blindado para Windows 10/11:
- Prevenção contra loops infinitos de recursão em NTFS Junctions / Reparse Points (ex: Application Data)
- Suporte a caminhos longos (MAX_PATH > 260 caracteres) via prefixo estendido \\?\
- Sondagem cirúrgica direcionada de perfis de navegadores e carteiras Web3/Cripto.
"""

import datetime
import os
import queue
import sys
import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from core.classifier import (
    CatalogEntry,
    CriticalFileItem,
    DiskClassifier,
    HotFolderItem,
    ScanErrorEntry,
    YearActivityStats,
)
from core.rules import DIR_BLOCKLIST, IGNORED_USERS, WEB3_EXTENSION_IDS


MAX_DIR_DEPTH: int = 35
CIRCUIT_BREAKER_MAX_ERRORS: int = 10
MAX_LIVE_ERRORS: int = 2000


def to_extended_path(path: str) -> str:
    """
    No Windows, converte para o prefixo estendido \\?\\ para contornar o limite MAX_PATH (260 caracteres).
    Mantém o caminho inalterado em Linux/macOS ou se já for estendido/caminho de rede UNC.
    """
    if sys.platform == "win32" and path:
        norm = os.path.normpath(os.path.abspath(path))
        if not norm.startswith("\\\\?\\") and not norm.startswith("\\\\"):
            return f"\\\\?\\{norm}"
    return path


def strip_extended_prefix(path: str) -> str:
    """Remove o prefixo \\?\\ para manter caminhos limpos e legíveis para Explorer, logs e GUI."""
    if path.startswith("\\\\?\\"):
        return path[4:]
    return path


@dataclass
class ScanResult:
    """Resultado consolidado de uma varredura Read-Only (completa ou interrompida)."""
    root_path: str
    was_cancelled: bool = False
    is_device_unplugged: bool = False
    elapsed_seconds: float = 0.0
    scanned_files: int = 0
    scanned_dirs: int = 0
    total_photos: int = 0
    total_videos: int = 0
    total_docs: int = 0
    total_errors_count: int = 0
    hot_folders: List[HotFolderItem] = field(default_factory=list)
    critical_items: List[CriticalFileItem] = field(default_factory=list)
    catalog_entries: List[CatalogEntry] = field(default_factory=list)
    errors: List[ScanErrorEntry] = field(default_factory=list)
    timeline_stats: List[YearActivityStats] = field(default_factory=list)
    peak_year: Optional[int] = None
    timeline_summary: str = ""


class AsyncDiskScanner:
    """
    Gerencia a thread de varredura Read-Only e envia atualizações para a GUI via queue.Queue.
    """

    def __init__(self, target_path: str, event_queue: queue.Queue) -> None:
        if target_path.lower().startswith(r"\\.\physicaldrive") or target_path.startswith("/dev/"):
            self.target_path = target_path
        else:
            self.target_path = os.path.abspath(target_path)
        self.event_queue = event_queue
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.is_running: bool = False
        self.is_device_unplugged: bool = False
        self._total_errors_count: int = 0
        self._live_classifier: Optional[DiskClassifier] = None
        self._live_errors: List[ScanErrorEntry] = []
        self._live_files: int = 0
        self._live_dirs: int = 0
        self._live_current_dir: str = ""
        self._live_start_time: float = 0.0

    def get_live_snapshot(self) -> Optional[ScanResult]:
        """Retorna um snapshot seguro do estado parcial da varredura em andamento."""
        clf = self._live_classifier
        if clf is None:
            return None
        elapsed = (time.monotonic() - self._live_start_time) if self._live_start_time > 0 else 0.0
        timeline_stats = clf.get_timeline_stats()
        _s, _e, peak_stats, timeline_summary = clf.get_timeline_summary()
        return ScanResult(
            root_path=self.target_path,
            was_cancelled=self._stop_event.is_set(),
            is_device_unplugged=self.is_device_unplugged,
            elapsed_seconds=elapsed,
            scanned_files=self._live_files,
            scanned_dirs=self._live_dirs,
            total_photos=clf.total_Photos,
            total_videos=clf.total_Videos,
            total_docs=clf.total_Docs,
            total_errors_count=self._total_errors_count,
            hot_folders=clf.get_sorted_hot_folders()[:200],
            critical_items=clf.get_all_critical_items()[:200],
            catalog_entries=[],
            errors=list(self._live_errors[-100:]),
            timeline_stats=timeline_stats,
            peak_year=peak_stats.year if peak_stats else None,
            timeline_summary=timeline_summary,
        )

    def start(self) -> None:
        """Inicia a varredura em background."""
        if self.is_running:
            return
        self._stop_event.clear()
        self.is_running = True
        self._thread = threading.Thread(target=self._run_scan, name="DiskRadarScannerThread", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Solicita o cancelamento imediato da varredura."""
        self._stop_event.set()

    def _run_scan(self) -> None:
        start_time = time.monotonic()
        self._live_start_time = start_time
        classifier = DiskClassifier(self.target_path)
        errors: List[ScanErrorEntry] = []
        self._live_classifier = classifier
        self._live_errors = errors
        self._live_files = 0
        self._live_dirs = 0

        scanned_files = 0
        scanned_dirs = 0
        last_ui_update = start_time

        self.event_queue.put({
            "type": "SCAN_STARTED",
            "root_path": self.target_path,
        })

        # BLINDAGEM DISCOS FÍSICOS BRUTOS / RAW
        if self.target_path.lower().startswith(r"\\.\physicaldrive") or self.target_path.startswith("/dev/"):
            self._record_error(
                errors,
                self.target_path,
                OSError(
                    "O dispositivo selecionado é um disco físico RAW sem sistema de arquivos montado. "
                    "A varredura por pastas não é aplicável. "
                    "Utilize o Inspetor Hexadecimal para leitura e auditoria direta de setores LBA."
                ),
            )
            self.is_running = False
            result = ScanResult(
                root_path=self.target_path,
                was_cancelled=False,
                elapsed_seconds=0.1,
                scanned_files=0,
                scanned_dirs=0,
                total_errors_count=1,
                errors=errors,
            )
            self.event_queue.put({"type": "SCAN_FINISHED", "result": result})
            return

        # ======================================================================
        # FASE 0: SONDAGEM CIRÚRGICA DE NAVEGADORES, SESSÕES E CARTEIRAS CRIPTO
        # Inspeciona caminhos exatos em AppData sem varrer 50.000 caches de lixo.
        # ======================================================================
        try:
            self._probe_browser_and_crypto_targets(self.target_path, classifier, errors)
        except Exception as exc:
            self._record_error(errors, self.target_path, exc)

        # Atualiza a UI imediatamente com os achados de alta prioridade
        self.event_queue.put({
            "type": "SCAN_PROGRESS",
            "current_dir": "Iniciando varredura geral do disco...",
            "scanned_files": scanned_files,
            "scanned_dirs": scanned_dirs,
            "hot_folders_count": len(classifier._hot_folders),
            "critical_count": classifier.total_Critical,
            "errors_count": len(errors),
            "elapsed": time.monotonic() - start_time,
        })

        # ======================================================================
        # FASE 1: VARREDURA GERAL READ-ONLY COM PROTEÇÃO ANTI-TRAVAMENTO
        # (Circuit Breaker, Pacing de I/O, Teto de Profundidade MAX_DIR_DEPTH)
        # ======================================================================
        root_extended = to_extended_path(self.target_path)
        dir_stack: List[Tuple[str, int]] = [(root_extended, 0)]

        while dir_stack and not self._stop_event.is_set():
            current_dir, depth = dir_stack.pop()
            scanned_dirs += 1
            self._live_dirs = scanned_dirs
            folder_io_errors = 0
            is_folder_circuit_broken = False

            now = time.monotonic()
            if now - last_ui_update >= 0.18:
                last_ui_update = now
                display_dir = strip_extended_prefix(current_dir)
                self._live_current_dir = display_dir
                self.event_queue.put({
                    "type": "SCAN_PROGRESS",
                    "current_dir": display_dir,
                    "scanned_files": scanned_files,
                    "scanned_dirs": scanned_dirs,
                    "hot_folders_count": len(classifier._hot_folders),
                    "critical_count": classifier.total_Critical,
                    "errors_count": self._total_errors_count,
                    "elapsed": now - start_time,
                })

            try:
                scandir_iter = os.scandir(current_dir)
            except (PermissionError, FileNotFoundError, OSError) as exc:
                self._record_error(errors, strip_extended_prefix(current_dir), exc)
                if self._is_surprise_unplug(exc):
                    self._handle_unplug(errors, current_dir)
                    break
                continue

            with scandir_iter as entries:
                while not self._stop_event.is_set() and not is_folder_circuit_broken:
                    try:
                        entry = next(entries)
                    except StopIteration:
                        break
                    except (PermissionError, FileNotFoundError, OSError) as exc:
                        folder_io_errors += 1
                        self._record_error(errors, strip_extended_prefix(current_dir), exc)
                        if self._is_surprise_unplug(exc):
                            self._handle_unplug(errors, current_dir)
                            break
                        if folder_io_errors >= CIRCUIT_BREAKER_MAX_ERRORS:
                            is_folder_circuit_broken = True
                            self._record_circuit_breaker(errors, current_dir)
                        break

                    try:
                        entry_name = entry.name
                        entry_name_lower = entry_name.lower()

                        # Identifica diretórios e Symlinks / Junctions NTFS
                        try:
                            is_dir = entry.is_dir(follow_symlinks=False)
                            is_symlink = entry.is_symlink()
                        except OSError as exc:
                            folder_io_errors += 1
                            if folder_io_errors >= CIRCUIT_BREAKER_MAX_ERRORS:
                                is_folder_circuit_broken = True
                                self._record_circuit_breaker(errors, current_dir)
                            continue

                        # BLINDAGEM WINDOWS: Bloqueia Reparse Points / Junctions (ex: Application Data)
                        # e teto de profundidade (MAX_DIR_DEPTH), evitando loops infinitos!
                        if is_dir and not is_symlink:
                            if entry_name_lower in DIR_BLOCKLIST:
                                continue
                            if depth + 1 <= MAX_DIR_DEPTH:
                                dir_stack.append((entry.path, depth + 1))
                        elif entry.is_file(follow_symlinks=False):
                            scanned_files += 1
                            self._live_files = scanned_files
                            st = entry.stat(follow_symlinks=False)

                            clean_file_path = strip_extended_prefix(entry.path)
                            clean_parent_dir = strip_extended_prefix(current_dir)

                            classifier.process_file(
                                file_path=clean_file_path,
                                file_name=entry_name,
                                parent_dir=clean_parent_dir,
                                size_bytes=st.st_size,
                                mtime=st.st_mtime,
                            )

                            # Pacing cooperativo anti-travamento de máquina: 1ms a cada 1.000 nós
                            if scanned_files % 1000 == 0:
                                time.sleep(0.001)

                            if scanned_files % 1200 == 0:
                                now_inner = time.monotonic()
                                if now_inner - last_ui_update >= 0.18:
                                    last_ui_update = now_inner
                                    display_dir = strip_extended_prefix(current_dir)
                                    self.event_queue.put({
                                        "type": "SCAN_PROGRESS",
                                        "current_dir": display_dir,
                                        "scanned_files": scanned_files,
                                        "scanned_dirs": scanned_dirs,
                                        "hot_folders_count": len(classifier._hot_folders),
                                        "critical_count": classifier.total_Critical,
                                        "errors_count": self._total_errors_count,
                                        "elapsed": now_inner - start_time,
                                    })
                    except (PermissionError, FileNotFoundError, OSError) as exc:
                        folder_io_errors += 1
                        err_path = getattr(entry, "path", current_dir)
                        self._record_error(errors, strip_extended_prefix(err_path), exc)
                        if self._is_surprise_unplug(exc):
                            self._handle_unplug(errors, current_dir)
                            break
                        if folder_io_errors >= CIRCUIT_BREAKER_MAX_ERRORS:
                            is_folder_circuit_broken = True
                            self._record_circuit_breaker(errors, current_dir)
                            break
                        continue

        elapsed = time.monotonic() - start_time
        self.is_running = False

        timeline_stats = classifier.get_timeline_stats()
        _start_yr, _end_yr, peak_stats, timeline_summary = classifier.get_timeline_summary()
        peak_year = peak_stats.year if peak_stats else None

        result = ScanResult(
            root_path=self.target_path,
            was_cancelled=self._stop_event.is_set(),
            is_device_unplugged=self.is_device_unplugged,
            elapsed_seconds=elapsed,
            scanned_files=scanned_files,
            scanned_dirs=scanned_dirs,
            total_photos=classifier.total_Photos,
            total_videos=classifier.total_Videos,
            total_docs=classifier.total_Docs,
            total_errors_count=self._total_errors_count,
            hot_folders=classifier.get_sorted_hot_folders(),
            critical_items=classifier.get_all_critical_items(),
            catalog_entries=classifier.get_catalog_entries(),
            errors=errors,
            timeline_stats=timeline_stats,
            peak_year=peak_year,
            timeline_summary=timeline_summary,
        )

        self.event_queue.put({
            "type": "SCAN_FINISHED",
            "result": result,
        })

    def _probe_browser_and_crypto_targets(
        self,
        root_path: str,
        classifier: DiskClassifier,
        errors: List[ScanErrorEntry],
    ) -> None:
        """
        Sondagem cirúrgica: localiza perfis de navegadores e carteiras sem varrer
        pastas gigantescas de cache.
        """
        candidate_user_dirs = [
            os.path.join(root_path, "Users"),
            os.path.join(root_path, "Usuários"),
            os.path.join(root_path, "Documents and Settings"),
            os.path.join(root_path, "home"),
        ]
        user_profiles: List[str] = []

        base_name = os.path.basename(os.path.normpath(root_path)).lower()
        if base_name in ("users", "usuários", "home", "documents and settings"):
            candidate_user_dirs.insert(0, root_path)
        else:
            if os.path.isdir(os.path.join(root_path, "AppData")):
                user_profiles.append(root_path)

        for u_dir in candidate_user_dirs:
            if not os.path.isdir(u_dir):
                continue
            try:
                with os.scandir(u_dir) as entries:
                    for entry in entries:
                        try:
                            # Bloqueia junctions em Users (ex: Default User junction)
                            if entry.is_dir(follow_symlinks=False) and not entry.is_symlink():
                                uname = entry.name.lower()
                                if uname not in IGNORED_USERS and not uname.startswith("."):
                                    user_profiles.append(entry.path)
                        except OSError:
                            continue
            except OSError:
                continue

        for profile in user_profiles:
            try:
                self._inspect_single_user_profile(profile, classifier, errors)
            except Exception as exc:
                self._record_error(errors, profile, exc)

    def _inspect_single_user_profile(
        self,
        profile_path: str,
        classifier: DiskClassifier,
        errors: List[ScanErrorEntry],
    ) -> None:
        username = os.path.basename(profile_path)
        appdata_local = os.path.join(profile_path, "AppData", "Local")
        appdata_roaming = os.path.join(profile_path, "AppData", "Roaming")

        # 1. Chromium based (Google Chrome, Edge, Brave)
        chromium_targets = [
            ("Google Chrome", os.path.join(appdata_local, "Google", "Chrome", "User Data")),
            ("Microsoft Edge", os.path.join(appdata_local, "Microsoft", "Edge", "User Data")),
            ("Brave Browser", os.path.join(appdata_local, "BraveSoftware", "Brave-Browser", "User Data")),
        ]

        for b_name, b_user_data in chromium_targets:
            if not os.path.isdir(b_user_data):
                continue

            profile_dirs = ["Default"]
            try:
                with os.scandir(b_user_data) as entries:
                    for entry in entries:
                        if entry.is_dir(follow_symlinks=False) and not entry.is_symlink() and entry.name.startswith("Profile "):
                            profile_dirs.append(entry.name)
            except OSError:
                pass

            for p_dir in profile_dirs:
                p_full = os.path.join(b_user_data, p_dir)
                if not os.path.isdir(p_full):
                    continue

                key_files = [
                    ("Login Data", f"[{b_name} Senhas]", "Banco SQLite com senhas salvas"),
                    ("Web Data", f"[{b_name} Autofill]", "Preenchimento automático e cartões"),
                    ("Bookmarks", f"[{b_name} Favoritos]", "Lista de favoritos JSON"),
                    ("History", f"[{b_name} Histórico]", "Histórico de navegação"),
                ]
                for k_file, tag, reason in key_files:
                    f_path = os.path.join(p_full, k_file)
                    if os.path.isfile(f_path):
                        try:
                            st = os.stat(f_path)
                            classifier.add_targeted_critical_item(
                                name=f"{b_name} ({username}/{p_dir}) - {k_file}",
                                full_path=f_path,
                                category_key="BROWSERS_CREDS",
                                tag_label=tag,
                                size_bytes=st.st_size,
                                mtime=st.st_mtime,
                                matched_reason=f"{reason} de {username}",
                            )
                        except OSError as exc:
                            self._record_error(errors, f_path, exc)

                ext_settings_dir = os.path.join(p_full, "Local Extension Settings")
                if os.path.isdir(ext_settings_dir):
                    try:
                        with os.scandir(ext_settings_dir) as ext_entries:
                            for ext_entry in ext_entries:
                                if ext_entry.is_dir(follow_symlinks=False) and not ext_entry.is_symlink():
                                    ext_id = ext_entry.name.lower()
                                    if ext_id in WEB3_EXTENSION_IDS:
                                        vault_name = WEB3_EXTENSION_IDS[ext_id]
                                        st = ext_entry.stat(follow_symlinks=False)
                                        classifier.add_targeted_critical_item(
                                            name=f"{vault_name} ({b_name} - {username})",
                                            full_path=ext_entry.path,
                                            category_key="CRYPTO_WALLETS",
                                            tag_label=f"[{vault_name}]",
                                            size_bytes=st.st_size,
                                            mtime=st.st_mtime,
                                            matched_reason=f"Cofre de extensão Web3 detectado em {b_name}",
                                        )
                    except OSError:
                        pass

        # 2. Opera / Opera GX (AppData/Roaming)
        opera_targets = [
            ("Opera Stable", os.path.join(appdata_roaming, "Opera Software", "Opera Stable")),
            ("Opera GX", os.path.join(appdata_roaming, "Opera Software", "Opera GX Stable")),
        ]
        for b_name, b_path in opera_targets:
            if not os.path.isdir(b_path):
                continue
            for k_file, tag in [
                ("Login Data", f"[{b_name} Senhas]"),
                ("Bookmarks", f"[{b_name} Favoritos]"),
                ("History", f"[{b_name} Histórico]"),
            ]:
                f_path = os.path.join(b_path, k_file)
                if os.path.isfile(f_path):
                    try:
                        st = os.stat(f_path)
                        classifier.add_targeted_critical_item(
                            name=f"{b_name} ({username}) - {k_file}",
                            full_path=f_path,
                            category_key="BROWSERS_CREDS",
                            tag_label=tag,
                            size_bytes=st.st_size,
                            mtime=st.st_mtime,
                            matched_reason=f"Dados do navegador {b_name}",
                        )
                    except OSError as exc:
                        self._record_error(errors, f_path, exc)

        # 3. Mozilla Firefox & Thunderbird (AppData/Roaming)
        moz_targets = [
            ("Firefox", os.path.join(appdata_roaming, "Mozilla", "Firefox", "Profiles")),
            ("Thunderbird", os.path.join(appdata_roaming, "Thunderbird", "Profiles")),
        ]
        for app_name, profiles_dir in moz_targets:
            if not os.path.isdir(profiles_dir):
                continue
            try:
                with os.scandir(profiles_dir) as prof_entries:
                    for entry in prof_entries:
                        if entry.is_dir(follow_symlinks=False) and not entry.is_symlink():
                            p_dir = entry.path
                            for f_name, tag_suffix in [
                                ("logins.json", "Senhas"),
                                ("key4.db", "Chave Mestra"),
                                ("places.sqlite", "Favoritos/Histórico"),
                            ]:
                                target_f = os.path.join(p_dir, f_name)
                                if os.path.isfile(target_f):
                                    try:
                                        st = os.stat(target_f)
                                        classifier.add_targeted_critical_item(
                                            name=f"{app_name} ({username}) - {f_name}",
                                            full_path=target_f,
                                            category_key="BROWSERS_CREDS",
                                            tag_label=f"[{app_name} {tag_suffix}]",
                                            size_bytes=st.st_size,
                                            mtime=st.st_mtime,
                                            matched_reason=f"Dados de perfil do {app_name}",
                                        )
                                    except OSError as exc:
                                        self._record_error(errors, target_f, exc)
            except OSError:
                pass

        # 4. Carteiras Desktop Cripto
        crypto_direct_paths = [
            ("Bitcoin Core", os.path.join(appdata_roaming, "Bitcoin", "wallet.dat")),
            ("Bitcoin Core (Home)", os.path.join(profile_path, ".bitcoin", "wallet.dat")),
            ("Dogecoin Core", os.path.join(appdata_roaming, "DogeCoin", "wallet.dat")),
            ("Litecoin Core", os.path.join(appdata_roaming, "Litecoin", "wallet.dat")),
            ("Exodus Vault", os.path.join(appdata_roaming, "Exodus", "exodus.wallet")),
        ]
        for w_label, c_path in crypto_direct_paths:
            if os.path.exists(c_path):
                try:
                    st = os.stat(c_path)
                    classifier.add_targeted_critical_item(
                        name=f"{w_label} ({username}) - {os.path.basename(c_path)}",
                        full_path=c_path,
                        category_key="CRYPTO_WALLETS",
                        tag_label="[Cripto Wallet]",
                        size_bytes=st.st_size,
                        mtime=st.st_mtime,
                        matched_reason=f"Carteira Desktop {w_label}",
                    )
                except OSError as exc:
                    self._record_error(errors, c_path, exc)

        for el_dir in [
            os.path.join(appdata_roaming, "Electrum", "wallets"),
            os.path.join(profile_path, ".electrum", "wallets"),
        ]:
            if os.path.isdir(el_dir):
                try:
                    with os.scandir(el_dir) as entries:
                        for entry in entries:
                            if entry.is_file(follow_symlinks=False):
                                st = entry.stat(follow_symlinks=False)
                                classifier.add_targeted_critical_item(
                                    name=f"Electrum Wallet ({username}) - {entry.name}",
                                    full_path=entry.path,
                                    category_key="CRYPTO_WALLETS",
                                    tag_label="[Electrum Wallet]",
                                    size_bytes=st.st_size,
                                    mtime=st.st_mtime,
                                    matched_reason=f"Arquivo de carteira Electrum de {username}",
                                )
                except OSError:
                    pass

        # Pastas de carteiras modernas (Sparrow, Wasabi, Monero, Daedalus)
        multi_wallet_folders = [
            ("Sparrow", os.path.join(appdata_roaming, "Sparrow", "wallets"), "[Sparrow Wallet]"),
            ("Sparrow (Home)", os.path.join(profile_path, ".sparrow", "wallets"), "[Sparrow Wallet]"),
            ("Wasabi", os.path.join(appdata_roaming, "WalletWasabi", "Client", "Wallets"), "[Wasabi Wallet]"),
            ("Monero", os.path.join(profile_path, "Documents", "Monero", "wallets"), "[Monero Wallet]"),
            ("Monero (Doc)", os.path.join(profile_path, "Documentos", "Monero", "wallets"), "[Monero Wallet]"),
            ("Daedalus", os.path.join(appdata_roaming, "Daedalus Mainnet", "wallets"), "[Daedalus Wallet]"),
        ]
        for w_app, w_folder, w_tag in multi_wallet_folders:
            if os.path.isdir(w_folder):
                try:
                    with os.scandir(w_folder) as entries:
                        for entry in entries:
                            if entry.is_file(follow_symlinks=False):
                                st = entry.stat(follow_symlinks=False)
                                classifier.add_targeted_critical_item(
                                    name=f"{w_app} ({username}) - {entry.name}",
                                    full_path=entry.path,
                                    category_key="CRYPTO_WALLETS",
                                    tag_label=w_tag,
                                    size_bytes=st.st_size,
                                    mtime=st.st_mtime,
                                    matched_reason=f"Arquivo de carteira {w_app} de {username}",
                                )
                except OSError:
                    pass

        # Aplicativos de Hardware Wallets / Cofres Desktop (Trezor, Ledger, Atomic)
        hw_suite_dirs = [
            ("Trezor Suite", os.path.join(appdata_roaming, "@trezor", "suite-desktop"), "[Trezor Suite]"),
            ("Ledger Live", os.path.join(appdata_roaming, "Ledger Live"), "[Ledger Live]"),
            ("Atomic Wallet", os.path.join(appdata_roaming, "atomic"), "[Atomic Wallet]"),
        ]
        for hw_label, hw_dir, hw_tag in hw_suite_dirs:
            if os.path.isdir(hw_dir):
                try:
                    st = os.stat(hw_dir)
                    classifier.add_targeted_critical_item(
                        name=f"{hw_label} ({username})",
                        full_path=hw_dir,
                        category_key="CRYPTO_WALLETS",
                        tag_label=hw_tag,
                        size_bytes=st.st_size,
                        mtime=st.st_mtime,
                        matched_reason=f"Dados de instalação e cofre local do {hw_label}",
                    )
                except OSError as exc:
                    self._record_error(errors, hw_dir, exc)

        eth_keystore_dir = os.path.join(appdata_roaming, "Ethereum", "keystore")
        if os.path.isdir(eth_keystore_dir):
            try:
                with os.scandir(eth_keystore_dir) as entries:
                    for entry in entries:
                        if entry.is_file(follow_symlinks=False):
                            st = entry.stat(follow_symlinks=False)
                            classifier.add_targeted_critical_item(
                                name=f"Ethereum Keystore ({username}) - {entry.name}",
                                full_path=entry.path,
                                category_key="CRYPTO_WALLETS",
                                tag_label="[Keystore ETH]",
                                size_bytes=st.st_size,
                                mtime=st.st_mtime,
                                matched_reason="Keystore UTC de Ethereum",
                            )
            except OSError:
                pass

    def _is_surprise_unplug(self, exc: BaseException) -> bool:
        """Identifica desconexão abrupta de hardware USB/SATA."""
        winerror = getattr(exc, "winerror", None)
        if winerror in (21, 1167, 433):  # ERROR_NOT_READY, ERROR_DEVICE_NOT_CONNECTED, ERROR_DEVICE_UNREACHABLE
            return True
        msg = str(exc).lower()
        if "device not ready" in msg or "device is not connected" in msg or "device unreachable" in msg:
            return True
        return False

    def _handle_unplug(self, errors: List[ScanErrorEntry], path: str) -> None:
        """Trata desconexão abrupta com segurança e preservação de achados."""
        self.is_device_unplugged = True
        self._record_error(errors, path, OSError(1167, "[DESCONEXÃO ABRUPTA] O dispositivo de armazenamento foi desconectado pelo hardware."))
        self.event_queue.put({
            "type": "DEVICE_UNPLUGGED",
            "path": strip_extended_prefix(path),
            "message": "Dispositivo removido ou desconectado durante a varredura.",
        })
        self._stop_event.set()

    def _record_circuit_breaker(self, errors: List[ScanErrorEntry], folder_path: str) -> None:
        """Desarma o circuito para uma subpasta repleta de erros físicos de hardware."""
        clean = strip_extended_prefix(folder_path)
        self._record_error(errors, clean, OSError(1117, f"[CIRCUIT BREAKER] Subpasta isolada e ignorada após {CIRCUIT_BREAKER_MAX_ERRORS} erros consecutivos de hardware/I/O."))

    def _record_error(self, errors: List[ScanErrorEntry], path: str, exc: BaseException) -> None:
        """Registra erro sem vazar memória RAM, limitando o catálogo em memória e isolando Bad Blocks."""
        self._total_errors_count += 1
        err_type = type(exc).__name__
        winerror = getattr(exc, "winerror", None)
        errno_val = getattr(exc, "errno", None)

        details = str(exc)
        if winerror in (23, 1117) or errno_val == 5 or "[CIRCUIT BREAKER]" in details:
            err_type = f"BAD BLOCK / ERRO FÍSICO I/O ({err_type})"

        errors.append(
            ScanErrorEntry(
                path=strip_extended_prefix(path),
                error_type=err_type,
                message=details,
                timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
            )
        )
        if len(errors) > MAX_LIVE_ERRORS:
            errors.pop(0)
