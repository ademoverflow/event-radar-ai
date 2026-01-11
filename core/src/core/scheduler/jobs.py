from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import select

from core.database import async_session_factory
from core.logger import get_logger
from core.models import LinkedInMonitoredProfile, LinkedInPost
from core.services.linkedin_scraper import LinkedInPostData, LinkedInScraper, LinkedInScraperError
from core.settings import get_settings

if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)
settings = get_settings()


def _get_scraper() -> LinkedInScraper:
    """Create a LinkedIn scraper instance with configured agent IDs."""
    return LinkedInScraper(
        profile_posts_agent_id=settings.phantombuster_profile_posts_agent_id or None,
    )


async def _store_posts(
    session: AsyncSession,
    posts: list[LinkedInPostData],
    profile_id: str | None = None,
    search_id: str | None = None,
) -> int:
    """Store scraped posts in the database.

    Args:
        session: Database session
        posts: List of scraped posts
        profile_id: Optional profile ID that sourced these posts
        search_id: Optional search ID that sourced these posts

    Returns:
        Number of new posts stored

    """
    stored_count = 0

    for post_data in posts:
        # Check if post already exists
        existing = await session.execute(
            select(LinkedInPost).where(
                LinkedInPost.linkedin_post_id == post_data.post_id  # type: ignore[arg-type]
            )
        )
        if existing.scalar_one_or_none():
            continue

        # Create new post
        post = LinkedInPost(
            profile_id=profile_id,  # type: ignore[arg-type]
            search_id=search_id,  # type: ignore[arg-type]
            linkedin_post_id=post_data.post_id,
            author_name=post_data.author_name,
            author_linkedin_url=post_data.author_url,
            content=post_data.content,
            posted_at=post_data.posted_at or datetime.now(UTC),
            raw_data=post_data.raw_data,
        )
        session.add(post)
        stored_count += 1

    if stored_count > 0:
        await session.commit()

    return stored_count


async def crawl_single_profile(
    profile: LinkedInMonitoredProfile,
    session: AsyncSession,
) -> int:
    """Crawl a single LinkedIn profile and store the posts.

    Args:
        profile: The profile to crawl
        session: Database session

    Returns:
        Number of new posts stored

    Raises:
        LinkedInScraperError: If scraping fails
        ValueError: If required settings are missing

    """
    if not settings.phantombuster_api_key:
        msg = "Phantombuster API key not configured"
        raise ValueError(msg)

    if not settings.phantombuster_profile_posts_agent_id:
        msg = "Profile posts agent ID not configured"
        raise ValueError(msg)

    if not settings.linkedin_session_cookie:
        msg = "LinkedIn session cookie not configured"
        raise ValueError(msg)

    scraper = _get_scraper()

    # Store values before any commits that might invalidate the session state
    profile_id = str(profile.id)
    profile_url = profile.url
    profile_display_name = profile.display_name

    logger.info(
        f"Crawling profile: {profile_display_name}",
        extra={"profile_id": profile_id, "url": profile_url},
    )

    posts = await scraper.scrape_profile_posts(
        profile_url=profile_url,
        max_posts=settings.max_posts_per_crawl,
        session_cookie=settings.linkedin_session_cookie,
        user_agent=settings.linkedin_user_agent or None,
    )

    stored = await _store_posts(
        session=session,
        posts=posts,
        profile_id=profile_id,
    )

    # Update last_crawled_at
    profile.last_crawled_at = datetime.now(UTC)
    await session.commit()

    logger.info(
        f"Stored {stored} new posts from profile {profile_display_name}",
        extra={"profile_id": profile_id},
    )

    return stored


async def crawl_profiles_job() -> None:
    """Background job to crawl monitored LinkedIn profiles.

    This job runs periodically to fetch new posts from profiles
    that are due for crawling based on their configured frequency.
    """
    logger.info("Starting profile crawl job")

    if not settings.phantombuster_api_key:
        logger.warning("Phantombuster API key not configured, skipping profile crawl")
        return

    if not settings.phantombuster_profile_posts_agent_id:
        logger.warning("Profile posts agent ID not configured, skipping profile crawl")
        return

    if not settings.linkedin_session_cookie:
        logger.warning("LinkedIn session cookie not configured, skipping profile crawl")
        return

    async with async_session_factory() as session:
        # Find profiles due for crawling
        now = datetime.now(UTC)
        statement = select(LinkedInMonitoredProfile).where(
            LinkedInMonitoredProfile.is_active == True,  # type: ignore[arg-type] # noqa: E712
            (
                (LinkedInMonitoredProfile.last_crawled_at == None)  # type: ignore[arg-type] # noqa: E711
                | (
                    LinkedInMonitoredProfile.last_crawled_at  # type: ignore[operator]
                    < now - timedelta(hours=1)  # Use 1 hour as minimum interval
                )
            ),
        )
        result = await session.execute(statement)
        profiles = result.scalars().all()

        if not profiles:
            logger.info("No profiles due for crawling")
            return

        logger.info(f"Found {len(profiles)} profiles to crawl")

        for profile in profiles:
            try:
                # Check if enough time has passed based on profile's frequency
                if profile.last_crawled_at:
                    next_crawl = profile.last_crawled_at + timedelta(
                        hours=profile.crawl_frequency_hours
                    )
                    if now < next_crawl:
                        continue

                await crawl_single_profile(profile, session)

            except (LinkedInScraperError, ValueError):
                logger.exception(
                    f"Failed to crawl profile {profile.display_name}",
                    extra={"profile_id": str(profile.id)},
                )
                continue

    logger.info("Profile crawl job completed")


async def crawl_searches_job() -> None:
    """Background job to search LinkedIn for keyword/hashtag matches.

    This job runs periodically to discover new posts matching
    user-configured keywords and hashtags.

    Note: Search crawling is disabled until a search posts agent is configured.
    """
    logger.info("Starting search crawl job")

    # Search crawling not yet implemented - requires separate PhantomBuster agent
    logger.info("Search crawl job skipped - not yet implemented")


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

    # Run search crawl every 30 minutes
    scheduler.add_job(
        crawl_searches_job,
        trigger="interval",
        minutes=30,
        id="crawl_searches",
        name="Crawl LinkedIn Searches",
        replace_existing=True,
    )

    logger.info("Registered scheduled jobs")

    logger.info("Registered scheduled jobs")
