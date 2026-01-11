from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from sqlmodel import col, select

from core.database import async_session_factory
from core.logger import get_logger
from core.models import LinkedInMonitoredProfile, LinkedInPost, LinkedInSearch, LinkedInSignal
from core.services.linkedin_scraper import LinkedInPostData, LinkedInScraper, LinkedInScraperError
from core.services.llm import LLMService, LLMServiceError, SignalExtraction
from core.settings import get_settings

if TYPE_CHECKING:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore[import-untyped]
    from sqlalchemy.ext.asyncio import AsyncSession

logger = get_logger(__name__)
settings = get_settings()

# Minimum relevance score to create a signal for non-event posts
MIN_RELEVANCE_SCORE_FOR_SIGNAL = 0.3


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


async def _get_user_id_for_post(
    session: AsyncSession,
    post: LinkedInPost,
) -> str | None:
    """Get the user_id associated with a post via its profile or search.

    Args:
        session: Database session
        post: The post to get user_id for

    Returns:
        User ID as string, or None if not found

    """
    if post.profile_id:
        result = await session.execute(
            select(col(LinkedInMonitoredProfile.user_id)).where(
                col(LinkedInMonitoredProfile.id) == post.profile_id
            )
        )
        user_id = result.scalar_one_or_none()
        if user_id:
            return str(user_id)

    if post.search_id:
        result = await session.execute(
            select(col(LinkedInSearch.user_id)).where(col(LinkedInSearch.id) == post.search_id)
        )
        user_id = result.scalar_one_or_none()
        if user_id:
            return str(user_id)

    return None


async def _create_signal_from_extraction(
    session: AsyncSession,
    post: LinkedInPost,
    user_id: str,
    extraction: SignalExtraction,
) -> LinkedInSignal:
    """Create a LinkedInSignal from an LLM extraction result.

    Args:
        session: Database session
        post: The source post
        user_id: The user ID to associate with the signal
        extraction: The extracted signal data from LLM

    Returns:
        The created LinkedInSignal

    """
    signal = LinkedInSignal(
        user_id=user_id,  # type: ignore[arg-type]
        post_id=str(post.id),  # type: ignore[arg-type]
        event_type=extraction.event_type,
        event_timing=extraction.event_timing,
        event_date=extraction.event_date,
        event_date_inferred=extraction.date_is_inferred,
        companies_mentioned=extraction.companies_mentioned,
        people_mentioned=extraction.people_mentioned,
        relevance_score=extraction.relevance_score,
        summary=extraction.summary,
        raw_llm_response=extraction.model_dump(mode="json"),
    )
    session.add(signal)
    return signal


async def analyze_single_post(
    post: LinkedInPost,
    session: AsyncSession,
    llm_service: LLMService | None = None,
) -> LinkedInSignal | None:
    """Analyze a single post for event signals using LLM.

    Args:
        post: The post to analyze
        session: Database session
        llm_service: Optional LLM service instance (will create one if not provided)

    Returns:
        The created signal if an event was detected, None otherwise

    Raises:
        LLMServiceError: If LLM extraction fails
        ValueError: If user_id cannot be determined for the post

    """
    # Get user_id for this post
    user_id = await _get_user_id_for_post(session, post)
    if not user_id:
        msg = f"Could not determine user_id for post {post.id}"
        raise ValueError(msg)

    # Store values before any potential commits
    post_id = str(post.id)
    post_content = post.content
    author_name = post.author_name

    # Initialize LLM service if not provided
    if llm_service is None:
        llm_service = LLMService()

    logger.info(
        "Analyzing post for signals",
        extra={"post_id": post_id, "author": author_name},
    )

    # Extract signal from post content
    extraction = await llm_service.extract_signal(
        post_content=post_content,
        author_name=author_name,
    )

    if extraction is None:
        logger.warning(
            "LLM extraction returned None",
            extra={"post_id": post_id},
        )
        return None

    # Only create signal if event-related or has meaningful relevance
    is_not_relevant = extraction.relevance_score < MIN_RELEVANCE_SCORE_FOR_SIGNAL
    if not extraction.is_event_related and is_not_relevant:
        logger.debug(
            "Post not event-related, skipping signal creation",
            extra={"post_id": post_id, "relevance_score": extraction.relevance_score},
        )
        return None

    signal = await _create_signal_from_extraction(
        session=session,
        post=post,
        user_id=user_id,
        extraction=extraction,
    )

    await session.commit()

    logger.info(
        "Created signal for post",
        extra={
            "post_id": post_id,
            "signal_id": str(signal.id),
            "event_type": extraction.event_type,
            "relevance_score": extraction.relevance_score,
        },
    )

    return signal


async def analyze_posts_job() -> None:
    """Background job to analyze unprocessed posts for event signals.

    This job runs periodically to process posts that haven't been
    analyzed by the LLM yet. It finds posts without associated signals
    and extracts event information from them.
    """
    logger.info("Starting post analysis job")

    if not settings.openai_api_key:
        logger.warning("OpenAI API key not configured, skipping post analysis")
        return

    async with async_session_factory() as session:
        # Find posts that don't have signals yet
        # Using a subquery to find post_ids that already have signals
        existing_signal_post_ids = select(col(LinkedInSignal.post_id))

        # Select posts not in that list, ordered by created_at desc (newest first)
        statement = (
            select(LinkedInPost)
            .where(col(LinkedInPost.id).notin_(existing_signal_post_ids))
            .order_by(col(LinkedInPost.created_at).desc())
            .limit(50)  # Process max 50 posts per job run to avoid timeout
        )

        result = await session.execute(statement)
        posts = result.scalars().all()

        if not posts:
            logger.info("No posts pending analysis")
            return

        logger.info(f"Found {len(posts)} posts to analyze")

        # Create a shared LLM service instance
        llm_service = LLMService()
        signals_created = 0
        errors = 0

        for post in posts:
            try:
                signal = await analyze_single_post(
                    post=post,
                    session=session,
                    llm_service=llm_service,
                )
                if signal:
                    signals_created += 1

            except (LLMServiceError, ValueError) as e:
                errors += 1
                logger.warning(
                    f"Failed to analyze post: {e}",
                    extra={"post_id": str(post.id)},
                )
                continue

    logger.info(
        "Post analysis job completed",
        extra={"signals_created": signals_created, "errors": errors},
    )


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

    # Run post analysis every 10 minutes to process new posts for signals
    scheduler.add_job(
        analyze_posts_job,
        trigger="interval",
        minutes=10,
        id="analyze_posts",
        name="Analyze Posts for Signals",
        replace_existing=True,
    )

    logger.info("Registered scheduled jobs")
