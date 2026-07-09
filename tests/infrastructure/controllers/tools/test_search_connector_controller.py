from unittest.mock import AsyncMock

import pytest
from mcp.server import FastMCP

from mcp_server.application.ports import CacheStats
from mcp_server.application.service_interfaces import ConnectorStatus
from mcp_server.domain.search import SearchDocument
from mcp_server.infrastructure.controllers.tools.search_connector_controller import SearchConnectorToolController
from mcp_server.infrastructure.dto import (
    ConnectorStatusResponse,
    RefreshResponse,
    SearchAnalyticsResponse,
    SearchQueryTestResponse,
)
from tests.conftest import get_tool_names

_DOC = SearchDocument(
    external_id="1",
    title="Restart deploy pipeline",
    description="Restart deploy pipeline",
    content="Restart deploy pipeline",
    link="https://x/sops/1",
    author="U1",
    tags=["deploy"],
    origin_channel="C1",
    date_updated="2026-01-01",
)


@pytest.fixture
def mock_service():
    service = AsyncMock()
    service.test_search = AsyncMock(return_value=[_DOC])
    service.refresh_cache = AsyncMock(
        return_value=CacheStats(total_docs=1, last_refresh="2026-01-01T00:00:00Z", hit_count=0, miss_count=0)
    )
    service.get_status = AsyncMock(
        return_value=ConnectorStatus(
            backend_reachable=True,
            cache=CacheStats(total_docs=1, last_refresh="2026-01-01T00:00:00Z", hit_count=3, miss_count=1),
            is_stale=False,
        )
    )
    return service


@pytest.fixture
def search_server(mock_service):
    server = FastMCP(name="test-search-connector")
    SearchConnectorToolController(server, mock_service).register()
    return server


class TestRegistration:
    def test_registers_all_tools(self, search_server):
        names = get_tool_names(search_server)
        assert "search_connector_status" in names
        assert "test_search_query" in names
        assert "refresh_search_index" in names
        assert "get_search_analytics" in names


class TestSearchConnectorStatus:
    @pytest.mark.anyio
    async def test_returns_status(self, mock_service):
        controller = SearchConnectorToolController.__new__(SearchConnectorToolController)
        controller._SearchConnectorToolController__service = mock_service

        result = await controller.search_connector_status()

        assert isinstance(result, ConnectorStatusResponse)
        assert result.backend_reachable is True
        assert result.cache_size == 1
        assert result.is_stale is False


class TestTestSearchQuery:
    @pytest.mark.anyio
    async def test_runs_search_and_returns_results(self, mock_service):
        controller = SearchConnectorToolController.__new__(SearchConnectorToolController)
        controller._SearchConnectorToolController__service = mock_service

        result = await controller.test_search_query(query="deploy")

        assert isinstance(result, SearchQueryTestResponse)
        assert result.query == "deploy"
        assert result.count == 1
        assert result.results[0].external_id == "1"
        mock_service.test_search.assert_awaited_once_with("deploy")


class TestRefreshSearchIndex:
    @pytest.mark.anyio
    async def test_refreshes_and_returns_summary(self, mock_service):
        controller = SearchConnectorToolController.__new__(SearchConnectorToolController)
        controller._SearchConnectorToolController__service = mock_service

        result = await controller.refresh_search_index()

        assert isinstance(result, RefreshResponse)
        assert result.total_indexed == 1
        assert result.status == "ok"
        mock_service.refresh_cache.assert_awaited_once()


class TestGetSearchAnalytics:
    @pytest.mark.anyio
    async def test_returns_hit_miss_counts(self, mock_service):
        controller = SearchConnectorToolController.__new__(SearchConnectorToolController)
        controller._SearchConnectorToolController__service = mock_service

        result = await controller.get_search_analytics()

        assert isinstance(result, SearchAnalyticsResponse)
        assert result.cache_hits == 3
        assert result.cache_misses == 1
        assert result.total_searches == 4
