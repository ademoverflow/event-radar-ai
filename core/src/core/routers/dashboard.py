"""Dashboard router for overview statistics."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.middlewares.user import get_current_user
from core.models.linkedin_profile import LinkedInMonitoredProfile
from core.models.linkedin_search import LinkedInSearch
from core.models.linkedin_signal import LinkedInSignal
from core.models.post import LinkedInPost
from core.models.user import User
from core.schemas.dashboard import DashboardSummary
from core.schemas.signals import SignalPostResponse, SignalResponse

dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@dashboard_router.get("/summary")
async def get_dashboard_summary(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DashboardSummary:
    """Get dashboard summary statistics."""
    # Profile counts
    total_profiles_query = select(func.count()).where(
        LinkedInMonitoredProfile.user_id == current_user.id
    )
    total_profiles = (await session.execute(total_profiles_query)).scalar() or 0

    active_profiles_query = select(func.count()).where(
        LinkedInMonitoredProfile.user_id == current_user.id,
        LinkedInMonitoredProfile.is_active == True,  # noqa: E712
    )
    active_profiles = (await session.execute(active_profiles_query)).scalar() or 0

    # Search counts
    total_searches_query = select(func.count()).where(
        LinkedInSearch.user_id == current_user.id
    )
    total_searches = (await session.execute(total_searches_query)).scalar() or 0

    active_searches_query = select(func.count()).where(
        LinkedInSearch.user_id == current_user.id,
        LinkedInSearch.is_active == True,  # noqa: E712
    )
    active_searches = (await session.execute(active_searches_query)).scalar() or 0

    # Post count (posts from user's profiles and searches)
    profile_ids_query = select(LinkedInMonitoredProfile.id).where(
        LinkedInMonitoredProfile.user_id == current_user.id
    )
    search_ids_query = select(LinkedInSearch.id).where(
        LinkedInSearch.user_id == current_user.id
    )

    total_posts_query = select(func.count()).where(
        (LinkedInPost.profile_id.in_(profile_ids_query))
        | (LinkedInPost.search_id.in_(search_ids_query))
    )
    total_posts = (await session.execute(total_posts_query)).scalar() or 0

    # Signal counts
    total_signals_query = select(func.count()).where(
        LinkedInSignal.user_id == current_user.id
    )
    total_signals = (await session.execute(total_signals_query)).scalar() or 0

    # Signals by type
    type_query = (
        select(LinkedInSignal.event_type, func.count())
        .where(LinkedInSignal.user_id == current_user.id)
        .group_by(LinkedInSignal.event_type)
    )
    type_result = await session.execute(type_query)
    signals_by_type = {row[0] or "unknown": row[1] for row in type_result.all()}

    # Signals by timing
    timing_query = (
        select(LinkedInSignal.event_timing, func.count())
        .where(LinkedInSignal.user_id == current_user.id)
        .group_by(LinkedInSignal.event_timing)
    )
    timing_result = await session.execute(timing_query)
    signals_by_timing = {row[0]: row[1] for row in timing_result.all()}

    # Recent signals (last 5)
    recent_query = (
        select(LinkedInSignal)
        .where(LinkedInSignal.user_id == current_user.id)
        .order_by(LinkedInSignal.created_at.desc())
        .limit(5)
    )
    recent_result = await session.execute(recent_query)
    recent_signals_db = recent_result.scalars().all()

    recent_signals = []
    for signal in recent_signals_db:
        post_query = select(LinkedInPost).where(LinkedInPost.id == signal.post_id)
        post_result = await session.execute(post_query)
        post = post_result.scalar_one_or_none()

        recent_signals.append(
            SignalResponse(
                id=signal.id,
                event_type=signal.event_type,
                event_timing=signal.event_timing,
                event_date=signal.event_date,
                event_date_inferred=signal.event_date_inferred,
                companies_mentioned=signal.companies_mentioned,
                people_mentioned=signal.people_mentioned,
                relevance_score=signal.relevance_score,
                summary=signal.summary,
                created_at=signal.created_at,
                post=SignalPostResponse(
                    id=post.id,
                    linkedin_post_id=post.linkedin_post_id,
                    author_name=post.author_name,
                    author_linkedin_url=post.author_linkedin_url,
                    content=post.content,
                    posted_at=post.posted_at,
                )
                if post
                else None,
            )
        )

    return DashboardSummary(
        total_profiles=total_profiles,
        active_profiles=active_profiles,
        total_searches=total_searches,
        active_searches=active_searches,
        total_posts=total_posts,
        total_signals=total_signals,
        signals_by_type=signals_by_type,
        signals_by_timing=signals_by_timing,
        recent_signals=recent_signals,
    )
