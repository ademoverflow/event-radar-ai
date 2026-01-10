from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]

from core.logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


async def start_scheduler() -> None:
    """Start the APScheduler."""
    scheduler.start()
    logger.info("APScheduler started")


async def stop_scheduler() -> None:
    """Stop the APScheduler gracefully."""
    scheduler.shutdown(wait=True)
    logger.info("APScheduler stopped")
