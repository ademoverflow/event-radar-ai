# Phase 2: Phantombuster Integration

**Status:** Completed

## Overview

Integrated Phantombuster API for LinkedIn scraping. Created services for API communication and LinkedIn data extraction, plus background jobs for automated crawling. Session credentials (li_at cookie and user agent) are loaded from environment variables.

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

    # Agent management methods
    async def fetch_agent(self, agent_id: str) -> AgentDetails
    async def update_agent_argument(self, agent_id: str, argument: dict) -> None
    async def get_agent_status(self, agent_id: str) -> AgentStatus
    async def fetch_all_agents(self) -> list[AgentSummary]
    async def validate_profile_posts_phantom(self, agent_id: str) -> ValidationResult
```

**Data Classes:**

```python
@dataclass
class AgentOutput:
    container_id: str
    status: str
    output: str | None
    result_object: list[dict[str, Any]] | dict[str, Any] | None

@dataclass
class AgentDetails:
    id: str
    name: str
    script_id: str
    launch_type: str
    last_run_at: datetime | None
    argument: dict[str, Any]

@dataclass
class AgentStatus:
    is_running: bool
    last_status: str
    last_end_time: datetime | None
    time_left_seconds: int

@dataclass
class AgentSummary:
    id: str
    name: str
    script_id: str

@dataclass
class ValidationResult:
    is_valid: bool
    has_session_cookie: bool
    missing_config: list[str]
    warnings: list[str]
```

**Key Features:**
- Async HTTP client with httpx
- Supports both API v1 and v2 endpoints
- Polling mechanism for agent completion
- Timeout handling with `PhantombusterTimeoutError`
- Error handling with `PhantombusterAgentError`
- Agent management (fetch, update, validate)

### LinkedInScraper

**File:** `core/src/core/services/linkedin_scraper.py`

High-level service for LinkedIn data extraction.

```python
class LinkedInScraper:
    def __init__(
        self,
        phantombuster_client: PhantombusterClient | None = None,
        profile_posts_agent_id: str | None = None,
        search_posts_agent_id: str | None = None,
    )

    async def scrape_profile_posts(
        self,
        profile_url: str,
        max_posts: int = 20,
        session_cookie: str | None = None,
        user_agent: str | None = None,
    ) -> list[LinkedInPostData]

    async def scrape_search_posts(
        self,
        search_term: str,
        *,
        is_hashtag: bool = False,
        max_posts: int = 20,
        session_cookie: str | None = None,
        user_agent: str | None = None,
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
    likes_count: int
    comments_count: int
    raw_data: dict[str, Any]

@dataclass
class LinkedInProfileData:
    profile_url: str
    full_name: str
    headline: str | None
    company: str | None
    location: str | None
    raw_data: dict[str, Any]
```

**Key Features:**
- Session cookie and user agent injection via parameters
- Parses various Phantombuster response formats (list or dict)
- Extracts post IDs from `postUrl` (urn:li:activity format)
- Handles `author` field as string or dict
- Parses dates from Unix timestamps and ISO strings
- Extracts engagement counts (likes, comments)
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
1. Skip if Phantombuster API key, agent ID, or LinkedIn session cookie not configured
2. Query profiles where:
   - `is_active == True`
   - `last_crawled_at IS NULL` OR `last_crawled_at < now - 1 hour`
3. For each profile, check if `crawl_frequency_hours` has elapsed
4. Scrape posts with session cookie and user agent from settings
5. Store new posts and update `last_crawled_at` timestamp

### crawl_searches_job

Runs every **30 minutes** - currently disabled (placeholder).

```python
async def crawl_searches_job() -> None:
    """Background job to search LinkedIn for keyword/hashtag matches.

    Note: Search crawling is disabled until a search posts agent is configured.
    """
```

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

## Settings

**File:** `core/src/core/settings.py`

```python
class Settings(BaseSettings):
    # LinkedIn scraper settings (Phantombuster)
    phantombuster_api_key: str = ""
    phantombuster_profile_posts_agent_id: str = ""

    # LinkedIn session credentials (from browser DevTools)
    linkedin_session_cookie: str
    linkedin_user_agent: str

    # Crawling settings
    default_crawl_frequency_hours: int = 24
    max_posts_per_crawl: int = 20
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
| `core/src/core/services/phantombuster.py` | Created - API client with agent management |
| `core/src/core/services/linkedin_scraper.py` | Created - scraper service with cookie injection |
| `core/src/core/scheduler/jobs.py` | Updated - crawl jobs using settings for credentials |
| `core/src/core/database.py` | Updated - added session factory |
| `core/src/core/settings.py` | Updated - added LinkedIn credentials settings |

## Environment Variables Required

```env
# Phantombuster API
PHANTOMBUSTER_API_KEY=your_api_key
PHANTOMBUSTER_PROFILE_POSTS_AGENT_ID=your_agent_id

# LinkedIn session credentials (from browser DevTools)
# li_at cookie: Application -> Cookies -> linkedin.com -> li_at
LINKEDIN_SESSION_COOKIE=your_li_at_cookie
# User-Agent: Network tab -> any request -> Headers -> User-Agent
LINKEDIN_USER_AGENT=Mozilla/5.0...

# Crawling settings
DEFAULT_CRAWL_FREQUENCY_HOURS=24
MAX_POSTS_PER_CRAWL=20
```

## Setup Instructions

### 1. Create PhantomBuster Phantom

1. Go to [phantombuster.com](https://phantombuster.com)
2. Create a new "LinkedIn Profile Posts Extractor" phantom
3. Copy the Agent ID from the URL (e.g., `4678091899725080`)

### 2. Get LinkedIn Credentials

1. Open LinkedIn in your browser
2. Open DevTools (F12)
3. **li_at cookie:** Application -> Cookies -> linkedin.com -> copy `li_at` value
4. **User-Agent:** Network tab -> click any request -> Headers -> copy `User-Agent` value

### 3. Configure Environment

Add to your `.env` file:
```env
PHANTOMBUSTER_API_KEY=your_api_key
PHANTOMBUSTER_PROFILE_POSTS_AGENT_ID=your_agent_id
LINKEDIN_SESSION_COOKIE=AQE...
LINKEDIN_USER_AGENT=Mozilla/5.0...
```

## Usage Example

```python
from core.services import LinkedInScraper, PhantombusterClient

# Using settings (recommended for background jobs)
scraper = LinkedInScraper(
    profile_posts_agent_id="your_agent_id"
)

# Scrape profile posts with cookie injection
posts = await scraper.scrape_profile_posts(
    profile_url="https://linkedin.com/in/someone",
    max_posts=10,
    session_cookie="your_li_at_cookie",
    user_agent="Mozilla/5.0...",
)

for post in posts:
    print(f"{post.author_name}: {post.content[:100]}")
    print(f"  Likes: {post.likes_count}, Comments: {post.comments_count}")
```

## Test Script

**File:** `test_phantombuster.py`

```bash
# Basic API test
uv run python test_phantombuster.py

# Scraping test (consumes PhantomBuster time)
export PHANTOMBUSTER_API_KEY="your_key"
export PHANTOMBUSTER_PROFILE_POSTS_AGENT_ID="your_agent_id"
export LINKEDIN_SESSION_COOKIE="your_li_at"
export LINKEDIN_USER_AGENT="Mozilla/5.0..."
uv run python test_phantombuster.py --scrape https://linkedin.com/in/profile
```

## Limitations & Notes

1. **Phantom Creation:** PhantomBuster API does not support creating phantoms programmatically. User must create the phantom once in the UI, then we manage everything else via API.

2. **Cookie Expiration:** LinkedIn li_at cookies expire periodically. Users need to manually refresh them when scraping fails.

3. **Search Crawling:** Not yet implemented - requires a separate PhantomBuster "LinkedIn Search Posts" phantom.

4. **Rate Limits:** PhantomBuster has execution time limits based on plan. Monitor `time_left` from API responses.
