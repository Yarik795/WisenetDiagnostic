import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

from .logging_config import get_logger, setup_logging
from .web.routes import router as web_router

APP_DIR = Path(__file__).resolve().parent

setup_logging()
logger = get_logger("http")

app = FastAPI(
    title="Wisenet Диагностика",
    version="0.2.0",
    description="Этап 0: реестр регистраторов и проверка SUNAPI",
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
