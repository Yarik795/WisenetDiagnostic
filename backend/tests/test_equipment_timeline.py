"""Тесты общей логики отчётов по времени."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.models import Recorder
from app.state_store import ChannelRow, RecorderMetricsRow, StateStore
from app.ui.equipment_timeline import (
    CameraWithContext,
    RecorderWithMetrics,
    aggregate_cameras_by_period,
    aggregate_disks_by_wear,
    aggregate_recorders_by_period,
    camera_age_detail_rows,
    camera_age_kpi,
    camera_age_missing_rows,
    disk_wear_detail_rows,
    disk_wear_missing_rows,
    explode_disk_rows,
    normalize_period_filter,
    parse_manufacture_date,
    period_key,
    recorder_age_detail_rows,
    recorder_age_missing_rows,
    wear_bucket_key,
)


def _recorder(
    *,
    rec_id: str = "nvr-1",
    object_name: str = "Объект А",
    device_kind: str = "tsv",
) -> Recorder:
    return Recorder(
        id=rec_id,
        object_name=object_name,
        host="10.0.0.1",
        device_kind=device_kind,  # type: ignore[arg-type]
    )


def _metrics(
    *,
    rec_id: str = "nvr-1",
    manufacture_date: str | None = "2020-09",
    disks_json: str | None = None,
    model: str | None = "PRN-4011",
) -> RecorderMetricsRow:
    return RecorderMetricsRow(
        recorder_id=rec_id,
        model=model,
        firmware_version=None,
        device_online=True,
        health_status="ok",
        health_reason=None,
        ntp_status=None,
        time_skew_seconds=None,
        storage_used_percent=None,
        storage_status=None,
        archive_start=None,
        archive_end=None,
        archive_days=None,
        archive_min_days=None,
        archive_max_days=None,
        channel_count=0,
        channels_ok=0,
        channels_warn=0,
        channels_error=0,
        channels_unknown=0,
        last_polled_at=None,
        manufacture_date=manufacture_date,
        disks_json=disks_json,
        serial_number="SN123",
    )


def test_parse_manufacture_date_and_period_key() -> None:
    parsed = parse_manufacture_date("2020-09")
    assert parsed is not None
    assert period_key(parsed, "month") == "2020-09"
    assert period_key(parsed, "quarter") == "2020-Q3"
    assert period_key(parsed, "year") == "2020"
    assert parse_manufacture_date("invalid") is None


def test_normalize_period_filter_quarter() -> None:
    assert normalize_period_filter("2020-09", "quarter") == "2020-Q3"
    assert normalize_period_filter("2020", "year") == "2020"


def test_aggregate_recorders_by_period_and_detail() -> None:
    items = [
        RecorderWithMetrics(_recorder(rec_id="nvr-1"), _metrics(rec_id="nvr-1", manufacture_date="2020-09")),
        RecorderWithMetrics(_recorder(rec_id="nvr-2", object_name="Объект Б"), _metrics(rec_id="nvr-2", manufacture_date="2020-11")),
        RecorderWithMetrics(_recorder(rec_id="nvr-3"), _metrics(rec_id="nvr-3", manufacture_date=None)),
        RecorderWithMetrics(
            _recorder(rec_id="skud-1", device_kind="skud"),
            _metrics(rec_id="skud-1", manufacture_date=None),
        ),
    ]
    chart = aggregate_recorders_by_period(items, grouping="quarter")
    assert chart["labels"]
    assert sum(chart["values"]) == 2

    rows = recorder_age_detail_rows(items, period="2020-Q3", grouping="quarter")
    assert len(rows) == 1
    assert rows[0]["object_name"] == "Объект А"
    assert rows[0]["metric_value"] == "сен. 2020"


def test_aggregate_recorders_period_filter() -> None:
    items = [
        RecorderWithMetrics(_recorder(), _metrics(manufacture_date="2019-06")),
        RecorderWithMetrics(_recorder(rec_id="nvr-2"), _metrics(rec_id="nvr-2", manufacture_date="2021-03")),
    ]
    chart = aggregate_recorders_by_period(
        items,
        grouping="year",
        from_key="2020",
        to_key="2020",
    )
    assert chart["keys"] == []
    assert chart["values"] == []

    chart2 = aggregate_recorders_by_period(
        items,
        grouping="year",
        from_key="2019",
        to_key="2021",
    )
    assert chart2["keys"] == ["2019", "2021"]
    assert chart2["values"] == [1, 1]


def test_disk_wear_buckets_and_detail() -> None:
    disks_json = (
        '[{"Storage":"1","Model":"WD_RED","PowerOnDuration":"4380"},'
        '{"Storage":"2","Model":"WD_RED","PowerOnDuration":"17520"}]'
    )
    items = [
        RecorderWithMetrics(_recorder(), _metrics(disks_json=disks_json)),
    ]
    exploded = explode_disk_rows(items)
    assert len(exploded) == 2
    assert wear_bucket_key(4380, 1.0) == "0-1"
    assert wear_bucket_key(17520, 1.0) == "2-3"

    chart = aggregate_disks_by_wear(exploded, bucket="1")
    assert sum(chart["values"]) == 2

    rows = disk_wear_detail_rows(exploded, bucket_key="0-1", bucket="1")
    assert len(rows) == 1
    assert rows[0]["object_name"] == "Объект А"
    assert rows[0]["disk_model"] == "WD_RED"


def test_list_tsv_recorders_with_metrics_filters_skud(tmp_path: Path) -> None:
    from app.config_store import ConfigStore

    config_path = tmp_path / "config.json"
    config_path.write_text(
        """{
  "credentials": {"username": "", "password": ""},
  "monitoring": {},
  "recorders": [
    {"id": "nvr-1", "object_name": "Obj", "host": "10.0.0.1", "device_kind": "tsv"},
    {"id": "skud-1", "object_name": "Obj2", "host": "10.0.0.2", "device_kind": "skud"}
  ]
}""",
        encoding="utf-8",
    )
    store = ConfigStore(path=config_path)
    state = StateStore(tmp_path / "monitoring.db")
    state.init_db()

    from app.ui.equipment_timeline import list_tsv_recorders_with_metrics

    items = list_tsv_recorders_with_metrics(store, state)
    assert len(items) == 1
    assert items[0].recorder.id == "nvr-1"


def _channel(**kwargs) -> ChannelRow:
    defaults = dict(
        id=1,
        recorder_id="nvr-1",
        channel_no=0,
        name="Cam 1",
        camera_ip="10.0.0.10",
        camera_model="IPC-HFW1230",
        source_state="On",
        health_status="ok",
        health_reason=None,
        video_loss=False,
        last_polled_at=None,
        manufacturer="dahua",
        manufacture_date="2020-06",
        manufacture_date_source="firmware_build",
        camera_serial="SN1",
    )
    defaults.update(kwargs)
    return ChannelRow(**defaults)


def test_aggregate_cameras_by_period_and_kpi() -> None:
    rec = _recorder()
    items = [
        CameraWithContext(_channel(), rec),
        CameraWithContext(
            _channel(channel_no=1, camera_ip="10.0.0.11", manufacture_date="2021-03"),
            rec,
        ),
        CameraWithContext(
            _channel(channel_no=2, camera_ip="10.0.0.12", manufacture_date=None),
            rec,
        ),
    ]
    chart = aggregate_cameras_by_period(items, grouping="year")
    assert chart["keys"] == ["2020", "2021"]
    assert chart["values"] == [1, 1]

    kpi = camera_age_kpi(items)
    assert kpi["total_cameras"] == 3
    assert kpi["with_date"] == 2
    assert kpi["dahua_count"] == 3

    rows = camera_age_detail_rows(items, period="2020", grouping="year")
    assert len(rows) == 1
    assert rows[0]["camera_ip"] == "10.0.0.10"
    assert rows[0]["date_source"] == "сборка прошивки"


def test_recorder_age_missing_rows() -> None:
    items = [
        RecorderWithMetrics(_recorder(rec_id="nvr-1"), _metrics(rec_id="nvr-1", manufacture_date="2020-09")),
        RecorderWithMetrics(_recorder(rec_id="nvr-2"), _metrics(rec_id="nvr-2", manufacture_date=None)),
        RecorderWithMetrics(_recorder(rec_id="nvr-3"), _metrics(rec_id="nvr-3", manufacture_date="bad-date")),
    ]
    missing = recorder_age_missing_rows(items)
    assert len(missing) == 2
    assert {r["recorder_name"] for r in missing} == {"10.0.0.1"}

    detail = recorder_age_detail_rows(items, period="2020-Q3", grouping="quarter")
    assert len(detail) == 1

    filtered = recorder_age_missing_rows(items, model="PRN-4011")
    assert len(filtered) == 2


def test_camera_age_missing_rows() -> None:
    rec = _recorder()
    items = [
        CameraWithContext(_channel(), rec),
        CameraWithContext(
            _channel(channel_no=1, camera_ip="10.0.0.11", manufacture_date=None),
            rec,
        ),
        CameraWithContext(
            _channel(
                channel_no=2,
                camera_ip="10.0.0.12",
                manufacture_date=None,
                camera_inventory_error="timeout",
            ),
            rec,
        ),
    ]
    missing = camera_age_missing_rows(items)
    assert len(missing) == 2
    assert missing[0]["camera_ip"] == "10.0.0.11"
    assert any(r["missing_reason"] == "timeout" for r in missing)

    detail = camera_age_detail_rows(items, period="2020", grouping="year")
    assert len(detail) == 1

    filtered = camera_age_missing_rows(items, model="IPC-HFW1230")
    assert len(filtered) == 2


def test_disk_wear_missing_rows() -> None:
    disks_json = (
        '[{"Storage":"1","Model":"WD_RED","PowerOnDuration":"4380"},'
        '{"Storage":"2","Model":"WD_RED"},'
        '{"Storage":"3","Model":"ST1000"}]'
    )
    items = [
        RecorderWithMetrics(_recorder(), _metrics(disks_json=disks_json)),
    ]
    missing = disk_wear_missing_rows(items)
    assert len(missing) == 2
    assert {r["disk_slot"] for r in missing} == {"2", "3"}

    exploded = explode_disk_rows(items)
    detail = disk_wear_detail_rows(exploded, bucket_key="0-1", bucket="1")
    assert len(detail) == 1

    filtered = disk_wear_missing_rows(items, model="ST1000")
    assert len(filtered) == 1
    assert filtered[0]["disk_model"] == "ST1000"


def test_channels_inventory_columns_migration(tmp_path: Path) -> None:
    state = StateStore(tmp_path / "monitoring.db")
    state.init_db()
    state.upsert_channel(
        "nvr-1",
        0,
        camera_ip="10.0.0.5",
        camera_user_id="admin",
        camera_http_port=80,
        camera_protocol="ONVIF",
    )
    state.update_camera_inventory(
        "nvr-1",
        0,
        manufacturer="dahua",
        camera_serial="ABC",
        manufacture_date="2020-01",
        manufacture_date_source="firmware_build",
    )
    row = state.get_channel("nvr-1", 0)
    assert row is not None
    assert row.camera_user_id == "admin"
    assert row.manufacturer == "dahua"
    assert row.manufacture_date == "2020-01"
