# Phase 5: Background Jobs (Complete Implementation)

**Status:** Partially Complete

## Overview

Finalize background job implementation with signal analysis integration and monitoring.

## Current State (from Phase 2)

Jobs already implemented:
- `crawl_profiles_job` - Runs every 15 minutes
- `crawl_searches_job` - Runs every 30 minutes

## Planned Additions

### Signal Analysis Job

**Add to:** `core/src/core/scheduler/jobs.py`

```python
async def analyze_posts_job() -> None:
    """Background job to analyze unprocessed posts with LLM."""
    # Find posts without signals
    # Call LLM service for each
    # Store extracted signals
```

**Schedule:** Every 10 minutes

### Job Monitoring

Add job status tracking:

```python
class JobStatus(SQLModel, table=True):
    __tablename__ = "job_status"

    id: UUID
    job_name: str
    last_run_at: datetime
    last_status: str  # success, failed, running
    items_processed: int
    error_message: str | None
```

### Manual Triggers

Expose endpoints for manual job triggering (for testing):

```python
@router.post("/jobs/crawl-profiles")
async def trigger_profile_crawl(
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    await crawl_profiles_job()
    return {"status": "completed"}
```

## Tasks

- [ ] Create `analyze_posts_job` for LLM signal extraction
- [ ] Add job status tracking table and model
- [ ] Implement job status updates in each job
- [ ] Create admin endpoints for manual job triggers
- [ ] Add error recovery / retry logic
- [ ] Add logging improvements for job monitoring

## Job Schedule Summary

| Job | Interval | Purpose |
|-----|----------|---------|
| crawl_profiles_job | 15 min | Fetch posts from monitored profiles |
| crawl_searches_job | 30 min | Fetch posts from keyword/hashtag searches |
| analyze_posts_job | 10 min | Extract signals from new posts |
