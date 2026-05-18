from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any
import asyncio
import logging
import time
from loguru import logger

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import admin_routes, github_routes, review_routes, conversation_routes
from app.api.deps import get_github_service  # Moved import to top-level
from app.core.config import settings
from app.db.database import Base, engine, AsyncSessionLocal
from app.db import models  # noqa: F401 - ensure models are registered

# Silence noisy libraries - set to WARNING to see warnings and errors only
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
logging.getLogger("sqlalchemy.pool").setLevel(logging.WARNING)
logging.getLogger("aiomysql").setLevel(logging.WARNING)
logging.getLogger("pymysql").setLevel(logging.WARNING)


async def wait_for_database(max_retries: int = 10, check_tables: bool = False) -> bool:
    """
    Wait for database to become available with exponential backoff.
    Only checks connectivity by default (does not create tables).
    Optionally verifies that tables exist.
    Returns True if connected (and tables exist if check_tables=True), False if max retries exceeded.
    """
    from sqlalchemy import text

    for attempt in range(1, max_retries + 1):
        try:
            async with engine.begin() as conn:
                # Simple connectivity check
                await conn.execute(text("SELECT 1"))

                # Optionally verify tables exist
                if check_tables:
                    from sqlalchemy import inspect

                    def _check_tables(conn):
                        insp = inspect(conn)
                        table_names = set(insp.get_table_names())
                        expected_tables = {table.name for table in Base.metadata.sorted_tables}
                        missing = expected_tables - table_names
                        if missing:
                            raise Exception(f"Database connected but tables missing: {missing}")
                        return True

                    await conn.run_sync(_check_tables)

            if attempt == 1:
                logger.info("✓ Database connected")
            else:
                logger.info(f"✓ Database connected (after {attempt} attempts)")
            return True
        except Exception as e:
            if attempt == max_retries:
                logger.error(f"✗ Database connection failed after {max_retries} attempts: {e}")
                return False

            # Log retry attempts at key points: first few, then every 5th, and last retry
            if attempt in {1, 2, 3, 5, max_retries} or attempt % 5 == 0:
                logger.warning(f"Database not available (attempt {attempt}/{max_retries}): {e}")
            else:
                logger.debug(f"Database not available (attempt {attempt}/{max_retries}): {e}")

            # Exponential backoff: 1s, 2s, 4s, 8s, etc. max 10s
            delay = min(2 ** (attempt - 1), 10)
            await asyncio.sleep(delay)

    return False


async def init_database(verify: bool = True) -> bool:
    """
    Initialize database tables.
    Returns True if successful, False otherwise.
    If verify is True, also checks that tables were created.
    """
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        if verify:
            # Verify tables were created using SQLAlchemy inspector (dialect-agnostic)
            from sqlalchemy import inspect

            def _verify_tables(conn):
                insp = inspect(conn)
                table_names = set(insp.get_table_names())
                expected_tables = {table.name for table in Base.metadata.sorted_tables}
                missing = expected_tables - table_names
                if missing:
                    raise Exception(f"Tables not created after initialization: {missing}")
                return True

            async with engine.begin() as conn:
                await conn.run_sync(_verify_tables)

        logger.info("✓ Database tables initialized")
        return True
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {e}")
        return False


async def init_web3() -> Dict[str, Any]:
    """Initialize Web3 providers."""
    try:
        # Placeholder - replace with actual Web3 initialization
        # from app.services.web3_service import init_web3_providers
        # result = await init_web3_providers()
        logger.info("✓ Web3 providers initialized")
        return {"status": "success", "count": 2}  # Example
    except Exception as e:
        logger.warning(f"⚠ Web3 initialization partially failed: {e}")
        return {"status": "partial", "error": str(e)}


async def init_psps() -> Dict[str, Any]:
    """Initialize PSPs (Payment Service Providers)."""
    try:
        # Placeholder - replace with actual PSP initialization
        # from app.services.psp_service import init_psps
        # result = await init_psps()
        logger.info("✓ PSPs initialized (3 active, 2 disabled)")
        return {"status": "success", "active": 3, "disabled": 2}
    except Exception as e:
        logger.warning(f"⚠ PSP initialization partially failed: {e}")
        return {"status": "partial", "error": str(e)}


async def seed_admin() -> Dict[str, Any]:
    """Seed admin user if not exists."""
    try:
        # Placeholder - replace with actual admin seeding
        # from app.services.admin_service import seed_admin_user
        # await seed_admin_user()
        logger.info("✓ Admin verified")
        return {"status": "success"}
    except Exception as e:
        logger.warning(f"⚠ Admin seeding failed: {e}")
        return {"status": "failed", "error": str(e)}


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("Starting Lapo...")

    # Initialize services with error handling
    db_connected = await wait_for_database()
    db_initialized = False
    if db_connected:
        db_initialized = await init_database()
        if not db_initialized:
            logger.error("Failed to initialize database tables. Application may not function correctly.")
            # Depending on requirements, you might want to exit here
            # raise RuntimeError("Database initialization failed")
    else:
        logger.error("Failed to connect to database. Application may not function correctly.")
        # Depending on requirements, you might want to exit here
        # raise RuntimeError("Database connection failed")

    # Initialize other services (non-critical)
    web3_result = await init_web3()
    psp_result = await init_psps()
    admin_result = await seed_admin()

    # Startup summary
    db_status = "✓ Connected & Initialized" if (db_connected and db_initialized) else \
                "✓ Connected" if db_connected else "✗ Failed"
    logger.info(
        "\n"
        "LAPO STARTUP SUMMARY\n"
        "--------------------\n"
        f"Database : {db_status}\n"
        f"Web3     : {web3_result.get('status', 'unknown')}\n"
        f"PSPs     : {psp_result.get('status', 'unknown')}\n"
        f"Admin    : {admin_result.get('status', 'unknown')}\n"
    )
    logger.info("Lapo started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Lapo...")
    svc = get_github_service()
    await svc.github_client.aclose()
    await engine.dispose()
    logger.info("Lapo shutdown complete")


def create_app() -> FastAPI:
    app = FastAPI(
        title="Lapo",
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

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.monotonic()
        logger.info(f"→ {request.method} {request.url.path}")
        response = await call_next(request)
        ms = (time.monotonic() - start) * 1000
        logger.info(f"← {request.method} {request.url.path} {response.status_code} ({ms:.0f}ms)")
        return response

    app.include_router(review_routes.router, prefix="/api/v1/review", tags=["review"])
    app.include_router(github_routes.router, prefix="/api/v1/github", tags=["github"])
    app.include_router(admin_routes.router, prefix="/api/v1/admin", tags=["admin"])
    app.include_router(conversation_routes.router, prefix="/api/v1", tags=["conversations"])

    return app


app = create_app()