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
from typing import List, Optional

from core.classifier import (
    CatalogEntry,
    CriticalFileItem,
    DiskClassifier,
    HotFolderItem,
    ScanErrorEntry,
    YearActivityStats,
)
from core.rules import DIR_BLOCKLIST, IGNORED_USERS, WEB3_EXTENSION_IDS


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
    elapsed_seconds: float = 0.0
    scanned_files: int = 0
    scanned_dirs: int = 0
    total_photos: int = 0
    total_videos: int = 0
    total_docs: int = 0
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
        self.target_path = os.path.abspath(target_path)
        self.event_queue = event_queue
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.is_running: bool = False

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
        classifier = DiskClassifier(self.target_path)
        errors: List[ScanErrorEntry] = []

        scanned_files = 0
        scanned_dirs = 0
        last_ui_update = start_time

        self.event_queue.put({
            "type": "SCAN_STARTED",
            "root_path": self.target_path,
        })

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
        # FASE 1: VARREDURA GERAL READ-ONLY COM PROTEÇÃO CONTRA JUNCTIONS E MAX_PATH
        # ======================================================================
        # Utiliza o prefixo estendido \\?\ no Windows para não quebrar em pastas >260 chars
        root_extended = to_extended_path(self.target_path)
        dir_stack: List[str] = [root_extended]

        while dir_stack and not self._stop_event.is_set():
            current_dir = dir_stack.pop()
            scanned_dirs += 1

            now = time.monotonic()
            if now - last_ui_update >= 0.18:
                last_ui_update = now
                display_dir = strip_extended_prefix(current_dir)
                self.event_queue.put({
                    "type": "SCAN_PROGRESS",
                    "current_dir": display_dir,
                    "scanned_files": scanned_files,
                    "scanned_dirs": scanned_dirs,
                    "hot_folders_count": len(classifier._hot_folders),
                    "critical_count": classifier.total_Critical,
                    "errors_count": len(errors),
                    "elapsed": now - start_time,
                })

            try:
                scandir_iter = os.scandir(current_dir)
            except (PermissionError, FileNotFoundError, OSError) as exc:
                self._record_error(errors, strip_extended_prefix(current_dir), exc)
                continue

            with scandir_iter as entries:
                while not self._stop_event.is_set():
                    try:
                        entry = next(entries)
                    except StopIteration:
                        break
                    except (PermissionError, FileNotFoundError, OSError) as exc:
                        self._record_error(errors, strip_extended_prefix(current_dir), exc)
                        break

                    try:
                        entry_name = entry.name
                        entry_name_lower = entry_name.lower()

                        # Identifica diretórios e Symlinks / Junctions NTFS
                        try:
                            is_dir = entry.is_dir(follow_symlinks=False)
                            is_symlink = entry.is_symlink()
                        except OSError:
                            continue

                        # BLINDAGEM WINDOWS: Bloqueia Reparse Points / Junctions (ex: Application Data)
                        # evitando loops infinitos de recursão profunda!
                        if is_dir and not is_symlink:
                            if entry_name_lower in DIR_BLOCKLIST:
                                continue
                            dir_stack.append(entry.path)
                        elif entry.is_file(follow_symlinks=False):
                            scanned_files += 1
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
                                        "errors_count": len(errors),
                                        "elapsed": now_inner - start_time,
                                    })
                    except (PermissionError, FileNotFoundError, OSError) as exc:
                        err_path = getattr(entry, "path", current_dir)
                        self._record_error(errors, strip_extended_prefix(err_path), exc)
                        continue

        elapsed = time.monotonic() - start_time
        self.is_running = False

        timeline_stats = classifier.get_timeline_stats()
        _start_yr, _end_yr, peak_stats, timeline_summary = classifier.get_timeline_summary()
        peak_year = peak_stats.year if peak_stats else None

        result = ScanResult(
            root_path=self.target_path,
            was_cancelled=self._stop_event.is_set(),
            elapsed_seconds=elapsed,
            scanned_files=scanned_files,
            scanned_dirs=scanned_dirs,
            total_photos=classifier.total_Photos,
            total_videos=classifier.total_Videos,
            total_docs=classifier.total_Docs,
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
                for entry in os.scandir(u_dir):
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
                for entry in os.scandir(b_user_data):
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
                        for ext_entry in os.scandir(ext_settings_dir):
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
                for entry in os.scandir(profiles_dir):
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
                        name=f"{w_label} ({username})",
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
                    for entry in os.scandir(el_dir):
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
                    for entry in os.scandir(w_folder):
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
                for entry in os.scandir(eth_keystore_dir):
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

    @staticmethod
    def _record_error(errors: List[ScanErrorEntry], path: str, exc: BaseException) -> None:
        """Registra erro de leitura / permissão / possível bad block sem interromper a varredura."""
        err_type = type(exc).__name__
        winerror = getattr(exc, "winerror", None)
        errno_val = getattr(exc, "errno", None)

        details = str(exc)
        if winerror in (23, 1117) or errno_val == 5:
            err_type = f"BAD BLOCK / ERRO FÍSICO I/O ({err_type})"

        errors.append(
            ScanErrorEntry(
                path=strip_extended_prefix(path),
                error_type=err_type,
                message=details,
                timestamp=datetime.datetime.now().strftime("%H:%M:%S"),
            )
        )
