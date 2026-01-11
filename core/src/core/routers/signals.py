"""Signals router for viewing detected LinkedIn signals."""

import uuid
from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.middlewares.user import get_current_user
from core.models.linkedin_signal import LinkedInSignal
from core.models.post import LinkedInPost
from core.models.user import User
from core.schemas.signals import (
    SignalListResponse,
    SignalPostResponse,
    SignalResponse,
    SignalStatsResponse,
)

signals_router = APIRouter(prefix="/signals", tags=["Signals"])


def _post_to_response(post: LinkedInPost) -> SignalPostResponse:
    """Convert a post model to response schema."""
    return SignalPostResponse(
        id=post.id,
        linkedin_post_id=post.linkedin_post_id,
        author_name=post.author_name,
        author_linkedin_url=post.author_linkedin_url,
        content=post.content,
        posted_at=post.posted_at,
    )


def _signal_to_response(signal: LinkedInSignal, post: LinkedInPost | None) -> SignalResponse:
    """Convert a signal model to response schema."""
    return SignalResponse(
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
        post=_post_to_response(post) if post else None,
    )


@signals_router.get("")
async def list_signals(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    event_type: str | None = None,
    event_timing: Literal["past", "future", "unknown"] | None = None,
    min_relevance: Annotated[float | None, Query(ge=0.0, le=1.0)] = None,
    from_date: date | None = None,
    to_date: date | None = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> SignalListResponse:
    """List signals with optional filters."""
    query = select(LinkedInSignal).where(LinkedInSignal.user_id == current_user.id)

    if event_type:
        query = query.where(LinkedInSignal.event_type == event_type)
    if event_timing:
        query = query.where(LinkedInSignal.event_timing == event_timing)
    if min_relevance is not None:
        query = query.where(LinkedInSignal.relevance_score >= min_relevance)
    if from_date:
        query = query.where(func.date(LinkedInSignal.created_at) >= from_date)
    if to_date:
        query = query.where(func.date(LinkedInSignal.created_at) <= to_date)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(LinkedInSignal.created_at.desc())
    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    signals = result.scalars().all()

    # Fetch related posts
    signal_responses = []
    for signal in signals:
        post_query = select(LinkedInPost).where(LinkedInPost.id == signal.post_id)
        post_result = await session.execute(post_query)
        post = post_result.scalar_one_or_none()
        signal_responses.append(_signal_to_response(signal, post))

    return SignalListResponse(
        items=signal_responses,
        total=total,
        limit=limit,
        offset=offset,
    )


@signals_router.get("/stats")
async def get_signal_stats(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SignalStatsResponse:
    """Get signal statistics for the current user."""
    # Total signals
    total_query = select(func.count()).where(LinkedInSignal.user_id == current_user.id)
    total_result = await session.execute(total_query)
    total_signals = total_result.scalar() or 0

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

    # Average relevance
    avg_query = select(func.avg(LinkedInSignal.relevance_score)).where(
        LinkedInSignal.user_id == current_user.id
    )
    avg_result = await session.execute(avg_query)
    average_relevance = avg_result.scalar() or 0.0

    return SignalStatsResponse(
        total_signals=total_signals,
        signals_by_type=signals_by_type,
        signals_by_timing=signals_by_timing,
        average_relevance=round(float(average_relevance), 2),
    )


@signals_router.get("/{signal_id}")
async def get_signal(
    signal_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SignalResponse:
    """Get a specific signal with its associated post."""
    query = select(LinkedInSignal).where(
        LinkedInSignal.id == signal_id,
        LinkedInSignal.user_id == current_user.id,
    )
    result = await session.execute(query)
    signal = result.scalar_one_or_none()

    if not signal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signal not found",
        )

    # Fetch related post
    post_query = select(LinkedInPost).where(LinkedInPost.id == signal.post_id)
    post_result = await session.execute(post_query)
    post = post_result.scalar_one_or_none()

    return _signal_to_response(signal, post)
