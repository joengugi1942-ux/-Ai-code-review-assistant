from fastapi import FastAPI

from app.api.v1 import review_routes, github_routes


def create_app() -> FastAPI:
    app = FastAPI(title="AI Code Review Assistant", version="0.1.0")

    # Routers
    app.include_router(review_routes.router, prefix="/api/v1/review", tags=["review"])
    app.include_router(github_routes.router, prefix="/api/v1/github", tags=["github"])

    return app


app = create_app()



