"""LLM service for extracting event signals from LinkedIn posts using OpenAI."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Literal

from openai import APIConnectionError, APIError, AsyncOpenAI, RateLimitError
from pydantic import BaseModel, Field, ValidationError

from core.logger import get_logger
from core.settings import get_settings

if TYPE_CHECKING:
    from datetime import date

logger = get_logger(__name__)
settings = get_settings()


# Type alias for event types
EventType = Literal[
    "seminar",
    "convention",
    "product_launch",
    "anniversary",
    "trade_show",
    "conference",
    "webinar",
    "networking",
    "other",
]

# Type alias for event timing
EventTiming = Literal["past", "future", "unknown"]

# Default OpenAI model for signal extraction
OPENAI_MODEL = "gpt-5.2"

# System prompt for LLM signal extraction
SIGNAL_EXTRACTION_SYSTEM_PROMPT = """\
You are an event detection specialist analyzing LinkedIn posts in French or English.
Your task is to identify business events and extract structured information.

Look for:
- Seminars, webinars, conferences
- Trade shows, conventions, exhibitions
- Product launches, announcements
- Company anniversaries, milestones
- Networking events, meetups

Extract:
- Event type and timing (past/future)
- Explicit or inferred dates
- Companies, brands, partners mentioned
- Decision-makers, organizers named
- Commercial relevance score (0-1)

Respond in the same language as the post content.
If no event is detected, set is_event_related to false and provide a low relevance_score."""

# JSON Schema for signal extraction response
SIGNAL_EXTRACTION_JSON_SCHEMA: dict[str, Any] = {
    "name": "signal_extraction",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "is_event_related": {
                "type": "boolean",
                "description": "Whether the post is related to a business event",
            },
            "event_type": {
                "type": ["string", "null"],
                "enum": [
                    "seminar",
                    "convention",
                    "product_launch",
                    "anniversary",
                    "trade_show",
                    "conference",
                    "webinar",
                    "networking",
                    "other",
                    None,
                ],
                "description": "Type of event detected",
            },
            "event_timing": {
                "type": "string",
                "enum": ["past", "future", "unknown"],
                "description": "Whether the event is in the past, future, or unknown",
            },
            "event_date": {
                "type": ["string", "null"],
                "description": "Date of the event in YYYY-MM-DD format if known, null otherwise",
            },
            "date_is_inferred": {
                "type": "boolean",
                "description": "Whether the event_date was inferred rather than explicitly stated",
            },
            "companies_mentioned": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of companies, brands, or organizations mentioned",
            },
            "people_mentioned": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of people (decision-makers, organizers, speakers) mentioned",
            },
            "relevance_score": {
                "type": "number",
                "description": "Commercial relevance score from 0 to 1",
            },
            "summary": {
                "type": "string",
                "description": "Brief summary of the event or post content",
            },
        },
        "required": [
            "is_event_related",
            "event_type",
            "event_timing",
            "event_date",
            "date_is_inferred",
            "companies_mentioned",
            "people_mentioned",
            "relevance_score",
            "summary",
        ],
        "additionalProperties": False,
    },
}


class SignalExtraction(BaseModel):
    """Structured output schema for signal extraction from LinkedIn posts."""

    is_event_related: bool = Field(description="Whether the post is related to a business event")
    event_type: EventType | None = Field(
        default=None,
        description="Type of event detected (seminar, convention, product_launch, anniversary, "
        "trade_show, conference, webinar, networking, other)",
    )
    event_timing: EventTiming = Field(
        default="unknown",
        description="Whether the event is in the past, future, or unknown",
    )
    event_date: date | None = Field(
        default=None,
        description="Date of the event if explicitly mentioned or can be inferred",
    )
    date_is_inferred: bool = Field(
        default=False,
        description="Whether the event_date was inferred rather than explicitly stated",
    )
    companies_mentioned: list[str] = Field(
        default_factory=list,
        description="List of companies, brands, or organizations mentioned in the post",
    )
    people_mentioned: list[str] = Field(
        default_factory=list,
        description="List of people (decision-makers, organizers, speakers) mentioned in the post",
    )
    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Commercial relevance score from 0 (not relevant) to 1 (highly relevant)",
    )
    summary: str = Field(
        default="",
        description="Brief summary of the event or post content in the same language as the post",
    )


class LLMServiceError(Exception):
    """Base exception for LLM service errors."""


class LLMService:
    """Service for extracting event signals from LinkedIn posts using OpenAI.

    This service uses OpenAI's Responses API with JSON schema to reliably extract
    event-related information from LinkedIn post content.

    Example:
        >>> llm = LLMService()
        >>> signal = await llm.extract_signal("Join us at TechConf 2025 on March 15!")
        >>> if signal and signal.is_event_related:
        ...     print(f"Event: {signal.event_type}, Date: {signal.event_date}")

    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        """Initialize LLM service.

        Args:
            api_key: OpenAI API key. Defaults to settings.openai_api_key.
            model: OpenAI model to use. Defaults to gpt-5.2.

        """
        self.api_key = api_key or settings.openai_api_key
        self.model = model or OPENAI_MODEL
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        """Lazy-initialize OpenAI client."""
        if self._client is None:
            if not self.api_key:
                msg = "OpenAI API key not configured"
                raise LLMServiceError(msg)
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    def _parse_response(self, content: str) -> SignalExtraction | None:
        """Parse JSON response content into SignalExtraction.

        Args:
            content: Raw JSON string from OpenAI response.

        Returns:
            SignalExtraction if parsing succeeds, None otherwise.

        """
        try:
            data = json.loads(content)
            return SignalExtraction.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(
                "Failed to parse LLM response",
                extra={"error": str(e), "content": content[:500]},
            )
            return None

    async def extract_signal(
        self,
        post_content: str,
        author_name: str | None = None,
        max_retries: int = 3,
    ) -> SignalExtraction | None:
        """Extract event signal from a LinkedIn post.

        Uses OpenAI's Responses API with JSON schema to reliably extract
        event-related information from post content.

        Args:
            post_content: The text content of the LinkedIn post.
            author_name: Optional name of the post author for context.
            max_retries: Maximum number of retry attempts on API failure.

        Returns:
            SignalExtraction with extracted data, or None if extraction fails.

        """
        if not post_content.strip():
            logger.warning("Empty post content provided for signal extraction")
            return None

        # Build user message with context
        user_message = f"Analyze this LinkedIn post for event signals:\n\n{post_content}"
        if author_name:
            user_message = f"Post by {author_name}:\n\n{post_content}"

        last_error: Exception | None = None

        for attempt in range(max_retries):
            try:
                response = await self.client.responses.create(
                    model=self.model,
                    instructions=SIGNAL_EXTRACTION_SYSTEM_PROMPT,
                    input=user_message,
                    text={
                        "format": {
                            "type": "json_schema",
                            "name": "signal_extraction",
                            "strict": True,
                            "schema": SIGNAL_EXTRACTION_JSON_SCHEMA["schema"],
                        }
                    },
                    temperature=0.1,
                )

                # Extract text content from response
                if response.output:
                    for item in response.output:
                        if item.type == "message":
                            for content_item in item.content:
                                if content_item.type == "output_text":
                                    extraction = self._parse_response(content_item.text)
                                    if extraction:
                                        logger.debug(
                                            "Successfully extracted signal from post",
                                            extra={
                                                "model": self.model,
                                                "attempt": attempt + 1,
                                                "is_event_related": extraction.is_event_related,
                                            },
                                        )
                                        return extraction

                logger.warning(
                    "No valid response content from OpenAI",
                    extra={"attempt": attempt + 1},
                )

            except (APIError, APIConnectionError, RateLimitError) as e:
                last_error = e
                logger.warning(
                    f"OpenAI API call failed (attempt {attempt + 1}/{max_retries})",
                    extra={"error": str(e)},
                )
                if attempt < max_retries - 1:
                    continue

        if last_error:
            logger.error(
                "Failed to extract signal after all retries",
                extra={"error": str(last_error)},
            )

        return None

    async def batch_extract_signals(
        self,
        posts: list[tuple[str, str | None]],
        max_retries: int = 3,
    ) -> list[SignalExtraction | None]:
        """Extract signals from multiple posts.

        Args:
            posts: List of (content, author_name) tuples.
            max_retries: Maximum retries per extraction.

        Returns:
            List of SignalExtraction results (None for failed extractions).

        """
        results: list[SignalExtraction | None] = []
        for content, author_name in posts:
            result = await self.extract_signal(
                post_content=content,
                author_name=author_name,
                max_retries=max_retries,
            )
            results.append(result)
        return results


def get_llm_service() -> LLMService:
    """Get a configured LLM service instance."""
    return LLMService()
