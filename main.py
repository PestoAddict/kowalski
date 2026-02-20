"""
Точка входа
"""

import uvicorn
from fastapi import FastAPI

from src import handlers
from src.core.config import settings
from src.depends.startup import startup


def build_app() -> FastAPI:
    """
    Формирование приложения для запуска
    """
    fast_api_app = FastAPI(
        title="Kowalski, analysis!",
        description="Сервис для команды аналитиков.",
        version="0.0.0")

    fast_api_app.include_router(handlers.router)
    return fast_api_app


app = build_app()


@app.on_event("startup")
async def on_startup():
    """_onon_startup_
    """
    await startup()


def main() -> None:
    """
    Главная функция с запуском сервиса
    """

    server = uvicorn.Server(
        uvicorn.Config(
            app=app,
            host=settings.WEB_APP_HOST,
            port=settings.WEB_APP_PORT,
            reload=True
        )
    )
    server.run()


if __name__ == "__main__":
    main()
