from typing import Any

from httpx2 import AsyncClient

from mcp_server.application.ports import ISlackWorkspaceSearchPort
from mcp_server.domain import SlackApiException
from mcp_server.domain.search import SlackWorkspaceSearchResult

_SLACK_API_BASE_URL = "https://slack.com/api"


class SlackWorkspaceSearchAdapter(ISlackWorkspaceSearchPort):
    """Calls Slack's assistant.search.context using a per-user OAuth token."""

    async def search_workspace(
        self, access_token: str, query: str, filters: dict[str, Any]
    ) -> list[SlackWorkspaceSearchResult]:
        payload: dict[str, Any] = {"query": query, **filters}

        async with AsyncClient() as client:
            try:
                response = await client.post(
                    f"{_SLACK_API_BASE_URL}/assistant.search.context",
                    json=payload,
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                response.raise_for_status()
                data = response.json()
            except Exception as exc:
                raise SlackApiException(f"Failed to reach Slack API method assistant.search.context: {exc}") from exc

            if not data.get("ok", False):
                raise SlackApiException(f"Slack API method assistant.search.context failed: {data.get('error')}")

            return self._map_results(data.get("results", {}))

    @staticmethod
    def _map_results(results: dict[str, Any]) -> list[SlackWorkspaceSearchResult]:
        mapped: list[SlackWorkspaceSearchResult] = []
        for content_type, section in results.items():
            for item in section.get("items", []):
                mapped.append(SlackWorkspaceSearchResult.from_api_item(content_type, item))
        return mapped
