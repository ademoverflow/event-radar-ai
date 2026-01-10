import uuid
from datetime import datetime
from typing import ClassVar, Literal, get_args

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import ENUM
from sqlmodel import Field, SQLModel

SearchType = Literal["keyword", "hashtag"]
SearchTypeEnum = ENUM(
    *get_args(SearchType),
    name="search_type",
    create_type=True,
)


class LinkedInSearch(SQLModel, table=True):
    """A keyword or hashtag used for LinkedIn discovery searches."""

    __tablename__: ClassVar[str] = "linkedin_searches"

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
    term: str = Field(
        sa_column=Column(String(100), nullable=False),
    )
    search_type: SearchType = Field(
        sa_column=Column(SearchTypeEnum, nullable=False),
    )
    is_active: bool = Field(
        default=True,
        nullable=False,
        sa_column_kwargs={"server_default": text("true")},
    )
    last_crawled_at: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True),
        default=None,
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
