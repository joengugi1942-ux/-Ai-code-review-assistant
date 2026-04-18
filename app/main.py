from fastapi import FastAPI
from loguru import logger

from app.api.v1 import admin_routes, github_routes, review_routes
from app.core.config import settings
from app.db.database import Base, engine
from app.db import models  # noqa: F401 - ensure models are registered

logger.add("logs/app.log", rotation="10 MB", retention="7 days", level="INFO")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Code Review Assistant",
        version="0.1.0",
        debug=settings.app_env == "development",
    )

    # Routers
    app.include_router(review_routes.router, prefix="/api/v1/review", tags=["review"])
    app.include_router(github_routes.router, prefix="/api/v1/github", tags=["github"])
    app.include_router(admin_routes.router, prefix="/api/v1/admin", tags=["admin"])

    # Startup event - create DB tables
    @app.on_event("startup")
    async def create_tables() -> None:
        logger.info("Starting application...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Application started successfully")

    return app


app = create_app()
