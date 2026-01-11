"""Users router."""

from typing import Annotated

from fastapi import APIRouter, Depends

from core.middlewares.user import get_current_user
from core.models.user import User
from core.schemas.auth import UserResponse

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me")
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current authenticated user."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
    )
