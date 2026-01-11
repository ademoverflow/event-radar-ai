"""Profiles router for managing LinkedIn monitored profiles."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from core.database import get_session
from core.middlewares.user import get_current_user
from core.models.linkedin_profile import LinkedInMonitoredProfile
from core.models.user import User
from core.schemas.profiles import (
    ProfileCreate,
    ProfileListResponse,
    ProfileResponse,
    ProfileUpdate,
)

profiles_router = APIRouter(prefix="/profiles", tags=["Profiles"])


def _profile_to_response(profile: LinkedInMonitoredProfile) -> ProfileResponse:
    """Convert a profile model to response schema."""
    return ProfileResponse(
        id=profile.id,
        url=profile.url,
        profile_type=profile.profile_type,
        display_name=profile.display_name,
        crawl_frequency_hours=profile.crawl_frequency_hours,
        is_active=profile.is_active,
        last_crawled_at=profile.last_crawled_at,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@profiles_router.get("")
async def list_profiles(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    is_active: Annotated[bool | None, Query()] = None,
) -> ProfileListResponse:
    """List all monitored profiles for the current user."""
    # Build base query
    query = select(LinkedInMonitoredProfile).where(
        col(LinkedInMonitoredProfile.user_id) == current_user.id
    )

    if is_active is not None:
        query = query.where(col(LinkedInMonitoredProfile.is_active) == is_active)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(col(LinkedInMonitoredProfile.created_at).desc())
    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    profiles = result.scalars().all()

    return ProfileListResponse(
        items=[_profile_to_response(p) for p in profiles],
        total=total,
        limit=limit,
        offset=offset,
    )


@profiles_router.post("", status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileResponse:
    """Create a new monitored profile."""
    profile = LinkedInMonitoredProfile(
        user_id=current_user.id,
        url=str(profile_data.url),
        profile_type=profile_data.profile_type,
        display_name=profile_data.display_name,
        crawl_frequency_hours=profile_data.crawl_frequency_hours,
    )
    session.add(profile)
    await session.commit()
    await session.refresh(profile)
    return _profile_to_response(profile)


@profiles_router.get("/{profile_id}")
async def get_profile(
    profile_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileResponse:
    """Get a specific profile by ID."""
    query = select(LinkedInMonitoredProfile).where(
        col(LinkedInMonitoredProfile.id) == profile_id,
        col(LinkedInMonitoredProfile.user_id) == current_user.id,
    )
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return _profile_to_response(profile)


@profiles_router.patch("/{profile_id}")
async def update_profile(
    profile_id: uuid.UUID,
    profile_data: ProfileUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileResponse:
    """Update a profile."""
    query = select(LinkedInMonitoredProfile).where(
        col(LinkedInMonitoredProfile.id) == profile_id,
        col(LinkedInMonitoredProfile.user_id) == current_user.id,
    )
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    update_data = profile_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await session.commit()
    await session.refresh(profile)
    return _profile_to_response(profile)


@profiles_router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    profile_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete a profile."""
    query = select(LinkedInMonitoredProfile).where(
        col(LinkedInMonitoredProfile.id) == profile_id,
        col(LinkedInMonitoredProfile.user_id) == current_user.id,
    )
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    await session.delete(profile)
    await session.commit()


@profiles_router.post("/{profile_id}/crawl")
async def trigger_crawl(
    profile_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    """Trigger a manual crawl for a profile."""
    query = select(LinkedInMonitoredProfile).where(
        col(LinkedInMonitoredProfile.id) == profile_id,
        col(LinkedInMonitoredProfile.user_id) == current_user.id,
    )
    result = await session.execute(query)
    profile = result.scalar_one_or_none()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    # Placeholder - scheduler integration to be implemented
    return {"message": f"Crawl triggered for profile {profile.display_name}"}
