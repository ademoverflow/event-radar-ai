from __future__ import annotations

from typing import TYPE_CHECKING

from core.logger import get_logger

if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]

logger = get_logger(__name__)


async def crawl_profiles_job() -> None:
    """Background job to crawl monitored LinkedIn profiles.

    This job runs periodically to fetch new posts from profiles
    that are due for crawling based on their configured frequency.

    Implementation pending:
    1. Query profiles where last_crawled_at + crawl_frequency_hours < now
    2. For each profile, call LinkedIn scraper
    3. Process new posts through LLM
    4. Store signals
    """
    logger.info("Starting profile crawl job")
    logger.info("Profile crawl job completed")


async def crawl_keywords_job() -> None:
    """Background job to search LinkedIn for keyword/hashtag matches.

    This job runs periodically to discover new posts matching
    user-configured keywords and hashtags.

    Implementation pending:
    1. Query active keywords
    2. For each keyword, search LinkedIn
    3. Process matching posts through LLM
    4. Store signals
    """
    logger.info("Starting keyword crawl job")
    logger.info("Keyword crawl job completed")


def register_jobs(scheduler: AsyncIOScheduler) -> None:
    """Register all scheduled jobs with the scheduler."""
    # Run profile crawl every 15 minutes to check for due profiles
    scheduler.add_job(
        crawl_profiles_job,
        trigger="interval",
        minutes=15,
        id="crawl_profiles",
        name="Crawl LinkedIn Profiles",
        replace_existing=True,
    )

    # Run keyword search every 30 minutes
    scheduler.add_job(
        crawl_keywords_job,
        trigger="interval",
        minutes=30,
        id="crawl_keywords",
        name="Crawl LinkedIn Keywords",
        replace_existing=True,
    )

    logger.info("Registered scheduled jobs")
