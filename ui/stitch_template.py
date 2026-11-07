"""
Template HTML5 + Tailwind CSS + JS Unificado da Interface Google Stitch "Cyber-Forensic Precision" (v2.2.0).
Integra todas as 10 telas e modais em uma Single-Page Application Desktop ultrarrápida conectada ao backend Python.
"""

STITCH_SPA_HTML = r"""<!DOCTYPE html>
<html class="dark" lang="pt-BR">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Geio DiskRadar v2.2.0 — Cyber-Forensic Precision (100% Read-Only)</title>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com"></script>
<script id="tailwind-config">
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "on-error-container": "#ffdad6",
        "on-background": "#e2e2eb",
        "tertiary-container": "#ffcdcf",
        "on-secondary-fixed-variant": "#005236",
        "on-secondary-container": "#00311f",
        "on-error": "#690005",
        "on-primary-fixed": "#002022",
        "surface-container-low": "#191b22",
        "inverse-surface": "#e2e2eb",
        "surface-bright": "#373940",
        "primary": "#dbfcff",
        "on-surface-variant": "#b9cacb",
        "primary-fixed": "#7df4ff",
        "inverse-on-surface": "#2e3037",
        "on-secondary": "#003824",
        "outline": "#849495",
        "surface-variant": "#33343b",
        "surface-dim": "#111319",
        "surface": "#111319",
        "on-primary-container": "#006970",
        "on-tertiary-fixed-variant": "#92002a",
        "inverse-primary": "#006970",
        "surface-container-lowest": "#0c0e14",
        "surface-container-highest": "#33343b",
        "background": "#111319",
        "surface-tint": "#00dbe9",
        "primary-fixed-dim": "#00dbe9",
        "on-secondary-fixed": "#002113",
        "surface-container-high": "#282a30",
        "secondary": "#4edea3",
        "error": "#ffb4ab",
        "tertiary-fixed-dim": "#ffb2b7",
        "tertiary": "#fff3f2",
        "on-tertiary": "#67001b",
        "secondary-fixed": "#6ffbbe",
        "surface-container": "#1e1f26",
        "on-tertiary-container": "#bc0b3b",
        "on-tertiary-fixed": "#40000d",
        "error-container": "#93000a",
        "on-primary": "#00363a",
        "primary-container": "#00f0ff",
        "secondary-container": "#00a572",
        "secondary-fixed-dim": "#4edea3",
        "on-primary-fixed-variant": "#004f54",
        "outline-variant": "#3b494b",
        "on-surface": "#e2e2eb",
        "tertiary-fixed": "#ffdadb"
      },
      borderRadius: {
        "DEFAULT": "0.125rem",
        "lg": "0.25rem",
        "xl": "0.5rem",
        "full": "0.75rem"
      },
      spacing: {
        "gutter": "0.5rem",
        "space-md": "0.5rem",
        "space-xs": "0.125rem",
        "space-xl": "1rem",
        "margin": "0.75rem",
        "space-2xl": "1.5rem",
        "gutter-dense": "0.25rem",
        "space-sm": "0.25rem",
        "space-lg": "0.75rem"
      },
      fontFamily: {
        "label-badge": ["JetBrains Mono", "Consolas", "monospace"],
        "headline-xl": ["Inter", "Segoe UI", "sans-serif"],
        "headline-lg": ["Inter", "Segoe UI", "sans-serif"],
        "body-lg": ["Inter", "Segoe UI", "sans-serif"],
        "data-mono-sm": ["JetBrains Mono", "Consolas", "monospace"],
        "data-mono-md": ["JetBrains Mono", "Consolas", "monospace"],
        "body-sm": ["Inter", "Segoe UI", "sans-serif"],
        "headline-sm": ["Inter", "Segoe UI", "sans-serif"],
        "data-mono-lg": ["JetBrains Mono", "Consolas", "monospace"],
        "body-md": ["Inter", "Segoe UI", "sans-serif"],
        "label-caps": ["JetBrains Mono", "Consolas", "monospace"]
      },
      fontSize: {
        "label-badge": ["11px", { lineHeight: "14px", fontWeight: "600" }],
        "headline-xl": ["24px", { lineHeight: "32px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "headline-lg": ["18px", { lineHeight: "24px", letterSpacing: "-0.015em", fontWeight: "600" }],
        "body-lg": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "data-mono-sm": ["11px", { lineHeight: "14px", fontWeight: "400" }],
        "data-mono-md": ["12px", { lineHeight: "16px", letterSpacing: "-0.01em", fontWeight: "400" }],
        "body-sm": ["12px", { lineHeight: "16px", fontWeight: "400" }],
        "headline-sm": ["14px", { lineHeight: "20px", letterSpacing: "-0.01em", fontWeight: "600" }],
        "data-mono-lg": ["13px", { lineHeight: "18px", letterSpacing: "-0.02em", fontWeight: "500" }],
        "body-md": ["13px", { lineHeight: "18px", fontWeight: "400" }],
        "label-caps": ["10px", { lineHeight: "12px", letterSpacing: "0.08em", fontWeight: "600" }]
      }
    }
  }
};
</script>
<style>
  /* Regras de precisão Cyber-Forensic e resiliência offline */
  .hidden { display: none !important; }
  
  html, body {
    margin: 0;
    padding: 0;
    background-color: #0c0e14;
    color: #e2e2eb;
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    overscroll-behavior: none;
  }
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #0c0e14; }
  ::-webkit-scrollbar-thumb { background: #33343b; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #00dbe9; }
  .mono-font { font-family: 'JetBrains Mono', 'Consolas', monospace; }
  .tab-panel { display: none; }
  .tab-panel.active { display: flex; flex-direction: column; }

  /* Fallback offline: garante integridade visual mesmo em bancada sem internet */
  .bg-surface-container-lowest { background-color: #0c0e14; }
  .bg-surface-container-low { background-color: #191b22; }
  .bg-surface-container { background-color: #1e1f26; }
  .bg-surface-container-high { background-color: #282a30; }
  .bg-surface-container-highest { background-color: #33343b; }
  .text-primary { color: #00f0ff; }
  .text-secondary { color: #4edea3; }
  .text-error { color: #ffb4ab; }
  .text-on-surface { color: #e2e2eb; }
  .text-on-surface-variant { color: #849495; }
</style>
</head>
<body class="bg-surface-container-lowest font-body-md text-on-surface select-none antialiased">

<!-- TOAST FLUTUANTE DE NOTIFICAÇÃO FORENSE -->
<div id="toast-clipboard" class="fixed bottom-10 right-6 z-[90] transform translate-y-16 opacity-0 transition-all duration-200 pointer-events-none flex items-center gap-space-sm bg-surface-bright text-primary px-space-md py-space-sm rounded shadow-2xl border border-primary/30">
  <span class="material-symbols-outlined text-[16px] text-secondary">check_circle</span>
  <span id="toast-text" class="font-data-mono-sm text-data-mono-sm">Operação concluída com integridade forense!</span>
</div>

<!-- ============================================================================
     HEADER GLOBAL FIXO (BARRA DE TÍTULO + CONTROLES + TELEMETRIA + 7 ABAS)
     ============================================================================ -->
<header class="fixed top-0 left-0 right-0 z-40 flex flex-col bg-surface-container-low shadow-[0_2px_10px_rgba(0,0,0,0.75)]">
  <!-- Linha 1: Barra de Status de Segurança Read-Only -->
  <div class="h-7 bg-surface-container-lowest flex items-center justify-between px-space-md border-b border-outline-variant/20">
    <div class="flex items-center gap-space-md">
      <span class="material-symbols-outlined text-primary-fixed-dim text-[15px]">radar</span>
      <span class="font-label-caps text-label-caps uppercase tracking-wider text-on-surface-variant">Geio DiskRadar // Workstation Engine v2.2.0</span>
      <div class="flex items-center gap-space-xs px-space-sm py-0.5 rounded bg-surface-container-high">
        <span class="h-1.5 w-1.5 rounded-full bg-secondary animate-pulse"></span>
        <span class="font-label-caps text-label-caps uppercase text-secondary font-bold">100% READ-ONLY SAFEGUARD ACTIVE</span>
      </div>
      <div id="header-scan-badge" class="hidden items-center gap-space-xs px-space-sm py-0.5 rounded bg-primary-container/20 text-primary-fixed">
        <span class="font-label-caps text-label-caps uppercase font-bold" id="header-scan-badge-text">EM VARREDURA</span>
      </div>
    </div>
    <div class="flex items-center gap-space-xs">
      <button onclick="openDiagnosticsModal()" class="h-6 px-space-sm flex items-center gap-1 rounded bg-surface-container hover:bg-surface-container-high text-primary font-label-caps text-label-caps uppercase transition-colors" title="Autoteste de Compatibilidade do Sistema Operacional">
        <span class="material-symbols-outlined text-[13px]">health_and_safety</span>
        <span>Diagnóstico</span>
      </button>
      <button onclick="openSmartModal()" class="h-6 px-space-sm flex items-center gap-1 rounded bg-surface-container hover:bg-surface-container-high text-primary-fixed font-label-caps text-label-caps uppercase transition-colors" title="Abrir Diagnóstico S.M.A.R.T. Avançado">
        <span class="material-symbols-outlined text-[13px]">neurology</span>
        <span>S.M.A.R.T. Raw</span>
      </button>
      <button onclick="openHexModal('')" class="h-6 px-space-sm flex items-center gap-1 rounded bg-surface-container hover:bg-surface-container-high text-secondary font-label-caps text-label-caps uppercase transition-colors" title="Abrir Inspecionador Hexadecimal Read-Only">
        <span class="material-symbols-outlined text-[13px]">biotech</span>
        <span>Hex Viewer</span>
      </button>
      <button onclick="shutdownApp()" class="h-7 w-9 flex items-center justify-center text-on-surface-variant hover:bg-error-container hover:text-on-error-container transition-colors" title="Encerrar Aplicação" type="button">
        <span class="material-symbols-outlined text-[14px]">close</span>
      </button>
    </div>
  </div>

  <!-- Linha 2: Seletor de Unidade e Botões Principais de Ação -->
  <div class="h-12 bg-surface-container flex items-center justify-between px-space-md gap-space-md">
    <div class="flex items-center gap-space-md flex-1 min-w-0">
      <div class="flex items-center gap-space-xs shrink-0">
        <span class="font-headline-sm text-headline-sm text-primary tracking-tight font-bold">Geio DiskRadar</span>
        <span class="font-data-mono-sm text-data-mono-sm text-primary-fixed bg-surface-container-high px-space-xs py-0.5 rounded font-bold">v2.2.0</span>
      </div>
      <!-- Dropdown de Unidades -->
      <div class="flex items-center gap-space-xs bg-surface-container-lowest px-space-sm py-1 rounded w-80 max-w-full border border-outline-variant/30">
        <span class="material-symbols-outlined text-primary-fixed-dim text-[16px]">hard_drive</span>
        <select id="drive-select" onchange="onDriveSelected(this.value)" class="bg-transparent text-on-surface font-data-mono-md text-data-mono-md outline-none w-full cursor-pointer">
          <option value="">Carregando unidades...</option>
        </select>
      </div>
      <button onclick="refreshDrives()" class="flex items-center gap-space-xs px-space-sm py-1 bg-surface-container-high hover:bg-surface-variant text-on-surface-variant hover:text-on-surface rounded transition-colors text-body-sm font-body-sm shrink-0" title="Atualizar Unidades e S.M.A.R.T." type="button">
        <span class="material-symbols-outlined text-[15px]">refresh</span>
        <span>Atualizar</span>
      </button>
      <button onclick="pickManualFolder()" class="flex items-center gap-space-xs px-space-sm py-1 bg-surface-container-high hover:bg-surface-variant text-on-surface-variant hover:text-on-surface rounded transition-colors text-body-sm font-body-sm shrink-0" title="Escolher Pasta Manual" type="button">
        <span class="material-symbols-outlined text-[15px]">folder_open</span>
        <span>Pasta Manual</span>
      </button>
    </div>

    <div class="flex items-center gap-space-sm shrink-0">
      <button id="btn-start-scan" onclick="startScan()" class="flex items-center gap-space-xs px-space-md py-1.5 rounded bg-secondary-container hover:bg-secondary text-on-secondary-container hover:text-on-secondary transition-colors font-headline-sm text-headline-sm font-bold shadow-[0_0_8px_rgba(78,222,163,0.25)]" type="button">
        <span class="material-symbols-outlined text-[16px]">play_arrow</span>
        <span id="btn-start-scan-text">Iniciar Varredura</span>
      </button>
      <button id="btn-stop-scan" onclick="stopScan()" class="flex items-center gap-space-xs px-space-md py-1.5 rounded bg-error-container hover:bg-error text-on-error-container hover:text-on-error transition-colors font-headline-sm text-headline-sm font-semibold opacity-60" type="button">
        <span class="material-symbols-outlined text-[16px]">stop</span>
        <span>Parar</span>
      </button>
      <button onclick="openExportModal()" class="flex items-center gap-space-xs px-space-md py-1.5 rounded bg-surface-container-high hover:bg-surface-variant text-primary hover:text-primary-container transition-colors font-headline-sm text-headline-sm font-semibold" type="button">
        <span class="material-symbols-outlined text-[16px]">description</span>
        <span>Exportar Relatório</span>
      </button>
    </div>
  </div>

  <!-- Linha 3: Barra de Telemetria Instantânea de Leitura -->
  <div class="h-8 bg-surface-container-lowest flex items-center justify-between px-space-md gap-space-md font-data-mono-sm text-data-mono-sm border-y border-outline-variant/20">
    <div class="flex items-center gap-space-sm min-w-0 flex-1">
      <span class="font-label-caps text-label-caps uppercase text-primary font-bold shrink-0">Status / Lendo:</span>
      <span id="top-current-dir" class="text-on-surface-variant truncate font-data-mono-sm text-data-mono-sm">Aguardando comando de varredura...</span>
    </div>
    <div class="flex items-center gap-space-md shrink-0">
      <div class="flex items-center gap-space-xs"><span class="text-on-surface-variant">Tempo:</span><span id="top-elapsed" class="text-on-surface font-semibold">00:00:00</span></div>
      <div class="h-3 w-px bg-outline-variant"></div>
      <div class="flex items-center gap-space-xs"><span class="text-on-surface-variant">Arquivos:</span><span id="top-files" class="text-secondary font-semibold">0</span></div>
      <div class="h-3 w-px bg-outline-variant"></div>
      <div class="flex items-center gap-space-xs"><span class="text-on-surface-variant">Pastas:</span><span id="top-dirs" class="text-on-surface font-semibold">0</span></div>
      <div class="h-3 w-px bg-outline-variant"></div>
      <div class="flex items-center gap-space-xs"><span class="text-on-surface-variant">Pastas Quentes:</span><span id="top-hot" class="text-primary-fixed font-semibold">0</span></div>
      <div class="h-3 w-px bg-outline-variant"></div>
      <div class="flex items-center gap-space-xs"><span class="text-on-surface-variant">Críticos:</span><span id="top-crit" class="text-error font-semibold">0</span></div>
      <div class="h-3 w-px bg-outline-variant"></div>
      <div class="flex items-center gap-space-xs"><span class="text-on-surface-variant">Erros/Bad:</span><span id="top-err" class="text-on-surface-variant font-semibold">0</span></div>
    </div>
  </div>

  <!-- Linha 4: Barra de Navegação das 7 Visões Forenses -->
  <nav class="h-9 bg-surface-container-low flex items-center px-space-md gap-space-xs overflow-x-auto">
    <button onclick="switchTab('pastas-quentes')" id="nav-pastas-quentes" class="nav-tab h-8 px-space-md flex items-center gap-space-xs rounded-t transition-colors bg-surface-container-high text-primary font-bold shrink-0" type="button">
      <span class="material-symbols-outlined text-[15px]">local_fire_department</span>
      <span>Pastas Quentes (Mídia &amp; Docs)</span>
      <span id="badge-nav-hot" class="bg-surface-container px-space-xs py-0.5 rounded font-label-badge text-label-badge text-primary">0</span>
    </button>
    <button onclick="switchTab('arquivos-criticos')" id="nav-arquivos-criticos" class="nav-tab h-8 px-space-md flex items-center gap-space-xs text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface rounded-t transition-colors font-body-sm text-body-sm shrink-0" type="button">
      <span class="material-symbols-outlined text-[15px] text-error">emergency</span>
      <span>Arquivos Críticos / Agulhas no Palheiro</span>
      <span id="badge-nav-crit" class="bg-error-container text-on-error-container px-space-xs py-0.5 rounded font-label-badge text-label-badge">0</span>
    </button>
    <button onclick="switchTab('usuarios-atalhos')" id="nav-usuarios-atalhos" class="nav-tab h-8 px-space-md flex items-center gap-space-xs text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface rounded-t transition-colors font-body-sm text-body-sm shrink-0" type="button">
      <span class="material-symbols-outlined text-[15px]">manage_accounts</span>
      <span>Usuários &amp; Atalhos Rápidos</span>
      <span id="badge-nav-users" class="bg-surface-container px-space-xs py-0.5 rounded font-label-badge text-label-badge text-on-surface-variant">0</span>
    </button>
    <button onclick="switchTab('linha-do-tempo')" id="nav-linha-do-tempo" class="nav-tab h-8 px-space-md flex items-center gap-space-xs text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface rounded-t transition-colors font-body-sm text-body-sm shrink-0" type="button">
      <span class="material-symbols-outlined text-[15px]">calendar_clock</span>
      <span>Linha do Tempo Anual (Timeline)</span>
    </button>
    <button onclick="switchTab('log-erros')" id="nav-log-erros" class="nav-tab h-8 px-space-md flex items-center gap-space-xs text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface rounded-t transition-colors font-body-sm text-body-sm shrink-0" type="button">
      <span class="material-symbols-outlined text-[15px]">report_problem</span>
      <span>Log de Erros / Bad Blocks</span>
      <span id="badge-nav-err" class="bg-surface-container px-space-xs py-0.5 rounded font-label-badge text-label-badge text-on-surface-variant">0</span>
    </button>
    <button onclick="switchTab('live-monitor')" id="nav-live-monitor" class="nav-tab h-8 px-space-md flex items-center gap-space-xs text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface rounded-t transition-colors font-body-sm text-body-sm shrink-0" type="button">
      <span class="material-symbols-outlined text-[15px] text-primary-fixed-dim">terminal</span>
      <span>Monitor Ao Vivo (Live Scan)</span>
    </button>
    <button onclick="switchTab('resumo-pos-varredura')" id="nav-resumo-pos-varredura" class="nav-tab h-8 px-space-md flex items-center gap-space-xs text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface rounded-t transition-colors font-body-sm text-body-sm shrink-0" type="button">
      <span class="material-symbols-outlined text-[15px] text-secondary">verified</span>
      <span>Resumo Executivo Pós-Varredura</span>
    </button>
  </nav>
</header>

<!-- ============================================================================
     CONTEÚDO PRINCIPAL (CRACHÁ DO DISCO + 7 PAINÉIS DE VISÃO)
     ============================================================================ -->
<main class="w-full pt-[146px] pb-12 bg-surface-container-lowest min-h-screen">
  <div class="flex flex-col w-full px-space-md py-space-sm gap-space-md">

    <!-- 1. CRACHÁ FORENSE GLOBAL DE HARDWARE (SEMPRE VISÍVEL NO TOPO) -->
    <section class="w-full bg-surface-container-low rounded p-space-md flex flex-col lg:flex-row lg:items-center justify-between gap-space-md shadow-md border border-outline-variant/20">
      <div class="flex items-center gap-space-lg min-w-0">
        <div class="h-11 w-11 rounded bg-surface-container-highest flex items-center justify-center shrink-0 text-primary-fixed-dim">
          <span class="material-symbols-outlined text-[26px]">developer_board</span>
        </div>
        <div class="flex flex-col min-w-0">
          <div class="flex items-center gap-space-sm flex-wrap">
            <span id="badge-model" class="font-headline-sm text-headline-sm text-primary font-bold tracking-tight">Carregando Hardware...</span>
            <span id="badge-mount" class="font-label-badge text-label-badge bg-surface-container text-on-surface-variant px-space-xs py-0.5 rounded">DRIVE</span>
            <span id="badge-smart-pill" class="font-label-badge text-label-badge bg-secondary-container text-on-secondary-container px-space-xs py-0.5 rounded flex items-center gap-1 font-bold">
              <span class="h-1.5 w-1.5 rounded-full bg-secondary"></span>
              <span id="badge-smart-text">S.M.A.R.T.: OK</span>
            </span>
            <span id="badge-fs" class="font-label-badge text-label-badge bg-primary-container text-on-primary-container px-space-xs py-0.5 rounded font-bold">NTFS</span>
          </div>
          <div class="flex items-center gap-space-md mt-1 text-on-surface-variant font-data-mono-sm text-data-mono-sm flex-wrap">
            <span>SERIAL: <strong id="badge-serial" class="text-on-surface select-all">N/A</strong></span>
            <button onclick="copySerialNumber()" class="px-1.5 py-0.2 bg-surface-container hover:bg-surface-variant text-primary-fixed rounded text-[10px] font-label-caps uppercase" type="button">Copiar S/N</button>
            <span class="text-outline-variant">•</span>
            <span>HORAS/CICLOS: <strong id="badge-poh" class="text-on-surface">N/A</strong></span>
            <span class="text-outline-variant">•</span>
            <span>USUÁRIOS: <strong id="badge-users" class="text-primary">N/A</strong></span>
            <span class="text-outline-variant">•</span>
            <span>ÚLTIMO USO: <strong id="badge-last-date" class="text-secondary">N/A</strong></span>
            <span class="text-outline-variant">•</span>
            <span>TEMP: <strong id="badge-temp" class="text-secondary">34°C</strong></span>
          </div>
        </div>
      </div>

      <!-- Barra de Capacidade e Botão Diag Raw -->
      <div class="flex items-center gap-space-lg shrink-0 lg:border-l border-surface-container-highest lg:pl-space-lg">
        <div class="flex flex-col items-end">
          <div class="flex items-baseline gap-space-xs">
            <span id="badge-used-gb" class="font-data-mono-lg text-data-mono-lg text-primary font-bold">0 GB</span>
            <span id="badge-total-gb" class="font-data-mono-sm text-data-mono-sm text-on-surface-variant">/ 0 GB</span>
          </div>
          <span id="badge-pct-label" class="font-label-caps text-label-caps uppercase text-on-surface-variant">Capacidade em Uso (0%)</span>
          <div class="w-48 h-2 bg-surface-container-lowest rounded-full overflow-hidden mt-1 relative">
            <div id="badge-cap-bar" class="h-full bg-gradient-to-r from-secondary to-primary-container transition-all duration-300" style="width: 0%;"></div>
          </div>
        </div>
        <button onclick="openSmartModal()" class="h-8 px-space-sm bg-surface-container hover:bg-surface-variant text-primary rounded flex items-center gap-space-xs transition-colors font-body-sm text-body-sm font-semibold shrink-0 border border-primary/30" title="Abrir Diagnóstico S.M.A.R.T. Avançado" type="button">
          <span class="material-symbols-outlined text-[16px]">query_stats</span>
          <span>Diag Raw</span>
        </button>
      </div>
    </section>

    <!-- Banner de Alerta S.M.A.R.T. (Visível apenas se o disco apresentar risco físico) -->
    <div id="smart-warning-banner" class="hidden w-full bg-error-container/30 border-l-4 border-error px-space-md py-space-sm rounded items-center justify-between gap-space-md">
      <div class="flex items-center gap-space-sm">
        <span class="material-symbols-outlined text-error text-[20px]">warning</span>
        <span class="font-body-md text-body-md text-on-error-container">
          <strong>ALERTA FÍSICO S.M.A.R.T. DETECTADO:</strong> Este disco apresenta setores realocados/pendentes ou falha preditiva! Priorize salvar <strong>Arquivos Críticos / Documentos leves</strong> antes de copiar vídeos pesados.
        </span>
      </div>
      <button onclick="openSmartModal()" class="px-space-sm py-1 rounded bg-error text-on-error font-label-caps text-label-caps uppercase font-bold shrink-0" type="button">Ver S.M.A.R.T.</button>
    </div>

    <!-- ========================================================================
         TELA 1: PASTAS QUENTES (MÍDIA & DOCS)
         ======================================================================== -->
    <div id="panel-pastas-quentes" class="tab-panel active gap-space-md">
      <!-- KPIs Bento -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-space-md">
        <div class="bg-surface-container-low rounded p-space-md flex items-center justify-between shadow-sm">
          <div class="flex flex-col min-w-0">
            <span class="font-label-caps text-label-caps text-secondary font-bold uppercase tracking-wider">Total de Fotos (&gt;50KB)</span>
            <span id="kpi-hot-photos" class="font-data-mono-lg text-headline-sm text-on-surface font-bold mt-0.5">0 fotos</span>
            <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-0.5">.jpg, .png, .heic, .raw</span>
          </div>
          <div class="h-9 w-9 rounded bg-secondary-container/20 flex items-center justify-center text-secondary shrink-0">
            <span class="material-symbols-outlined text-[20px]">photo_camera</span>
          </div>
        </div>
        <div class="bg-surface-container-low rounded p-space-md flex items-center justify-between shadow-sm">
          <div class="flex flex-col min-w-0">
            <span class="font-label-caps text-label-caps text-tertiary-fixed-dim font-bold uppercase tracking-wider">Total de Vídeos (&gt;500KB)</span>
            <span id="kpi-hot-videos" class="font-data-mono-lg text-headline-sm text-on-surface font-bold mt-0.5">0 vídeos</span>
            <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-0.5">.mp4, .mov, .mkv, .avi</span>
          </div>
          <div class="h-9 w-9 rounded bg-tertiary-container/20 flex items-center justify-center text-tertiary-fixed-dim shrink-0">
            <span class="material-symbols-outlined text-[20px]">videocam</span>
          </div>
        </div>
        <div class="bg-surface-container-low rounded p-space-md flex items-center justify-between shadow-sm">
          <div class="flex flex-col min-w-0">
            <span class="font-label-caps text-label-caps text-primary-fixed-dim font-bold uppercase tracking-wider">Documentos Pessoais/Trabalho</span>
            <span id="kpi-hot-docs" class="font-data-mono-lg text-headline-sm text-on-surface font-bold mt-0.5">0 docs</span>
            <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-0.5">.pdf, .docx, .xlsx, .pptx</span>
          </div>
          <div class="h-9 w-9 rounded bg-primary-container/20 flex items-center justify-center text-primary-fixed-dim shrink-0">
            <span class="material-symbols-outlined text-[20px]">description</span>
          </div>
        </div>
        <div class="bg-surface-container-low rounded p-space-md flex items-center justify-between shadow-sm">
          <div class="flex flex-col min-w-0">
            <span class="font-label-caps text-label-caps text-primary font-bold uppercase tracking-wider">Volume Acumulado Quente</span>
            <span id="kpi-hot-volume" class="font-data-mono-lg text-headline-sm text-primary font-bold mt-0.5">0 B</span>
            <span id="kpi-hot-count-sub" class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-0.5">0 diretórios relevantes</span>
          </div>
          <div class="h-9 w-9 rounded bg-surface-container-highest flex items-center justify-center text-primary shrink-0">
            <span class="material-symbols-outlined text-[20px]">folder_special</span>
          </div>
        </div>
      </div>

      <!-- Barra de Filtros e Ordenação de Pastas Quentes -->
      <div class="bg-surface-container-low p-space-md rounded flex flex-col md:flex-row md:items-center justify-between gap-space-md shadow-sm">
        <div class="flex items-center gap-space-xs overflow-x-auto" id="hot-cat-buttons">
          <button onclick="setHotCategory('ALL')" data-cat="ALL" class="hot-cat-btn h-7 px-space-md rounded font-label-badge text-label-badge bg-primary text-on-primary font-bold transition-colors shrink-0" type="button">TODAS</button>
          <button onclick="setHotCategory('FOTOS')" data-cat="FOTOS" class="hot-cat-btn h-7 px-space-md rounded font-label-badge text-label-badge bg-surface-container text-secondary hover:bg-surface-container-high transition-colors shrink-0" type="button">FOTOS</button>
          <button onclick="setHotCategory('VIDEOS')" data-cat="VIDEOS" class="hot-cat-btn h-7 px-space-md rounded font-label-badge text-label-badge bg-surface-container text-tertiary-fixed-dim hover:bg-surface-container-high transition-colors shrink-0" type="button">VÍDEOS</button>
          <button onclick="setHotCategory('DOCS')" data-cat="DOCS" class="hot-cat-btn h-7 px-space-md rounded font-label-badge text-label-badge bg-surface-container text-primary-fixed-dim hover:bg-surface-container-high transition-colors shrink-0" type="button">DOCS</button>
          <button onclick="setHotCategory('MISTO')" data-cat="MISTO" class="hot-cat-btn h-7 px-space-md rounded font-label-badge text-label-badge bg-surface-container text-on-surface hover:bg-surface-container-high transition-colors shrink-0" type="button">MISTO</button>
        </div>
        <div class="flex items-center gap-space-md shrink-0 flex-wrap">
          <div class="relative w-64">
            <input id="hot-search-input" oninput="renderHotFolders()" class="w-full h-7 pl-7 pr-space-sm bg-surface-container-lowest text-on-surface font-body-sm text-body-sm rounded outline-none focus:bg-surface-container-high transition-colors" placeholder="Filtrar pasta por nome ou caminho..." type="text"/>
            <span class="material-symbols-outlined absolute left-1.5 top-1.5 text-on-surface-variant text-[15px] pointer-events-none">search</span>
          </div>
          <div class="flex items-center gap-space-xs bg-surface-container-lowest px-space-sm h-7 rounded shrink-0">
            <span class="material-symbols-outlined text-on-surface-variant text-[15px]">sort</span>
            <select id="hot-sort-select" onchange="renderHotFolders()" class="bg-transparent text-on-surface font-data-mono-sm text-data-mono-sm outline-none cursor-pointer">
              <option class="bg-surface-container-low text-on-surface" value="score">Ordenar por: Score Forense (Relevância)</option>
              <option class="bg-surface-container-low text-on-surface" value="volume">Ordenar por: Maior Volume (Bytes)</option>
              <option class="bg-surface-container-low text-on-surface" value="files">Ordenar por: Quantidade de Arquivos</option>
              <option class="bg-surface-container-low text-on-surface" value="recent">Ordenar por: Modificação Mais Recente</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Lista de Cards de Pastas Quentes -->
      <div id="hot-folders-list" class="flex flex-col gap-space-xs"></div>
    </div>

    <!-- ========================================================================
         TELA 2: ARQUIVOS CRÍTICOS / AGULHAS NO PALHEIRO
         ======================================================================== -->
    <div id="panel-arquivos-criticos" class="tab-panel gap-space-md">
      <div class="bg-surface-container-low p-space-sm rounded flex flex-col md:flex-row items-stretch md:items-center justify-between gap-space-md">
        <div class="flex-1 flex items-center bg-surface-container-lowest rounded px-space-sm py-1.5">
          <span class="material-symbols-outlined text-outline text-[18px] mr-space-xs shrink-0">filter_alt</span>
          <input id="crit-search-input" oninput="renderCriticalItems()" class="bg-transparent text-on-surface placeholder:text-on-surface-variant font-body-md text-body-md w-full outline-none" placeholder="Filtrar agulhas por nome, extensão, motivo heurístico ou caminho..." type="text"/>
        </div>
        <div class="flex items-center gap-space-xs shrink-0">
          <span class="font-label-caps text-label-caps uppercase text-on-surface-variant">Ordenar por:</span>
          <div class="bg-surface-container-lowest px-space-sm py-1 rounded flex items-center">
            <select id="crit-sort-select" onchange="renderCriticalItems()" class="bg-transparent text-primary font-data-mono-sm text-data-mono-sm outline-none cursor-pointer">
              <option class="bg-surface-container-low text-on-surface" value="date_desc">Data de Modificação (Mais Recente)</option>
              <option class="bg-surface-container-low text-on-surface" value="size_desc">Tamanho (Maior → Menor)</option>
              <option class="bg-surface-container-low text-on-surface" value="name_asc">Nome de Arquivo (A → Z)</option>
            </select>
          </div>
        </div>
        <div class="flex items-center gap-space-xs text-on-surface-variant font-data-mono-sm text-data-mono-sm shrink-0 bg-surface-container px-space-sm py-1 rounded">
          <span class="w-1.5 h-1.5 rounded-full bg-secondary"></span>
          <span id="crit-display-count" class="text-on-surface font-semibold">0 itens</span>
        </div>
      </div>

      <!-- Pílulas de Categoria Forense -->
      <div class="flex items-center gap-space-xs overflow-x-auto pb-1" id="crit-cat-pills">
        <button onclick="setCritCategory('ALL')" data-cat="ALL" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-primary-fixed-dim text-on-primary-fixed font-headline-sm text-headline-sm font-semibold shrink-0" type="button">Todas</button>
        <button onclick="setCritCategory('CRYPTO_WALLETS')" data-cat="CRYPTO_WALLETS" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-surface-container-low text-on-surface-variant hover:text-error font-body-sm text-body-sm shrink-0" type="button">🔑 Cripto &amp; Carteiras</button>
        <button onclick="setCritCategory('BROWSERS_CREDS')" data-cat="BROWSERS_CREDS" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-surface-container-low text-on-surface-variant hover:text-primary font-body-sm text-body-sm shrink-0" type="button">🌐 Navegadores &amp; Sessões</button>
        <button onclick="setCritCategory('KEYWORDS')" data-cat="KEYWORDS" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-surface-container-low text-on-surface-variant hover:text-tertiary-fixed-dim font-body-sm text-body-sm shrink-0" type="button">🕵️ Senhas/Keywords</button>
        <button onclick="setCritCategory('CAD_DESIGN')" data-cat="CAD_DESIGN" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-surface-container-low text-on-surface-variant hover:text-primary-fixed font-body-sm text-body-sm shrink-0" type="button">📐 Engenharia/CAD/Design</button>
        <button onclick="setCritCategory('IRPF_FISCAL')" data-cat="IRPF_FISCAL" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-surface-container-low text-on-surface-variant hover:text-secondary font-body-sm text-body-sm shrink-0" type="button">🧾 Contábil/IRPF/XML</button>
        <button onclick="setCritCategory('CERT_KEYS')" data-cat="CERT_KEYS" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-surface-container-low text-on-surface-variant hover:text-secondary font-body-sm text-body-sm shrink-0" type="button">🔐 Certificados/Chaves</button>
        <button onclick="setCritCategory('EMAIL_MSG')" data-cat="EMAIL_MSG" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-surface-container-low text-on-surface-variant hover:text-primary font-body-sm text-body-sm shrink-0" type="button">📧 E-mails/Mensagens</button>
        <button onclick="setCritCategory('DB_ERP')" data-cat="DB_ERP" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-surface-container-low text-on-surface-variant hover:text-primary font-body-sm text-body-sm shrink-0" type="button">🗄️ Bancos SQL/ERP</button>
        <button onclick="setCritCategory('ARCHIVES')" data-cat="ARCHIVES" class="crit-pill h-7 px-space-sm flex items-center gap-space-xs rounded bg-surface-container-low text-on-surface-variant hover:text-primary font-body-sm text-body-sm shrink-0" type="button">📦 Backups/VMs/Compactados</button>
      </div>

      <!-- Lista de Cards Forenses de Agulhas no Palheiro -->
      <div id="crit-items-list" class="flex flex-col gap-space-xs"></div>
    </div>

    <!-- ========================================================================
         TELA 3: USUÁRIOS & ATALHOS RÁPIDOS
         ======================================================================== -->
    <div id="panel-usuarios-atalhos" class="tab-panel gap-space-md">
      <div class="bg-surface-container flex flex-col md:flex-row items-start md:items-center justify-between gap-space-md px-space-md py-2.5 rounded shadow-sm">
        <div class="flex items-center gap-space-md">
          <div class="w-8 h-8 rounded bg-surface-container-high flex items-center justify-center shrink-0 text-primary">
            <span class="material-symbols-outlined text-[18px]">security</span>
          </div>
          <div class="flex flex-col">
            <div class="flex items-center gap-space-sm">
              <h2 class="font-headline-sm text-headline-sm text-primary font-bold">Perfis de Usuários Detectados e Atalhos Diretos (Explorer Bridge)</h2>
              <span class="font-label-caps text-label-caps uppercase text-secondary bg-surface-container-lowest px-space-xs py-0.5 rounded font-bold">Instant Dispatch</span>
            </div>
            <p class="font-body-sm text-body-sm text-on-surface-variant">
              Abertura direta no Windows Explorer via <span class="font-data-mono-sm text-data-mono-sm text-primary font-semibold">explorer_bridge</span> nativo. Clique em qualquer atalho para inspecionar a pasta imediatamente.
            </p>
          </div>
        </div>
      </div>

      <!-- Grid de Perfis de Usuários -->
      <div id="users-cards-grid" class="grid grid-cols-1 lg:grid-cols-12 gap-space-md"></div>

      <!-- Card Especial: Diretórios Globais do Sistema -->
      <div class="flex flex-col bg-surface-container-low rounded p-space-md shadow-sm">
        <div class="flex items-center justify-between gap-space-sm pb-space-sm bg-surface-container px-space-sm py-space-sm rounded mb-space-sm">
          <div class="flex items-center gap-space-sm">
            <div class="w-8 h-8 rounded bg-surface-container-highest flex items-center justify-center text-primary">
              <span class="material-symbols-outlined text-[18px]">dns</span>
            </div>
            <div>
              <h3 class="font-headline-sm text-headline-sm text-primary font-bold">Diretórios Globais da Unidade</h3>
              <p class="font-body-sm text-body-sm text-on-surface-variant">Acesso rápido à raiz da unidade analisada, ProgramData e diretórios centrais.</p>
            </div>
          </div>
        </div>
        <div id="global-dirs-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-space-sm"></div>
      </div>
    </div>

    <!-- ========================================================================
         TELA 4: LINHA DO TEMPO ANUAL (TIMELINE)
         ======================================================================== -->
    <div id="panel-linha-do-tempo" class="tab-panel gap-space-md">
      <div class="flex flex-col lg:flex-row items-stretch gap-space-md">
        <div class="flex-1 bg-surface-container-low p-space-md rounded flex flex-col justify-between shadow-md">
          <div class="flex flex-col gap-space-xs">
            <div class="flex items-center gap-space-xs">
              <span class="material-symbols-outlined text-primary text-[18px]">calendar_clock</span>
              <span class="font-label-caps text-label-caps text-primary uppercase font-bold tracking-widest">CRONOGEOGRAFIA DIGITAL</span>
            </div>
            <h2 class="font-headline-lg text-headline-lg text-on-surface tracking-tight">Linha do Tempo de Atividade da Mídia (Análise Anual de Modificação de Arquivos)</h2>
            <p id="timeline-summary-text" class="font-body-md text-body-md text-on-surface-variant mt-0.5">
              Execute a varredura para reconstituir a distribuição cronológica de arquivos por ano.
            </p>
          </div>
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-space-sm mt-space-md pt-space-md bg-surface-container-lowest/50 p-space-sm rounded">
            <div class="flex flex-col">
              <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">JANELA TEMPORAL</span>
              <span id="tl-span" class="font-data-mono-lg text-data-mono-lg text-on-surface font-semibold">N/A</span>
            </div>
            <div class="flex flex-col">
              <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">ARQUIVOS VARRIDOS</span>
              <span id="tl-files" class="font-data-mono-lg text-data-mono-lg text-secondary font-semibold">0</span>
            </div>
            <div class="flex flex-col">
              <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">VOLUME QUENTE</span>
              <span id="tl-vol" class="font-data-mono-lg text-data-mono-lg text-primary font-semibold">0 B</span>
            </div>
            <div class="flex flex-col">
              <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">ALVOS CRÍTICOS</span>
              <span id="tl-crit" class="font-data-mono-lg text-data-mono-lg text-error font-semibold">0</span>
            </div>
          </div>
        </div>

        <div class="w-full lg:w-96 bg-surface-container p-space-md rounded flex flex-col justify-between shadow-md">
          <div class="flex items-center justify-between pb-space-xs">
            <div class="flex items-center gap-space-xs">
              <span class="material-symbols-outlined text-primary-fixed-dim text-[16px]">psychology</span>
              <span class="font-label-caps text-label-caps text-primary-fixed uppercase font-bold tracking-wider">INSIGHT FORENSE // METADADOS</span>
            </div>
            <span class="bg-surface-container-highest text-primary-fixed text-label-badge font-label-badge px-space-xs py-0.5 rounded">MFT STAT</span>
          </div>
          <div class="my-space-xs">
            <div class="font-label-caps text-label-caps text-on-surface-variant uppercase">ANO DE PICO IDENTIFICADO</div>
            <div class="flex items-baseline gap-space-xs mt-0.5">
              <span id="tl-peak-year" class="font-headline-xl text-headline-xl text-primary font-bold tracking-tight">—</span>
              <span class="font-body-sm text-body-sm text-on-surface-variant">(Maior concentração de arquivos)</span>
            </div>
          </div>
          <div class="flex items-center justify-between mt-space-sm pt-space-xs font-data-mono-sm text-data-mono-sm text-on-surface-variant">
            <span>Última atividade detectada:</span>
            <span id="tl-last-activity" class="text-secondary font-semibold">N/A</span>
          </div>
        </div>
      </div>

      <!-- Barras Horizontais por Ano -->
      <div class="bg-surface-container-low rounded p-space-md shadow-md flex flex-col gap-space-md">
        <div class="flex flex-wrap items-center justify-between gap-space-md pb-space-xs">
          <div class="flex items-center gap-space-xs">
            <span class="material-symbols-outlined text-secondary text-[18px]">bar_chart</span>
            <span class="font-headline-sm text-headline-sm text-on-surface font-semibold">Distribuição de Carga Temporal por Ano (YearActivityStats)</span>
          </div>
          <div class="flex items-center gap-space-md font-label-badge text-label-badge flex-wrap">
            <div class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-sm bg-secondary"></span><span class="text-on-surface-variant">Fotos (&gt;50KB)</span></div>
            <div class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-sm bg-tertiary-container"></span><span class="text-on-surface-variant">Vídeos (&gt;500KB)</span></div>
            <div class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-sm bg-primary-fixed-dim"></span><span class="text-on-surface-variant">Documentos</span></div>
            <div class="flex items-center gap-1.5"><span class="h-2.5 w-2.5 rounded-sm bg-error"></span><span class="text-on-surface-variant">Críticos</span></div>
          </div>
        </div>
        <div id="timeline-bars-container" class="flex flex-col gap-space-sm"></div>
      </div>

      <!-- Matriz Analítica Consolidada em Tabela -->
      <div class="bg-surface-container-low rounded p-space-md shadow-md flex flex-col gap-space-md">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-space-xs">
            <span class="material-symbols-outlined text-primary text-[18px]">table_chart</span>
            <span class="font-headline-sm text-headline-sm text-on-surface font-semibold">Matriz Analítica Consolidada de Modificações Cronológicas</span>
          </div>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left font-data-mono-sm text-data-mono-sm">
            <thead>
              <tr class="bg-surface-container text-on-surface-variant uppercase font-label-caps text-label-caps h-8">
                <th class="px-space-md py-1">Ano Base</th>
                <th class="px-space-md py-1">Total Relevantes</th>
                <th class="px-space-md py-1">Volume Somado</th>
                <th class="px-space-md py-1 text-secondary">Fotos (&gt;50KB)</th>
                <th class="px-space-md py-1 text-tertiary-fixed-dim">Vídeos (&gt;500KB)</th>
                <th class="px-space-md py-1 text-primary-fixed">Documentos</th>
                <th class="px-space-md py-1 text-error">Achados Críticos</th>
                <th class="px-space-md py-1">% Volume</th>
              </tr>
            </thead>
            <tbody id="timeline-table-body" class="divide-y divide-surface-container"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ========================================================================
         TELA 5: LOG DE ERROS / BAD BLOCKS
         ======================================================================== -->
    <div id="panel-log-erros" class="tab-panel gap-space-md">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-space-md">
        <div class="flex flex-col justify-between p-space-md bg-surface-container rounded shadow-sm">
          <div class="flex items-center justify-between mb-space-sm">
            <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">I/O READ / BAD BLOCKS</span>
            <span class="material-symbols-outlined text-error text-[16px]">disc_full</span>
          </div>
          <span id="err-kpi-io" class="font-headline-xl text-headline-xl text-error font-bold font-data-mono-lg">0</span>
          <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-space-xs">Falhas físicas / CRC / I/O</span>
        </div>
        <div class="flex flex-col justify-between p-space-md bg-surface-container rounded shadow-sm">
          <div class="flex items-center justify-between mb-space-sm">
            <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">ACL / PERMISSÕES NTFS</span>
            <span class="material-symbols-outlined text-primary text-[16px]">lock_clock</span>
          </div>
          <span id="err-kpi-acl" class="font-headline-xl text-headline-xl text-primary font-bold font-data-mono-lg">0</span>
          <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-space-xs">Caminhos protegidos pelo SO</span>
        </div>
        <div class="flex flex-col justify-between p-space-md bg-surface-container rounded shadow-sm">
          <div class="flex items-center justify-between mb-space-sm">
            <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">TOTAL DE INCIDENTES</span>
            <span class="material-symbols-outlined text-primary-fixed-dim text-[16px]">report</span>
          </div>
          <span id="err-kpi-total" class="font-headline-xl text-headline-xl text-primary-fixed-dim font-bold font-data-mono-lg">0</span>
          <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-space-xs">Exceções isoladas sem travar</span>
        </div>
        <div class="flex flex-col justify-between p-space-md bg-surface-container rounded shadow-sm">
          <div class="flex items-center justify-between mb-space-sm">
            <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">S.M.A.R.T. ID 05 / C5</span>
            <span class="material-symbols-outlined text-secondary text-[16px]">vital_signs</span>
          </div>
          <span id="err-kpi-smart" class="font-headline-xl text-headline-xl text-secondary font-bold font-data-mono-lg">0 / 0</span>
          <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-space-xs">Realocados | Pendentes</span>
        </div>
      </div>

      <!-- Barra de Filtros de Erros -->
      <div class="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-space-md bg-surface-container-low p-space-md rounded shadow-sm">
        <div class="flex items-center gap-space-sm flex-1 flex-wrap">
          <div class="flex items-center gap-space-xs bg-surface-container-lowest px-space-sm py-1 rounded w-full md:w-80">
            <span class="material-symbols-outlined text-outline text-[16px]">search</span>
            <input id="err-search-input" oninput="renderErrorsTable()" class="bg-transparent text-on-surface font-body-sm text-body-sm outline-none w-full" placeholder="Filtrar por caminho ou tipo de erro..." type="text"/>
          </div>
          <label class="flex items-center gap-space-xs cursor-pointer px-space-sm py-1 bg-surface-container rounded hover:bg-surface-container-high transition-colors">
            <input id="err-hide-acl" onchange="renderErrorsTable()" class="accent-primary w-3.5 h-3.5 rounded cursor-pointer" type="checkbox"/>
            <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant">Ocultar PermissionError (ACLs de Sistema)</span>
          </label>
        </div>
        <div class="flex items-center gap-space-sm shrink-0">
          <button onclick="exportErrorDumpTxt()" class="flex items-center gap-space-xs px-space-md py-1 rounded bg-primary-container hover:bg-primary-fixed text-on-primary font-headline-sm text-headline-sm font-bold shadow-sm transition-colors" type="button">
            <span class="material-symbols-outlined text-[16px]">file_download</span>
            <span>Exportar Dump .TXT</span>
          </button>
        </div>
      </div>

      <!-- Tabela Forense de Erros -->
      <div class="w-full overflow-x-auto rounded bg-surface-container-low shadow-sm">
        <table class="w-full text-left font-data-mono-md text-data-mono-md border-collapse">
          <thead>
            <tr class="bg-surface-container h-8 text-on-surface-variant font-label-caps text-label-caps uppercase">
              <th class="px-space-md py-1 w-32">TIMESTAMP</th>
              <th class="px-space-md py-1 w-56">TIPO DE ERRO</th>
              <th class="px-space-md py-1 w-32">OFFSET LBA</th>
              <th class="px-space-md py-1">CAMINHO AFETADO</th>
              <th class="px-space-md py-1">DIAGNÓSTICO TÉCNICO</th>
              <th class="px-space-md py-1 text-right w-40">AÇÕES</th>
            </tr>
          </thead>
          <tbody id="err-table-body" class="divide-y divide-surface-container-highest/20 font-data-mono-sm text-data-mono-sm"></tbody>
        </table>
      </div>
    </div>

    <!-- ========================================================================
         TELA 6: MONITOR DE VARREDURA EM ANDAMENTO (LIVE SCAN MONITOR)
         ======================================================================== -->
    <div id="panel-live-monitor" class="tab-panel gap-space-md">
      <section class="bg-surface-container-low rounded-lg p-space-md shadow-md flex flex-wrap items-center justify-between gap-space-md">
        <div class="flex items-center gap-space-md min-w-0">
          <div class="relative flex items-center justify-center w-9 h-9 rounded-lg bg-surface-container-high shrink-0">
            <span id="live-spin-icon" class="material-symbols-outlined text-primary-fixed-dim text-[20px]">cyclone</span>
          </div>
          <div class="flex flex-col min-w-0">
            <div class="flex items-center gap-space-sm flex-wrap">
              <span id="live-banner-title" class="font-headline-sm text-headline-sm text-primary font-bold tracking-tight">MONITOR DE VARREDURA FORENSE EM TEMPO REAL</span>
              <span class="font-data-mono-sm text-data-mono-sm text-secondary bg-secondary-container/20 px-space-xs py-0.5 rounded flex items-center gap-1 font-semibold">
                <span class="material-symbols-outlined text-[13px]">verified_user</span>
                100% READ-ONLY BUFFER RAM
              </span>
            </div>
            <span id="live-banner-sub" class="font-data-mono-sm text-data-mono-sm text-on-surface-variant truncate">Pronto para varredura...</span>
          </div>
        </div>
        <div class="flex items-center gap-space-sm">
          <button onclick="startScan()" class="flex items-center gap-space-xs px-space-md py-1 rounded bg-secondary-container hover:bg-secondary text-on-secondary-container font-headline-sm text-headline-sm font-bold" type="button">
            <span class="material-symbols-outlined text-[16px]">play_arrow</span>
            <span>Iniciar</span>
          </button>
          <button onclick="stopScan()" class="flex items-center gap-space-xs px-space-md py-1 rounded bg-error-container hover:bg-error text-on-error-container font-headline-sm text-headline-sm font-bold shadow-sm" type="button">
            <span class="material-symbols-outlined text-[16px]">stop_circle</span>
            <span>Interromper &amp; Preservar</span>
          </button>
        </div>
      </section>

      <!-- Cards de Telemetria ao Vivo -->
      <section class="grid grid-cols-2 lg:grid-cols-5 gap-space-md w-full">
        <div class="bg-surface-container-low rounded-lg p-space-md flex flex-col justify-between shadow-md">
          <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">Tempo Decorrido</span>
          <span id="live-elapsed" class="font-headline-xl text-headline-xl text-primary font-bold font-data-mono-lg my-1">00:00:00</span>
          <span id="live-rate" class="font-data-mono-sm text-data-mono-sm text-secondary">0 arqs/seg</span>
        </div>
        <div class="bg-surface-container-low rounded-lg p-space-md flex flex-col justify-between shadow-md">
          <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">Arquivos Auditados</span>
          <span id="live-files" class="font-headline-xl text-headline-xl text-on-surface font-bold font-data-mono-lg my-1">0</span>
          <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant">Metadados stat()</span>
        </div>
        <div class="bg-surface-container-low rounded-lg p-space-md flex flex-col justify-between shadow-md">
          <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">Pastas Varridas</span>
          <span id="live-dirs" class="font-headline-xl text-headline-xl text-on-surface font-bold font-data-mono-lg my-1">0</span>
          <span class="font-data-mono-sm text-data-mono-sm text-primary-fixed-dim">Blocklist anti-lixo ativa</span>
        </div>
        <div class="bg-surface-container-low rounded-lg p-space-md flex flex-col justify-between shadow-md">
          <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">Pastas Quentes</span>
          <span id="live-hot" class="font-headline-xl text-headline-xl text-primary-fixed font-bold font-data-mono-lg my-1">0</span>
          <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant">Fotos, Vídeos e Docs</span>
        </div>
        <div class="bg-surface-container-low rounded-lg p-space-md flex flex-col justify-between shadow-md">
          <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">Agulhas Críticas</span>
          <span id="live-crit" class="font-headline-xl text-headline-xl text-error font-bold font-data-mono-lg my-1">0</span>
          <span id="live-err-sub" class="font-data-mono-sm text-data-mono-sm text-on-surface-variant">0 incidentes I/O</span>
        </div>
      </section>

      <!-- Duas Colunas: Console de Stream em Tempo Real (60%) + Descobertas Ao Vivo (40%) -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-space-lg w-full items-start">
        <section class="lg:col-span-7 flex flex-col bg-surface-container-low rounded-lg shadow-md overflow-hidden">
          <div class="px-space-md py-space-sm bg-surface-container flex items-center justify-between">
            <div class="flex items-center gap-space-sm">
              <span class="material-symbols-outlined text-[16px] text-primary-fixed-dim">terminal</span>
              <span class="font-headline-sm text-headline-sm text-on-surface font-bold">Console de I/O em Tempo Real</span>
            </div>
            <span class="font-label-caps text-label-caps text-secondary uppercase font-bold">STREAM ATIVO</span>
          </div>
          <div id="live-terminal-stream" class="p-space-md bg-surface-container-lowest font-data-mono-sm text-data-mono-sm h-[420px] overflow-y-auto flex flex-col gap-1 leading-tight select-text"></div>
        </section>

        <section class="lg:col-span-5 flex flex-col gap-space-sm bg-surface-container-low rounded-lg p-space-md shadow-md">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-space-xs">
              <span class="material-symbols-outlined text-error text-[18px]">emergency</span>
              <span class="font-headline-sm text-headline-sm text-on-surface font-bold">Últimas Agulhas Críticas Detectadas</span>
            </div>
            <button onclick="switchTab('arquivos-criticos')" class="text-primary hover:underline font-data-mono-sm text-data-mono-sm" type="button">Ver Todas →</button>
          </div>
          <div id="live-findings-feed" class="flex flex-col gap-space-xs max-h-[400px] overflow-y-auto"></div>
        </section>
      </div>
    </div>

    <!-- ========================================================================
         TELA 7: RESUMO PÓS-VARREDURA FORENSE (TRIAGEM EXECUTIVA)
         ======================================================================== -->
    <div id="panel-resumo-pos-varredura" class="tab-panel gap-space-md">
      <!-- Banner de Conclusão -->
      <section class="w-full bg-surface-container-low rounded-lg p-space-lg shadow-xl relative overflow-hidden border border-secondary/30">
        <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-space-lg">
          <div class="flex flex-col gap-space-xs">
            <div class="flex items-center gap-space-sm flex-wrap">
              <span class="flex items-center justify-center w-6 h-6 rounded bg-secondary-container text-on-secondary-container">
                <span class="material-symbols-outlined text-[16px]">verified</span>
              </span>
              <span id="exec-banner-title" class="font-headline-lg text-headline-lg text-primary tracking-tight font-bold">
                SUMÁRIO EXECUTIVO DE TRIAGEM FORENSE READ-ONLY
              </span>
            </div>
            <div class="flex items-center gap-space-xs flex-wrap font-label-caps text-label-caps text-on-surface-variant pt-space-xs">
              <div class="flex items-center gap-1 bg-surface-container-lowest px-space-sm py-1 rounded">
                <span class="material-symbols-outlined text-secondary text-[13px]">lock</span>
                <span class="text-secondary font-bold">100% READ-ONLY PRESERVADO</span>
              </div>
              <div class="flex items-center gap-1 bg-surface-container-lowest px-space-sm py-1 rounded">
                <span class="material-symbols-outlined text-secondary text-[13px]">block</span>
                <span class="text-on-surface">ZERO BYTES GRAVADOS NO DISCO ALVO</span>
              </div>
            </div>
          </div>
          <div class="flex items-center gap-space-xs flex-wrap shrink-0">
            <button onclick="openExportModal()" class="h-8 px-space-md bg-secondary-container hover:bg-secondary text-on-secondary-container hover:text-on-secondary rounded transition-colors font-headline-sm text-headline-sm font-bold flex items-center gap-space-xs shadow-md" type="button">
              <span class="material-symbols-outlined text-[16px]">html</span>
              <span>Exportar Catálogo HTML Completo</span>
            </button>
          </div>
        </div>
      </section>

      <!-- Cadeia de Custódia & Identificação -->
      <section class="w-full bg-surface-container-low rounded-lg p-space-md flex flex-col gap-space-sm shadow-md">
        <div class="flex items-center justify-between pb-space-xs">
          <div class="flex items-center gap-space-xs">
            <span class="material-symbols-outlined text-primary text-[16px]">fingerprint</span>
            <span class="font-headline-sm text-headline-sm text-on-surface uppercase tracking-wider font-bold">
              Identificação Criptográfica da Triagem &amp; Cadeia de Custódia
            </span>
          </div>
          <span class="font-label-caps text-label-caps text-secondary bg-surface-container-highest px-space-sm py-0.5 rounded font-bold">STRICT READ-ONLY</span>
        </div>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-space-md bg-surface-container-lowest p-space-md rounded font-data-mono-sm text-data-mono-sm">
          <div class="flex items-center justify-between bg-surface-container-low p-space-sm rounded">
            <div class="flex flex-col min-w-0 pr-space-sm">
              <span class="text-on-surface-variant font-label-caps text-label-caps">HASH DE EVIDÊNCIA DA SESSÃO (SHA-256):</span>
              <span id="exec-sha256" class="text-secondary font-bold truncate select-all">N/A</span>
            </div>
            <button onclick="copyTextValue(document.getElementById('exec-sha256').innerText, 'Hash SHA-256 copiado!')" class="shrink-0 bg-surface-container-high hover:bg-surface-variant text-primary px-space-xs py-1 rounded text-label-caps font-label-caps uppercase" type="button">Copiar</button>
          </div>
          <div class="flex items-center justify-between bg-surface-container-low p-space-sm rounded">
            <div class="flex flex-col min-w-0 pr-space-sm">
              <span class="text-on-surface-variant font-label-caps text-label-caps">DISPOSITIVO FÍSICO INSPECIONADO:</span>
              <span id="exec-device-summary" class="text-primary font-bold truncate">N/A</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Top Achados Críticos e Top Pastas Quentes no Resumo Executivo -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-space-md">
        <div class="lg:col-span-7 bg-surface-container-low rounded-lg p-space-md flex flex-col gap-space-sm shadow-md">
          <div class="flex items-center justify-between">
            <span class="font-headline-sm text-headline-sm text-error uppercase font-bold flex items-center gap-1">
              <span class="material-symbols-outlined text-[16px]">emergency</span>
              Top Agulhas Críticas Encontradas
            </span>
            <button onclick="switchTab('arquivos-criticos')" class="text-primary hover:underline font-data-mono-sm text-data-mono-sm" type="button">Abrir Aba Completa →</button>
          </div>
          <div id="exec-top-crit" class="flex flex-col gap-space-xs"></div>
        </div>
        <div class="lg:col-span-5 bg-surface-container-low rounded-lg p-space-md flex flex-col gap-space-sm shadow-md">
          <div class="flex items-center justify-between">
            <span class="font-headline-sm text-headline-sm text-primary-fixed uppercase font-bold flex items-center gap-1">
              <span class="material-symbols-outlined text-[16px]">local_fire_department</span>
              Top Pastas Quentes (Volume/Relevância)
            </span>
            <button onclick="switchTab('pastas-quentes')" class="text-primary hover:underline font-data-mono-sm text-data-mono-sm" type="button">Abrir Aba Completa →</button>
          </div>
          <div id="exec-top-hot" class="flex flex-col gap-space-xs"></div>
        </div>
      </div>
    </div>

  </div>
</main>

<!-- ============================================================================
     MODAL DIAGNÓSTICO DO SISTEMA (COMPATIBILIDADE WINDOWS 10/11)
     ============================================================================ -->
<div id="modal-diagnostics" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-surface-container-lowest/85 backdrop-blur-md p-space-md">
  <div class="w-full max-w-4xl max-h-[90vh] bg-surface-container-low rounded-lg shadow-2xl flex flex-col overflow-hidden border border-outline-variant/60">
    <div class="h-11 px-space-md bg-surface-container-high flex items-center justify-between shrink-0">
      <div class="flex items-center gap-space-sm min-w-0">
        <span class="material-symbols-outlined text-primary text-[18px]">health_and_safety</span>
        <span class="font-headline-sm text-headline-sm font-bold text-primary truncate">
          AUTOTESTE DE COMPATIBILIDADE &amp; PRONTIDÃO DO SISTEMA OPERACIONAL
        </span>
      </div>
      <div class="flex items-center gap-space-xs">
        <button onclick="loadDiagnosticsData()" class="h-7 px-space-sm flex items-center gap-1 rounded bg-surface-container hover:bg-surface-bright text-primary font-data-mono-sm text-data-mono-sm" type="button">
          <span class="material-symbols-outlined text-[14px]">refresh</span>
          <span>Reexecutar</span>
        </button>
        <button onclick="closeDiagnosticsModal()" class="h-7 w-7 flex items-center justify-center rounded bg-error-container/40 hover:bg-error-container text-error hover:text-on-error" type="button">
          <span class="material-symbols-outlined text-[16px]">close</span>
        </button>
      </div>
    </div>
    <div class="p-space-md bg-surface-container-lowest flex items-center justify-between border-b border-outline-variant/20 shrink-0">
      <div class="flex items-center gap-space-sm">
        <span class="font-label-caps text-label-caps uppercase text-on-surface-variant font-bold">Status do Ambiente:</span>
        <span id="diag-overall-badge" class="font-label-caps text-label-caps px-space-sm py-0.5 rounded bg-secondary-container text-on-secondary-container font-bold">CONSULTANDO...</span>
      </div>
      <span id="diag-summary-text" class="font-data-mono-sm text-data-mono-sm text-on-surface-variant">Executando varredura de subsistemas...</span>
    </div>
    <div id="diag-checks-list" class="p-space-md overflow-y-auto space-y-space-sm flex-1">
      <div class="text-center py-8 text-on-surface-variant">Carregando telemetria de ambiente...</div>
    </div>
    <div class="p-space-md bg-surface-container-high flex items-center justify-between shrink-0">
      <span class="text-body-sm font-body-sm text-on-surface-variant">Geio DiskRadar v2.2.0 • Verificação passiva 100% segura</span>
      <button onclick="closeDiagnosticsModal()" class="h-8 px-space-md rounded bg-surface-container hover:bg-surface-variant text-on-surface font-body-sm font-semibold" type="button">Fechar</button>
    </div>
  </div>
</div>

<!-- ============================================================================
     MODAL DE CONFIRMAÇÃO DE EXTRAÇÃO DE EVIDÊNCIA FORENSE
     ============================================================================ -->
<div id="modal-evidence-success" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-surface-container-lowest/85 backdrop-blur-md p-space-md">
  <div class="w-full max-w-2xl bg-surface-container-low rounded-lg shadow-2xl flex flex-col overflow-hidden border border-secondary/40">
    <div class="h-11 px-space-md bg-secondary-container text-on-secondary-container flex items-center justify-between shrink-0">
      <div class="flex items-center gap-space-sm min-w-0 font-bold">
        <span class="material-symbols-outlined text-[18px]">verified</span>
        <span>EVIDÊNCIA EXTRAÍDA COM SUCESSO (CADEIA DE CUSTÓDIA)</span>
      </div>
      <button onclick="closeEvidenceModal()" class="h-7 w-7 flex items-center justify-center rounded hover:bg-black/20" type="button">
        <span class="material-symbols-outlined text-[16px]">close</span>
      </button>
    </div>
    <div class="p-space-md bg-surface-container-lowest space-y-space-md">
      <div class="flex items-center gap-space-sm text-secondary font-bold font-body-md">
        <span class="material-symbols-outlined">lock</span>
        <span>Integridade Matemática Validada (SHA-256 Idêntico)</span>
      </div>
      <div class="space-y-space-xs font-data-mono-sm text-data-mono-sm bg-surface-container-low p-space-sm rounded">
        <div><span class="text-on-surface-variant">Arquivo:</span> <strong id="evi-modal-name" class="text-on-surface"></strong></div>
        <div class="truncate"><span class="text-on-surface-variant">Destino:</span> <code id="evi-modal-path" class="text-primary truncate select-all"></code></div>
        <div class="truncate"><span class="text-on-surface-variant">Hash SHA-256:</span> <code id="evi-modal-sha" class="text-secondary truncate select-all"></code></div>
        <div class="truncate"><span class="text-on-surface-variant">Manifesto:</span> <code id="evi-modal-manifest" class="text-on-surface-variant truncate select-all"></code></div>
      </div>
    </div>
    <div class="p-space-md bg-surface-container-high flex items-center justify-between shrink-0">
      <button id="evi-btn-open-folder" onclick="" class="h-8 px-space-md rounded bg-secondary-container hover:bg-secondary text-on-secondary-container font-body-sm font-bold flex items-center gap-1" type="button">
        <span class="material-symbols-outlined text-[14px]">folder_open</span>
        <span>Abrir Pasta de Evidências</span>
      </button>
      <button onclick="closeEvidenceModal()" class="h-8 px-space-md rounded bg-surface-container hover:bg-surface-variant text-on-surface font-body-sm font-semibold" type="button">Fechar</button>
    </div>
  </div>
</div>

<!-- ============================================================================
     MODAL 8: DIAGNÓSTICO S.M.A.R.T. AVANÇADO (ATRIBUTOS ATA/NVMe)
     ============================================================================ -->
<div id="modal-smart" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-surface-container-lowest/85 backdrop-blur-md p-space-md">
  <div class="w-full max-w-6xl max-h-[92vh] bg-surface-container-low rounded-lg shadow-2xl flex flex-col overflow-hidden border border-outline-variant/60">
    <!-- Cabeçalho Modal SMART -->
    <div class="h-11 px-space-md bg-surface-container-high flex items-center justify-between shrink-0">
      <div class="flex items-center gap-space-sm min-w-0">
        <span class="material-symbols-outlined text-primary-fixed-dim text-[18px]">neurology</span>
        <span class="font-headline-sm text-headline-sm font-bold text-primary truncate">
          DIAGNÓSTICO AVANÇADO DE HARDWARE // TELEMETRIA S.M.A.R.T. &amp; ATRIBUTOS ATA/NVMe
        </span>
        <span class="hidden sm:inline-block font-label-caps text-label-caps px-space-xs py-0.5 rounded bg-surface-container-lowest text-secondary font-bold">
          100% READ-ONLY • PASSIVE POLLING
        </span>
      </div>
      <div class="flex items-center gap-space-xs">
        <button onclick="refreshDrives()" class="h-7 px-space-sm flex items-center gap-1 rounded bg-surface-container hover:bg-surface-bright text-primary font-data-mono-sm text-data-mono-sm" type="button">
          <span class="material-symbols-outlined text-[14px]">sync</span>
          <span>Reconsultar WMI/SMART</span>
        </button>
        <button onclick="closeSmartModal()" class="h-7 w-7 flex items-center justify-center rounded bg-error-container/40 hover:bg-error-container text-error hover:text-on-error" type="button">
          <span class="material-symbols-outlined text-[16px]">close</span>
        </button>
      </div>
    </div>

    <!-- Painel de Score Eletromecânico + 6 Micro-Cards -->
    <div class="p-space-md bg-surface-container-lowest grid grid-cols-1 xl:grid-cols-12 gap-space-md shrink-0">
      <div class="xl:col-span-4 bg-surface-container-low rounded p-space-md flex flex-col justify-between">
        <div class="flex items-start justify-between">
          <div>
            <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">Índice de Integridade Física</span>
            <div class="font-headline-sm text-headline-sm font-bold text-on-surface">Score Eletromecânico</div>
          </div>
          <span id="smart-modal-banner" class="font-label-caps text-label-caps px-space-xs py-0.5 rounded bg-secondary-container text-on-secondary-container font-bold">SAUDÁVEL</span>
        </div>
        <div class="flex items-baseline gap-space-md my-space-sm">
          <span id="smart-modal-score" class="font-headline-xl text-headline-xl text-primary text-[34px] leading-none font-bold">100%</span>
          <span id="smart-modal-risk" class="font-data-mono-sm text-data-mono-sm text-on-surface-variant">Baixo Risco Físico</span>
        </div>
        <div class="h-2 w-full bg-surface-container-highest rounded-full overflow-hidden">
          <div id="smart-modal-bar" class="h-full bg-secondary transition-all" style="width: 100%;"></div>
        </div>
      </div>

      <div class="xl:col-span-8 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-space-sm font-data-mono-sm text-data-mono-sm">
        <div class="bg-surface-container rounded p-space-sm flex flex-col justify-between">
          <span class="font-label-caps text-label-caps text-on-surface-variant">TEMP. ATUAL</span>
          <span id="sm-card-temp" class="font-headline-lg text-headline-lg font-bold text-secondary">34°C</span>
          <span class="text-on-surface-variant">Termistor</span>
        </div>
        <div class="bg-surface-container rounded p-space-sm flex flex-col justify-between">
          <span class="font-label-caps text-label-caps text-on-surface-variant">POWER-ON</span>
          <span id="sm-card-poh" class="font-headline-lg text-headline-lg font-bold text-on-surface">0h</span>
          <span id="sm-card-days" class="text-on-surface-variant">Horas Ligado</span>
        </div>
        <div class="bg-surface-container rounded p-space-sm flex flex-col justify-between">
          <span class="font-label-caps text-label-caps text-on-surface-variant">IGNIÇÕES</span>
          <span id="sm-card-cycles" class="font-headline-lg text-headline-lg font-bold text-on-surface">0</span>
          <span class="text-on-surface-variant">Power Cycles</span>
        </div>
        <div class="bg-surface-container rounded p-space-sm flex flex-col justify-between">
          <span class="font-label-caps text-label-caps text-error font-bold">REALOCADOS (05)</span>
          <span id="sm-card-realloc" class="font-headline-lg text-headline-lg font-bold text-error">0</span>
          <span class="text-on-surface-variant">Setores G-List</span>
        </div>
        <div class="bg-surface-container rounded p-space-sm flex flex-col justify-between">
          <span class="font-label-caps text-label-caps text-tertiary-fixed-dim font-bold">PENDENTES (C5)</span>
          <span id="sm-card-pending" class="font-headline-lg text-headline-lg font-bold text-tertiary-fixed-dim">0</span>
          <span class="text-on-surface-variant">Quarentena</span>
        </div>
        <div class="bg-surface-container rounded p-space-sm flex flex-col justify-between">
          <span class="font-label-caps text-label-caps text-error font-bold">OFFLINE UNC (C6)</span>
          <span id="sm-card-unc" class="font-headline-lg text-headline-lg font-bold text-error">0</span>
          <span class="text-on-surface-variant">Incorrigíveis</span>
        </div>
      </div>
    </div>

    <!-- Barra de Filtro da Tabela SMART -->
    <div class="px-space-md py-space-sm bg-surface-container-high flex flex-wrap items-center justify-between gap-space-sm shrink-0">
      <div class="flex items-center gap-space-xs">
        <button onclick="setSmartFilter('all')" class=" h-7 px-space-sm rounded font-label-caps text-label-caps font-bold uppercase bg-primary text-on-primary" type="button">Todos</button>
        <button onclick="setSmartFilter('criticos')" class="h-7 px-space-sm rounded font-label-caps text-label-caps font-bold uppercase bg-surface-container text-on-surface-variant hover:text-on-surface" type="button">Críticos</button>
        <button onclick="setSmartFilter('desgaste')" class="h-7 px-space-sm rounded font-label-caps text-label-caps font-bold uppercase bg-surface-container text-on-surface-variant hover:text-on-surface" type="button">Desgaste &amp; Ciclos</button>
        <button onclick="setSmartFilter('erros')" class="h-7 px-space-sm rounded font-label-caps text-label-caps font-bold uppercase bg-surface-container text-on-surface-variant hover:text-on-surface" type="button">Erros &amp; Latência</button>
      </div>
      <div class="flex items-center gap-space-sm">
        <button onclick="toggleSmartHexDec()" class="h-7 px-space-sm rounded bg-surface-container hover:bg-surface-variant text-on-surface font-data-mono-sm text-data-mono-sm" type="button">
          Exibir: <strong id="smart-raw-mode-label" class="text-primary">RAW HEX</strong>
        </button>
      </div>
    </div>

    <!-- Tabela de Atributos SMART -->
    <div class="w-full overflow-x-auto bg-surface-container-lowest flex-1 overflow-y-auto">
      <table class="w-full text-left font-data-mono-sm text-data-mono-sm border-collapse">
        <thead class="sticky top-0 bg-surface-container z-10 font-label-caps text-label-caps text-on-surface-variant uppercase">
          <tr>
            <th class="py-2 px-space-md">ID</th>
            <th class="py-2 px-space-md">Atributo S.M.A.R.T.</th>
            <th class="py-2 px-space-md text-center">Status</th>
            <th class="py-2 px-space-md text-right">Atual</th>
            <th class="py-2 px-space-md text-right">Pior</th>
            <th class="py-2 px-space-md text-right">Limiar</th>
            <th class="py-2 px-space-md text-right text-primary">Valor Bruto</th>
            <th class="py-2 px-space-md">Interpretação Pericial</th>
          </tr>
        </thead>
        <tbody id="smart-modal-tbody" class="divide-y divide-surface-container"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- ============================================================================
     MODAL 9: PRÉ-VISUALIZAÇÃO & EXPORTAÇÃO DO RELATÓRIO HTML FORENSE
     ============================================================================ -->
<div id="modal-export" class="hidden fixed inset-0 z-50 flex items-center justify-center p-space-md bg-surface-container-lowest/85 backdrop-blur-md">
  <div class="bg-surface-container-low border border-outline-variant/60 rounded-lg shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden">
    <div class="px-space-lg py-space-md bg-surface-container border-b border-outline-variant/40 flex items-center justify-between gap-space-md shrink-0">
      <div class="space-y-0.5 min-w-0">
        <div class="flex items-center gap-space-xs">
          <span class="material-symbols-outlined text-primary text-[20px]">description</span>
          <h2 class="font-headline-lg text-headline-lg text-primary font-bold tracking-tight">Pré-visualização &amp; Exportação do Catálogo de Autópsia HTML</h2>
          <span class="bg-secondary-container text-on-secondary-container px-space-xs py-0.5 rounded font-label-badge text-label-badge font-bold">100% AUTOCONTIDO OFFLINE</span>
        </div>
        <div class="flex items-center gap-space-xs font-data-mono-sm text-data-mono-sm text-on-surface-variant truncate">
          <span>Destino:</span>
          <code id="export-modal-path" class="text-primary-fixed bg-surface-container-lowest px-1.5 py-0.5 rounded select-all truncate">Relatorio.html</code>
        </div>
      </div>
      <button onclick="closeExportModal()" class="w-8 h-8 flex items-center justify-center rounded hover:bg-surface-variant text-on-surface-variant hover:text-on-surface" type="button">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    </div>

    <div class="p-space-lg bg-surface-container-lowest flex-1 overflow-y-auto space-y-space-md">
      <div class="bg-surface-container-low border border-primary/30 p-space-md rounded flex items-center justify-between gap-space-md">
        <div>
          <div class="font-headline-sm text-headline-sm text-primary font-bold">GEIO DISKRADAR FORENSIC AUDIT REPORT (v2.2.0)</div>
          <div id="export-preview-meta" class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-0.5">Unidade analisada em modo 100% Read-Only</div>
        </div>
        <div class="text-right font-data-mono-sm text-data-mono-sm text-secondary font-bold">OFFLINE SEARCHABLE</div>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-4 gap-space-sm font-data-mono-sm text-data-mono-sm">
        <div class="bg-surface-container p-space-sm rounded">
          <span class="text-on-surface-variant block text-label-caps font-label-caps">MODELO / SÉRIE</span>
          <span id="exp-prev-model" class="text-primary font-semibold truncate block">N/A</span>
        </div>
        <div class="bg-surface-container p-space-sm rounded">
          <span class="text-on-surface-variant block text-label-caps font-label-caps">PASTAS QUENTES</span>
          <span id="exp-prev-hot" class="text-secondary font-semibold">0 pastas</span>
        </div>
        <div class="bg-surface-container p-space-sm rounded">
          <span class="text-on-surface-variant block text-label-caps font-label-caps">AGULHAS CRÍTICAS</span>
          <span id="exp-prev-crit" class="text-error font-bold">0 achados</span>
        </div>
        <div class="bg-surface-container p-space-sm rounded">
          <span class="text-on-surface-variant block text-label-caps font-label-caps">USUÁRIOS</span>
          <span id="exp-prev-users" class="text-on-surface font-semibold truncate block">N/A</span>
        </div>
      </div>

      <div class="p-space-sm bg-surface-container rounded text-on-surface-variant font-body-sm text-body-sm">
        O arquivo <strong>.HTML</strong> gerado inclui o Crachá Forense do Disco, Tabela de Pastas Quentes, Tabela Filtrável de Agulhas no Palheiro, Histograma Anual de Linha do Tempo e o <strong>Catálogo Pesquisável Instantâneo em JavaScript</strong> para consultar o conteúdo do HD mesmo após o descarte físico da mídia.
      </div>
    </div>

    <div class="px-space-lg py-space-md bg-surface-container border-t border-outline-variant/40 flex flex-wrap items-center justify-between gap-space-md shrink-0">
      <label class="flex items-center gap-space-xs cursor-pointer text-on-surface">
        <input id="export-open-after" checked class="accent-secondary w-4 h-4 rounded" type="checkbox"/>
        <span class="text-body-sm font-body-sm">Abrir relatório no navegador padrão após salvar</span>
      </label>
      <div class="flex items-center gap-space-sm">
        <button onclick="closeExportModal()" class="px-space-md py-1.5 rounded bg-surface-container-high hover:bg-surface-variant text-on-surface font-headline-sm text-headline-sm" type="button">Cancelar</button>
        <button onclick="pickReportOutput()" class="px-space-md py-1.5 rounded bg-surface-container-high hover:bg-surface-variant text-primary-fixed font-headline-sm text-headline-sm flex items-center gap-space-xs" type="button">
          <span class="material-symbols-outlined text-[15px]">folder_open</span>
          <span>Alterar Destino...</span>
        </button>
        <button onclick="confirmExportReport()" class="px-space-lg py-1.5 rounded bg-secondary-container hover:bg-secondary text-on-secondary-container hover:text-on-secondary font-headline-sm text-headline-sm font-bold shadow-[0_0_8px_rgba(78,222,163,0.25)] flex items-center gap-space-xs" type="button">
          <span class="material-symbols-outlined text-[16px]">file_download</span>
          <span>Gerar &amp; Salvar Relatório HTML</span>
        </button>
      </div>
    </div>
  </div>
</div>

<!-- ============================================================================
     MODAL 10: HEX VIEWER DE SETOR / ARQUIVO CRU (100% READ-ONLY)
     ============================================================================ -->
<div id="modal-hex" class="hidden fixed inset-0 z-50 flex items-center justify-center bg-surface-container-lowest/85 backdrop-blur-md p-space-md">
  <div class="w-full max-w-7xl max-h-[92vh] flex flex-col bg-surface shadow-2xl rounded-lg overflow-hidden border border-outline-variant/60">
    <!-- Header Hex Viewer -->
    <div class="bg-surface-container-low px-space-xl py-space-md flex flex-wrap items-center justify-between gap-space-md shrink-0">
      <div class="flex flex-col gap-0.5 min-w-0">
        <div class="flex items-center gap-space-sm">
          <span class="material-symbols-outlined text-primary-fixed-dim text-[18px]">biotech</span>
          <span class="font-headline-sm text-headline-sm text-primary font-bold">
            Inspeção Forense de Bloco / Setor LBA (Raw Hex &amp; ASCII Read-Only)
          </span>
          <span class="bg-surface-container-high text-primary-fixed font-label-caps text-label-caps px-space-sm py-0.5 rounded">512B PAGE</span>
        </div>
        <div class="flex flex-wrap items-center gap-space-md text-on-surface-variant font-data-mono-sm text-data-mono-sm mt-0.5">
          <span id="hex-path-label" class="text-primary font-semibold truncate max-w-2xl">Selecione um arquivo</span>
          <span>•</span>
          <span>Tamanho: <strong id="hex-size-label" class="text-on-surface">0 B</strong></span>
          <span>•</span>
          <span>Offset: <strong id="hex-offset-label" class="text-secondary">0x00000000</strong></span>
        </div>
      </div>
      <div class="flex items-center gap-space-sm">
        <div class="flex items-center gap-space-xs px-space-sm py-1 rounded bg-secondary-container/20">
          <span class="h-2 w-2 rounded-full bg-secondary animate-pulse"></span>
          <span class="font-label-caps text-label-caps text-secondary font-bold uppercase">100% READ-ONLY (`rb`)</span>
        </div>
        <button onclick="closeHexModal()" class="w-8 h-8 flex items-center justify-center rounded bg-surface-container hover:bg-error-container text-on-surface-variant hover:text-on-error-container" type="button">
          <span class="material-symbols-outlined text-[18px]">close</span>
        </button>
      </div>
    </div>

    <!-- Barra de Navegação de Offset / Setor -->
    <div class="bg-surface-container px-space-xl py-space-sm flex flex-wrap items-center justify-between gap-space-md shrink-0">
      <div class="flex items-center gap-space-sm flex-wrap">
        <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">Offset Bytes:</span>
        <input id="hex-offset-input" onchange="reloadHexCurrent()" onkeydown="if(event.key==='Enter')reloadHexCurrent()" class="bg-surface-container-lowest font-data-mono-md text-data-mono-md text-on-surface px-space-sm py-1 rounded w-28 outline-none border border-outline-variant/30 focus:border-primary" type="number" min="0" step="512" value="0"/>
        <button onclick="stepHexOffset(-512)" class="px-space-md py-1 bg-surface-container-high hover:bg-surface-variant text-on-surface rounded font-data-mono-sm text-data-mono-sm flex items-center gap-1" type="button">
          <span class="material-symbols-outlined text-[14px]">arrow_back</span>
          <span>Anterior (-512B)</span>
        </button>
        <button onclick="stepHexOffset(512)" class="px-space-md py-1 bg-surface-container-high hover:bg-surface-variant text-on-surface rounded font-data-mono-sm text-data-mono-sm flex items-center gap-1" type="button">
          <span>Próximo (+512B)</span>
          <span class="material-symbols-outlined text-[14px]">arrow_forward</span>
        </button>
        <button onclick="reloadHexCurrent()" class="px-space-md py-1 bg-surface-container-high hover:bg-surface-variant text-primary rounded font-data-mono-sm text-data-mono-sm" type="button">Ir / Recarregar</button>
      </div>
      <div class="flex items-center gap-space-sm">
        <button onclick="copyHexDump()" class="px-space-md py-1 bg-surface-container-high hover:bg-surface-variant text-on-surface rounded font-data-mono-sm text-data-mono-sm flex items-center gap-1" type="button">
          <span class="material-symbols-outlined text-[14px]">content_copy</span>
          <span>Copiar Dump Hex</span>
        </button>
      </div>
    </div>

    <!-- Corpo Principal: Matriz Hex (Esquerda) + Intérprete de Dados (Direita) -->
    <div class="grid grid-cols-12 min-h-0 flex-1 overflow-hidden">
      <div class="col-span-12 lg:col-span-9 flex flex-col bg-surface-container-lowest min-h-0">
        <div class="grid grid-cols-12 bg-surface-container px-space-xl py-1 font-label-caps text-label-caps text-outline uppercase select-none shrink-0">
          <div class="col-span-2 text-on-surface-variant">OFFSET (HEX)</div>
          <div class="col-span-7 font-data-mono-sm text-data-mono-sm text-primary-fixed-dim">00 01 02 03 04 05 06 07 | 08 09 0A 0B 0C 0D 0E 0F</div>
          <div class="col-span-3 text-right text-on-surface-variant">TEXT DECODED (ASCII)</div>
        </div>
        <div id="hex-rows-container" class="flex-1 overflow-y-auto px-space-xl py-space-sm font-data-mono-sm text-data-mono-sm space-y-0.5 select-text"></div>
      </div>

      <div class="col-span-12 lg:col-span-3 bg-surface-container-low flex flex-col p-space-md overflow-y-auto gap-space-md border-l border-outline-variant/30">
        <div class="font-headline-sm text-headline-sm text-primary font-bold flex items-center gap-1">
          <span class="material-symbols-outlined text-[16px]">query_stats</span>
          <span>Intérprete de Dados</span>
        </div>
        <div class="flex flex-col gap-1.5 font-data-mono-sm text-data-mono-sm">
          <div class="flex items-center justify-between p-space-sm bg-surface-container rounded">
            <span class="text-on-surface-variant font-label-caps text-label-caps">uint8</span>
            <span id="hex-prim-u8" class="text-on-surface font-semibold">N/A</span>
          </div>
          <div class="flex items-center justify-between p-space-sm bg-surface-container rounded">
            <span class="text-on-surface-variant font-label-caps text-label-caps">uint16 (LE)</span>
            <span id="hex-prim-u16" class="text-on-surface font-semibold">N/A</span>
          </div>
          <div class="flex items-center justify-between p-space-sm bg-surface-container rounded">
            <span class="text-on-surface-variant font-label-caps text-label-caps">uint32 (LE)</span>
            <span id="hex-prim-u32" class="text-secondary font-bold">N/A</span>
          </div>
        </div>

        <div class="flex flex-col gap-space-sm bg-surface-container p-space-md rounded">
          <span class="font-label-caps text-label-caps text-on-surface-variant uppercase font-bold">Diagnóstico Forense de Bloco</span>
          <div class="flex flex-col gap-1">
            <div class="flex items-center justify-between">
              <span class="text-body-sm font-body-sm text-on-surface">Entropia de Shannon:</span>
              <span id="hex-entropy-val" class="font-data-mono-sm text-data-mono-sm text-primary font-bold">0.00 bits/byte</span>
            </div>
            <div class="w-full bg-surface-container-highest h-1.5 rounded-full overflow-hidden">
              <div id="hex-entropy-bar" class="bg-primary-container h-full rounded-full" style="width: 0%;"></div>
            </div>
            <span id="hex-entropy-desc" class="text-[10px] text-outline">Baixa entropia</span>
          </div>

          <div class="flex flex-col gap-0.5 mt-space-xs p-space-sm bg-surface-container-high rounded">
            <span class="text-body-sm font-body-sm text-secondary font-semibold">Assinatura Mágica (Magic Header):</span>
            <span id="hex-magic-sig" class="font-data-mono-sm text-data-mono-sm text-on-surface font-bold">N/A</span>
            <span id="hex-magic-desc" class="text-[10px] text-on-surface-variant"></span>
          </div>

          <div class="flex flex-col gap-0.5 mt-space-xs">
            <span class="font-label-caps text-label-caps text-on-surface-variant uppercase">SHA-256 Parcial (64KB Header):</span>
            <div id="hex-sha256" class="p-space-sm bg-surface-container-lowest rounded font-data-mono-sm text-data-mono-sm text-outline-variant select-all break-all">N/A</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<!-- ============================================================================
     JAVASCRIPT ENGINE: SINCRONIZAÇÃO EM TEMPO REAL COM O BACKEND PYTHON
     ============================================================================ -->
<script>
let APP_STATE = null;
let ACTIVE_TAB = 'pastas-quentes';
let HOT_CATEGORY = 'ALL';
let CRIT_CATEGORY = 'ALL';
let SMART_FILTER = 'all';
let SMART_HEX_MODE = true;
let CURRENT_HEX_PATH = '';
let CURRENT_HEX_DUMP = '';
let WAS_SCANNING_PREV = false;
let LAST_RENDER_SIGNATURE = '';

function escapeHtml(str) {
  return String(str ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function showToast(msg) {
  const toast = document.getElementById('toast-clipboard');
  const text = document.getElementById('toast-text');
  if (!toast || !text) return;
  text.innerText = msg;
  toast.classList.remove('translate-y-16', 'opacity-0');
  toast.classList.add('translate-y-0', 'opacity-100');
  setTimeout(() => {
    toast.classList.add('translate-y-16', 'opacity-0');
    toast.classList.remove('translate-y-0', 'opacity-100');
  }, 2600);
}

function fallbackCopy(text, msg) {
  try {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.top = '-9999px';
    ta.style.left = '-9999px';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(ta);
    if (ok) {
      showToast(msg || 'Copiado para a área de transferência!');
    } else {
      showToast('Copiado!');
    }
  } catch (err) {
    showToast('Falha ao acessar área de transferência.');
  }
}

function copyTextValue(val, toastMsg) {
  if (!val) return;
  const msg = toastMsg || 'Copiado para a área de transferência!';
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(val)
      .then(() => showToast(msg))
      .catch(() => fallbackCopy(val, msg));
  } else {
    fallbackCopy(val, msg);
  }
}

function copySerialNumber() {
  const sn = APP_STATE?.badge?.serial_number || 'N/A';
  copyTextValue(sn, 'Serial Number copiado: ' + sn);
}

function switchTab(tabId) {
  ACTIVE_TAB = tabId;
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  const target = document.getElementById('panel-' + tabId);
  if (target) target.classList.add('active');

  document.querySelectorAll('.nav-tab').forEach(btn => {
    btn.classList.remove('bg-surface-container-high', 'text-primary', 'font-bold');
    btn.classList.add('text-on-surface-variant');
  });
  const activeBtn = document.getElementById('nav-' + tabId);
  if (activeBtn) {
    activeBtn.classList.remove('text-on-surface-variant');
    activeBtn.classList.add('bg-surface-container-high', 'text-primary', 'font-bold');
  }
}

async function apiPost(endpoint, payload = {}) {
  try {
    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return await res.json();
  } catch (err) {
    return { ok: false, error: String(err) };
  }
}

async function fetchState() {
  try {
    const res = await fetch('/api/state', { cache: 'no-store' });
    if (!res.ok) return;
    const data = await res.json();
    const isNowScanning = Boolean(data.scan?.is_scanning);
    const hasFinished = Boolean(data.scan?.has_finished);

    // Transição automática inteligente ao finalizar varredura
    if (WAS_SCANNING_PREV && !isNowScanning && hasFinished) {
      showToast('Varredura forense finalizada! Dados consolidados.');
      if (ACTIVE_TAB === 'live-monitor') {
        switchTab('resumo-pos-varredura');
      }
    }
    WAS_SCANNING_PREV = isNowScanning;
    APP_STATE = data;

    // Se estiver em modo estático (fora de varredura), evita re-renderizar desnecessariamente o DOM
    const stateSig = `${data.selected_path}|${isNowScanning}|${data.scan?.scanned_files}|${data.results?.hot_folders_total}|${data.results?.critical_items_total}|${data.results?.errors_total}|${data.badge?.serial_number}`;
    if (!isNowScanning && stateSig === LAST_RENDER_SIGNATURE) {
      return;
    }
    LAST_RENDER_SIGNATURE = stateSig;
    renderAll();
  } catch (e) {}
}

async function onDriveSelected(path) {
  if (!path) return;
  showToast('Carregando informações da unidade: ' + path);
  const r = await apiPost('/api/select_target', { path });
  if (!r.ok) {
    showToast('Aviso: ' + (r.error || 'Não foi possível carregar a unidade selecionada.'));
  }
  await fetchState();
}

async function refreshDrives() {
  showToast('Reconsultando unidades e S.M.A.R.T. via WMI...');
  await apiPost('/api/refresh_drives');
  await fetchState();
}

async function pickManualFolder() {
  showToast('Abrindo seletor de pasta nativo...');
  const r = await apiPost('/api/pick_folder');
  if (r.ok) {
    showToast('Pasta selecionada: ' + r.selected_path);
    await fetchState();
  }
}

async function startScan() {
  const r = await apiPost('/api/scan/start');
  if (r.ok) {
    WAS_SCANNING_PREV = true;
    switchTab('live-monitor');
    showToast('Varredura Read-Only iniciada!');
    await fetchState();
  } else if (r.error) {
    showToast(r.error);
  }
}

async function stopScan() {
  const r = await apiPost('/api/scan/stop');
  if (r.ok) {
    showToast('Solicitação de parada enviada. Preservando achados...');
    await fetchState();
  }
}

async function openInExplorer(targetPath) {
  if (!targetPath) return;
  showToast('Abrindo no Explorer: ' + targetPath);
  const r = await apiPost('/api/open_explorer', { path: targetPath });
  if (!r.ok) {
    showToast('Não foi possível abrir o Explorer para: ' + targetPath);
  }
}

function renderAll() {
  if (!APP_STATE) return;
  const b = APP_STATE.badge;
  const s = APP_STATE.scan;
  const r = APP_STATE.results;

  // 1. Dropdown de Drives
  const sel = document.getElementById('drive-select');
  if (sel) {
    const drives = APP_STATE.drives || [];
    const currentPath = APP_STATE.selected_path;
    let hasCustom = !drives.some(d => d.path === currentPath);
    let optsHtml = drives.map(d =>
      `<option class="bg-surface-container-low text-on-surface" value="${escapeHtml(d.path)}" ${d.path === currentPath ? 'selected' : ''}>${escapeHtml(d.label)}</option>`
    ).join('');
    if (hasCustom && currentPath) {
      optsHtml = `<option class="bg-surface-container-low text-on-surface" value="${escapeHtml(currentPath)}" selected>${escapeHtml(currentPath)} (Pasta Manual)</option>` + optsHtml;
    }
    if (sel.innerHTML !== optsHtml) sel.innerHTML = optsHtml;
  }

  // 2. Barra Superior de Status
  document.getElementById('top-current-dir').innerText = s.current_dir || '';
  document.getElementById('top-elapsed').innerText = s.elapsed_formatted || '00:00:00';
  document.getElementById('top-files').innerText = (s.scanned_files || 0).toLocaleString('pt-BR');
  document.getElementById('top-dirs').innerText = (s.scanned_dirs || 0).toLocaleString('pt-BR');
  document.getElementById('top-hot').innerText = (s.hot_folders_count || 0).toLocaleString('pt-BR');
  document.getElementById('top-crit').innerText = (s.critical_count || 0).toLocaleString('pt-BR');
  document.getElementById('top-err').innerText = (s.errors_count || 0).toLocaleString('pt-BR');

  document.getElementById('badge-nav-hot').innerText = r.hot_folders_total || 0;
  document.getElementById('badge-nav-crit').innerText = r.critical_items_total || 0;
  document.getElementById('badge-nav-users').innerText = (b.detected_users || []).length;
  document.getElementById('badge-nav-err').innerText = r.errors_total || 0;

  const startBtn = document.getElementById('btn-start-scan');
  const startBtnText = document.getElementById('btn-start-scan-text');
  const stopBtn = document.getElementById('btn-stop-scan');
  if (s.is_scanning) {
    if (startBtnText) startBtnText.innerText = 'Varrendo...';
    if (startBtn) {
      startBtn.disabled = true;
      startBtn.classList.add('opacity-60', 'cursor-not-allowed');
    }
    if (stopBtn) {
      stopBtn.disabled = false;
      stopBtn.classList.remove('opacity-60', 'cursor-not-allowed');
    }
  } else {
    if (startBtnText) startBtnText.innerText = 'Iniciar Varredura';
    if (startBtn) {
      startBtn.disabled = false;
      startBtn.classList.remove('opacity-60', 'cursor-not-allowed');
    }
    if (stopBtn) {
      stopBtn.disabled = true;
      stopBtn.classList.add('opacity-60', 'cursor-not-allowed');
    }
  }

  // 3. Crachá do Disco
  document.getElementById('badge-model').innerText = b.model;
  document.getElementById('badge-mount').innerText = b.mountpoint;
  document.getElementById('badge-smart-text').innerText = 'S.M.A.R.T.: ' + b.smart_details;
  document.getElementById('badge-fs').innerText = b.filesystem;
  document.getElementById('badge-serial').innerText = b.serial_number;
  document.getElementById('badge-poh').innerText = b.power_on_summary;
  document.getElementById('badge-users').innerText = b.users_summary;
  document.getElementById('badge-last-date').innerText = b.last_activity_date;
  document.getElementById('badge-temp').innerText = (b.temperature_c || 34) + '°C';
  document.getElementById('badge-used-gb').innerText = b.formatted_used;
  document.getElementById('badge-total-gb').innerText = '/ ' + b.formatted_total;
  document.getElementById('badge-pct-label').innerText = `Capacidade em Uso (${b.percent_used}%)`;
  document.getElementById('badge-cap-bar').style.width = `${Math.min(100, b.percent_used)}%`;

  const smartPill = document.getElementById('badge-smart-pill');
  const warnBanner = document.getElementById('smart-warning-banner');
  if (b.is_healthy) {
    smartPill.className = 'font-label-badge text-label-badge bg-secondary-container text-on-secondary-container px-space-xs py-0.5 rounded flex items-center gap-1 font-bold';
    warnBanner.classList.add('hidden');
    warnBanner.classList.remove('flex');
  } else {
    smartPill.className = 'font-label-badge text-label-badge bg-error-container text-on-error-container px-space-xs py-0.5 rounded flex items-center gap-1 font-bold animate-pulse';
    warnBanner.classList.remove('hidden');
    warnBanner.classList.add('flex');
  }

  // Renderiza abas
  renderHotFolders();
  renderCriticalItems();
  renderUsersTab();
  renderTimelineTab();
  renderErrorsTable();
  renderLiveMonitor();
  renderExecutiveSummary();
  renderSmartModalContent();
}

/* ============================================================================
   RENDERIZAÇÃO ABA 1: PASTAS QUENTES
   ============================================================================ */
function setHotCategory(cat) {
  HOT_CATEGORY = cat;
  document.querySelectorAll('.hot-cat-btn').forEach(btn => {
    if (btn.dataset.cat === cat) {
      btn.classList.add('bg-primary', 'text-on-primary', 'font-bold');
      btn.classList.remove('bg-surface-container');
    } else {
      btn.classList.remove('bg-primary', 'text-on-primary', 'font-bold');
      btn.classList.add('bg-surface-container');
    }
  });
  renderHotFolders();
}

function renderHotFolders() {
  if (!APP_STATE) return;
  const r = APP_STATE.results;
  document.getElementById('kpi-hot-photos').innerText = `${(r.total_photos || 0).toLocaleString('pt-BR')} fotos`;
  document.getElementById('kpi-hot-videos').innerText = `${(r.total_videos || 0).toLocaleString('pt-BR')} vídeos`;
  document.getElementById('kpi-hot-docs').innerText = `${(r.total_docs || 0).toLocaleString('pt-BR')} docs`;
  document.getElementById('kpi-hot-volume').innerText = r.total_hot_formatted || '0 B';
  document.getElementById('kpi-hot-count-sub').innerText = `${r.hot_folders_total || 0} diretórios catalogados`;

  const query = (document.getElementById('hot-search-input')?.value || '').trim().toLowerCase();
  const sortBy = document.getElementById('hot-sort-select')?.value || 'score';
  let list = (r.hot_folders || []).filter(item => {
    const matchCat = (HOT_CATEGORY === 'ALL') || (item.category === HOT_CATEGORY);
    const matchQ = !query || item.folder_path.toLowerCase().includes(query);
    return matchCat && matchQ;
  });

  list.sort((a, b) => {
    if (sortBy === 'volume') return b.total_bytes - a.total_bytes;
    if (sortBy === 'files') return b.total_files - a.total_files;
    if (sortBy === 'recent') return b.latest_mtime - a.latest_mtime;
    return b.score - a.score;
  });

  const container = document.getElementById('hot-folders-list');
  if (!list.length) {
    container.innerHTML = `<div class="bg-surface-container-low rounded p-space-xl text-center text-on-surface-variant font-body-md">Nenhuma pasta quente para exibir com os filtros atuais. Clique em <strong>Iniciar Varredura</strong> no topo para mapear a unidade.</div>`;
    return;
  }

  container.innerHTML = list.slice(0, 120).map(h => {
    let badgeClass = 'bg-secondary-container text-on-secondary-container';
    if (h.category === 'VIDEOS') badgeClass = 'bg-tertiary-container text-on-tertiary-container';
    else if (h.category === 'DOCS') badgeClass = 'bg-primary-container text-on-primary-container';
    else if (h.category === 'MISTO') badgeClass = 'bg-surface-bright text-primary';

    return `
    <article class="bg-surface-container-low hover:bg-surface-container p-space-md rounded transition-colors flex flex-col lg:flex-row lg:items-center justify-between gap-space-md shadow-sm">
      <div class="flex items-start gap-space-md min-w-0 flex-1">
        <div class="shrink-0 flex flex-col items-center gap-1 mt-0.5">
          <span class="font-label-badge text-label-badge ${badgeClass} px-space-sm py-0.5 rounded font-bold">${escapeHtml(h.dominant_tag)}</span>
          <span class="text-secondary font-data-mono-sm text-data-mono-sm">⚡ ${h.score}</span>
        </div>
        <div class="flex flex-col min-w-0 flex-1">
          <span class="font-data-mono-md text-data-mono-md text-primary font-bold truncate select-all">${escapeHtml(h.folder_path)}</span>
          <div class="flex items-center gap-space-md mt-1 text-on-surface-variant font-data-mono-sm text-data-mono-sm flex-wrap">
            <span>🖼️ <strong class="text-on-surface">${h.photos_count.toLocaleString('pt-BR')} Fotos</strong> (&gt;50KB)</span>
            <span>•</span>
            <span>🎬 <strong class="text-on-surface">${h.videos_count.toLocaleString('pt-BR')} Vídeos</strong> (&gt;500KB)</span>
            <span>•</span>
            <span>📑 <strong class="text-on-surface">${h.docs_count.toLocaleString('pt-BR')} Docs</strong></span>
          </div>
        </div>
      </div>
      <div class="flex items-center justify-between lg:justify-end gap-space-lg shrink-0">
        <div class="flex flex-col lg:items-end">
          <span class="font-data-mono-lg text-data-mono-lg text-on-surface font-bold">${escapeHtml(h.formatted_size)}</span>
          <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant">Modificado: ${escapeHtml(h.formatted_date)}</span>
        </div>
        <div class="flex items-center gap-space-xs">
          <button onclick="copyTextValue(this.getAttribute('data-path'), 'Caminho da pasta copiado!')" data-path="${escapeHtml(h.folder_path)}" class="h-7 px-space-sm rounded bg-surface-container-high hover:bg-surface-variant text-on-surface-variant hover:text-primary flex items-center gap-1 font-body-sm text-body-sm" type="button">
            <span class="material-symbols-outlined text-[14px]">content_copy</span><span>Copiar</span>
          </button>
          <button onclick="openInExplorer(this.getAttribute('data-path'))" data-path="${escapeHtml(h.folder_path)}" class="h-7 px-space-sm rounded bg-primary hover:bg-primary-container text-on-primary flex items-center gap-1 font-body-sm text-body-sm font-semibold shadow-sm" type="button">
            <span class="material-symbols-outlined text-[15px]">folder_open</span><span>Explorar</span>
          </button>
        </div>
      </div>
    </article>`;
  }).join('');
}

/* ============================================================================
   RENDERIZAÇÃO ABA 2: ARQUIVOS CRÍTICOS / AGULHAS NO PALHEIRO
   ============================================================================ */
function setCritCategory(cat) {
  CRIT_CATEGORY = cat;
  document.querySelectorAll('.crit-pill').forEach(btn => {
    if (btn.dataset.cat === cat) {
      btn.classList.add('bg-primary-fixed-dim', 'text-on-primary-fixed', 'font-semibold');
      btn.classList.remove('bg-surface-container-low', 'text-on-surface-variant');
    } else {
      btn.classList.remove('bg-primary-fixed-dim', 'text-on-primary-fixed', 'font-semibold');
      btn.classList.add('bg-surface-container-low', 'text-on-surface-variant');
    }
  });
  renderCriticalItems();
}

function renderCriticalItems() {
  if (!APP_STATE) return;
  const r = APP_STATE.results;
  const query = (document.getElementById('crit-search-input')?.value || '').trim().toLowerCase();
  const sortBy = document.getElementById('crit-sort-select')?.value || 'date_desc';

  let list = (r.critical_items || []).filter(c => {
    const matchCat = (CRIT_CATEGORY === 'ALL') || (c.category_key === CRIT_CATEGORY);
    const matchQ = !query ||
      c.name.toLowerCase().includes(query) ||
      c.full_path.toLowerCase().includes(query) ||
      c.tag_label.toLowerCase().includes(query) ||
      (c.matched_reason || '').toLowerCase().includes(query);
    return matchCat && matchQ;
  });

  list.sort((a, b) => {
    if (sortBy === 'size_desc') return b.size_bytes - a.size_bytes;
    if (sortBy === 'name_asc') return a.name.localeCompare(b.name);
    return b.mtime - a.mtime;
  });

  document.getElementById('crit-display-count').innerText = `${list.length} de ${r.critical_items_total || 0} achados`;

  const container = document.getElementById('crit-items-list');
  if (!list.length) {
    container.innerHTML = `<div class="bg-surface-container-low rounded p-space-xl text-center text-on-surface-variant font-body-md">Nenhuma agulha crítica encontrada para o filtro atual.</div>`;
    return;
  }

  container.innerHTML = list.slice(0, 150).map(c => {
    const isCryptoOrKey = c.category_key === 'CRYPTO_WALLETS' || c.category_key === 'CERT_KEYS';
    const badgeCls = isCryptoOrKey
      ? 'bg-error-container text-on-error-container'
      : 'bg-surface-container-high text-primary';
    return `
    <article class="bg-surface-container-low hover:bg-surface-container p-space-sm rounded transition-all shadow-sm border-l-2 ${isCryptoOrKey ? 'border-error' : 'border-primary-fixed-dim'}">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-space-sm">
        <div class="flex-1 min-w-0 space-y-1">
          <div class="flex items-center gap-space-xs flex-wrap">
            <span class="${badgeCls} font-label-badge text-label-badge px-1.5 py-0.5 rounded font-bold">${escapeHtml(c.tag_label)}</span>
            <span class="${isCryptoOrKey ? 'text-error' : 'text-primary'} font-headline-sm text-headline-sm font-bold select-all">${escapeHtml(c.name)}</span>
          </div>
          <div class="bg-surface-container-lowest px-space-sm py-1 rounded flex items-center gap-space-xs">
            <span class="font-body-sm text-body-sm text-on-surface-variant">Heurística: <strong class="text-on-surface">${escapeHtml(c.matched_reason || 'Regra forense de alta prioridade')}</strong></span>
          </div>
          <div class="flex items-center gap-space-xs font-data-mono-sm text-data-mono-sm text-on-surface-variant truncate">
            <span class="material-symbols-outlined text-[13px] text-outline">folder</span>
            <code class="text-on-surface truncate select-all">${escapeHtml(c.full_path)}</code>
          </div>
          <div class="flex items-center gap-space-md font-data-mono-sm text-data-mono-sm text-on-surface-variant flex-wrap">
            <span>Tamanho: <strong class="text-on-surface">${escapeHtml(c.formatted_size)}</strong></span>
            <span>•</span>
            <span>Modificado: <strong class="text-on-surface">${escapeHtml(c.formatted_date)}</strong></span>
            <span>•</span>
            <span class="text-primary-fixed font-semibold">CATEGORIA: ${escapeHtml(c.category_key)}</span>
          </div>
        </div>
        <div class="flex lg:flex-col gap-space-xs shrink-0 items-end justify-start self-start pt-1">
          <div class="flex items-center gap-space-xs w-full">
            <button onclick="openHexModal(this.getAttribute('data-path'))" data-path="${escapeHtml(c.full_path)}" class="flex-1 h-7 px-space-sm bg-surface-container-high hover:bg-surface-variant text-secondary rounded flex items-center justify-center gap-1 text-body-sm font-body-sm font-semibold" title="Inspecionar Primeiros Bytes em Hex (Read-Only)" type="button">
              <span class="material-symbols-outlined text-[14px]">biotech</span><span>Ver Hex</span>
            </button>
            <button onclick="copyTextValue(this.getAttribute('data-path'), 'Caminho copiado!')" data-path="${escapeHtml(c.full_path)}" class="flex-1 h-7 px-space-sm bg-surface-container-high hover:bg-surface-variant text-primary rounded flex items-center justify-center gap-1 text-body-sm font-body-sm" type="button">
              <span class="material-symbols-outlined text-[14px]">content_copy</span><span>Copiar</span>
            </button>
          </div>
          <button onclick="openInExplorer(this.getAttribute('data-path'))" data-path="${escapeHtml(c.full_path)}" class="w-full h-7 px-space-sm bg-secondary-container hover:bg-secondary text-on-secondary-container hover:text-on-secondary rounded flex items-center justify-center gap-space-xs text-body-sm font-body-sm font-bold" type="button">
            <span class="material-symbols-outlined text-[14px]">folder_open</span>
            <span>Abrir no Explorer</span>
          </button>
          <button onclick="exportEvidenceItem(this.getAttribute('data-path'))" data-path="${escapeHtml(c.full_path)}" class="w-full h-7 px-space-sm bg-primary/20 hover:bg-primary text-primary hover:text-on-primary rounded flex items-center justify-center gap-space-xs text-body-sm font-body-sm font-bold transition-colors" title="Exportar Cópia Segura com Hash SHA-256 e Cadeia de Custódia" type="button">
            <span class="material-symbols-outlined text-[14px]">save</span>
            <span>Extrair Evidência</span>
          </button>
        </div>
      </div>
    </article>`;
  }).join('');
}

/* ============================================================================
   RENDERIZAÇÃO ABA 3: USUÁRIOS & ATALHOS RÁPIDOS
   ============================================================================ */
function renderUsersTab() {
  if (!APP_STATE) return;
  const users = APP_STATE.badge?.detected_users || [];
  const globalDirs = APP_STATE.badge?.global_dirs || [];

  const grid = document.getElementById('users-cards-grid');
  if (!users.length) {
    grid.innerHTML = `<div class="lg:col-span-12 bg-surface-container-low rounded p-space-xl text-center text-on-surface-variant">Nenhum perfil padrão em Users/ detectado nesta unidade ou pasta. Utilize os Diretórios Globais abaixo.</div>`;
  } else {
    grid.innerHTML = users.map(u => {
      const safeProfile = escapeHtml(JSON.stringify(u.profile_path));
      const sc = u.shortcuts || {};
      const shortcutItems = [
        { label: 'Área de Trabalho', sub: '...\\Desktop', icon: 'desktop_windows', color: 'text-primary', path: sc.Desktop },
        { label: 'Documentos', sub: '...\\Documents', icon: 'folder_shared', color: 'text-secondary', path: sc.Documents },
        { label: 'Downloads', sub: '...\\Downloads', icon: 'download_for_offline', color: 'text-primary-fixed', path: sc.Downloads },
        { label: 'Fotos / Imagens', sub: '...\\Pictures', icon: 'image', color: 'text-tertiary-fixed-dim', path: sc.Pictures },
        { label: 'Vídeos', sub: '...\\Videos', icon: 'video_library', color: 'text-secondary-fixed', path: sc.Videos },
        { label: 'AppData (Local/Roam)', sub: '...\\AppData', icon: 'settings_system_daydream', color: 'text-primary', path: sc.AppData },
        { label: 'Perfis de Navegadores', sub: '...\\User Data', icon: 'public', color: 'text-primary-fixed-dim', path: sc.Browsers },
        { label: 'Chaves SSH (.ssh)', sub: '...\\.ssh', icon: 'key', color: 'text-error', path: sc.SSH },
      ];

      const buttonsHtml = shortcutItems.map(item => {
        const itemPath = item.path || u.profile_path;
        return `
        <button onclick="openInExplorer(this.getAttribute('data-path'))" data-path="${escapeHtml(itemPath)}" class="group flex items-center justify-between p-space-sm rounded bg-surface-container hover:bg-surface-container-high transition-colors text-left" type="button">
          <div class="flex items-center gap-space-sm min-w-0">
            <span class="material-symbols-outlined ${item.color} text-[18px]">${item.icon}</span>
            <div class="flex flex-col min-w-0">
              <span class="font-body-sm text-body-sm text-on-surface font-semibold group-hover:text-primary transition-colors">${escapeHtml(item.label)}</span>
              <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant truncate">${escapeHtml(item.sub)}</span>
            </div>
          </div>
          <span class="material-symbols-outlined text-outline-variant group-hover:text-primary text-[15px]">arrow_forward</span>
        </button>`;
      }).join('');

      return `
      <div class="lg:col-span-6 flex flex-col bg-surface-container-low rounded p-space-md shadow-sm">
        <div class="flex items-start justify-between pb-space-sm bg-surface-container px-space-sm py-space-sm rounded mb-space-sm">
          <div class="flex items-center gap-space-sm">
            <div class="w-10 h-10 rounded bg-primary-fixed-dim flex items-center justify-center text-on-primary-fixed font-bold text-headline-sm">${escapeHtml(u.initials)}</div>
            <div class="flex flex-col">
              <div class="flex items-center gap-space-xs">
                <span class="font-headline-sm text-headline-sm text-primary font-bold">${escapeHtml(u.username)}</span>
                <span class="font-label-badge text-label-badge bg-secondary-container text-on-secondary-container px-space-xs py-0.5 rounded">${escapeHtml(u.role)}</span>
              </div>
              <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant truncate">${escapeHtml(u.profile_path)}</span>
            </div>
          </div>
          <button onclick="openInExplorer(this.getAttribute('data-path'))" data-path="${escapeHtml(u.profile_path)}" class="flex items-center gap-1 px-space-sm py-1 rounded bg-primary hover:bg-primary-container text-on-primary font-headline-sm text-headline-sm font-bold" type="button">
            <span class="material-symbols-outlined text-[15px]">open_in_new</span>
            <span>Abrir Perfil</span>
          </button>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-space-xs">${buttonsHtml}</div>
      </div>`;
    }).join('');
  }

  const gGrid = document.getElementById('global-dirs-grid');
  gGrid.innerHTML = globalDirs.map(g => {
    return `
    <div class="flex flex-col justify-between bg-surface-container p-space-sm rounded hover:bg-surface-container-high transition-colors">
      <div class="flex items-start justify-between gap-space-xs mb-space-xs">
        <div class="flex items-center gap-space-xs min-w-0">
          <span class="material-symbols-outlined text-primary text-[18px]">${escapeHtml(g.icon)}</span>
          <span class="font-body-sm text-body-sm text-on-surface font-bold truncate">${escapeHtml(g.label)}</span>
        </div>
        <span class="font-label-badge text-label-badge bg-surface-container-lowest text-secondary px-1 rounded">${escapeHtml(g.tag)}</span>
      </div>
      <div class="font-data-mono-sm text-data-mono-sm text-on-surface-variant truncate mb-space-sm">${escapeHtml(g.path)}</div>
      <button onclick="openInExplorer(this.getAttribute('data-path'))" data-path="${escapeHtml(g.path)}" class="w-full flex items-center justify-center gap-1 py-1 rounded bg-surface-container-highest hover:bg-surface-bright text-on-surface font-body-sm text-body-sm" type="button">
        <span class="material-symbols-outlined text-[14px]">open_in_new</span>
        <span>Explorar Pasta</span>
      </button>
    </div>`;
  }).join('');
}

/* ============================================================================
   RENDERIZAÇÃO ABA 4: LINHA DO TEMPO ANUAL (TIMELINE)
   ============================================================================ */
function renderTimelineTab() {
  if (!APP_STATE) return;
  const r = APP_STATE.results;
  const s = APP_STATE.scan;
  const b = APP_STATE.badge;

  document.getElementById('timeline-summary-text').innerText = r.timeline_summary;
  document.getElementById('tl-span').innerText = r.timeline_span || 'N/A';
  document.getElementById('tl-files').innerText = (s.scanned_files || 0).toLocaleString('pt-BR');
  document.getElementById('tl-vol').innerText = r.total_hot_formatted || '0 B';
  document.getElementById('tl-crit').innerText = (r.critical_items_total || 0).toLocaleString('pt-BR');
  document.getElementById('tl-peak-year').innerText = r.peak_year || '—';
  document.getElementById('tl-last-activity').innerText = b.last_activity_date || 'N/A';

  const stats = r.timeline_stats || [];
  const barsContainer = document.getElementById('timeline-bars-container');
  const tbody = document.getElementById('timeline-table-body');

  if (!stats.length) {
    barsContainer.innerHTML = `<div class="p-space-lg text-center text-on-surface-variant">Inicie a varredura para gerar o histograma anual de criação e modificação de arquivos.</div>`;
    tbody.innerHTML = `<tr><td colspan="8" class="px-space-md py-space-md text-center text-on-surface-variant">Sem dados cronológicos.</td></tr>`;
    return;
  }

  barsContainer.innerHTML = stats.map(st => `
    <div class="flex flex-col gap-space-xs ${st.is_peak ? 'bg-surface-container p-space-sm rounded border border-primary/40' : 'bg-surface-container/60 p-space-sm rounded'}">
      <div class="flex items-center justify-between font-data-mono-md text-data-mono-md flex-wrap gap-2">
        <div class="flex items-center gap-space-md flex-wrap">
          <span class="font-headline-sm text-headline-sm font-bold ${st.is_peak ? 'text-primary' : 'text-on-surface'} w-14">${st.year}</span>
          <span class="text-secondary font-semibold">${st.total_files.toLocaleString('pt-BR')} arqs</span>
          <span>•</span>
          <span class="text-primary font-semibold">${escapeHtml(st.formatted_size)}</span>
          <span>•</span>
          <span class="bg-error-container text-on-error-container px-1 rounded text-label-badge font-label-badge">${st.critical_count} Críticos</span>
          ${st.is_peak ? '<span class="bg-secondary-container text-on-secondary-container px-space-xs py-0.5 rounded text-label-badge font-label-badge font-bold">★ ANO DE PICO FORENSE</span>' : ''}
        </div>
        <span class="text-on-surface-variant font-data-mono-sm text-data-mono-sm">${st.disk_share_pct}% do volume</span>
      </div>
      <div class="w-full h-3.5 bg-surface-container-lowest rounded-sm overflow-hidden flex" style="width: ${st.bar_scale}%;">
        <div class="h-full bg-secondary" style="width: ${st.photos_pct}%" title="Fotos: ${st.photos_count}"></div>
        <div class="h-full bg-tertiary-container" style="width: ${st.videos_pct}%" title="Vídeos: ${st.videos_count}"></div>
        <div class="h-full bg-primary-fixed-dim" style="width: ${st.docs_pct}%" title="Docs: ${st.docs_count}"></div>
        <div class="h-full bg-error" style="width: ${st.crit_pct}%" title="Críticos: ${st.critical_count}"></div>
      </div>
    </div>
  `).join('');

  tbody.innerHTML = stats.map(st => `
    <tr class="hover:bg-surface-container/60 transition-colors h-9">
      <td class="px-space-md py-1 font-bold ${st.is_peak ? 'text-primary' : 'text-on-surface'}">${st.year} ${st.is_peak ? '★' : ''}</td>
      <td class="px-space-md py-1 text-secondary font-semibold">${st.total_files.toLocaleString('pt-BR')}</td>
      <td class="px-space-md py-1 text-primary">${escapeHtml(st.formatted_size)}</td>
      <td class="px-space-md py-1 text-on-surface">${st.photos_count.toLocaleString('pt-BR')}</td>
      <td class="px-space-md py-1 text-on-surface">${st.videos_count.toLocaleString('pt-BR')}</td>
      <td class="px-space-md py-1 text-on-surface">${st.docs_count.toLocaleString('pt-BR')}</td>
      <td class="px-space-md py-1"><span class="bg-error-container text-on-error-container px-1.5 py-0.5 rounded font-label-badge text-label-badge">${st.critical_count}</span></td>
      <td class="px-space-md py-1 text-on-surface font-semibold">${st.disk_share_pct}%</td>
    </tr>
  `).join('');
}

/* ============================================================================
   RENDERIZAÇÃO ABA 5: LOG DE ERROS / BAD BLOCKS
   ============================================================================ */
function renderErrorsTable() {
  if (!APP_STATE) return;
  const r = APP_STATE.results;
  const b = APP_STATE.badge;
  const allErrors = r.errors || [];

  const ioCount = allErrors.filter(e => e.category !== 'acl').length;
  const aclCount = allErrors.filter(e => e.category === 'acl').length;

  document.getElementById('err-kpi-io').innerText = ioCount;
  document.getElementById('err-kpi-acl').innerText = aclCount;
  document.getElementById('err-kpi-total').innerText = allErrors.length;
  document.getElementById('err-kpi-smart').innerText = `${b.reallocated_sectors || 0} / ${b.pending_sectors || 0}`;

  const q = (document.getElementById('err-search-input')?.value || '').trim().toLowerCase();
  const hideAcl = Boolean(document.getElementById('err-hide-acl')?.checked);

  const filtered = allErrors.filter(e => {
    if (hideAcl && e.category === 'acl') return false;
    if (!q) return true;
    return e.path.toLowerCase().includes(q) || e.error_type.toLowerCase().includes(q) || e.message.toLowerCase().includes(q);
  });

  const tbody = document.getElementById('err-table-body');
  if (!filtered.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="px-space-md py-space-lg text-center text-secondary font-semibold">✓ Nenhum erro de leitura ou Bad Block registrado para os filtros atuais.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(e => {
    return `
    <tr class="hover:bg-surface-container transition-colors">
      <td class="px-space-md py-1.5 text-on-surface-variant whitespace-nowrap">${escapeHtml(e.timestamp)}</td>
      <td class="px-space-md py-1.5"><span class="px-space-xs py-0.5 rounded bg-error-container text-on-error-container font-label-badge text-label-badge font-bold">${escapeHtml(e.error_type)}</span></td>
      <td class="px-space-md py-1.5 text-error font-semibold">${escapeHtml(e.lba)}</td>
      <td class="px-space-md py-1.5 text-on-surface font-semibold max-w-xs truncate" title="${escapeHtml(e.path)}">${escapeHtml(e.path)}</td>
      <td class="px-space-md py-1.5 text-on-surface-variant max-w-md truncate">${escapeHtml(e.message)}</td>
      <td class="px-space-md py-1.5 text-right whitespace-nowrap">
        <button onclick="copyTextValue(this.getAttribute('data-path'), 'Caminho copiado!')" data-path="${escapeHtml(e.path)}" class="px-space-xs py-0.5 bg-surface-container-high hover:bg-surface-variant text-primary rounded text-[10px] font-label-caps uppercase" type="button">Copiar</button>
      </td>
    </tr>`;
  }).join('');
}

function exportErrorDumpTxt() {
  if (!APP_STATE) return;
  const errs = APP_STATE.results?.errors || [];
  let lines = [
    "================================================================================",
    "GEIO DISKRADAR v2.2.0 - FORENSIC READ ERROR AUDIT DUMP",
    "Unidade: " + (APP_STATE.selected_path || ""),
    "Data: " + new Date().toLocaleString('pt-BR'),
    "================================================================================",
    ""
  ];
  errs.forEach(e => {
    lines.push(`[#${e.id}] ${e.timestamp} | ${e.error_type} | ${e.path}`);
    lines.push(`    Detalhe: ${e.message}`);
  });
  const blob = new Blob([lines.join("\n")], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'GeioDiskRadar_ErrorDump.txt';
  a.click();
  URL.revokeObjectURL(url);
  showToast('Dump .TXT de erros exportado!');
}

/* ============================================================================
   RENDERIZAÇÃO ABA 6: MONITOR AO VIVO (LIVE SCAN MONITOR)
   ============================================================================ */
function renderLiveMonitor() {
  if (!APP_STATE) return;
  const s = APP_STATE.scan;
  const r = APP_STATE.results;

  const spin = document.getElementById('live-spin-icon');
  if (s.is_scanning) {
    spin.classList.add('animate-spin');
    document.getElementById('live-banner-title').innerText = 'VARREDURA FORENSE EM ANDAMENTO // MULTI-STAGE READ-ONLY';
  } else {
    spin.classList.remove('animate-spin');
    document.getElementById('live-banner-title').innerText = s.has_finished
      ? 'VARREDURA CONCLUÍDA // CONSOLE DE AUDITORIA PRESERVADO'
      : 'MONITOR DE VARREDURA EM ESPERA (STANDBY)';
  }
  document.getElementById('live-banner-sub').innerText = s.current_dir || '';
  document.getElementById('live-elapsed').innerText = s.elapsed_formatted || '00:00:00';
  document.getElementById('live-rate').innerText = `${(s.files_per_sec || 0).toLocaleString('pt-BR')} arqs/seg`;
  document.getElementById('live-files').innerText = (s.scanned_files || 0).toLocaleString('pt-BR');
  document.getElementById('live-dirs').innerText = (s.scanned_dirs || 0).toLocaleString('pt-BR');
  document.getElementById('live-hot').innerText = (s.hot_folders_count || 0).toLocaleString('pt-BR');
  document.getElementById('live-crit').innerText = (s.critical_count || 0).toLocaleString('pt-BR');
  document.getElementById('live-err-sub').innerText = `${s.errors_count || 0} incidentes I/O`;

  const term = document.getElementById('live-terminal-stream');
  const wasNearBottom = (term.scrollHeight - term.scrollTop - term.clientHeight) < 60;
  const logs = s.live_logs || [];
  term.innerHTML = logs.map(l => {
    let colorCls = 'text-on-surface-variant';
    if (l.level === 'crit') colorCls = 'bg-error-container/20 p-1 rounded text-error font-bold';
    else if (l.level === 'warn') colorCls = 'text-amber-400';
    else if (l.level === 'info') colorCls = 'text-primary-fixed-dim';
    return `
      <div class="flex items-start gap-2 ${colorCls}">
        <span class="text-outline shrink-0">${escapeHtml(l.time)}</span>
        <span class="font-bold shrink-0">${escapeHtml(l.tag)}</span>
        <span class="truncate">${escapeHtml(l.msg)}</span>
      </div>`;
  }).join('');
  if (wasNearBottom || s.is_scanning) {
    term.scrollTop = term.scrollHeight;
  }

  const feed = document.getElementById('live-findings-feed');
  const crits = (r.critical_items || []).slice(0, 8);
  if (!crits.length) {
    feed.innerHTML = `<div class="p-space-md text-center text-on-surface-variant font-data-mono-sm">Nenhuma agulha crítica detectada até o momento.</div>`;
  } else {
    feed.innerHTML = crits.map(c => {
      return `
      <div class="bg-surface-container rounded p-space-sm flex flex-col gap-1 border-l-2 border-error">
        <div class="flex items-center justify-between">
          <span class="px-1.5 py-0.5 rounded bg-error-container text-on-error-container font-label-caps text-label-caps font-bold">${escapeHtml(c.tag_label)}</span>
          <span class="font-data-mono-sm text-data-mono-sm text-on-surface-variant">${escapeHtml(c.formatted_size)}</span>
        </div>
        <div class="font-headline-sm text-headline-sm text-primary font-bold truncate">${escapeHtml(c.name)}</div>
        <div class="font-data-mono-sm text-data-mono-sm text-on-surface-variant truncate">${escapeHtml(c.full_path)}</div>
        <div class="flex items-center justify-end gap-space-xs pt-1">
          <button onclick="openHexModal(this.getAttribute('data-path'))" data-path="${escapeHtml(c.full_path)}" class="px-space-xs py-0.5 rounded bg-primary-container text-on-primary-container font-label-caps text-label-caps font-bold" type="button">Ver Hex</button>
          <button onclick="openInExplorer(this.getAttribute('data-path'))" data-path="${escapeHtml(c.full_path)}" class="px-space-xs py-0.5 rounded bg-surface-container-high text-on-surface font-label-caps text-label-caps" type="button">Explorer</button>
        </div>
      </div>`;
    }).join('');
  }
}

/* ============================================================================
   RENDERIZAÇÃO ABA 7: RESUMO EXECUTIVO PÓS-VARREDURA
   ============================================================================ */
function renderExecutiveSummary() {
  if (!APP_STATE) return;
  const b = APP_STATE.badge;
  const s = APP_STATE.scan;
  const r = APP_STATE.results;

  document.getElementById('exec-sha256').innerText = r.evidence_sha256 || 'N/A';
  document.getElementById('exec-device-summary').innerText = `${b.mountpoint} — ${b.model} (S/N: ${b.serial_number} • ${b.formatted_total})`;

  const topCrit = document.getElementById('exec-top-crit');
  const crits = (r.critical_items || []).slice(0, 6);
  if (!crits.length) {
    topCrit.innerHTML = `<div class="p-space-md text-on-surface-variant font-data-mono-sm">Nenhum arquivo crítico catalogado ainda.</div>`;
  } else {
    topCrit.innerHTML = crits.map(c => {
      return `
      <div class="bg-surface-container-lowest p-space-sm rounded flex items-center justify-between gap-space-sm">
        <div class="min-w-0 flex-1">
          <div class="flex items-center gap-space-xs">
            <span class="bg-error-container text-on-error-container px-1.5 py-0.5 rounded font-label-badge text-label-badge font-bold">${escapeHtml(c.tag_label)}</span>
            <span class="text-primary font-bold truncate">${escapeHtml(c.name)}</span>
          </div>
          <div class="font-data-mono-sm text-data-mono-sm text-on-surface-variant truncate mt-0.5">${escapeHtml(c.full_path)}</div>
        </div>
        <div class="flex items-center gap-1 shrink-0">
          <button onclick="openHexModal(this.getAttribute('data-path'))" data-path="${escapeHtml(c.full_path)}" class="px-space-xs py-0.5 rounded bg-primary-container text-on-primary-container font-label-caps text-label-caps font-bold" type="button">Hex</button>
          <button onclick="openInExplorer(this.getAttribute('data-path'))" data-path="${escapeHtml(c.full_path)}" class="px-space-xs py-0.5 rounded bg-surface-container-high text-secondary font-label-caps text-label-caps font-bold" type="button">Explorer</button>
        </div>
      </div>`;
    }).join('');
  }

  const topHot = document.getElementById('exec-top-hot');
  const hots = (r.hot_folders || []).slice(0, 6);
  if (!hots.length) {
    topHot.innerHTML = `<div class="p-space-md text-on-surface-variant font-data-mono-sm">Nenhuma pasta quente catalogada ainda.</div>`;
  } else {
    topHot.innerHTML = hots.map(h => {
      return `
      <div class="bg-surface-container-lowest p-space-sm rounded flex items-center justify-between gap-space-sm">
        <div class="min-w-0 flex-1">
          <div class="flex items-center justify-between">
            <span class="text-secondary font-bold font-data-mono-sm text-data-mono-sm truncate">${escapeHtml(h.folder_path)}</span>
            <span class="text-primary font-bold font-data-mono-sm text-data-mono-sm shrink-0 ml-2">${escapeHtml(h.formatted_size)}</span>
          </div>
          <div class="text-[11px] text-on-surface-variant font-data-mono-sm">${h.photos_count} fotos • ${h.videos_count} vídeos • ${h.docs_count} docs</div>
        </div>
        <button onclick="openInExplorer(this.getAttribute('data-path'))" data-path="${escapeHtml(h.folder_path)}" class="px-space-xs py-0.5 rounded bg-surface-container-high text-primary font-label-caps text-label-caps" type="button">Abrir</button>
      </div>`;
    }).join('');
  }
}

/* ============================================================================
   MODAL 8: S.M.A.R.T. AVANÇADO
   ============================================================================ */
function openSmartModal() {
  document.getElementById('modal-smart').classList.remove('hidden');
  renderSmartModalContent();
}

function closeSmartModal() {
  document.getElementById('modal-smart').classList.add('hidden');
}

function setSmartFilter(f) {
  SMART_FILTER = f;
  renderSmartModalContent();
}

function toggleSmartHexDec() {
  SMART_HEX_MODE = !SMART_HEX_MODE;
  document.getElementById('smart-raw-mode-label').innerText = SMART_HEX_MODE ? 'RAW HEX' : 'DECIMAL';
  renderSmartModalContent();
}

function renderSmartModalContent() {
  if (!APP_STATE?.smart_diag) return;
  const sd = APP_STATE.smart_diag;
  document.getElementById('smart-modal-score').innerText = sd.score + '%';
  document.getElementById('smart-modal-banner').innerText = sd.status_banner;
  document.getElementById('smart-modal-risk').innerText = sd.risk_label;
  document.getElementById('smart-modal-bar').style.width = sd.score + '%';

  document.getElementById('sm-card-temp').innerText = sd.temp_c + '°C';
  document.getElementById('sm-card-poh').innerText = sd.poh.toLocaleString('pt-BR') + 'h';
  document.getElementById('sm-card-days').innerText = `~${sd.poh_days} dias`;
  document.getElementById('sm-card-cycles').innerText = sd.power_cycles.toLocaleString('pt-BR');
  document.getElementById('sm-card-realloc').innerText = sd.reallocated;
  document.getElementById('sm-card-pending').innerText = sd.pending;
  document.getElementById('sm-card-unc').innerText = sd.uncorrectable;

  const attrs = (sd.attributes || []).filter(a => SMART_FILTER === 'all' || a.category === SMART_FILTER);
  const tbody = document.getElementById('smart-modal-tbody');
  tbody.innerHTML = attrs.map(a => {
    const isWarn = a.status !== 'OK';
    return `
    <tr class="hover:bg-surface-container/60 transition-colors ${isWarn ? 'bg-error-container/10' : ''}">
      <td class="py-1.5 px-space-md text-on-surface-variant">${escapeHtml(a.id_dec)} <span class="text-outline">(${escapeHtml(a.id_hex)})</span></td>
      <td class="py-1.5 px-space-md font-medium ${isWarn ? 'text-error font-bold' : 'text-on-surface'}">${escapeHtml(a.name)}</td>
      <td class="py-1.5 px-space-md text-center">
        <span class="px-space-xs py-0.5 rounded ${isWarn ? 'bg-error-container text-on-error-container' : 'bg-secondary-container/30 text-secondary'} font-label-caps text-label-caps font-bold">${escapeHtml(a.status)}</span>
      </td>
      <td class="py-1.5 px-space-md text-right">${escapeHtml(a.norm)}</td>
      <td class="py-1.5 px-space-md text-right text-on-surface-variant">${escapeHtml(a.worst)}</td>
      <td class="py-1.5 px-space-md text-right text-outline">${escapeHtml(a.thresh)}</td>
      <td class="py-1.5 px-space-md text-right font-bold ${isWarn ? 'text-error' : 'text-primary'}">${escapeHtml(SMART_HEX_MODE ? a.raw_hex : a.raw_dec)}</td>
      <td class="py-1.5 px-space-md text-on-surface-variant">${escapeHtml(a.diag)}</td>
    </tr>`;
  }).join('');
}

/* ============================================================================
   MODAL 9: EXPORTAÇÃO DO RELATÓRIO HTML
   ============================================================================ */
function openExportModal() {
  if (APP_STATE) {
    document.getElementById('export-modal-path').innerText = APP_STATE.suggested_report_path || 'Relatorio.html';
    document.getElementById('exp-prev-model').innerText = `${APP_STATE.badge.model} (${APP_STATE.badge.serial_number})`;
    document.getElementById('exp-prev-hot').innerText = `${APP_STATE.results.hot_folders_total} pastas (${APP_STATE.results.total_hot_formatted})`;
    document.getElementById('exp-prev-crit').innerText = `${APP_STATE.results.critical_items_total} achados`;
    document.getElementById('exp-prev-users').innerText = APP_STATE.badge.users_summary;
  }
  document.getElementById('modal-export').classList.remove('hidden');
}

function closeExportModal() {
  document.getElementById('modal-export').classList.add('hidden');
}

async function pickReportOutput() {
  const r = await apiPost('/api/pick_report_output');
  if (r.ok && r.output_path) {
    document.getElementById('export-modal-path').innerText = r.output_path;
    showToast('Destino atualizado!');
  }
}

async function confirmExportReport() {
  const openAfter = Boolean(document.getElementById('export-open-after')?.checked);
  const outPath = document.getElementById('export-modal-path')?.innerText || '';
  showToast('Gerando Catálogo de Autópsia HTML Autocontido...');
  const r = await apiPost('/api/export_report', { open_after: openAfter, output_path: outPath });
  if (r.ok) {
    closeExportModal();
    showToast('Relatório HTML salvo em: ' + r.saved_path);
  } else {
    showToast('Erro ao exportar: ' + (r.error || 'Desconhecido'));
  }
}

/* ============================================================================
   MODAL 10: HEX VIEWER READ-ONLY
   ============================================================================ */
async function openHexModal(filePath) {
  let target = filePath;
  if (!target && APP_STATE) {
    const firstCrit = APP_STATE.results?.critical_items?.[0]?.full_path;
    target = firstCrit || APP_STATE.selected_path;
  }
  CURRENT_HEX_PATH = target;
  document.getElementById('hex-offset-input').value = 0;
  document.getElementById('modal-hex').classList.remove('hidden');
  await loadHexData(target, 0);
}

function closeHexModal() {
  document.getElementById('modal-hex').classList.add('hidden');
}

async function stepHexOffset(delta) {
  const inp = document.getElementById('hex-offset-input');
  let curr = parseInt(inp.value || '0', 10);
  curr = Math.max(0, curr + delta);
  inp.value = curr;
  await loadHexData(CURRENT_HEX_PATH, curr);
}

async function reloadHexCurrent() {
  const inp = document.getElementById('hex-offset-input');
  let curr = Math.max(0, parseInt(inp.value || '0', 10));
  await loadHexData(CURRENT_HEX_PATH, curr);
}

async function loadHexData(path, offset) {
  const res = await apiPost('/api/hex_inspect', { path, offset, length: 512 });
  document.getElementById('hex-path-label').innerText = res.file_path || path;
  document.getElementById('hex-size-label').innerText = res.formatted_size || '0 B';
  document.getElementById('hex-offset-label').innerText = `${res.offset_hex || '0x00000000'} (LBA #${res.sector_lba || 0})`;
  document.getElementById('hex-prim-u8').innerText = res.primitives?.uint8 || 'N/A';
  document.getElementById('hex-prim-u16').innerText = res.primitives?.uint16_le || 'N/A';
  document.getElementById('hex-prim-u32').innerText = res.primitives?.uint32_le || 'N/A';
  document.getElementById('hex-entropy-val').innerText = `${res.entropy || 0} bits/byte`;
  document.getElementById('hex-entropy-bar').style.width = `${res.entropy_pct || 0}%`;
  document.getElementById('hex-entropy-desc').innerText = res.entropy_label || '';
  document.getElementById('hex-magic-sig').innerText = res.magic_signature || 'N/A';
  document.getElementById('hex-magic-desc').innerText = res.magic_details || '';
  document.getElementById('hex-sha256').innerText = res.partial_sha256 || 'N/A';
  CURRENT_HEX_DUMP = res.raw_text_dump || '';

  const container = document.getElementById('hex-rows-container');
  if (res.error_message && (!res.rows || !res.rows.length)) {
    container.innerHTML = `<div class="p-space-lg text-error font-bold">${escapeHtml(res.error_message)}</div>`;
    return;
  }

  container.innerHTML = (res.rows || []).map(row => {
    const leftBytes = row.hex_bytes.slice(0, 8).map(b => `<span class="w-5 text-center inline-block">${escapeHtml(b)}</span>`).join(' ');
    const rightBytes = row.hex_bytes.slice(8, 16).map(b => `<span class="w-5 text-center inline-block">${escapeHtml(b)}</span>`).join(' ');
    return `
      <div class="grid grid-cols-12 py-0.5 items-center hover:bg-surface-container rounded px-1 ${row.has_read_error ? 'bg-error-container/20 text-error font-bold' : ''}">
        <div class="col-span-2 text-primary font-semibold select-none">${escapeHtml(row.offset_hex)}</div>
        <div class="col-span-7 font-data-mono-sm text-on-surface">${leftBytes} <span class="text-outline mx-1">|</span> ${rightBytes}</div>
        <div class="col-span-3 text-right text-secondary font-data-mono-sm tracking-widest">${escapeHtml(row.ascii_str)}</div>
      </div>`;
  }).join('');
}

function copyHexDump() {
  copyTextValue(CURRENT_HEX_DUMP, 'Dump Hexadecimal copiado para a área de transferência!');
}

async function shutdownApp() {
  showToast('Encerrando aplicação...');
  await apiPost('/api/app/shutdown');
  try {
    window.close();
  } catch (e) {}

  // Fallback caso o navegador bloqueie window.close() em modo app
  setTimeout(() => {
    document.body.innerHTML = `
      <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;background-color:#0c0e14;color:#e2e2eb;font-family:sans-serif;text-align:center;padding:24px;">
        <div style="font-size:48px;margin-bottom:12px;">🔒</div>
        <h2 style="font-size:22px;color:#00f0ff;margin:0 0 8px 0;font-weight:bold;">Geio DiskRadar // Sessão Encerrada com Segurança</h2>
        <p style="font-size:14px;color:#849495;max-width:540px;line-height:1.5;">O motor forense Read-Only foi desativado. Todos os dados foram preservados e o disco pode ser desconectado da dock com segurança.</p>
        <p style="font-size:13px;color:#4edea3;margin-top:18px;font-weight:600;">Você já pode fechar esta janela.</p>
      </div>
    `;
  }, 450);
}

/* ============================================================================
   MODAL DIAGNÓSTICO DO SISTEMA (COMPATIBILIDADE WINDOWS)
   ============================================================================ */
async function openDiagnosticsModal() {
  document.getElementById('modal-diagnostics').classList.remove('hidden');
  await loadDiagnosticsData();
}

function closeDiagnosticsModal() {
  document.getElementById('modal-diagnostics').classList.add('hidden');
}

async function loadDiagnosticsData() {
  const container = document.getElementById('diag-checks-list');
  const badge = document.getElementById('diag-overall-badge');
  const summary = document.getElementById('diag-summary-text');
  container.innerHTML = '<div class="text-center py-6 text-on-surface-variant font-data-mono-sm">Consultando subsistemas e políticas WMI do Windows...</div>';
  badge.className = 'font-label-caps text-label-caps px-space-sm py-0.5 rounded bg-surface-container text-on-surface-variant font-bold';
  badge.innerText = 'CONSULTANDO...';

  try {
    const res = await fetch('/api/system_diagnostics').then(r => r.json());
    if (res.status === 'READY') {
      badge.className = 'font-label-caps text-label-caps px-space-sm py-0.5 rounded bg-secondary-container text-on-secondary-container font-bold';
      badge.innerText = 'PRONTO / OPERACIONAL';
      summary.innerText = `Todos os subsistemas essenciais estão validados (${res.total_checks} verificações).`;
    } else {
      badge.className = 'font-label-caps text-label-caps px-space-sm py-0.5 rounded bg-error-container text-on-error-container font-bold';
      badge.innerText = 'ATENÇÃO / REQUER AJUSTE';
      summary.innerText = `Alguns subsistemas podem operar com limitações (${res.total_checks} verificações).`;
    }

    container.innerHTML = (res.checks || []).map(c => {
      let statusBadge = '<span class="px-2 py-0.5 rounded bg-secondary-container text-on-secondary-container font-bold text-label-badge font-label-badge">PASS</span>';
      let borderCls = 'border-secondary/40';
      if (c.status === 'WARN' || c.status === 'INFO') {
        statusBadge = '<span class="px-2 py-0.5 rounded bg-surface-container-high text-primary font-bold text-label-badge font-label-badge">' + escapeHtml(c.status) + '</span>';
        borderCls = 'border-primary/40';
      } else if (c.status === 'FAIL') {
        statusBadge = '<span class="px-2 py-0.5 rounded bg-error-container text-on-error-container font-bold text-label-badge font-label-badge">FAIL</span>';
        borderCls = 'border-error/60';
      }

      return `
        <div class="bg-surface-container p-space-sm rounded border-l-2 ${borderCls} flex items-center justify-between gap-space-md">
          <div class="flex-1 min-w-0">
            <div class="flex items-center gap-space-xs">
              <strong class="font-headline-sm text-headline-sm text-on-surface">${escapeHtml(c.name)}</strong>
              ${statusBadge}
            </div>
            <div class="font-data-mono-sm text-data-mono-sm text-on-surface-variant mt-0.5 truncate">${escapeHtml(c.message)}</div>
          </div>
        </div>
      `;
    }).join('');
  } catch (err) {
    container.innerHTML = `<div class="p-space-md text-error font-bold">Falha ao consultar diagnóstico: ${escapeHtml(err.message)}</div>`;
  }
}

/* ============================================================================
   EXTRAÇÃO SEGURA DE EVIDÊNCIAS FORENSES (CADEIA DE CUSTÓDIA COM SHA-256)
   ============================================================================ */
async function exportEvidenceItem(filePath) {
  if (!filePath) return;
  showToast('Iniciando extração forense Read-Only e cálculo de Hash SHA-256...');
  try {
    const res = await apiPost('/api/export_evidence', { path: filePath });
    if (res.ok) {
      document.getElementById('evi-modal-name').innerText = res.file_name;
      document.getElementById('evi-modal-path').innerText = res.dest_path;
      document.getElementById('evi-modal-sha').innerText = res.sha256;
      document.getElementById('evi-modal-manifest').innerText = res.manifest_path;
      document.getElementById('evi-btn-open-folder').onclick = () => openInExplorer(res.destination_dir);
      document.getElementById('modal-evidence-success').classList.remove('hidden');
      showToast('Evidência extraída e validada!');
    } else {
      showToast('Falha na extração: ' + (res.error || 'Erro desconhecido'));
    }
  } catch (err) {
    showToast('Erro ao comunicar com o servidor: ' + err.message);
  }
}

function closeEvidenceModal() {
  document.getElementById('modal-evidence-success').classList.add('hidden');
}

// Fechar modais com tecla ESC
document.addEventListener('keydown', (ev) => {
  if (ev.key === 'Escape') {
    closeDiagnosticsModal();
    closeEvidenceModal();
    closeSmartModal();
    closeExportModal();
    closeHexModal();
  }
});

// Loop de sincronização e heartbeat
setInterval(fetchState, 600);
setInterval(() => apiPost('/api/heartbeat'), 2000);
window.addEventListener('DOMContentLoaded', fetchState);
</script>
</body>
</html>
"""
