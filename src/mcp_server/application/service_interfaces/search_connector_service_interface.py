from abc import ABC, abstractmethod
from typing import Any, TypedDict

from mcp_server.application.ports import CacheStats
from mcp_server.domain.search import SearchDocument


class ConnectorStatus(TypedDict):
    """Health snapshot of the Slack search connector."""

    backend_reachable: bool
    cache: CacheStats
    is_stale: bool


class ISearchConnectorService(ABC):
    """Interface for the Slack Enterprise Search connector use case."""

    @abstractmethod
    async def handle_search(self, query: str, filters: dict[str, str]) -> list[SearchDocument]:
        """Answer a live search query from Slack using the cached SOP index.

        Args:
            query: Free-text search query from the Slack user.
            filters: Key-value filters selected by the user.
        Returns:
            Matching documents, capped at 50.
        """

    @abstractmethod
    async def handle_entity_details(self, external_ref: dict[str, Any]) -> dict[str, Any]:
        """Resolve full details for a single search result the user clicked on.

        Args:
            external_ref: The external_ref object identifying the SOP (contains "id").
        Returns:
            The raw SOP data from the backend.
        """

    @abstractmethod
    async def refresh_cache(self) -> CacheStats:
        """Force a full refresh of the SOP search cache from the backend.

        Returns:
            The cache statistics after the refresh.
        """

    @abstractmethod
    async def get_status(self) -> ConnectorStatus:
        """Return the connector's current health and cache statistics."""

    @abstractmethod
    async def test_search(self, query: str) -> list[SearchDocument]:
        """Run a search against the cache without going through Slack, for diagnostics.

        Args:
            query: Free-text search query to test.
        Returns:
            Matching documents, capped at 50.
        """
