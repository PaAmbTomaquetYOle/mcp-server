from abc import ABC, abstractmethod
from typing import Any

from mcp_server.domain.search import SlackWorkspaceSearchResult


class ISlackWorkspaceSearchService(ABC):
    """Interface for searching a Slack workspace's internal content on behalf of an authenticated user."""

    @abstractmethod
    async def search(
        self, slack_user_id: str, query: str, filters: dict[str, Any] | None = None
    ) -> list[SlackWorkspaceSearchResult]:
        """
        Search Slack's internal messages/files/channels/users on behalf of a user.

        Args:
            slack_user_id: The Slack user ID whose stored OAuth token authorizes the search.
            query: Free-text search query.
            filters: Optional filters, e.g. content_types, channel_types.
        Returns:
            Matching results across the requested content types.
        Raises:
            UserTokensNotFoundException: If the user has not completed the Slack OAuth flow.
        """
