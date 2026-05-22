from types import SimpleNamespace

from app.models import Credentials, MonitoringSettings
from app.ui.helpers import device_web_interface_url, device_web_link_title
from app.ui.error_report import build_error_report_context


def _rec(**kwargs):
    base = dict(
        id="r1",
        object_name="ВСП-001",
        name="NVR-main",
        host="192.168.1.10",
        port=80,
        use_https=False,
        enabled=True,
    )
    base.update(kwargs)
    return SimpleNamespace(**base)


def test_device_web_interface_url_plain() -> None:
    url = device_web_interface_url(_rec())
    assert url == "http://192.168.1.10"


def test_device_web_interface_url_userinfo() -> None:
    creds = Credentials(username="admin", password="p@ss:word")
    url = device_web_interface_url(
        _rec(), credentials=creds, device_auth="userinfo"
    )
    assert url.startswith("http://admin:p%40ss%3Aword@192.168.1.10")


def test_device_web_link_title() -> None:
    assert device_web_link_title(_rec()) == "Открыть web-интерфейс NVR: NVR-main"


def test_build_error_report_empty() -> None:
    ctx = build_error_report_context([], {}, MonitoringSettings())
    assert ctx.problem_count == 0
    assert ctx.device_auth_warning == ""
