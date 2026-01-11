from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.models.serializer import deserialize, serialize
from core.settings import get_settings

settings = get_settings()
async_db_url = settings.database_url.replace("postgresql", "postgresql+asyncpg")

engine = create_async_engine(async_db_url, json_serializer=serialize, json_deserializer=deserialize)

# Session factory for use outside of FastAPI dependency injection (e.g., background jobs)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession]:
    """Get a session for FastAPI dependency injection."""
    async with AsyncSession(engine) as session:
        yield session


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession]:
    """Get a session as an async context manager for use in background jobs."""
    async with async_session_factory() as session:
        yield session
