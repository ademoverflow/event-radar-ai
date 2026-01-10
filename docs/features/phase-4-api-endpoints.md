# Phase 4: API Endpoints

**Status:** Pending

## Overview

Create FastAPI routers for CRUD operations on monitored profiles, searches, and signals.

## Planned Routers

### Profiles Router

**File to create:** `core/src/core/routers/profiles.py`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/profiles` | List user's monitored profiles |
| POST | `/profiles` | Add a new profile to monitor |
| GET | `/profiles/{id}` | Get profile details |
| PATCH | `/profiles/{id}` | Update profile settings |
| DELETE | `/profiles/{id}` | Remove profile from monitoring |
| POST | `/profiles/{id}/crawl` | Trigger manual crawl |

**Request/Response Models:**

```python
class ProfileCreate(BaseModel):
    url: str
    profile_type: Literal["company", "personal"]
    display_name: str
    crawl_frequency_hours: int = 24

class ProfileUpdate(BaseModel):
    display_name: str | None = None
    crawl_frequency_hours: int | None = None
    is_active: bool | None = None

class ProfileResponse(BaseModel):
    id: UUID
    url: str
    profile_type: str
    display_name: str
    crawl_frequency_hours: int
    is_active: bool
    last_crawled_at: datetime | None
    created_at: datetime
```

### Searches Router

**File to create:** `core/src/core/routers/searches.py`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/searches` | List user's saved searches |
| POST | `/searches` | Create a new search |
| GET | `/searches/{id}` | Get search details |
| PATCH | `/searches/{id}` | Update search settings |
| DELETE | `/searches/{id}` | Remove search |
| POST | `/searches/{id}/crawl` | Trigger manual crawl |

**Request/Response Models:**

```python
class SearchCreate(BaseModel):
    term: str
    search_type: Literal["keyword", "hashtag"]

class SearchUpdate(BaseModel):
    term: str | None = None
    is_active: bool | None = None

class SearchResponse(BaseModel):
    id: UUID
    term: str
    search_type: str
    is_active: bool
    last_crawled_at: datetime | None
    created_at: datetime
```

### Signals Router

**File to create:** `core/src/core/routers/signals.py`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/signals` | List detected signals with filters |
| GET | `/signals/{id}` | Get signal details with post |
| GET | `/signals/stats` | Get signal statistics |

**Query Parameters for GET /signals:**

```python
class SignalFilters(BaseModel):
    event_type: str | None = None
    event_timing: Literal["past", "future", "unknown"] | None = None
    min_relevance: float | None = None
    from_date: date | None = None
    to_date: date | None = None
    limit: int = 50
    offset: int = 0
```

### Dashboard Router

**File to create:** `core/src/core/routers/dashboard.py`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/dashboard/summary` | Get overview stats |

**Response:**

```python
class DashboardSummary(BaseModel):
    total_profiles: int
    total_searches: int
    total_posts: int
    total_signals: int
    signals_by_type: dict[str, int]
    recent_signals: list[SignalResponse]
```

## Tasks

- [ ] Create `core/src/core/routers/profiles.py`
- [ ] Create `core/src/core/routers/searches.py`
- [ ] Create `core/src/core/routers/signals.py`
- [ ] Create `core/src/core/routers/dashboard.py`
- [ ] Register routers in `main.py`
- [ ] Add authentication middleware to all endpoints
- [ ] Add pagination utilities
- [ ] Add input validation

## Authentication

All endpoints require authentication. Use existing JWT middleware:

```python
from core.middlewares.user import get_current_user

@router.get("/profiles")
async def list_profiles(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> list[ProfileResponse]:
    ...
```
