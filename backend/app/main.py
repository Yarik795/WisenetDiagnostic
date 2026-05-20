from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .web.routes import router as web_router

APP_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Wisenet Диагностика",
    version="0.2.0",
    description="Этап 0: реестр регистраторов и проверка SUNAPI",
)

app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
app.include_router(web_router)
