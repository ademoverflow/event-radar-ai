# Phase 2: Phantombuster Integration

**Status:** Completed

## Overview

Integrated Phantombuster API for LinkedIn scraping. Created services for API communication and LinkedIn data extraction, plus background jobs for automated crawling.

## Services Created

### PhantombusterClient

**File:** `core/src/core/services/phantombuster.py`

Low-level client for Phantombuster API communication.

```python
class PhantombusterClient:
    BASE_URL = "https://api.phantombuster.com/api/v1"
    BASE_URL_V2 = "https://api.phantombuster.com/api/v2"

    async def get_user(self) -> dict[str, Any]
    async def get_agent(self, agent_id: str) -> dict[str, Any]
    async def launch_agent(self, agent_id: str, argument: dict | None) -> str
    async def get_agent_output(self, agent_id: str) -> AgentOutput
    async def fetch_result_object(self, agent_id: str) -> dict | None
    async def launch_and_wait(
        self,
        agent_id: str,
        argument: dict | None = None,
        timeout_seconds: int = 300,
        poll_interval_seconds: int = 10,
    ) -> AgentOutput
```

**Key Features:**
- Async HTTP client with httpx
- Supports both API v1 and v2 endpoints
- Polling mechanism for agent completion
- Timeout handling with `PhantombusterTimeoutError`
- Error handling with `PhantombusterAgentError`

### LinkedInScraper

**File:** `core/src/core/services/linkedin_scraper.py`

High-level service for LinkedIn data extraction.

```python
class LinkedInScraper:
    def __init__(
        self,
        api_key: str | None = None,
        profile_posts_agent_id: str | None = None,
        search_posts_agent_id: str | None = None,
    )

    async def scrape_profile_posts(
        self,
        profile_url: str,
        max_posts: int = 20,
    ) -> list[LinkedInPostData]

    async def scrape_search_posts(
        self,
        search_term: str,
        *,
        is_hashtag: bool = False,
        max_posts: int = 20,
    ) -> list[LinkedInPostData]
```

**Data Classes:**

```python
@dataclass
class LinkedInPostData:
    post_id: str
    author_name: str
    author_url: str
    content: str
    posted_at: datetime | None
    raw_data: dict[str, Any]

@dataclass
class LinkedInProfileData:
    profile_url: str
    name: str
    headline: str | None
    description: str | None
    raw_data: dict[str, Any]
```

**Key Features:**
- Parses various Phantombuster response formats
- Handles both list and dict result structures
- Extracts post IDs from multiple possible fields
- Parses dates from Unix timestamps and ISO strings
- Graceful error handling per post

## Background Jobs

**File:** `core/src/core/scheduler/jobs.py`

### crawl_profiles_job

Runs every **15 minutes** to check for profiles due for crawling.

```python
async def crawl_profiles_job() -> None:
    """Background job to crawl monitored LinkedIn profiles."""
```

**Logic:**
1. Skip if Phantombuster API key or agent ID not configured
2. Query profiles where:
   - `is_active == True`
   - `last_crawled_at IS NULL` OR `last_crawled_at < now - 1 hour`
3. For each profile, check if `crawl_frequency_hours` has elapsed
4. Scrape posts and store new ones
5. Update `last_crawled_at` timestamp

### crawl_searches_job

Runs every **30 minutes** to check for searches due for crawling.

```python
async def crawl_searches_job() -> None:
    """Background job to search LinkedIn for keyword/hashtag matches."""
```

**Logic:**
1. Skip if Phantombuster API key or agent ID not configured
2. Query searches where:
   - `is_active == True`
   - `last_crawled_at IS NULL` OR `last_crawled_at < now - 1 hour`
3. For each search, scrape posts (keyword or hashtag based on `search_type`)
4. Store new posts and update `last_crawled_at`

### Helper Functions

```python
def _get_scraper() -> LinkedInScraper
async def _store_posts(
    session: AsyncSession,
    posts: list[LinkedInPostData],
    profile_id: str | None = None,
    search_id: str | None = None,
) -> int  # Returns count of new posts stored

def register_jobs(scheduler: AsyncIOScheduler) -> None
```

## Database Changes

**File:** `core/src/core/database.py`

Added session factory for background jobs:

```python
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
```

## Exception Hierarchy

```
PhantombusterError (base)
├── PhantombusterAgentError (agent execution failed)
└── PhantombusterTimeoutError (agent timed out)

LinkedInScraperError (base)
└── (wraps PhantombusterError in scraper context)
```

## Files Created/Modified

| File | Action |
|------|--------|
| `core/src/core/services/__init__.py` | Created - exports all services |
| `core/src/core/services/phantombuster.py` | Created - API client |
| `core/src/core/services/linkedin_scraper.py` | Created - scraper service |
| `core/src/core/scheduler/jobs.py` | Updated - added crawl jobs |
| `core/src/core/database.py` | Updated - added session factory |

## Environment Variables Required

```env
PHANTOMBUSTER_API_KEY=your_api_key
PHANTOMBUSTER_PROFILE_POSTS_AGENT_ID=your_profile_agent_id
PHANTOMBUSTER_SEARCH_POSTS_AGENT_ID=your_search_agent_id
```

## Usage Example

```python
from core.services import LinkedInScraper

scraper = LinkedInScraper()

# Scrape profile posts
posts = await scraper.scrape_profile_posts(
    profile_url="https://linkedin.com/in/someone",
    max_posts=10,
)

# Search posts by keyword
posts = await scraper.scrape_search_posts(
    search_term="AI conference",
    is_hashtag=False,
    max_posts=20,
)

# Search posts by hashtag
posts = await scraper.scrape_search_posts(
    search_term="TechEvent2026",
    is_hashtag=True,
    max_posts=20,
)
```
