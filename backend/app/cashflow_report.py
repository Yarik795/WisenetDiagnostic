"""Генерация отчёта «Статус оплаты» из Excel-выгрузки заявок."""

from __future__ import annotations

import base64
import json
import re
import shutil
from datetime import date, datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DATA_DIR = PROJECT_ROOT / "inputData"
UPLOADS_DIR = PROJECT_ROOT / "data" / "uploads"
REQUESTS_NAME_MARKER = "заявки"
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
REQUESTS_FILENAME = "requests.xlsx"
REPORT_ARTIFACT = REPORTS_DIR / "cashflow_report.json"

SAP_URL_TEMPLATE = (
    "https://sap-asus.sigma.sbrf.ru/sap/bc/ui2/flp2#ZSPL_REQ_TSO-display"
    "&//ZC_REQUEST_TSO('{num}')"
)

REQUIRED_COLUMNS = (
    "Вид работ",
    "Статус",
    "Статус акта",
    "ФИО заказчика",
    "Фактическая дата выполнения (UTC)",
    "Территориальный банк",
    "Сумма с НДС",
    "Заявка №",
)

DRUG_COLUMN = "№ заявки ДРУГ"

RVR_EXTRA_COLUMNS = ("В лимите",)

FIO_NAMES = [
    "Зайцев",
    "Петров Андрей",
    "Войнов",
    "Кириллов",
    "Леонид Николаевич",
    "Шомко",
    "Седун",
    "Андрей Константинович",
    "Губин",
    "Михаил Леонидович",
    "Михаил Сергеевич",
    "Крашенинников",
    "Фролов",
    "Уткин",
    "Станислав Павлович",
    "Олег Юрьевич",
    "Дмитрий Андреевич",
    "Алексей Валентинович",
    "Марина Васильевна Л",
    "Алексей Валентинович Ф",
    "Дмитрий Анатольевич К",
    "Василий Сергеевич Т",
    "Дмитрий Андреевич Ш",
    "Иван Юрьевич Х",
    "Михаил Леонидович У",
    "Алексей Владимирович О",
    "Войнов Леонид Николаевич",
    "Олег Александрович К",
    "Алексей Анатольевич М",
]

COLOR_MAP = {
    "Согласовано": "#34d399",
    "ОТСО": "#38bdf8",
    "Войнов": "#38bdf8",
    "ЦС": "#fb923c",
    "СТК": "#c084fc",
    "Семенова": "#f87171",
    "Никитичев": "#38bdf8",
    "ДБ": "#f87171",
    "Алферов": "#f87171",
    "УКБ": "#38bdf8",
    "Внутренний клиент": "#38bdf8",
}

STATUS_BADGE_CLASSES = {
    "ОТСО": "status-otso",
    "Войнов": "status-otso",
    "Никитичев": "status-otso",
    "УКБ": "status-otso",
    "Внутренний клиент": "status-otso",
    "ДБ": "status-db",
    "Семенова": "status-db",
    "ЦС": "status-cs",
    "СТК": "status-stk",
}

SECTION_SPECS = (
    ("az_mb", "АЗ МБ"),
    ("az_ca", "АЗ ЦА"),
    ("vsp_mb", "ВСП и УС МБ"),
    ("vsp_ca", "ЦА (К32 и пр.)"),
)

ProgressCallback = Callable[[str, int], None]


def requests_file_path() -> Path:
    return UPLOADS_DIR / REQUESTS_FILENAME


def input_data_dir() -> Path:
    return INPUT_DATA_DIR


def find_latest_requests_source_file(
    directory: Path | None = None,
) -> Path:
    """Ищет .xlsx с «Заявки» в имени и возвращает файл с самой поздней датой изменения."""
    from .data_sources import REQUESTS_SOURCE, find_latest_source_file

    return find_latest_source_file(REQUESTS_SOURCE, directory)


def requests_source_file_info(
    directory: Path | None = None,
) -> Optional[dict[str, Any]]:
    try:
        path = find_latest_requests_source_file(directory)
    except FileNotFoundError:
        return None
    stat = path.stat()
    return {
        "path": path,
        "filename": path.name,
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
    }


def import_requests_from_source(source: Path, dest: Path | None = None) -> tuple[Path, int]:
    """Копирует найденный исходный файл в централизованное хранилище."""
    target = dest or requests_file_path()
    ensure_storage_dirs()
    shutil.copy2(source, target)
    return target, target.stat().st_size


def ensure_storage_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def format_amount_rub(value: float) -> str:
    if pd.isna(value) or value is None:
        return "0,00 руб."
    s = f"{value:,.2f}"
    return f"{s.replace(',', ' ').replace('.', ',')} руб."


def _set_matplotlib_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.unicode_minus": False,
            "figure.facecolor": "#1a1d24",
            "axes.facecolor": "#1a1d24",
            "axes.edgecolor": "#3d4450",
            "axes.labelcolor": "#e8eaed",
            "text.color": "#e8eaed",
            "xtick.color": "#9aa0a6",
            "ytick.color": "#9aa0a6",
            "grid.color": "#2d323c",
            "legend.facecolor": "#1a1d24",
            "legend.edgecolor": "#3d4450",
        }
    )
    for style in (
        "seaborn-v0_8-darkgrid",
        "seaborn-darkgrid",
        "ggplot",
        "classic",
    ):
        if style in plt.style.available:
            plt.style.use(style)
            break


def _validate_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(
            "В файле отсутствуют обязательные столбцы: " + ", ".join(missing)
        )
    if df.empty:
        raise ValueError("Файл не содержит строк с данными")


def read_excel(path: Path) -> pd.DataFrame:
    try:
        return pd.read_excel(path, engine="openpyxl")
    except Exception as exc:
        raise ValueError(f"Ошибка чтения Excel: {exc}") from exc


def vectorized_status(df: pd.DataFrame) -> pd.Series:
    st = df.get("Статус")
    act = df.get("Статус акта")
    conds = [
        st.isin(["На согласовании", "Возвращена на согласование"])
        | st.eq("На утверждении ВК"),
        act.eq("Согласовано"),
        act.eq("На согласовании ЦС"),
        act.eq("На согласовании ТБ"),
        st.isin(
            [
                "На доработке из Акта",
                "Подтверждение объёмов",
                "Корректировка объёмов",
                "Возвращена на доработку",
            ]
        )
        | act.isin(["Проект", "Возвращен на доработку"]),
    ]
    choices = ["ОТСО", "Согласовано", "ЦС", "ДБ", "СТК"]
    return pd.Series(np.select(conds, choices, default="СТК"), index=df.index)


def cleanup_money(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.replace(r"\s+", "", regex=True).str.replace(",", ".")
    return pd.to_numeric(s, errors="coerce").fillna(0.0)


def month_period_str(dt_series: pd.Series) -> pd.Series:
    return pd.to_datetime(dt_series, errors="coerce").dt.to_period("M").astype(str)


def fio_pattern() -> str:
    return "|".join(sorted(FIO_NAMES, key=len, reverse=True))


def _apply_date_status_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.loc[
        out["Статус"] == "Возвращена на доработку",
        "Фактическая дата выполнения (UTC)",
    ] = pd.Timestamp(date.today())
    out["Фактическая дата выполнения (UTC)"] = pd.to_datetime(
        out["Фактическая дата выполнения (UTC)"], errors="coerce"
    )
    out = out.dropna(subset=["Фактическая дата выполнения (UTC)"])
    cutoff = pd.Timestamp.today().normalize() - pd.DateOffset(months=6)
    out = out[out["Фактическая дата выполнения (UTC)"] > cutoff]
    out["Статус согласования"] = vectorized_status(out)
    return out


def _apply_naumen_cost_fallback(
    dfx: pd.DataFrame,
    naumen_cost_map: Optional[dict[str, float]],
) -> None:
    if not naumen_cost_map or DRUG_COLUMN not in dfx.columns:
        return
    zero = dfx["Сумма с НДС"] == 0
    if not zero.any():
        return
    keys = dfx.loc[zero, DRUG_COLUMN].astype(str).str.strip()
    dfx.loc[zero, "Сумма с НДС"] = keys.map(naumen_cost_map).fillna(0.0).values


def _split_by_fio_tb(
    df: pd.DataFrame,
    pattern: str,
    *,
    naumen_cost_map: Optional[dict[str, float]] = None,
) -> dict[str, pd.DataFrame]:
    fio_mask = df["ФИО заказчика"].str.contains(pattern, na=False, case=False)
    df_az = _apply_date_status_pipeline(df[fio_mask])
    df_vsp = _apply_date_status_pipeline(df[~fio_mask])

    result = {
        "az_mb": df_az[
            df_az["Территориальный банк"].astype(str).str.contains("38", na=False)
        ].copy(),
        "az_ca": df_az[
            df_az["Территориальный банк"].astype(str).str.contains("99", na=False)
        ].copy(),
        "vsp_mb": df_vsp[
            df_vsp["Территориальный банк"].astype(str).str.contains("38", na=False)
        ].copy(),
        "vsp_ca": df_vsp[
            df_vsp["Территориальный банк"].astype(str).str.contains("99", na=False)
        ].copy(),
    }
    for key, dfx in result.items():
        dfx["Месяц выполнения"] = month_period_str(dfx["Фактическая дата выполнения (UTC)"])
        dfx["Сумма с НДС"] = cleanup_money(dfx["Сумма с НДС"])
        _apply_naumen_cost_fallback(dfx, naumen_cost_map)
    return result


def _apply_chart_renames(frames: dict[str, pd.DataFrame], *, modern: bool) -> None:
    if modern:
        frames["az_mb"]["Статус согласования"] = frames["az_mb"]["Статус согласования"].replace(
            {"ДБ": "Семенова", "ОТСО": "Войнов"}
        )
        frames["az_ca"]["Статус согласования"] = frames["az_ca"]["Статус согласования"].replace(
            {"ОТСО": "Войнов", "ДБ": "Семенова"}
        )
        frames["vsp_mb"]["Статус согласования"] = frames["vsp_mb"][
            "Статус согласования"
        ].replace({"ДБ": "Семенова", "ОТСО": "Внутренний клиент"})
        frames["vsp_ca"]["Статус согласования"] = frames["vsp_ca"][
            "Статус согласования"
        ].replace({"ОТСО": "УКБ"})
    else:
        for key in ("az_mb", "az_ca"):
            frames[key]["Статус согласования"] = frames[key]["Статус согласования"].replace(
                {"ДБ": "Семенова", "ОТСО": "Войнов"}
            )
        frames["vsp_mb"]["Статус согласования"] = frames["vsp_mb"][
            "Статус согласования"
        ].replace({"ДБ": "Семенова", "ОТСО": "Внутренний клиент"})
        frames["vsp_ca"]["Статус согласования"] = frames["vsp_ca"][
            "Статус согласования"
        ].replace({"ОТСО": "УКБ"})


def _empty_frames() -> dict[str, pd.DataFrame]:
    empty = pd.DataFrame(columns=list(REQUIRED_COLUMNS) + ["Месяц выполнения", "Статус согласования"])
    return {key: empty.copy() for key, _ in SECTION_SPECS}


def _plot_stacked_by_month(df: pd.DataFrame, title: str) -> str:
    if df.empty or "Месяц выполнения" not in df.columns:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.text(0.5, 0.5, "Нет данных", ha="center", va="center", color="#9aa0a6")
        ax.set_axis_off()
        fig.tight_layout()
        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
        plt.close(fig)
        return base64.b64encode(buf.getvalue()).decode("ascii")

    grouped = (
        df.groupby(["Месяц выполнения", "Статус согласования"]).size().unstack(fill_value=0)
    )
    colors = [COLOR_MAP.get(col, "#6b7280") for col in grouped.columns]
    fig, ax = plt.subplots(figsize=(12, 5))
    grouped.plot(kind="bar", stacked=True, ax=ax, color=colors)
    for container in ax.containers:
        for bar in container:
            value = bar.get_height()
            if value > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + value / 2,
                    f"{int(value)}",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white",
                )
    ax.set_title(title, fontsize=14, pad=12)
    ax.set_xlabel("Месяц выполнения", fontsize=11)
    ax.set_ylabel("Количество заявок", fontsize=11)
    ax.legend(title="Статус", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    max_value = grouped.values.max() if grouped.size else 0
    if max_value > 843:
        ax.axhline(y=843, color="#6b7280", linestyle="--", linewidth=1)
    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _normalize_request_number(value: Any) -> str:
    if pd.isna(value):
        return ""
    raw = str(value).strip()
    if not raw:
        return ""
    digits = re.sub(r"\D", "", raw)
    return digits if digits else raw


def _status_badge(status: str) -> dict[str, str]:
    return {
        "text": status,
        "class": STATUS_BADGE_CLASSES.get(status, "status-default"),
    }


def _kpi_payload(df_filtered: pd.DataFrame, df_source: pd.DataFrame) -> dict[str, Any]:
    total_count = len(df_filtered)
    total_sum_val = df_source[df_source["Статус согласования"] != "Согласовано"][
        "Сумма с НДС"
    ].sum()
    oldest_date = (
        str(df_filtered["Месяц выполнения"].min())
        if not df_filtered.empty
        else "—"
    )
    return {
        "total_count": int(total_count),
        "total_sum": format_amount_rub(float(total_sum_val)),
        "oldest_date": oldest_date,
    }


def _table_rows(dfx: pd.DataFrame) -> list[dict[str, Any]]:
    cols = [
        "Месяц выполнения",
        "Статус согласования",
        "Заявка №",
        "Сумма с НДС",
        "Статус",
        "Статус акта",
    ]
    filtered = dfx[dfx["Статус согласования"] != "Согласовано"].copy()
    filtered = filtered[cols].sort_values(
        ["Месяц выполнения", "Статус согласования", "Заявка №"]
    )
    rows: list[dict[str, Any]] = []
    for _, row in filtered.iterrows():
        status_raw = str(row["Статус согласования"])
        request_num = _normalize_request_number(row["Заявка №"])
        rows.append(
            {
                "month": str(row["Месяц выполнения"]),
                "status": _status_badge(status_raw),
                "request_number": request_num,
                "request_url": SAP_URL_TEMPLATE.format(num=request_num)
                if request_num
                else "",
                "amount": format_amount_rub(float(row["Сумма с НДС"])).replace(
                    " руб.", ""
                ),
                "status_raw": str(row["Статус"]),
                "act_status": str(row["Статус акта"]),
            }
        )
    return rows


def _chart_titles(modern: bool) -> dict[str, str]:
    if modern:
        return {
            "az_mb": "Статус согласования заявок на модернизацию административных зданий МБ",
            "az_ca": "Статус согласования заявок на модернизацию административных зданий ЦА-МБ",
            "vsp_mb": "Статус согласования заявок на модернизацию ВСП и УС МБ",
            "vsp_ca": "Статус согласования заявок на модернизацию административных зданий ЦА (К32 и др.)",
        }
    return {
        "az_mb": "Статус согласования заявок на РВР административных зданий МБ",
        "az_ca": "Статус согласования заявок на РВР административных зданий ЦА-МБ",
        "vsp_mb": "Статус согласования заявок на РВР ВСП и УС МБ",
        "vsp_ca": "Статус согласования заявок на РВР административных зданий ЦА (К32 и др.)",
    }


def _build_report_kind(
    frames: dict[str, pd.DataFrame],
    *,
    modern: bool,
    on_progress: Optional[ProgressCallback] = None,
    progress_base: int = 0,
) -> dict[str, Any]:
    _apply_chart_renames(frames, modern=modern)
    titles = _chart_titles(modern)
    sections: list[dict[str, Any]] = []
    for idx, (key, title) in enumerate(SECTION_SPECS):
        if on_progress:
            on_progress("Построение графиков", progress_base + int(70 * (idx + 1) / 4))
        dfx = frames[key]
        filtered = dfx[dfx["Статус согласования"] != "Согласовано"]
        sections.append(
            {
                "key": key,
                "title": title,
                "kpi": _kpi_payload(filtered, dfx),
                "chart_b64": _plot_stacked_by_month(dfx, titles[key]),
                "rows": _table_rows(dfx),
            }
        )
    report_title = (
        "Отчет по статусу согласования заявок на модернизацию"
        if modern
        else "Отчет по статусу согласования заявок на ремонтно-восстановительные работы (РВР)"
    )
    return {"title": report_title, "sections": sections}


def _process_modern(
    df: pd.DataFrame,
    pattern: str,
    *,
    naumen_cost_map: Optional[dict[str, float]] = None,
) -> dict[str, pd.DataFrame]:
    df_modern = df[~df["Вид работ"].isin(["РВР", "ПТО", "Внеплановое ТО"])]
    df_modern = df_modern[~df_modern["Статус"].isin(["Отозвана ДБ", "Отозвана ВК"])]
    return _split_by_fio_tb(df_modern, pattern, naumen_cost_map=naumen_cost_map)


def _process_rvr(
    df: pd.DataFrame,
    pattern: str,
    *,
    naumen_cost_map: Optional[dict[str, float]] = None,
) -> dict[str, pd.DataFrame]:
    if "В лимите" not in df.columns:
        return _empty_frames()
    df_rvr = df[
        (
            ~df["Вид работ"].isin(
                [
                    "Модернизация",
                    "ПТО",
                    "Внеплановое ТО",
                    "Проектирование",
                    "Установка новых систем ТСО",
                ]
            )
        )
        & (~df["Статус"].isin(["Отозвана ДБ", "Отозвана ВК"]))
        & (
            df["В лимите"]
            .astype(str)
            .str.strip()
            .isin(["-", "Московский банк", "ЦА Сбербанк"])
        )
    ]
    if "Гарантийная заявка" in df_rvr.columns:
        df_rvr = df_rvr[df_rvr["Гарантийная заявка"] != 1]
    return _split_by_fio_tb(df_rvr, pattern, naumen_cost_map=naumen_cost_map)


def build_cashflow_report(
    xlsx_path: Path,
    *,
    on_progress: Optional[ProgressCallback] = None,
    naumen_cost_map: Optional[dict[str, float]] = None,
) -> dict[str, Any]:
    """Строит отчёт и возвращает JSON-структуру."""
    ensure_storage_dirs()
    _set_matplotlib_style()

    if on_progress:
        on_progress("Чтение файла", 5)

    df = read_excel(xlsx_path)
    _validate_columns(df)
    pattern = fio_pattern()

    if on_progress:
        on_progress("Обработка данных (модернизация)", 25)

    modern_frames = _process_modern(df, pattern, naumen_cost_map=naumen_cost_map)
    if on_progress:
        on_progress("Обработка данных (РВР)", 45)

    rvr_frames = _process_rvr(df, pattern, naumen_cost_map=naumen_cost_map)

    modern_report = _build_report_kind(
        modern_frames,
        modern=True,
        on_progress=on_progress,
        progress_base=50,
    )
    rvr_report = _build_report_kind(
        rvr_frames,
        modern=False,
        on_progress=on_progress,
        progress_base=75,
    )

    if on_progress:
        on_progress("Сохранение результата", 95)

    stat = xlsx_path.stat()
    generated_at = datetime.now(timezone.utc)
    payload = {
        "generated_at": generated_at.isoformat(),
        "source_file": xlsx_path.name,
        "source_mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "source_size": stat.st_size,
        "row_count": int(len(df)),
        "reports": {
            "modern": modern_report,
            "rvr": rvr_report,
        },
    }
    save_report_artifact(payload)
    if on_progress:
        on_progress("Готово", 100)
    return payload


def save_report_artifact(payload: dict[str, Any]) -> Path:
    ensure_storage_dirs()
    REPORT_ARTIFACT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return REPORT_ARTIFACT


def load_report_artifact() -> Optional[dict[str, Any]]:
    if not REPORT_ARTIFACT.is_file():
        return None
    try:
        return json.loads(REPORT_ARTIFACT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def requests_file_info() -> Optional[dict[str, Any]]:
    path = requests_file_path()
    if not path.is_file():
        return None
    stat = path.stat()
    return {
        "path": path,
        "filename": path.name,
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
    }
