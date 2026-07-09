from mcp.server import FastMCP

from mcp_server.application.service_interfaces import ISearchConnectorService
from mcp_server.infrastructure.controllers.base_controller import BaseController
from mcp_server.infrastructure.controllers.error_handler import tool_error_handler
from mcp_server.infrastructure.dto import (
    ConnectorStatusResponse,
    RefreshResponse,
    SearchAnalyticsResponse,
    SearchQueryTestResponse,
    SearchResultItem,
)


class SearchConnectorToolController(BaseController):
    """Controller for tools that manage and diagnose the Slack Enterprise Search connector."""

    __service: ISearchConnectorService

    def __init__(self, server: FastMCP, service: ISearchConnectorService) -> None:
        super().__init__(server)
        self.__service = service

    def register(self) -> None:
        self._server.add_tool(
            self.search_connector_status,
            name="search_connector_status",
            title="Slack search connector status",
            description="Report the health of the Slack Enterprise Search connector: backend "
            "reachability and SOP cache statistics.",
        )
        self._server.add_tool(
            self.test_search_query,
            name="test_search_query",
            title="Test a search query",
            description="Run a search against the cached SOP index without going through Slack, "
            "for testing and diagnostics.",
        )
        self._server.add_tool(
            self.refresh_search_index,
            name="refresh_search_index",
            title="Refresh the SOP search index",
            description="Force a full refresh of the SOP search cache from the backend API.",
        )
        self._server.add_tool(
            self.get_search_analytics,
            name="get_search_analytics",
            title="Get search connector analytics",
            description="Report cache hit/miss statistics for the Slack search connector.",
        )

    @tool_error_handler
    async def search_connector_status(self) -> ConnectorStatusResponse:
        """Report the health of the Slack search connector."""
        status = await self.__service.get_status()
        return ConnectorStatusResponse(
            backend_reachable=status["backend_reachable"],
            cache_size=status["cache"]["total_docs"],
            last_refresh=status["cache"]["last_refresh"],
            is_stale=status["is_stale"],
        )

    @tool_error_handler
    async def test_search_query(self, query: str) -> SearchQueryTestResponse:
        """Run a test search against the cached SOP index.

        Args:
            query (str): Free-text search query.
        """
        documents = await self.__service.test_search(query)
        results = [
            SearchResultItem(
                external_id=doc.external_id,
                title=doc.title,
                description=doc.description,
                link=doc.link,
                author=doc.author,
                tags=doc.tags,
                date_updated=doc.date_updated,
            )
            for doc in documents
        ]
        return SearchQueryTestResponse(query=query, results=results, count=len(results))

    @tool_error_handler
    async def refresh_search_index(self) -> RefreshResponse:
        """Force a full refresh of the SOP search cache from the backend."""
        stats = await self.__service.refresh_cache()
        return RefreshResponse(total_indexed=stats["total_docs"], status="ok")

    @tool_error_handler
    async def get_search_analytics(self) -> SearchAnalyticsResponse:
        """Report cache hit/miss statistics for the search connector."""
        status = await self.__service.get_status()
        cache = status["cache"]
        return SearchAnalyticsResponse(
            total_searches=cache["hit_count"] + cache["miss_count"],
            cache_hits=cache["hit_count"],
            cache_misses=cache["miss_count"],
        )
