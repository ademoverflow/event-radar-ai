"""Authentication router."""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.database import get_session
from core.models.user import User
from core.schemas.auth import LoginRequest
from core.security.password import verify_password
from core.security.token import create_access_token
from core.settings import get_settings

settings = get_settings()
auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/login")
async def login(
    credentials: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> JSONResponse:
    """Login with email and password, set HTTP-only cookie."""
    # Find user by email
    statement = select(User).where(User.email == credentials.email).limit(1)
    result = await session.execute(statement)
    user = result.scalar_one_or_none()

    # Validate credentials
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # Create access token
    token = create_access_token(
        data={"email": user.email},
        expires_delta=timedelta(minutes=settings.core_jwt_expiration_timedelta_minutes),
    )

    # Create response with cookie
    response = JSONResponse(content={"message": "Login successful"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
        max_age=settings.core_jwt_expiration_timedelta_minutes * 60,
    )

    return response


@auth_router.post("/logout")
async def logout() -> JSONResponse:
    """Logout by clearing the access token cookie."""
    response = JSONResponse(content={"message": "Logout successful"})
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        domain=settings.cookie_domain,
    )
    return response
