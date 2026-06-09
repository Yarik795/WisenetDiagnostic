from pathlib import Path

from fastapi.templating import Jinja2Templates

from ..config_store import ConfigStore
from ..device_kinds import ALL_DEVICE_KINDS, SYSTEM_KIND_LABELS, kind_label, source_label
from ..exclusions import excluded_ids_set
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
from ..ui.health_classifiers import BADGE_CODES, CATEGORY_LABELS, recorder_problem_badges
from ..ui.health_dashboard import object_category_problem_counts, object_health_problem_count
from ..ui.time_dashboard import object_time_problem_count
from ..ui.metrics_helpers import (
    disk_field,
    disk_percent_display,
    disk_slot,
    disk_temperature_display,
    disk_total_display,
    disk_used_display,
    is_manual_sync,
    needs_ntp_time_update,
    ntp_action_button_label,
    show_ntp_action_button,
    max_disk_temperature,
    format_archive_days,
    format_archive_days_value,
    format_archive_range,
    format_manufacture_date,
    format_bool_ru,
    format_channel_counts,
    format_mb,
    format_percent,
    format_cpu_usage,
    format_mbps,
    format_skew,
    disk_drop_display,
    disk_power_on_hours,
    parse_disks_json,
    sync_type_badge_class,
    sync_type_label,
    system_events_display,
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
templates.env.globals["format_cpu_usage"] = format_cpu_usage
templates.env.globals["format_mbps"] = format_mbps
templates.env.globals["disk_drop_display"] = disk_drop_display
templates.env.globals["disk_power_on_hours"] = disk_power_on_hours
templates.env.globals["format_archive_days"] = format_archive_days
templates.env.globals["format_archive_days_value"] = format_archive_days_value
templates.env.globals["format_archive_range"] = format_archive_range
templates.env.globals["format_manufacture_date"] = format_manufacture_date
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
templates.env.globals["system_events_display"] = system_events_display
templates.env.globals["is_manual_sync"] = is_manual_sync
templates.env.globals["needs_ntp_time_update"] = needs_ntp_time_update
templates.env.globals["show_ntp_action_button"] = show_ntp_action_button
templates.env.globals["ntp_action_button_label"] = ntp_action_button_label
templates.env.globals["sync_type_label"] = sync_type_label
templates.env.globals["sync_type_badge_class"] = sync_type_badge_class
templates.env.globals["archive_days_required"] = (
    lambda: ConfigStore().load().monitoring.archive_days_required
)
templates.env.globals["get_monitoring_settings"] = (
    lambda: ConfigStore().load().monitoring
)
templates.env.globals["object_time_problem_count"] = object_time_problem_count
templates.env.globals["object_health_problem_count"] = object_health_problem_count
templates.env.globals["object_category_problem_counts"] = object_category_problem_counts
templates.env.globals["recorder_problem_badges"] = recorder_problem_badges
templates.env.globals["category_badge_code"] = lambda c: BADGE_CODES.get(c, c)
templates.env.globals["category_label"] = lambda c: CATEGORY_LABELS.get(c, c)


def _is_recorder_excluded(recorder_id: str) -> bool:
    return recorder_id in excluded_ids_set(ConfigStore().load())


templates.env.globals["is_recorder_excluded"] = _is_recorder_excluded
templates.env.globals["device_kinds"] = ALL_DEVICE_KINDS
templates.env.globals["kind_labels"] = SYSTEM_KIND_LABELS
templates.env.globals["kind_label"] = kind_label
templates.env.globals["source_label"] = source_label
