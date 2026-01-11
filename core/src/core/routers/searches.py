"""Searches router for managing LinkedIn keyword/hashtag searches."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_session
from core.middlewares.user import get_current_user
from core.models.linkedin_search import LinkedInSearch
from core.models.user import User
from core.schemas.searches import (
    SearchCreate,
    SearchListResponse,
    SearchResponse,
    SearchUpdate,
)

searches_router = APIRouter(prefix="/searches", tags=["Searches"])


def _search_to_response(search: LinkedInSearch) -> SearchResponse:
    """Convert a search model to response schema."""
    return SearchResponse(
        id=search.id,
        term=search.term,
        search_type=search.search_type,
        is_active=search.is_active,
        last_crawled_at=search.last_crawled_at,
        created_at=search.created_at,
        updated_at=search.updated_at,
    )


@searches_router.get("")
async def list_searches(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    is_active: Annotated[bool | None, Query()] = None,
) -> SearchListResponse:
    """List all saved searches for the current user."""
    # Build base query
    query = select(LinkedInSearch).where(LinkedInSearch.user_id == current_user.id)

    if is_active is not None:
        query = query.where(LinkedInSearch.is_active == is_active)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = query.order_by(LinkedInSearch.created_at.desc())
    query = query.offset(offset).limit(limit)
    result = await session.execute(query)
    searches = result.scalars().all()

    return SearchListResponse(
        items=[_search_to_response(s) for s in searches],
        total=total,
        limit=limit,
        offset=offset,
    )


@searches_router.post("", status_code=status.HTTP_201_CREATED)
async def create_search(
    search_data: SearchCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SearchResponse:
    """Create a new search."""
    search = LinkedInSearch(
        user_id=current_user.id,
        term=search_data.term,
        search_type=search_data.search_type,
    )
    session.add(search)
    await session.commit()
    await session.refresh(search)
    return _search_to_response(search)


@searches_router.get("/{search_id}")
async def get_search(
    search_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SearchResponse:
    """Get a specific search by ID."""
    query = select(LinkedInSearch).where(
        LinkedInSearch.id == search_id,
        LinkedInSearch.user_id == current_user.id,
    )
    result = await session.execute(query)
    search = result.scalar_one_or_none()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found",
        )

    return _search_to_response(search)


@searches_router.patch("/{search_id}")
async def update_search(
    search_id: uuid.UUID,
    search_data: SearchUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SearchResponse:
    """Update a search."""
    query = select(LinkedInSearch).where(
        LinkedInSearch.id == search_id,
        LinkedInSearch.user_id == current_user.id,
    )
    result = await session.execute(query)
    search = result.scalar_one_or_none()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found",
        )

    update_data = search_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(search, field, value)

    await session.commit()
    await session.refresh(search)
    return _search_to_response(search)


@searches_router.delete("/{search_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_search(
    search_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete a search."""
    query = select(LinkedInSearch).where(
        LinkedInSearch.id == search_id,
        LinkedInSearch.user_id == current_user.id,
    )
    result = await session.execute(query)
    search = result.scalar_one_or_none()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found",
        )

    await session.delete(search)
    await session.commit()


@searches_router.post("/{search_id}/crawl")
async def trigger_crawl(
    search_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict[str, str]:
    """Trigger a manual crawl for a search."""
    query = select(LinkedInSearch).where(
        LinkedInSearch.id == search_id,
        LinkedInSearch.user_id == current_user.id,
    )
    result = await session.execute(query)
    search = result.scalar_one_or_none()

    if not search:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search not found",
        )

    # Placeholder - scheduler integration to be implemented
    return {"message": f"Crawl triggered for search '{search.term}'"}
