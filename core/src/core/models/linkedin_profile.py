import uuid
from datetime import datetime
from typing import ClassVar, Literal, get_args

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlmodel import Field, SQLModel

ProfileType = Literal["company", "personal"]
ProfileTypeEnum = ENUM(
    *get_args(ProfileType),
    name="profile_type",
    create_type=True,
)


class LinkedInMonitoredProfile(SQLModel, table=True):
    """A LinkedIn profile monitored by a user for event signals."""

    __tablename__: ClassVar[str] = "linkedin_monitored_profiles"

    id: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        ),
        default_factory=uuid.uuid4,
    )
    user_id: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )
    url: str = Field(
        sa_column=Column(String(500), nullable=False),
    )
    profile_type: ProfileType = Field(
        sa_column=Column(ProfileTypeEnum, nullable=False),
    )
    display_name: str = Field(
        sa_column=Column(String(200), nullable=False),
    )
    crawl_frequency_hours: int = Field(
        default=24,
        nullable=False,
        sa_column_kwargs={"server_default": text("24")},
    )
    last_crawled_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True),
        default=None,
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("true")},
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
        default_factory=datetime.now,
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),
            onupdate=text("now()"),
            nullable=False,
        ),
        default_factory=datetime.now,
    )
