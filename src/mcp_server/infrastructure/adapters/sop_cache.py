from __future__ import annotations

from datetime import UTC, datetime

from mcp_server.application.ports import CacheStats, ISopCachePort
from mcp_server.domain.search import SearchDocument

_MAX_RESULTS = 50


class InMemorySopCacheAdapter(ISopCachePort):
    """In-memory cache of SOPs indexed for Slack search, refreshed periodically from the backend."""

    __documents: list[SearchDocument]
    __last_refresh: datetime | None
    __hit_count: int
    __miss_count: int
    __ttl_seconds: int

    def __init__(self, ttl_seconds: int) -> None:
        self.__documents = []
        self.__last_refresh = None
        self.__hit_count = 0
        self.__miss_count = 0
        self.__ttl_seconds = ttl_seconds

    async def search(self, query: str, filters: dict[str, str]) -> list[SearchDocument]:
        needle = query.lower()
        matches = [doc for doc in self.__documents if self._matches(doc, needle)]

        if matches:
            self.__hit_count += 1
        else:
            self.__miss_count += 1

        return matches[:_MAX_RESULTS]

    @staticmethod
    def _matches(doc: SearchDocument, needle: str) -> bool:
        haystacks = [doc.title, doc.content, *doc.tags]
        return any(needle in haystack.lower() for haystack in haystacks)

    async def refresh(self, documents: list[SearchDocument]) -> None:
        self.__documents = list(documents)
        self.__last_refresh = datetime.now(UTC)

    async def get_stats(self) -> CacheStats:
        return CacheStats(
            total_docs=len(self.__documents),
            last_refresh=self.__last_refresh.isoformat() if self.__last_refresh else None,
            hit_count=self.__hit_count,
            miss_count=self.__miss_count,
        )

    async def is_stale(self) -> bool:
        if self.__last_refresh is None:
            return True
        age = (datetime.now(UTC) - self.__last_refresh).total_seconds()
        return age >= self.__ttl_seconds
