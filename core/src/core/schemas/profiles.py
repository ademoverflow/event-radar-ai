"""Profile schemas for API requests and responses."""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ProfileCreate(BaseModel):
    """Schema for creating a new monitored profile."""

    url: HttpUrl
    profile_type: Literal["company", "personal"]
    display_name: str = Field(min_length=1, max_length=200)
    crawl_frequency_hours: int = Field(default=24, ge=1, le=168)


class ProfileUpdate(BaseModel):
    """Schema for updating a monitored profile."""

    display_name: str | None = Field(default=None, min_length=1, max_length=200)
    crawl_frequency_hours: int | None = Field(default=None, ge=1, le=168)
    is_active: bool | None = None


class ProfileResponse(BaseModel):
    """Schema for profile response."""

    id: uuid.UUID
    url: str
    profile_type: str
    display_name: str
    crawl_frequency_hours: int
    is_active: bool
    last_crawled_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ProfileListResponse(BaseModel):
    """Schema for paginated profile list response."""

    items: list[ProfileResponse]
    total: int
    limit: int
    offset: int
