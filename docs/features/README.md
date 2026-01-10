# LinkedIn Signal Detection - Implementation Phases

This directory contains documentation for each implementation phase of the LinkedIn Signal Detection feature.

## Phase Overview

| Phase | Name | Status | Description |
|-------|------|--------|-------------|
| 1 | [Foundation](phase-1-foundation.md) | Completed | Dependencies, data models, migrations, scheduler setup |
| 2 | [Phantombuster](phase-2-phantombuster.md) | Completed | LinkedIn scraping via Phantombuster API |
| 3 | [LLM Extraction](phase-3-llm-extraction.md) | Pending | OpenAI GPT-5.2 signal extraction |
| 4 | [API Endpoints](phase-4-api-endpoints.md) | Pending | FastAPI routers for profiles, searches, signals |
| 5 | [Background Jobs](phase-5-background-jobs.md) | Partial | Complete job implementation with monitoring |
| 6 | [Frontend](phase-6-frontend.md) | Pending | React TypeScript UI |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
│  - Add/manage monitored profiles                                │
│  - Configure keywords/hashtags                                  │
│  - View detected signals                                        │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND                            │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Routers   │  │  Services   │  │   Models    │             │
│  │             │  │             │  │             │             │
│  │ /profiles   │  │ LinkedInSvc │  │ Profile     │             │
│  │ /searches   │  │ LLMSvc      │  │ Post        │             │
│  │ /signals    │  │ Phantombustr│  │ Signal      │             │
│  │ /dashboard  │  │             │  │ Search      │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    SCHEDULER (APScheduler)                  ││
│  │  - Profile crawl jobs (every 15 min)                        ││
│  │  - Search crawl jobs (every 30 min)                         ││
│  │  - Signal analysis jobs (every 10 min)                      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
        ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
        │Phantombuster│ │   OpenAI    │ │  PostgreSQL │
        │   (SaaS)    │ │  GPT-5.2    │ │  Database   │
        └─────────────┘ └─────────────┘ └─────────────┘
```

## Key Technical Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| LinkedIn Scraping | Phantombuster (only) | Handles anti-bot, reliable API |
| LLM Provider | OpenAI GPT-5.2 | Function calling for structured output |
| Languages | French + English | LinkedIn content will be mixed |
| Scheduler | APScheduler | Simple, no extra infrastructure |
| Database | PostgreSQL with ENUMs | Type-safe, existing stack |

## Environment Variables

```env
# Database
DATABASE_URL=postgresql://...

# Phantombuster
PHANTOMBUSTER_API_KEY=your_api_key
PHANTOMBUSTER_PROFILE_POSTS_AGENT_ID=your_profile_agent
PHANTOMBUSTER_SEARCH_POSTS_AGENT_ID=your_search_agent

# OpenAI
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-5.2

# Crawling
DEFAULT_CRAWL_FREQUENCY_HOURS=24
MAX_POSTS_PER_CRAWL=20
```

## Reference

- [Original POC Document](../POC.md)
- [Implementation Plan](../../.claude/plans/glittery-swinging-minsky.md)
