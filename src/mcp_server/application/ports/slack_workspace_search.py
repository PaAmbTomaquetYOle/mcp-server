from abc import ABC, abstractmethod
from typing import Any

from mcp_server.domain.search import SlackWorkspaceSearchResult


class ISlackWorkspaceSearchPort(ABC):
    """Interface for searching a Slack workspace's internal content via a user token."""

    @abstractmethod
    async def search_workspace(
        self, access_token: str, query: str, filters: dict[str, Any]
    ) -> list[SlackWorkspaceSearchResult]:
        """
        Search Slack's internal messages/files/channels/users using assistant.search.context.

        Args:
            access_token: The Slack user token (xoxp-) authorizing the search.
            query: Free-text search query.
            filters: Optional filters, e.g. content_types, channel_types.
        Returns:
            Matching results across the requested content types.
        """
