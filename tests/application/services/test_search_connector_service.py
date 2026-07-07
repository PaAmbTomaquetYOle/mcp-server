from unittest.mock import AsyncMock

import pytest

from mcp_server.application.ports import CacheStats
from mcp_server.application.services.search_connector_service import SearchConnectorService
from mcp_server.domain import BackendApiException
from mcp_server.domain.search import SearchDocument

_SOP_1 = {
    "id": "1",
    "content": "Restart deploy pipeline",
    "author": "U1",
    "tags": ["deploy"],
    "origin_channel": "C1",
    "updated_at": "2026-01-01T00:00:00Z",
}
_SOP_2 = {
    "id": "2",
    "content": "Onboard new hire",
    "author": "U2",
    "tags": ["hr"],
    "origin_channel": "C2",
    "updated_at": "2026-01-02T00:00:00Z",
}

_DOC_1 = SearchDocument.from_sop(_SOP_1, base_url="https://x/sops")


@pytest.fixture
def mock_backend_api():
    api = AsyncMock()
    api.search_sops = AsyncMock(
        return_value={"items": [_SOP_1, _SOP_2], "page": 1, "size": 20, "total": 2, "total_pages": 1}
    )
    api.get_sop = AsyncMock(return_value=_SOP_1)
    return api


@pytest.fixture
def mock_sop_cache():
    cache = AsyncMock()
    cache.search = AsyncMock(return_value=[_DOC_1])
    cache.refresh = AsyncMock()
    cache.get_stats = AsyncMock(
        return_value=CacheStats(total_docs=1, last_refresh="2026-01-01T00:00:00Z", hit_count=0, miss_count=0)
    )
    cache.is_stale = AsyncMock(return_value=False)
    return cache


@pytest.fixture
def service(mock_backend_api, mock_sop_cache):
    return SearchConnectorService(backend_api=mock_backend_api, sop_cache=mock_sop_cache, sop_base_url="https://x/sops")


class TestHandleSearch:
    @pytest.mark.anyio
    async def test_delegates_to_cache(self, service, mock_sop_cache):
        results = await service.handle_search("deploy", filters={})

        assert results == [_DOC_1]
        mock_sop_cache.search.assert_awaited_once_with("deploy", {})


class TestTestSearch:
    @pytest.mark.anyio
    async def test_same_as_handle_search(self, service, mock_sop_cache):
        results = await service.test_search("deploy")

        assert results == [_DOC_1]
        mock_sop_cache.search.assert_awaited_once_with("deploy", {})


class TestHandleEntityDetails:
    @pytest.mark.anyio
    async def test_fetches_sop_by_id(self, service, mock_backend_api):
        result = await service.handle_entity_details({"id": "1"})

        assert result == _SOP_1
        mock_backend_api.get_sop.assert_awaited_once_with("1")


class TestRefreshCache:
    @pytest.mark.anyio
    async def test_fetches_all_sops_and_refreshes_cache(self, service, mock_backend_api, mock_sop_cache):
        stats = await service.refresh_cache()

        mock_backend_api.search_sops.assert_awaited_once()
        refreshed_docs = mock_sop_cache.refresh.await_args.args[0]
        assert len(refreshed_docs) == 2
        assert all(isinstance(d, SearchDocument) for d in refreshed_docs)
        assert stats["total_docs"] == 1

    @pytest.mark.anyio
    async def test_paginates_through_all_pages(self, service, mock_backend_api, mock_sop_cache):
        mock_backend_api.search_sops.side_effect = [
            {"items": [_SOP_1], "page": 1, "size": 1, "total": 2, "total_pages": 2},
            {"items": [_SOP_2], "page": 2, "size": 1, "total": 2, "total_pages": 2},
        ]

        await service.refresh_cache()

        assert mock_backend_api.search_sops.await_count == 2
        refreshed_docs = mock_sop_cache.refresh.await_args.args[0]
        assert len(refreshed_docs) == 2

    @pytest.mark.anyio
    async def test_backend_error_propagates(self, service, mock_backend_api):
        mock_backend_api.search_sops.side_effect = BackendApiException("down")

        with pytest.raises(BackendApiException):
            await service.refresh_cache()


class TestGetStatus:
    @pytest.mark.anyio
    async def test_reports_backend_reachable_when_search_succeeds(self, service, mock_backend_api, mock_sop_cache):
        status = await service.get_status()

        assert status["backend_reachable"] is True
        assert status["cache"]["total_docs"] == 1
        assert status["is_stale"] is False

    @pytest.mark.anyio
    async def test_reports_backend_unreachable_on_error(self, service, mock_backend_api):
        mock_backend_api.search_sops.side_effect = BackendApiException("down")

        status = await service.get_status()

        assert status["backend_reachable"] is False
