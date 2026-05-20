from pathlib import Path

from fastapi.templating import Jinja2Templates

from ..config_store import ConfigStore
from ..ui.grouping import (
    STATUS_LABELS,
    effective_status,
    problem_count,
)
from ..ui.helpers import (
    display_recorder_name,
    format_datetime,
    format_host_port,
    format_time,
)
from ..ui.metrics_helpers import (
    disk_field,
    disk_percent_display,
    disk_slot,
    disk_temperature_display,
    disk_total_display,
    disk_used_display,
    max_disk_temperature,
    format_archive_days,
    format_archive_days_value,
    format_archive_range,
    format_bool_ru,
    format_channel_counts,
    format_mb,
    format_percent,
    format_skew,
    parse_disks_json,
)

APP_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

templates.env.globals["display_recorder_name"] = display_recorder_name
templates.env.globals["format_host_port"] = format_host_port
templates.env.globals["format_time"] = format_time
templates.env.globals["format_datetime"] = format_datetime
templates.env.globals["status_label"] = lambda s: STATUS_LABELS.get(s, s)
templates.env.globals["effective_status"] = effective_status
templates.env.globals["problem_count"] = problem_count
templates.env.globals["parse_disks"] = parse_disks_json
templates.env.globals["format_mb"] = format_mb
templates.env.globals["format_percent"] = format_percent
templates.env.globals["format_archive_days"] = format_archive_days
templates.env.globals["format_archive_days_value"] = format_archive_days_value
templates.env.globals["format_archive_range"] = format_archive_range
templates.env.globals["format_skew"] = format_skew
templates.env.globals["format_channel_counts"] = format_channel_counts
templates.env.globals["format_bool_ru"] = format_bool_ru
templates.env.globals["disk_slot"] = disk_slot
templates.env.globals["disk_field"] = disk_field
templates.env.globals["disk_used_display"] = disk_used_display
templates.env.globals["disk_total_display"] = disk_total_display
templates.env.globals["disk_percent_display"] = disk_percent_display
templates.env.globals["disk_temperature_display"] = disk_temperature_display
templates.env.globals["max_disk_temperature"] = max_disk_temperature
templates.env.globals["archive_days_required"] = (
    lambda: ConfigStore().load().monitoring.archive_days_required
)
