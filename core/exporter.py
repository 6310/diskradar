"""
Módulo Gerador de 'Catálogo de Autópsia' (Relatório HTML Único e Autocontido).
Gera um arquivo .html 100% offline com Dark Mode elegante e busca instantânea em JavaScript
capaz de pesquisar até 50.000 arquivos relevantes de usuário em milissegundos.
"""

import datetime
import html
import json
import re
from typing import Optional

from core.disk_info import DiskBadgeInfo
from core.rules import CRITICAL_CATEGORIES, format_size
from core.scanner import ScanResult


def _sanitize_filename_part(text: str, max_len: int = 35) -> str:
    """Remove caracteres inválidos para nome de arquivo no Windows/Linux."""
    if not text:
        return "NA"
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", text.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_.")
    return (cleaned[:max_len] or "NA")


def build_default_report_filename(badge: DiskBadgeInfo) -> str:
    """
    Gera o nome padrão sugerido:
    Relatorio_YYYY-MM-DD_<Usuarios>_<Modelo>_SN-<Serial>.html
    """
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    if badge.detected_users:
        users_part = "-".join(u.username for u in badge.detected_users[:3])
    else:
        users_part = "SemUsuario"

    u_clean = _sanitize_filename_part(users_part, 30)
    m_clean = _sanitize_filename_part(badge.model, 35)
    s_clean = _sanitize_filename_part(badge.serial_number, 25)

    return f"Relatorio_{today_str}_{u_clean}_{m_clean}_SN-{s_clean}.html"


def export_html_report(
    output_path: str,
    badge: DiskBadgeInfo,
    scan_result: Optional[ScanResult],
) -> str:
    """
    Gera o arquivo HTML autocontido no caminho `output_path` e retorna o caminho salvo.
    """
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    smart_color_class = "badge-ok" if badge.is_healthy else "badge-warn"
    smart_alert_html = ""
    if not badge.is_healthy:
        smart_alert_html = (
            '<div class="smart-alert">'
            "⚠️ <strong>ALERTA DE DISCO:</strong> Risco físico detectado! "
            "Salve documentos leves antes de copiar fotos/vídeos pesados."
            "</div>"
        )

    hot_folders = scan_result.hot_folders if scan_result else []
    critical_items = scan_result.critical_items if scan_result else []
    catalog_entries = scan_result.catalog_entries if scan_result else []
    errors = scan_result.errors if scan_result else []
    timeline_stats = scan_result.timeline_stats if scan_result else []
    peak_year = scan_result.peak_year if scan_result else None
    timeline_summary = scan_result.timeline_summary if scan_result else ""

    scanned_files = scan_result.scanned_files if scan_result else 0
    scanned_dirs = scan_result.scanned_dirs if scan_result else 0
    elapsed_sec = scan_result.elapsed_seconds if scan_result else 0.0
    total_photos = scan_result.total_photos if scan_result else 0
    total_videos = scan_result.total_videos if scan_result else 0
    total_docs = scan_result.total_docs if scan_result else 0

    # Monta linhas da tabela de Pastas Quentes
    hot_rows_html = []
    for hf in hot_folders:
        hot_rows_html.append(
            f"<tr>"
            f'<td><span class="tag tag-folder">{html.escape(hf.dominant_icon_tag)}</span></td>'
            f'<td class="mono">{html.escape(hf.folder_path)}</td>'
            f'<td class="num">{hf.photos_count}</td>'
            f'<td class="num">{hf.videos_count}</td>'
            f'<td class="num">{hf.docs_count}</td>'
            f'<td class="num"><strong>{html.escape(hf.formatted_size)}</strong></td>'
            f"<td>{html.escape(hf.formatted_date)}</td>"
            f"</tr>"
        )
    hot_table_body = "\n".join(hot_rows_html) if hot_rows_html else (
        '<tr><td colspan="7" class="empty">Nenhuma pasta quente encontrada.</td></tr>'
    )

    # Estilos de tag por categoria
    cat_tag_classes = {
        "CRYPTO_WALLETS": "tag-crypto",
        "BROWSERS_CREDS": "tag-browser",
        "CAD_DESIGN": "tag-cad",
        "EMAIL_MSG": "tag-email",
        "CERT_KEYS": "tag-cert",
        "IRPF_FISCAL": "tag-fiscal",
        "DB_ERP": "tag-db",
        "ARCHIVES": "tag-archive",
        "KEYWORDS": "tag-keyword",
    }

    # Monta linhas da tabela de Arquivos Críticos
    crit_rows_html = []
    for ci in critical_items:
        tag_cls = cat_tag_classes.get(ci.category_key, "tag-crit")
        crit_rows_html.append(
            f'<tr data-cat="{html.escape(ci.category_key)}">'
            f'<td><span class="tag {tag_cls}">{html.escape(ci.tag_label)}</span></td>'
            f"<td><strong>{html.escape(ci.name)}</strong></td>"
            f'<td class="mono">{html.escape(ci.full_path)}</td>'
            f'<td class="num">{html.escape(ci.formatted_size)}</td>'
            f"<td>{html.escape(ci.formatted_date)}</td>"
            f"</tr>"
        )
    crit_table_body = "\n".join(crit_rows_html) if crit_rows_html else (
        '<tr><td colspan="5" class="empty">Nenhum arquivo crítico isolado detectado.</td></tr>'
    )

    # Monta linhas de Erros / Bad Blocks
    err_rows_html = []
    for err in errors:
        err_rows_html.append(
            f"<tr>"
            f"<td>{html.escape(err.timestamp)}</td>"
            f'<td><span class="tag tag-err">{html.escape(err.error_type)}</span></td>'
            f'<td class="mono">{html.escape(err.path)}</td>'
            f"<td>{html.escape(err.message)}</td>"
            f"</tr>"
        )
    err_table_body = "\n".join(err_rows_html) if err_rows_html else (
        '<tr><td colspan="4" class="empty">Nenhum erro de leitura ou Bad Block registrado durante a triagem.</td></tr>'
    )

    # Monta Linha do Tempo e Histograma Anual de Atividade
    max_year_files = max((s.total_files for s in timeline_stats), default=1) or 1
    timeline_rows_html = []
    for stat in timeline_stats:
        pct = max(3.0, (stat.total_files / max_year_files) * 100.0)
        is_peak = (stat.year == peak_year)
        peak_badge = ' <span class="badge-peak">★ PICO</span>' if is_peak else ""
        bar_class = "bar-fill peak-bar" if is_peak else "bar-fill"

        timeline_rows_html.append(
            f'<div class="timeline-row">'
            f'  <div class="timeline-year"><strong>{stat.year}</strong>{peak_badge}</div>'
            f'  <div class="timeline-bar-container">'
            f'    <div class="{bar_class}" style="width: {pct:.1f}%;"></div>'
            f'  </div>'
            f'  <div class="timeline-metrics">'
            f'    <span class="t-pill">📄 <strong>{stat.total_files:,}</strong> arqs</span>'
            f'    <span class="t-pill">📦 {html.escape(stat.formatted_size)}</span>'
            f'    <span class="t-sub">🖼️ {stat.photos_count:,} fotos &bull; 🎬 {stat.videos_count:,} vídeos &bull; 📑 {stat.docs_count:,} docs &bull; 🎯 {stat.critical_count:,} críticos</span>'
            f'  </div>'
            f'</div>'
        )
    timeline_body = "\n".join(timeline_rows_html) if timeline_rows_html else (
        '<div class="empty">Nenhum registro de data válido encontrado para gerar o histograma.</div>'
    )
    timeline_span_str = f"{timeline_stats[0].year} - {timeline_stats[-1].year}" if timeline_stats else "N/A"

    # Serializa catálogo pesquisável como JSON compacto para filtro instantâneo em JS
    catalog_json_data = [
        [
            entry.rel_path,
            entry.category,
            entry.formatted_size,
            entry.formatted_date,
        ]
        for entry in catalog_entries
    ]
    catalog_json_str = json.dumps(catalog_json_data, ensure_ascii=False)

    users_html = html.escape(badge.users_summary)
    last_activity_html = html.escape(badge.last_activity_date or "Não identificada")

    # Monta options do dropdown de categorias
    cat_options_html = ['<option value="ALL">Todas as Categorias</option>']
    for k, v in CRITICAL_CATEGORIES.items():
        if k != "ALL":
            cat_options_html.append(f'<option value="{html.escape(k)}">{html.escape(v)}</option>')
    cat_options_str = "\n        ".join(cat_options_html)

    html_doc = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Catálogo de Autópsia DiskRadar - {html.escape(badge.model)} ({html.escape(badge.serial_number)})</title>
<style>
  :root {{
    --bg: #0f172a;
    --card: #1e293b;
    --card-alt: #263449;
    --text: #f1f5f9;
    --muted: #94a3b8;
    --accent: #38bdf8;
    --accent-hover: #0284c7;
    --ok: #22c55e;
    --warn: #f59e0b;
    --danger: #ef4444;
    --border: #334155;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    padding: 24px;
    background-color: var(--bg);
    color: var(--text);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Ubuntu, sans-serif;
    line-height: 1.5;
  }}
  .container {{
    max-width: 1400px;
    margin: 0 auto;
  }}
  header {{
    background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.35);
  }}
  .header-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 16px;
    margin-bottom: 16px;
  }}
  h1 {{
    margin: 0;
    font-size: 1.65rem;
    color: var(--accent);
    letter-spacing: 0.5px;
  }}
  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 14px;
  }}
  .meta-box {{
    background: rgba(255,255,255,0.03);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 12px 16px;
  }}
  .meta-label {{
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--muted);
    margin-bottom: 4px;
  }}
  .meta-value {{
    font-size: 1.02rem;
    font-weight: 600;
    word-break: break-word;
  }}
  .badge-ok {{
    display: inline-block;
    background: rgba(34, 197, 94, 0.2);
    color: #4ade80;
    border: 1px solid #22c55e;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 700;
  }}
  .badge-warn {{
    display: inline-block;
    background: rgba(239, 68, 68, 0.25);
    color: #fca5a5;
    border: 1px solid #ef4444;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 700;
  }}
  .smart-alert {{
    margin-top: 16px;
    padding: 14px 18px;
    background: rgba(239, 68, 68, 0.18);
    border-left: 5px solid var(--danger);
    border-radius: 6px;
    color: #fecaca;
    font-size: 0.95rem;
  }}
  .stats-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 16px;
  }}
  .stat-pill {{
    background: var(--card-alt);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.88rem;
  }}
  section {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
  }}
  h2 {{
    margin-top: 0;
    margin-bottom: 14px;
    font-size: 1.25rem;
    color: var(--accent);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
  }}
  .controls {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 14px;
  }}
  input[type="text"], select {{
    background: #0f172a;
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 0.95rem;
    outline: none;
  }}
  input[type="text"] {{
    flex: 1;
    min-width: 260px;
  }}
  input[type="text"]:focus, select:focus {{
    border-color: var(--accent);
  }}
  .table-wrap {{
    overflow-x: auto;
    max-height: 520px;
    overflow-y: auto;
    border: 1px solid var(--border);
    border-radius: 8px;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }}
  th, td {{
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid var(--border);
  }}
  th {{
    background: #0f172a;
    color: var(--muted);
    position: sticky;
    top: 0;
    z-index: 1;
    font-weight: 600;
  }}
  tr:hover {{
    background: rgba(56, 189, 248, 0.06);
  }}
  .mono {{
    font-family: "Consolas", "JetBrains Mono", monospace;
    font-size: 0.84rem;
    word-break: break-all;
  }}
  .num {{
    text-align: right;
    white-space: nowrap;
  }}
  .tag {{
    display: inline-block;
    padding: 3px 9px;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 700;
    white-space: nowrap;
  }}
  .tag-folder {{ background: rgba(56, 189, 248, 0.18); color: #7dd3fc; }}
  .tag-crit {{ background: rgba(245, 158, 11, 0.2); color: #fcd34d; }}
  .tag-crypto {{ background: rgba(234, 179, 8, 0.25); color: #fde047; border: 1px solid #ca8a04; }}
  .tag-browser {{ background: rgba(139, 92, 246, 0.25); color: #c4b5fd; border: 1px solid #7c3aed; }}
  .tag-cad {{ background: rgba(6, 182, 212, 0.25); color: #67e8f9; border: 1px solid #0891b2; }}
  .tag-email {{ background: rgba(37, 99, 235, 0.25); color: #93c5fd; border: 1px solid #2563eb; }}
  .tag-cert {{ background: rgba(220, 38, 38, 0.25); color: #fca5a5; border: 1px solid #dc2626; }}
  .tag-fiscal {{ background: rgba(16, 185, 129, 0.25); color: #6ee7b7; border: 1px solid #059669; }}
  .tag-db {{ background: rgba(234, 88, 12, 0.25); color: #fdba74; border: 1px solid #ea580c; }}
  .tag-archive {{ background: rgba(100, 116, 139, 0.25); color: #cbd5e1; border: 1px solid #64748b; }}
  .tag-keyword {{ background: rgba(202, 138, 4, 0.25); color: #fef08a; }}
  .tag-err {{ background: rgba(239, 68, 68, 0.2); color: #fca5a5; }}
  .empty {{
    text-align: center;
    color: var(--muted);
    padding: 24px;
  }}
  .timeline-box {{
    margin-top: 10px;
    padding: 16px;
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border);
    border-radius: 8px;
  }}
  .timeline-row {{
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
    flex-wrap: wrap;
  }}
  .timeline-year {{
    width: 120px;
    font-size: 0.95rem;
    font-family: "Consolas", monospace;
  }}
  .badge-peak {{
    background: #eab308;
    color: #000000;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 2px 6px;
    border-radius: 4px;
    margin-left: 4px;
  }}
  .timeline-bar-container {{
    flex: 1;
    min-width: 200px;
    height: 12px;
    background: #0f172a;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid var(--border);
  }}
  .bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, #0284c7, #38bdf8);
    border-radius: 6px;
  }}
  .peak-bar {{
    background: linear-gradient(90deg, #ca8a04, #eab308);
  }}
  .timeline-metrics {{
    display: flex;
    gap: 8px;
    align-items: center;
    font-size: 0.85rem;
    flex-wrap: wrap;
  }}
  .t-pill {{
    background: var(--card-alt);
    border: 1px solid var(--border);
    padding: 2px 8px;
    border-radius: 6px;
  }}
  .t-sub {{
    color: var(--muted);
    font-size: 0.8rem;
  }}
  .catalog-info {{
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 10px;
  }}
  footer {{
    text-align: center;
    color: var(--muted);
    font-size: 0.82rem;
    margin-top: 30px;
    padding-bottom: 20px;
  }}
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="header-top">
      <div>
        <h1>📡 Geio DiskRadar — Catálogo de Autópsia Read-Only</h1>
        <div style="color: var(--muted); font-size: 0.9rem;">Gerado em: {now_str} | Caminho Analisado: <code>{html.escape(badge.target_path)}</code></div>
      </div>
      <div>
        <span class="{smart_color_class}">S.M.A.R.T.: {html.escape(badge.smart_details)}</span>
      </div>
    </div>

    <div class="meta-grid">
      <div class="meta-box">
        <div class="meta-label">Modelo Físico do Disco</div>
        <div class="meta-value">{html.escape(badge.model)}</div>
      </div>
      <div class="meta-box">
        <div class="meta-label">Número de Série (Serial Number)</div>
        <div class="meta-value">{html.escape(badge.serial_number)}</div>
      </div>
      <div class="meta-box">
        <div class="meta-label">Capacidade Total / Usada</div>
        <div class="meta-value">{html.escape(badge.capacity_summary)}</div>
      </div>
      <div class="meta-box">
        <div class="meta-label">Possíveis Donos (Usuários)</div>
        <div class="meta-value">{users_html}</div>
      </div>
      <div class="meta-box">
        <div class="meta-label">Último Uso Estimado</div>
        <div class="meta-value">{last_activity_html}</div>
      </div>
      <div class="meta-box">
        <div class="meta-label">Sistema de Arquivos / Ponto</div>
        <div class="meta-value">{html.escape(badge.filesystem)} ({html.escape(badge.mountpoint)})</div>
      </div>
      <div class="meta-box">
        <div class="meta-label">Horas de Ligação (Power-On)</div>
        <div class="meta-value">{html.escape(badge.power_on_summary)}</div>
      </div>
      <div class="meta-box">
        <div class="meta-label">Mídia / Rotação / Temp</div>
        <div class="meta-value">{html.escape(badge.hardware_media_summary)}</div>
      </div>
    </div>

    {smart_alert_html}

    <div class="stats-row">
      <div class="stat-pill">📁 Diretórios Varridos: <strong>{scanned_dirs:,}</strong></div>
      <div class="stat-pill">📄 Arquivos Inspecionados: <strong>{scanned_files:,}</strong></div>
      <div class="stat-pill">🖼️ Fotos Relevantes (&gt;50KB): <strong>{total_photos:,}</strong></div>
      <div class="stat-pill">🎬 Vídeos (&gt;500KB): <strong>{total_videos:,}</strong></div>
      <div class="stat-pill">📑 Documentos: <strong>{total_docs:,}</strong></div>
      <div class="stat-pill">🔥 Pastas Quentes: <strong>{len(hot_folders):,}</strong></div>
      <div class="stat-pill">🎯 Arquivos Críticos: <strong>{len(critical_items):,}</strong></div>
      <div class="stat-pill">📅 Período Ativo: <strong>{html.escape(timeline_span_str)}</strong></div>
      <div class="stat-pill">⚠️ Erros / Bad Blocks: <strong>{len(errors):,}</strong></div>
      <div class="stat-pill">⏱️ Tempo de Varredura: <strong>{elapsed_sec:.2f}s</strong></div>
    </div>
  </header>

  <!-- SEÇÃO 1: PASTAS QUENTES -->
  <section>
    <h2>1. 🔥 Pastas Quentes (Agrupamento de Mídia &amp; Documentos) <span>({len(hot_folders)} pastas)</span></h2>
    <div class="controls">
      <input type="text" id="hotSearch" placeholder="Filtrar pastas quentes por caminho..." oninput="filterTable('hotTable', this.value)">
    </div>
    <div class="table-wrap">
      <table id="hotTable">
        <thead>
          <tr>
            <th>Tipo</th>
            <th>Caminho da Pasta</th>
            <th class="num">Fotos</th>
            <th class="num">Vídeos</th>
            <th class="num">Docs</th>
            <th class="num">Tamanho Somado</th>
            <th>Data Recente</th>
          </tr>
        </thead>
        <tbody>
          {hot_table_body}
        </tbody>
      </table>
    </div>
  </section>

  <!-- SEÇÃO 2: AGULHAS NO PALHEIRO (ARQUIVOS CRÍTICOS) -->
  <section>
    <h2>2. 🎯 Agulhas no Palheiro (Cripto, Sessões, CAD, IRPF, Bancos &amp; Backups) <span>({len(critical_items)} itens)</span></h2>
    <div class="controls">
      <input type="text" id="critSearch" placeholder="Buscar por nome, extensão, palavra-chave ou caminho..." oninput="filterCritTable()">
      <select id="critCat" onchange="filterCritTable()">
        {cat_options_str}
      </select>
    </div>
    <div class="table-wrap">
      <table id="critTable">
        <thead>
          <tr>
            <th>Tag / Tipo</th>
            <th>Nome do Arquivo / Lote</th>
            <th>Caminho Completo</th>
            <th class="num">Tamanho</th>
            <th>Modificado em</th>
          </tr>
        </thead>
        <tbody>
          {crit_table_body}
        </tbody>
      </table>
    </div>
  </section>

  <!-- SEÇÃO 3: LINHA DO TEMPO & HISTOGRAMA DE ATIVIDADE -->
  <section>
    <h2>3. 📅 Linha do Tempo &amp; Histograma Anual de Atividade <span>({len(timeline_stats)} anos registrados)</span></h2>
    <div class="catalog-info">
      {html.escape(timeline_summary or "Distribuição temporal da criação e modificação dos arquivos ao longo dos anos.")}
    </div>
    <div class="timeline-box">
      {timeline_body}
    </div>
  </section>

  <!-- SEÇÃO 4: CATÁLOGO PESQUISÁVEL COMPLETO -->
  <section>
    <h2>4. 🔎 Catálogo Pesquisável Completo de Arquivos do Disco <span>({len(catalog_entries):,} arquivos indexados)</span></h2>
    <div class="catalog-info">
      Pesquise instantaneamente qualquer arquivo indexado neste HD mesmo após o descarte físico da mídia.
      (Exibindo os primeiros 300 resultados correspondentes em tempo real para máxima fluidez).
    </div>
    <div class="controls">
      <input type="text" id="catalogSearch" placeholder="Digite qualquer parte do nome do arquivo, pasta, extensão ou data (ex: carteira, 2021, .dwg, contrato)..." oninput="renderCatalog()">
    </div>
    <div id="catalogStatus" class="catalog-info"></div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Caminho Relativo</th>
            <th>Categoria</th>
            <th class="num">Tamanho</th>
            <th>Data de Modificação</th>
          </tr>
        </thead>
        <tbody id="catalogBody"></tbody>
      </table>
    </div>
  </section>

  <!-- SEÇÃO 5: LOG DE ERROS E BAD BLOCKS -->
  <section>
    <h2>5. ⚠️ Log de Erros de Leitura / Possíveis Bad Blocks <span>({len(errors)} ocorrências)</span></h2>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Horário</th>
            <th>Tipo de Falha</th>
            <th>Caminho Afetado</th>
            <th>Detalhes do Sistema</th>
          </tr>
        </thead>
        <tbody>
          {err_table_body}
        </tbody>
      </table>
    </div>
  </section>

  <footer>
    Geio DiskRadar — Triador e Indexador Read-Only de HDs e SSDs de Sucata | Relatório HTML 100% Autocontido
  </footer>
</div>

<script>
const CATALOG_DATA = {catalog_json_str};

function escapeHtml(str) {{
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}}

function filterTable(tableId, query) {{
  const q = query.trim().toLowerCase();
  const rows = document.querySelectorAll(`#${{tableId}} tbody tr`);
  rows.forEach(row => {{
    if (row.querySelector(".empty")) return;
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(q) ? "" : "none";
  }});
}}

function filterCritTable() {{
  const q = document.getElementById("critSearch").value.trim().toLowerCase();
  const cat = document.getElementById("critCat").value;
  const rows = document.querySelectorAll("#critTable tbody tr");
  rows.forEach(row => {{
    if (row.querySelector(".empty")) return;
    const rowCat = row.getAttribute("data-cat") || "";
    const matchCat = (cat === "ALL" || rowCat === cat);
    const matchText = !q || row.textContent.toLowerCase().includes(q);
    row.style.display = (matchCat && matchText) ? "" : "none";
  }});
}}

function renderCatalog() {{
  const q = document.getElementById("catalogSearch").value.trim().toLowerCase();
  const tbody = document.getElementById("catalogBody");
  const status = document.getElementById("catalogStatus");
  const maxRender = 300;
  let matched = 0;
  let htmlRows = "";

  for (let i = 0; i < CATALOG_DATA.length; i++) {{
    const item = CATALOG_DATA[i];
    const relPath = item[0];
    const cat = item[1];
    const size = item[2];
    const date = item[3];

    if (!q || relPath.toLowerCase().includes(q) || cat.toLowerCase().includes(q) || date.toLowerCase().includes(q)) {{
      matched++;
      if (matched <= maxRender) {{
        htmlRows += `<tr>
          <td class="mono">${{escapeHtml(relPath)}}</td>
          <td><span class="tag tag-folder">${{escapeHtml(cat)}}</span></td>
          <td class="num">${{escapeHtml(size)}}</td>
          <td>${{escapeHtml(date)}}</td>
        </tr>`;
      }}
    }}
  }}

  if (matched === 0) {{
    tbody.innerHTML = '<tr><td colspan="4" class="empty">Nenhum arquivo correspondente encontrado no catálogo.</td></tr>';
    status.textContent = "0 resultados encontrados.";
  }} else {{
    tbody.innerHTML = htmlRows;
    if (matched > maxRender) {{
      status.textContent = `Exibindo os primeiros ${{maxRender}} de ${{matched.toLocaleString()}} arquivos encontrados. Digite mais termos para refinar.`;
    }} else {{
      status.textContent = `Exibindo ${{matched.toLocaleString()}} arquivo(s) encontrado(s).`;
    }}
  }}
}}

document.addEventListener("DOMContentLoaded", () => {{
  renderCatalog();
}});
</script>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_doc)

    return output_path
