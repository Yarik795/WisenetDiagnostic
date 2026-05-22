import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from .config_store import ConfigStore
from .logging_config import get_log_file_path, get_logger, setup_logging
from .poll_jobs import PollJobManager
from .scheduler import MonitoringScheduler
from .state_store import StateStore
from .ui.dependencies import get_state_store
from .web.routes import router as web_router

APP_DIR = Path(__file__).resolve().parent

setup_logging()
logger = get_logger("http")


@asynccontextmanager
async def lifespan(app: FastAPI):
    log_path = get_log_file_path()
    state_store = get_state_store()
    poll_jobs = PollJobManager()
    app.state.poll_job_manager = poll_jobs
    scheduler = MonitoringScheduler(ConfigStore(), state_store, poll_jobs=poll_jobs)
    app.state.scheduler = scheduler
    scheduler.start()
    logger.info(
        "application startup",
        extra={"event": "app_startup", "extra_log_file": str(log_path)},
    )
    yield
    await scheduler.stop()


app = FastAPI(
    title="Wisenet Диагностика",
    version="0.3.0",
    description="Этап 1: мониторинг регистраторов и каналов (SUNAPI)",
    lifespan=lifespan,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    is_htmx = request.headers.get("HX-Request") == "true"
    htmx_url = request.headers.get("HX-Current-URL", "")

    logger.info(
        "request",
        extra={
            "event": "http_request",
            "extra_method": request.method,
            "extra_path": request.url.path,
            "extra_htmx": is_htmx,
            "extra_htmx_url": htmx_url or None,
            "extra_client": request.client.host if request.client else None,
        },
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000)
        logger.exception(
            "request failed",
            extra={
                "event": "http_error",
                "extra_method": request.method,
                "extra_path": request.url.path,
                "extra_duration_ms": duration_ms,
            },
        )
        raise

    duration_ms = round((time.perf_counter() - start) * 1000)
    logger.info(
        "response",
        extra={
            "event": "http_response",
            "extra_method": request.method,
            "extra_path": request.url.path,
            "extra_status": response.status_code,
            "extra_duration_ms": duration_ms,
            "extra_htmx": is_htmx,
        },
    )
    return response


app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
app.include_router(web_router)
