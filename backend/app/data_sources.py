"""Единый реестр и загрузка исходных данных из inputData."""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Optional

from .cashflow_report import build_cashflow_report, ensure_storage_dirs
from .cmdb_sync import sync_from_cmdb

if TYPE_CHECKING:
    from .config_store import ConfigStore
    from .state_store import StateStore

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DATA_DIR = PROJECT_ROOT / "inputData"
UPLOADS_DIR = PROJECT_ROOT / "data" / "uploads"

ProgressCallback = Callable[[str, int], None]


@dataclass(frozen=True)
class SourceLoadResult:
    ok: bool
    message: str
    record_count: int = 0
    changed: bool = True
    filename: Optional[str] = None


@dataclass(frozen=True)
class RunnerDeps:
    store: "ConfigStore"
    state: "StateStore"


@dataclass(frozen=True)
class SourceSpec:
    key: str
    label: str
    button_label: str
    button_title: str
    name_marker: str
    storage_filename: str


def input_data_dir() -> Path:
    return INPUT_DATA_DIR


def storage_path(spec: SourceSpec) -> Path:
    return UPLOADS_DIR / spec.storage_filename


def ensure_input_data_dir() -> Path:
    INPUT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    return INPUT_DATA_DIR


def find_latest_source_file(
    spec: SourceSpec,
    directory: Path | None = None,
) -> Path:
    """Самый свежий .xlsx в inputData с маркером в имени."""
    root = directory or INPUT_DATA_DIR
    if not root.is_dir():
        raise FileNotFoundError(
            f"Папка inputData не найдена: {root}. "
            f"Положите файл с «{spec.name_marker}» в названии."
        )

    marker = spec.name_marker.lower()
    candidates = [
        path
        for path in root.iterdir()
        if path.is_file()
        and path.suffix.lower() == ".xlsx"
        and marker in path.name.lower()
    ]
    if not candidates:
        raise FileNotFoundError(
            f"В папке {root} нет файлов .xlsx с «{spec.name_marker}» в названии"
        )
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_identical(source: Path, dest: Path) -> bool:
    if not dest.is_file():
        return False
    return _file_hash(source) == _file_hash(dest)


def _clear_readonly(path: Path) -> None:
    if not path.is_file():
        return
    mode = path.stat().st_mode
    if not mode & stat.S_IWRITE:
        path.chmod(mode | stat.S_IWRITE)


def storage_permission_message(target: Path) -> str:
    return (
        f"Не удалось перезаписать {target.name} в data/uploads/. "
        "Закройте этот файл в Excel или проводнике и повторите загрузку."
    )


def copy_to_storage(spec: SourceSpec, source: Path) -> Path:
    ensure_storage_dirs()
    target = storage_path(spec)
    tmp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    try:
        shutil.copy2(source, tmp)
        _clear_readonly(target)
        os.replace(tmp, target)
    except PermissionError as exc:
        tmp.unlink(missing_ok=True)
        raise PermissionError(storage_permission_message(target)) from exc
    except OSError:
        tmp.unlink(missing_ok=True)
        raise
    return target


def _run_cmdb(
    dest: Path,
    source: Path,
    deps: RunnerDeps,
    on_progress: ProgressCallback,
    *,
    file_unchanged: bool,
) -> SourceLoadResult:
    on_progress("Чтение CMDB", 40)
    result = sync_from_cmdb(
        deps.store, dest, state=deps.state, record_import=False
    )
    on_progress("Сохранение", 90)

    if not result.ok:
        return SourceLoadResult(
            ok=False,
            message=result.message,
            filename=source.name,
        )

    changed = not (
        file_unchanged and result.stats and result.stats.added == 0 and result.stats.removed == 0
    )
    if "Изменений нет" in result.message or not changed:
        message = "Новых данных нет"
        changed = False
    elif result.stats:
        message = (
            f"Данные загружены: обновлено {result.total_recorders} устройств "
            f"(новых {result.stats.added}, удалено {result.stats.removed})"
        )
    else:
        message = f"Данные загружены: {result.total_recorders} устройств"

    return SourceLoadResult(
        ok=True,
        message=message,
        record_count=result.total_recorders,
        changed=changed,
        filename=source.name,
    )


def _run_requests(
    dest: Path,
    source: Path,
    deps: RunnerDeps,
    on_progress: ProgressCallback,
    *,
    file_unchanged: bool,
) -> SourceLoadResult:
    from .cashflow_report import load_report_artifact

    if file_unchanged and load_report_artifact() is not None:
        on_progress("Проверка", 50)
        return SourceLoadResult(
            ok=True,
            message="Новых данных нет",
            record_count=0,
            changed=False,
            filename=source.name,
        )

    def report_progress(phase: str, percent: int) -> None:
        on_progress(phase, 25 + int(percent * 0.65))

    report = build_cashflow_report(
        dest,
        on_progress=report_progress,
        naumen_cost_map=deps.state.naumen_cost_by_sberdrug(),
    )
    row_count = int(report.get("row_count", 0))
    return SourceLoadResult(
        ok=True,
        message=f"Данные загружены: {row_count} строк",
        record_count=row_count,
        changed=True,
        filename=source.name,
    )


def _run_naumen(
    dest: Path,
    source: Path,
    deps: RunnerDeps,
    on_progress: ProgressCallback,
    *,
    file_unchanged: bool,
) -> SourceLoadResult:
    if file_unchanged and deps.state.count_naumen_records() > 0:
        on_progress("Проверка", 50)
        return SourceLoadResult(
            ok=True,
            message="Новых данных нет",
            record_count=deps.state.count_naumen_records(),
            changed=False,
            filename=source.name,
        )

    from .naumen_import import import_naumen_xlsx

    def report_progress(phase: str, percent: int) -> None:
        on_progress(phase, 25 + int(percent * 0.65))

    row_count = import_naumen_xlsx(dest, deps.state, on_progress=report_progress)
    return SourceLoadResult(
        ok=True,
        message=f"Данные загружены: {row_count} строк",
        record_count=row_count,
        changed=True,
        filename=source.name,
    )


def _run_arsenal(
    dest: Path,
    source: Path,
    deps: RunnerDeps,
    on_progress: ProgressCallback,
    *,
    file_unchanged: bool,
) -> SourceLoadResult:
    if file_unchanged and deps.state.count_arsenal_records() > 0:
        on_progress("Проверка", 50)
        return SourceLoadResult(
            ok=True,
            message="Новых данных нет",
            record_count=deps.state.count_arsenal_records(),
            changed=False,
            filename=source.name,
        )

    from .arsenal_import import import_arsenal_xlsx

    def report_progress(phase: str, percent: int) -> None:
        on_progress(phase, 25 + int(percent * 0.65))

    row_count = import_arsenal_xlsx(dest, deps.state, on_progress=report_progress)
    return SourceLoadResult(
        ok=True,
        message=f"Данные загружены: {row_count} паспортов",
        record_count=row_count,
        changed=True,
        filename=source.name,
    )


_RUNNERS: dict[str, Callable[..., SourceLoadResult]] = {
    "cmdb": _run_cmdb,
    "requests": _run_requests,
    "naumen": _run_naumen,
    "arsenal": _run_arsenal,
}

CMDB_SOURCE = SourceSpec(
    key="cmdb",
    label="CMDB",
    button_label="Обновить CMDB",
    button_title=(
        'Берёт самый свежий файл *.xlsx, содержащий "cmdb" в имени, из папки inputData'
    ),
    name_marker="cmdb",
    storage_filename="cmdb.xlsx",
)

REQUESTS_SOURCE = SourceSpec(
    key="requests",
    label="Заявки с ПП",
    button_label="Обновить заявки с ПП",
    button_title=(
        'Берёт самый свежий файл *.xlsx, содержащий "заявки" в имени, из папки inputData'
    ),
    name_marker="заявки",
    storage_filename="requests.xlsx",
)

NAUMEN_SOURCE = SourceSpec(
    key="naumen",
    label="Данные из Naumen",
    button_label="Обновить Naumen",
    button_title=(
        'Берёт самый свежий файл *.xlsx с «naumen» в имени '
        '(например naumen_all.xlsx) из папки inputData'
    ),
    name_marker="naumen",
    storage_filename="naumen.xlsx",
)

ARSENAL_SOURCE = SourceSpec(
    key="arsenal",
    label="АС Арсенал",
    button_label="Обновить Арсенал",
    button_title=(
        'Берёт самый свежий файл *.xlsx с «паспортам» в имени '
        'из папки inputData'
    ),
    name_marker="паспортам",
    storage_filename="arsenal.xlsx",
)

SOURCES: dict[str, SourceSpec] = {
    CMDB_SOURCE.key: CMDB_SOURCE,
    REQUESTS_SOURCE.key: REQUESTS_SOURCE,
    NAUMEN_SOURCE.key: NAUMEN_SOURCE,
    ARSENAL_SOURCE.key: ARSENAL_SOURCE,
}


def get_source_spec(key: str) -> SourceSpec:
    spec = SOURCES.get(key)
    if spec is None:
        raise KeyError(f"Неизвестный источник данных: {key}")
    return spec


def load_source(
    key: str,
    deps: RunnerDeps,
    on_progress: Optional[ProgressCallback] = None,
) -> SourceLoadResult:
    """Находит файл в inputData, копирует в хранилище и обрабатывает."""
    spec = get_source_spec(key)
    progress = on_progress or (lambda _phase, _percent: None)

    progress("Поиск файла", 5)
    try:
        source = find_latest_source_file(spec)
    except FileNotFoundError as exc:
        return SourceLoadResult(ok=False, message=str(exc))

    dest = storage_path(spec)
    unchanged = dest.is_file() and files_identical(source, dest)
    storage_copy_skipped = False

    if not unchanged:
        progress("Копирование", 20)
        try:
            copy_to_storage(spec, source)
        except PermissionError:
            # Файл в data/uploads/ часто занят Excel на Windows — импортируем из inputData.
            dest = source
            storage_copy_skipped = True
            progress("Чтение из inputData", 20)
    else:
        progress("Файл без изменений", 20)

    runner = _RUNNERS[spec.key]
    result = runner(
        dest,
        source,
        deps,
        progress,
        file_unchanged=unchanged and not storage_copy_skipped,
    )

    if result.ok and storage_copy_skipped:
        result = SourceLoadResult(
            ok=True,
            message=(
                f"{result.message} "
                f"(копия в data/uploads не обновлена: {storage_path(spec).name} занят — "
                "закройте файл в Excel)"
            ),
            record_count=result.record_count,
            changed=result.changed,
            filename=result.filename,
        )

    if result.ok:
        deps.state.record_source_import(
            spec.key,
            filename=result.filename or source.name,
            record_count=result.record_count,
            status="ok",
            message=result.message,
        )
    else:
        deps.state.record_source_import(
            spec.key,
            filename=result.filename or source.name,
            record_count=0,
            status="error",
            message=result.message,
        )

    return result

