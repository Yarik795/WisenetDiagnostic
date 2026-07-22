"""Генерация отчёта «Статус оплаты» из Excel-выгрузки заявок."""

from __future__ import annotations

import json
import re
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DATA_DIR = PROJECT_ROOT / "inputData"
UPLOADS_DIR = PROJECT_ROOT / "data" / "uploads"
REQUESTS_NAME_MARKER = "заявки"
REPORTS_DIR = PROJECT_ROOT / "data" / "reports"
REQUESTS_FILENAME = "requests.xlsx"
REPORT_ARTIFACT = REPORTS_DIR / "cashflow_report.json"

SAP_URL_TEMPLATE = "https://example.com/requests/{num}"

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


def _empty_approved(month_count: int = 0) -> dict[str, Any]:
    return {
        "amount": [0.0] * month_count,
        "count": [0] * month_count,
        "total_amount": 0.0,
        "total_count": 0,
    }


def _empty_series() -> dict[str, Any]:
    return {
        "months": [],
        "parties": [],
        "matrix": {},
        "party_totals": {},
        "count_matrix": {},
        "count_totals": {},
        "approved": _empty_approved(),
        "colors": {},
    }


def _series_by_month_party(df: pd.DataFrame) -> dict[str, Any]:
    """Агрегирует неоплаченную сумму/кол-во по месяцам и сторонам; отдельно — согласованные."""
    if df.empty or "Месяц выполнения" not in df.columns:
        return _empty_series()

    unpaid = df[df["Статус согласования"] != "Согласовано"]
    approved_df = df[df["Статус согласования"] == "Согласовано"]

    unpaid_months = (
        set(unpaid["Месяц выполнения"].astype(str).unique()) if not unpaid.empty else set()
    )
    approved_months = (
        set(approved_df["Месяц выполнения"].astype(str).unique())
        if not approved_df.empty
        else set()
    )
    all_months = sorted(unpaid_months | approved_months)
    if not all_months:
        return _empty_series()

    if unpaid.empty:
        parties: list[str] = []
        matrix: dict[str, list[float]] = {}
        party_totals: dict[str, float] = {}
        count_matrix: dict[str, list[int]] = {}
        count_totals: dict[str, int] = {}
    else:
        pivot = (
            unpaid.groupby(["Месяц выполнения", "Статус согласования"])["Сумма с НДС"]
            .sum()
            .unstack(fill_value=0.0)
        )
        count_pivot = (
            unpaid.groupby(["Месяц выполнения", "Статус согласования"])
            .size()
            .unstack(fill_value=0)
        )
        parties = [str(col) for col in pivot.columns]
        pivot = pivot.reindex(all_months, fill_value=0.0)
        count_pivot = count_pivot.reindex(all_months, fill_value=0)
        for party in parties:
            if party not in count_pivot.columns:
                count_pivot[party] = 0
        matrix = {party: [float(v) for v in pivot[party].values] for party in parties}
        party_totals = {party: float(pivot[party].sum()) for party in parties}
        count_matrix = {
            party: [int(v) for v in count_pivot[party].values] for party in parties
        }
        count_totals = {party: int(count_pivot[party].sum()) for party in parties}

    if approved_df.empty:
        approved = _empty_approved(len(all_months))
    else:
        approved_by_month = (
            approved_df.groupby("Месяц выполнения")
            .agg(amount=("Сумма с НДС", "sum"), count=("Сумма с НДС", "size"))
            .reindex(all_months, fill_value=0)
        )
        approved = {
            "amount": [float(v) for v in approved_by_month["amount"].values],
            "count": [int(v) for v in approved_by_month["count"].values],
            "total_amount": float(approved_by_month["amount"].sum()),
            "total_count": int(approved_by_month["count"].sum()),
        }

    colors = {party: COLOR_MAP.get(party, "#6b7280") for party in parties}
    colors["Согласовано"] = COLOR_MAP.get("Согласовано", "#34d399")

    return {
        "months": all_months,
        "parties": parties,
        "matrix": matrix,
        "party_totals": party_totals,
        "count_matrix": count_matrix,
        "count_totals": count_totals,
        "approved": approved,
        "colors": colors,
    }


def _parse_amount_display(amount: Any) -> float:
    if amount is None:
        return 0.0
    if isinstance(amount, (int, float)):
        return float(amount)
    text = str(amount).replace(" руб.", "").replace("\xa0", " ").strip()
    text = re.sub(r"\s+", "", text).replace(",", ".")
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def _row_amount_value(row: dict[str, Any]) -> float:
    if "amount_value" in row and row["amount_value"] is not None:
        return float(row["amount_value"])
    return _parse_amount_display(row.get("amount"))


def _row_party_name(row: dict[str, Any]) -> str:
    status = row.get("status")
    if isinstance(status, dict):
        return str(status.get("text", ""))
    return str(status or "")


def _series_from_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Восстанавливает series из строк таблицы (старые артефакты с chart_b64)."""
    if not rows:
        return _empty_series()
    month_party_amount: dict[str, dict[str, float]] = {}
    month_party_count: dict[str, dict[str, int]] = {}
    for row in rows:
        month = str(row.get("month", "")).strip()
        party = _row_party_name(row)
        if not month or not party:
            continue
        month_party_amount.setdefault(month, {})
        month_party_count.setdefault(month, {})
        month_party_amount[month][party] = (
            month_party_amount[month].get(party, 0.0) + _row_amount_value(row)
        )
        month_party_count[month][party] = month_party_count[month].get(party, 0) + 1
    if not month_party_amount:
        return _empty_series()
    months = sorted(month_party_amount.keys())
    parties = sorted({party for amounts in month_party_amount.values() for party in amounts})
    matrix = {
        party: [float(month_party_amount.get(month, {}).get(party, 0.0)) for month in months]
        for party in parties
    }
    count_matrix = {
        party: [int(month_party_count.get(month, {}).get(party, 0)) for month in months]
        for party in parties
    }
    party_totals = {party: float(sum(matrix[party])) for party in parties}
    count_totals = {party: int(sum(count_matrix[party])) for party in parties}
    colors = {party: COLOR_MAP.get(party, "#6b7280") for party in parties}
    colors["Согласовано"] = COLOR_MAP.get("Согласовано", "#34d399")
    return {
        "months": months,
        "parties": parties,
        "matrix": matrix,
        "party_totals": party_totals,
        "count_matrix": count_matrix,
        "count_totals": count_totals,
        "approved": _empty_approved(len(months)),
        "colors": colors,
    }


def _normalize_section(section: dict[str, Any]) -> dict[str, Any]:
    out = dict(section)
    rows = list(out.get("rows") or [])
    for row in rows:
        if "amount_value" not in row or row["amount_value"] is None:
            row["amount_value"] = _row_amount_value(row)
    out["rows"] = rows
    if "series" not in out or out["series"] is None:
        out["series"] = _series_from_rows(rows)
    kpi = dict(out.get("kpi") or {})
    if "largest_amount" not in kpi:
        if rows:
            largest_val = max(_row_amount_value(row) for row in rows)
            kpi["largest_amount"] = format_amount_rub(largest_val) if largest_val else "—"
        else:
            kpi["largest_amount"] = "—"
    out["kpi"] = kpi
    out.pop("chart_b64", None)
    return out


def normalize_report_payload(report: dict[str, Any]) -> dict[str, Any]:
    """Приводит артефакт отчёта к актуальной схеме (series, largest_amount)."""
    out = dict(report)
    reports = out.get("reports")
    if not isinstance(reports, dict):
        return out
    normalized_reports: dict[str, Any] = {}
    for kind, kind_report in reports.items():
        if not isinstance(kind_report, dict):
            normalized_reports[kind] = kind_report
            continue
        kind_out = dict(kind_report)
        sections = kind_out.get("sections")
        if isinstance(sections, list):
            kind_out["sections"] = [_normalize_section(section) for section in sections if isinstance(section, dict)]
        normalized_reports[kind] = kind_out
    out["reports"] = normalized_reports
    return out


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
    unpaid = df_source[df_source["Статус согласования"] != "Согласовано"]
    total_sum_val = unpaid["Сумма с НДС"].sum()
    oldest_date = (
        str(df_filtered["Месяц выполнения"].min())
        if not df_filtered.empty
        else "—"
    )
    if df_filtered.empty:
        largest_amount = "—"
    else:
        largest_val = float(df_filtered["Сумма с НДС"].max())
        largest_amount = format_amount_rub(largest_val)
    return {
        "total_count": int(total_count),
        "total_sum": format_amount_rub(float(total_sum_val)),
        "oldest_date": oldest_date,
        "largest_amount": largest_amount,
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
                "amount_value": float(row["Сумма с НДС"]),
                "status_raw": str(row["Статус"]),
                "act_status": str(row["Статус акта"]),
            }
        )
    return rows


def _build_report_kind(
    frames: dict[str, pd.DataFrame],
    *,
    modern: bool,
    on_progress: Optional[ProgressCallback] = None,
    progress_base: int = 0,
) -> dict[str, Any]:
    _apply_chart_renames(frames, modern=modern)
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
                "series": _series_by_month_party(dfx),
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
        payload = json.loads(REPORT_ARTIFACT.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not isinstance(payload, dict):
        return None
    return normalize_report_payload(payload)


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
