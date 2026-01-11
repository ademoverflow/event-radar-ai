"""Authentication schemas."""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User response schema (safe to expose)."""

    id: uuid.UUID
    email: EmailStr
    is_active: bool
    created_at: datetime
