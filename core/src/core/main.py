from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import __version__
from core.routers import auth_router, health_router, users_router
from core.scheduler import scheduler, start_scheduler, stop_scheduler
from core.scheduler.jobs import register_jobs
from core.settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator:
    """Lifespan of the application.

    Args:
        app (FastAPI): FastAPI application instance.

    Returns:
        AsyncIterator: Async context manager for lifespan.

    """
    config = Config("core/src/core/alembic/alembic.ini")
    command.upgrade(config, "head")

    # Start the background scheduler
    register_jobs(scheduler)
    await start_scheduler()

    yield

    # Stop the scheduler on shutdown
    await stop_scheduler()


app = FastAPI(
    title="Event Radar Ai",
    description="Event Radar Ai Core API",
    version=__version__,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.webapp_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(users_router)
