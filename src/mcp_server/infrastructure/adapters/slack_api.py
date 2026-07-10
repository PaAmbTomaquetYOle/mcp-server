from typing import Any

from httpx2 import AsyncClient

from mcp_server.application.ports import ISlackApiPort
from mcp_server.domain import SlackApiException

_SLACK_API_BASE_URL = "https://slack.com/api"


class SlackApiAdapter(ISlackApiPort):
    """HTTP adapter for the Slack Web API, used by the Enterprise Search connector."""

    __bot_token: str

    def __init__(self, bot_token: str) -> None:
        self.__bot_token = bot_token

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.__bot_token}"}

    async def _post(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        async with AsyncClient() as client:
            try:
                response = await client.post(
                    f"{_SLACK_API_BASE_URL}/{method}",
                    json=payload,
                    headers=self._headers(),
                )
                response.raise_for_status()
                data = response.json()
            except Exception as exc:
                raise SlackApiException(f"Failed to reach Slack API method {method}: {exc}") from exc

            if not data.get("ok", False):
                raise SlackApiException(f"Slack API method {method} failed: {data.get('error')}")

            return data

    async def complete_search_success(self, function_execution_id: str, results: list[dict[str, Any]]) -> None:
        await self._post(
            "functions.completeSuccess",
            {
                "function_execution_id": function_execution_id,
                "outputs": {"search_results": results},
            },
        )

    async def complete_search_error(self, function_execution_id: str, error: str) -> None:
        await self._post(
            "functions.completeError",
            {"function_execution_id": function_execution_id, "error": error},
        )

    async def update_user_connection(self, user_id: str, status: str) -> None:
        await self._post(
            "apps.user.connection.update",
            {"user_id": user_id, "status": status},
        )

    async def present_entity_details(self, trigger_id: str, metadata: dict[str, Any]) -> None:
        await self._post(
            "entity.presentDetails",
            {"trigger_id": trigger_id, "metadata": metadata},
        )
