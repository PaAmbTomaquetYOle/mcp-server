from abc import ABC, abstractmethod
from typing import TypedDict

from mcp_server.domain.search import SearchDocument


class CacheStats(TypedDict):
    """Snapshot of the SOP search cache's health and usage."""

    total_docs: int
    last_refresh: str | None
    hit_count: int
    miss_count: int


class ISopCachePort(ABC):
    """Interface for the in-memory cache of SOPs indexed for Slack search."""

    @abstractmethod
    async def search(self, query: str, filters: dict[str, str]) -> list[SearchDocument]:
        """
        Search cached documents by query text, optionally narrowed by filters.

        Args:
            query: Free-text search query.
            filters: Key-value filters selected by the searching user.
        Returns:
            Matching documents, most relevant first, capped at 50.
        """

    @abstractmethod
    async def refresh(self, documents: list[SearchDocument]) -> None:
        """
        Replace the cached document set with a freshly fetched one.

        Args:
            documents: The full, up-to-date list of searchable documents.
        """

    @abstractmethod
    async def get_stats(self) -> CacheStats:
        """Return the current cache statistics."""

    @abstractmethod
    async def is_stale(self) -> bool:
        """Return True if the cache has never been refreshed or has exceeded its TTL."""
