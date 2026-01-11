import asyncio
import contextlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from http import HTTPStatus
from typing import Any

import httpx

from core.logger import get_logger
from core.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()


class PhantombusterError(Exception):
    """Base exception for Phantombuster errors."""


class PhantombusterAgentError(PhantombusterError):
    """Error when agent execution fails."""


class PhantombusterTimeoutError(PhantombusterError):
    """Error when agent execution times out."""


@dataclass
class AgentOutput:
    """Result from a Phantombuster agent execution."""

    container_id: str
    status: str
    output: str | None
    result_object: list[dict[str, Any]] | dict[str, Any] | None


@dataclass
class AgentDetails:
    """Detailed information about a Phantombuster agent."""

    id: str
    name: str
    script_id: str
    launch_type: str
    last_run_at: datetime | None
    argument: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentStatus:
    """Current status of a Phantombuster agent."""

    is_running: bool
    last_status: str
    last_end_time: datetime | None
    time_left_seconds: int


@dataclass
class AgentSummary:
    """Summary information about a Phantombuster agent."""

    id: str
    name: str
    script_id: str


@dataclass
class ValidationResult:
    """Result of validating a Phantombuster agent configuration."""

    is_valid: bool
    has_session_cookie: bool
    missing_config: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class PhantombusterClient:
    """Client for interacting with the Phantombuster API.

    Phantombuster is a cloud-based automation platform that provides
    pre-built "Phantoms" (agents) for scraping LinkedIn profiles and posts.

    API Documentation: https://hub.phantombuster.com/docs/api
    """

    BASE_URL = "https://api.phantombuster.com/api/v1"
    BASE_URL_V2 = "https://api.phantombuster.com/api/v2"

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize Phantombuster client.

        Args:
            api_key: Phantombuster API key. If not provided, uses settings.

        """
        self.api_key = api_key or settings.phantombuster_api_key
        if not self.api_key:
            msg = "Phantombuster API key is required"
            raise PhantombusterError(msg)

        self._headers = {
            "X-Phantombuster-Key-1": self.api_key,
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        version: int = 1,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request to the Phantombuster API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            version: API version (1 or 2)
            params: Query parameters
            json_data: JSON body data

        Returns:
            Response JSON data

        Raises:
            PhantombusterError: If the request fails

        """
        base_url = self.BASE_URL if version == 1 else self.BASE_URL_V2
        url = f"{base_url}{endpoint}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.request(
                method,
                url,
                headers=self._headers,
                params=params,
                json=json_data,
            )

            if response.status_code >= HTTPStatus.BAD_REQUEST:
                logger.error(
                    "Phantombuster API error",
                    extra={
                        "status_code": response.status_code,
                        "response": response.text,
                        "endpoint": endpoint,
                    },
                )
                msg = f"API request failed with status {response.status_code}: {response.text}"
                raise PhantombusterError(msg)

            return response.json()  # type: ignore[no-any-return]

    async def get_user(self) -> dict[str, Any]:
        """Get current user information.

        Returns:
            User data including email and time left

        """
        return await self._request("GET", "/user")

    async def get_agent(self, agent_id: str) -> dict[str, Any]:
        """Get agent information.

        Args:
            agent_id: The Phantombuster agent ID

        Returns:
            Agent configuration and status

        """
        return await self._request("GET", f"/agent/{agent_id}")

    async def launch_agent(
        self,
        agent_id: str,
        argument: dict[str, Any] | None = None,
    ) -> str:
        """Launch a Phantombuster agent.

        Args:
            agent_id: The Phantombuster agent ID
            argument: Optional arguments to pass to the agent

        Returns:
            Container ID for tracking the execution

        """
        json_data: dict[str, Any] = {"id": agent_id}
        if argument:
            # Phantombuster API expects argument as a JSON string
            json_data["argument"] = json.dumps(argument)

        response = await self._request(
            "POST",
            "/agents/launch",
            version=2,
            json_data=json_data,
        )

        container_id = response.get("containerId")
        if not container_id:
            msg = "No container ID returned from launch"
            raise PhantombusterError(msg)

        logger.info(
            "Launched Phantombuster agent",
            extra={"agent_id": agent_id, "container_id": container_id},
        )
        return container_id  # type: ignore[no-any-return]

    async def get_agent_output(self, agent_id: str) -> AgentOutput:
        """Get the output from an agent's last execution.

        Args:
            agent_id: The Phantombuster agent ID

        Returns:
            Agent output including status and result

        """
        response = await self._request("GET", f"/agent/{agent_id}/output")

        # API returns {'status': 'success', 'data': {...}} structure
        # The actual data is nested inside 'data' key
        data = response.get("data", response)

        # resultObject may be a JSON string that needs parsing
        result_object = data.get("resultObject")
        if isinstance(result_object, str):
            with contextlib.suppress(json.JSONDecodeError):
                result_object = json.loads(result_object)

        return AgentOutput(
            container_id=data.get("containerId", ""),
            status=response.get("status", data.get("containerStatus", "unknown")),
            output=data.get("output"),
            result_object=result_object,
        )

    async def fetch_result_object(self, agent_id: str) -> dict[str, Any] | None:
        """Fetch the result object from an agent's last execution.

        Args:
            agent_id: The Phantombuster agent ID

        Returns:
            The result object (parsed JSON) or None

        """
        response = await self._request(
            "GET",
            f"/agent/{agent_id}/output",
            params={"withoutResultObject": "false"},
        )
        return response.get("resultObject")

    async def launch_and_wait(
        self,
        agent_id: str,
        argument: dict[str, Any] | None = None,
        timeout_seconds: int = 300,
        poll_interval_seconds: int = 10,
    ) -> AgentOutput:
        """Launch an agent and wait for completion.

        Args:
            agent_id: The Phantombuster agent ID
            argument: Optional arguments to pass to the agent
            timeout_seconds: Maximum time to wait for completion
            poll_interval_seconds: Time between status checks

        Returns:
            Agent output after completion

        Raises:
            PhantombusterTimeoutError: If execution times out
            PhantombusterAgentError: If execution fails

        """
        container_id = await self.launch_agent(agent_id, argument)

        elapsed = 0
        while elapsed < timeout_seconds:
            await asyncio.sleep(poll_interval_seconds)
            elapsed += poll_interval_seconds

            output = await self.get_agent_output(agent_id)

            if output.container_id != container_id:
                # A new execution started, something is wrong
                logger.warning(
                    "Container ID mismatch during wait",
                    extra={
                        "expected": container_id,
                        "actual": output.container_id,
                    },
                )
                continue

            if output.status in ("finished", "success"):
                logger.info(
                    "Agent execution completed",
                    extra={"agent_id": agent_id, "container_id": container_id},
                )
                return output

            if output.status in ("error", "failed"):
                msg = f"Agent execution failed: {output.output}"
                raise PhantombusterAgentError(msg)

            logger.debug(
                "Waiting for agent completion",
                extra={
                    "agent_id": agent_id,
                    "status": output.status,
                    "elapsed": elapsed,
                },
            )

        msg = f"Agent execution timed out after {timeout_seconds} seconds"
        raise PhantombusterTimeoutError(msg)

    async def fetch_agent(self, agent_id: str) -> AgentDetails:
        """Fetch detailed information about a specific agent.

        Args:
            agent_id: The Phantombuster agent ID

        Returns:
            Agent details including configuration and last run info

        """
        response = await self._request(
            "GET",
            "/agents/fetch",
            version=2,
            params={"id": agent_id},
        )

        # Parse saved argument from JSON string
        argument: dict[str, Any] = {}
        raw_argument = response.get("argument")
        if raw_argument and isinstance(raw_argument, str):
            with contextlib.suppress(json.JSONDecodeError):
                argument = json.loads(raw_argument)
        elif isinstance(raw_argument, dict):
            argument = raw_argument

        # Parse last run timestamp
        last_run_at: datetime | None = None
        last_ended = response.get("lastEndedAt")
        if last_ended:
            with contextlib.suppress(ValueError, TypeError):
                # v2 API uses milliseconds
                last_run_at = datetime.fromtimestamp(last_ended / 1000, tz=UTC)

        return AgentDetails(
            id=str(response.get("id", agent_id)),
            name=response.get("name", ""),
            script_id=str(response.get("scriptId", "")),
            launch_type=response.get("launchType", "manual"),
            last_run_at=last_run_at,
            argument=argument,
        )

    async def update_agent_argument(
        self,
        agent_id: str,
        argument: dict[str, Any],
    ) -> None:
        """Update the saved argument configuration for an agent.

        Args:
            agent_id: The Phantombuster agent ID
            argument: New argument configuration to save

        """
        await self._request(
            "POST",
            "/agents/save",
            version=2,
            json_data={
                "id": agent_id,
                "argument": json.dumps(argument),
            },
        )

        logger.info(
            "Updated agent argument",
            extra={"agent_id": agent_id},
        )

    async def get_agent_status(self, agent_id: str) -> AgentStatus:
        """Get the current status of an agent.

        Args:
            agent_id: The Phantombuster agent ID

        Returns:
            Current agent status including running state and time remaining

        """
        # Fetch agent details
        agent_response = await self._request(
            "GET",
            "/agents/fetch",
            version=2,
            params={"id": agent_id},
        )

        # Fetch user info for time remaining
        user_response = await self._request("GET", "/user")

        # Parse last end time
        last_end_time: datetime | None = None
        last_ended = agent_response.get("lastEndedAt")
        if last_ended:
            with contextlib.suppress(ValueError, TypeError):
                last_end_time = datetime.fromtimestamp(last_ended / 1000, tz=UTC)

        # Check if agent is currently running
        is_running = agent_response.get("runningContainers", 0) > 0

        return AgentStatus(
            is_running=is_running,
            last_status=agent_response.get("lastEndStatus", "unknown"),
            last_end_time=last_end_time,
            time_left_seconds=int(user_response.get("data", {}).get("timeLeft", 0) * 60),
        )

    async def fetch_all_agents(self) -> list[AgentSummary]:
        """Fetch all agents in the workspace.

        Returns:
            List of agent summaries

        """
        response = await self._request(
            "GET",
            "/agents/fetch-all",
            version=2,
        )

        agents_data: list[dict[str, Any]] = response if isinstance(response, list) else []
        return [
            AgentSummary(
                id=str(agent_data.get("id", "")),
                name=agent_data.get("name", ""),
                script_id=str(agent_data.get("scriptId", "")),
            )
            for agent_data in agents_data
        ]

    async def validate_profile_posts_phantom(self, agent_id: str) -> ValidationResult:
        """Validate that an agent is configured for LinkedIn profile posts extraction.

        Args:
            agent_id: The Phantombuster agent ID

        Returns:
            Validation result with configuration status

        """
        try:
            agent = await self.fetch_agent(agent_id)
        except PhantombusterError as e:
            return ValidationResult(
                is_valid=False,
                has_session_cookie=False,
                missing_config=[f"Could not fetch agent: {e}"],
            )

        missing_config: list[str] = []
        warnings: list[str] = []

        # Check for session cookie in saved arguments
        has_session_cookie = bool(agent.argument.get("sessionCookie"))

        if not has_session_cookie:
            warnings.append(
                "No session cookie configured. You can provide one via API "
                "or configure it in the Phantombuster UI."
            )

        # Check agent name suggests it's a profile posts extractor
        name_lower = agent.name.lower()
        expected_keywords = ["activity", "posts", "profile"]
        if not any(kw in name_lower for kw in expected_keywords):
            warnings.append(
                f"Agent name '{agent.name}' doesn't suggest it's a profile posts extractor. "
                "Please verify you're using the correct phantom."
            )

        # Check if agent has been run before
        if agent.last_run_at is None:
            warnings.append("Agent has never been executed. Consider running a test first.")

        return ValidationResult(
            is_valid=len(missing_config) == 0,
            has_session_cookie=has_session_cookie,
            missing_config=missing_config,
            warnings=warnings,
        )
