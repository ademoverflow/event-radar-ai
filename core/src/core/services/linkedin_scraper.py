from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from core.logger import get_logger
from core.services.phantombuster import (
    PhantombusterClient,
    PhantombusterError,
)
from core.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class LinkedInScraperError(Exception):
    """Base exception for LinkedIn scraper errors."""


@dataclass
class LinkedInPostData:
    """Structured data for a LinkedIn post."""

    post_id: str
    author_name: str
    author_url: str
    content: str
    posted_at: datetime | None
    likes_count: int
    comments_count: int
    raw_data: dict[str, Any]


@dataclass
class LinkedInProfileData:
    """Structured data for a LinkedIn profile."""

    profile_url: str
    full_name: str
    headline: str | None
    company: str | None
    location: str | None
    raw_data: dict[str, Any]


class LinkedInScraper:
    """Service for scraping LinkedIn content via Phantombuster.

    This service provides methods to scrape:
    - Profile posts (for monitored profiles)
    - Search results (for keyword/hashtag discovery)

    Phantombuster Agent IDs should be configured in the Phantombuster dashboard
    and their IDs stored in environment variables or settings.
    """

    def __init__(
        self,
        phantombuster_client: PhantombusterClient | None = None,
        profile_posts_agent_id: str | None = None,
        search_posts_agent_id: str | None = None,
    ) -> None:
        """Initialize LinkedIn scraper.

        Args:
            phantombuster_client: Phantombuster client instance
            profile_posts_agent_id: Agent ID for profile posts scraper
            search_posts_agent_id: Agent ID for search/hashtag scraper

        """
        self.client = phantombuster_client or PhantombusterClient()
        self.profile_posts_agent_id = profile_posts_agent_id
        self.search_posts_agent_id = search_posts_agent_id

    async def scrape_profile_posts(
        self,
        profile_url: str,
        max_posts: int = 20,
        session_cookie: str | None = None,
        user_agent: str | None = None,
    ) -> list[LinkedInPostData]:
        """Scrape recent posts from a LinkedIn profile.

        Args:
            profile_url: LinkedIn profile URL
            max_posts: Maximum number of posts to retrieve
            session_cookie: LinkedIn li_at session cookie. If provided,
                          it will be injected into the phantom arguments.
                          This overrides any cookie saved in PhantomBuster.
            user_agent: Browser user agent string. Required by PhantomBuster
                       to mimic a real browser. Get yours from browser DevTools.

        Returns:
            List of post data

        Raises:
            LinkedInScraperError: If scraping fails

        """
        if not self.profile_posts_agent_id:
            msg = (
                "Profile posts agent ID not configured. "
                "Set up a LinkedIn Profile Posts Scraper in Phantombuster "
                "and configure the agent ID."
            )
            raise LinkedInScraperError(msg)

        try:
            # Arguments for LinkedIn Activity Extractor phantom
            argument: dict[str, Any] = {
                "spreadsheetUrl": profile_url,
                "numberMaxOfPosts": max_posts,
            }

            # Inject session cookie if provided
            if session_cookie:
                argument["sessionCookie"] = session_cookie

            # Inject user agent if provided
            if user_agent:
                argument["userAgent"] = user_agent

            output = await self.client.launch_and_wait(
                agent_id=self.profile_posts_agent_id,
                argument=argument,
                timeout_seconds=300,
            )

            if not output.result_object:
                logger.warning(
                    "No result object from profile posts scraper",
                    extra={"profile_url": profile_url},
                )
                return []

            return self._parse_posts(output.result_object)

        except PhantombusterError as e:
            msg = f"Failed to scrape profile posts: {e}"
            raise LinkedInScraperError(msg) from e

    async def scrape_search_posts(
        self,
        search_term: str,
        *,
        is_hashtag: bool = False,
        max_posts: int = 20,
        session_cookie: str | None = None,
        user_agent: str | None = None,
    ) -> list[LinkedInPostData]:
        """Scrape posts matching a search term or hashtag.

        Args:
            search_term: Keyword or hashtag to search for
            is_hashtag: Whether the term is a hashtag
            max_posts: Maximum number of posts to retrieve
            session_cookie: LinkedIn li_at session cookie. If provided,
                          it will be injected into the phantom arguments.
            user_agent: Browser user agent string. Required by PhantomBuster
                       to mimic a real browser.

        Returns:
            List of post data

        Raises:
            LinkedInScraperError: If scraping fails

        """
        if not self.search_posts_agent_id:
            msg = (
                "Search posts agent ID not configured. "
                "Set up a LinkedIn Search Posts Scraper in Phantombuster "
                "and configure the agent ID."
            )
            raise LinkedInScraperError(msg)

        # Format hashtag if needed
        formatted_term = (
            f"#{search_term}" if is_hashtag and not search_term.startswith("#") else search_term
        )

        try:
            argument: dict[str, Any] = {
                "searchTerm": formatted_term,
                "numberOfPosts": max_posts,
            }

            # Inject session cookie if provided
            if session_cookie:
                argument["sessionCookie"] = session_cookie

            # Inject user agent if provided
            if user_agent:
                argument["userAgent"] = user_agent

            output = await self.client.launch_and_wait(
                agent_id=self.search_posts_agent_id,
                argument=argument,
                timeout_seconds=300,
            )

            if not output.result_object:
                logger.warning(
                    "No result object from search posts scraper",
                    extra={"search_term": formatted_term},
                )
                return []

            return self._parse_posts(output.result_object)

        except PhantombusterError as e:
            msg = f"Failed to scrape search posts: {e}"
            raise LinkedInScraperError(msg) from e

    def _parse_posts(
        self, result_object: list[dict[str, Any]] | dict[str, Any]
    ) -> list[LinkedInPostData]:
        """Parse Phantombuster result into structured post data.

        Args:
            result_object: Raw result from Phantombuster

        Returns:
            List of parsed post data

        """
        posts: list[LinkedInPostData] = []

        # Handle both list and dict formats from Phantombuster
        raw_posts: list[dict[str, Any]]
        if isinstance(result_object, list):
            raw_posts = result_object
        elif isinstance(result_object, dict):
            posts_data = result_object.get("posts") or result_object.get("results") or []
            raw_posts = posts_data if isinstance(posts_data, list) else []
        else:
            logger.warning("Unexpected result format from Phantombuster")
            return []

        for raw_post in raw_posts:
            try:
                post = self._parse_single_post(raw_post)
                if post:
                    posts.append(post)
            except (KeyError, ValueError, TypeError) as e:
                logger.warning(
                    "Failed to parse post",
                    extra={"error": str(e), "raw_post": raw_post},
                )
                continue

        logger.info(f"Parsed {len(posts)} posts from Phantombuster result")
        return posts

    def _parse_single_post(self, raw_post: dict[str, Any]) -> LinkedInPostData | None:
        """Parse a single post from Phantombuster data.

        Args:
            raw_post: Raw post data from Phantombuster

        Returns:
            Parsed post data or None if invalid

        """
        # Extract post ID - various formats from Phantombuster
        # Priority: explicit ID fields, then extract from postUrl
        post_id = (
            raw_post.get("postId")
            or raw_post.get("activityId")
            or raw_post.get("urn")
            or raw_post.get("id")
        )

        # If no explicit ID, try to extract from postUrl
        # Format: https://www.linkedin.com/feed/update/urn:li:activity:7414651074265153536
        if not post_id:
            post_url = raw_post.get("postUrl", "")
            if "urn:li:activity:" in post_url:
                post_id = post_url.split("urn:li:activity:")[-1].split("?")[0]
            elif post_url:
                # Use the URL itself as a fallback ID
                post_id = post_url

        if not post_id:
            return None

        # Extract author info
        # Note: "author" can be a string or a dict depending on PhantomBuster phantom
        author_field = raw_post.get("author")
        author_from_field = (
            author_field
            if isinstance(author_field, str)
            else author_field.get("name")
            if isinstance(author_field, dict)
            else None
        )
        author_name = (
            raw_post.get("authorName")
            or raw_post.get("profileName")
            or author_from_field
            or raw_post.get("posterName")
            or "Unknown"
        )

        author_url_from_field = (
            author_field.get("profileUrl") if isinstance(author_field, dict) else None
        )
        author_url = (
            raw_post.get("authorUrl")
            or raw_post.get("authorProfileUrl")
            or raw_post.get("profileUrl")
            or author_url_from_field
            or raw_post.get("posterProfileUrl")
            or ""
        )

        # Extract content
        content = (
            raw_post.get("postContent") or raw_post.get("text") or raw_post.get("content") or ""
        )

        # Parse posted date
        posted_at: datetime | None = None
        date_str = (
            raw_post.get("postDate")
            or raw_post.get("postedAt")
            or raw_post.get("date")
            or raw_post.get("timestamp")
        )
        if date_str:
            try:
                if isinstance(date_str, int):
                    posted_at = datetime.fromtimestamp(date_str / 1000, tz=UTC)  # Unix ms
                else:
                    posted_at = datetime.fromisoformat(date_str)
            except (ValueError, TypeError):
                pass

        # Extract engagement counts - handle various field names
        likes_count = (
            raw_post.get("likeCount") or raw_post.get("likesCount") or raw_post.get("likes") or 0
        )
        comments_count = (
            raw_post.get("commentCount")
            or raw_post.get("commentsCount")
            or raw_post.get("comments")
            or 0
        )

        return LinkedInPostData(
            post_id=str(post_id),
            author_name=author_name,
            author_url=author_url,
            content=content,
            posted_at=posted_at,
            likes_count=int(likes_count) if likes_count else 0,
            comments_count=int(comments_count) if comments_count else 0,
            raw_data=raw_post,
        )

    async def scrape_profile_info(self, profile_url: str) -> LinkedInProfileData | None:
        """Scrape basic info from a LinkedIn profile.

        This is useful for validating profile URLs and getting display names.

        Args:
            profile_url: LinkedIn profile URL

        Returns:
            Profile data or None if scraping fails

        """
        # This would use the LinkedIn Profile Scraper Phantom
        # For now, return None as it requires a separate agent setup
        logger.info(
            "Profile info scraping not implemented yet",
            extra={"profile_url": profile_url},
        )
        return None
