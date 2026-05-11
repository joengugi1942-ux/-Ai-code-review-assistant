from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import admin_routes, github_routes, review_routes, conversation_routes
from app.core.config import settings
from app.db.database import Base, engine
from app.db import models  # noqa: F401 - ensure models are registered

logger.add("logs/app.log", rotation="10 MB", retention="7 days", level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting application...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Application started successfully")
    yield
    # Close persistent httpx client in GithubService singleton
    from app.api.deps import get_github_service
    svc = get_github_service()
    await svc.github_client.aclose()
    await engine.dispose()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Code Review Assistant",
        version="0.1.0",
        debug=settings.app_env == "development",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(review_routes.router, prefix="/api/v1/review", tags=["review"])
    app.include_router(github_routes.router, prefix="/api/v1/github", tags=["github"])
    app.include_router(admin_routes.router, prefix="/api/v1/admin", tags=["admin"])
    app.include_router(conversation_routes.router, prefix="/api/v1", tags=["conversations"])

    return app


app = create_app()
