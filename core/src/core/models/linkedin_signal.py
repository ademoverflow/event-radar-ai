import uuid
from datetime import date, datetime
from typing import Any, ClassVar, Literal, get_args

from sqlalchemy import UUID, Column, Date, DateTime, Float, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB
from sqlmodel import Field, SQLModel

EventTiming = Literal["past", "future", "unknown"]
EventTimingEnum = ENUM(
    *get_args(EventTiming),
    name="event_timing",
    create_type=True,
)


class LinkedInSignal(SQLModel, table=True):
    """An event signal extracted from a LinkedIn post using LLM analysis."""

    __tablename__: ClassVar[str] = "linkedin_signals"

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
    post_id: uuid.UUID = Field(
        sa_column=Column(
            UUID,
            ForeignKey("linkedin_posts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )
    event_type: str | None = Field(
        sa_column=Column(String(50), nullable=True),
        default=None,
    )
    event_timing: EventTiming = Field(
        sa_column=Column(EventTimingEnum, nullable=False),
        default="unknown",
    )
    event_date: date | None = Field(
        sa_column=Column(Date, nullable=True),
        default=None,
    )
    event_date_inferred: bool = Field(
        default=False,
        nullable=False,
        sa_column_kwargs={"server_default": text("false")},
    )
    companies_mentioned: list[str] = Field(
        sa_column=Column(ARRAY(String), nullable=False),
        default_factory=list,
    )
    people_mentioned: list[str] = Field(
        sa_column=Column(ARRAY(String), nullable=False),
        default_factory=list,
    )
    relevance_score: float = Field(
        sa_column=Column(Float, nullable=False),
        default=0.0,
    )
    summary: str = Field(
        sa_column=Column(Text, nullable=False),
        default="",
    )
    raw_llm_response: dict[str, Any] = Field(
        sa_column=Column(JSONB, nullable=False),
        default_factory=dict,
    )
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            server_default=text("now()"),
            nullable=False,
        ),
        default_factory=datetime.now,
    )
