"""Signal schemas for API requests and responses."""

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field


class SignalPostResponse(BaseModel):
    """Schema for embedded post in signal response."""

    id: uuid.UUID
    linkedin_post_id: str
    author_name: str
    author_linkedin_url: str
    content: str
    posted_at: datetime


class SignalResponse(BaseModel):
    """Schema for signal response."""

    id: uuid.UUID
    event_type: str | None
    event_timing: str
    event_date: date | None
    event_date_inferred: bool
    companies_mentioned: list[str]
    people_mentioned: list[str]
    relevance_score: float
    summary: str
    created_at: datetime
    post: SignalPostResponse | None = None


class SignalListResponse(BaseModel):
    """Schema for paginated signal list response."""

    items: list[SignalResponse]
    total: int
    limit: int
    offset: int


class SignalFilters(BaseModel):
    """Schema for signal filtering query parameters."""

    event_type: str | None = None
    event_timing: Literal["past", "future", "unknown"] | None = None
    min_relevance: float | None = Field(default=None, ge=0.0, le=1.0)
    from_date: date | None = None
    to_date: date | None = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class SignalStatsResponse(BaseModel):
    """Schema for signal statistics response."""

    total_signals: int
    signals_by_type: dict[str, int]
    signals_by_timing: dict[str, int]
    average_relevance: float
