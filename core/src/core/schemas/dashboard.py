"""Dashboard schemas for API responses."""

from pydantic import BaseModel

from core.schemas.signals import SignalResponse


class DashboardSummary(BaseModel):
    """Schema for dashboard summary response."""

    total_profiles: int
    active_profiles: int
    total_searches: int
    active_searches: int
    total_posts: int
    total_signals: int
    signals_by_type: dict[str, int]
    signals_by_timing: dict[str, int]
    recent_signals: list[SignalResponse]
