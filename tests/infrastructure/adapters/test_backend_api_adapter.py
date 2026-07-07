from unittest.mock import AsyncMock, patch

import pytest

from mcp_server.domain import BackendApiException
from mcp_server.infrastructure.adapters.backend_api import BackendApiAdapter


@pytest.fixture
def adapter():
    return BackendApiAdapter(
        base_url="http://backend/api/v1",
        jwt_secret="secret",
        jwt_issuer="mcp-server",
    )


def _mock_response(json_data, status_code=200):
    response = AsyncMock()
    response.status_code = status_code
    response.json = lambda: json_data
    response.raise_for_status = lambda: None
    return response


class TestSearchSops:
    @pytest.mark.anyio
    async def test_search_sops_returns_raw_page_response(self, adapter):
        page = {"items": [{"id": "s1"}], "page": 1, "size": 20, "total": 1, "total_pages": 1}
        with patch("mcp_server.infrastructure.adapters.backend_api.AsyncClient") as mock_client_cls:
            client = AsyncMock()
            client.get = AsyncMock(return_value=_mock_response(page))
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await adapter.search_sops(text="deploy", tags=["ops"], page=1, size=20)

        assert result == page
        client.get.assert_awaited_once()
        called_url = client.get.await_args.args[0]
        assert "http://backend/api/v1/sops" in called_url
        assert "q=deploy" in called_url

    @pytest.mark.anyio
    async def test_search_sops_wraps_http_errors(self, adapter):
        from httpx2 import HTTPStatusError

        with patch("mcp_server.infrastructure.adapters.backend_api.AsyncClient") as mock_client_cls:
            client = AsyncMock()
            error_response = _mock_response({}, status_code=500)

            def _raise():
                raise HTTPStatusError("error", request=None, response=error_response)

            error_response.raise_for_status = _raise
            client.get = AsyncMock(return_value=error_response)
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            with pytest.raises(BackendApiException):
                await adapter.search_sops(text="deploy")


class TestGetSop:
    @pytest.mark.anyio
    async def test_get_sop_returns_sop_data(self, adapter):
        sop = {"id": "s1", "content": "text"}
        with patch("mcp_server.infrastructure.adapters.backend_api.AsyncClient") as mock_client_cls:
            client = AsyncMock()
            client.get = AsyncMock(return_value=_mock_response(sop))
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await adapter.get_sop("s1")

        assert result == sop
        client.get.assert_awaited_once_with(
            "http://backend/api/v1/sops/s1", headers=client.get.await_args.kwargs["headers"]
        )
