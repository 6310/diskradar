"""
Interface Gráfica Principal do Geio DiskRadar em CustomTkinter (Dark Mode nativo).
Design Moderno, Ergonômico e Otimizado para Triagem Forense Read-Only de HDs e SSDs.

Destaques de UI/UX:
- Header com identidade visual e barra de ferramentas integrada
- Crachá do Disco estilo dashboard com medidor visual de capacidade (gauge bar) e cópia de S/N
- HUD ao vivo com contadores em tempo real durante a varredura
- Abas com ordenação rápida (Relevância, Tamanho, Data, Quantidade)
- Linhas em cartões modernos com badges coloridos e botões "Copiar Caminho" com feedback tátil ("✔ Copiado!")
- Cópia completa de logs de erros/bad blocks para a área de transferência
- Performance máxima com debounce de 200ms e renderização sob demanda (Lazy Loading)
"""

import os
import queue
import threading
from tkinter import filedialog, messagebox
from typing import Callable, Dict, List, Optional

import customtkinter as ctk

from core.classifier import (
    CriticalFileItem,
    HotFolderItem,
    ScanErrorEntry,
    YearActivityStats,
)
from core.disk_info import (
    DiskBadgeInfo,
    fill_hardware_info,
    get_disk_badge_info,
    list_available_drives,
)
from core.explorer_bridge import open_in_explorer
from core.exporter import build_default_report_filename, export_html_report
from core.rules import CRITICAL_CATEGORIES
from core.scanner import AsyncDiskScanner, ScanResult

# Configuração visual global CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

PAGE_CHUNK_SIZE = 35


class DiskRadarApp(ctk.CTk):
    """Janela principal da aplicação Desktop Geio DiskRadar."""

    def __init__(self) -> None:
        super().__init__()

        self.title("Geio DiskRadar v2.2.0 — Triador e Indexador Read-Only de HDs e SSDs de Sucata")
        self.geometry("1340x880")
        self.minsize(1060, 720)

        # Estado da aplicação
        self._stitch_url: Optional[str] = None
        self.event_queue: queue.Queue = queue.Queue()
        self.scanner: Optional[AsyncDiskScanner] = None
        self.drives_map: Dict[str, str] = {}  # label -> path
        self.current_target_path: str = ""
        self.current_badge: Optional[DiskBadgeInfo] = None
        self.last_scan_result: Optional[ScanResult] = None

        # Controles de desempenho e lazy loading
        self._hot_visible_limit: int = PAGE_CHUNK_SIZE
        self._crit_visible_limit: int = PAGE_CHUNK_SIZE
        self._hot_debounce_timer: Optional[str] = None
        self._crit_debounce_timer: Optional[str] = None
        self._hw_query_thread: Optional[threading.Thread] = None

        # Construção do Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_top_bar()
        self._build_disk_badge_panel()
        self._build_status_bar()
        self._build_tabs()

        # Carrega unidades iniciais
        self.refresh_drives()

        # Inicia loop de leitura da fila assíncrona
        self.after(100, self._process_event_queue)

    # ==========================================================================
    # UTILITÁRIO DE ÁREA DE TRANSFERÊNCIA COM FEEDBACK VISUAL
    # ==========================================================================
    def copy_to_clipboard(
        self,
        text_to_copy: str,
        btn: Optional[ctk.CTkButton] = None,
        original_label: str = "",
        original_fg: Optional[str] = None,
    ) -> None:
        """Copia texto para a área de transferência com feedback tátil no botão acionador."""
        if not text_to_copy:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(text_to_copy)
            self.update()
        except Exception:
            pass

        if btn and original_label:
            btn.configure(text="✔ Copiado!", fg_color="#15803d")
            self.after(
                1400,
                lambda b=btn, txt=original_label, fg=original_fg: self._restore_btn_state(b, txt, fg),
            )

    @staticmethod
    def _restore_btn_state(btn: ctk.CTkButton, text: str, fg: Optional[str]) -> None:
        try:
            if btn.winfo_exists():
                cfg = {"text": text}
                if fg:
                    cfg["fg_color"] = fg
                btn.configure(**cfg)
        except Exception:
            pass

    # ==========================================================================
    # CONSTRUÇÃO DOS COMPONENTES DE UI
    # ==========================================================================
    def _build_top_bar(self) -> None:
        """Barra superior com identidade visual, seletor de unidade e botões de ação principais."""
        top_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=("#e2e8f0", "#111827"))
        top_frame.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")
        top_frame.grid_columnconfigure(1, weight=1)

        # Bloco da Esquerda: Identidade Visual & Branding
        brand_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        brand_frame.grid(row=0, column=0, rowspan=2, padx=(16, 12), pady=10, sticky="w")

        lbl_logo = ctk.CTkLabel(
            brand_frame,
            text="📡 DISKRADAR",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#38bdf8",
        )
        lbl_logo.grid(row=0, column=0, sticky="w")

        lbl_sub = ctk.CTkLabel(
            brand_frame,
            text="v2.2.0 • Cyber-Forensic Precision",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#00f0ff",
        )
        lbl_sub.grid(row=1, column=0, sticky="w")

        # Bloco Central / Linha 0: Seletor de Unidades & Ferramentas
        controls_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        controls_frame.grid(row=0, column=1, padx=6, pady=(10, 4), sticky="w")

        ctk.CTkLabel(
            controls_frame,
            text="💿 Unidade Alvo:",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, padx=(0, 8), pady=2)

        self.drive_option_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=["Carregando unidades..."],
            command=self._on_drive_selected,
            width=280,
            dynamic_resizing=False,
            fg_color="#1e293b",
            button_color="#334155",
            button_hover_color="#475569",
        )
        self.drive_option_menu.grid(row=0, column=1, padx=6, pady=2)

        self.btn_refresh = ctk.CTkButton(
            controls_frame,
            text="🔄 Atualizar",
            width=110,
            height=28,
            fg_color="#334155",
            hover_color="#475569",
            command=self.refresh_drives,
        )
        self.btn_refresh.grid(row=0, column=2, padx=6, pady=2)

        self.btn_custom_dir = ctk.CTkButton(
            controls_frame,
            text="📂 Pasta Avulsa",
            width=125,
            height=28,
            fg_color="#334155",
            hover_color="#475569",
            command=self._choose_custom_folder,
        )
        self.btn_custom_dir.grid(row=0, column=3, padx=6, pady=2)

        self.btn_open_stitch = ctk.CTkButton(
            controls_frame,
            text="⚡ Interface Stitch (10 Telas)",
            width=195,
            height=28,
            fg_color="#0891b2",
            hover_color="#06b6d4",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._open_stitch_gui,
        )
        self.btn_open_stitch.grid(row=0, column=4, padx=6, pady=2)

        # Bloco da Direita: Ações Primárias (Iniciar, Parar, Exportar HTML)
        actions_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        actions_frame.grid(row=0, column=2, rowspan=2, padx=(8, 16), pady=10, sticky="e")

        self.btn_start_scan = ctk.CTkButton(
            actions_frame,
            text="▶ Iniciar Varredura",
            width=175,
            height=34,
            fg_color="#16a34a",
            hover_color="#15803d",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.start_scan,
        )
        self.btn_start_scan.grid(row=0, column=0, padx=5, pady=2)

        self.btn_stop_scan = ctk.CTkButton(
            actions_frame,
            text="⏹ Parar",
            width=85,
            height=34,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            font=ctk.CTkFont(size=13, weight="bold"),
            state="disabled",
            command=self.stop_scan,
        )
        self.btn_stop_scan.grid(row=0, column=1, padx=5, pady=2)

        self.btn_export_html = ctk.CTkButton(
            actions_frame,
            text="📄 Exportar Relatório HTML",
            width=210,
            height=34,
            fg_color="#0284c7",
            hover_color="#0369a1",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.export_html_catalog,
        )
        self.btn_export_html.grid(row=0, column=2, padx=(5, 0), pady=2)

    def _build_disk_badge_panel(self) -> None:
        """Painel 'Crachá do Disco' (Dashboard com dados físicos, medidor de capacidade e S.M.A.R.T.)."""
        self.badge_frame = ctk.CTkFrame(self, corner_radius=12, fg_color=("#f1f5f9", "#111827"))
        self.badge_frame.grid(row=1, column=0, padx=14, pady=6, sticky="ew")
        for col in range(4):
            self.badge_frame.grid_columnconfigure(col, weight=1)

        # Linha 0: Cabeçalho com Título do Disco + Badge S.M.A.R.T.
        header_row = ctk.CTkFrame(self.badge_frame, fg_color="transparent")
        header_row.grid(row=0, column=0, columnspan=4, padx=14, pady=(10, 4), sticky="ew")
        header_row.grid_columnconfigure(0, weight=1)

        self.lbl_badge_title = ctk.CTkLabel(
            header_row,
            text="CRACHÁ DO DISCO — Selecione uma unidade para inspeção",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc",
            anchor="w",
        )
        self.lbl_badge_title.grid(row=0, column=0, sticky="w")

        self.lbl_smart_badge = ctk.CTkLabel(
            header_row,
            text=" 🛡️ S.M.A.R.T.: Desconhecido ",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#334155",
            text_color="#ffffff",
            corner_radius=8,
            padx=12,
            pady=4,
        )
        self.lbl_smart_badge.grid(row=0, column=1, sticky="e")

        # Linha 1: 4 Cartões do Dashboard
        # Card 0: Modelo & Medidor de Capacidade
        card_model = ctk.CTkFrame(self.badge_frame, fg_color=("#e2e8f0", "#1e293b"), corner_radius=10)
        card_model.grid(row=1, column=0, padx=6, pady=8, sticky="nsew")
        card_model.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card_model,
            text="💽 MODELO & CAPACIDADE",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8",
            anchor="w",
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        self.lbl_model_val = ctk.CTkLabel(
            card_model,
            text="—",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            justify="left",
            wraplength=260,
        )
        self.lbl_model_val.grid(row=1, column=0, padx=12, pady=(0, 4), sticky="w")

        self.capacity_progress = ctk.CTkProgressBar(card_model, height=6, corner_radius=3)
        self.capacity_progress.grid(row=2, column=0, padx=12, pady=(2, 8), sticky="ew")
        self.capacity_progress.set(0)

        # Card 1: Número de Série & Ação de Copiar
        card_serial = ctk.CTkFrame(self.badge_frame, fg_color=("#e2e8f0", "#1e293b"), corner_radius=10)
        card_serial.grid(row=1, column=1, padx=6, pady=8, sticky="nsew")
        card_serial.grid_columnconfigure(0, weight=1)

        serial_header = ctk.CTkFrame(card_serial, fg_color="transparent")
        serial_header.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="ew")
        serial_header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            serial_header,
            text="🏷️ NÚMERO DE SÉRIE (S/N)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.btn_copy_serial = ctk.CTkButton(
            serial_header,
            text="📋 Copiar",
            width=70,
            height=20,
            font=ctk.CTkFont(size=10, weight="bold"),
            fg_color="#334155",
            hover_color="#475569",
            command=self._copy_current_serial,
        )
        self.btn_copy_serial.grid(row=0, column=1, sticky="e")

        self.lbl_serial_val = ctk.CTkLabel(
            card_serial,
            text="—",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color="#38bdf8",
            anchor="w",
            justify="left",
            wraplength=260,
        )
        self.lbl_serial_val.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")

        # Card 2: Possíveis Donos (Usuários)
        card_users = ctk.CTkFrame(self.badge_frame, fg_color=("#e2e8f0", "#1e293b"), corner_radius=10)
        card_users.grid(row=1, column=2, padx=6, pady=8, sticky="nsew")
        card_users.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card_users,
            text="👥 POSSÍVEIS DONOS (USUÁRIOS)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8",
            anchor="w",
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        self.lbl_users_val = ctk.CTkLabel(
            card_users,
            text="—",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            justify="left",
            wraplength=260,
        )
        self.lbl_users_val.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")

        # Card 3: Última Atividade Estimada
        card_activity = ctk.CTkFrame(self.badge_frame, fg_color=("#e2e8f0", "#1e293b"), corner_radius=10)
        card_activity.grid(row=1, column=3, padx=6, pady=8, sticky="nsew")
        card_activity.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card_activity,
            text="📅 ÚLTIMA ATIVIDADE ESTIMADA",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94a3b8",
            anchor="w",
        ).grid(row=0, column=0, padx=12, pady=(8, 2), sticky="w")

        self.lbl_activity_val = ctk.CTkLabel(
            card_activity,
            text="—",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            justify="left",
            wraplength=260,
        )
        self.lbl_activity_val.grid(row=1, column=0, padx=12, pady=(0, 8), sticky="w")

        # Linha 2: Banner de Alerta Físico S.M.A.R.T.
        self.smart_warning_banner = ctk.CTkLabel(
            self.badge_frame,
            text="⚠️ ALERTA DE DISCO: Risco físico detectado! Salve documentos leves antes de copiar fotos/vídeos pesados.",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#7f1d1d",
            text_color="#fecaca",
            corner_radius=8,
            padx=14,
            pady=8,
        )
        self.smart_warning_banner.grid(row=2, column=0, columnspan=4, padx=10, pady=(2, 10), sticky="ew")
        self.smart_warning_banner.grid_remove()

    def _copy_current_serial(self) -> None:
        """Copia o número de série para o clipboard com feedback visual."""
        sn = self.lbl_serial_val.cget("text")
        if sn and sn not in ("—", "Consultando...", "N/A"):
            self.copy_to_clipboard(sn, self.btn_copy_serial, "📋 Copiar", "#334155")

    def _build_status_bar(self) -> None:
        """HUD de status em tempo real com pílulas de contagem ao vivo."""
        status_frame = ctk.CTkFrame(self, corner_radius=8, fg_color=("#cbd5e1", "#0b1329"))
        status_frame.grid(row=2, column=0, padx=14, pady=4, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)

        self.lbl_status_text = ctk.CTkLabel(
            status_frame,
            text="Pronto para iniciar varredura 100% Read-Only.",
            font=ctk.CTkFont(size=12),
            text_color="#e2e8f0",
            anchor="w",
        )
        self.lbl_status_text.grid(row=0, column=0, padx=14, pady=(6, 2), sticky="ew")

        self.lbl_counters = ctk.CTkLabel(
            status_frame,
            text="📁 Pastas: 0 | 📄 Arquivos: 0 | 🔥 Pastas Quentes: 0 | 🎯 Críticos: 0 | ⚠️ Erros: 0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#38bdf8",
            anchor="e",
        )
        self.lbl_counters.grid(row=0, column=1, padx=14, pady=(6, 2), sticky="e")

        self.progress_bar = ctk.CTkProgressBar(status_frame, height=6, corner_radius=3)
        self.progress_bar.grid(row=1, column=0, columnspan=2, padx=14, pady=(2, 8), sticky="ew")
        self.progress_bar.set(0)

    def _build_tabs(self) -> None:
        """Área principal com as 4 Abas do CTkTabview."""
        self.tabview = ctk.CTkTabview(self, corner_radius=12)
        self.tabview.grid(row=3, column=0, padx=14, pady=(4, 14), sticky="nsew")

        self.tab_hot = self.tabview.add("🔥 1. Pastas Quentes (Mídia & Docs)")
        self.tab_crit = self.tabview.add("🎯 2. Arquivos Críticos (Agulhas no Palheiro)")
        self.tab_users = self.tabview.add("👤 3. Árvore de Usuários & Atalhos Rápidos")
        self.tab_timeline = self.tabview.add("📅 4. Linha do Tempo & Atividade")
        self.tab_errors = self.tabview.add("⚠️ 5. Log de Erros / Bad Blocks")

        self._setup_tab_hot_folders()
        self._setup_tab_critical_files()
        self._setup_tab_users_shortcuts()
        self._setup_tab_timeline()
        self._setup_tab_errors()

    def _setup_tab_hot_folders(self) -> None:
        self.tab_hot.grid_columnconfigure(0, weight=1)
        self.tab_hot.grid_rowconfigure(1, weight=1)

        filter_bar = ctk.CTkFrame(self.tab_hot, fg_color="transparent")
        filter_bar.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        filter_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(filter_bar, text="🔍 Filtrar:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, padx=(4, 6), pady=4
        )
        self.entry_hot_filter = ctk.CTkEntry(
            filter_bar,
            placeholder_text="Filtrar por pasta (ex: Desktop, Fotos, Clientes, 2021)...",
        )
        self.entry_hot_filter.grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        self.entry_hot_filter.bind("<KeyRelease>", self._on_hot_filter_key)

        ctk.CTkLabel(filter_bar, text="Ordenar:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=2, padx=(12, 4), pady=4
        )
        self.opt_hot_sort = ctk.CTkOptionMenu(
            filter_bar,
            values=["Mais Relevantes", "Maior Tamanho", "Mais Arquivos", "Data Mais Recente"],
            width=165,
            command=lambda _val: self._trigger_hot_filter_reset(),
        )
        self.opt_hot_sort.grid(row=0, column=3, padx=4, pady=4)
        self.opt_hot_sort.set("Mais Relevantes")

        self.lbl_hot_summary = ctk.CTkLabel(
            filter_bar,
            text="0 pastas quentes",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
        )
        self.lbl_hot_summary.grid(row=0, column=4, padx=10, pady=4)

        self.scroll_hot = ctk.CTkScrollableFrame(self.tab_hot, corner_radius=10)
        self.scroll_hot.grid(row=1, column=0, padx=8, pady=4, sticky="nsew")
        self.scroll_hot.grid_columnconfigure(1, weight=1)

    def _setup_tab_critical_files(self) -> None:
        self.tab_crit.grid_columnconfigure(0, weight=1)
        self.tab_crit.grid_rowconfigure(1, weight=1)

        filter_bar = ctk.CTkFrame(self.tab_crit, fg_color="transparent")
        filter_bar.grid(row=0, column=0, padx=8, pady=6, sticky="ew")
        filter_bar.grid_columnconfigure(2, weight=1)

        ctk.CTkLabel(filter_bar, text="Categoria:", font=ctk.CTkFont(size=13, weight="bold")).grid(
            row=0, column=0, padx=(4, 6), pady=4
        )

        self.crit_cat_label_to_key = {v: k for k, v in CRITICAL_CATEGORIES.items()}
        self.opt_crit_category = ctk.CTkOptionMenu(
            filter_bar,
            values=list(CRITICAL_CATEGORIES.values()),
            width=210,
            command=lambda _val: self._trigger_crit_filter_reset(),
        )
        self.opt_crit_category.grid(row=0, column=1, padx=6, pady=4)
        self.opt_crit_category.set("Todos")

        self.entry_crit_filter = ctk.CTkEntry(
            filter_bar,
            placeholder_text="Buscar por nome, extensão (.wallet, .dwg, .psd, .pst) ou palavra-chave...",
        )
        self.entry_crit_filter.grid(row=0, column=2, padx=6, pady=4, sticky="ew")
        self.entry_crit_filter.bind("<KeyRelease>", self._on_crit_filter_key)

        ctk.CTkLabel(filter_bar, text="Ordenar:", font=ctk.CTkFont(size=12, weight="bold")).grid(
            row=0, column=3, padx=(12, 4), pady=4
        )
        self.opt_crit_sort = ctk.CTkOptionMenu(
            filter_bar,
            values=["Mais Recentes", "Maior Tamanho", "Nome (A-Z)"],
            width=150,
            command=lambda _val: self._trigger_crit_filter_reset(),
        )
        self.opt_crit_sort.grid(row=0, column=4, padx=4, pady=4)
        self.opt_crit_sort.set("Mais Recentes")

        self.lbl_crit_summary = ctk.CTkLabel(
            filter_bar,
            text="0 itens críticos",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
        )
        self.lbl_crit_summary.grid(row=0, column=5, padx=10, pady=4)

        self.scroll_crit = ctk.CTkScrollableFrame(self.tab_crit, corner_radius=10)
        self.scroll_crit.grid(row=1, column=0, padx=8, pady=4, sticky="nsew")
        self.scroll_crit.grid_columnconfigure(2, weight=1)

    def _setup_tab_users_shortcuts(self) -> None:
        self.tab_users.grid_columnconfigure(0, weight=1)
        self.tab_users.grid_rowconfigure(0, weight=1)

        self.scroll_users = ctk.CTkScrollableFrame(self.tab_users, corner_radius=10)
        self.scroll_users.grid(row=0, column=0, padx=8, pady=8, sticky="nsew")
        self.scroll_users.grid_columnconfigure(0, weight=1)

    def _setup_tab_timeline(self) -> None:
        self.tab_timeline.grid_columnconfigure(0, weight=1)
        self.tab_timeline.grid_rowconfigure(1, weight=1)

        # Header com resumo forense da linha do tempo
        self.timeline_header_card = ctk.CTkFrame(self.tab_timeline, fg_color=("#e2e8f0", "#1e293b"), corner_radius=10)
        self.timeline_header_card.grid(row=0, column=0, padx=8, pady=(6, 4), sticky="ew")
        self.timeline_header_card.grid_columnconfigure(0, weight=1)

        header_content = ctk.CTkFrame(self.timeline_header_card, fg_color="transparent")
        header_content.grid(row=0, column=0, padx=14, pady=10, sticky="ew")
        header_content.grid_columnconfigure(0, weight=1)

        self.lbl_timeline_title = ctk.CTkLabel(
            header_content,
            text="📅 HISTOGRAMA FORENSE DE ATIVIDADE DO DISCO",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#38bdf8",
            anchor="w",
        )
        self.lbl_timeline_title.grid(row=0, column=0, sticky="w")

        self.lbl_timeline_summary = ctk.CTkLabel(
            header_content,
            text="Inicie a varredura para mapear os anos de criação e modificação dos arquivos e descobrir o período de uso deste disco.",
            font=ctk.CTkFont(size=12),
            text_color="#cbd5e1",
            anchor="w",
            wraplength=950,
            justify="left",
        )
        self.lbl_timeline_summary.grid(row=1, column=0, pady=(2, 0), sticky="w")

        self.scroll_timeline = ctk.CTkScrollableFrame(self.tab_timeline, corner_radius=10)
        self.scroll_timeline.grid(row=1, column=0, padx=8, pady=4, sticky="nsew")
        self.scroll_timeline.grid_columnconfigure(0, weight=1)

    def _setup_tab_errors(self) -> None:
        self.tab_errors.grid_columnconfigure(0, weight=1)
        self.tab_errors.grid_rowconfigure(1, weight=1)

        top_info = ctk.CTkFrame(self.tab_errors, fg_color="transparent")
        top_info.grid(row=0, column=0, padx=8, pady=4, sticky="ew")
        top_info.grid_columnconfigure(0, weight=1)

        self.lbl_errors_summary = ctk.CTkLabel(
            top_info,
            text="Pastas ou arquivos que apresentaram erro de I/O (possíveis Bad Blocks) ou Permissão Negada:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        self.lbl_errors_summary.grid(row=0, column=0, padx=4, pady=4, sticky="w")

        self.btn_copy_errors = ctk.CTkButton(
            top_info,
            text="📋 Copiar Relatório de Erros",
            width=190,
            height=28,
            fg_color="#334155",
            hover_color="#475569",
            command=self._copy_all_errors_to_clipboard,
        )
        self.btn_copy_errors.grid(row=0, column=1, padx=4, pady=4, sticky="e")

        self.scroll_errors = ctk.CTkScrollableFrame(self.tab_errors, corner_radius=10)
        self.scroll_errors.grid(row=1, column=0, padx=8, pady=4, sticky="nsew")
        self.scroll_errors.grid_columnconfigure(2, weight=1)

    # ==========================================================================
    # AÇÕES E EVENTOS DE UNIDADE
    # ==========================================================================
    def refresh_drives(self) -> None:
        """Atualiza o dropdown de unidades montadas e seleciona a primeira disponível."""
        drives = list_available_drives()
        self.drives_map.clear()
        labels: List[str] = []

        for d in drives:
            lbl = d["label"]
            self.drives_map[lbl] = d["path"]
            labels.append(lbl)

        self.drive_option_menu.configure(values=labels)
        if labels:
            self.drive_option_menu.set(labels[0])
            self._select_target_path(self.drives_map[labels[0]])

    def _on_drive_selected(self, selected_label: str) -> None:
        path = self.drives_map.get(selected_label)
        if path:
            self._select_target_path(path)

    def _choose_custom_folder(self) -> None:
        folder = filedialog.askdirectory(
            title="Selecione uma Pasta ou Unidade Montada para Triagem Read-Only",
            initialdir=self.current_target_path or os.path.expanduser("~"),
        )
        if folder:
            custom_label = f"{folder} (Pasta Avulsa)"
            self.drives_map[custom_label] = folder
            current_vals = list(self.drive_option_menu.cget("values"))
            if custom_label not in current_vals:
                current_vals.insert(0, custom_label)
                self.drive_option_menu.configure(values=current_vals)
            self.drive_option_menu.set(custom_label)
            self._select_target_path(folder)

    def _open_stitch_gui(self) -> None:
        """Inicia o servidor Stitch local (caso ainda não ativo) e abre a interface de 10 telas."""
        try:
            import webbrowser
            from ui.stitch_server import start_stitch_background_server

            if not self._stitch_url:
                url, _ctrl, _srv = start_stitch_background_server()
                self._stitch_url = url
            webbrowser.open(self._stitch_url)
        except Exception as exc:
            messagebox.showerror("Erro ao abrir Interface Stitch", str(exc))

    def _select_target_path(self, target_path: str) -> None:
        """Atualiza imediatamente a interface e dispara consulta física em background."""
        self.current_target_path = os.path.abspath(target_path)

        badge = get_disk_badge_info(self.current_target_path, query_hw=False)
        self.current_badge = badge

        self.lbl_badge_title.configure(
            text=f"CRACHÁ DO DISCO — Unidade: {badge.target_path} ({badge.filesystem})"
        )
        self.lbl_model_val.configure(text=f"Identificando...\n{badge.capacity_summary}")
        self.lbl_serial_val.configure(text="Consultando...")
        self.lbl_users_val.configure(text=badge.users_summary)

        # Atualiza a barra de progresso visual de capacidade
        prog_val = min(max(badge.percent_used / 100.0, 0.0), 1.0)
        self.capacity_progress.set(prog_val)
        if prog_val >= 0.90:
            self.capacity_progress.configure(progress_color="#ef4444")
        elif prog_val >= 0.75:
            self.capacity_progress.configure(progress_color="#f59e0b")
        else:
            self.capacity_progress.configure(progress_color="#0284c7")

        if badge.last_activity_date:
            self.lbl_activity_val.configure(text=f"Último uso estimado: {badge.last_activity_date}")
        else:
            self.lbl_activity_val.configure(text="Último uso estimado: Não identificado")

        self.lbl_smart_badge.configure(
            text=" ⏳ S.M.A.R.T.: Consultando hardware... ",
            fg_color="#334155",
        )
        self.smart_warning_banner.grid_remove()

        self._render_users_shortcuts_tab()

        def _hw_worker(b: DiskBadgeInfo) -> None:
            fill_hardware_info(b)
            self.after(0, lambda: self._apply_hw_info_to_ui(b))

        self._hw_query_thread = threading.Thread(
            target=_hw_worker,
            args=(badge,),
            daemon=True,
            name="DiskRadarHwQueryThread",
        )
        self._hw_query_thread.start()

    def _apply_hw_info_to_ui(self, badge: DiskBadgeInfo) -> None:
        """Aplica os dados de Hardware, S.M.A.R.T., Horas de Uso e RPM retornados pelo PowerShell."""
        if not self.current_badge or self.current_badge.target_path != badge.target_path:
            return

        media_str = f" ({badge.hardware_media_summary})" if badge.hardware_media_summary != "Tipo não especificado" else ""
        self.lbl_model_val.configure(text=f"{badge.model}{media_str}\n{badge.capacity_summary}")
        self.lbl_serial_val.configure(text=badge.serial_number)

        act_text = f"Último uso: {badge.last_activity_date}" if badge.last_activity_date else "Último uso: Não identificado"
        poh_text = f"\n⏳ {badge.power_on_summary}" if badge.power_on_hours is not None else ""
        self.lbl_activity_val.configure(text=f"{act_text}{poh_text}")

        if badge.is_healthy:
            self.lbl_smart_badge.configure(
                text=f" 🛡️ S.M.A.R.T.: {badge.smart_details} ",
                fg_color="#15803d",
            )
            self.smart_warning_banner.grid_remove()
        else:
            color = "#d97706" if badge.smart_status == "Warning" else "#dc2626"
            self.lbl_smart_badge.configure(
                text=f" ⚠️ S.M.A.R.T.: {badge.smart_details} ",
                fg_color=color,
            )
            self.smart_warning_banner.grid()

    # ==========================================================================
    # DEBOUNCE INTELIGENTE DE BUSCA
    # ==========================================================================
    def _on_hot_filter_key(self, _event=None) -> None:
        if self._hot_debounce_timer:
            self.after_cancel(self._hot_debounce_timer)
        self._hot_debounce_timer = self.after(200, self._trigger_hot_filter_reset)

    def _trigger_hot_filter_reset(self) -> None:
        self._hot_visible_limit = PAGE_CHUNK_SIZE
        self._render_hot_folders_list()

    def _on_crit_filter_key(self, _event=None) -> None:
        if self._crit_debounce_timer:
            self.after_cancel(self._crit_debounce_timer)
        self._crit_debounce_timer = self.after(200, self._trigger_crit_filter_reset)

    def _trigger_crit_filter_reset(self) -> None:
        self._crit_visible_limit = PAGE_CHUNK_SIZE
        self._render_critical_files_list()

    # ==========================================================================
    # VARREDURA ASSÍNCRONA E FILA DE EVENTOS
    # ==========================================================================
    def start_scan(self) -> None:
        if not self.current_target_path or not os.path.exists(self.current_target_path):
            messagebox.showwarning("Unidade Inválida", "Selecione uma unidade ou pasta válida antes de varrer.")
            return

        if self.scanner and self.scanner.is_running:
            return

        self.last_scan_result = None
        self._hot_visible_limit = PAGE_CHUNK_SIZE
        self._crit_visible_limit = PAGE_CHUNK_SIZE
        self._clear_scrollable(self.scroll_hot)
        self._clear_scrollable(self.scroll_crit)
        self._clear_scrollable(self.scroll_timeline)
        self._clear_scrollable(self.scroll_errors)

        self.btn_start_scan.configure(state="disabled")
        self.btn_stop_scan.configure(state="normal")
        self.drive_option_menu.configure(state="disabled")
        self.btn_custom_dir.configure(state="disabled")

        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        self.scanner = AsyncDiskScanner(self.current_target_path, self.event_queue)
        self.scanner.start()

    def stop_scan(self) -> None:
        if self.scanner and self.scanner.is_running:
            self.lbl_status_text.configure(text="Cancelando varredura... consolidando dados coletados.")
            self.scanner.stop()

    def _process_event_queue(self) -> None:
        """Consome mensagens da thread de varredura sem bloquear a interface."""
        try:
            while True:
                msg = self.event_queue.get_nowait()
                mtype = msg.get("type")

                if mtype == "SCAN_STARTED":
                    self.lbl_status_text.configure(
                        text=f"Varrendo metadados (Read-Only): {msg.get('root_path')}..."
                    )

                elif mtype == "SCAN_PROGRESS":
                    curr_dir = msg.get("current_dir", "")
                    if len(curr_dir) > 85:
                        curr_dir = "..." + curr_dir[-82:]
                    files_cnt = msg.get("scanned_files", 0)
                    dirs_cnt = msg.get("scanned_dirs", 0)
                    hot_cnt = msg.get("hot_folders_count", 0)
                    crit_cnt = msg.get("critical_count", 0)
                    err_cnt = msg.get("errors_count", 0)
                    elapsed = msg.get("elapsed", 0.0)

                    self.lbl_status_text.configure(
                        text=f"⚡ Analisando ({elapsed:.1f}s): {curr_dir}"
                    )
                    self.lbl_counters.configure(
                        text=(
                            f"📁 Pastas: {dirs_cnt:,} | 📄 Arquivos: {files_cnt:,} | "
                            f"🔥 Pastas Quentes: {hot_cnt:,} | 🎯 Críticos: {crit_cnt:,} | "
                            f"⚠️ Erros: {err_cnt:,}"
                        )
                    )

                elif mtype == "SCAN_FINISHED":
                    result: ScanResult = msg["result"]
                    self._on_scan_finished(result)

        except queue.Empty:
            pass
        finally:
            self.after(100, self._process_event_queue)

    def _on_scan_finished(self, result: ScanResult) -> None:
        self.last_scan_result = result

        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)

        self.btn_start_scan.configure(state="normal")
        self.btn_stop_scan.configure(state="disabled")
        self.drive_option_menu.configure(state="normal")
        self.btn_custom_dir.configure(state="normal")

        status_prefix = "Varredura interrompida pelo usuário" if result.was_cancelled else "Varredura Read-Only concluída"
        self.lbl_status_text.configure(
            text=(
                f"{status_prefix} em {result.elapsed_seconds:.2f}s — "
                f"Fotos: {result.total_photos:,} | Vídeos: {result.total_videos:,} | Docs: {result.total_docs:,}"
            )
        )
        self.lbl_counters.configure(
            text=(
                f"📁 Pastas: {result.scanned_dirs:,} | 📄 Arquivos: {result.scanned_files:,} | "
                f"🔥 Pastas Quentes: {len(result.hot_folders):,} | 🎯 Críticos: {len(result.critical_items):,} | "
                f"⚠️ Erros: {len(result.errors):,}"
            )
        )

        self._render_hot_folders_list()
        self._render_critical_files_list()
        self._render_timeline_tab()
        self._render_errors_list()

    # ==========================================================================
    # RENDERIZAÇÃO OTIMIZADA DAS ABAS
    # ==========================================================================
    @staticmethod
    def _clear_scrollable(frame: ctk.CTkScrollableFrame) -> None:
        for child in frame.winfo_children():
            child.destroy()

    def _render_hot_folders_list(self) -> None:
        """Renderiza a Aba 1 com ordenação dinâmica e lazy loading."""
        self._clear_scrollable(self.scroll_hot)
        if not self.last_scan_result:
            ctk.CTkLabel(
                self.scroll_hot,
                text="Clique em '▶ Iniciar Varredura' para mapear as Pastas Quentes do disco.",
                text_color="#94a3b8",
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, padx=12, pady=28)
            return

        query = self.entry_hot_filter.get().strip().lower()
        all_folders = list(self.last_scan_result.hot_folders)

        # Filtragem por texto
        filtered = [
            hf for hf in all_folders
            if not query or query in hf.folder_path.lower()
        ]

        # Ordenação dinâmica
        sort_mode = self.opt_hot_sort.get()
        if sort_mode == "Maior Tamanho":
            filtered.sort(key=lambda x: x.total_bytes, reverse=True)
        elif sort_mode == "Mais Arquivos":
            filtered.sort(key=lambda x: x.total_files, reverse=True)
        elif sort_mode == "Data Mais Recente":
            filtered.sort(key=lambda x: x.latest_mtime, reverse=True)
        else:
            filtered.sort(key=lambda x: (x.relevance_score, x.total_bytes), reverse=True)

        showing = min(len(filtered), self._hot_visible_limit)
        self.lbl_hot_summary.configure(
            text=f"Mostrando {showing} de {len(filtered)} pastas quentes"
        )

        if not filtered:
            ctk.CTkLabel(
                self.scroll_hot,
                text="Nenhuma Pasta Quente encontrada para o filtro informado.",
                text_color="#94a3b8",
            ).grid(row=0, column=0, padx=12, pady=20)
            return

        for idx, hf in enumerate(filtered[:self._hot_visible_limit]):
            self._create_hot_folder_row(idx, hf)

        if len(filtered) > self._hot_visible_limit:
            btn_more = ctk.CTkButton(
                self.scroll_hot,
                text=f"⬇️ Carregar mais {PAGE_CHUNK_SIZE} pastas (Exibindo {self._hot_visible_limit} de {len(filtered)})...",
                fg_color="#1e293b",
                hover_color="#334155",
                height=34,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=self._load_more_hot_folders,
            )
            btn_more.grid(row=self._hot_visible_limit, column=0, columnspan=2, padx=12, pady=10, sticky="ew")

    def _load_more_hot_folders(self) -> None:
        self._hot_visible_limit += PAGE_CHUNK_SIZE
        self._render_hot_folders_list()

    def _create_hot_folder_row(self, row_idx: int, item: HotFolderItem) -> None:
        """Renderiza um card visual expansivo e detalhado para Pasta Quente."""
        card = ctk.CTkFrame(
            self.scroll_hot,
            fg_color=("#ffffff", "#1e293b"),
            border_width=1,
            border_color=("#cbd5e1", "#334155"),
            corner_radius=10,
        )
        card.grid(row=row_idx, column=0, columnspan=2, padx=6, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # ----------------------------------------------------------------------
        # Linha 1: Cabeçalho do Card (Tag principal + Nome da Pasta + Métricas)
        # ----------------------------------------------------------------------
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        tag_color = "#0284c7" if item.dominant_icon_tag == "[FOTOS]" else (
            "#7c3aed" if item.dominant_icon_tag == "[VÍDEOS]" else (
                "#0d9488" if item.dominant_icon_tag == "[DOCS]" else "#475569"
            )
        )
        lbl_tag = ctk.CTkLabel(
            header,
            text=f" {item.dominant_icon_tag} ",
            fg_color=tag_color,
            text_color="#ffffff",
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=26,
        )
        lbl_tag.grid(row=0, column=0, padx=(0, 10), sticky="w")

        folder_display_name = os.path.basename(item.folder_path.rstrip("\\/")) or item.folder_path
        lbl_name = ctk.CTkLabel(
            header,
            text=f"📁 {folder_display_name}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#0f172a", "#f8fafc"),
            anchor="w",
        )
        lbl_name.grid(row=0, column=1, sticky="w")

        # Pílulas métricas à direita
        pills_frame = ctk.CTkFrame(header, fg_color="transparent")
        pills_frame.grid(row=0, column=2, sticky="e")

        col_p = 0
        if item.photos_count > 0:
            ctk.CTkLabel(
                pills_frame,
                text=f" 🖼️ {item.photos_count:,} ",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=("#e0f2fe", "#0c4a6e"),
                text_color=("#0369a1", "#38bdf8"),
                corner_radius=5,
                height=22,
            ).grid(row=0, column=col_p, padx=3)
            col_p += 1

        if item.videos_count > 0:
            ctk.CTkLabel(
                pills_frame,
                text=f" 🎬 {item.videos_count:,} ",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=("#f3e8ff", "#581c87"),
                text_color=("#7e22ce", "#c084fc"),
                corner_radius=5,
                height=22,
            ).grid(row=0, column=col_p, padx=3)
            col_p += 1

        if item.docs_count > 0:
            ctk.CTkLabel(
                pills_frame,
                text=f" 📑 {item.docs_count:,} ",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=("#ccfbf1", "#134e4a"),
                text_color=("#0f766e", "#2dd4bf"),
                corner_radius=5,
                height=22,
            ).grid(row=0, column=col_p, padx=3)
            col_p += 1

        ctk.CTkLabel(
            pills_frame,
            text=f" 📦 {item.formatted_size} ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#f1f5f9", "#334155"),
            text_color=("#334155", "#f1f5f9"),
            corner_radius=5,
            height=22,
        ).grid(row=0, column=col_p, padx=3)
        col_p += 1

        ctk.CTkLabel(
            pills_frame,
            text=f" 📅 {item.formatted_date} ",
            font=ctk.CTkFont(size=11),
            fg_color=("#f1f5f9", "#1e293b"),
            text_color=("#64748b", "#94a3b8"),
            corner_radius=5,
            height=22,
        ).grid(row=0, column=col_p, padx=(3, 0))

        # ----------------------------------------------------------------------
        # Linha 2: Barra de Caminho + Botões de Ação
        # ----------------------------------------------------------------------
        bottom_bar = ctk.CTkFrame(card, fg_color="transparent")
        bottom_bar.grid(row=1, column=0, padx=12, pady=(2, 10), sticky="ew")
        bottom_bar.grid_columnconfigure(0, weight=1)

        path_box = ctk.CTkFrame(
            bottom_bar,
            fg_color=("#f1f5f9", "#0f172a"),
            corner_radius=6,
            border_width=1,
            border_color=("#e2e8f0", "#1e293b"),
        )
        path_box.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        path_box.grid_columnconfigure(0, weight=1)

        lbl_path = ctk.CTkLabel(
            path_box,
            text=f"📍 {item.folder_path}",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=("#475569", "#cbd5e1"),
            anchor="w",
            height=28,
        )
        lbl_path.grid(row=0, column=0, padx=8, pady=2, sticky="ew")

        actions = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e")

        btn_copy = ctk.CTkButton(
            actions,
            text="📋 Copiar",
            width=85,
            height=28,
            fg_color=("#cbd5e1", "#334155"),
            hover_color=("#94a3b8", "#475569"),
            text_color=("#0f172a", "#f8fafc"),
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        btn_copy.configure(
            command=lambda p=item.folder_path, b=btn_copy: self.copy_to_clipboard(p, b, "📋 Copiar", "#334155")
        )
        btn_copy.grid(row=0, column=0, padx=4)

        btn_open = ctk.CTkButton(
            actions,
            text="📂 Abrir no Explorer",
            width=150,
            height=28,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda p=item.folder_path: open_in_explorer(p, select_item=False),
        )
        btn_open.grid(row=0, column=1, padx=4)

    def _render_critical_files_list(self) -> None:
        """Renderiza a Aba 2 com ordenação dinâmica e lazy loading."""
        self._clear_scrollable(self.scroll_crit)
        if not self.last_scan_result:
            ctk.CTkLabel(
                self.scroll_crit,
                text="Clique em '▶ Iniciar Varredura' para caçar Arquivos Críticos no disco.",
                text_color="#94a3b8",
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, padx=12, pady=28)
            return

        selected_cat_label = self.opt_crit_category.get()
        cat_key = self.crit_cat_label_to_key.get(selected_cat_label, "ALL")
        query = self.entry_crit_filter.get().strip().lower()

        filtered: List[CriticalFileItem] = []
        for ci in self.last_scan_result.critical_items:
            if cat_key != "ALL" and ci.category_key != cat_key:
                continue
            if query and (
                query not in ci.name.lower()
                and query not in ci.full_path.lower()
                and query not in ci.tag_label.lower()
            ):
                continue
            filtered.append(ci)

        # Ordenação dinâmica
        sort_mode = self.opt_crit_sort.get()
        if sort_mode == "Maior Tamanho":
            filtered.sort(key=lambda x: x.size_bytes, reverse=True)
        elif sort_mode == "Nome (A-Z)":
            filtered.sort(key=lambda x: x.name.lower())
        else:
            filtered.sort(key=lambda x: (x.mtime, x.size_bytes), reverse=True)

        showing = min(len(filtered), self._crit_visible_limit)
        self.lbl_crit_summary.configure(
            text=f"Mostrando {showing} de {len(filtered)} itens críticos"
        )

        if not filtered:
            ctk.CTkLabel(
                self.scroll_crit,
                text="Nenhum arquivo crítico encontrado para o filtro selecionado.",
                text_color="#94a3b8",
            ).grid(row=0, column=0, padx=12, pady=20)
            return

        for idx, ci in enumerate(filtered[:self._crit_visible_limit]):
            self._create_critical_file_row(idx, ci)

        if len(filtered) > self._crit_visible_limit:
            btn_more = ctk.CTkButton(
                self.scroll_crit,
                text=f"⬇️ Carregar mais {PAGE_CHUNK_SIZE} itens (Exibindo {self._crit_visible_limit} de {len(filtered)})...",
                fg_color="#1e293b",
                hover_color="#334155",
                height=34,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=self._load_more_critical_files,
            )
            btn_more.grid(row=self._crit_visible_limit, column=0, columnspan=3, padx=12, pady=10, sticky="ew")

    def _load_more_critical_files(self) -> None:
        self._crit_visible_limit += PAGE_CHUNK_SIZE
        self._render_critical_files_list()

    def _create_critical_file_row(self, row_idx: int, item: CriticalFileItem) -> None:
        """Renderiza um card forense de evidência com alto contraste e clareza visual."""
        card = ctk.CTkFrame(
            self.scroll_crit,
            fg_color=("#ffffff", "#1e293b"),
            border_width=1,
            border_color=("#cbd5e1", "#334155"),
            corner_radius=10,
        )
        card.grid(row=row_idx, column=0, columnspan=3, padx=6, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # ----------------------------------------------------------------------
        # Linha 1: Cabeçalho do Card (Categoria + Nome + Motivo + Tamanho/Data)
        # ----------------------------------------------------------------------
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        cat_meta = {
            "CRYPTO_WALLETS": ("🪙 CRIPTO WALLET", "#d97706"),
            "BROWSERS_CREDS": ("🔑 SENHAS / LOGIN", "#7c3aed"),
            "CAD_DESIGN": ("📐 CAD / DWG", "#0891b2"),
            "EMAIL_MSG": ("✉️ E-MAILS / PST", "#2563eb"),
            "CERT_KEYS": ("🛡️ CERTIFICADO / SSH", "#dc2626"),
            "IRPF_FISCAL": ("📊 IRPF / FISCAL", "#059669"),
            "DB_ERP": ("🗄️ BANCO DE DADOS", "#ea580c"),
            "ARCHIVES": ("📦 COMPACTADO", "#475569"),
            "KEYWORDS": ("🔍 ACHADO CHAVE", "#ca8a04"),
        }
        badge_text, badge_color = cat_meta.get(
            item.category_key, (item.tag_label, "#b45309")
        )

        lbl_cat = ctk.CTkLabel(
            header,
            text=f" {badge_text} ",
            fg_color=badge_color,
            text_color="#ffffff",
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=26,
        )
        lbl_cat.grid(row=0, column=0, padx=(0, 10), sticky="w")

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=1, sticky="w")

        lbl_name = ctk.CTkLabel(
            title_box,
            text=item.name,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#0f172a", "#f8fafc"),
            anchor="w",
        )
        lbl_name.grid(row=0, column=0, sticky="w")

        if item.matched_reason:
            lbl_reason = ctk.CTkLabel(
                title_box,
                text=f"  {item.matched_reason}  ",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=("#e0f2fe", "#0369a1"),
                text_color=("#0284c7", "#e0f2fe"),
                corner_radius=4,
                height=20,
            )
            lbl_reason.grid(row=0, column=1, padx=(8, 0), sticky="w")

        meta_box = ctk.CTkFrame(header, fg_color="transparent")
        meta_box.grid(row=0, column=2, sticky="e")

        ctk.CTkLabel(
            meta_box,
            text=f" 📦 {item.formatted_size} ",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=("#f1f5f9", "#334155"),
            text_color=("#334155", "#f1f5f9"),
            corner_radius=5,
            height=22,
        ).grid(row=0, column=0, padx=3)

        ctk.CTkLabel(
            meta_box,
            text=f" 📅 {item.formatted_date} ",
            font=ctk.CTkFont(size=11),
            fg_color=("#f1f5f9", "#1e293b"),
            text_color=("#64748b", "#94a3b8"),
            corner_radius=5,
            height=22,
        ).grid(row=0, column=1, padx=(3, 0))

        # ----------------------------------------------------------------------
        # Linha 2: Barra de Caminho + Botões de Ação
        # ----------------------------------------------------------------------
        bottom_bar = ctk.CTkFrame(card, fg_color="transparent")
        bottom_bar.grid(row=1, column=0, padx=12, pady=(2, 10), sticky="ew")
        bottom_bar.grid_columnconfigure(0, weight=1)

        path_box = ctk.CTkFrame(
            bottom_bar,
            fg_color=("#f1f5f9", "#0f172a"),
            corner_radius=6,
            border_width=1,
            border_color=("#e2e8f0", "#1e293b"),
        )
        path_box.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        path_box.grid_columnconfigure(0, weight=1)

        lbl_path = ctk.CTkLabel(
            path_box,
            text=f"📍 {item.full_path}",
            font=ctk.CTkFont(family="Consolas", size=11),
            text_color=("#475569", "#cbd5e1"),
            anchor="w",
            height=28,
        )
        lbl_path.grid(row=0, column=0, padx=8, pady=2, sticky="ew")

        actions = ctk.CTkFrame(bottom_bar, fg_color="transparent")
        actions.grid(row=0, column=1, sticky="e")

        btn_copy = ctk.CTkButton(
            actions,
            text="📋 Copiar",
            width=85,
            height=28,
            fg_color=("#cbd5e1", "#334155"),
            hover_color=("#94a3b8", "#475569"),
            text_color=("#0f172a", "#f8fafc"),
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        btn_copy.configure(
            command=lambda p=item.full_path, b=btn_copy: self.copy_to_clipboard(p, b, "📋 Copiar", "#334155")
        )
        btn_copy.grid(row=0, column=0, padx=4)

        btn_open = ctk.CTkButton(
            actions,
            text="📂 Abrir no Explorer",
            width=150,
            height=28,
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda p=item.full_path: open_in_explorer(p, select_item=True),
        )
        btn_open.grid(row=0, column=1, padx=4)

    def _render_users_shortcuts_tab(self) -> None:
        """Renderiza a Aba 3: Árvore de Usuários & Atalhos Rápidos com design de cartões profissionais."""
        self._clear_scrollable(self.scroll_users)
        badge = self.current_badge
        if not badge:
            return

        # Cartão da Raiz da Unidade
        root_card = ctk.CTkFrame(self.scroll_users, fg_color=("#e2e8f0", "#1e293b"), corner_radius=10)
        root_card.grid(row=0, column=0, padx=8, pady=8, sticky="ew")
        root_card.grid_columnconfigure(0, weight=1)

        root_info = ctk.CTkFrame(root_card, fg_color="transparent")
        root_info.grid(row=0, column=0, padx=14, pady=10, sticky="w")

        ctk.CTkLabel(
            root_info,
            text=f"💿 Raiz da Unidade Analisada: {badge.target_path}",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#f8fafc",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            root_info,
            text=f"Sistema de Arquivos: {badge.filesystem} • {badge.capacity_summary}",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8",
            anchor="w",
        ).grid(row=1, column=0, sticky="w")

        root_actions = ctk.CTkFrame(root_card, fg_color="transparent")
        root_actions.grid(row=0, column=1, padx=14, pady=10)

        btn_copy_root = ctk.CTkButton(
            root_actions,
            text="📋 Copiar Caminho",
            width=135,
            height=30,
            fg_color="#334155",
            hover_color="#475569",
        )
        btn_copy_root.configure(
            command=lambda p=badge.target_path, b=btn_copy_root: self.copy_to_clipboard(p, b, "📋 Copiar Caminho", "#334155")
        )
        btn_copy_root.grid(row=0, column=0, padx=5)

        ctk.CTkButton(
            root_actions,
            text="📂 Abrir Raiz no Explorer",
            width=170,
            height=30,
            command=lambda p=badge.target_path: open_in_explorer(p, select_item=False),
        ).grid(row=0, column=1, padx=5)

        if not badge.detected_users:
            empty_card = ctk.CTkFrame(self.scroll_users, fg_color=("#e2e8f0", "#1e293b"), corner_radius=10)
            empty_card.grid(row=1, column=0, padx=8, pady=12, sticky="ew")
            ctk.CTkLabel(
                empty_card,
                text=(
                    "ℹ️ Nenhuma pasta padrão de usuário ('Users' ou 'Documents and Settings') foi detectada na raiz deste disco.\n"
                    "O disco pode ser um drive de dados secundário ou de sistema não-Windows. Utilize as Abas 1 e 2 para navegar pelos achados."
                ),
                text_color="#94a3b8",
                justify="left",
                font=ctk.CTkFont(size=12),
            ).grid(row=0, column=0, padx=16, pady=16, sticky="w")
            return

        for idx, user in enumerate(badge.detected_users, start=1):
            u_card = ctk.CTkFrame(self.scroll_users, fg_color=("#e2e8f0", "#1e293b"), corner_radius=10)
            u_card.grid(row=idx, column=0, padx=8, pady=6, sticky="ew")
            u_card.grid_columnconfigure(0, weight=1)

            # Cabeçalho do Usuário
            u_header = ctk.CTkFrame(u_card, fg_color="transparent")
            u_header.grid(row=0, column=0, padx=14, pady=(10, 6), sticky="ew")
            u_header.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                u_header,
                text=f"👤 Perfil de Usuário: {user.username}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#38bdf8",
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            btn_copy_profile = ctk.CTkButton(
                u_header,
                text="📋 Copiar Caminho",
                width=130,
                height=24,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#334155",
                hover_color="#475569",
            )
            btn_copy_profile.configure(
                command=lambda p=user.profile_path, b=btn_copy_profile: self.copy_to_clipboard(p, b, "📋 Copiar Caminho", "#334155")
            )
            btn_copy_profile.grid(row=0, column=1, sticky="e")

            # Caminho em texto muted
            ctk.CTkLabel(
                u_card,
                text=user.profile_path,
                font=ctk.CTkFont(family="Consolas", size=11),
                text_color="#94a3b8",
                anchor="w",
            ).grid(row=1, column=0, padx=14, pady=(0, 8), sticky="w")

            # Barra de Botões Rápidos
            btn_bar = ctk.CTkFrame(u_card, fg_color="transparent")
            btn_bar.grid(row=2, column=0, padx=10, pady=(2, 12), sticky="w")

            # Linha 1: Pastas Pessoais
            ctk.CTkButton(
                btn_bar,
                text="📁 Perfil Completo",
                width=140,
                height=28,
                fg_color="#334155",
                hover_color="#475569",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda p=user.profile_path: open_in_explorer(p, select_item=True),
            ).grid(row=0, column=0, padx=4, pady=3)

            shortcut_icons = {
                "Desktop": "🖥️ Desktop",
                "Documents": "📑 Documents",
                "Pictures": "🖼️ Pictures",
                "Downloads": "⬇️ Downloads",
            }
            col_idx = 1
            for key, label_text in shortcut_icons.items():
                target_dir = user.shortcuts.get(key)
                if target_dir:
                    ctk.CTkButton(
                        btn_bar,
                        text=f"{label_text}",
                        width=140,
                        height=28,
                        fg_color="#0284c7",
                        hover_color="#0369a1",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        command=lambda p=target_dir: open_in_explorer(p, select_item=True),
                    ).grid(row=0, column=col_idx, padx=4, pady=3)
                else:
                    ctk.CTkButton(
                        btn_bar,
                        text=f"{label_text} (—)",
                        width=140,
                        height=28,
                        state="disabled",
                        fg_color="#1e293b",
                        font=ctk.CTkFont(size=11),
                    ).grid(row=0, column=col_idx, padx=4, pady=3)
                col_idx += 1

            # Linha 2: Navegadores e AppData do Usuário
            browser_shortcuts = [
                ("🌐 Chrome Data", os.path.join(user.profile_path, "AppData", "Local", "Google", "Chrome", "User Data")),
                ("🌐 Edge Data", os.path.join(user.profile_path, "AppData", "Local", "Microsoft", "Edge", "User Data")),
                ("🦊 Firefox Profiles", os.path.join(user.profile_path, "AppData", "Roaming", "Mozilla", "Firefox", "Profiles")),
                ("📦 AppData Geral", os.path.join(user.profile_path, "AppData")),
            ]
            for b_idx, (b_label, b_path) in enumerate(browser_shortcuts):
                if os.path.isdir(b_path):
                    ctk.CTkButton(
                        btn_bar,
                        text=b_label,
                        width=140,
                        height=28,
                        fg_color="#6366f1",
                        hover_color="#4f46e5",
                        font=ctk.CTkFont(size=11, weight="bold"),
                        command=lambda p=b_path: open_in_explorer(p, select_item=True),
                    ).grid(row=1, column=b_idx + 1, padx=4, pady=3)
                else:
                    ctk.CTkButton(
                        btn_bar,
                        text=f"{b_label} (—)",
                        width=140,
                        height=28,
                        state="disabled",
                        fg_color="#1e293b",
                        font=ctk.CTkFont(size=11),
                    ).grid(row=1, column=b_idx + 1, padx=4, pady=3)

    def _render_timeline_tab(self) -> None:
        """Renderiza a Aba de Linha do Tempo & Histograma Anual de Atividade."""
        self._clear_scrollable(self.scroll_timeline)
        if not self.last_scan_result or not self.last_scan_result.timeline_stats:
            self.lbl_timeline_summary.configure(
                text="Nenhum arquivo relevante com data válida foi encontrado para gerar o histograma."
            )
            ctk.CTkLabel(
                self.scroll_timeline,
                text="Nenhum registro de data válido encontrado no disco.",
                text_color="#94a3b8",
                font=ctk.CTkFont(size=13),
            ).grid(row=0, column=0, padx=12, pady=28)
            return

        summary = self.last_scan_result.timeline_summary
        peak_yr = self.last_scan_result.peak_year
        self.lbl_timeline_summary.configure(text=summary)

        max_files = max((stat.total_files for stat in self.last_scan_result.timeline_stats), default=1) or 1

        for idx, stat in enumerate(self.last_scan_result.timeline_stats):
            self._create_timeline_year_row(idx, stat, peak_yr, max_files)

    def _create_timeline_year_row(
        self,
        row_idx: int,
        stat: YearActivityStats,
        peak_year: Optional[int],
        max_files: int,
    ) -> None:
        is_peak = (stat.year == peak_year)
        bg_color = ("#e0f2fe", "#172554") if is_peak else ("#f1f5f9", "#1e293b")

        row_card = ctk.CTkFrame(
            self.scroll_timeline,
            fg_color=bg_color,
            corner_radius=10,
            border_width=2 if is_peak else 0,
            border_color="#0284c7" if is_peak else "transparent",
        )
        row_card.grid(row=row_idx, column=0, padx=6, pady=4, sticky="ew")
        row_card.grid_columnconfigure(1, weight=1)

        # Coluna 0: Badge do Ano com destaque especial para Pico
        badge_frame = ctk.CTkFrame(row_card, fg_color="transparent")
        badge_frame.grid(row=0, column=0, rowspan=2, padx=(12, 8), pady=10)

        year_text = f"★ {stat.year} (PICO)" if is_peak else f"📅 {stat.year}"
        year_badge_color = "#d97706" if is_peak else "#0284c7"

        lbl_year = ctk.CTkLabel(
            badge_frame,
            text=f" {year_text} ",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=year_badge_color,
            text_color="#ffffff",
            corner_radius=6,
            width=130,
            height=30,
        )
        lbl_year.grid(row=0, column=0)

        # Coluna 1: Informações e Barra de Progresso Visual
        info_col = ctk.CTkFrame(row_card, fg_color="transparent")
        info_col.grid(row=0, column=1, rowspan=2, padx=8, pady=8, sticky="nsew")
        info_col.grid_columnconfigure(0, weight=1)

        # Linha superior de métricas
        metrics_text = (
            f"📄 Total: {stat.total_files:,} arquivos   •   📦 Volume: {stat.formatted_size}   •   "
            f"🖼️ Fotos: {stat.photos_count:,}   🎬 Vídeos: {stat.videos_count:,}   "
            f"📑 Docs: {stat.docs_count:,}   🎯 Críticos: {stat.critical_count:,}"
        )
        lbl_metrics = ctk.CTkLabel(
            info_col,
            text=metrics_text,
            font=ctk.CTkFont(size=12, weight="bold" if is_peak else "normal"),
            text_color="#f8fafc" if is_peak else "#cbd5e1",
            anchor="w",
        )
        lbl_metrics.grid(row=0, column=0, sticky="w", pady=(0, 4))

        # Barra visual proporcional
        bar = ctk.CTkProgressBar(info_col, height=8, corner_radius=4)
        bar.grid(row=1, column=0, sticky="ew", pady=(2, 2))
        progress_val = min(1.0, max(0.02, stat.total_files / max_files))
        bar.set(progress_val)
        if is_peak:
            bar.configure(progress_color="#eab308")
        else:
            bar.configure(progress_color="#38bdf8")

        # Coluna 2: Botão de ação rápida (Filtrar Arquivos Críticos deste ano na Aba 2)
        btn_filter_year = ctk.CTkButton(
            row_card,
            text=f"🎯 Ver Críticos de {stat.year}",
            width=175,
            height=30,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#334155",
            hover_color="#475569",
            command=lambda y=stat.year: self._navigate_to_crit_year(y),
        )
        btn_filter_year.grid(row=0, column=2, rowspan=2, padx=(6, 12), pady=10)

    def _navigate_to_crit_year(self, year: int) -> None:
        """Navega para a Aba 2 e filtra os itens pelo ano selecionado."""
        self.entry_crit_filter.delete(0, "end")
        self.entry_crit_filter.insert(0, str(year))
        self.opt_crit_category.set("Todos")
        self._trigger_crit_filter_reset()
        self.tabview.set("🎯 2. Arquivos Críticos (Agulhas no Palheiro)")

    def _render_errors_list(self) -> None:
        """Renderiza a Aba 4: Log de Erros / Bad Blocks."""
        self._clear_scrollable(self.scroll_errors)
        if not self.last_scan_result:
            return

        errors = self.last_scan_result.errors
        self.lbl_errors_summary.configure(
            text=f"Total de falhas registradas (Bad Blocks / Permissão Negada): {len(errors)}"
        )

        if not errors:
            ctk.CTkLabel(
                self.scroll_errors,
                text="✔ Nenhum erro de leitura ou Bad Block encontrado durante a varredura.",
                text_color="#4ade80",
                font=ctk.CTkFont(size=13, weight="bold"),
            ).grid(row=0, column=0, padx=12, pady=24)
            return

        for idx, err in enumerate(errors[:100]):
            self._create_error_row(idx, err)

    def _create_error_row(self, row_idx: int, err: ScanErrorEntry) -> None:
        row_frame = ctk.CTkFrame(self.scroll_errors, fg_color=("#f1f5f9", "#1e293b"), corner_radius=8)
        row_frame.grid(row=row_idx, column=0, columnspan=3, padx=4, pady=4, sticky="ew")
        row_frame.grid_columnconfigure(1, weight=1)

        is_bad_block = "BAD BLOCK" in err.error_type.upper()
        badge_bg = "#dc2626" if is_bad_block else "#d97706"

        ctk.CTkLabel(
            row_frame,
            text=f" {err.timestamp} | {err.error_type} ",
            fg_color=badge_bg,
            text_color="#ffffff",
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=28,
        ).grid(row=0, column=0, rowspan=2, padx=10, pady=8)

        info_col = ctk.CTkFrame(row_frame, fg_color="transparent")
        info_col.grid(row=0, column=1, rowspan=2, padx=6, pady=6, sticky="nsew")
        info_col.grid_columnconfigure(0, weight=1)

        lbl_path = ctk.CTkLabel(
            info_col,
            text=err.path,
            font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            text_color="#f8fafc",
            anchor="w",
        )
        lbl_path.grid(row=0, column=0, sticky="w")

        lbl_msg = ctk.CTkLabel(
            info_col,
            text=err.message,
            font=ctk.CTkFont(size=11),
            text_color="#fca5a5",
            anchor="w",
        )
        lbl_msg.grid(row=1, column=0, sticky="w")

        btn_copy = ctk.CTkButton(
            row_frame,
            text="📋 Copiar",
            width=80,
            height=28,
            fg_color="#334155",
            hover_color="#475569",
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        btn_copy.configure(
            command=lambda p=err.path, b=btn_copy: self.copy_to_clipboard(p, b, "📋 Copiar", "#334155")
        )
        btn_copy.grid(row=0, column=2, rowspan=2, padx=(6, 12), pady=8)

    def _copy_all_errors_to_clipboard(self) -> None:
        """Exporta o relatório consolidado de erros para a área de transferência."""
        if not self.last_scan_result or not self.last_scan_result.errors:
            messagebox.showinfo("Sem Erros", "Nenhum erro de leitura registrado para copiar.")
            return

        lines = [
            f"Relatório de Erros e Possíveis Bad Blocks - Geio DiskRadar",
            f"Unidade: {self.current_target_path}",
            f"Total de ocorrências: {len(self.last_scan_result.errors)}",
            "=" * 70,
        ]
        for err in self.last_scan_result.errors:
            lines.append(f"[{err.timestamp}] {err.error_type}: {err.path}")
            lines.append(f"   Mensagem: {err.message}")
            lines.append("-" * 70)

        report_txt = "\n".join(lines)
        self.copy_to_clipboard(report_txt, self.btn_copy_errors, "📋 Copiar Relatório de Erros", "#334155")

    # ==========================================================================
    # EXPORTAÇÃO DO CATÁLOGO DE AUTÓPSIA (RELATÓRIO HTML)
    # ==========================================================================
    def export_html_catalog(self) -> None:
        """Abre diálogo para salvar o Relatório HTML Autocontido com nome sugerido."""
        if not self.current_badge:
            messagebox.showwarning("Sem Disco Selecionado", "Selecione uma unidade antes de exportar o relatório.")
            return

        default_name = build_default_report_filename(self.current_badge)
        save_path = filedialog.asksaveasfilename(
            title="Salvar Catálogo de Autópsia HTML do Disco",
            initialfile=default_name,
            defaultextension=".html",
            filetypes=[("Relatório HTML Autocontido", "*.html"), ("Todos os Arquivos", "*.*")],
        )
        if not save_path:
            return

        try:
            saved = export_html_report(
                output_path=save_path,
                badge=self.current_badge,
                scan_result=self.last_scan_result,
            )
            messagebox.showinfo(
                "Relatório HTML Gerado",
                f"Catálogo de Autópsia exportado com sucesso!\n\nArquivo:\n{saved}",
            )
            open_in_explorer(saved, select_item=True)
        except Exception as exc:
            messagebox.showerror(
                "Erro ao Exportar HTML",
                f"Não foi possível salvar o relatório HTML:\n{exc}",
            )
