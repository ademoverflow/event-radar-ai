import uuid
from datetime import datetime
from typing import Any, ClassVar

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class LinkedInPost(SQLModel, table=True):
    """A LinkedIn post retrieved from crawling."""

    __tablename__: ClassVar[str] = "linkedin_posts"

    id: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            primary_key=True,
            server_default=text("gen_random_uuid()"),
        ),
        default_factory=uuid.uuid4,
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
        default_factory=datetime.now,
    )
    profile_id: uuid.UUID | None = Field(
        sa_column=Column(
            UUID,
            ForeignKey("linkedin_monitored_profiles.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        default=None,
    )
    search_id: uuid.UUID | None = Field(
        sa_column=Column(
            UUID,
            ForeignKey("linkedin_searches.id", ondelete="CASCADE"),
            nullable=True,
            index=True,
        ),
        default=None,
    )
    linkedin_post_id: str = Field(
        sa_column=Column(String(100), unique=True, nullable=False, index=True),
    )
    author_name: str = Field(
        sa_column=Column(String(200), nullable=False),
    )
    author_linkedin_url: str = Field(
        sa_column=Column(String(500), nullable=False),
    )
    content: str = Field(
        sa_column=Column(Text, nullable=False),
    )
    posted_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    raw_data: dict[str, Any] = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=dict,
    )
