import os
import re
import ssl
import smtplib
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.header import Header

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==== HTML отчет по статусу согласования (в стиле budget_html_report) ====
import base64
import os
from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt

# 1) Хелпер для кликабельных ссылок по заявке
SAP_URL_TEMPLATE = "https://sap-asus.sigma.sbrf.ru/sap/bc/ui2/flp2#ZSPL_REQ_TSO-display&//ZC_REQUEST_TSO('{num}')"

def add_request_links(df: pd.DataFrame) -> pd.DataFrame:
    """
    Возвращает копию df, где значения в колонке 'Заявка №' заменены на кликабельные ссылки.
    Открываются в новой вкладке.
    """
    d = df.copy()
    if 'Заявка №' not in d.columns:
        return d

    def mk_link(v):
        if pd.isna(v):
            return ''
        raw = str(v).strip()
        if not raw:
            return ''
        # Нормализуем номер: берём только цифры (убираем возможные пробелы/суффикс .0)
        digits = re.sub(r'\D', '', raw)
        num = digits if digits else raw
        url = SAP_URL_TEMPLATE.format(num=num)
        # В отображении оставим очищенный номер без лишних символов
        display = num
        return f'<a href="{url}" target="_blank" rel="noopener noreferrer">{display}</a>'

    d['Заявка №'] = d['Заявка №'].apply(mk_link)
    return d

def set_matplotlib_style():
    # стиль графиков в духе budget_html_report
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['axes.unicode_minus'] = False
    try:
        preferred = [
            'seaborn-v0_8-whitegrid',
            'seaborn-whitegrid',
            'seaborn-v0_8',
            'seaborn',
            'ggplot',
            'classic'
        ]
        for style in preferred:
            if style in plt.style.available:
                plt.style.use(style)
                break
    except Exception:
        pass

def _image_file_to_base64_uri(path: str) -> str:
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    return f"data:image/png;base64,{b64}"

def html_css():
    return """
<style>
:root {
  --bg: #ffffff;
  --card-bg: #f8fafc;
  --text: #1f2937;
  --muted: #6b7280;
  --primary: #0ea5e9;
  --success: #10b981;
  --warn: #f59e0b;
  --danger: #ef4444;
  --border: #e5e7eb;
}
html, body { background: var(--bg); color: var(--text); margin: 0; font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
.container { max-width: 1320px; margin: 0 auto; padding: 18px 18px 28px; }
h1 { font-size: 22px; margin: 12px 0 10px; }
h2 { font-size: 18px; margin: 18px 0 8px; }
h3 { font-size: 16px; margin: 0; } /* Уберем отступы у h3 внутри триггера */
.muted { color: var(--muted); }
.section { margin: 18px 0 26px; padding: 14px; background: #fff; border: 1px solid var(--border); border-radius: 12px; }
.section h2 { margin-top: 0; }
.grid-1 { display: grid; grid-template-columns: 1fr; gap: 14px; align-items: start; }
.img-box { background: #fff; border: 1px dashed var(--border); padding: 8px; border-radius: 8px; text-align:center; }

table { border-collapse: collapse; width: 100%; }
th, td { padding: 8px 10px; border-bottom: 1px solid var(--border); font-size: 13px; }
th { text-align: left; background: #fafafa; cursor: pointer; user-select: none; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
tr:hover { background: #f9fafb; }

.nav { display:flex; gap:8px; flex-wrap: wrap; margin: 6px 0 8px; }
.nav a { text-decoration: none; background: var(--card-bg); border:1px solid var(--border); color: var(--text); padding:6px 10px; border-radius:8px; font-size:13px; }
.nav a:hover { border-color: var(--primary); color: var(--primary); }
.footer { color: var(--muted); font-size: 12px; margin-top: 8px; }
hr.sep { border:0; border-top:1px solid var(--border); margin: 12px 0; }

.table-tools { display:flex; gap:8px; align-items:center; margin: 6px 0 10px; }
.table-tools input[type="text"] {
  padding: 6px 10px; border:1px solid var(--border); border-radius:8px; font-size:13px; width: 280px;
}
.sort-ind { color: var(--muted); font-size: 12px; margin-left: auto; }

/* === Стили для сворачиваемого списка === */
.collapsible { margin-top: 16px; }
.collapsible-trigger {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    user-select: none;
    padding: 10px 14px;
    background-color: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    transition: background-color 0.2s;
}
.collapsible-trigger:hover {
    background-color: #f1f5f9;
}
.collapsible-indicator {
    font-size: 22px;
    font-weight: 500;
    color: var(--primary);
    line-height: 1;
}
.collapsible-content {
    display: none;
    padding: 15px 12px 5px;
    border: 1px solid var(--border);
    border-top: none;
    border-bottom-left-radius: 8px;
    border-bottom-right-radius: 8px;
}
.collapsible.is-open .collapsible-content { display: block; }
.collapsible.is-open .collapsible-trigger {
    border-bottom-left-radius: 0;
    border-bottom-right-radius: 0;
}

/* === НОВЫЕ СТИЛИ: KPI карточки === */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
    margin-top: 10px;
}
.kpi-card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 18px;
}
.kpi-card .value {
    font-size: 24px;
    font-weight: 600;
    color: var(--primary);
}
.kpi-card .label {
    font-size: 13px;
    color: var(--muted);
    margin-top: 4px;
}

/* === НОВЫЕ СТИЛИ: Метки статусов в таблице === */
.status-badge {
    display: inline-block;
    padding: 3px 9px;
    border-radius: 12px;
    font-weight: 500;
    font-size: 11px;
    line-height: 1.2;
    white-space: nowrap;
}
.status-otso { background-color: #e0f2fe; color: #0284c7; } /* Синий */
.status-db { background-color: #fee2e2; color: #dc2626; }   /* Красный */
.status-cs { background-color: #ffedd5; color: #f97316; }   /* Оранжевый */
.status-stk { background-color: #f3e8ff; color: #9333ea; }   /* Фиолетовый */
.status-default { background-color: #e5e7eb; color: #4b5563; } /* Серый */
</style>
"""

def prepare_table_html(df, title, table_id, search_id):
    """
    Возвращает HTML-блок в виде сворачиваемого списка ("аккордеона"):
    заголовок с кнопкой "+", строка поиска и таблица.
    """
    # Делаем номера заявок кликабельными
    df_click = add_request_links(df)

    # Генерируем HTML таблицы (escape=False, чтобы ссылки не экранировались)
    table_html = df_click.to_html(index=False, border=0, justify='left', escape=False)
    table_html = table_html.replace("<table", f"<table id=\"{table_id}\" class=\"data-table\"")

    tools = f"""
<div class="table-tools">
  <input type="text" id="{search_id}" placeholder="Поиск по таблице..." />
  <div class="sort-ind">Клик по заголовку — сортировка</div>
</div>
"""
    # НОВАЯ СТРУКТУРА ДЛЯ СВОРАЧИВАЕМОГО СПИСКА
    return f"""
<div class="collapsible">
  <div class="collapsible-trigger">
    <h3>{title}</h3>
    <span class="collapsible-indicator">+</span>
  </div>
  <div class="collapsible-content">
    {tools}
    {table_html}
  </div>
</div>
"""

def _df_section_html(title: str, df_html: str, img_uri: str):
    return f"""
<div class="section">
  <h2>{title}</h2>
  <div class="grid-1">
    <div class="img-box"><img src="{img_uri}" alt="chart" style="max-width:100%;height:auto"/></div>
    {df_html}
  </div>
</div>
"""

def prepare_kpi_html(df_for_kpi: pd.DataFrame, df_source: pd.DataFrame):
    """Готовит HTML-блок с KPI-карточками."""

    # df_for_kpi - это уже отфильтрованный DataFrame без 'Согласовано'
    # df_source - это исходный DataFrame до фильтрации, для расчета сумм

    total_count = len(df_for_kpi)

    # Используем исходный df (dfAZ38, dfVSP99 и т.д.) для суммы, т.к. в make_result мы ее не трогали
    total_sum_val = df_source[df_source['Статус согласования'] != 'Согласовано']['Сумма с НДС'].sum()
    total_sum_str = format_amount_rub(total_sum_val)

    if not df_for_kpi.empty:
        oldest_date = df_for_kpi['Месяц выполнения'].min()
    else:
        oldest_date = '—'

    return f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="value">{total_count}</div>
    <div class="label">Заявок в работе</div>
  </div>
  <div class="kpi-card">
    <div class="value">{total_sum_str}</div>
    <div class="label">Общая сумма</div>
  </div>
  <div class="kpi-card">
    <div class="value">{oldest_date}</div>
    <div class="label">Самая "старая" заявка</div>
  </div>
</div>
"""

def save_status_html_report(
        result_az_mb, result_az_ca, result_vsp_mb, result_vsp_ca,
        source_df_az_mb, source_df_az_ca, source_df_vsp_mb, source_df_vsp_ca,
        img_az_mb_path, img_az_ca_path, img_vsp_mb_path, img_vsp_ca_path,
        output_html="status_report.html",
        report_title="Отчет по статусу согласования заявок на модернизацию"
):
    data_map = {
        'az_mb': {'title': 'АЗ МБ', 'df': result_az_mb, 'source_df': source_df_az_mb, 'img_path': img_az_mb_path, 'anchor': 'az_mb'},
        'az_ca': {'title': 'АЗ ЦА', 'df': result_az_ca, 'source_df': source_df_az_ca, 'img_path': img_az_ca_path, 'anchor': 'az_ca'},
        'vsp_mb': {'title': 'ВСП и УС МБ', 'df': result_vsp_mb, 'source_df': source_df_vsp_mb, 'img_path': img_vsp_mb_path, 'anchor': 'vsp_mb'},
        'vsp_ca': {'title': 'ЦА (К32 и пр.)', 'df': result_vsp_ca, 'source_df': source_df_vsp_ca, 'img_path': img_vsp_ca_path, 'anchor': 'vsp_ca'},
    }

    # Преобразуем PNG в base64 и готовим HTML
    for key, item in data_map.items():
        if not os.path.isfile(item['img_path']):
            raise FileNotFoundError(f"Не найден файл графика: {item['img_path']}")
        with open(item['img_path'], 'rb') as f:
            item['img_uri'] = "data:image/png;base64," + base64.b64encode(f.read()).decode('ascii')

        item['kpi_html'] = prepare_kpi_html(item['df'], item['source_df'])

        df_for_html = item['df'].copy()
        df_for_html['Сумма с НДС'] = df_for_html['Сумма с НДС'].apply(lambda x: format_amount_rub(x).replace(" руб.", ""))

        table_id = f"tbl_{key}"
        search_id = f"search_{key}"
        table_title = f"Заявки {item['title']} (без «Согласовано»)"
        item['table_html'] = prepare_table_html(df_for_html, table_title, table_id, search_id)

    html = []
    html.append("<!doctype html><html lang='ru'><head><meta charset='utf-8'>")
    html.append("<meta name='viewport' content='width=device-width, initial-scale=1'/>")
    html.append(f"<title>{report_title}</title>")
    html.append(html_css())
    html.append("</head><body>")
    html.append("<div class='container'>")
    html.append(f"<h1>{report_title}</h1>")

    html.append("<div class='nav'>")
    html.append("<a href='#az_mb'>АЗ МБ</a>")
    html.append("<a href='#az_ca'>АЗ ЦА</a>")
    html.append("<a href='#vsp_mb'>ВСП и УС МБ</a>")
    html.append("<a href='#vsp_ca'>ЦА (К32 и пр.)</a>")
    html.append("</div>")
    html.append("<hr class='sep'/>")

    for key, item in data_map.items():
        html.append(f"<a id='{item['anchor']}'></a>")
        html.append(f"""
<div class="section">
  <h2>{item['title']}: статус согласования</h2>
  {item['kpi_html']}
  <div class="grid-1">
    <div class="img-box"><img src="{item['img_uri']}" alt="chart_{key}" style="max-width:100%;height:auto"/></div>
    {item['table_html']}
  </div>
</div>
""")

    # --- ИСПРАВЛЕННЫЙ БЛОК SCRIPT ---
    html.append("""
<script>
(function(){
  // --- Логика для сворачиваемых списков ("аккордеон") ---
  function initCollapsibles() {
    document.querySelectorAll('.collapsible-trigger').forEach(trigger => {
      trigger.addEventListener('click', function() {
        const parent = this.closest('.collapsible');
        if (!parent) return;

        parent.classList.toggle('is-open');
        const indicator = this.querySelector('.collapsible-indicator');
        if (indicator) {
          indicator.textContent = parent.classList.contains('is-open') ? '−' : '+';
        }
      });
    });
  }

  // --- Функции для сортировки и поиска по таблице ---
  function parseNumberRu(txt) {
      if (!txt) return null;
      // Убираем пробелы, HTML-теги и заменяем запятую на точку
      const cleaned = txt.replace(/<[^>]*>/g, '').replace(/\\s/g, '').replace(',', '.').trim();
      const num = parseFloat(cleaned);
      return isNaN(num) ? null : num;
  }

  function detectColumnType(table, colIdx) {
      const rows = table.querySelectorAll('tbody tr');
      if (rows.length === 0) return 'string';
      // Проверяем несколько строк для надежности
      for (let i = 0; i < Math.min(rows.length, 5); i++) {
          const cell = rows[i].cells[colIdx];
          // Если в ячейке есть число, считаем колонку числовой
          if (cell && parseNumberRu(cell.textContent) !== null) {
              return 'number-ru';
          }
      }
      return 'string';
  }
  
  function sortTableByColumn(table, colIdx, asc = true) {
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const colType = detectColumnType(table, colIdx);

      const sortedRows = rows.sort((a, b) => {
          const cellA = a.cells[colIdx];
          const cellB = b.cells[colIdx];
          
          let valA = cellA ? cellA.textContent.trim() : '';
          let valB = cellB ? cellB.textContent.trim() : '';

          if (colType === 'number-ru') {
              valA = parseNumberRu(valA);
              valB = parseNumberRu(valB);
              // Пустые/нечисловые значения отправляем в конец
              if (valA === null) return 1;
              if (valB === null) return -1;
          }

          if (valA < valB) {
              return asc ? -1 : 1;
          }
          if (valA > valB) {
              return asc ? 1 : -1;
          }
          return 0;
      });

      // Удаляем старые строки и вставляем отсортированные
      tbody.innerHTML = '';
      sortedRows.forEach(row => tbody.appendChild(row));
  }

  function bindSorting(table) {
      const headers = table.querySelectorAll('thead th');
      headers.forEach((header, index) => {
          header.addEventListener('click', () => {
              const currentAsc = header.dataset.sortDir !== 'desc';
              const newAsc = !currentAsc;

              // Сбрасываем индикаторы на всех заголовках
              headers.forEach(h => {
                  h.dataset.sortDir = '';
                  h.innerHTML = h.innerHTML.replace(/ [▲▼]$/, '');
              });

              // Устанавливаем направление и индикатор для текущего
              header.dataset.sortDir = newAsc ? 'asc' : 'desc';
              header.innerHTML += newAsc ? ' ▲' : ' ▼';
              
              sortTableByColumn(table, index, newAsc);
          });
      });
  }

  function bindSearch(input, table) {
      if (!input || !table) return;
      const tbody = table.querySelector('tbody');
      if (!tbody) return;

      input.addEventListener('input', function() {
          const query = this.value.trim().toLowerCase();
          const rows = tbody.querySelectorAll('tr');
          rows.forEach(row => {
              const text = row.textContent.toLowerCase();
              row.style.display = text.includes(query) ? '' : 'none';
          });
      });
  }
  
  function initTable(tableId, searchId) {
    const table = document.getElementById(tableId);
    const search = document.getElementById(searchId);
    if (!table) return;
    
    // Включаем сортировку
    bindSorting(table); 
    
    if (search) {
      bindSearch(search, table);
    }
  }

  // --- Инициализация всего при загрузке страницы ---
  document.addEventListener('DOMContentLoaded', function(){
    initTable('tbl_az_mb', 'search_az_mb');
    initTable('tbl_az_ca', 'search_az_ca');
    initTable('tbl_vsp_mb', 'search_vsp_mb');
    initTable('tbl_vsp_ca', 'search_vsp_ca');
    
    initCollapsibles();
  });
})();
</script>
""")

    html.append("<div class='footer'>Сформировано автоматически</div>")
    html.append("</div></body></html>")

    with open(output_html, "w", encoding="utf-8") as f:
        f.write("".join(html))

    print(f"HTML-отчет сохранен: {os.path.abspath(output_html)}")
    return os.path.abspath(output_html)

# ---------------------- Configuration ----------------------
EXCEL_PATH='Заявки.xlsx'
SMTP_HOST='MTA.SIGMA.SBRF.RU'
SMTP_PORT=25
SMTP_USER='21204476'
SMTP_PASS='syurikZAY1502++'
MAIL_FROM='yaleksezaytsev@sberbank.ru'
MAIL_TO='yaleksezaytsev@sberbank.ru'
SUBJECT='Отчет 2 по статусу согласования заявок на модернизацию'

# ---------------------- Helpers ----------------------
def read_excel(path: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(path, engine='openpyxl')
        print("Excel loaded.")
        return df
    except Exception as e:
        raise RuntimeError(f"Ошибка чтения Excel: {e}")

def vectorized_status(df: pd.DataFrame) -> pd.Series:
    st = df.get('Статус')
    act = df.get('Статус акта')

    conds = [
        st.isin(['На согласовании', 'Возвращена на согласование']) | st.eq('На утверждении ВК'),
        act.eq('Согласовано'),
        act.eq('На согласовании ЦС'),
        act.eq('На согласовании ТБ'),
        st.isin([
            'На доработке из Акта',
            'Подтверждение объёмов',
            'Корректировка объёмов',
            'Возвращена на доработку'
        ]) | act.isin(['Проект', 'Возвращен на доработку'])
    ]
    choices = ['ОТСО', 'Согласовано', 'ЦС', 'ДБ', 'СТК']
    return np.select(conds, choices, default='СТК')

def cleanup_money(series: pd.Series) -> pd.Series:
    # Convert "1 234 567,89" -> float
    s = series.astype(str).str.replace(r'\s+', '', regex=True).str.replace(',', '.')
    return pd.to_numeric(s, errors='coerce').fillna(0.0)

def month_period_str(dt_series: pd.Series) -> pd.Series:
    return pd.to_datetime(dt_series, errors='coerce').dt.to_period('M').astype(str)

def format_amount_rub(value: float) -> str:
    """Форматирует число в денежный формат '1 234 567,89 руб.'"""
    if pd.isna(value) or value is None:
        return "0,00 руб."
    # Форматируем с пробелами как разделителями тысяч и запятой для копеек
    s = f"{value:,.2f}"
    # Заменяем запятые на пробелы, а точку на запятую
    formatted_s = s.replace(",", " ").replace(".", ",")
    return f"{formatted_s} руб."

def plot_stacked_by_month(df: pd.DataFrame, title: str, filename: str, color_map: dict) -> str:
    grouped = df.groupby(['Месяц выполнения', 'Статус согласования']).size().unstack(fill_value=0)
    colors = [color_map.get(col, 'gray') for col in grouped.columns]

    ax = grouped.plot(kind='bar', stacked=True, figsize=(12, 6), color=colors)

    # annotate non-zero bars
    for container in ax.containers:
        for bar in container:
            value = bar.get_height()
            if value > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + value / 2,
                    f'{int(value)}',
                    ha='center', va='center', fontsize=10, color='white'
                )

    plt.title(title, fontsize=16)
    plt.xlabel('Месяц выполнения', fontsize=12)
    plt.ylabel('Количество заявок', fontsize=12)
    plt.legend(title='Статус акта', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)

    # Добавление горизонтальной пунктирной серой линии при значении 843,
    # но только если есть значения больше 843
    max_value = grouped.values.max()
    if max_value > 843:
        ax.axhline(y=843, color='gray', linestyle='--', linewidth=1, label='Опорное значение')

    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    return filename

def send_dataframe_via_email(df1: pd.DataFrame, df2: pd.DataFrame, img1_path: str, img2_path: str) -> None:
    # SMTP/почта
    SMTP_HOST = "MTA.SIGMA.SBRF.RU"
    SMTP_PORT = 25
    MAIL_FROM = "yaleksezaytsev@sberbank.ru"
    RECIPIENTS = ["yaleksezaytsev@sberbank.ru"]
    SUBJECT = "Отчет по статусу согласования заявок на модернизацию"

    LOGIN_USER = os.environ.get("SMTP_USER", "21204476")
    LOGIN_PASSWORD = os.environ.get("SMTP_PASSWORD", "syurikZAY1502++")  # укажите пароль

    # HTML-стили и таблицы
    style = """
    <style type="text/css">
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    tr:nth-child(even){background-color: #f2f2f2;}
    tr:hover {background-color: #ddd;}
    th { padding-top: 12px; padding-bottom: 12px; text-align: left; background-color: #04AA6D; color: white; }
    </style>
    """
    df1_html = style + "<h2>Заявки МБ</h2>" + df1.to_html(index=False, justify='left', border=0)
    df2_html = style + "<h2>Заявки ЦА</h2>" + df2.to_html(index=False, justify='left', border=0)

    html_body = f"""
    <html>
    <body>
      <p>Добрый день!</p>
      <p>Ниже — статус согласования заявок.</p>
      <img src="cid:plot_image1"><br>
      <img src="cid:plot_image2"><br>
      {df1_html}
      {df2_html}
    </body>
    </html>
    """

    # Письмо: multipart/related + alternative
    outer = MIMEMultipart('related')
    outer['Subject'] = str(Header(SUBJECT, 'utf-8'))
    outer['From'] = MAIL_FROM
    outer['To'] = ", ".join(RECIPIENTS)

    alt = MIMEMultipart('alternative')
    alt.attach(MIMEText("Отчет по статусу согласования заявок (см. HTML-версию).", 'plain', 'utf-8'))
    alt.attach(MIMEText(html_body, 'html', 'utf-8'))
    outer.attach(alt)

    # Встроенные изображения (CID)
    for cid, path in [('plot_image1', img1_path), ('plot_image2', img2_path)]:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Файл изображения не найден: {path}")
        with open(path, 'rb') as f:
            img = MIMEImage(f.read(), name=os.path.basename(path))
            img.add_header('Content-ID', f'<{cid}>')
            img.add_header('Content-Disposition', 'inline', filename=os.path.basename(path))
            outer.attach(img)

    # НЕБЕЗОПАСНЫЙ TLS-контекст: без проверки сертификата
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Отправка
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(LOGIN_USER, LOGIN_PASSWORD)
            server.sendmail(MAIL_FROM, RECIPIENTS, outer.as_string())
            print("Email отправлен (TLS без проверки сертификата).")
    except Exception as e:
        print(f"Ошибка отправки Email: {e}")
        raise

def save_fio_list(df: pd.DataFrame, fio_pattern: str, filename: str):
    """
    Сохраняет уникальные ФИО заказчиков в файл, помечая,
    кто попадает под заданный паттерн.
    """
    if 'ФИО заказчика' not in df.columns:
        print("В данных отсутствует столбец 'ФИО заказчика'. Файл не будет создан.")
        return

    # Получаем отсортированный список уникальных не-пустых ФИО
    unique_fios = sorted(df['ФИО заказчика'].dropna().unique())

    lines_to_write = []
    for fio in unique_fios:
        # Проверяем каждое ФИО на соответствие паттерну
        # re.search удобен для таких проверок с ignore case
        if re.search(fio_pattern, str(fio), re.IGNORECASE):
            marker = '[АЗ]'  # Попадает в маску (Административные Здания)
        else:
            marker = '[ВСП]' # Не попадает в маску (Вне Списка)

        lines_to_write.append(f"{fio} {marker}\n")

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Добавим заголовок для понятности
            f.write(f"# Список уникальных ФИО заказчиков ({date.today()})\n")
            f.write("# [АЗ] - ФИО соответствует маске отбора\n")
            f.write("# [ВСП] - ФИО не соответствует маске (остальные)\n")
            f.write("-" * 40 + "\n")
            f.writelines(lines_to_write)
        print(f"Список заказчиков сохранен в файл: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"Ошибка при сохранении файла со списком заказчиков: {e}")

# ---------------------- НОВАЯ ФУНКЦИЯ ДЛЯ РВР ОТЧЕТА ----------------------
def process_rvr_data(df: pd.DataFrame, fio_pattern: str):
    """
    Обрабатывает данные для отчета по РВР (ремонтно-восстановительные работы)
    """
    # Фильтрация для РВР
    #dfRVR = df[~df['Вид работ'].isin(['Модернизация', 'ПТО', 'Внеплановое ТО', 'Проектирование', 'Установка новых систем ТСО'])]
    #dfRVR = dfRVR[~dfRVR['Статус'].isin(['Отозвана ДБ', 'Отозвана ВК'])]

    dfRVR = df[
        (~df['Вид работ'].isin(['Модернизация', 'ПТО', 'Внеплановое ТО', 'Проектирование', 'Установка новых систем ТСО'])) &
        (~df['Статус'].isin(['Отозвана ДБ', 'Отозвана ВК'])) &
        (df['В лимите'].astype(str).str.strip().isin(['-', 'Московский банк', 'ЦА Сбербанк']))
        ]

    # Исключаем гарантийные заявки
    if 'Гарантийная заявка' in dfRVR.columns:
        dfRVR = dfRVR[dfRVR['Гарантийная заявка'] != 1]

    # Сохраняем список заказчиков для РВР
    save_fio_list(dfRVR, fio_pattern, 'Заказчики_RVR.mb')
    dfRVR.to_excel('RVR.xlsx', index=False, engine='openpyxl')
    print(f"Данные по РВР сохранены в файл: {os.path.abspath('RVR.xlsx')}")


    # Разделение по ФИО заказчика
    fio_mask = dfRVR['ФИО заказчика'].str.contains(fio_pattern, na=False, case=False)
    dfAZ = dfRVR[fio_mask].copy()
    dfVSP = dfRVR[~fio_mask].copy()

    # Обработка дат и статусов для АЗ
    dfAZ.loc[dfAZ['Статус'] == 'Возвращена на доработку', 'Фактическая дата выполнения (UTC)'] = pd.Timestamp(date.today())
    dfAZ['Фактическая дата выполнения (UTC)'] = pd.to_datetime(dfAZ['Фактическая дата выполнения (UTC)'], errors='coerce')
    dfAZ = dfAZ.dropna(subset=['Фактическая дата выполнения (UTC)'])
    cutoff = pd.Timestamp.today().normalize() - pd.DateOffset(months=6)
    dfAZ = dfAZ[dfAZ['Фактическая дата выполнения (UTC)'] > cutoff]
    dfAZ['Статус согласования'] = vectorized_status(dfAZ)

    # Обработка дат и статусов для ВСП
    dfVSP.loc[dfVSP['Статус'] == 'Возвращена на доработку', 'Фактическая дата выполнения (UTC)'] = pd.Timestamp(date.today())
    dfVSP['Фактическая дата выполнения (UTC)'] = pd.to_datetime(dfVSP['Фактическая дата выполнения (UTC)'], errors='coerce')
    dfVSP = dfVSP.dropna(subset=['Фактическая дата выполнения (UTC)'])
    dfVSP = dfVSP[dfVSP['Фактическая дата выполнения (UTC)'] > cutoff]
    dfVSP['Статус согласования'] = vectorized_status(dfVSP)

    # Разделение по ТБ
    dfAZ99 = dfAZ[dfAZ['Территориальный банк'].astype(str).str.contains('99', na=False, case=False)].copy()
    dfAZ38 = dfAZ[dfAZ['Территориальный банк'].astype(str).str.contains('38', na=False, case=False)].copy()
    dfVSP99 = dfVSP[dfVSP['Территориальный банк'].astype(str).str.contains('99', na=False, case=False)].copy()
    dfVSP38 = dfVSP[dfVSP['Территориальный банк'].astype(str).str.contains('38', na=False, case=False)].copy()

    # Month period
    for dfx in (dfAZ99, dfAZ38, dfVSP99, dfVSP38):
        dfx['Месяц выполнения'] = month_period_str(dfx['Фактическая дата выполнения (UTC)'])

    # Apply renames for chart
    dfAZ38['Статус согласования'] = dfAZ38['Статус согласования'].replace({
        'ДБ': 'Семенова',
        'ОТСО': 'Войнов'
    })
    dfAZ99['Статус согласования'] = dfAZ99['Статус согласования'].replace({
        'ДБ': 'Семенова',
        'ОТСО': 'Войнов'
    })
    dfVSP38['Статус согласования'] = dfVSP38['Статус согласования'].replace({
        'ДБ': 'Семенова',
        'ОТСО': 'Внутренний клиент'
    })
    dfVSP99['Статус согласования'] = dfVSP99['Статус согласования'].replace({
        'ОТСО': 'УКБ'
    })

    # Numeric cleanup
    for dfx in (dfAZ99, dfAZ38, dfVSP99, dfVSP38):
        dfx['Сумма с НДС'] = cleanup_money(dfx['Сумма с НДС'])

    return dfAZ99, dfAZ38, dfVSP99, dfVSP38

# ---------------------- Main pipeline ----------------------
def main():
    # Включаем стиль графиков до построения PNG
    set_matplotlib_style()

    df = read_excel(EXCEL_PATH)

    # Базовые фильтры для модернизации
    df_modern = df[~df['Вид работ'].isin(['РВР', 'ПТО', 'Внеплановое ТО'])]
    df_modern = df_modern[~df_modern['Статус'].isin(['Отозвана ДБ', 'Отозвана ВК'])]

    names = [
        # Старые
        'Зайцев', 'Петров Андрей', 'Войнов', 'Кириллов', 'Леонид Николаевич', 'Шомко', 'Седун',
        'Андрей Константинович', 'Губин', 'Михаил Леонидович', 'Михаил Сергеевич',
        'Крашенинников', 'Фролов', 'Уткин', 'Станислав Павлович', 'Олег Юрьевич',
        'Дмитрий Андреевич', 'Алексей Валентинович',
        # Новые
        'Марина Васильевна Л', 'Алексей Валентинович Ф', 'Дмитрий Анатольевич К',
        'Василий Сергеевич Т', 'Дмитрий Андреевич Ш', 'Иван Юрьевич Х',
        'Михаил Леонидович У', 'Алексей Владимирович О', 'Войнов Леонид Николаевич',
        'Олег Александрович К', 'Алексей Анатольевич М'
    ]

    # Сортируем по убыванию длины и объединяем через |
    # Это гарантирует, что "Войнов Леонид Николаевич" найдется раньше, чем просто "Войнов"
    fio_pattern = '|'.join(sorted(names, key=len, reverse=True))

    # Обработка данных для модернизации
    save_fio_list(df_modern, fio_pattern, 'Заказчики.mb')

    fio_mask = df_modern['ФИО заказчика'].str.contains(fio_pattern, na=False, case=False)
    dfAZ = df_modern[fio_mask].copy()
    dfVSP = df_modern[~fio_mask].copy()

    # --- Обработка dfAZ ---
    dfAZ.loc[dfAZ['Статус'] == 'Возвращена на доработку', 'Фактическая дата выполнения (UTC)'] = pd.Timestamp(date.today())
    dfAZ['Фактическая дата выполнения (UTC)'] = pd.to_datetime(dfAZ['Фактическая дата выполнения (UTC)'], errors='coerce')
    dfAZ = dfAZ.dropna(subset=['Фактическая дата выполнения (UTC)'])
    cutoff = pd.Timestamp.today().normalize() - pd.DateOffset(months=6)
    dfAZ = dfAZ[dfAZ['Фактическая дата выполнения (UTC)'] > cutoff]
    dfAZ['Статус согласования'] = vectorized_status(dfAZ)

    # --- Обработка dfVSP ---
    dfVSP.loc[dfVSP['Статус'] == 'Возвращена на доработку', 'Фактическая дата выполнения (UTC)'] = pd.Timestamp(date.today())
    dfVSP['Фактическая дата выполнения (UTC)'] = pd.to_datetime(dfVSP['Фактическая дата выполнения (UTC)'], errors='coerce')
    dfVSP = dfVSP.dropna(subset=['Фактическая дата выполнения (UTC)'])
    dfVSP = dfVSP[dfVSP['Фактическая дата выполнения (UTC)'] > cutoff]
    dfVSP['Статус согласования'] = vectorized_status(dfVSP)

    # --- Разделение по ТБ ---
    dfAZ99 = dfAZ[dfAZ['Территориальный банк'].astype(str).str.contains('99', na=False, case=False)].copy()
    dfAZ38 = dfAZ[dfAZ['Территориальный банк'].astype(str).str.contains('38', na=False, case=False)].copy()
    dfVSP99 = dfVSP[dfVSP['Территориальный банк'].astype(str).str.contains('99', na=False, case=False)].copy()
    dfVSP38 = dfVSP[dfVSP['Территориальный банк'].astype(str).str.contains('38', na=False, case=False)].copy()

    # Month period
    for dfx in (dfAZ99, dfAZ38, dfVSP99, dfVSP38):
        dfx['Месяц выполнения'] = month_period_str(dfx['Фактическая дата выполнения (UTC)'])

    # Apply requested renames for MB chart
    dfAZ38['Статус согласования'] = dfAZ38['Статус согласования'].replace({
        'ДБ': 'Семенова',
        'ОТСО': 'Войнов'
    })
    dfAZ99['Статус согласования'] = dfAZ99['Статус согласования'].replace({
        'ОТСО': 'Войнов',
        'ДБ': 'Семенова'
    })
    dfVSP38['Статус согласования'] = dfVSP38['Статус согласования'].replace({
        'ДБ': 'Семенова',
        'ОТСО': 'Внутренний клиент'
    })
    dfVSP99['Статус согласования'] = dfVSP99['Статус согласования'].replace({
        'ОТСО': 'УКБ'
    })
    color_map = {
        'Согласовано': 'lightgreen',
        'ОТСО': 'skyblue',
        'Войнов': 'skyblue',
        'ЦС': 'orange',
        'СТК': 'plum',
        'Семенова': 'lightcoral',
        'Никитичев': 'skyblue',
        'ДБ': 'lightcoral',
        'Алферов': 'lightcoral',
        'УКБ': 'skyblue'
    }

    # Plots для модернизации
    img_az_ca = plot_stacked_by_month(
        dfAZ99,
        'Статус согласования заявок на модернизацию административных зданий ЦА-МБ',
        'plot_az_ca.png',
        color_map
    )
    img_az_mb = plot_stacked_by_month(
        dfAZ38,
        'Статус согласования заявок на модернизацию административных зданий МБ',
        'plot_az_mb.png',
        color_map
    )
    img_vsp_ca = plot_stacked_by_month(
        dfVSP99,
        'Статус согласования заявок на модернизацию административных зданий ЦА (К32 и др.)',
        'plot_vsp_ca.png',
        color_map
    )
    img_vsp_mb = plot_stacked_by_month(
        dfVSP38,
        'Статус согласования заявок на модернизацию ВСП и УС МБ',
        'plot_vsp_mb.png',
        color_map
    )

    # Numeric cleanup
    for dfx in (dfAZ99, dfAZ38, dfVSP99, dfVSP38):
        dfx['Сумма с НДС'] = cleanup_money(dfx['Сумма с НДС'])

    start_date = pd.Timestamp('2026-01-01')
    sum_az_99 = dfAZ99[dfAZ99['Фактическая дата выполнения (UTC)'] >= start_date]['Сумма с НДС'].sum()
    sum_az_38 = dfAZ38[dfAZ38['Фактическая дата выполнения (UTC)'] >= start_date]['Сумма с НДС'].sum()
    sum_vsp_99 = dfVSP99[dfVSP99['Фактическая дата выполнения (UTC)'] >= start_date]['Сумма с НДС'].sum()
    sum_vsp_38 = dfVSP38[dfVSP38['Фактическая дата выполнения (UTC)'] >= start_date]['Сумма с НДС'].sum()

    print(f"Сумма для АЗ ЦА (99) с 2026-01-01: {format_amount_rub(sum_az_99)} руб.")
    print(f"Сумма для АЗ МБ (38) с 2026-01-01: {format_amount_rub(sum_az_38)} руб.")
    print(f"Сумма для ВСП ЦА (99) с 2026-01-01: {format_amount_rub(sum_vsp_99)} руб.")
    print(f"Сумма для ВСП МБ (38) с 2026-01-01: {format_amount_rub(sum_vsp_38)} руб.")

    # Tables for email (exclude 'Согласовано')
    def make_result(dfx: pd.DataFrame) -> pd.DataFrame:
        cols = ['Месяц выполнения', 'Статус согласования', 'Заявка №', 'Сумма с НДС', 'Статус', 'Статус акта']

        # Делаем копию, чтобы избежать SettingWithCopyWarning
        df_filtered = dfx[dfx['Статус согласования'] != 'Согласовано'].copy()

        out = df_filtered[cols]
        out = out.sort_values(['Месяц выполнения', 'Статус согласования', 'Заявка №'])

        # Добавляем HTML-разметку для статусов
        status_map_classes = {
            'ОТСО': 'status-otso', 'Войнов': 'status-otso', 'Никитичев': 'status-otso',
            'ДБ': 'status-db', 'Семенова': 'status-db',
            'ЦС': 'status-cs',
            'СТК': 'status-stk',
        }

        def format_status_badge(s):
            class_name = status_map_classes.get(s, 'status-default')
            return f'<span class="status-badge {class_name}">{s}</span>'

        # Применяем форматирование к колонке
        out['Статус согласования'] = out['Статус согласования'].apply(format_status_badge)

        # Сумма с НДС остается числом для дальнейших расчетов
        return out

    # Таблицы для отчета по модернизации
    result_az_mb = make_result(dfAZ38)
    result_az_ca = make_result(dfAZ99)
    result_vsp_mb = make_result(dfVSP38)
    result_vsp_ca = make_result(dfVSP99)

    # ==== СОХРАНЕНИЕ ОТЧЕТА ПО МОДЕРНИЗАЦИИ ====
    save_status_html_report(
        result_az_mb=result_az_mb,
        result_az_ca=result_az_ca,
        result_vsp_mb=result_vsp_mb,
        result_vsp_ca=result_vsp_ca,
        # Передаем исходные датафреймы для расчета KPI
        source_df_az_mb=dfAZ38,
        source_df_az_ca=dfAZ99,
        source_df_vsp_mb=dfVSP38,
        source_df_vsp_ca=dfVSP99,
        # Пути к изображениям
        img_az_mb_path=img_az_mb,
        img_az_ca_path=img_az_ca,
        img_vsp_mb_path=img_vsp_mb,
        img_vsp_ca_path=img_vsp_ca,
        output_html="status_report.html",
        report_title="Отчет по статусу согласования заявок на модернизацию"
    )

    # ==== СОЗДАНИЕ ОТЧЕТА ПО РВР ====
    print("\n" + "="*60)
    print("ФОРМИРОВАНИЕ ОТЧЕТА ПО РВР (РЕМОНТНО-ВОССТАНОВИТЕЛЬНЫЕ РАБОТЫ)")
    print("="*60)

    # Обрабатываем данные для РВР
    dfAZ99_rvr, dfAZ38_rvr, dfVSP99_rvr, dfVSP38_rvr = process_rvr_data(df, fio_pattern)

    # Графики для РВР
    img_az_ca_rvr = plot_stacked_by_month(
        dfAZ99_rvr,
        'Статус согласования заявок на РВР административных зданий ЦА-МБ',
        'plot_az_ca_RVR.png',
        color_map
    )
    img_az_mb_rvr = plot_stacked_by_month(
        dfAZ38_rvr,
        'Статус согласования заявок на РВР административных зданий МБ',
        'plot_az_mb_RVR.png',
        color_map
    )
    img_vsp_ca_rvr = plot_stacked_by_month(
        dfVSP99_rvr,
        'Статус согласования заявок на РВР административных зданий ЦА (К32 и др.)',
        'plot_vsp_ca_RVR.png',
        color_map
    )
    img_vsp_mb_rvr = plot_stacked_by_month(
        dfVSP38_rvr,
        'Статус согласования заявок на РВР ВСП и УС МБ',
        'plot_vsp_mb_RVR.png',
        color_map
    )

    # Таблицы для отчета по РВР
    result_az_mb_rvr = make_result(dfAZ38_rvr)
    result_az_ca_rvr = make_result(dfAZ99_rvr)
    result_vsp_mb_rvr = make_result(dfVSP38_rvr)
    result_vsp_ca_rvr = make_result(dfVSP99_rvr)

    # Сохранение отчета по РВР
    save_status_html_report(
        result_az_mb=result_az_mb_rvr,
        result_az_ca=result_az_ca_rvr,
        result_vsp_mb=result_vsp_mb_rvr,
        result_vsp_ca=result_vsp_ca_rvr,
        source_df_az_mb=dfAZ38_rvr,
        source_df_az_ca=dfAZ99_rvr,
        source_df_vsp_mb=dfVSP38_rvr,
        source_df_vsp_ca=dfVSP99_rvr,
        img_az_mb_path=img_az_mb_rvr,
        img_az_ca_path=img_az_ca_rvr,
        img_vsp_mb_path=img_vsp_mb_rvr,
        img_vsp_ca_path=img_vsp_ca_rvr,
        output_html="status_report_RVR.html",
        report_title="Отчет по статусу согласования заявок на ремонтно-восстановительные работы (РВР)"
    )

if __name__ == '__main__':
    main()