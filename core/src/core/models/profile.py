import uuid
from datetime import datetime
from typing import ClassVar, Literal

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, text
from sqlmodel import Field, SQLModel


class MonitoredProfile(SQLModel, table=True):
    """A LinkedIn profile monitored by a user for event signals."""

    __tablename__: ClassVar[str] = "monitored_profiles"

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
    linkedin_url: str = Field(
        sa_column=Column(String(500), nullable=False),
    )
    profile_type: Literal["company", "personal"] = Field(
        sa_column=Column(String(20), nullable=False),
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
