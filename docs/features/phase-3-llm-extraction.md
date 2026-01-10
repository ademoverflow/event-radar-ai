# Phase 3: LLM Signal Extraction

**Status:** Pending

## Overview

Integrate OpenAI GPT-5.2 for extracting event signals from LinkedIn posts. Use structured output (function calling) for reliable JSON extraction.

## Planned Implementation

### LLM Service

**File to create:** `core/src/core/services/llm.py`

```python
from openai import AsyncOpenAI

class LLMService:
    def __init__(self, api_key: str | None = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.openai_api_key)
        self.model = settings.openai_model  # "gpt-5.2"

    async def extract_signal(self, post_content: str) -> SignalExtraction | None:
        """Extract event signal from a LinkedIn post."""
        ...
```

### Signal Extraction Schema

```python
signal_extraction_function = {
    "name": "extract_event_signal",
    "description": "Extract event-related business signals from a LinkedIn post",
    "parameters": {
        "type": "object",
        "properties": {
            "is_event_related": {"type": "boolean"},
            "event_type": {
                "type": "string",
                "enum": ["seminar", "convention", "product_launch",
                         "anniversary", "trade_show", "conference", "other"]
            },
            "event_timing": {"type": "string", "enum": ["past", "future", "unknown"]},
            "event_date": {"type": "string", "format": "date", "nullable": True},
            "date_is_inferred": {"type": "boolean"},
            "companies_mentioned": {"type": "array", "items": {"type": "string"}},
            "people_mentioned": {"type": "array", "items": {"type": "string"}},
            "relevance_score": {"type": "number", "minimum": 0, "maximum": 1},
            "summary": {"type": "string"}
        },
        "required": ["is_event_related", "relevance_score"]
    }
}
```

### System Prompt (FR+EN)

```
You are an event detection specialist analyzing LinkedIn posts in French or English.
Your task is to identify business events and extract structured information.

Look for:
- Seminars, webinars, conferences
- Trade shows, conventions, exhibitions
- Product launches, announcements
- Company anniversaries, milestones
- Networking events, meetups

Extract:
- Event type and timing (past/future)
- Explicit or inferred dates
- Companies, brands, partners mentioned
- Decision-makers, organizers named
- Commercial relevance score (0-1)

Respond in the same language as the post content.
```

## Tasks

- [ ] Create `core/src/core/services/llm.py` with LLMService class
- [ ] Define SignalExtraction dataclass for parsed responses
- [ ] Implement retry logic for API failures
- [ ] Create signal processing job to analyze new posts
- [ ] Store signals in `linkedin_signals` table
- [ ] Add rate limiting / token usage tracking
- [ ] Handle multilingual content (FR/EN)

## Environment Variables

```env
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-5.2
```

## Integration Points

The LLM service will be called:
1. After `crawl_profiles_job` stores new posts
2. After `crawl_searches_job` stores new posts
3. Could also be a separate `analyze_posts_job` that processes unanalyzed posts
