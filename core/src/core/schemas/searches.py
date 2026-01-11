"""Search schemas for API requests and responses."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class SearchCreate(BaseModel):
    """Schema for creating a new search."""

    term: str = Field(min_length=1, max_length=100)
    search_type: Literal["keyword", "hashtag"]


class SearchUpdate(BaseModel):
    """Schema for updating a search."""

    term: str | None = Field(default=None, min_length=1, max_length=100)
    is_active: bool | None = None


class SearchResponse(BaseModel):
    """Schema for search response."""

    id: uuid.UUID
    term: str
    search_type: str
    is_active: bool
    last_crawled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SearchListResponse(BaseModel):
    """Schema for paginated search list response."""

    items: list[SearchResponse]
    total: int
    limit: int
    offset: int
