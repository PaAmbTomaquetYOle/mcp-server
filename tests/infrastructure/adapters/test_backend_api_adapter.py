from unittest.mock import AsyncMock

import pytest

from mcp_server.domain import BackendApiException
from mcp_server.infrastructure.adapters.backend_api import BackendApiAdapter


class _StubTokenProvider:
    async def get_access_token(self) -> str:
        return "test-token"


def _mock_response(json_data, status_code=200):
    response = AsyncMock()
    response.status_code = status_code
    response.json = lambda: json_data
    response.raise_for_status = lambda: None
    return response


@pytest.fixture
def client():
    return AsyncMock()


@pytest.fixture
def adapter(client):
    return BackendApiAdapter(
        base_url="http://backend/api/v1",
        token_provider=_StubTokenProvider(),
        client=client,
    )


class TestSearchDossiers:
    @pytest.mark.anyio
    async def test_search_dossiers_sends_bearer_token(self, adapter, client):
        page = {"items": [{"id": "d1"}]}
        client.get = AsyncMock(return_value=_mock_response(page))

        result = await adapter.search_dossiers(employee_name="Jane")

        assert result == [{"id": "d1"}]
        client.get.assert_awaited_once()
        called_url = client.get.await_args.args[0]
        called_headers = client.get.await_args.kwargs["headers"]
        assert "http://backend/api/v1/dossiers/search" in called_url
        assert called_headers == {"Authorization": "Bearer test-token"}


class TestSearchSops:
    @pytest.mark.anyio
    async def test_search_sops_returns_raw_page_response(self, adapter, client):
        page = {"items": [{"id": "s1"}], "page": 1, "size": 20, "total": 1, "total_pages": 1}
        client.get = AsyncMock(return_value=_mock_response(page))

        result = await adapter.search_sops(text="deploy", tags=["ops"], page=1, size=20)

        assert result == page
        client.get.assert_awaited_once()
        called_url = client.get.await_args.args[0]
        called_headers = client.get.await_args.kwargs["headers"]
        assert "http://backend/api/v1/sops" in called_url
        assert "q=deploy" in called_url
        assert called_headers == {"Authorization": "Bearer test-token"}

    @pytest.mark.anyio
    async def test_search_sops_wraps_http_errors(self, adapter, client):
        from httpx2 import HTTPStatusError

        error_response = _mock_response({}, status_code=500)

        def _raise():
            raise HTTPStatusError("error", request=None, response=error_response)

        error_response.raise_for_status = _raise
        client.get = AsyncMock(return_value=error_response)

        with pytest.raises(BackendApiException):
            await adapter.search_sops(text="deploy")


class TestGetSop:
    @pytest.mark.anyio
    async def test_get_sop_returns_sop_data(self, adapter, client):
        sop = {"id": "s1", "content": "text"}
        client.get = AsyncMock(return_value=_mock_response(sop))

        result = await adapter.get_sop("s1")

        assert result == sop
        client.get.assert_awaited_once_with(
            "http://backend/api/v1/sops/s1",
            headers={"Authorization": "Bearer test-token"},
        )
