from pathlib import Path

from fastapi.templating import Jinja2Templates

from ..ui.grouping import (
    STATUS_LABELS,
    effective_status,
    problem_count,
)
from ..ui.helpers import display_recorder_name, format_host_port, format_time

APP_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

templates.env.globals["display_recorder_name"] = display_recorder_name
templates.env.globals["format_host_port"] = format_host_port
templates.env.globals["format_time"] = format_time
templates.env.globals["status_label"] = lambda s: STATUS_LABELS.get(s, s)
templates.env.globals["effective_status"] = effective_status
templates.env.globals["problem_count"] = problem_count
