"""Pydantic schemas for API requests and responses."""

from .auth import LoginRequest, UserResponse
from .dashboard import DashboardSummary
from .profiles import ProfileCreate, ProfileListResponse, ProfileResponse, ProfileUpdate
from .searches import SearchCreate, SearchListResponse, SearchResponse, SearchUpdate
from .signals import (
    SignalFilters,
    SignalListResponse,
    SignalPostResponse,
    SignalResponse,
    SignalStatsResponse,
)

__all__ = [
    "DashboardSummary",
    "LoginRequest",
    "ProfileCreate",
    "ProfileListResponse",
    "ProfileResponse",
    "ProfileUpdate",
    "SearchCreate",
    "SearchListResponse",
    "SearchResponse",
    "SearchUpdate",
    "SignalFilters",
    "SignalListResponse",
    "SignalPostResponse",
    "SignalResponse",
    "SignalStatsResponse",
    "UserResponse",
]
