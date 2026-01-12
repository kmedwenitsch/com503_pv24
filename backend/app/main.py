from fastapi import FastAPI

from .core.config import settings
from .core.logging import setup_logging

from .api.routes_health import router as health_router
from .api.routes_jobs import router as jobs_router
from .api.routes_outputs import router as outputs_router


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title=settings.app_name)

    app.include_router(health_router)
    app.include_router(jobs_router)
    app.include_router(outputs_router)

    return app


app = create_app()
