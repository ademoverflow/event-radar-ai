# Phase 1: Foundation (Infrastructure)

**Status:** Completed

## Overview

Set up the foundational infrastructure for the LinkedIn Signal Detection feature including dependencies, data models, database migrations, and scheduler setup.

## Dependencies Added

```toml
# core/pyproject.toml
dependencies = [
    "apscheduler>=3.11.0",  # Background job scheduling
    "httpx>=0.28.1",         # Async HTTP client for Phantombuster API
    "openai>=1.82.0",        # LLM signal extraction (Phase 3)
]
```

## Data Models Created

### LinkedInMonitoredProfile

**File:** `core/src/core/models/linkedin_profile.py`
**Table:** `linkedin_monitored_profiles`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users table |
| url | String(500) | LinkedIn profile URL |
| profile_type | ENUM('company', 'personal') | PostgreSQL ENUM |
| display_name | String(200) | Display name for the profile |
| crawl_frequency_hours | Integer | Default 24 |
| last_crawled_at | DateTime | Nullable |
| is_active | Boolean | Default true |
| created_at | DateTime | Auto-generated |
| updated_at | DateTime | Auto-generated |

### LinkedInSearch

**File:** `core/src/core/models/linkedin_search.py`
**Table:** `linkedin_searches`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users table |
| term | String(100) | Search term or hashtag |
| search_type | ENUM('keyword', 'hashtag') | PostgreSQL ENUM |
| is_active | Boolean | Default true |
| last_crawled_at | DateTime | Nullable |
| created_at | DateTime | Auto-generated |
| updated_at | DateTime | Auto-generated |

### LinkedInPost

**File:** `core/src/core/models/post.py`
**Table:** `linkedin_posts`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| created_at | DateTime | Auto-generated |
| profile_id | UUID | FK to linkedin_monitored_profiles (nullable) |
| search_id | UUID | FK to linkedin_searches (nullable) |
| linkedin_post_id | String(100) | Unique LinkedIn post identifier |
| author_name | String(200) | Post author name |
| author_linkedin_url | String(500) | Author's LinkedIn URL |
| content | Text | Post content |
| posted_at | DateTime | When post was published |
| raw_data | JSONB | Raw data from scraper |

### LinkedInSignal

**File:** `core/src/core/models/linkedin_signal.py`
**Table:** `linkedin_signals`

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| user_id | UUID | FK to users table |
| post_id | UUID | FK to linkedin_posts |
| event_type | String(50) | seminar, convention, launch, etc. |
| event_timing | ENUM('past', 'future', 'unknown') | PostgreSQL ENUM |
| event_date | Date | Nullable |
| event_date_inferred | Boolean | Default false |
| companies_mentioned | ARRAY(String) | Companies in the post |
| people_mentioned | ARRAY(String) | People in the post |
| relevance_score | Float | 0-1 score |
| summary | Text | LLM-generated summary |
| raw_llm_response | JSONB | Full LLM response |
| created_at | DateTime | Auto-generated |

## Scheduler Infrastructure

**Files:**
- `core/src/core/scheduler/__init__.py` - Scheduler setup with AsyncIOScheduler
- `core/src/core/scheduler/jobs.py` - Job definitions

**Integration in main.py:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # ... alembic migrations ...
    register_jobs(scheduler)
    await start_scheduler()
    yield
    await stop_scheduler()
```

## Settings Added

**File:** `core/src/core/settings.py`

```python
# OpenAI settings for LLM signal extraction
openai_api_key: str = ""
openai_model: str = "gpt-5.2"

# LinkedIn scraper settings (Phantombuster)
phantombuster_api_key: str = ""
phantombuster_profile_posts_agent_id: str = ""
phantombuster_search_posts_agent_id: str = ""

# Crawling settings
default_crawl_frequency_hours: int = 24
max_posts_per_crawl: int = 20
```

## Migration

**File:** `core/src/core/alembic/versions/a89a422dd59b_add_linkedin_models_with_enums.py`

Creates all tables with PostgreSQL ENUMs for type-safe columns.

## Files Created/Modified

| File | Action |
|------|--------|
| `core/src/core/models/linkedin_profile.py` | Created |
| `core/src/core/models/linkedin_search.py` | Created |
| `core/src/core/models/linkedin_signal.py` | Created |
| `core/src/core/models/post.py` | Created |
| `core/src/core/models/__init__.py` | Updated exports |
| `core/src/core/scheduler/__init__.py` | Created |
| `core/src/core/scheduler/jobs.py` | Created |
| `core/src/core/settings.py` | Added new settings |
| `core/src/core/main.py` | Added scheduler lifecycle |
| `core/pyproject.toml` | Added dependencies |
